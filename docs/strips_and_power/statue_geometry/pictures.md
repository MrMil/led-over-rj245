# Layout tool: pictures, cuts and the LED render

Path: [docs](../../README.md) › [strips_and_power](../README.md) › [statue_geometry](README.md) › **pictures**
Parent: [README.md](README.md)
**Covers:** the four viewpoints, projecting a picture onto the faces, cut masks and islands, the LED render and the show registry, DXF export, `?load=`.

## Pictures, cuts and the LED render (owner, 2026-10-21: one page, not two)

The projection maker was built as a second page on 2026-10-21 and folded into this page the same
day (owner: "I want just one page, the LEDs in the layout decider, the actual cut when moving the
statues"). Four viewpoints each own 14 faces: the bench seat facing a statue owns its inner faces
(the two that look at the centre), a back viewpoint on the apex axis behind the apex tower (owner's
choice over the centre or the circle edge; default 3 m, eye 1200 mm, field of view 90° from the final layout) owns the
outer faces. A picture per viewpoint, raster (white is wood, the rest is cut and lit; a pixel is
wood above 90 % luminance, transparency counts as white) or DXF (inside the closed shapes is cut;
polylines, lines, circles, arcs and splines, open chains joined by endpoint), is stretched to the
silhouette of the 14 faces as seen from that eye, shrinkable from left / right / top / bottom
(owner), and projected onto the faces. Moving a tower re-projects its cuts; masks are cached per
face so a slider only recomputes what it touches. The page opens with the demo smiley on all four viewpoints (owner, 2026-10-23: "leave the smiley faces for now": the artist is drawing different art). **Changed 2026-10-23:** from 2026-10-22 the page opened with the four generated pictures when it could fetch them; they were made for the previous layout and are superseded ([../art/README.md](../../art/README.md)).

- **A picture fits the whole silhouette of its 14 faces from the viewpoint, the tip towers' feet
  included** (owner, 2026-10-21: "the whole point of this tool is to help us create an image that
  would be displayed on all towers"). The artist draws for that box and pulls it in with the shrink
  controls. Two band fits remain as options (the height every face of T2–T6, or of all seven, can
  show); they were briefly the default on 2026-10-21 and rejected by the owner the same day.
- **Each face gets its own wood canvas at its aspect; no texture repeat** (agent, 2026-10-21). In
  three r128 the colour map's repeat/offset transform is applied to the alpha mask too, so a
  repeated wood texture stretched the cut pattern by height over width. This bug is why the
  projected smiley was unreadable before.
- **Statue 2 has its own viewpoints by default** (owner, 2026-10-23: the artist will work on the
  viewpoints and must be able to upload each picture without unticking anything): "Statue 2 uses
  statue 1's pictures and viewpoints" starts unticked, and all four viewpoints start with the same
  smiley and settings, as in the owner's file. Ticking it makes statue 2 mirror statue 1 (same
  picture, insets, eye, distance and field of view; owner, 2026-10-21: "if I upload a file to one
  view it should look identical on the other view"). **Changed 2026-10-23:** previously ticked by
  default. Briefly the same day an agent kept it ticked against the owner's file, reasoning that
  the copies looked identical; the owner had unticked it on purpose.
- **The unlit base and the face border (default 20 mm, measured on the wood) are always wood**
  (agent): no LED sits behind the base.
- **Wood islands are reported per face, never fixed** (owner): a wood region not connected to the
  plate edge, on the 2 mm mask, specks under ~4 mm² ignored; faces are named A/B (inner, left/right
  from the bench) and C/D (outer, left/right from behind) so the message names a physical face.
- **LEDs are a diffuser one plate thickness behind the cut face** (owner: thickness 6 mm default).
  Each LED lights the line opposite it and blends additively with its neighbours over one pitch, in
  a shader fed by one small colour texture per tower; all four faces share the strip as in the real
  wiring.
- **The LEDs are a light source, not a lit texture** (owner, 2026-10-25: "a source of light and not just a
  colourful matte piece"). Two things make that: a bloom pass over the frame (Three.js `UnrealBloomPass`, loaded
  from the same CDN as the controls), so lit faces glow past their edges, and one point light inside every tower,
  coloured each frame by the mean of its LEDs and scaled by how much strip is lit, so the ground and the
  neighbouring wood take the colour. The `LED glow` slider scales both; the constants behind it (`GLOW` in the
  page) were set by eye on the drone view. The bloom threshold stays above anything the point lights can make
  the wood, so only the diffusers bloom: the first values (night 0.7 at threshold 0.4) bloomed the lit wood too
  and the halo filled the cut shapes, which hid the picture (owner, 2026-10-25: "I don't see the smiley now").
  By day both are off (owner, 2026-10-25: "the sun is so much stronger than LEDs"; the first version lit the
  floor by day, which looked wrong); the glow exists at night only. The render goes through an
  `EffectComposer` with a multisampled target where WebGL2 allows, so edges stay smooth; `Save PNG` reads the
  same canvas. Point lights cast no shadows: fourteen shadow maps would cost more than the look is worth.
- **Night has no sunlight** (owner, 2026-10-25). The sun is off and a faint starlight hemisphere keeps the wood
  and the ground legible; the LEDs are the only real light. **Changed 2026-10-25:** previously night kept a dim
  blue sun (0.15) so the towers stayed visible; the point lights now do that where the show reaches, and the
  owner asked for a night with no sun.
- **The LED show is a registry of animations, and the moving rainbow is its first entry** (owner,
  2026-10-21: "a slowly moving rainbow … the basis for the future animations work"). Each entry is
  a `frame(ctx)` function called once per tower per frame with the time, the tower, its LED count and
  an RGBA array in strip order, bottom to top (LED 0 at the foot of the tower), the same order the
  controller sends
  ([../firmware/README.md](../../firmware/README.md)), so an effect written here maps one-to-one onto the
  real LEDs. The registry is also `window.statueAnimations`, so a script can add a show without
  editing the page. Entries: rainbow (default, 0.15 cycles/s), a chase as a template, all white,
  off. **Shows compute as if every tower had the tallest tower's LED count** (owner, 2026-10-21):
  LED i is the same colour on every tower at the same height, and a shorter tower simply ends
  earlier, so the picture stays consistent across the V. The call also carries the tower's offset
  into the controller's one logical strip, for porting 1D WLED effects. The speed slider is the one time base; a future show reads it from `ctx.params`.
  **Since 2026-10-25 the same select also lists every WLED effect of the controller's firmware**
  ("WLED · Solid" first), run by the firmware's own code compiled to WebAssembly (`tools/wled_wasm/`)
  once per frame over the whole segment and scattered to the towers, with WLED's own controls on the
  Animations tab; why and how in
  [../../firmware/effects_in_browser.md](../../firmware/effects_in_browser.md).
- **DXF export is R12 POLYLINE/VERTEX, mm, layers OUTLINE and CUT** (agent: the dialect every laser
  program reads), traced from a 1 mm mask, simplified and smoothed once; one file per face, zipped
  per viewpoint, tower, statue or everything, with a manifest of sizes and island counts. For the
  generated pictures this export is superseded: their cut files are written as vectors by the
  generator ([../art/README.md](../../art/README.md), `art/dxf/`), because a trace of a mask is never
  smooth; the export remains for pictures uploaded by hand.
- **Pictures travel in the layout JSON** (owner: one file; version 3 adds `params.projection` with
  the viewpoints, insets, border, thickness and the pictures as data URLs or DXF text; version 4
  only changes the derived `leds_power` block to the neighbours-only supply grouping). Versions 1
  to 3 load as before. The browser store drops the pictures if they exceed its quota.
  `tools/embed_pictures.py` writes the generated pictures into the file ([../art/README.md](../../art/README.md)).
- **`?load=<url>` opens a layout JSON by link** (agent, 2026-10-22): headless renders and shared
  links can show the real handoff file with its pictures, instead of the page defaults and the demo
  smiley. Like every URL parameter it is never written to the browser store, and `?dump=1` waits
  for it, so `?load=...&dump=1` round-trips the file through the page.
- **Pictures are kept at up to 4096 px on the long side (`PICTURE_MAX`), raster and DXF alike**
  (owner, 2026-10-22: the cuts must not be pixelated). At the previous 2048 the apex tower seen from
  the bench got 3.5 mm per picture pixel, coarser than the 2 mm mask cells; 4096 keeps every face
  under 2 mm per pixel. Reason for the old cap: unknown, presumably memory; 4096 × 2691 loads in
  well under a second.
- **Her distances ride the solver's rails** (owner, 2026-10-21): the default layout takes the six
  spacings of her file (1200 / 1700 / 1300 / 2200 / 1500 / 1000 mm since 2026-10-23) as hand-set
  pairs and places the towers with the touching solver from the bench, because she placed them to
  look like a solved statue. Her 2026-10-23 file is itself on the rails (no free positions), so
  `?free=1` starts free dragging from its solved positions; it used to show the raw positions of
  her 2026-10-21 file, which no longer exists as a layout (agent, 2026-10-23).

## Related

- [README.md](README.md) — the tool.
- [../../art/README.md](../../art/README.md) — the generated pictures (superseded).
- [../../firmware/effects_in_browser.md](../../firmware/effects_in_browser.md) — the WLED effects that run in this LED render.
