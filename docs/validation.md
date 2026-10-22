# Validation and limits

Checked 21 October 2026 on macOS with existing local tools. These are scoped observations, not a claim of universal quality or renderer support.

## Completed checks

- 22 Python configuration/cache and actual FFmpeg media tests passed. Covered explicit private configuration, PATH and relative-path resolution, dependency cache invalidation, missing/invalid configuration, H.264 codec, size, integer/fractional rate, duration, actual decoded frame count, audio alignment, corrupted inputs, multi-video rejection and operation without Manim.
- 3 real-browser regression tests passed: stateless scene restoration, failure for accumulating state, failure when a static scene is incorrectly expected to move, and preservation of an existing report. Dependencies were already installed; no browser was downloaded.
- Real local Kokoro synthesis produced a 48kHz stereo take; a repeated call reused byte-identical cached audio. Whisper wording review matched the test phrase. These are functional checks, not a perceptual listening judgment.
- The revised 640x360 and 1080x1920 starters passed exact repeated PNG checks at start, early and midpoint in an 11-sample shuffled-time probe. The original first seek left the orbit at 0 degrees while a repeated seek produced 15 degrees. Warm timeline initialization and an explicit transform mode repaired that defect. A seed-specific paint-layer hint also removed a separately diagnosed portrait raster instability; this is local to the starter, not a general layer-promotion policy.
- The causal-flow example passed sampled seeking with explicit tiny raster tolerance. Independent state inspection found matching geometry/styles; Chrome still changed 9 to 13 edge pixels by at most 11/255 between repeated renders. The diagnostic retains exact hashes, reports differences, defaults to at most 16 changed pixels and maximum channel difference 12/255, and offers `--exact`. Subtle changes inside that bound can be missed.
- Independent interactive checks passed state restoration, alternate routes, play/pause, runtime reduced-motion changes, route changes while reduced motion is active, and restoration of controls. Fixed capture and interactive clocks remain separate.
- Flowcraft SVG, PNG and vector PDF were rendered and visually inspected. The final PPTX was imported and all 8 slides rendered/inspected. Text and diagram objects remain editable. PDF font substitution is disclosed in the diagram source map. PowerPoint itself was not exercised.
- A full baseline skill backup was recovered to a separate directory and all 32 baseline file hashes matched. Public text and PPTX XML were checked for personal absolute paths.

The silent causal-flow movie was captured from unchanged source as 240 explicit frames at 30fps. Final H.264 yuv420p decoded at 960x540, 8.0 seconds, 240 frames, with no audio streams; all media contracts passed. Encoded representative frames were visually inspected. Mobile preview at 390x844 had no horizontal overflow. Full normal-speed human playback was not performed.

On 22 October, the example's color was changed from peach to a cool signal accent. The current HTML was recaptured as 240 explicit frames; sampled backward seeks remained within the declared 16-pixel/12-channel tolerance, with no browser errors. The new H.264 movie passed full decode and the same 960x540/30fps/8.0-second/240-frame contract. Encoded frames at 0, 3, 6 and 7.9 seconds were inspected, and the 390px preview still had no horizontal overflow. The editable diagram SVG, PNG and vector PDF and the eight-slide PPTX were recolored consistently; the PDF and presentation were rendered and inspected after export. These checks verify this release's files, not artistic quality across requests.

A final fresh-source starter render passed full decode and the 640x360 / 30fps / 6.0-second / 180-frame contract. Representative encoded title/motion/footer states were inspected after the final CSS and transform fixes.

## Delivery boundaries

The supplied X post returned 403 and its contents remain unverified. The prompt collection supplied inspiration and source leads; its model claims and media counts were not used as comparative evidence. No creator videos or gallery assets are bundled.

The cloud presentation service failed before editing. The local PPTX is the presentation deliverable. Optional HyperFrames/Kokoro/Manim adapters still require existing compatible installations described in portable setup; a presence check is not renderer proof. Cross-platform execution beyond the documented macOS/Linux interfaces, general photoreal/character quality, full perceptual sound review and arbitrary receiving-system compatibility were not established.

The diagnostic checks sampled frames. It does not approve the whole film's pacing, reading speed, all intermediate states, flash safety, color management, physical simulation or artistic quality. Use the specific production checks required by the actual brief.
