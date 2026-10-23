# Presentation source

`build.mjs` rebuilds the eleven-slide release presentation using editable slide objects. `base.pptx` is the preceding public deck, retained as the layout, font and palette template. Its SHA256 is `0f7902456eeaf77565af0dddbe9d582679cef2fd4e3a04620d4be468891927b4`.

The deck explains the current animation skill, with the neutral scaffold, explicit title example, original ink/pixel studies, optional spring retargeting, significant-time sampling and scoped research findings. The workflow diagram on slide 8 remains editable. The spring chart on slide 6 is an editable native chart with values derived directly from the repository's helper and rounded to 12 significant digits for the embedded chart workbook. The two example pictures are embedded raster previews with their original aspect ratios. Their editable native scenes and movies remain in `examples/ink-study/` and `examples/power-cell/`.

## Rebuild in an existing Artifact Tool environment

The script requires Node.js and an environment that already supplies `@oai/artifact-tool`, such as the bundled Codex artifact runtime. That authoring dependency is not vendored or installed by this repository. A general Node.js installation alone does not establish that the script can run. The PPTX itself remains editable in compatible presentation software without this script.

From the repository root, with the dependency available:

```sh
node animation/docs/presentation-source/build.mjs . /absolute/path/to/new-output-directory
```

If the existing module is outside normal Node.js package resolution, `ANIMATION_ARTIFACT_MODULE` can point to its existing `artifact_tool.mjs` entry. This selects a local authoring dependency and does not install anything.

The output directory must not exist. The script produces a candidate PPTX, slide PNGs, layout JSON and the actual spring-series values. It uses repository-relative sources and never fetches remote assets. Review current renders and validate the candidate before replacing a selected master. This is an authoring source, not a universal cross-application compatibility validator.

The script rebuilds the authored candidate. The selected public master additionally contains an embedded chart-data workbook packaged during finalization, so identical PPTX bytes are not promised.

Arial follows the existing presentation template. The scene previews show their own native typography. No font binaries, gallery artwork or third-party runtime code are copied into this source folder.

## Content and asset sources

- `animation/SKILL.md` and its conditional craft/production references.
- `animation/assets/motion/retargeted-spring.mjs` for spring values, with explicit parameters retained in `build.mjs`.
- `animation/tests/test_motion_browser.py` for the diagnostic sampling example.
- `examples/ink-study/preview.png` and `examples/power-cell/preview.png` for original reviewed scene pictures. See each example's `LICENSE`, and power-cell's `THIRD-PARTY.txt` for its separate native-source runtime notice.
- `docs/pass2-research.md` and `docs/research-addendum.md` for primary-source provenance and evidence limits.

Speaker notes retain the corresponding public relative references and primary links. The release license covers original slide content and authoring code. No third-party video or excluded character artwork appears in the presentation.
