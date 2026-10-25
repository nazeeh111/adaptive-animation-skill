# Contributing

Keep changes tied to an observable improvement in animation, design, editability or execution. A new tool, style card or metric needs a concrete use, not just another option in a list. Discuss substantial changes in an issue or pull request before expanding the skill's scope.

## Work locally

Use Python 3.9+ and an existing Node installation. Tests never install engines or download a browser.

```sh
python3 -m unittest discover -s animation/tests -v
node --test animation/tests/test_retargeted_spring.mjs
```

Media tests need FFmpeg/FFprobe. Browser checks need existing Chrome and Playwright; the generic pixel checker also needs Sharp. Follow [the exact dependency/environment setup](animation/references/portable-setup.md#run-the-tests), then run:

```sh
python3 -m unittest discover -s animation/tests -p test_motion_browser.py -v
node --test examples/causal-flow/test-preview.mjs
```

Read the summaries: browser tests skip without `ANIMATION_TEST_BROWSER`. The example test is repository-scoped. Do not report skipped tests as verification.

The public Checks workflow runs these suites on a standard Ubuntu runner with an existing browser, pinned action commits and no artifact/cache uploads. Its result covers the exercised Linux environment; it does not clear optional local editor/voice/render adapters.

## Change and review

- Preserve unrelated work, private configuration and a usable prior output.
- Read the current source and test the actual affected behavior. Add a regression for a consequential defect; avoid tests that only match prose or implementation details.
- Keep instructions conditional and concise. Retain native sources; examples are explicitly selected studies, not defaults for every project.
- For visual changes, inspect the current rendered artifact and its relevant transitions or states. Distinguish pixel/state checks from ordinary motion or sound judgment.
- Keep software, fonts, media and generated-output terms separate. Include provenance and required notices; don't copy gallery media or private examples.

Describe the concrete problem, resulting behavior, relevant checks and remaining limits in a pull request. Include the exact artifact/source version behind a visual claim.

## Repository assets

The README demo is composed from the two original public masters. To reproduce it with existing FFmpeg, choose a fresh output path:

```sh
python3 docs/media/build_demo.py --output /absolute/new-demo.gif
```

The presentation has [its own authoring source and runtime boundary](animation/docs/presentation-source/README.md). The installable folder does not contain the repository-only examples. Avoid private paths, configuration, caches, logs and unlicensed assets in commits or release archives.
