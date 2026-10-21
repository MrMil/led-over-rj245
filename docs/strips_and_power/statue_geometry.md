# Statue geometry and sightlines

Path: [docs](../README.md) › [strips_and_power](README.md) › **statue_geometry**
Parent: [README.md](README.md)
**Code:** `tools/statue_render.html` (layout solver, mural projection, three camera views, LED/supply calculator, JSON export/load), `layout/statue-layout.json` (the handoff file), `renders/*.png`, `index.html`, `.nojekyll`
**Covers:** where the 14 towers stand inside the 8 m circle, what a viewer at the centre sees, and
the 3D check that the owner and the artist use to judge the tower heights. Not the wiring between
towers ([trenches.md](trenches.md)).

## What it does

The owner's constraints (owner, 2026-10-19): every tower is a 400 × 400 mm box; one corner of each
tower points at the centre of the circle; towers are 1–2 m apart, 1.5 m preferred; seen from the
centre, the silhouettes of neighbouring towers touch, so the cut pattern reads as one picture (a
smiley per statue); the whole piece fits a circle of exactly 8 m diameter.

`tools/statue_render.html` is a self-contained Three.js page (open it as a file, or the published
artifact). Its inputs, each a slider plus a text box in mm (owner, 2026-10-19): tower side length,
the seven tower heights, minimum / maximum / optimum spacing, circle diameter, plus the free radius
the viewer keeps at the centre, eye height and field of view. It solves the arm of a statue from
the apex outwards: the apex tower's far corner sits on the circle, and each next tower is placed at
the chosen spacing at the azimuth where its silhouette exactly touches the previous one. The
spacing used is the optimum if that solution fits (inside the circle, tip tower clear of the free
radius), otherwise the largest spacing that fits, clamped to the minimum; the panel says which.
**Compute heights for a level top line** sets T1–T3 and T5–T7 so every top sits on one line from
the eye, keeping T4; this is the artist's actual goal (owner, 2026-10-19). The page then projects
the smiley from the eye point onto the faces that look at the centre, renders the eye view
(horizontal field of view 100°, eye 1.6 m), a drone view with a 1.75 m figure at the centre and a
top-down plan (orthographic, 1 m grid, a "1 m" bar at the bottom right), and prints per tower:
distance, azimuth, angular gap to the neighbour, top elevation and the angle its lit part
subtends. Headless Chrome produced `renders/*.png` from URL parameters (`view=centre|drone|top`,
`side`, `h1`–`h7`, `smin`, `smax`, `sopt`, `p1`–`p6` with `manual=1`, `d`, `clear`, `eye`,
`fov`, `shot=1`), and `?dump=1` prints the export JSON instead of the page.

### Individual spacings

The six pairs T1–T2 … T6–T7 each have their own control (owner, 2026-10-19). Until one is
touched they show the solved spacing; once the user edits one, the layout is "set by hand": the
solver no longer overwrites the pairs, and each arm is solved with its own three chords (left
arm T4→T3→T2→T1, right arm T4→T5→T6→T7), so the two arms may differ. Changing minimum, maximum
or optimum then asks before resetting the pairs, because hand-set values are deliberate; "keep
mine" also puts the three range values back. The page's own confirmation box is used because
`confirm()` returns false inside hosted viewers.

### Statue 2 on its own, free positions, undo

- **Statue 2 mirrors statue 1 until "Set statue 2 separately" is ticked** (owner, 2026-10-19, for
  the artist: move everything together first, then decouple). Ticking it copies statue 1's
  heights, pair spacings and positions into statue 2, which then has its own controls, its own
  mural projection, its own level-top heights and its own LED/supply side. Unticking asks first
  when statue 2 differs, because it loses those settings.
- **Towers can be dragged freely in the top-down view, and in the eye and drone views with the
  "Drag towers" toggle on** (owner, 2026-10-19; the toggle sits with the view buttons). The toggle
  takes the left button and the single finger away from the camera, so right-drag, the pad and
  the keys still move the camera while towers are being placed. The first drag
  snapshots the solved positions; from then on the solver is bypassed, the pair boxes only report
  distances, and the readout checks the circle and the free radius as before. Towers keep one
  corner to the centre wherever they stand, because the mural is still read from there. Dragging
  a tower while coupled moves its mirror on statue 2. Any solver setting (spacing range, circle,
  free radius, side, arm method or angle) asks before re-solving, exactly as for hand-set pairs;
  "keep mine" puts the setting back.
- **Undo and redo keep a stack of parameter snapshots**, one per change that rebuilt the layout
  (owner, 2026-10-19). A slider drag collapses into one step (same control within 0.8 s). Undo
  restores through the same loader as the JSON file, so it is as complete as the export. The stack
  is per page load; the browser store keeps only the latest state.
- **Cameras** (owner, 2026-10-19: as in 3D software, with a pad so it works on a phone). Eye view:
  left-drag looks, right-drag or arrows/WASD walks; the eye height slider keeps the walked
  position. Drone: left-drag orbits, right-drag or arrows pans, wheel zooms. The on-screen pad
  does the same by touch. Pressing the active view's button, or ⟲, resets that camera.

