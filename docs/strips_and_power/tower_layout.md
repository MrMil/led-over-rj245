# Tower layout

Path: [docs](../README.md) › [strips_and_power](README.md) › **tower_layout**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`TOWER_H`, `TOWERS`, `GPIO`), `guide/setup.md` (layout table), `guide/build.md` (LED counts, strip cut list)
**Covers:** the towers of a statue and how their LEDs map onto channels.

## What it does

Each statue is a V of 7 towers, numbered T1–T7 from one tip to the other, T4 the apex:

| Tower | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
|---|---|---|---|---|---|---|---|
| Height (mm) | 1100 | 1400 | 1700 | 2000 | 1700 | 1400 | 1100 |
| Lit height (−150 mm base) | 950 | 1250 | 1550 | 1850 | 1550 | 1250 | 950 |
| LEDs per face at 60/m | 57 | 75 | 93 | 111 | 93 | 75 | 57 |

Heights: **final** (artist, via the owner, 2026-10-21: the build must be finished within a
week): 2 × 2000, 4 × 1700, 4 × 1400, 4 × 1100 mm, in this order along the V. The source is
`layout/statue-layout.json`, exported from the sightline tool
([statue_geometry/final_layout.md](statue_geometry/final_layout.md)), which also fixes where each tower stands.
**Changed 2026-10-21:** previously 950, 1250, 1600, 2000, 1600, 1250, 950 (2026-10-18), and
before that 800, 1150, 1550, 2000, 1150, 800, 500 mm, read off the owner's model photo.

Towers are 408 × 408 mm outside, 400 × 400 inside: two opposite sides are 400 mm pieces, the
other two 408 mm pieces that cover their edges, so the 4 mm wood thickness is accounted for
(owner, 2026-10-28: 4 mm plywood; which faces are long: [statue_geometry/final_layout.md](statue_geometry/final_layout.md#the-box-two-short-and-two-long-pieces-owner-2026-10-23)).
**Changed 2026-10-28:** from 2026-10-23 the wood was 6 mm and the box 412 × 412; the owner went
down to 4 mm, which re-solved the layout by a few millimetres and redid the art checks and cut files
([statue_geometry/final_layout.md](statue_geometry/final_layout.md#4-mm-wood-owner-2026-10-28)).
A structural post stands in the middle. Each face has one strip, mounted
on the post facing out, about 15 cm behind a diffuser and the CNC-cut face. **Each tower is
one channel; its 4 strips get the same data in parallel** through the tower-base splitter
([tower_base.md](tower_base.md)). Strips run bottom to top. Per statue: 561 rendered pixels,
2244 physical LEDs, 37.4 m of strip. Both statues: 4488 LEDs, 74.8 m, every face cut whole
from one reel (no joins): 15 reels of 5 m cut, the 16th kept whole as the spare (cut list in
`guide/build.md`).

## Decisions

### One channel per tower, same data on all 4 faces

**Why.** All faces show the same animation (owner, 2026-10-10). One channel per tower means
data never has to come back down from the top of a tower: no return wiring (owner, 2026-10-10,
the reason for the two-statue layout). The ESP32 renders one face per tower, 1122 pixels
for both statues, so frame rate is not a concern.
**Rejected.** *One strand per arm of the V* (2026-10-09): needed data to snake up and down
the towers. *Independent faces:* not wanted for the art.
**Changed 2026-10-10:** previously four statues, two channels per statue, strips chained.
**Constrains.** The 2-tower fallback (12 channels if 14 outputs fail) puts two towers on one
channel in parallel, so those two always show the same.

### No dividers inside the tower

**Why.** With one strip per face 15 cm behind a 40 cm-wide face, one strip alone lights the
face edges at only ~20–30 % of the centre. The mural spans tower edges, so that would show as
dark bands. With no dividers, each face's edges are also lit by the neighbouring faces' strips
at a steeper, more direct angle. That brings the edges to ~50 % and halfway out to ~75 %
(agent geometry, 2026-10-10; a line source on a plane falls off as cos³). Because all faces
show the same data, the light mixing at the corners is invisible (owner, 2026-10-10).
**Rejected.** *White X dividers from the post to the corners:* similar evenness, more build
work; only needed for independent faces. *Strips crossing the tower to the opposite face:*
the central post blocks the light (owner). *Two strips per face:* double LEDs and power.
**Constrains.** If faces ever need different content, light will bleed ~10–20 cm round the
corners. Evenness numbers are geometry estimates; check with the brightness mock-up
([led_power_budget.md](led_power_budget.md)).

### The cut list: 15 reels cut, one kept whole

**What** (agent, 2026-10-25). Three reel patterns, pooled across both statues: 8 × (93, 93,
57, 57), 4 × (111, 111, 75), 3 × (75, 75, 75, 75). 15 × 300 = 4500 LEDs for 4488 needed, so 12
LEDs are wasted, in 3-LED tails on the 111 reels. Pieces are labelled by LED count only, not by
statue or tower, because pieces of one count are interchangeable.
**Why.** 15 reels is the minimum (4488 / 300 = 14.96). An exhaustive search over every maximal
reel pattern found it; the layout tool's first-fit-decreasing packing
([statue_geometry/handoff.md](statue_geometry/handoff.md)) reports 8 per statue and 16 even pooled,
with the 312 spare LEDs scattered as tails of 3–129 LEDs. Cutting 15 leaves a whole 300-LED reel
instead, which yields two spare faces of any height in the field (111 + 111 + 75).
**Rejected.** *8 reels per statue, (93, 93, 57, 57) and (111, 75, 75):* keeps each statue on its
own reels, but spends the 16th reel on 8 tails of 39 LEDs, too short for any face. Statue-separate reels buy nothing, since
pieces of one count are identical.
**Constrains.** 11 of the 15 reels have no slack: a reel with a bad LED cannot be cut to its
pattern, so it becomes the spare and the field spare is reduced to its good stretches. The
counts assume the 150 mm base and a strip up to the tower top, still to confirm with the
artist (`TODO.md`); they are the maximum, since a piece can be trimmed at mounting but not
lengthened. The 75s pattern cuts after LED 150, which is 2.5 m and so a factory joint on reels
built from 0.5 m sections.

## Gotchas

- Heights have changed several times; the tower order along the V is assumed. Confirm on site.
- LED counts assume full lit height at 60/m; correct them to the strips as fitted.
- One dead LED darkens the rest of that face above it; the other faces are unaffected.

## Related

- [tower_base.md](tower_base.md) — how one channel becomes four faces.
- [../firmware/README.md](../firmware/README.md) — the rolled 2D map built on this layout.
