# Production on this Mac

## Dated local runtime profile

This profile records the setup verified15October2026, not the newest available software or a universal route. Check current paths/settings when the job depends on them, while preserving pinned versions for reproducibility.

The configured browser default is locally scoped HyperFrames0.8.162, verified15October2026 with actual portrait pixels and local fonts. It retains screenshot capture, no-overwrite/process ownership and explicit opt-outs. Its local state-directory patch and upstream package integrity are retained with the runtime. Keep the task folder: this runtime lives under `work/unified-skill/hyperframes-0.8.162-candidate`, whose directory name records its isolated origin. `hyperframes_rollback_runner` retains the tested0.8.33 path; use that original route for old exact-output recipes. Do not replace vendor-managed plugin files or auto-update either runtime. Reassess newer versions for actual brief needs.

The command examples below target the installed skill. When evaluating a task-local candidate, resolve its own scripts/configuration instead; verify source, installed and invoked identities before treating an execution as evidence for that candidate. A historical receipt does not establish the current bytes.

## Start and revise

Use the user's existing project when one exists. The CLI scaffold is a video convenience, not a universal asset format: create the native project directly when a sprite, vector, rig or interactive artifact needs different dimensions/settings. New projects default to an empty native-source workspace. For a new project, the helper creates only a note, settings and useful folders. `--template motion` adds an unstyled browser capture scaffold: dimensions, a paused clock and preview controls, with no artwork, palette, copy or font pairing. Author the scene for the actual brief before rendering. No scene schema constrains the native source.

```sh
python3 <animation-root>/scripts/studio.py doctor --route motion
python3 <animation-root>/scripts/studio.py init /absolute/new-project --brief 'Audience, subject and intended result' --size 1920x1080 --fps 30 --duration 8 --template motion
# Author source/motion for this brief; the scaffold contains no visible scene.
python3 <animation-root>/scripts/studio.py render-motion /absolute/new-project --output /absolute/new-project/renders/scene-v1.mp4 --quality standard
python3 <animation-root>/scripts/studio.py verify /absolute/new-project/renders/scene-v1.mp4 --resolution 1920x1080 --fps 30 --duration 8 --frames 240
```

To reproduce the preserved six-second title study deliberately, add `--example orbit-title` to `init --template motion` and use `--duration 6`. Only that selection copies its artwork and Inter/Newsreader fonts. Existing authored projects remain unchanged; older generic motion quickstarts now create the unstyled scaffold.

Use a discovered Python3 executable; helpers support Python3.9+. Configured engine runtimes remain separate. `doctor` checks selected files and executables, not a working render, network or live editor session. `scripts/local.json` is this Mac's nonsecret path configuration. Move/reinstall dependencies deliberately if it reports missing paths.

`render-motion` freezes only `source/motion`, copies local assets and records hashes before delegating to the existing runner. The snapshot is evidence of submitted source, not successful completion. Generated root `.hyperframes/` reports/caches are excluded and preserved in the working project, allowing native check followed by render. Other hidden files and links remain rejected. Engine-generated reports may subsequently appear inside the snapshot; the manifest identifies submitted input bytes, not every generated artifact. It rejects existing outputs/snapshots and unsafe file types; use a new version name. Keep render/QC logs next to the result. Do not put private records, dependencies or symlinks in a composition. The snapshot does not sandbox JavaScript or detect arbitrary network calls; inspect source and keep assets local. Do not run unknown third-party code merely to research it.

The current browser runner owns its workers and responds to cancellation, but does not impose an automatic execution deadline. For unattended or uncertain jobs, call the selected CLI through the bundled `processes.run(argv, log_path, timeout=seconds)` from a small task-local Python runner. It gives the owned process group a bounded elapsed-time window and retains logs; choose the window for the real scene and machine. Do not start a second GPU job until cleanup has completed. A deadline through machine sleep is not a hard wall-clock guarantee.

## Offline composition and time

Use a native static root with explicit dimensions, duration and composition ID. Keep `window.__timelines.<id>` paused and seekable. For compatibility with the retained0.8.33 linter, place the final timeline registration in an inline script: the static linter does not inspect external JavaScript registration, even though rendering executes it. For this offline time-driven capture route, every animated property must follow timeline time or a repeatable evaluation of it. For a Canvas frame drawn in `onUpdate`, use callback-enabled seeking, such as `timeline.seek(seconds,false)`, when reviewing or implementing a scrubber. A clock change alone is not drawing proof: confirm different-time images differ and a repeated time matches after backward seeking. Seed procedural variation; avoid wall clocks, unseeded randomness, CSS autoplay and state that accumulates differently when seeking backward. Put photo/video/audio files in the local composition and declare timed media in the HTML, not only in JavaScript. Keep media duration synchronized with shot timing.

