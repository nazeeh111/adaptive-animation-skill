# Removing inherited visual direction

Correction incorporated into the public release, 23 October 2026. See [combined release validation](release-validation.md) for current checks.

## Observed cause

Bare `studio.py init` already created an empty workspace. However, the README and production quickstart selected `--template motion`. That branch copied a complete authored six-second composition: pale sage, dark teal and orange, Inter/Newsreader, a split title/orbit layout and the same seed movement. Changing the brief only changed project metadata. Independent probes generated identical scene trees from unrelated briefs.

The renderer forwarded authored source without adding that identity. The evidence establishes reuse of a starter, not authorship by Anthropic or another organization. A subjective resemblance alone cannot establish provenance.

## Correction

- Generic motion initialization now supplies dimensions, local GSAP, a paused seekable clock and optional preview controls. It supplies no scene, copy, palette or font pairing. `--duration` records the intended time range.
- The prior three authored files are preserved byte-for-byte under `animation/assets/examples/orbit-title/`. `--template motion --example orbit-title` explicitly selects that six-second study, including its original fonts and licenses. Existing projects are untouched.
- Generic quickstarts require authoring the actual scene before rendering. Art-direction guidance distinguishes reusing capture code from reusing a composition. There is no required style menu or universal replacement look.
- Previous retargeted motion, sampled pixel checking, native render/source contracts, private path configuration and compact skill entrypoint remain in place.

## Verification

Four initializer tests passed: empty workspace, generic dimensions/duration and no inherited artwork/font files, exact explicit-example copy with licensed fonts, and preflight/no-overwrite preservation. Raw migration hashes match the current installed pre-change artwork for all three files. This establishes source preservation, separately from rendered behavior.

Independent browser consumption exposed a regression in the newly written scaffold: an expression-bodied `renderFrame` returned the paused GSAP Timeline, which is thenable, so an awaiting capturer hung. The function now explicitly returns no value. A real init → browser checker regression test covers this route; it does not infer correctness from the function text.

The corrected scaffold passed 35 independent real-browser checks across landscape and portrait sizes: geometry/duration, no inherited artwork/font files/external requests, paused and backward seeking, preview controls and live reduced-motion changes. Explicit orbit-title loading passed exact pixel/geometry replay at repeated times across eight sampled states. The new actual-capture integration test passed against both candidate and installed skill.

## Distinct authored representatives

Both began with the generic scaffold and no explicit example. Their independent scene sources remain editable. These are bounded regression probes, not a required style menu.

| Representative | Composition and type | Action and motion language |
| --- | --- | --- |
| Ink botanical study | Portrait plate, irregular SVG contours, marginal Georgia annotations and attached plant anatomy | Continuous stem growth and uncoiling, leaf articulation, then petals reveal the center |
| Pixel maintenance rover | Asymmetric industrial stage, original low-resolution Canvas drawing, native monospace labels | Held poses, cell insertion, actual power response and conveyor movement, with visible rolling transport |

Each actual silent H.264 master is four seconds and 120 decoded frames at 30 fps. Both have full-decode and exact sampled replay evidence. Current-source imagery and affected encoded frames receive independent review. Initial craft review identified sliding feet, opposing belt/crate direction, and a briefly detached botanical tip; these findings are repaired and checked in fresh versions, with earlier work retained.

These checks establish that the neutral route can support materially different staging and motion, not universal freedom from style bias or artistic perfection. Source, sampled-image and decoded-frame review are distinct from full normal-speed perceptual acceptance, which was not performed. No audio judgment is claimed for silent studies.


Final independent review closed all three artifact findings against the selected revisions. Later ink stage PNGs independently match the prior version. Selected identities:

- Ink attachment revision: `4480cdf900c7c75af93a8e94a956201ea3affaeafd74a3b8c2128cc4db3be489`.
- Pixel v4: `c6d22e7724958548229b1943223256e14094ac697d3d64168d326efd22407a5a`.

Public editable sources, selected movies, previews and reproduction notes are provided in [the ink study](../examples/ink-study/README.md) and [the power-cell study](../examples/power-cell/README.md). Their master hashes above identify the reviewed encoded bytes. System-font rendering can vary across hosts; exact pixel claims apply to the exercised browser/font environment.
