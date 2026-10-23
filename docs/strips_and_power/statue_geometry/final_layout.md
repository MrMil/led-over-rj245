# The final layout, the tower box and the bench

Path: [docs](../../README.md) › [strips_and_power](../README.md) › [statue_geometry](README.md) › **final_layout**
Parent: [README.md](README.md)
**Covers:** the artist's final layout as the tool's default, the 400 / 412 mm box and which faces are long, and the bench at the centre.

## Final layout (artist, 2026-10-23)

The artist's export of 2026-10-23 is the final layout, and the page's built-in defaults are its
settings (owner, 2026-10-23: "the final layout … put the new statue layout as the default");
`layout/statue-layout.json` is the owner's export of them after the artist's phone changes (below). Heights 1100 / 1400 / 1700 / 2000 mm (unchanged); a Ø 3800 mm
bench at the centre (below), so the eye points stand 1.9 m from the centre; her six spacings
as hand-set pairs 1200 / 1700 / 1300 / 2200 / 1500 / 1000 mm on the solver's rails (no free
positions in the file); circle Ø 18 m, apexes 17.4 m apart (8.7 m from the centre, unchanged),
every tower turned 45° like the apex (the `parallel` arm method, [controls.md](controls.md));
tips T1 4.8 m and T7 4.3 m from the centre, nearest tower corner 2.1 m beyond the bench edge;
spacing range 1000–2310 mm, optimum 2310, 2.15 m kept free; eye 1200 mm (a seated audience),
bench field of view 120°; back viewpoint 3 m behind the apex, eye 1200 mm, field of view 90°.
Statue 2 mirrors statue 1's layout but has its own four viewpoints' settings and pictures, all the demo smiley for now ([pictures.md](pictures.md)).
Consequences recorded elsewhere: trench segments
([trenches.md](../trenches.md)); LED counts, currents and the CAT5e length did not change, since
heights and apexes did not ([led_power_budget.md](../led_power_budget.md),
[../data_link/cabling.md](../../data_link/cabling.md)). The four generated pictures were made for
the previous layout and are superseded ([../art/README.md](../../art/README.md)).
**Since the box became 412 mm outside (same day, below), the towers are re-solved and no longer
sit exactly where her file put them** (owner chose this over keeping her positions): the apexes
move 8 mm in, the tips up to 35 mm sideways, the spacings stay hers. `layout/statue-layout.json`
was then regenerated from the page with `?dump=1`, and later replaced by the owner's file with the
artist's phone changes (below), which was made with the 412 mm box; her first raw file is in git
history.
**The default reads "artist's spacings", not "set by hand"** (owner, 2026-10-23: "it should be
tool-solved"). Her six spacings are hand-set pairs in the file format, but the solver still places
every tower so neighbouring silhouettes touch; only the spacings are hers. The badge says "set by
hand" again as soon as a spacing differs from hers. A fully solved layout (uniform spacing from
min / max / optimum) was offered and declined: with her range it puts 2133 mm everywhere and pulls
the tips in to 2.4 m from the centre, not her layout.
**The artist's changes by phone (owner, 2026-10-23, in the owner's local copy of the tool,
`statue-layout-2026-10-23.json`):** every tower at 45° like the apex instead of a corner to the
centre (the tips move up to 34 mm, the inner towers barely), and the back viewpoint at 3000 mm /
eye 1200 mm. The page's defaults reproduce that file exactly, including "statue 2 uses statue 1's pictures"
unticked (owner: on purpose, so the artist can upload statue 2's pictures directly), and
`layout/statue-layout.json` is that file, unchanged. **Changed 2026-10-23:** before
the call, the default was the `touch` method and the back viewpoint 3.2 m / eye 1460 mm.
**Changed 2026-10-23:** previously the artist's export of 2026-10-21: pairs 1120 / 1590 / 2200 /
1340 / 1760 / 1102 mm, bench 3000 mm (a working value), spacing range 1000–3000, 2.35 m kept
free, bench field of view 100°, back viewpoint 3 m / 1600 mm / 100°, tips 4.1 m from the
centre. Changed because the artist sent the final layout.

## The box: two short and two long pieces (owner, 2026-10-23)

A tower is built from two 400 mm pieces on opposite sides and two 412 mm pieces on the other two,
which cover the short pieces' edges, so the 6 mm wood thickness is accounted for: 412 × 412 mm
outside, 400 × 400 inside. The page models it: "Short piece width" (`side`, 400) and "Wood
thickness" (`thick`, 6) give the outside `side + 2 × thick`.
- **Everything seen from outside uses the outside size**: the silhouettes the solver makes touch,
  the circle, the free radius and the bench clearance. So the wood thickness is a solver input now,
  and changing it re-solves like changing the side. Old files load with `side_mm` 400 read as the
  short pieces, which makes their towers 412 outside; that is the intent, the boxes were never 400
  outside (owner).
- **Which faces are long** (owner): the inner face nearer the centre line (the line through both
  apexes) and, necessarily, the face opposite it; on the apex, which sits on the line, the inner
  face on the left as seen from the bench (A). So T1–T3 have long B and D, T4–T7 long A and C, in
  both statues. From behind, the long outer face is therefore the one farther from the centre line.
  Reason for the rule: not recorded.
- **Each plate spans only its own piece**: picture, mask, island check and DXF of a long face are
  412 mm wide, of a short face 400 mm, centred on the face; the 6 mm strips either side of a short
  face are the long pieces' end grain, drawn as plain wood. The DXF manifest's `width_mm` and the
  export's per-tower `plate_widths_mm` (by face letter) and `outside_mm` say which is which. The
  picture box is still taken from the whole outside of the faces, because that is the silhouette.
- **The diffuser sits on the inside of the wood**, 200 mm from the tower centre, 400 mm wide (the
  inside of the box), one thickness behind every cut face.
**Changed 2026-10-23:** previously the box was `side` (400) outside with four equal faces of zero
thickness, and the diffuser stood one thickness behind each face, `side − 2 × thick` wide. Changed
because the real build uses 400 and 412 pieces.

## The bench at the centre (owner, 2026-10-21)

A circular bench stands at the centre; the audience sits on its edge facing out, which is why
the eye height is 1200 mm. The artist placed the towers before mentioning it. **Its diameter is
3800 mm**, as set in the artist's final file (2026-10-23); whether that is the built bench's
measured size or her estimate is not recorded. **Changed 2026-10-23:** previously 3000 mm as a
working value until the real size was known (owner, 2026-10-21: the bench stays in the view);
changed because her final file sets it. A loaded file without a bench field keeps
the current bench rather than removing it, for the same reason. (Briefly on 2026-10-21 the default
was 0, a misreading of the owner; reverted the same day.) Consequences in the tool:
- **One eye point per statue, on the bench edge, on the apex axis** (owner): the eye view has a
  button per statue, the figure stands at each eye point (the bench itself is not drawn), and
  the mural, the level-top heights, the gaps and the readout angles are all taken from that
  point, not from the centre. The solver also places towers so that silhouettes touch from the
  eye point: it works in the eye's frame and checks the circle and the free radius from the
  centre.
- **Bench clearance is checked**: the nearest tower corner must lie beyond the bench edge; the
  result box and the readout say by how much, or by how much a tower stands inside the bench.
  `fits` in the export includes it, and `layout.bench_clearance_mm` records it.
- Files without `bench_diameter_mm` (versions 1 and 2 before this change) load with the eye at
  the centre, as they were made.

## Related

- [README.md](README.md) — the tool.
- [../tower_layout.md](../tower_layout.md) — tower order and heights.
- [../trenches.md](../trenches.md) — segment lengths from this layout.
