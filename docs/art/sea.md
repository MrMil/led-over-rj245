# The artist's sea drawing: the bench side of statue 1

Path: [docs](../README.md) › [art](README.md) › **sea**
Parent: [README.md](README.md)
**Covers:** the artist's first bench drawing (`art/sea/SeaFinalll.dxf`, her fix of `Seafinal.dxf`), its
check and supports with `tools/check_art.py` on the bench viewpoint's projection, the two shrinks baked
into the copy for her (`art/sea/SeaFinalll-supported.dxf`), and the rules tried on the first version and reverted. The method and the
thresholds are the eye's ([eye_final.md](eye_final.md)); this page records what is specific to this
drawing and what the bench side changed in the checker.

## What the drawing is

`art/sea/SeaFinalll.dxf` (artist, 2026-10-29, after `Seafinal.dxf` of 2026-10-28, "first front is
ready"): an Illustrator export like the others, 427 filled shapes in centimetres, 27.6 × 14.9 cm,
three manta rays in a shoal of fish. Her instruction: **top shrink 0.01, bottom shrink 0.16**. The
bench silhouette box is 1.10 × 0.74 (an aspect of 0.67); with the shrinks it is 0.557, close to the
drawing's 0.54. **The fix** (owner, 2026-10-29: "I just had the artist fix it"): the left ray's face
redrawn with room round the eye, and most of the enclosed dots gone (9 islands and specks cut away
against 55 before); the first file is not kept, the fix replaced it before anything was committed.

## Decisions

- **It is the bench of statue 1** (agent, 2026-10-28: "first front" with no statue named; the two
  bench projections are mirror-identical as the back ones are, so the check is the same either way
  and only the file names and the viewpoint in the tool would change). Confirm with the owner before
  cutting; moving it to statue 2 is a rerun of `--cut` with `bench2` in the projection file's
  `viewpoint` and the picture under the other viewpoint in the tool.
- **The bench projection is extracted like the back ones**: `art/sea/bench1-projection.json`, the
  snippet of [eye_final.md](eye_final.md) with `key = 'bench1'` and the inner faces A and B; the eye
  sits on the bench edge, 1.9 m from the centre at 1200 mm, so the near tip towers are the finest
  plates: 1 cm of drawing is 84 × 86 mm on T7-A and 111 × 109 mm on T1-B, against 383 × 275 mm on
  the apex. The detail therefore lands on the tips, the opposite of the back drawings.
- **The checker is the one the eye and the praying figure were made with; the rules written for this
  drawing were reverted** (owner, 2026-10-29: "go back to the script as it was before I brought in the
  ray, the new script is terrible"). What was tried on the first file, `Seafinal.dxf`, and thrown away:
  widening a thin lane by shaving every stroke beside it (cut the eye ring to a broken C); moving a
  stroke away from the lane with its width kept (the owner's own idea, "bring the front of the face a
  bit forward"); shaving only the thickest stroke; a re-check of the plate per candidate; small pockets
  left for the owner; filling geometry crumbs under 4 mm² in the support pass and in `--cut`; specks
  held by under 3 mm instead of 2; and the plate picture of `--cut` in bench order. All of it made the
  face worse or no better, and the artist fixed the face herself instead; the checker went back to
  `git` as of commit 470b638: bars, two per loose piece, islands under 400 mm² cut away. Two of the
  reverted pieces were plain fixes and may be wanted again when the cut files are made: `--cut`
  draws `plates.png` as seen from behind (T7 on the left, C before D) even for a bench viewpoint, and
  leaves enclosed wood crumbs under 4 mm² as tiny loops in the DXF (the tool's raster shows one such
  crumb as an island now and then).
- **On this drawing (her fix):** 37 bars at 19 spots: 14 on T7-A (the right ray's dense body), 2 on
  T1-B, 2 on T5-A, 1 on T6-A; 7 dots cut away; nothing on the apex plates. The left ray's face takes
  one pair of bars (T1-B); she had redrawn it with room round the eye and removed most of the enclosed
  dots herself (7 cut away against 55 in her first file). The first file is not kept; it was replaced
  before anything was committed.
- **The two shrinks are baked in together** (`--shrink-top 0.01 --shrink-bottom 0.16 --bake`):
  marker squares extend the drawing box at both ends, so the supported copy loads with no insets.
- **Geometry crumbs are cut away too** (agent, 2026-10-28, a checker rule for every drawing): the
  check ignores enclosed wood under 4 mm² (`MIN_PIECE_MM2`), as the tool's island report was meant
  to, but the tool's 2 mm raster still showed one such crumb on T7-B as an island, and the cut files
  carried up to 23 of them per plate as loops of a millimetre or two for the laser to trace and a
  flake to fall out. The support pass now fills them with the specks (88 on this drawing) and
  `--cut` fills any that remain, so every plate is one piece and the vector and raster checks agree.
  The eye and praying cut files had none, so they are unchanged.
- **The support pass is not byte-deterministic** (noted 2026-10-28): two runs on the same input wrote
  the same 469 shapes (symmetric difference zero) in a different vertex order, so a supported DXF may
  differ byte-wise from the copy embedded in `layout/statue-layout.json` while being the same drawing;
  compare geometry, not bytes, and regenerate the handoff file after the last run.
- **The plate picture of `--cut` follows the viewpoint** (agent, 2026-10-28): from behind T7 is on
  the left and C before D, from the bench T1 is on the left and A before B; the first run drew the
  sea mirrored, as seen from behind.

## The tool's default (2026-10-28)

`SeaFinalll-supported.dxf` is the bench-1 picture the layout tool opens with and the one in
`layout/statue-layout.json`, as the back drawings are
([../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md));
bench 2 opens with her dancing drawing since 2026-10-30 ([dancing.md](dancing.md)).

## The cut files (owner, 2026-10-29: "approved, please make the cut files")

`art/sea/cut/` holds `S1-T<n>-<A|B>.dxf` for the inner faces of statue 1, in the eye's format, with
`manifest.json`, `plates.png` and the bundle `art/sea/SeaFinalll-cut-files.zip`, made by the committed
checker from the supported drawing with no insets: 19 to 34 % of each plate cut, 16 slivers under
10 mm² dropped, no islands, nothing loose; the tool's island report agrees. Two cosmetic marks of the
reverted fixes, recorded so nobody hunts for them: `plates.png` draws the faces in the order seen
from behind (T7 on the left), which is mirrored for a bench drawing, and `S1-T6-A.dxf` carries one
enclosed wood crumb of 1.9 mm² (3 × 1 mm, at x 176–179 mm, y 694 mm) as a tiny loop that a laser
burns away. A first set made from the first file on 2026-10-28 had been deleted.

```bash
.venv/bin/python tools/check_art.py art/sea/SeaFinalll.dxf --projection art/sea/bench1-projection.json --shrink-top 0.01 --shrink-bottom 0.16 --support --bake --out art/sea
```

```bash
.venv/bin/python tools/check_art.py art/sea/SeaFinalll-supported.dxf --projection art/sea/bench1-projection.json --cut art/sea/cut
```

## Related

- [eye_final.md](eye_final.md) — the method, the thresholds, the extraction snippet.
- [praying.md](praying.md) — the speck rule this drawing's crumb rule extends.
- [sheets.md](sheets.md) — where these plates sit on the plywood sheets.
