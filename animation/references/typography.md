# Typography that survives rendering

Choose faces for the subject and audience. The bundled Inter variable sans and Newsreader variable serif are options for clear text and editorial display; neither is mandatory. Brand fonts, licensed project-supplied fonts, drawn lettering and different visual languages are supported. Keep fonts local with license, source URL and file hash. Global installation is unnecessary. The two bundled OFL licenses permit embedding and redistribution under their stated terms. Files are unmodified; sources.json pins commits and hashes.

Distinguish display, supporting text, labels and captions with purposeful scale and spacing. Select weights rather than making everything bold. Author line breaks around phrases; check ascenders, descenders, accents, punctuation and tight pairs at the actual output size. A large display face can fail at small labels. Align numeric columns with tabular figures; keep mathematical symbols in a suitable math face instead of forcing them through a Latin display font. Non-Latin scripts need appropriate licensed coverage and shaping proof; these two fonts are not universal-script coverage.

## Browser motion

Use local `@font-face` aliases as the starter does. Declare the variable weight range and `font-synthesis:none`, so missing weights are visible rather than silently synthesized. Wait for font readiness in browser inspection. Verify actual rendered fonts through browser font/DOM inspection and compare final encoded glyphs. `document.fonts.check()` alone may return true for fallback, so combine it with the loaded FontFaceSet or actual platform font evidence and visual inspection. Do not fetch Google Fonts at render time.

Preview h1 plus body and numeric samples at each delivery aspect ratio. Check text boxes throughout motion, not just at rest: masks and transforms can clip glyphs, and a shared background may cross behind text. Keep essential information readable within platform-specific safe areas; write these for the placement rather than assuming one universal margin. Persistent captions need enough exposure at normal narration speed. A screenshot cannot establish reading pace.

## ManimGX0.1.1 on this setup

The pinned text API accepts DIRECTORY paths:

```python
from pathlib import Path
import manimgx as m
fonts = Path('/absolute/project/assets/fonts')
heading = m.Text('Light takes a turn.', font='Newsreader 16pt', weight='MEDIUM',
                 font_paths=[fonts], line_spacing=.16)
body = m.Text('One shared clock.', font='Inter', weight='SEMIBOLD',
              font_paths=[fonts], line_spacing=.16)
```

Typst currently resolves the downloaded Newsreader through its legacy family `Newsreader 16pt`. Requesting only `Newsreader` silently fell back in the CPU probe. The browser alias is independent of this native family name. When changing files or engine versions, probe a short sample and compare outlines/face resolution again. Include font hashes and any glyph adapter in cache keys. Tracking uses `typst_preamble='#set text(tracking: -0.01em)'`; check it optically rather than prescribing it globally.

Use dedicated math typesetting for equations. In the physics revision, Inter numeric glyphs need a project adapter because the default animated-number path chooses another face; retain the adapter in source and cache identity. Do not globally monkey-patch the engine.

## Blender/editor finishing

For Blender text load a project font into the native text object (`bpy.data.fonts.load(path)`), assign it, then save/package with its license. A font loading into Blender does not establish every variable axis or complex script shapes correctly. Inspect native glyphs; use a static licensed instance or vector outlines when native shaping is inadequate. Keep text editable where possible, preserving outlined source separately when baking is necessary.

Revise titles in a retained finishing composition when appropriate instead of rerendering unchanged expensive 3D frames. Resolve/Fusion title support and interchange can differ by font/version; compare receiving-side frames or bake a reviewed title to a suitable intermediate. Preserve the original editable title and font references.
