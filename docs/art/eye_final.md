# The artist's eye drawing: checking it and holding it together

Path: [docs](../README.md) › [art](README.md) › **eye_final**
Parent: [README.md](README.md)
**Covers:** the artist's final drawing for the back of statue 1 (`art/eye/EyeFinal.dxf`), how it is
checked at real plate scale with `tools/check_art.py`, what was wrong with it, the supported copy
sent back to her (`art/eye/EyeFinal-supported.dxf`, then `EyeFinal-supported-added.dxf` with her band, then
`EyeFinal-4mm-supported.dxf` for the 4 mm wood), and the 14 cut files made from it for the laser (`art/eye/cut/`).

## What the drawing is

`art/eye/EyeFinal.dxf` (artist, 2026-10-27) is an Illustrator export: 263 filled shapes (HATCH, each
with its outline SPLINE) in centimetres, 15.0 × 24.6 cm, black is cut. The layout tool reads the
closed splines and stretches the drawing over the back viewpoint's silhouette box
([../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md)).
The artist's instruction with it (owner, 2026-10-27): **"shrink from bottom 0.13" in the tool**, i.e.
the back viewpoint's bottom inset is 0.13; with it the drawing's proportions (0.61) match the box
(0.63), without it the drawing is stretched 15 % taller.

## Decisions

- **The drawing is checked by projecting it onto every plate in millimetres with the tool's own
  projection, not by eye and not on the raster masks** (agent, 2026-10-27). 1 cm of the drawing is
  113 × 74 mm on the apex tower and up to 314 × 182 mm on the tip towers (with the 0.13 shrink), so
  the same stroke is three times narrower on T4 than on T7 and only a plate-scale check says what
  holds. `tools/check_art.py` maps each plate's rectangle through the homography the tool uses
  (`faceMask` in `tools/statue_render.html`), keeps the tool's 20 mm border and 150 mm unlit base as
  wood, and reports per plate: islands (wood touching no plate edge), loose pieces (wood an opening
  by 15 mm separates from the edge, with the width of the neck that holds it) and thin walls. The
  tool's own island report was run on the same file and agrees (without shrink: T4-C 3, T4-D 1,
  T5-D 2 islands; with it: T4-C 4, T4-D 1, T5-D 2).
- **The projection is extracted from the tool, not recomputed** (as for `art/viewpoints.json`,
  [pipeline.md](pipeline.md)): `art/eye/back1-projection.json` holds, per outer face of statue 1,
  the nine coefficients of the plate-to-picture map and the silhouette box, read from
  `window.statueDebug` in the page's console with the layout file loaded. Regenerate it after any
  layout change:

  ```js
  const D = window.statueDebug, key = 'back1', box = D.povBox(key, D.current, D.faces), pose = box.pose;
  const out = { viewpoint: key, border_mm: D.state.border, unlit_mm: D.state.unlit, box: { x0: box.full[0], y0: box.full[1], x1: box.full[2], y1: box.full[3] }, insets: D.state.povs[key].insets, faces: [] };
  D.faces.filter(f => f.povKey === key && f.tower.statue === 1).forEach(f => { const o = f.origin.clone().sub(pose.pos), rw = f.rw;
    out.faces.push({ tower: f.tower.name, face: f.letter, width_mm: Math.round(f.pw * 1000), height_mm: Math.round(f.tower.h * 1000),
      coef: { oF: o.dot(pose.F), rF: rw.dot(pose.F), uF: pose.F.y, oR: o.dot(pose.Rt), rR: rw.dot(pose.Rt), uR: pose.Rt.y, oU: o.dot(pose.U), rU: rw.dot(pose.U), uU: pose.U.y } }); });
  JSON.stringify(out)
  ```

  Note that the page is in `tools/`, so from the repo root it is
  `tools/statue_render.html?load=../layout/statue-layout.json`.
- **Thresholds are the recorded cuttability rules** ([cuttability.md](cuttability.md)): wood under
  15 mm holds nothing, a support is an 18 mm lane. Cut widths are not checked: this is for a laser
  (owner, 2026-10-27), whose kerf is a fraction of a millimetre, not the 10 mm router bit the rules
  were written for.
