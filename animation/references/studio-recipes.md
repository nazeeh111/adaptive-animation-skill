# Tested local studio recipes

Retained task root: `<local-production-workspace>`.
Evidence root: its `outputs/studio` folder. Keep this task folder: the installed skill references its projects and isolated runtimes; it is not a portable installer. Start with `START-HERE.html`, `evidence/inventory.json` and each selected film's README. Continuation state is task-root `TASK_STATE.md`.

## Choose the shot's native route

| Need | Route | Actual proof and boundary |
| --- | --- | --- |
| Equations, geometry, scientific explanation | `manimgx-studio`, pinned ManimGX 0.1.1 | `films/physics-v3/final-v1`: 85.867-second film, eight editable scenes, measured local narration and exact phase-front geometry. Earlier `films/physics` retains selective revision and natural-request routing proofs. |
| Designed interface motion and typography | `hyperframes-local` with existing authoring skills | `films/product-v2`: 32-second TRACE landscape and independently composed portrait. Select `trace-horizontal-v2.mp4` and `trace-vertical-v2-r3.mp4`. Earlier portrait versions remain as comparisons. |
| Existing React motion project | Remotion plugin | Isolated 4.0.534 comparison under `benchmarks`; no global replacement or universal performance winner. |
| Procedural space, materials, lights, camera choreography | `blender-local`, native Blender 5.1.2 EEVEE | `films/architecture-v3/solstice-v3.mp4`, selected `source/solstice-v3-render.blend` and GLB. The native scene retains cameras, probes and cuts. GLB is a separate geometry/material/camera handoff, with shader, GI, AREA-light and timeline limits. |
| Free local narration | `local-speech`, Kokoro ONNX 0.6.1 | Stable CPU preset route; `tools/narration.py` adds measured phrase cues, take caching, pronunciation substitutions and captions. No fabricated word timestamps. |
| Expressive speech experiment | Isolated Qwen3-TTS 1.7B CustomVoice 4-bit | `research/voice.md` and `research/voice-audition.html`. Seven bounded groups retained 21 sentences by ASR; names, joins and naturalness need listening. The long unsegmented take omitted content. Do not download more weights by default. |
| Editorial conform, grading or complex mix | Existing Palmier/Resolve skills | Check current availability per job. Palmier was not running at audit; configured Resolve tools do not establish a live timeline or receiving-side interchange. Add an editor when the actual job benefits. |
| Real-photo reconstruction, learned masks/depth, generated video | Research shortlist | `research/spatial-frontier.md`. The synthetic pavilion is not proof of these capabilities. |

The three revised films preserve one visible cause or object: equal-time advances determine the transmitted wavefront; the same reservation button becomes a timing witness and returns with immediate feedback; the architectural route returns through the portal to its sculpture. These are reusable staging mechanisms, not a compulsory house style.

## Reproduce or revise the physics film

Use the pinned `work/runtime/bin/python`, not ambient `python3`. A resumed shell resolved to Xcode Python 3.9 and omitted local media tools. The process helper scopes the verified media directory to its children, and the builder rejects a different AST-generating Python before rendering.

Commands run from the task root. Always use a fresh output directory:

```sh
work/runtime/bin/python outputs/studio/tools/narration.py outputs/studio/films/physics-v3/narration.json --out outputs/studio/films/physics-v3/audio-new --cache work/studio-cache/speech
work/runtime/bin/python outputs/studio/films/physics-v3/source/build_film.py --audio outputs/studio/films/physics-v3/audio-new --out outputs/studio/films/physics-v3/inspect-new --inspect-only
work/runtime/bin/python outputs/studio/films/physics-v3/source/build_film.py --audio outputs/studio/films/physics-v3/audio-new --out outputs/studio/films/physics-v3/draft-new --profile draft
work/runtime/bin/python outputs/studio/films/physics-v3/source/build_film.py --audio outputs/studio/films/physics-v3/audio-new --out outputs/studio/films/physics-v3/final-new --profile final
```

Inspect the draft before the final. Final is native 1920×1080 at 30 fps; draft is 1280×720. The model assumes a flat boundary, stationary transparent media and a monochromatic wave. Its construction arc is geometric, not a radiated pulse. Read the film README before changing its physics.

