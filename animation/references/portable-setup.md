# Portable setup and boundaries

The skill instructions work with suitable native tools already available to the agent. The helper scripts are conveniences, not a requirement to use one renderer. Original Python helpers require Python 3.9+ on macOS/Linux. Process-group cleanup uses POSIX signals, so native Windows execution is not established. No helper installs an engine, reads credentials or calls a billed model API.

## Install the skill

Copy the repository's `animation/` folder into your user-owned skills directory, preserving any existing version first. Keep your local configuration private. Restart or refresh skill discovery as your host requires. Invoke `$animation` for a production request; the entrypoint routes only to relevant guidance.

## Configuration

Helpers select `ANIMATION_CONFIG` when set, otherwise `scripts/local.json` when present, otherwise `scripts/local.example.json`. An explicitly selected missing/invalid file fails rather than silently choosing another configuration. Copy the example to a private path and set only the tools you use. Relative paths resolve beside that configuration file; bare executable names resolve through PATH. Example:

```sh
cp animation/scripts/local.example.json /your/private/animation-local.json
export ANIMATION_CONFIG=/your/private/animation-local.json
python3 animation/scripts/studio.py doctor --route motion
```

`doctor` checks files/configuration only. Null settings describe optional unavailable tools and should produce a useful missing-setting message. They do not indicate an installed renderer. Configuration paths are not secrets, but personal machine paths do not belong in a public repository.

## Self-contained helpers

- `studio.py init` creates a source workspace without engine dependencies. `--template motion` includes local GSAP and licensed fonts. It is an optional six-second study, not an imposed aesthetic.
- `studio.py verify` uses installed FFmpeg and FFprobe directly. It validates the H.264 delivery contract and full decoding, independently of Manim. `verify-layer` covers its documented transparent formats. These checks do not judge artistic quality.
- `pack-sources`, `recover-sources`, and `compare_renders.py` work with the documented inputs and dependencies. Pack/recover retain no-overwrite, traversal and integrity checks.
- `examples/causal-flow/index.html` in the repository is an editable browser animation with no JavaScript dependencies. Add `?preview=1` for playback, route selection and scrubbing. Capture URLs stay paused until evaluated through `renderFrame(seconds)`.

## Optional browser pixel diagnostics

`check_motion.mjs` needs Node.js, already installed Playwright and Sharp packages and a browser executable. It never downloads a browser. Install the free package in your own project if needed, or point `ANIMATION_PLAYWRIGHT_MODULE` to an existing Playwright entry file and `ANIMATION_IMAGE_MODULE` to an existing Sharp package. Tested here with Playwright 1.62.1 and installed Chrome. A different host/browser needs its own check.

```sh
node animation/scripts/check_motion.mjs examples/causal-flow \
  --browser /absolute/path/to/chrome \
  --out /absolute/new-pixel-report --expect-motion
```

The helper starts one owned loopback server/browser and blocks external page resource requests. It is a diagnostic for inspected local source, not a sandbox for untrusted JavaScript. It samples explicit times, saves PNGs and reports repeated-time pixel differences and browser errors. Static holds can legitimately produce identical samples; `--expect-motion` applies only when a sampled change is expected. Exact PNG hashes remain in the report. The default comparison permits at most 16 changed pixels with a maximum channel difference of 12/255, based on observed tiny Chromium SVG edge variations; it reports the measured differences. Use `--exact` for zero tolerance. Small changes within this bound can be missed, so a pass is limited sampled evidence. This tolerance does not clear a state/geometry defect. It does not render the whole film, approve smoothness, listen to audio, or verify the receiving editor.

## Optional native adapters

The following are retained interfaces to an existing local production setup, not engines bundled by this repository:

| Route | Required external contract |
| --- | --- |
| `render-motion` | `hyperframes_runner` must be a compatible reviewed Python bridge exporting `CHROME`, `environment()` and `main()`, with the render arguments used by `hf_screenshot.py`. It is **not** a path to the stock HyperFrames JavaScript CLI. The dated retained profile is HyperFrames 0.8.162. Use HyperFrames' native CLI/skill directly if you do not have that bridge. |
| Math | `manim_launcher` is an existing compatible launcher, not a Manim package import. Author directly with the installed Manim/ManimGX workflow when appropriate. |
| 3D/editing | Blender/Resolve or the receiving application's own tools and native project. The presence check cannot establish a live session. |
| Kokoro voice | `speech_python` and `speech_root` refer to an existing installation with `synthesize.py`, `models/kokoro-v1.0.onnx`, `models/voices-v1.0.bin` and the CLI expected by `narration.py`. Installing a package called Kokoro alone does not provide that adapter. |
| Voice wording review | Existing whisper.cpp CLI, model and optional VAD model paths. No weights are downloaded. |
| Optional Qwen voice | Existing engine environment and explicit model manifest under its documented separate terms. It is never loaded by discovery alone. |

Retain a working native renderer and prove the requested operation before committing a production to an adapter. Do not interpret unavailable optional adapters as permission to acquire credentials, spend money or run arbitrary installers.
