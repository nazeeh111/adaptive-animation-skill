# Animation workflow diagram

[Editable SVG](diagram.svg), [PNG preview](diagram.png), [vector PDF](diagram.pdf), and [editable presentation](presentation.pptx).

The figure shows the animation skill's production workflow. It describes intended behavior, not a claim that every possible output has passed every check. Simple tasks may combine stages. The eleven-slide presentation covers subject-specific craft, original ink/pixel examples, the neutral scaffold and explicit example, time and input, optional spring retargeting, significant-time diagnostics, research limits and native handoff. Slide 8 retains a shorter six-step workflow, combining render and review and treating packaging as part of the handoff. The standalone SVG retains eight explicit stages.

| SVG element IDs | Meaning and source |
| --- | --- |
| `brief`, `craft`, `build`, `render`, `review`, `package`, `receiver`, `deliver` | Workflow interpretation of the current `SKILL.md` craft, native route, verification and handoff guidance. |
| `brief-to-craft` through `receiver-to-deliver` | Main production path. Receiver success means the required editing controls survive. |
| `review-to-craft` | Material review findings revise the affected beat before another render. |
| `receiver-to-build` | Receiving-application defects repair the source or handoff, then recheck. |
| `acceptance-note` | Normal-speed review, proportionate verification and preserving the last valid render. |

The SVG is the object-editable master with stable IDs and accessible title/description. PNG is the raster preview. PDF retains vector geometry and text with font substitution; its actual render was inspected for legibility, clipping and complete paths. In the PPTX, text, rules, process diagram and the spring data chart remain editable. The chart includes an embedded workbook. Original scene previews are raster images, with their editable native sources retained in the public examples. Slide citations are in speaker notes. [Presentation source](presentation-source/README.md) retains the authoring script, template and spring values, with its existing-runtime dependency stated explicitly.

Primary references cited in the presentation:

- [Remotion: flickering and independent frame rendering](https://www.remotion.dev/docs/flickering)
- [GSAP: timeline seek](<https://gsap.com/docs/v3/GSAP/Timeline/seek()/>)
- [Three.js: disposing of resources](https://threejs.org/manual/pages/cleanup.html)
- [W3C: Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)
- [Motion Canvas: named time events](https://motioncanvas.io/docs/time-events/)
- [User-supplied animation gallery](https://github.com/yihui-dev/awesome-opus5-5-videos), used as inspiration rather than a benchmark

Artwork and slide content are original release documentation. No gallery videos, screenshots, fonts or third-party artwork are redistributed here.
