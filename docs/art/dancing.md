# The artist's dancing drawing: the bench side of statue 2

Path: [docs](../README.md) › [art](README.md) › **dancing**
Parent: [README.md](README.md)
**Covers:** the artist's second bench drawing (`art/dancing/DancingFinal3.dxf`, her third file of the night, "2nd front"), its check and
supports with `tools/check_art.py` on statue 2's bench projection, and the supported copy for her
approval (`art/dancing/DancingFinal3-supported.dxf`). The method and the thresholds are the eye's
([eye_final.md](eye_final.md)); the bench side's particulars are the sea's ([sea.md](sea.md)). This
page records only what is specific to this drawing, its cut files (`art/dancing/cut/`) and its place as
the bench-2 default in the tool.

## What the drawing is

`art/dancing/DancingFinal3.dxf` (artist, 2026-10-30, her third file; `Dancing.dxf` and
`DancingFinal3.dxf` of the same night, "2nd front", were replaced by it before anything was
committed and are not kept): an
Illustrator export like the others, 356 filled shapes in centimetres, 27.5 × 15.1 cm (an aspect of
0.549, the sea's is 0.539), a dancing figure with arms raised in waves of hair and water, stars and
dots above. Each file is the same drawing with a few strokes redrawn in the hair at the right end (drawing
18–20.5, 16.8–17.9), where the first check had put bars: the second file moved the drawing 2 cm down
the page and redrew 0.2 cm² there to no effect, the third redrew another 0.25 cm² and took T7-A from
6 loose pieces to 3, 12 bars fewer. No shrink instruction came with either file.

## Decisions

- **It is the bench of statue 2** (owner, 2026-10-30: "2nd front", after the sea was the "first
  front"; the sea's place on statue 1 is still to be confirmed, [sea.md](sea.md), and the two go
  together: if the sea moves, this one moves the other way).
- **Statue 2's bench projection is extracted, and it is statue 1's to the last digit** (agent,
  2026-10-30): `art/dancing/bench2-projection.json`, the snippet of [eye_final.md](eye_final.md) with
  `key = 'bench2'` and `statue === 2`, run on the page's defaults (`?thick=4`); every coefficient is
  within 1e-15 of `art/sea/bench1-projection.json`, for the reason the back ones match
  ([praying.md](praying.md)): statue 2 mirrors statue 1 and each bench viewpoint stands in its own
  statue's frame. Kept as its own file, like the back one, so a change to one viewpoint has a place to land.
- **Bottom shrink 0.14, no top shrink** (owner, 2026-10-30: "Bottom shrink 0.14"; the artist gave
  none with the file). The box becomes 0.67 × 0.86 = 0.577 against the drawing's 0.549, a 5 %
  stretch. A first run with the sea's pair (top 0.01, bottom 0.16, assumed from the drawings'
  matching proportions) was replaced by this one the same day, before anything was sent to the artist.
- **The checker's loader follows a block inside a block** (agent, 2026-10-30, `read_drawing` in
  `tools/check_art.py`): this export nests the drawing two blocks deep (`Block_0` holding only an
  insert of `Block_1`, which holds the shapes), where the earlier files had one block; the loader
  took one level and would have read an empty drawing. It now recurses through inserts, and stops
  with a message if an insert is placed anywhere but the origin at scale 1 and no rotation, because
  it does not apply block transforms (every Illustrator export so far is at the origin). This is a
  loader fix, not a new rule: the check and the supports are the committed ones.
- **On this drawing: 24 bars at 24 spots, 16 specks and dots cut away, nothing on the apex plates
  but one island** (agent, 2026-10-30): the bars sit on T7-A and T1-B (the wavy strokes of the hair
  at both ends, where 1 cm of drawing is 84 × 88 mm on T7-A and 112 × 111 mm on T1-B), two on T6-B,
  and two under the one real island, 2268 mm² on T4-B, a hole enclosed by the figure's raised arm at
  the apex (drawing 9.5, 19.3). The other islands were 5 to 35 mm² dots and were cut away with the
  specks. `DancingFinal3-supported.png` shows the bars in red and the specks in blue;
  `DancingFinal3-supports-sheet.png` is the close-up the owner shows the artist.

```bash
.venv/bin/python tools/check_art.py art/dancing/DancingFinal3.dxf --projection art/dancing/bench2-projection.json --shrink-bottom 0.14 --support --bake --out art/dancing
```

## The tool's default (owner, 2026-10-30: approved)

`DancingFinal3-supported.dxf` is the bench-2 picture the layout tool opens with (`DEFAULT_PICTURES`
in `tools/statue_render.html`), the one in `layout/statue-layout.json` (a `?dump=1&thick=4` export
of the page, in which only the bench-2 viewpoint changed against the previous file) and a supporting
file of the claude.ai artifact, as the sea is for bench 1 ([sea.md](sea.md)). With it all four
viewpoints open with the artist's drawings and the demo smiley only shows in a bare file.

## The cut files (owner, 2026-10-30: "approved, please make the cut files")

`art/dancing/cut/` holds `S2-T<n>-<A|B>.dxf` for the inner faces of statue 2, in the eye's format,
with `manifest.json`, `plates.png` and the bundle `art/dancing/DancingFinal3-cut-files.zip`, made from
the supported drawing with no insets: 18 to 29 % of each plate cut, 3 slivers under 10 mm² dropped
(1 on T6-B, 2 on T7-A), no islands, nothing loose. The same two cosmetic marks as the sea's:
`plates.png` is titled and ordered as seen from behind (T7 on the left), mirrored for a bench
drawing, and the manifest counts a second "wood piece" on `S2-T2-A.dxf` that is a degenerate
zero-area point at x 284 mm, y 1012 mm, nothing a laser can cut.

```bash
.venv/bin/python tools/check_art.py art/dancing/DancingFinal3-supported.dxf --projection art/dancing/bench2-projection.json --cut art/dancing/cut
```

## Related

- [sea.md](sea.md) — the first bench drawing: the bench projection, the shrinks, what was tried and reverted.
- [eye_final.md](eye_final.md) — the method, the thresholds, the extraction snippet.
- [sheets.md](sheets.md) — where these plates sit on the plywood sheets.
