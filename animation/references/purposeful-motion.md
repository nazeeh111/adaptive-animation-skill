# Purposeful motion

Read when a film feels static, repetitive, hard to follow, or lively without meaning. A quiet character shot, a diagram and a fast product film need different rhythms. Dynamic means the viewer can follow change and consequence; a hold can be the strongest beat.

## Stage an action that earns the next image

Translate the subject into a visible verb: a signal chooses a route, force bends a beam, a hand transfers weight, a product completes a real task. Establish the starting relationship, show the decisive change, and let the consequence motivate the next shot. Reuse an object, shape, trajectory or sound across a transition when it helps the viewer carry meaning forward. A decorative match cut must not imply a false causal link.

Give the important action a clear silhouette and a stable place to read it. Assign one dominant change at a time unless simultaneous comparison is the subject. Let supporting motion lead or follow that action. Anticipation prepares attention; acceleration suggests force; settling and a hold make the result readable. These are choices, not a required effect stack.

When assessing a reference, note the relevant time span, what remains fixed, what moves, why the cut occurs, how long the viewer reads, and what sound contributes. Judge the actual sequence if accessible. A prompt list, remake tag or thumbnail cannot establish the original execution or its production method. Learn the mechanism and make original work.

## Rhythm at normal speed

Read the actual script against the animatic. Leave room to recognize a new object, understand a transformation and read its label. Alternate density where the subject needs it: setup, action, consequence, breath. Do not impose a universal cut interval, retention formula or demand that everything move. A looping background can compete with the only idea the viewer needs.

Use camera movement to reveal scale, a relationship or an unseen detail. Preserve orientation and a recognizable landmark through spatial transitions. Moving the camera, subject and labels together can remove the viewer's reference frame. A push-in and particles cannot repair a weak demonstration.

Review the opening, a representative transition and the payoff together. Compare before/after with the same timing and audio. If only still images are available, report visual staging evidence and leave rhythm or audio unverified.

## Animated flowcharts and explanations

Keep the diagram's topology, meaning which nodes connect, separate from its playback. Make arrows, branches and feedback truthful before animation. Introduce the context needed for a branch, show the signal reaching its cause, then reveal its consequence. Keep enough of the traveled path visible for orientation. Distinguish alternatives from concurrent operations through labels or staging. Color alone should not carry the distinction.

A moving token may illustrate a path, but it must not invent measured throughput, latency or a scientific result. Label illustrative timings. For a research method diagram, check sources and the entities/relationships first; use the available editable figure workflow when it helps. Keep an editable static diagram beside the film or interactive version when requested.

Use a resolved static view, transcript or meaningful stepping controls for a reduced-motion version. A permanently frozen entry frame can hide the entire explanation. In an interactive host, update on a changed motion preference and preserve essential state. Preview playback and fixed-frame export need separate timing behavior and checks.

## Reliable code-authored pictures

When a timing revision would otherwise touch scattered timestamps, name the meaningful cues in the existing project and derive the affected action, sound and captions from them. Native timeline labels, a small cue object or bound markers can suffice. Keep the intended reading/settling interval; do not force every action onto a beat or stretch speech to fit a visual preset. A marker alone does not retime unrelated keys or media.

Separate global edit time, shot-relative time and transition progress. Overlapping shots share part of the edit: 40 and 60 frames with a 30-frame overlap make 70 frames, while an overlaid effect need not shorten it. Avoid applying a shot offset twice. These mechanisms work in existing native sources; they do not require a framework change.

Offline rendering may evaluate frames in any order. Build each frame from explicit scene time, seeded inputs and authoritative assets, or seek baked state. Do not accumulate positions, emit particles on each seek, or treat a timeline callback as a durable drawing. GSAP seek suppresses callbacks by default. Prefer persistent visuals and explicit drawing; when callbacks are necessary, use callback-enabled evaluation and prove the image changes and restores after a backward seek. Repeated callbacks must not duplicate objects, retrigger sound or produce external side effects. A custom renderer may need an explicit draw function after timeline evaluation.

Wait for fonts, images and the relevant video frame before capture. Probe the first frame, the interesting action, the cut boundary and a repeated earlier time after a later one. Compare rendered pixels, not only the timeline clock. Procedural motion should include a saved seed. For stateful simulation, replay fixed inputs or bake the actual cache; an arbitrary seed does not by itself make a seekable simulation.

For repeated target changes in a replayable interaction, [retargeted motion](retargeted-motion.md) explains an optional fixed-spring track and when the native runtime is a better choice. For live or interactive work, make time and input behavior explicit instead of forcing an offline model. Use elapsed time rather than frames for variable refresh. Pause idle rendering when practical. Dispose of owned Three.js geometries, materials, textures and listeners when replacing a scene; removing a mesh alone does not release GPU resources. Profile the target runtime before adding workers or reducing quality.

For scientific work, identify measured data, a numerical model, a qualitative illustration or a metaphor. Bind units and scales to authoritative inputs and check discriminating states or invariants. A stress-colored shader is not evidence of a material solver or a validated engineering result.

For seamless loops, check the mathematical endpoint against the start and inspect the final encoded frame followed by the first. Check nearby trajectories, speed, particle state and audio where material. Matching positions can conceal a speed kink or click. Encode a half-open interval rather than adding a duplicate endpoint frame merely to force equality.

## Review the received story

When an interpretation check can change the result, let a reviewer encounter the actual passage before reading the builder's explanation or automated findings. Supply the audience, purpose and authoritative references. Ask what happened, what caused the next event and where attention went, then compare that account with the brief. A layout capture made with reduced motion does not show the ordinary choreography.

Tie a material critique to a time interval or interaction, its visible symptom, the audience consequence and a concrete source correction. Compare the revised passage at the same pace and check connected cuts or states. Preserve what worked. An attractive new preference alone does not justify reopening a resolved finding or an endless polish loop.

## Practical review questions

- Can the audience describe the action and consequence without the caption explaining missing action?
- Are direction, contact, subject identity and spatial orientation preserved across adjacent shots?
- Does each important label survive movement and stay visible long enough at actual output size?
- Are holds intentional, changes motivated and the ending complete?
- Do a loop seam, an interrupt, a resize or a backward seek break the specific delivery contract?

Choose only the checks relevant to the artifact. More activity and more automation do not establish better animation.

Primary technical sources: [GSAP seek](<https://gsap.com/docs/v3/GSAP/Timeline/seek()/>), [Remotion frame determinism](https://www.remotion.dev/docs/flickering), [Three.js disposal](https://threejs.org/manual/pages/cleanup.html), [W3C pause/stop/hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html). The craft direction here is synthesis, not a claim these sources prove a universal aesthetic.

Timing mechanisms: [Motion Canvas named cues](https://motioncanvas.io/docs/time-events/), [Remotion sequence offsets](https://www.remotion.dev/docs/sequence), [transition overlap](https://www.remotion.dev/docs/transitions/transitionseries). These sources inform authoring choices; no renderer comparison is implied.
