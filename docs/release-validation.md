# Release validation, 23 October 2026

This release combines the neutral browser scaffold, explicit preserved title study, replayable spring helper, significant-time browser diagnostics and updated creative guidance. It retains native editing/rendering choices and the existing configuration, source-recovery and media-verification contracts.

## Current automated checks

The current candidate passed 32 Python tests in 53.096 seconds, with all six real-browser tests enabled rather than skipped. Six independent Node spring tests also passed. The exercised host was macOS, Python 3.14, Node 24.14.0, existing Chrome, Playwright 1.62.1, Sharp 0.35.5 and installed FFmpeg/FFprobe. These results are scoped to the versions and contracts exercised, not every host or renderer.

The Python suite covers configuration selection/path handling, voice cache contracts with controlled fixtures, media size/rate/duration/decoded frames and invalid inputs, initializer routing and no-overwrite behavior, arbitrary/backward capture, explicit brief-action samples, static expectations and state-accumulation rejection. It does not synthesize a new voice or establish listening quality. The spring tests compare actual helper evaluation with independently integrated dynamics and cover continuity, repeated/backward sampling, validation, immutable inputs and extreme coefficients.

[Portable test instructions](../animation/references/portable-setup.md#run-the-tests) explain the optional browser dependencies and environment. Skipped tests are not passes. More detailed historical observations remain in [the original release record](validation.md), [motion follow-up](pass2-validation.md) and [starter correction](style-leak-validation.md).

## Public artifacts

- [Ink study](../examples/ink-study/README.md): native SVG/browser source, selected four-second master and preview.
- [Power-cell study](../examples/power-cell/README.md): native pixel Canvas source, selected four-second master and preview.
- [Editable presentation](../animation/docs/presentation.pptx), [workflow SVG](../animation/docs/diagram.svg) and [source map](../animation/docs/diagram-source-map.md).
- [Causal-flow example](../examples/causal-flow/index.html) and [selected eight-second movie](../animation/docs/causal-flow.mp4).

The ink and power-cell masters each fully decoded as 120 frames at 30 fps. Replay tests inspect actual pixels, not only clocks. Independent source/image/encoded-frame review corrected contact, conveyor direction and a briefly detached growing tip. Example notes distinguish local font dependence, silent delivery, full decode, sampled replay and perceptual review. These examples demonstrate different staging and movement; they are not an exhaustive style benchmark.

## Release checks and limits

Publication checks inspect the exact staged Git objects, including presentation XML and example dependencies, rather than trusting ignore rules alone. Personal machine configuration, logs, caches, backups, private research snapshots and task history stay excluded. Third-party notices retain GSAP's separate Standard License and font OFL terms; original code and materials retain MIT.

The eleven-slide presentation was exported, re-imported and all eleven received pages visually inspected. Package, layout, font and native chart/embedded-workbook checks passed. The public authoring source rebuilt all eleven slide PNGs identically in the exercised Artifact Tool environment. The spring chart retains actual helper-derived values rounded to 12 significant digits for workbook precision. The selected PPTX SHA256 is `2defad3dc525255c4ee6677fd2e7d68038382298c4637f8f0c4c394a2e914351`. Native PowerPoint and Google Slides were not exercised; this is not a claim of testing every receiving application. The final public commit and selected assets are checked after pushing.

Full normal-speed human perceptual acceptance, listening quality, universal style coverage, general physical simulation correctness and every target editor/runtime are not established by these tests. The skill directs productions to choose and verify their actual requirements, including meaningful holds and reduced-motion behavior. No palette, speed threshold, fixed composition or style catalog substitutes for the brief.
