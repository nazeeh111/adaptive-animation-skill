import test from 'node:test';
import assert from 'node:assert/strict';
import {createRetargetedSpring} from '../assets/motion/retargeted-spring.mjs';

function near(actual, expected, tolerance, message) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    message + ': actual=' + actual + ', expected=' + expected);
}

// Independent reference: numerically integrate acceleration from Newton's
// second-order linear equation with RK4. No analytic response formula is used.
// Split at target events so integration never averages two different inputs.
function integrate(options, endTime, maxStep = 1 / 6000) {
  let position = options.initialValue;
  let velocity = 0;
  let target = position;
  let time = 0;
  let next = 0;
  const omega = 2 * Math.PI * options.frequencyHz;
  const acceleration = (x, v) =>
    omega * omega * (target - x) - 2 * options.dampingRatio * omega * v;
  while (time < endTime) {
    while (next < options.events.length && options.events[next].time <= time) {
      target = options.events[next++].target;
    }
    const boundary = Math.min(endTime, options.events[next]?.time ?? endTime);
    const step = Math.min(maxStep, boundary - time);
    if (step <= 0) { time = boundary; continue; }
    const a1 = acceleration(position, velocity);
    const v2 = velocity + a1 * step / 2;
    const a2 = acceleration(position + velocity * step / 2, v2);
    const v3 = velocity + a2 * step / 2;
    const a3 = acceleration(position + v2 * step / 2, v3);
    const v4 = velocity + a3 * step;
    const a4 = acceleration(position + v3 * step, v4);
    position += step * (velocity + 2 * v2 + 2 * v3 + v4) / 6;
    velocity += step * (a1 + 2 * a2 + 2 * a3 + a4) / 6;
    time = Math.min(time + step, boundary);
  }
  return {value: position, velocity};
}

test('matches independent RK4 integration over dense, backward and repeated times', () => {
  const options = {
    frequencyHz: 2.3, dampingRatio: 0.61, initialValue: -14,
    events: [
      {time: 0.03, target: 120}, {time: 0.23, target: 24},
      {time: 0.51, target: 148}, {time: 0.51, target: 90},
      {time: 0.79, target: -35},
    ],
  };
  const spring = createRetargetedSpring(options);
  const times = Array.from({length: 171}, (_, i) => i / 100);
  let seed = 713;
  for (let i = 0; i < 60; i++) {
    seed = (seed * 16807) % 2147483647;
    times.push(seed / 2147483647 * 1.7);
  }
  const saved = new Map();
  for (const time of times) {
    const sampled = spring.sample(time);
    const expected = integrate(options, time);
    near(sampled.value, expected.value, 0.000002, 'RK4 position at ' + time);
    near(sampled.velocity, expected.velocity, 0.00002, 'RK4 velocity at ' + time);
    saved.set(time, sampled);
  }
  for (const time of times.reverse()) {
    assert.deepEqual(spring.sample(time), saved.get(time));
    assert.deepEqual(spring.sample(time), spring.sample(time));
  }
});

test('retargeting preserves both position and velocity, including simultaneous changes', () => {
  const options = {
    frequencyHz: 1.8, dampingRatio: 0.72, initialValue: 17,
    events: [
      {time: 0, target: 100}, {time: 0.23, target: -40},
      {time: 0.23, target: 72}, {time: 0.57, target: 145},
    ],
  };
  const spring = createRetargetedSpring(options);
  const epsilon = 1e-7;
  for (const at of [0.23, 0.57]) {
    const left = spring.sample(at - epsilon);
    const middle = spring.sample(at);
    const right = spring.sample(at + epsilon);
    const prior = createRetargetedSpring({
      ...options, events: options.events.filter(event => event.time < at),
    }).sample(at);
    near(middle.value, prior.value, 1e-12, 'no position jump');
    near(middle.velocity, prior.velocity, 1e-12, 'no velocity jump');
    near(left.value, right.value, 0.001, 'position continuity');
    near(left.velocity, right.velocity, 0.01, 'velocity continuity');
    near((right.value - left.value) / (2 * epsilon), middle.velocity, 0.001,
      'returned velocity matches independent position derivative');
  }
  const coalesced = createRetargetedSpring({
    ...options, events: options.events.filter(event => event.target !== -40),
  });
  for (let time = 0; time < 1.5; time += 0.013) {
    assert.deepEqual(spring.sample(time), coalesced.sample(time));
  }
});