The capture scaffold and explicit title study have Play/Restart/scrub controls only at `index.html?preview=1`. Ordinary capture URLs omit them. Loading the file without that query intentionally leaves the timeline paused. Preview is for review; the actual exported frames remain the delivery evidence. Author vertical formats as compositions in their own right, not clipped horizontal frames.

For CSS 3D cards or panels whose depth must survive a fade, apply opacity to a 2D wrapper around the complete perspective/3D stage. Opacity below 1 and certain filters, masks and other grouping values can flatten a `preserve-3d` node even when its computed style still reports that keyword. Inspect the intended front/back face and depth order during the affected move in the actual browser. In the generic scaffold, keep `#studio` as the 2D capture root and nest the perspective/preserve-3d stage inside it: the root's `overflow:hidden` and `isolation:isolate` also impose grouping. Separate effects when they would flatten the actual 3D context. See [CSSWG grouping rules](https://drafts.csswg.org/css-transforms-2/#grouping-property-values) and [MDN transform-style](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/transform-style#description). A self-contained [front/back comparison](https://github.com/nazeeh111/adaptive-animation-skill/tree/main/examples/css3d-grouping) demonstrates the opacity case; other grouping combinations need their own relevant check.

For an illustrated world, first define its visual materials, depth layers and recurring objects. Animate a continuous action, use foreground overlap and parallax where they clarify space, and preserve object identity across transitions. A camera can reveal relationships; constant camera motion can also obscure them. For code-drawn characters use a small rig and readable poses; test contact, walk cycles and silhouettes. For complex acting or dynamics choose the native drawing, rig or simulation system appropriate to the medium; Blender is an exercised option for3D rigs and cached dynamics. A generic browser starter does not establish character-animation quality.

For 3D, retain the native .blend, asset paths, color management and render settings. Match editorial frame rate before producing frames; convert Blender's one-based inclusive range to the edit's zero-based half-open range. Confirm simulation caches and random seeds before resuming. A saved native file does not establish saved simulation state. For a stateful shot, bake with the actual cache type, save after baking, quit and reopen, then compare selected states when seeking in a different order. Check a separately recovered copy without relying on original cache paths. Do not infer rigid-body disk-cache support from generic PointCache fields; the exercised Blender 5.1.2 route persisted its rigid-body bake inside the native file. Invalidate/rebuild affected state after an upstream change. Native EEVEE rendered here; Cycles Metal remains experimental. Photo reconstruction requires actual input and an appropriate tested reconstruction workflow.

## Interactive, live and recorded time

Keep the actual host/runtime and input model. Identify which clock drives simulation, presentation and recording. Decide what pause means: freeze presentation while ingestion continues, stop the model or buffer input. Define reconnect/catch-up, missing/duplicate/out-of-order events and replay only to the extent the real source requires them. Do not silently drop scientifically meaningful events to smooth the picture. A recording can use a timestamped input fixture and fixed evaluation/capture clock; it does not prove a live connection works. Avoid frame-count-dependent motion in a variable-rate browser callback.

For functional motion, distinguish acknowledgment of input, pending work and real completion. A routine control should respond promptly and stay interruptible, even while an expressive scene plays. Show completion after the actual operation succeeds, or identify the result as an illustrative prototype. If the display changes optimistically before confirmation, retain failure and recovery behavior.

For state transitions, test interruption and rapid/repeated input where relevant, not just a clean scripted path. Preserve essential information when reduced motion is requested; for example show a stable resolved state instead of merely slowing a perpetual decorative loop. Check preference changes at runtime where the host supports them. Pause/stop/hide controls for ongoing content and reduced-motion preferences solve different needs. Check actual embedding, resize, input/focus and performance on the target device before claiming runtime delivery. No new universal state machine or event framework is required.

When a sound-led host promises synchronization to a recorded score, derive its picture from the actual media transport. A wall-clock fallback can silently advance the picture during media pause or buffering; probe that interruption, not only the host's own Pause button. Cancel obsolete asynchronous play/voice starts after reset, and keep saved gesture/strike events in the same timebase. Check actual input, replay pixels and generated audio rather than only control counters. Authored score cues describe planned excitations; they do not establish live microphone or waveform analysis. A fixed film performance and a playable host need separate acceptance evidence.

## Color, transparency and receiving systems

For a composite or professional interchange, read the existing project/receiver specification before choosing defaults. Record frame range/handles, exact rate, resolution/pixel aspect, camera axes/units/lens/distortion and shutter timing when those affect the shot. Check camera and blur alignment over motion, not only one still. Agree which rig/actions, masks, caches and nodes must stay editable.