- **Supports are added in the drawing, two per loose piece, from the piece to the nearest safe
  wood** (owner, 2026-10-27: "minimal wooden supports so that every island and piece that's hanging
  by a thread is supported from at least 2 sides"). A support is a straight 18 mm wood bar
  (`BRIDGE_MM`) from the piece's 15 mm core to the nearest wood that reaches a plate edge, run 12 mm
  into both, on two sides at least 100° apart around the piece (60° and then anything when the piece
  offers no better). It is placed in plate millimetres, where the widths mean something, and mapped
  back into the drawing, so the same bar is a different size in the drawing on different towers.
  Islands under 400 mm² are cut away instead of bridged (a speck of 26 mm² would get a bar bigger
  than itself). Plates are done in order and each re-checks after the previous ones' bars, so a
  piece the apex plate already holds is not bridged again on the hidden face of T5 that shows the
  same part of the drawing. Rounds repeat until nothing is loose.
- **The output drawing bakes the 0.13 shrink in** (owner, 2026-10-27: "preferably without needing
  the 0.13 bottom shrink"). The tool stretches a drawing over the box it reads from the shapes'
  bounds, so `EyeFinal-supported.dxf` carries two 0.5 mm marker squares on layer `BOX` at the
  bottom corners of a box extended downwards by 0.13 / 0.87 of the height: loaded with no inset it
  lands exactly where the original lands with the 0.13 inset. The markers fall below every plate (the
  bottom of the silhouette is the apex's foot, the corners are beyond the tip towers), so they cut
  nothing. Verified by checking the baked file with no inset (same scale per plate, nothing loose)
  and by loading it in the tool (no islands).
- **The shapes are written as closed polylines on layer `CUT`, filled even-odd** (agent,
  2026-10-27): the tool reads exactly that, and a bar across a stroke splits the stroke into two
  shapes, which splines could not express without re-fitting. The artist gets polylines back, not her
  splines; the supports are the only change to her art.

## What was found (2026-10-27)

Without the shrink: 6 islands (4 distinct spots, two of them on the hidden part of T5-D too), 20
loose pieces, the worst held by 7 mm (`art/eye/` has no render of this run; the message to the owner
had it). With the 0.13 shrink, which is the real setting: 6 islands and 29 loose pieces (worst 6 mm),
almost all on the apex T4, where the drawing is smallest. The cloud's spiral is a 20 to 25 mm wood
tongue held at one end, not a thread; the upper-left quarter of the iris is enclosed by black and is
saved only by the box corner and the 20 mm border running through it.

`art/eye/EyeFinal-check.png` circles every problem on the drawing (with the shrink).
`EyeFinal-supported.png` is the drawing with the 58 bars in red (43 spots) and the cut-away speck in
blue, `EyeFinal-supports-sheet.png` shows each spot close up, `EyeFinal-supported-plates.png` the 14
plates with the bars. After the bars, nothing is loose on any plate.

## The band at the bottom (artist, 2026-10-28)

The artist approved the supported drawing and, asked for 1.5 cm more art under the apex (the 0.13
inset had left 115 mm of blank lit wood above the apex's base, [the owner's question of
2026-10-27](eye_final.md)), returned `art/eye/EyeFinal-supported-added.dxf`: the baked file with
the band drawn in, the marker squares kept. It is the drawing of record. Checked with no inset:
nothing loose, no islands; the apex plates' cuts now run from the base to the top. The cut files
below are made from it.

## The tool's default (owner, 2026-10-28)

`EyeFinal-4mm-supported.dxf` (below; `EyeFinal-supported-added.dxf` earlier the same day) is the
back-1 picture the layout tool opens with and the one in `layout/statue-layout.json`, with zero
insets since the 0.13 is baked in
([../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md)).

## The 4 mm layout (2026-10-28)

The owner went to 4 mm wood, which makes the long plates 408 mm and moves every tower by a few
millimetres ([../strips_and_power/statue_geometry/final_layout.md](../strips_and_power/statue_geometry/final_layout.md#4-mm-wood-owner-2026-10-28)).
`art/eye/back1-projection.json` was re-extracted from the tool for it (the snippet above; the 6 mm
one is in git history).
- **Checked against it, `EyeFinal-supported-added.dxf` was one neck short** (agent, 2026-10-28): no
  islands, but on T4-D a piece of 4678 mm² (604 mm up the plate, right of its centre, below the iris)
  was held by 14 mm, 1 mm under the 15 mm rule; it passed on the 412 mm plates, where the same neck
  mapped a millimetre wider. The five specks the cut rule removes anyway were the same as before.
- **`EyeFinal-4mm-supported.dxf` is the drawing of record** (owner, 2026-10-28: "add the support"):
  the support pass against the 4 mm projection added 2 bars on T4-D and cut the 5 specks away (3 on
  T4-D, 2 on T3-D), nothing else; `EyeFinal-4mm-supported.png` shows them in red (specks in blue) and
  `EyeFinal-4mm-supports-sheet.png` close up, which is what the owner showed the artist by phone.
  `EyeFinal-4mm-check.png` and `EyeFinal-4mm-plates.png` are the check before the bars,
  `EyeFinal-4mm-supported-check.png` and `EyeFinal-4mm-supported-plates.png` the check of the drawing of
  record (clean), written by the `--cut` run. The artist approved it by phone the same day. `--stem` names the outputs, because the
  drawing's own name would have given `EyeFinal-supported-added-supported.dxf`.

## The cut files (owner, 2026-10-27: "this is what we send to the laser guy")

`art/eye/cut/` holds the 14 cut files for the outer faces of statue 1, made from
`EyeFinal-4mm-supported.dxf` on the 4 mm projection (2026-10-28; the first set, from
`EyeFinal-supported-added.dxf` on 412 mm plates, is in git history and must not be cut: the long plates
would be 4 mm too wide and the picture a few millimetres off at every seam), a quarter of the wood:
`S1-T<n>-<C|D>.dxf`, R12, millimetres, layer `OUTLINE` the
plate rectangle (400 or 408 wide by the tower height, [../strips_and_power/statue_geometry/final_layout.md](../strips_and_power/statue_geometry/final_layout.md)),
layer `CUT` every closed contour, holes inside a cut as separate contours on the same layer, the same
format as the generator's and the tool's exports. `manifest.json` lists each file with its size, cut
count and cut fraction (30 to 40 % of each plate); `plates.png` shows all 14 in the order seen from
behind; `art/eye/EyeFinal-cut-files.zip` is the bundle to send (regenerated 2026-10-28; whoever has the
first zip needs this one instead).
- **They are made by `tools/check_art.py --cut`, from the supported drawing with no inset, the same
  projection the check used** (agent, 2026-10-27): the vector shapes are mapped plate by plate
  through the tool's homography, clipped to the plate inside its 20 mm border and above the 150 mm
  unlit base, simplified at 0.05 mm, and written only when the check finds nothing loose, so a cut
  file can never disagree with the check that passed it. The tool's own DXF export was not used
  because it traces the 2 mm raster mask ([pipeline.md](pipeline.md)).
- **Cut pieces under 10 mm² are dropped** (agent, 2026-10-27): five slivers (six on the 412 mm plates)
  the plate border clipped off strokes that cross a seam; a laser would just scorch them. Nothing
  else is cleaned: the laser's kerf needs no minimum cut width.
- **Specks are cut away in the cut files too** (agent, 2026-10-28, see [praying.md](praying.md) for
  the rule); on the 4 mm drawing of record they are already gone from the drawing itself.
- Every plate is one piece of wood, no islands, nothing loose (`manifest.json` records it per file);
  the tool's island report on `layout/statue-layout.json` agrees.

## The 22 mm trial (2026-10-28)

A 22 mm wood minimum (the 15 mm lane's strength in 4 mm wood) was tried on the drawing of record: 217 bars at 92 spots, mostly in the iris. The owner kept 15 mm and the trial files were deleted ([cuttability.md](cuttability.md)).

## Running it

```bash
.venv/bin/python tools/check_art.py art/eye/EyeFinal.dxf --shrink-bottom 0.13 --support --bake --out art/eye
```

```bash
.venv/bin/python tools/check_art.py art/eye/EyeFinal-supported-added.dxf --projection art/eye/back1-projection.json --support --stem EyeFinal-4mm --out art/eye
```

```bash
.venv/bin/python tools/check_art.py art/eye/EyeFinal-4mm-supported.dxf --projection art/eye/back1-projection.json --cut art/eye/cut
```

(the project's `.venv`, [README.md](README.md#gotchas).) Without `--support` or `--cut` it only reports and
draws `<stem>-check.png` and `<stem>-plates.png`. The script takes 30 s. The zip is `zip -j` of the
14 DXFs, `manifest.json` and `plates.png`.

## Related

- [cuttability.md](cuttability.md) — the rules the thresholds come from.
- [pipeline.md](pipeline.md) — the generated pictures' homography and the extraction precedent.
- [../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md) — how the tool fits and projects a picture, insets, islands.
