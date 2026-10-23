# Adaptive Animation Skill

An adaptable Codex skill for creating and improving animation, motion design, style frames, films, explainers and editable visual projects. It connects the audience's purpose to visible action, chooses suitable native tools, and checks the delivered result.

![Adaptive animation workflow](animation/docs/diagram.png)

The skill supports restrained scientific explanations, character work, cinematic 3D and expressive motion. It does not impose a visual style, model hierarchy, mandatory team or research phase on every request.

## Use it

Copy `animation/` into your user-owned skills directory after preserving any existing version. Then ask, for example:

> Use $animation to turn this process into a clear eight-second explanation. Make the decision and consequence visible, keep the diagram editable, and deliver the native source and reviewed output.

For a quick edit, just provide the source and desired change. The skill should execute directly when additional planning would not help.

See [the skill](animation/SKILL.md) and [portable setup](animation/references/portable-setup.md). Core Python helpers use the standard library. FFmpeg/FFprobe provide media checks. Browser diagnostics optionally use installed Playwright, Sharp and Chrome. Native rendering, editing and voice engines are separate installations, and retained adapters have explicit compatibility requirements. No paid API is required.

## Current release

- New browser projects contain capture structure and a paused clock, with no inherited artwork, palette, font pairing or staging. The old title study is explicitly selectable.
- Optional continuous spring retargeting preserves velocity and supports arbitrary-time replay.
- Browser diagnostics accept important event times, so a brief action need not fall between all default samples.
- Craft guidance covers causal action, continuity, named timing cues, real interaction feedback and review of the received story.
- Native editable sources remain the deliverable boundary; there is no universal renderer, style menu or quality score.

Read [current release validation](docs/release-validation.md), [motion research](docs/pass2-research.md), [retargeted-motion checks](docs/pass2-validation.md) and [the starter correction](docs/style-leak-validation.md). Earlier [21 October validation](docs/validation.md) remains historical evidence.

## Different subjects, different staging

[Ink botanical study](examples/ink-study/README.md) uses a portrait SVG illustration with growth and unfolding. [Power-cell study](examples/power-cell/README.md) uses stepped pixel motion, visible rolling contact, insertion and a conveyor consequence. Each includes editable source and a selected four-second movie. They are examples for inspection, not default art directions.

## Explore the example

[![Signal-routing example](animation/docs/causal-flow-preview.png)](animation/docs/causal-flow.mp4)

[Watch the eight-second example](animation/docs/causal-flow.mp4). It was captured as 240 explicit frames and verified after encoding.

Open [examples/causal-flow/index.html](examples/causal-flow/index.html) locally. Add `?preview=1` to the file URL for controls. The review/direct switch changes the explanation's route. Playback respects reduced-motion preferences; deterministic capture uses an explicit `renderFrame(seconds)` function. Timing is illustrative.

## Diagram and presentation

- [Editable SVG](animation/docs/diagram.svg), [PNG](animation/docs/diagram.png), [vector PDF](animation/docs/diagram.pdf)
- [Eleven-slide editable presentation](animation/docs/presentation.pptx) and [authoring source](animation/docs/presentation-source/README.md)
- [Research and source notes](docs/research.md), [motion transfers](docs/pass2-research.md), [later comparisons](docs/research-addendum.md)

## Verify helper behavior

```sh
python3 -m unittest discover -s animation/tests -v
node --test animation/tests/test_retargeted_spring.mjs
python3 animation/scripts/studio.py init /absolute/new-project \
  --brief 'An action and its visible consequence' --size 1280x720 --fps 30 --duration 6 --template motion
python3 animation/scripts/studio.py verify /absolute/movie.mp4 \
  --resolution 1280x720 --fps 30 --duration 6 --frames 180
```

Plain `init` creates an empty workspace. `--template motion` adds an unstyled capture scaffold, not a finished animation; author the subject-specific scene before rendering. Select `--template motion --example orbit-title` explicitly to reproduce the preserved six-second title study. Its artwork and fonts are not inherited by generic projects.

The media tests require FFmpeg/FFprobe and use temporary fixtures. Browser tests are opt-in and otherwise report as skipped; follow the [browser test setup](animation/references/portable-setup.md#run-the-tests) to exercise them. Optional engine paths are never silently installed. See each command's `--help` and the [production reference](animation/references/production.md) for its scope.

## License and credits

Original instructions, helper code, example and release materials use the [MIT license](LICENSE). Bundled **GSAP has its own Standard License**, which includes restrictions and is not MIT. Inter and Newsreader use the SIL Open Font License. Retain the [third-party notices](animation/assets/THIRD-PARTY.txt). This repository does not redistribute creator videos or claim that a prompt-gallery license clears them.

Research began with [Awesome Opus 5.5 Videos](https://github.com/yihui-dev/awesome-opus5-5-videos) and expanded to original prompts, source implementations and primary technical documentation. The workflow is model-adaptive and makes no model superiority claim.
