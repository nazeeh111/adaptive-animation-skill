# Repeated target changes

Use when an authored or replayable interaction changes a target before motion settles. Prefer the existing runtime's interruption behavior when it already works. A continuous offline track is useful when restarting a tween loses speed, a live spring cannot seek backward, or the same input history must drive a film and preview. This is one optional mechanism, not a motion style or required stage.

## Fixed linear spring track

`assets/motion/retargeted-spring.mjs` exports `createRetargetedSpring`. It adds the step response of each target change and evaluates the sum directly at the requested time. This keeps position and velocity continuous without a per-frame simulation cache. Frequency and damping are explicit creative inputs, not a universal timing preset.

```js
import {createRetargetedSpring} from './retargeted-spring.mjs';
const track = createRetargetedSpring({
  initialValue: 40,
  frequencyHz: 2.3,       // natural frequency in cycles per second
  dampingRatio: 0.61,    // supported range: strictly between 0 and 1
  events: [{time: 0.1, target: 240}, {time: 0.28, target: 90}]
});
const {value, velocity} = track.sample(0.32);
// Value uses the same units as the target, velocity uses units per second.
```

Events use nonnegative seconds in nondecreasing order. At a simultaneous change, the last target wins. Inputs are copied; later mutations do not rewrite the track. Samples can arrive in any order, and before the first change the initial value is at rest. The returned velocity supports a meaningful continuity check; matching positions alone can hide a speed discontinuity.

Choose the amount of settling and overshoot for the subject. Keep target/state changes tied to the real action. A spring is inappropriate where the desired motion is a deliberate cut, a held drawing, a measured physical result or a non-oscillating response. Native WAAPI, Motion or GSAP may already provide the needed live behavior without this helper.

## Boundaries and proof

The formula assumes fixed parameters and a scalar linear spring with damping below the critical value. It is not a collision/contact solver, changing-parameter simulation, nonlinear material model, input recorder or evidence of artistic quality. For live input, retain timestamped targets for replay or use the actual runtime's spring. Sampling cost grows with the number of earlier target changes; do not use an unbounded event history as a streaming engine.

Validate the property that matters: probe around a retarget while the object is moving, compare position and velocity, and replay earlier times after later ones. Test the displayed geometry as well as the numeric state. Browser edge rasterization and scene-state drift are different failures. Use explicit seconds in `scripts/check_motion.mjs` around the actual event when its default samples do not cover it.

The implementation is original code informed by the closed-form superposition mechanism in [the original UI-motion prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/92aee2f586ac0715cb3cbcb6384834f98a33383d/prompts/twoclipping-402193.md). The prompt is a source lead, not a local quality benchmark. Independent tests compare the helper with numerical integration of the second-order spring equation:

```sh
node --test animation/tests/test_retargeted_spring.mjs
```

These tests establish the exercised mathematical and replay properties, not that spring motion improves every interface or animation.