test('slow, lightly damped, and nearly critical springs match numerical dynamics', () => {
  for (const [frequencyHz, dampingRatio] of [[0.2, 0.1], [15, 0.015], [5, 0.999999]]) {
    const options = {frequencyHz, dampingRatio, initialValue: 5,
      events: [{time: 0, target: 90}, {time: 0.27, target: -20}]};
    const spring = createRetargetedSpring(options);
    for (const time of [0.08, 0.27, 0.3, 0.75]) {
      const expected = integrate(options, time);
      const actual = spring.sample(time);
      near(actual.value, expected.value, 0.00001, 'parameter-range position');
      near(actual.velocity, expected.velocity, 0.001, 'parameter-range velocity');
    }
  }
});

test('copies caller data and retains initial rest before the first change', () => {
  const options = {
    frequencyHz: 3, dampingRatio: 0.8, initialValue: 12,
    events: [{time: 0.2, target: 90}],
  };
  const spring = createRetargetedSpring(options);
  const original = spring.sample(0.3);
  options.frequencyHz = 20;
  options.events[0].time = 0;
  options.events[0].target = -100;
  options.events.push({time: 0.1, target: 2});
  assert.deepEqual(spring.sample(0.3), original);
  for (const time of [-100, -0.1, 0, 0.199, 0.2]) {
    assert.deepEqual(spring.sample(time), {value: 12, velocity: 0});
  }
  assert.deepEqual(createRetargetedSpring({
    frequencyHz: 1, dampingRatio: 0.5, initialValue: -7, events: [],
  }).sample(100), {value: -7, velocity: 0});
});

test('validates finite explicit parameters, sorted events and sample times', () => {
  const valid = {frequencyHz: 2, dampingRatio: 0.7, initialValue: 0, events: []};
  for (const field of ['frequencyHz', 'dampingRatio', 'initialValue']) {
    for (const invalid of [undefined, NaN, Infinity, -Infinity, '2', null]) {
      assert.throws(() => createRetargetedSpring({...valid, [field]: invalid}), TypeError);
    }
  }
  for (const frequencyHz of [0, -1, Number.MAX_VALUE]) {
    assert.throws(() => createRetargetedSpring({...valid, frequencyHz}), RangeError);
  }
  for (const dampingRatio of [-1, 0, 1, 2]) {
    assert.throws(() => createRetargetedSpring({...valid, dampingRatio}), RangeError);
  }
  assert.throws(() => createRetargetedSpring(null), TypeError);
  assert.throws(() => createRetargetedSpring({...valid, events: {}}), TypeError);
  for (const events of [
    [{time: -1, target: 1}],
    [{time: 0.3, target: 1}, {time: 0.2, target: 2}],
  ]) assert.throws(() => createRetargetedSpring({...valid, events}), RangeError);
  for (const events of [
    [null], [{time: NaN, target: 1}], [{time: 1, target: Infinity}],
    [{time: '0', target: 1}], [{time: 0}],
  ]) assert.throws(() => createRetargetedSpring({...valid, events}), TypeError);
  const spring = createRetargetedSpring(valid);
  for (const time of [NaN, Infinity, -Infinity, '0', undefined]) {
    assert.throws(() => spring.sample(time), TypeError);
  }
});

test('very late samples settle without infinite phase and unreasonable ranges fail clearly', () => {
  const spring = createRetargetedSpring({
    frequencyHz: 2, dampingRatio: 0.7, initialValue: 0,
    events: [{time: 0, target: 70}, {time: 0.3, target: -20}],
  });
  assert.deepEqual(spring.sample(Number.MAX_VALUE), {value: -20, velocity: 0});
  assert.throws(() => createRetargetedSpring({
    frequencyHz: 2, dampingRatio: 0.7, initialValue: -Number.MAX_VALUE,
    events: [{time: 0, target: Number.MAX_VALUE}],
  }), RangeError);
});

