# Statue geometry and sightlines

Path: [docs](../../README.md) › [strips_and_power](../README.md) › **statue_geometry**
Parent: [../README.md](../README.md)
**Code:** `tools/statue_render.html` (layout solver, four viewpoints, picture projection and cut masks, LED render, DXF export, LED/supply calculator, JSON export/load, `?load=`), `layout/statue-layout.json` (the handoff file: the artist's final layout, with the demo smiley), `renders/*.png`, `index.html`, `.nojekyll`, `.claude/launch.json`
**Covers:** where the 14 towers stand inside the 18 m circle, what a viewer at the bench sees, and
the 3D check that the owner and the artist use to judge the tower heights. Not the wiring between
towers ([trenches.md](../trenches.md)).

## What it does

The owner's constraints (owner, 2026-10-19): every tower is a 400 × 400 mm box (412 × 412 outside since 2026-10-23, [final_layout.md](final_layout.md)); one corner of each
tower points at the centre of the circle (since 2026-10-23 every tower is turned like its apex
instead, [controls.md](controls.md)); towers are 1–2 m apart, 1.5 m preferred; seen from the
centre, the silhouettes of neighbouring towers touch, so the cut pattern reads as one picture (a
smiley per statue); the whole piece fits a circle of exactly 8 m diameter.

`tools/statue_render.html` is a self-contained Three.js page (open it as a file, or the published
artifact). Its inputs, each a slider plus a text box in mm (owner, 2026-10-19): tower side length (the short pieces' width since 2026-10-23),
the seven tower heights, minimum / maximum / optimum spacing, circle diameter, plus the free radius
the viewer keeps at the centre, eye height and field of view. It solves the arm of a statue from
the apex outwards: the apex tower's far corner sits on the circle, and each next tower is placed at
the chosen spacing at the azimuth where its silhouette exactly touches the previous one. The
spacing used is the optimum if that solution fits (inside the circle, tip tower clear of the free
radius), otherwise the largest spacing that fits, clamped to the minimum; the panel says which.
**Compute heights for a level top line** sets T1–T3 and T5–T7 so every top sits on one line from
the eye, keeping T4; this is the artist's actual goal (owner, 2026-10-19). The page then projects
the smiley from the eye point onto the faces that look at the centre, renders the eye view
(horizontal field of view and eye height as set; defaults under Final layout), a drone view with a 1.75 m figure at the centre and a
top-down plan (orthographic, 1 m grid, a "1 m" bar at the bottom right), and prints per tower:
distance, azimuth, angular gap to the neighbour, top elevation and the angle its lit part
subtends. Headless Chrome produced `renders/*.png` from URL parameters (`view=centre|drone|top`, `pov=2` for the statue 2 eye, `bench`,
`side`, `h1`–`h7`, `smin`, `smax`, `sopt`, `p1`–`p6` with `manual=1`, `d`, `clear`, `eye`,
`fov`, `shot=1`), and `?dump=1` prints the export JSON instead of the page.

## Contents

- [`controls.md`](controls.md) — individual spacings, the arm methods (touching, straight, all at 45°), statue 2 on its own, dragging towers, undo.
- [`final_layout.md`](final_layout.md) — the artist's final layout as the default, the 400 / 412 mm box and its long faces, the bench.
- [`pictures.md`](pictures.md) — viewpoints, pictures projected onto the faces, cut masks, the LED render, DXF export.
- [`handoff.md`](handoff.md) — the JSON handoff file, the LED / supply calculator, hosting.

## Earlier findings (agent, 2026-10-19, on the 8 m circle that preceded the final layout)

- **Touching silhouettes, Ø 8 m and 1.5 m spacing cannot all hold.** Three steps of 1.5 m from a
  4 m radius cross the centre. With exact touching the arm must point almost at the viewer, so the
  spacing is capped: 1.0 m puts the tip tower's nearest corner 0.97 m from the centre, 1.1 m puts
  it at 0.6 m, 1.3 m has no solution. The owner then set the range to 500 / 750 / 1000 mm
  (2026-10-19); 750 mm fits with room to spare, so the defaults now solve at the optimum.
- **The artist's heights (950/1250/1600/2000) are proportional to distance only for an eye at
  ground level.** At 0.9 m spacing the ratio height/distance is nearly constant (0.53–0.59), which
  is what the heights seem designed for. But a standing viewer's eye is at 1.6 m, so a 950 tower
  1.3–1.6 m away is below the eye and its top drops out of the picture: the mural band shared by
  T2–T6 is 12° tall, and T1/T7 carry none of it. For every top to sit on one line from a 1.6 m eye
  the heights would be about 1720/1820/1910/2000 mm (apex kept at 2000); the page computes this
  for any eye height and spacing and can render it (`level=1`).
- **Each statue fills about ±57° of the view at 1.0 m spacing**, so the two statues leave two
  free sectors of roughly 65° at the sides for people to walk in.

## Decisions

- **The free radius at the centre is a parameter (default 900 mm)** (agent, 2026-10-19). Without
  it "closest to the optimum" would pick a spacing that leaves the tip towers 0.3 m from the
  viewer; the owner did not name this limit, so it is exposed rather than fixed.
- **Labels sit beside the towers, on the outer side, in the drone and top views; above the top
  only in the eye view** (owner, 2026-10-19: on the towers they hid them). Outward because the
  inner side is where the next tower stands. **Off by default** (owner, 2026-10-23); the "Tower
  labels" box or `?labels=1` turns them on, and they are not kept in the browser store.
  **Changed 2026-10-23:** previously on by default (`?labels=0` turned them off). Reason for the
  change: not recorded.
- **The last settings are kept in `localStorage` and restored on the next open; "Restore project
  defaults" clears them and reloads** (owner, 2026-10-19). URL parameters win over the store and
  are never saved, so headless renders and shared links stay deterministic. The store is a
  per-browser convenience: the page works without it, and the JSON export is the real record.
- **Eye height runs from 400 mm** (owner, 2026-10-19: the piece should work for people sitting).
  The level-top heights and the mural band follow the eye height, so a seated eye gives a different
  height set; the export records which eye height it was computed for.
- **The settings panel folds to a tab at the left edge** (owner, 2026-10-19) so the render can be
  seen whole; the folded state is kept in `localStorage` only, a per-browser convenience that the
  page works without.
- **The top-down camera sits at 25 m, under the fog start** (agent, 2026-10-19): at 60 m the
  scene fog greyed the plan out.
- **The 4 m radius is the apex tower's far corner, not its centre** (agent, 2026-10-19). "The
  diameter of the whole circle is exactly 8 m" reads as the footprint; the centre would put the
  corner at 4.28 m.
- **Arms are solved for exact touching rather than drawn straight** (agent, 2026-10-19). Touching
  is the condition that makes the mural continuous, which is the point of the artwork
  ([tower_layout.md](../tower_layout.md)); a straight arm can only satisfy it for one pair of towers.
  A straight-arm mode with an angle slider stays in the page for comparison, and since
  2026-10-23 a third method keeps every tower at the apex's 45° ([controls.md](controls.md)).
- **The mural is defined in the viewer's angular space and sampled per texel** (agent,
  2026-10-19), so the cut shapes are perspective-correct from the centre by construction, and the
  tower edges fall wherever they fall in the picture, as the owner described the artwork.
- **Outer faces repeat the pattern of the face opposite** because every face of a tower shows the
  same pixels ([tower_layout.md](../tower_layout.md)).
- **Three.js r128 from a CDN, no build step** (agent, 2026-10-19): the page must open as a plain
  file on the owner's machine and publish unchanged as an artifact, whose allow-list permits only a
  few script hosts.

## Gotchas

- The page needs network access once for the Three.js scripts.
- The render's field of view is rectilinear; a real eye is not, so the tip towers at the frame
  edges look more stretched than they will in life.
- The heights, spacings and bench are final (artist, 2026-10-23, [final_layout.md](final_layout.md)),
  so is the arm method, every tower at 45° like the apex ([controls.md](controls.md)). Open items
  are in [TODO.md](../../../TODO.md).

## Related

- [tower_layout.md](../tower_layout.md) — tower order and heights, one channel per tower.
- [trenches.md](../trenches.md) — cable runs along the arms, whose lengths follow from this layout.
- [final_layout.md](final_layout.md) — the current defaults.
