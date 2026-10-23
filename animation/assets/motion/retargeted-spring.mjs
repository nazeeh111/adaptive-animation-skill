/**
 * Optional scalar motion for an authored, repeatedly retargeted property.
 *
 * A fixed underdamped linear spring is evaluated directly at any time:
 * no clock, integration cache, browser, framework, or global state.
 * frequencyHz is the natural frequency in cycles/second; dampingRatio must
 * be strictly between 0 and 1. These are explicit creative inputs.
 *
 * events are {time, target} records in nondecreasing seconds. Simultaneous
 * changes use the last target. Before time zero the initial value is at rest.
 * Input records are copied, so later caller mutations cannot change the track.
 *
 * This is not a collision/contact solver, nonlinear spring, changing-parameter
 * simulation, or an interactive event recorder. For live input, retain a
 * timestamped target history or use the receiving runtime's native animation.
 * Sampling costs O(the number of elapsed target changes).
 *
 * Original implementation. The transferable superposition idea was observed in
 * yihui-dev/awesome-opus5-5-videos, commit
 * 92aee2f586ac0715cb3cbcb6384834f98a33383d, prompt twoclipping-402193.
 * No framework implementation or prompt prose is included.
 */
function finiteNumber(value, name) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new TypeError(name + ' must be a finite number');
  }
  return value;
}

export function createRetargetedSpring(options) {
  if (!options || typeof options !== 'object' || Array.isArray(options)) {
    throw new TypeError('Expected spring options');
  }
  const frequencyHz = finiteNumber(options.frequencyHz, 'frequencyHz');
  const dampingRatio = finiteNumber(options.dampingRatio, 'dampingRatio');
  const initialValue = finiteNumber(options.initialValue, 'initialValue');
  if (frequencyHz <= 0) throw new RangeError('frequencyHz must be positive');
  if (dampingRatio <= 0 || dampingRatio >= 1) {
    throw new RangeError('Only underdamped springs with 0 < dampingRatio < 1 are supported');
  }
  if (!Array.isArray(options.events)) throw new TypeError('events must be an array');

  const omega = 2 * Math.PI * frequencyHz;
  const decay = dampingRatio * omega;
  const dampedOmega = omega * Math.sqrt((1 - dampingRatio) * (1 + dampingRatio));
  const velocityScale = omega * (omega / dampedOmega);
  if (![omega, decay, dampedOmega, velocityScale].every(Number.isFinite) ||
      decay <= 0 || dampedOmega <= 0) {
    throw new RangeError('Spring parameters exceed the supported numerical range');
  }

  const changes = [];
  let previousTime = -Infinity;
  let previousTarget = initialValue;
  for (let i = 0; i < options.events.length; i++) {
    const event = options.events[i];
    if (!event || typeof event !== 'object' || Array.isArray(event)) {
      throw new TypeError('events[' + i + '] must be a time/target record');
    }
    const time = finiteNumber(event.time, 'events[' + i + '].time');
    const target = finiteNumber(event.target, 'events[' + i + '].target');
    if (time < 0 || time < previousTime) {
      throw new RangeError('Event times must be nonnegative and ordered');
    }
    // Coalesce simultaneous changes before calculating deltas; only the final
    // target applies at that instant.
    if (changes.length && time === previousTime) changes[changes.length - 1].target = target;
    else changes.push({time, target});
    previousTime = time;
  }
  for (const change of changes) {
    change.delta = change.target - previousTarget;
    if (!Number.isFinite(change.delta)) {
      throw new RangeError('A target change exceeds the supported numerical range');
    }
    previousTarget = change.target;
  }

  function sample(timeSeconds) {
    finiteNumber(timeSeconds, 'timeSeconds');
    let value = initialValue;
    let velocity = 0;
    for (const change of changes) {
      const elapsed = timeSeconds - change.time;
      if (elapsed < 0) break;
      if (elapsed === 0 || change.delta === 0) continue;
      const attenuation = Math.exp(-decay * elapsed);
      // Avoid evaluating an enormous phase after its contribution underflows.
      if (attenuation === 0) {
        value += change.delta;
        continue;
      }
      const phase = dampedOmega * elapsed;
      if (!Number.isFinite(phase)) {
        throw new RangeError('Sample time exceeds the supported numerical range');
      }
      const sine = Math.sin(phase);
      const halfSine = Math.sin(phase / 2);
      // Algebraically the ordinary damped step response. expm1 and the
      // half-angle identity reduce cancellation close to a target change.
      const response = -Math.expm1(-decay * elapsed) +
        attenuation * (2 * halfSine * halfSine - (decay / dampedOmega) * sine);
      value += change.delta * response;
      velocity += change.delta * velocityScale * attenuation * sine;
    }
    if (!Number.isFinite(value) || !Number.isFinite(velocity)) {
      throw new RangeError('Sample result exceeds the supported numerical range');
    }
    return {value, velocity};
  }
  return Object.freeze({sample});
}

