# Editing: material, story, sound and handoff

Use native editing when the requested work needs timeline interaction, footage conform, grading or a real audio mix. A complete browser or Manim film need not pass through an editor merely to claim integration.

## Build the edit from the material

Inspect the source and existing timeline before choosing software or changing settings. Establish audience/purpose, essential meaning, desired duration/formats and which edits must remain native. Preserve originals, source names/timecodes and a usable prior project. If a task is a trim, cleanup or conform, do it directly; no mandatory screenplay, storyboard or full rebuild.

For an unfamiliar collection, make only useful selects/logs: source ID and time range, what happens/is said, usable sound, and the reason it belongs. A transcript is an index, not a substitute for watching performance or preserving context. Find the decisive moments and build a coherent rough cut before fine transitions, grade or graphics. Let each cut change information, attention, emotion or time. Preserve orientation and speaker meaning; use cutaways or audio-leading/trailing cuts when they actually improve continuity. Silence, held images and slower passages may be the right rhythm.

Make dialogue intelligible before adding music. Inspect source channels, peaks, noise and sync; use restrained repair appropriate to the defect and retain the unprocessed source. Room tone, effects, ambience and music should support the scene without concealing speech or creating accidental sound changes at joins. Listen across edits and at intended playback level. Separate stems when they earn revision value; a loudness number does not establish a good mix.

## Protect timing and source fidelity

Read the actual source rate/timebase, variable-rate behavior, sample rate, pixel aspect, orientation and color. Distinguish source ranges from timeline ranges, inclusive native frame numbers from half-open edit intervals, and timecode from elapsed seconds. Use proxies or deliberate conform only when needed; keep original media and the mapping back to it. Do not treat an extension or nominal frame rate as proof of exact frame/time behavior. Check retimes, adjacent edits, held frames and sync at the actual cut, not only the opening.

Deliver the requested native project or honest cut instructions plus relinkable dependencies, a selected master and required derivatives. Verify actual export bounds, cuts, text, sound, missing/offline media and representative source/timeline matches. For a substantial edit, reopen a separate project copy when recovery or handoff is material. Native effects are editable only where the actual receiving application preserves them. [Production](production.md) covers color, alpha, camera/shutter and live/offline boundaries; [YouTube](youtube.md) covers release packaging when in scope.

## Dated local editor profile and failure lessons

The following records the15October2026 setup and narrow historical proofs. Check actual edition/version/control before reuse. These are options and observed limits, not a permanent editor prescription.

On this Mac, `resolve-free-codex` documents Resolve Free21.1. Use visible UI for live projects, inspecting the current state and protecting unsaved user work. External Python scripting is unavailable in this edition here; offline artifact tools do not apply changes inside the live app. Do not bypass that restriction.

The installed `davinci-resolve-advanced` MCP offers grouped offline artifact and report operations. An actual `editorial.parse_interchange` EDL proof returned two contiguous cuts,150frames/5seconds at30fps from unchanged copied media. This proves parsing and timing readback only. Grade generation, Fusion composition generation, audio planning and delivery reports are available by tool description until their specific operation is run and checked. Read the current action schema and provide explicit input, fresh output and overwrite policy for conversions.

The editorial tools describe EDL, OTIO and XMEML. XMEML is Final Cut Pro7 XML and differs from modern FCPXML. Do not assume their compatibility. Palmier's historical FCPXML route is conditional on the live app and actual versions; no receiving-side roundtrip was established here. Preserve native projects and referenced media.

For a required interchange, test a short representative edit first: media relink, clip count, source/timeline ranges, resolution/rate, timecode, retimes, transforms, crops, transitions, titles, audio fades and color. Compare receiving-side frames and sound. Bake unsupported effects to reviewed media while retaining the original editable source. Only call the handoff editable for the elements actually preserved.

Local offline proof artifacts are retained under the original task's `outputs/studio/unified-skill/editor-proof`. The later `unified-skill/resolve-live-proof` exercised actual Resolve Free: imported picture and local speech, two contiguous4second cuts, A1 speech, native H.264/AAC export, nativeDRP export and import into a separate recovery project. The recovery visibly retained both cuts, waveform and linked picture. The exported XMEML independently parses as240frames/30fps with the exact source ranges; its receiving-side XML import remained disabled, so XML roundtrip is not established. These are historical receipts, not required paths for future projects.

Native Quick Export appended `.mov` even though the proposed name ended `.mp4`. Probe the actual file, not its assumed extension. Its video was8seconds/240frames, but the AAC metadata extended64ms beyond picture. A pure stream-copy trim retained that duration; the selected web derivative copies picture and explicitly trims/reencodes audio to8seconds. Retain the native export and label any later conform accurately. Full decode and expected-word recognition passed; this does not establish complex grading, Fusion or mixing.

Qt accessibility toggles may change a checkbox without switching the page. Prefer an observed native keyboard action and inspect the resulting page. Native macOS Open/Save panels can interrupt control; reacquire the app and inspect state rather than replaying uncertain edits. A responsive app with a timed-out control connection is not proof of a crash. Never restart or overwrite an unrelated project just to recover automation.

Choose editorial tools per brief. Existing native projects deserve their own editor. Direct FFmpeg assembly is sufficient for simple measured cuts/muxing; use Resolve when its actual editing/color/audio workflow helps. Current Kdenlive or Shotcut may be better free candidates when open project formats, their effects or controllable export solve a concrete missing need. They were researched, not installed or benchmarked here. Check current official releases, Mac architecture, licenses, dependencies and one representative project before adoption. Do not impose an editor as a mandatory final stage.