For a sentence revision, edit only the intended narration segment and create new audio. Identical text, voice, take, pronunciation and runtime hashes reuse dry audio. Changed measured timing invalidates the affected native shot. Each scene's source key excludes other scene classes but includes its shared geometry/helpers. The builder freezes source/cues, caches native and color-converted delivery shots, verifies identity/media hashes, and preserves invalid attempts before a retry.

The earlier final-v2 timing repair reused seven native and seven delivery clips, rebuilt only s07, and took 19.90 seconds on that warm cache. This is a measured revision, not a cold-render benchmark. A fresh plain-language installed-skill trial under `films/physics/natural-request-trial` produced verified MP4/SRT with eight cached takes.

A narration-only change that fits exactly the same measured shot slots can use:

```sh
work/runtime/bin/python outputs/studio/tools/remix_narration.py --film outputs/studio/films/physics/final-v2 --audio NEW_AUDIO_DIRECTORY --out NEW_REMIX_DIRECTORY
```

That demonstrated baseline recipe preserved the encoded picture with zero native renders and zero picture re-encodes. The helper rejects changed cue timing before output creation. Otherwise use the native shot builder. Keep the demonstrated baseline separate from the newer film revision.

## Browser capture and 3D rendering

`benchmarks/results.md` and `benchmarks/compare.html` retain matched browser fixtures, repeated timings, deliberate color revisions, intentional vertical layouts and native 4K vector/type exports. Embedded footage remains its original resolution. Cache/warm definitions and small font/color differences prevent a universal winner claim.

The tested explicit screenshot adapter is `tools/hf_screenshot.py`. It extends the pinned runner's sanitized child environment without editing vendor files:

```sh
work/runtime/bin/python outputs/studio/tools/hf_screenshot.py render PATH_TO_STATIC_COMPOSITION --output NEW_EXPORT.mp4 --fps 30 --quality high --workers 1
```

Bake media tags and root layout into static HTML. Dynamic media insertion froze benchmark footage; JavaScript-only root sizing cropped frames. Freeze/hash queued input bytes: editing source after launch does not revise that job. Local font aliases avoided Google Fonts fetch messages in TRACE, but request-level network isolation is not established.

Use official Blender MCP for owned scene queries, versioned edits, bakes and short previews. The installed bridge actually performed these operations. A long preview exceeded its 240-second client deadline without stopping the render. Verify the exact owned native process has stopped before giving the GPU to another job. Long sequences use a bounded owned native batch with source/settings fingerprints and atomic PNG checkpoints. The original final recovered 582 frames; the new preview recovered 290 frames and rendered the remaining 70.

Inspect the material cause before raising samples: native water probes showed that more samples and full ray resolution did not repair transmission grain. The selected synthetic scene uses a dark, opaque reflective approximation with gentle waves. It does not demonstrate validated water refraction. Selected native source and parameter receipts are under `films/architecture-v3`.

When converting an interactive lesson or webpage to MP4, inspect the exported states themselves. A frozen page does not preserve learner interaction. Surface missing media, estimated timing and unsupported scenes before final rendering. The source-level OpenMAIC comparison and424-record metadata screen are at `research/openmaic-review.md`; that application is a conditional classroom companion, not an installed production dependency.

## Recovery and research

`tools/processes.py` writes durable logs and bounds its owned process group. Cancellation/timeout probes passed, including a descendant ignoring TERM; power-loss recovery and unrelated applications are outside that contract. Preserve native projects, dry takes, captions and previous exports.

Installation receipts under `evidence` contain installed hashes and backup paths. Check those hashes before restoring a backup so later user changes are not lost. Vendor-managed skill caches stay unchanged. The source archive excludes applications, models and render caches; it is editable material, not a self-contained runtime.

Both studio recurring checks are PAUSED at the user's request. Keep work manual unless asked otherwise. The retained public metadata command is:

```sh
work/runtime/bin/python outputs/studio/tools/discovery_run.py --out outputs/studio/research/discovery-NEW-ID
```

Six public metadata feeds, at most 2 MB per response and 10 seconds per request. It preserves the last successful observation across outages and deduplicates repeated errors. It neither installs tools nor downloads models. Read release notes and test a useful isolated change before promoting it. Prior registration/state tests do not prove a future timer fired.
