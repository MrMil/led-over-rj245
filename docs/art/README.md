# Art: the pictures cut into the faces

Path: [docs](../README.md) › **art**
Parent: [../README.md](../README.md)

**Covers:** the four pictures cut into the tower faces (one per viewpoint), how they are generated
as vector cut files so that a CNC can cut them out of 6 mm plywood, and how their previews get into
the handoff file. Not the projection in the tool itself
([../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md)).
**Code:** `tools/face_art.py` (the generator), `art/viewpoints.json` (where every face lands in
each picture, extracted from the tool), `art/dxf/S<statue>-T<n>-<face>.dxf` (the cut files, one per
plate, each with an `.svg` twin to inspect in a browser), `art/<viewpoint>.png` (the pictures as the tool's preview), `art/<viewpoint>-preview.png`
(the pictures with the faces drawn in), `art/<viewpoint>-towers.png` (only the plates, 8192 px, anti-aliased), `tools/embed_pictures.py` (puts the preview pictures into
`layout/statue-layout.json`), `tools/statue_render.html` (`PICTURE_MAX`, `?load=`).

**Status (owner, 2026-10-23): superseded, kept as they are.** The pictures, `art/viewpoints.json`
and the cut files in `art/dxf/` were made for the layout of 2026-10-21. The final layout of
2026-10-23 ([../strips_and_power/statue_geometry/final_layout.md](../strips_and_power/statue_geometry/final_layout.md))
moved every tower but the apexes, so they no longer fit the faces and must not be cut. They are
left unchanged and not regenerated, because the artist is drawing different art (owner,
2026-10-23: "do not change the art"). The tool shows the demo smiley again
([pipeline.md](pipeline.md)). What follows records how they were made, for whoever picks the
generator up again.
**Changed 2026-10-23:** previously a working state, not final, and the tool's defaults so the
layout could be judged with real cuts in place (owner, 2026-10-22). Changed because the layout
moved under them and the artist is doing the art instead.

## What it does

The owner's brief (2026-10-22): statue 1 bench, a woman blessing with her hands stretched out to
the sides; statue 1 back, an open eye; statue 2 bench, a bird with open wings and a third eye
radiating energy; statue 2 back, a magical mushroom. All intricate, ayahuasca / DMT / psilocybin /
LSD art, and all cuttable out of wood.

`tools/face_art.py` draws each picture for the silhouette of the 14 faces its viewpoint sees, as
polygons: a figure in "design units" (pixels of a 2048-wide picture) over lattices of cut cells
drawn in millimetres in each plate's own frame. Every plate is a flat rectangle, so its mapping
from the picture plane is a homography (fitted to the plate's four corners as the tool projects
them), and a homography maps polygons to polygons exactly. Each plate's cuts are composed, checked
and written to DXF as polygons in millimetres; no raster step touches the cuts. The PNG is a 1 mm
rasterisation of the same cuts for the tool's 3D preview, and `art/<name>-preview.png` shows it
with the faces outlined, their wood borders and unlit bases greyed, and the area no face shows
darkened: that is what to look at when judging a picture.

## Contents

### Pages

- [`pipeline.md`](pipeline.md) — design units, the per-plate homography, local frames, `art/viewpoints.json`, previews, why the tool no longer opens with them.
- [`cuttability.md`](cuttability.md) — minimum widths, islands, cantilevers, needles, seams, the final small-piece pass.
- [`compositions.md`](compositions.md) — the four pictures, where they land, and their design decisions.

## Gotchas

- The generator needs a Python environment with numpy, pillow, scipy and shapely (not in the repo:
  `python3 -m venv .venv && .venv/bin/pip install numpy pillow scipy shapely`). The 14 plates of a
  picture run in parallel across the cores (each plate is independent): about 20 s per picture on
  a 16-core machine, 15 to 20 s of CPU per plate. Run one generator at a time; the plates already
  use every core.
- Keep the polygons' arc resolution where it is: finer arcs (the buffers' segments, the sectors'
  sampling) made the polygon operations ten times slower for no visible gain on a router.
- After any change to the layout, re-extract `art/viewpoints.json` and regenerate; the
  compositions are placed on the silhouette and will not follow a moved tower by themselves.
  As of 2026-10-23 this has not been done for the final layout (see Status).
- Do not run `tools/embed_pictures.py` on the current handoff file: it would put these outdated
  pictures into `layout/statue-layout.json` in place of the artist's file.
- The generator's own report is the word on cuttability (it prints LOOSE WOOD per plate if any
  region is left unconnected); the tool's "Islands and pieces" on the loaded handoff file checks
  the 1 mm preview and may differ by a cell at the edges.
- The DXF polylines are the polygons' vertices (arcs as short segments, 0.05 mm simplification);
  every contour is closed; holes inside a cut region are separate closed contours on the same
  layer, as the tool's export does it.

## Related

- [../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md) — the tool that projects these pictures onto the faces and exports the DXF.
- [../strips_and_power/tower_layout.md](../strips_and_power/tower_layout.md) — the towers the pictures are cut into.
