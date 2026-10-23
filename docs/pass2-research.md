# Animation improvement pass, 23 October 2026

This follow-up builds on the existing animation helpers and current skill entrypoint. No new framework, font, theme, credential, billed API, background service or renderer was installed.

## Selected transfers

| Source mechanism | Decision and reason |
| --- | --- |
| Original gallery prompts for closed-form repeated spring retargets | Add a small optional scalar helper. Direct evaluation preserves velocity during target changes while permitting backward/offline sampling. It is limited to a fixed underdamped linear spring, with explicit parameters and zero initial velocity. Independent numerical integration provides a falsifiable reference. |
| Motion Canvas named time events, Particle Beach shared edit/audio metadata, Remotion sequence offsets and transition overlap | Add conditional advice to author meaningful cues once and distinguish local, global and overlap clocks. Use existing labels/markers/native project code; installing those frameworks just for this mechanism adds cost. |
| Hallmark/Impeccable artifact-first critique | Judge the actual sequence before its builder's rationale or linter findings. Tie a material finding to a time, visible symptom, audience consequence and source correction. Preserve strengths and scope; no mandatory review rounds or scores. |
| Functional interaction feedback | Separate input acknowledgment, pending work and actual completion. Keep routine controls interruptible and avoid treating a display change as proof that an operation succeeded. |
| Actual DESIGN.md specimens | Preserve reference identity and distinguish observations from inferred or unseen behavior. A third-party style catalog does not establish easing, hidden states, proprietary font rights or a universal palette. |
| Local browser diagnostic source | Add explicit significant-time samples. A 300ms authored action at 2.0–2.3s in a 12s composition was invisible at all default samples. The new option targets those moments and records the schedule; default evidence remains limited. Retain only necessary decoded checkpoints instead of all frames. |

## Primary sources inspected

- [Original gallery, commit 92aee2f](https://github.com/yihui-dev/awesome-opus5-5-videos/tree/92aee2f586ac0715cb3cbcb6384834f98a33383d), especially [twoclipping-402193](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/92aee2f586ac0715cb3cbcb6384834f98a33383d/prompts/twoclipping-402193.md) and [verbove-268381](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/92aee2f586ac0715cb3cbcb6384834f98a33383d/prompts/verbove-268381.md). Duplicate prompts do not provide independent corroboration.
- [Motion Canvas time events](https://motioncanvas.io/docs/time-events/) and [v3.17.2 scheduling source](https://github.com/motion-canvas/motion-canvas/blob/v3.17.2/packages/core/src/flow/scheduling.ts).
- [Particle Beach shot metadata](https://github.com/ishuagrawal/particle-beach/blob/92db82255b962acf2930f19bf6e5e7790174a790/js/trailer-shots.js) and [audio source](https://github.com/ishuagrawal/particle-beach/blob/92db82255b962acf2930f19bf6e5e7790174a790/js/trailer-audio.js). Source inspection, not local reproduction.
- [Remotion v4.0.534 frame-offset implementation](https://github.com/remotion-dev/remotion/blob/v4.0.534/packages/core/src/use-current-frame.ts), [transition documentation](https://www.remotion.dev/docs/transitions/transitionseries) and [current terms](https://www.remotion.dev/docs/license).
- [Awesome DESIGN.md, commit 3b60532](https://github.com/voltagent/awesome-design-md/tree/3b605329240ce735b510037cca322f1831fdd7f8), including Apple, Linear and Runway specimens. MIT repository terms do not grant rights to every named brand's assets.
- [Hallmark finish review](https://github.com/Nutlope/hallmark/blob/7ec868225c6caa040558c321ee0fefa0e73f83a8/skills/hallmark/references/review-finish.md) and [browser renderer](https://github.com/Nutlope/hallmark/blob/7ec868225c6caa040558c321ee0fefa0e73f83a8/skills/hallmark/scripts/sloplint-render.mjs#L109-L137), MIT. The renderer sets reduced motion before capture; those stills cannot establish ordinary choreography.
- [Impeccable animate guidance](https://github.com/pbakaus/impeccable/blob/a05436993fc753ec9a302f0db8d395025b246633/.agents/skills/impeccable/reference/animate.md), [critique](https://github.com/pbakaus/impeccable/blob/a05436993fc753ec9a302f0db8d395025b246633/.agents/skills/impeccable/reference/critique.md) and [NOTICE](https://github.com/pbakaus/impeccable/blob/a05436993fc753ec9a302f0db8d395025b246633/NOTICE.md), Apache-2.0 with identified MIT-derived platform material.

The new helper is original code implementing linear superposition; no framework implementation or prompt prose was copied. Guidance is original synthesis with provenance above. Existing bundled third-party terms remain unchanged.

## Deferred or rejected

A framework is useful when its native components, timeline or renderer solve a current need. There is no measured throughput or editable-source blocker in this pass. Remotion, Motion Canvas and Blender remain viable per brief; existing sources do not need migration. [fframes v1.3.0](https://github.com/dmtrKovalenko/fframes/releases/tag/v1.3.0) has interesting native rendering/cache mechanisms, but no local matched performance evidence justified a Rust/Skia setup or rewrite.

Do not import palette/font bans, a fixed number of motion primitives, novelty/ornament quotas, mandatory dual reviews, approval records, self-scoring loops or remote concept-seed services. An aesthetic detector is an advisory about its own preferences, not evidence of physics or viewer comprehension.

The sources were read at the cited versions. No cited third-party application was executed and no broad aesthetic-superiority or new-renderer performance claim is made. New behavior is checked on the changed helpers and a current-source representative artifact; older validation remains historical evidence.
