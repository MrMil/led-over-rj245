# The artist's praying figure: the back of statue 2

Path: [docs](../README.md) › [art](README.md) › **praying**
Parent: [README.md](README.md)
**Covers:** the artist's drawing for the back of statue 2 (`art/praying/Praying.dxf`), its check and
supports with `tools/check_art.py`, and the 0.02 top shrink baked into the copy sent back to her
(`art/praying/Praying-supported.dxf`), and the 14 cut files in `art/praying/cut/`. The method and the thresholds are those of the eye
([eye_final.md](eye_final.md)); this page records only what is specific to this drawing.

## What the drawing is

`art/praying/Praying.dxf` (artist, 2026-10-28): an Illustrator export like the eye's, 263 filled
shapes in centimetres, 18.2 × 30.4 cm, a praying woman with a sun and a moon above her head. The
artist's instruction with it (owner, 2026-10-28): **0.02 shrink from the top** in the tool (first relayed as 0.2 and
corrected the same day; the 0.2 run left the top 370 mm of the apex blank and is superseded).

## Decisions

- **The back viewpoint of statue 2 has the same projection as statue 1's** (agent, 2026-10-28):
  `art/praying/back2-projection.json` was extracted from the tool for `back2` and statue 2's outer
  faces, with the snippet in [eye_final.md](eye_final.md) and `key = 'back2'`, `statue === 2`; it
  came out identical to `back1-projection.json` to the last digit, because statue 2 mirrors
  statue 1's layout and each back viewpoint stands in its own statue's frame, at the same 3000 mm,
  eye 1200 mm and 90°. Kept as its own file so a change to statue 2's viewpoint has a place to land.
- **The 0.02 top shrink costs nothing visible** (recorded, 2026-10-28): the box's top is the apex's
  top, so a top inset empties the apex's top the way the eye's bottom inset emptied its bottom
  ([eye_final.md](eye_final.md)); at 0.02 that is 40 mm, of which 20 mm is the plate's border, so
  the apex plates' cuts stop 7 mm below the border and nothing else is affected.
- **Supports: 9 bars at 5 spots, all in the face and hair on the apex faces** (agent, 2026-10-28,
  same rule as the eye): the closed eyes, a hair strand and a brow stroke hold wood by 4, 10 and
  12 mm on the apex, where 1 cm of drawing is 93 × 68 mm. Seven hairline specks were cut away, one of
  them the wedge between the praying hands.
- **Wood specks the raster sees as islands are cut away** (agent, 2026-10-28, a `check_art.py` rule
  that applies to every drawing). The tool's island report on the supported drawing still named two
  islands of 2 and 3 cells (8 and 12 mm²) that the vector check could not see: a wedge of wood 3 mm
  wide and 20 mm long where one stroke curls back on itself, and a pocket between two strokes that
  all but touch, held by a hairline. The 2 mm raster loses the hairline; a laser would leave a
  charred hair. So the check now lists as specks, and `--support` and `--cut` both cut away: a wood
  pocket under 400 mm² that an opening by 2 mm separates from the plate edge, and a wedge of wood
  under 4 mm wide and 60 mm² that lies between two cuts or is longer than 8 mm (the opening's own
  corner roundings are a few mm across and stay). Vector and raster now agree: no islands on either
  back. The eye's cut files were regenerated under the same rule (six specks on T3-D, T4-C, T4-D).

## The tool's default (owner, 2026-10-28)

`Praying-supported.dxf` is the back-2 picture the layout tool opens with and the one in
`layout/statue-layout.json`, with zero insets since the 0.02 is baked in
([../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md)).

## The cut files (2026-10-28)

`art/praying/cut/` holds the 14 cut files `S2-T<n>-<C|D>.dxf` for the outer faces of statue 2, in
the eye's format ([eye_final.md](eye_final.md)), with `manifest.json`, `plates.png` and the bundle
`art/praying/Praying-cut-files.zip`. The owner sends the supported drawing and the bundle to the
artist together, so that on her approval she can pass the bundle straight to the laser cutter (owner,
2026-10-28). Six slivers under 10 mm² dropped; every plate one piece, no islands, nothing loose.
`--cut` names the files after the projection's viewpoint (`back2` → `S2`); the first run named them
`S1` and was redone.

```bash
.venv/bin/python tools/check_art.py art/praying/Praying.dxf --projection art/praying/back2-projection.json --shrink-top 0.02 --support --bake --out art/praying
.venv/bin/python tools/check_art.py art/praying/Praying-supported.dxf --projection art/praying/back2-projection.json --cut art/praying/cut
```

## Related

- [eye_final.md](eye_final.md) — the method, the thresholds, the extraction snippet, the cut files.
- [cuttability.md](cuttability.md) — where the 15 mm and 18 mm come from.
