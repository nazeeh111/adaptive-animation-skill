# Animation research: findings for the skill revision

Reviewed 21 October 2026. This report distinguishes source observations from proposals. No third-party animation was executed and no full video was perceptually reviewed. No model-quality comparison was performed.

## What the supplied collection establishes

The collection is a discovery surface of shared prompts and linked remakes. Its README reports 703 prompt entries and 418 live remakes, with a latest update dated 12 October 2026. It explicitly says that some entries are incomplete prompts or descriptions of results. These counts are publisher claims, not audited success rates. The collection cannot establish that one model, tool, prompt formula or workflow universally produces better animation.
Source: https://github.com/yihui-dev/awesome-opus5-5-videos

The supplied X URL returned HTTP 403 through normal access. Its content and age remain unverified. No alternate access was attempted.
Source: https://x.com/kingao476942/status/2112729924943634602?s=46

## Representative originals, not just the README

- Product launch prompt asks for an identifiable real SaaS and its actual assets. Transfer: ground the demonstration in authentic product behavior. Do not transfer its assumption that internet assets may be freely republished.
  https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/moritzkremb-466494.md
- Short inference-startup explainer is essentially one sentence requesting polish. Transfer: the skill must supply audience, visual mechanism, proof of benefit and readable timing that a sparse prompt omits.
  https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/deedydas-252537.md
- Showreel prompt explicitly connects kinetic type, 2D/3D, effects and camera through coherent direction rather than a random effect montage. Transfer: dynamic means a changing visual idea with hierarchy and continuity, not maximizing simultaneous motion.
  https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/lukasersil-726495.md
- 1906 Market Street prompt asks for building facts tied to archival sources and reusable procedural generators before the shot. Transfer: visual research should become actual scene parameters with confidence where historical or scientific fidelity matters. Its remake tags say Three.js although the original asks for Blender. Gallery tags are not trustworthy evidence of the original production method.
  https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/alexalbert-274839.md
- Deterministic butterfly entry describes independent frame evaluation, explicit canvas/fonts/encoding, and a seam check. It is written as a narrative report with claimed counters, not a released validator. Transfer the frame contract; do not import its claimed six-zero validation as proof. Frame zero matching the mathematical endpoint alone does not establish continuous velocity or the perceptual seam.
  https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/0xkarmi-129839.md
- GSAP entry specifies distinct card/title/metadata timing and Playwright frame inspection. Transfer differentiated timing roles and targeted repair. The particular millisecond values fit that UI example, not every medium.
  https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/fleyta88-443662.md
- Brake-pedal entry is a creator report in Chinese describing Three.js, a shader stress map, progressively growing fracture and bilingual subtitles. It supplies no material model, loads, solver, validation or uncertainty. Transfer causal staging and language support; a colorful shader must not be called physically solved stress.
  https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/chang-200908.md
- Particle beach entry explicitly admits two or three additional prompts and links actual source. Transfer iterative direction; do not label the shown result a demonstrated one-prompt output.
  https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/ishuagra02-678129.md

## High-value changes beyond the existing skill

Existing SKILL.md plus production/styles/typography/editorial/character references already cover native sources, technique choice, deterministic offline time, actual modality limits, local fonts, reduced motion, interrupted controls, color/alpha, authored performance, recovery and proportionate checks. Preserve that coverage. Avoid another mandatory research/test/delegation apparatus.

### 1. Make dynamic direction actionable

Proposed guidance: Identify the main visible change in each beat, what the audience follows across that change, and where it settles long enough to understand. Give dominant action, supporting response and background different timing roles. Vary motion density and scale across the sequence. Carry identity through transforms when it represents the same thing; use a cut or dissolve when a morph would falsely imply continuity. Choose pauses and contrast intentionally. An arbitrary rule that something must move every few seconds can undermine clarity.

Primary basis: Mike Bostock's object-constancy explanation demonstrates stable data identity across reorderings and warns that unrelated data should not fly through misleading transitions.
https://bost.ocks.org/mike/constancy/

Foundational counterevidence: Tversky, Morrison and Betrancourt (2002), Animation: Can It Facilitate?, distinguishes semantic fit from perceptual clarity. Its analysis of teaching complex systems cautions against fast, complex motion and confounded claims of learning gains, and suggests learner control. This is not current evidence against animation generally, nor a result about entertainment/showreels.
https://www.tc.columbia.edu/faculty/bt2158/faculty-profile/files/_Morrison_Betrancourt_AnimationCanitfacilitate.pdf

### 2. Fix the subtle seek/callback trap