An EXR is a container, not a declaration of color space. Preserve the receiving OCIO configuration/version, input and working spaces, display/view and required output transform. OCIO means OpenColorIO, the configuration system used to name color transforms. ACES is a color-management system; do not silently upgrade a studio's chosen ACES/OCIO configuration to the latest release. Keep data channels such as depth/normals out of color transforms. A display/view transform for review and a scene-linear master have different purposes; avoid accidental double transforms or baking a review look into a master that requires scene-linear values.

Agree straight versus premultiplied alpha, meaning whether RGB is stored independently or multiplied by opacity. Check semitransparent/motion-blurred edges over light and dark backgrounds, required channels and relinking in the actual receiver. Render a small representative transfer before the full job. A proxy movie, matching tags or a successful local decode cannot prove alpha, color or editable native handoff. Existing opaque-H.264 checks remain scoped to that route.

## Selected sources and transparent layers

Use the shared helpers when a handoff or transparent delivery needs these checks; ordinary native saving does not require a ZIP. For a bundle, write an explicit JSON selection beside the project:

```json
{"root":".","files":["source/shot.blend","assets/plate.webm","tracking/corners.json","LICENSE.txt"],"external_dependencies":[{"name":"Blender","version":"record the exercised version"}]}
```

An entry may instead be `{"path":"assets/plate.webm","sha256":"expected lowercase SHA256"}` to require unchanged dependency bytes. Include fonts, textures, caches, source media, licenses and reproduction settings that the actual project needs. External dependencies are declarations, not verified installations. Avoid bundling an entire environment, model cache or unrelated private media.

```sh
python3 <animation-root>/scripts/studio.py pack-sources /absolute/project/selection.json --output /absolute/new-sources.zip
python3 <animation-root>/scripts/studio.py recover-sources /absolute/new-sources.zip --out /absolute/new-recovery-directory
python3 <animation-root>/scripts/studio.py verify-layer /absolute/overlay.mov --resolution 1080x1920 --codec prores --fps 30 --duration 8 --frames 240 --alpha-mode straight
```

Pack/recover refuse existing destinations, links, unsafe paths and case/Unicode aliases. They stream selected bytes and validate the complete index, CRC and SHA256 before starting recovery; unexpected write failures retain/report the partial directory. Parent directories must already exist. Default uncompressed budget is 4 GiB, override with `--max-bytes`; metadata is capped at 8 MiB and 100,000 files. ZIP central-directory parsing is not a hostile-file sandbox or a hard memory bound. This is explicit byte recovery. Reopen a separately recovered native project and exercise its needed media, controls or representative renders before claiming working native recovery.

`verify-layer` fully decodes one still/movie's actual alpha plane, checks supplied expectations and reports unsigned16 alpha extrema/counts. Its default requires varying nonempty alpha; `--alpha-content present` deliberately permits a constant plane. `--max-bytes` bounds decoded-alpha scratch, default 4 GiB. An alpha tag alone cannot pass. `--alpha-mode` is a caller declaration, not a measured association. This does not verify color transforms, float/HDR channels, timestamps, image-sequence completeness, audio or receiving-system fidelity. Retain sequence manifests and use native checks when those are the deliverable. For a real transfer, independently recompose representative edges over light/dark and the actual plate in the intended color pipeline.

For real footage replacement, derive attachment from picture observations of persistent physical detail. A changing display is not a stable tracking texture. Check physical edges or held-out landmarks across the shot, including the far edge: a low fit residual on a narrow strip can still produce large extrapolation error. Retain confidence, rejected intervals and labeled manual corrections. Keep creative insert, plate and measured track separate so an art revision can reuse verified unchanged dependencies. Preserve original stream timing when conforming audio/video with different start offsets.

## Narration and sound

Bundled `narration.py` retains measured, cached local takes. Kokoro is the default CPU engine; explicit Qwen adds delivery instructions using existing local weights. Read [voice controls and review](voice.md) when selecting an engine or performance. Default example:

```json
{"fps":30,"voice":"bm_george","language":"en-gb","pronunciations":{"Snell":"Snell"},"segments":[{"id":"opening","text":"Light meets a boundary.","pause_after":0.4,"take":"v1"}]}
```

```sh
python3 <animation-root>/scripts/studio.py narrate /absolute/spec.json --out /absolute/new-project/audio/take-v1 --cache /absolute/new-project/audio/cache
```

