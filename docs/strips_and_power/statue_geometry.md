# Statue geometry and sightlines

Path: [docs](../README.md) › [strips_and_power](README.md) › **statue_geometry**
Parent: [README.md](README.md)
**Code:** `tools/statue_render.html` (layout solver, mural projection, two camera views), `renders/*.png`
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
(horizontal field of view 100°, eye 1.6 m) and a drone view with a 1.75 m figure at the centre,
and prints per tower: distance, azimuth, angular gap to the neighbour, top elevation and the angle
its lit part subtends. Headless Chrome produced `renders/*.png` from URL parameters (`view`,
`side`, `h1`–`h7`, `smin`, `smax`, `sopt`, `d`, `clear`, `eye`, `fov`, `shot=1`).

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

## Findings (agent, 2026-10-19; for the owner and artist to confirm)

- **Touching silhouettes, Ø 8 m and 1.5 m spacing cannot all hold.** Three steps of 1.5 m from a
  4 m radius cross the centre. With exact touching the arm must point almost at the viewer, so the
  spacing is capped: 1.0 m puts the tip tower's nearest corner 0.97 m from the centre, 1.1 m puts
  it at 0.6 m, 1.3 m has no solution. With the defaults (optimum 1.5 m, 0.9 m free at the
  centre) the solver settles on 1.0 m.
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
- **Drone-view labels are a third the size of eye-view labels** (owner, 2026-10-19): at full size
  they hid the towers.
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