### The JSON handoff file

**Export / Load** writes `led-over-rj245/statue-layout` version 2 and reads versions 1 and 2
(owner, 2026-10-19: the artist has saved version 1 files, so they must keep loading; a version 1
file simply has no `statue2` and no `free_positions_mm`, which read as "mirrors" and "solved").
Version 2 adds `params.statue2` (null while mirrored), `params.free_positions_mm` (plan x/y per
tower, null while solved), per-statue `level_top_heights_mm` and `leds_power.side_2`. The file
comes back into this repository for the field blueprints and the LED order. It holds
every input under `params` (so a load restores the page exactly), the solved layout under
`layout` (per tower: height, lit length, LEDs per face, `r_mm`, `azimuth_deg`, plan `x_mm`/`y_mm`
with statue 1's apex on +y and azimuth clockwise from it, box yaw, spacing to the next tower,
full-white current) and the per-side and both-sides totals under `leds_power`. Derived values
are ignored on load. The current export lives at `layout/statue-layout.json`; regenerate it
with `?dump=1` (see the Hosting section's headless command in git history, or the dump line in
the page) rather than by hand. **Not done yet:** `tools/wiring_diagrams.py` still carries its own
`TOWER_H`; reading heights from this file is the natural next step once the artist's layout is
final.

### LEDs and power supplies

The **Compute LEDs and power supplies** button (owner, 2026-10-19) takes the current heights and
its own inputs (unlit base per face, LEDs per metre, mA per LED, current ceiling per supply, reel
length; defaults from [led_power_budget.md](led_power_budget.md): 150 mm, 60/m, 29.4 mA, 18 A,
5 m) and reports per side and for both sides: metres of strip, reels, and supplies.
- **Reels are bin-packed with whole face strips** because every face is cut whole from one reel,
  no joins ([tower_layout.md](tower_layout.md)); first-fit decreasing, so a 2.6 m tower takes 4
  reels. The both-sides figure also shows what pooling offcuts across the sides would save.
- **Supplies are bin-packed with whole towers**: no tower may be fed by two supplies (owner,
  2026-10-19). The count is the exact minimum (search over 7 towers); the grouping shown prefers
  neighbouring towers on one supply when that reaches the same count, because each supply sits by
  the towers it feeds ([power_distribution.md](power_distribution.md)).

### Hosting

**Published on GitHub Pages from the `main` branch root** (owner, 2026-10-19: the artist uses
it). `index.html` at the repo root only redirects to `tools/statue_render.html`, and `.nojekyll`
stops Jekyll from processing the site, since nothing here is a Jekyll site and it would only add
build time and surprises. The same file is also published as a private claude.ai artifact.

## Final layout (artist, 2026-10-21)

`layout/statue-layout.json` is the artist's export of 2026-10-21 and the project default in
the tool (owner: the build must be finished within a week, so these are the sizes). Heights
1100 / 1400 / 1700 / 2000 mm; towers placed by hand (free positions, so the solver is bypassed
until "Reset to the solved layout" or `?solved=1`); circle Ø 18 m, apexes 17.4 m apart
(8.7 m from the centre), tips 4.1 m from the centre, 2.35 m kept free; eye 1200 mm (a seated
audience); spacing range 1000–3000 mm with hand-set pairs 1120 / 1590 / 2200 / 1340 / 1760 /
1102 mm. Statue 2 mirrors statue 1. Consequences recorded elsewhere: LED counts and currents
([led_power_budget.md](led_power_budget.md)), trench segments ([trenches.md](trenches.md)),
the CAT5e length ([../data_link/cabling.md](../data_link/cabling.md)).

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
  inner side is where the next tower stands.
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
  ([tower_layout.md](tower_layout.md)); a straight arm can only satisfy it for one pair of towers.
  A straight-arm mode with an angle slider stays in the page for comparison.
- **The mural is defined in the viewer's angular space and sampled per texel** (agent,
  2026-10-19), so the cut shapes are perspective-correct from the centre by construction, and the
  tower edges fall wherever they fall in the picture, as the owner described the artwork.
- **Outer faces repeat the pattern of the face opposite** because every face of a tower shows the
  same pixels ([tower_layout.md](tower_layout.md)).
- **Three.js r128 from a CDN, no build step** (agent, 2026-10-19): the page must open as a plain
  file on the owner's machine and publish unchanged as an artifact, whose allow-list permits only a
  few script hosts.

## Gotchas

- The page needs network access once for the Three.js scripts.
- The render's field of view is rectilinear; a real eye is not, so the tip towers at the frame
  edges look more stretched than they will in life.
- Nothing here is confirmed by the owner or the artist yet. The spacing, the arm shape and the
  heights are all open ([TODO.md](../../TODO.md)).

## Related

- [tower_layout.md](tower_layout.md) — tower order and heights, one channel per tower.
- [trenches.md](trenches.md) — cable runs along the arms, whose lengths follow from this layout.
