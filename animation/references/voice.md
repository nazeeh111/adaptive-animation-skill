# Local narration choices

Use Kokoro for the exercised fast CPU route, and explicit Qwen for instruction-directed performance when the brief benefits. This is a workflow choice, not a listening-quality ranking. Both run locally without a paid API or private reference voice. Keep their native runtimes separate; model weights are not bundled with this skill.

## Choose and direct a take

Kokoro remains the default `engine` when omitted. Its existing `voice`, `language` and `speed` controls apply; it has no learned emotional instruction control. Do not imply that changing playback speed creates an acted performance.

Qwen uses the already downloaded **Qwen3-TTS1.7B CustomVoice4bit** conversion through the retained **MLX-Audio0.5.8** runtime on this Mac. The exact model revision and local hashes are retained in its configuration/provenance. CustomVoice presets support delivery instructions. VoiceDesign and Base cloning are separate models and are not installed by this adapter.

```json
{
  "engine": "qwen", "fps": 30,
  "voice": "Ryan", "language": "English", "seed": 0,
  "temperature": 0.7, "max_tokens": 512,
  "segments": [
    {"id":"opening", "text":"The signal is back.",
     "instruct":"Calm relief, with clear natural phrasing.",
     "pause_after":0.4, "take":"v1"}
  ]
}
```

```sh
python3 <animation-root>/scripts/studio.py narrate /absolute/spec.json --out /absolute/project/audio/take-v1 --cache /absolute/project/audio/cache
```

Qwen supports per-segment voice, language, instruction, seed, temperature and token budget. `spoken` and top-level `pronunciations` let speech use a readable verbal form while captions retain the written form. No SSML or phoneme dictionary is implied. A seed improves repeatability within the pinned runtime; it does not guarantee identical speech after an engine/hardware change. Qwen rejects `speed`; direct its pacing with `instruct` and measure the result.

Use short editable passages: the helper caps each Qwen segment at35spoken words and300characters, based on the previous long-input omission and bounded-group repair. These are local adapter limits, not a universal model limit. For scripts without whitespace word boundaries, the character cap still applies. Do not split solely to maximize clip count: choose meaningful phrase/sentence boundaries and check joins. The worker loads one model for missing takes, serially, with a600second owned-process deadline; coordinate it with rendering on this Mac. The deadline cannot guarantee wall time through system sleep. Inference sets offline flags and never fetches missing weights. A missing dependency is an actionable error, not permission to auto-download.

## Revise, time and review

The helper retains dry24kHz mono takes, resampled48kHz stereo copies, frame-aligned assembled narration, `cues.json`, SRT and receipts. Use a fresh output directory. Identical takes reuse validated cached bytes; changing one passage/instruction/take regenerates only that identity. Model, settings, worker and runtime identity participate in Qwen cache keys. Preserve failed artifacts and use a new take ID when intentionally auditioning again.

Both engines reject unsupported spec/segment controls before generation; use the documented `pause_after` and `minimum_seconds` fields rather than guessed aliases. SRT serialization removes blank paragraph separators while preserving useful nonblank lines; original written text remains in `cues.json`. Qwen fingerprints the whole adapter, so an adapter code revision changes its cache identities even when a passage is unchanged. Preserve old cached takes; do not claim reuse across that boundary without checking the current identity.

Cues are measured phrase boundaries, not forced word alignment. For word highlighting or lip sync, acquire/test appropriate alignment or viseme tooling for that output; Whisper draft captions alone are not exact phoneme timing. Measure audio before setting shot lengths. A new engine's pacing cannot replace an older WAV while assuming the same synchronization.

Listen for omitted/extra words, names, numbers, consonants, pacing, intended expression, timbre consistency and joins. ASR can reveal suspected omissions; finite PCM, distinct waveforms and full decode do not prove acting quality. Retain clean stems, measured levels, room for music/effects and an intelligible final mix. Select a voice for the actual audience and story, not a brand claim.

For short English wording checks, run the CPU helper against a dry take or final media:

```sh
python3 <animation-root>/scripts/studio.py review-voice /absolute/take.wav --spec /absolute/spec.json --segment opening --out /absolute/review-v1
```

Alternatively use `--expected-file /absolute/spoken.txt`. Use a fresh output. The existing Whisper base.en model analyzes the full input without voice-activity detection (VAD, a tool that removes likely nonspeech) or an expected-text prompt. The local calm take's quiet opening was incorrectly excluded by VAD; full-input recognition recovered every word without altering the healthy audio. `--vad-diagnostic` retains a separate comparison when diagnosing that problem.

Read `review.json`: `wording_match` means normalized recognized words matched; `differences_flagged` lists likely substitutions/omissions/additions; `insufficient_signal` prevents silence from passing even if recognition hallucinates the expected words. Exit0 means the report completed, not approval. The helper preserves raw recognition, the written versus spoken form, pronunciation substitutions, source/runtime hashes and measured signal. It supports English input up to60seconds and80expected words/1000characters. It does not assess acting, intelligibility to a human, exact word timing, multilingual coverage or nonverbal events. Review discrepancies in the audio before regenerating; retry only the affected take when there is a real generation defect.

## Current alternatives and provenance

Primary research checked15October2026 selected existing Qwen as the practical expressive audition on M4/32GB. The current **MLX ChatterboxTurbo4bit** card documents a default voice and approximately417MB snapshot; it is a promising untested challenger, especially for nonverbal events. Full original Turbo is a different download. FishDrama3's published41.5GB snapshot is not an unquantized fit on32GB merely because only3B parameters are active. FishS2-Pro remains noncommercial/research; Drama's conditional Community terms differ. Inspect actual artifact terms, all dependent downloads and the runtime before proposing a model trial. Do not infer model/voice rights from an application's license.

Retained task evidence: `outputs/studio/research/voice-current-20261015.md`, `voice-audition.html`, `voice-provenance/runtime.json`, and `unified-skill/qwen-adapter-proof/`. These are dated evidence, not a permanent ranking. Use [on-demand discovery](discovery.md) when a real requirement or changed blocker warrants another option. No background upgrade, new weights or provider is enabled.