It creates dry takes, 48kHz stereo narration, sentence-frame cues and SRT. Supported integer FPS must divide48000 for exact sample/frame boundaries. Cache keys include spoken text, voice, speed, take, synthesis source and model/voice hashes. Changing one segment reuses unchanged takes. Captions retain written text while pronunciation substitutions affect speech. Sentence timing is not word-level alignment. Validate wording/pronunciation by listening; transcription can catch omissions but cannot select the best performance. Music, effects and ducking remain creative decisions; preserve stems and avoid clipping. Qwen is an explicit expressive option with bounded passage/cache proof, not an automatic replacement or listening-quality winner.

## Focused verification

The `verify` command targets opaque H.264 video. Use `verify-layer` for the separate decoded-alpha contract above. GIF, SVG, interactive scenes, rig exports and other delivery properties still need the appropriate native/receiving checks. For H.264, it delegates to the tested media verifier: resolution/rate/positive-duration/codec/audio boundary checks plus full decode. Add `--duration SECONDS` and `--frames COUNT` for the expected timeline when known: the first compares video duration within one microsecond, the second counts decoded video frames in an additional CPU pass. This catches a valid but truncated film that ordinary decode alone accepts. For fractional frame rates derive the duration from the exact frame count/rate rather than a rounded headline. The central `verify --fps` accepts exact rational rates such as `30000/1001`; a rounded `29.97` is a different value. It checks the actual average stream rate, not every frame timestamp. Browser `init`/`render-motion` and narration keep their exercised integer-rate contracts; use the native edit/capture route suited to a different timebase. Add `--audio` when audio is required. It does not inspect visual craft, text accuracy or listening quality. Review final encoded frames where text is largest, longest, changing or near a cut. Inspect motion at changed transitions, opening/ending, and sync at sentence boundaries. For consequential novel work, use one independent reviewer with the brief and actual artifacts. Fix material findings; do not repeat score rituals after the relevant checks pass.

Keep source render color, compositing and delivery tags explicit. Opaque H.264 is the tested delivery route. Alpha, HDR, ProRes or editor interchange requires a small representative receiving-side check before committing a whole job. Preserve masters and originals; media conversion must use explicit input, new output and overwrite policy.

For a localized revision with a trustworthy prior master and unchanged picture timing, optionally use the aligned-render comparator below. It accepts one opaque 8-bit standard dynamic range (SDR) video stream with matching dimensions, frame timestamps and durations. It measures every bounded frame pair, then exports changed-range boundaries and peaks with neighbors in one extraction pass. Read `report.json` status and `review.html`; exit 0 means a report was written. One shared 60-second processing deadline (`--seconds` can shorten it), source frame/pixel/file limits and image/output limits bound the job. Oversized, fragmented or broad changes show an explicit fallback to direct review. Defaults select RGB channel differences above 12 levels on at least 32 pixels. Re-encoding can flag most frames; raising thresholds can hide a small symbol, so return to direct review when comparison cannot narrow the work. Zero selected differences does not establish identity or approval. Retain normal-speed motion, listening and comprehension review when the brief needs them.

```sh
python3 <animation-root>/scripts/compare_renders.py /absolute/prior.mp4 /absolute/revision.mp4 --out /absolute/new-review
```

## Perceptual review and feedback

When motion or listening judgment is requested, check the current review route's
actual inputs before calling it available. A desktop player can emit sound without
supplying audio to the reviewer. Screenshots, playback telemetry, waveform/loudness
measurements and transcription each provide narrower evidence. State the artifact
version, observed mode and any missing modality; keep technical verification
separate from perceptual approval. Reassess this boundary when tools/models change,
rather than permanently assuming a model can or cannot hear or watch.

If a required modality is unavailable, provide the exact selected master in an
authorized playable view, retain its path/hash, and ask for focused feedback with
timecodes or a short description. Continue independent checks while waiting, and
leave the requested judgment pending until feedback or a capable route arrives.
For normal-speed audiovisual review, confirm the intended rate, audible sound and
the full relevant interval; silent samples cannot clear sound design or sync.
Reproduce material findings against that version, revise the affected source and
recheck the affected result. Do not rerender unchanged work, install a generator
or build another player merely to compensate for missing perceptual access.

For a sound-led film, retain atmosphere, effects and music stems when they materially help revisions. Measure the actual mix and encoded delivery, including quiet passages, clipping, start/end and action sync. Choose loudness for the brief; one target is not a universal standard. Noise-rich material may have low raw sample correlation after lossy AAC even when timing is correct. Before blaming the renderer or relaxing a check, compare a direct encode with the same codec/bitrate and inspect alignment/envelopes. Room for Two's192kbps browser audio matched its direct192control; a320kbps source encode preserved more rain detail by measurement. Its selected audio-only revision copied the H.264 picture stream exactly. Use that option when it earns the bitrate, not as a mandatory setting or listening-quality claim. Keep lossless stems and recheck the receiving format.
