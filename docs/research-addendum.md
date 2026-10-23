# Research decisions for the current release

Research is used to improve a specific visual or execution property, not to lock the skill to a vendor, catalog or engine. The original gallery, Motion Canvas, Remotion, native editing/drawing systems, Hallmark and Impeccable are compared in [the motion research notes](pass2-research.md).

## Huashu Art Motion

Inspected original code and documentation at [commit 8a0d7d7](https://github.com/alchaincyf/huashu-art-motion/tree/8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c), including camera.js, brush.js, medium.js and film_gate.py. This was a source review, not a matched render benchmark.

Its procedural brushes and material compositing are substantive: seeded bristles, pressure-shaped strokes, ink spread, grounds and pigment layers. They remain useful candidates for a painterly production where the result can be compared against an actual reference. The global utility, geometry, stage and cache dependencies need deliberate isolation; one file is not a standalone painting engine. No upstream runtime was imported merely to expand a capability list.

Its scene-specific composition guidance agrees with the neutral scaffold. Its mandatory direction count, fast-motion delivery threshold and palette gate would restrict legitimate quiet work and subject-specific visual identities, so those policies are not transferred. This distinction preserves the useful drawing mechanisms without adopting the whole workflow.

For narrower work, [GSAP DrawSVG](https://gsap.com/docs/v3/Plugins/DrawSVGPlugin/) supplies progressive vector-stroke reveal through dash properties, while [Manim MovingCamera](https://docs.manim.community/en/stable/reference/manim.camera.moving_camera.MovingCamera.html) provides a native mathematical/vector camera route. Neither establishes painterly pigment behavior, and Manim Community documentation does not establish API equivalence with a different installed fork. No new plugin, renderer or service was installed for this comparison.

The [root MIT license](https://github.com/alchaincyf/huashu-art-motion/blob/8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c/LICENSE) covers original code/documentation subject to notice retention. Its [asset exceptions](https://github.com/alchaincyf/huashu-art-motion/blob/8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c/README.md) separately identify demo-only character/media, OFL fonts and Arphic-licensed stroke derivatives. No excluded artwork or third-party runtime is redistributed here.

Selection is conditional: a future brief may favor that painting code, another native method or no new dependency. No small comparison establishes universal artistic superiority.


## Earned browser-depth correction

An original [CSS 3D consumer comparison](../examples/css3d-grouping/README.md) reproduced flattening when opacity is placed directly on a preserve-3d card. At 120 degrees, that case showed 17,892 front-face pixels and no back-face pixels; the same fade on a wrapper outside the full 3D stage showed 17,849 back-face pixels and no front-face pixels. Computed transform-style still said preserve-3d in both cases. Four angles were captured; the example retains source, screenshot and measured report.

This supports conditional production guidance about separating grouping effects from depth, informed by [CSSWG](https://drafts.csswg.org/css-transforms-2/#grouping-property-values) and [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/transform-style#description). It is a real native-source transfer, not a new dependency or aesthetic restriction. The report does not establish every browser/filter combination.

[GSAP Flip](https://gsap.com/docs/v3/Plugins/Flip/) addresses measured layout transitions but does not supply 3D transform support. [Three.js arc-length curve sampling](https://threejs.org/docs/pages/Curve.html#getPointAt) is useful when steady path travel is intended; it is not a reason to force constant speed. A separate six-frame FFmpeg temporal-mixing probe changed a black/white hard cut into intermediate values, but the current capture route does not use that accumulation, so no speculative blur warning or pipeline change was added.