Official GSAP docs state that seek() suppresses callbacks by default and preserves the current paused/reversed state. A scene that creates essential objects in onComplete/onStart callbacks can look correct in playback and fail when captured out of order. Add route-specific advice: construct persistent visuals before capture, drive visibility/geometry from timeline state, or explicitly reconstruct callback-dependent state. Do not blindly use seek(t,false): replaying callbacks can duplicate objects or trigger sound/network effects. Pause the transport and test direct, repeated, backward and shuffled target times around actual scene boundaries.
https://gsap.com/docs/v3/GSAP/Timeline/seek()/

Remotion's official explanation confirms that parallel render tabs do not share state, and sequential frame dependence, unready assets, independent animation clocks and randomness cause inconsistent captures. Reducing concurrency is not a general synchronization fix.
https://www.remotion.dev/docs/flickering

### 3. Judge loop continuity, not just endpoint identity

Proposed check when a loop is requested: evaluate the mathematical endpoint against the start; inspect last encoded frame followed by first at normal speed; inspect nearby trajectories, velocity and audio continuity when material. Do not add a duplicate endpoint frame to the movie merely to force equality. A positional match can still have a speed kink, a dropped particle or an audible click. Use seeded periodic phases, time-wrapped noise or a baked repeat where appropriate.

This is an inference from the independent-frame contract and the difference between a sampled movie and its mathematical endpoint, not a claimed gallery measurement.
https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/0xkarmi-129839.md

### 4. Broaden browser performance from render completion to actual use

On a performance-sensitive browser brief, profile the target viewport/device before adding effects; prefer composited transform/opacity where they fit, and avoid layer promotion everywhere. Current web.dev guide warns that will-change itself can harm performance and should follow evidence. Do not mistake slow offline capture for interactive frame pacing.
https://web.dev/articles/animations-guide

Three.js official documentation explains render-on-demand for idle scenes and explicit disposal of geometry/material/texture resources. For interactive scenes that change projects/assets, stop obsolete loops/listeners, release owned resources and test repeated replay/rebuild. Rendering while animation is active is legitimate; on-demand is not a universal replacement.
https://threejs.org/manual/pages/rendering-on-demand.html
https://threejs.org/manual/pages/cleanup.html

### 5. Keep scientific truth separate from attractive shaders

Proposed guidance: name whether a visual is measured data, a numerical model, a qualitative illustration or an artistic metaphor. Bind units, scales and labels to authoritative numerical inputs; validate a few discriminating states or invariants. Show uncertainty or assumptions where they change interpretation. A stress-colored surface, orbital path or fluid appearance alone is not evidence of physical simulation.

Source motivating the gap:
https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/chang-200908.md

### 6. Expand the adjacent-image continuity lesson to data identity

Preserve the existing visual continuity section. Add a brief direct pointer for diagrams: retain node/entity keys and labels through sort/filter/reparent transitions; only morph entities that genuinely correspond. Dynamic flowcharts should reveal a causal process or comparison, not animate a static node wall arbitrarily.
https://bost.ocks.org/mike/constancy/

### 7. Make accessibility concrete without blanket requirements

Existing production text is good. If expanded, keep separate: pause/stop/hide for qualifying automatically moving content; reduced-motion support for nonessential interaction-triggered motion; caption/readable fallback for meaning; flash safety. WCAG 2.2 SC 2.2.2 applies to automatic motion lasting more than five seconds presented alongside other content, with stated exceptions. SC 2.3.3 is AAA. Do not say every five-second film is required to stop itself or that slowing an endless animation satisfies motion preferences.
https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide
https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion

## An actual source-level mechanism worth learning

Particle Beach publishes separate live and cinematic modes. Source inspection shows:
- Explicit shot records with duration in beats, local time, camera pose, lighting/look, ambience and effects, while scene geography stays shared.
- Offline frame rendering uses fixed subframe sampling with a declared half-open shutter.
- Stateful trails/waves are warmed before a shot. Seeking backward or changing shots rebuilds from the shot start, then advances the same substeps.
- The sound is generated with OfflineAudioContext from the same edit metadata and seeded noise.

Transfer the separation of editable world, authored shot clock and offline recording; keep each in its native representation. It is useful counterevidence to banning all stateful simulations. These are source observations, not a local replication or an endorsement of the film's visual/audio quality, performance, science or safety.
https://github.com/ishuagrawal/particle-beach
https://github.com/ishuagrawal/particle-beach/blob/main/js/trailer-shots.js
https://github.com/ishuagrawal/particle-beach/blob/main/js/trailer.js
https://github.com/ishuagrawal/particle-beach/blob/main/js/trailer-audio.js

## What I would not add

No permanent model hierarchy, fixed tool winner, mandatory expert swarm, absolute timing recipe, visual-effects quota, static-frame proof of full motion, claimed universal perfection, mandatory paid score/narration service, or unverified exporter coverage. Do not bundle third-party video clips or imply their prompt collection license clears creator media. Reuse mechanisms with attribution and preserve native project/source rights.
