# Projection maker

Path: [docs](../README.md) › [strips_and_power](README.md) › **projection_maker**
Parent: [README.md](README.md)
**Code:** `tools/projection_maker.html` (viewpoints, picture projection, masks, islands, LED render, DXF export), `layout/statue-layout.json` (its input)
**Covers:** how a picture per viewpoint becomes the cut pattern of every tower face, how the cut faces
are rendered over the LEDs, and the DXF files that go to the laser cutter. Not the layout itself
([statue_geometry.md](statue_geometry.md)).

## What it does

Four viewpoints each own 14 faces (owner, 2026-10-21): the bench seat facing a statue owns that
statue's inner faces (the two that look at the centre), and a "back" viewpoint on the apex axis
behind the apex tower owns the outer faces. A picture is uploaded per viewpoint, either a raster
(white is wood, anything else is cut and lit) or a DXF (inside the closed shapes is cut). The
picture is stretched to the silhouette of the 14 faces as seen from that eye, shrinkable from
each side, and projected from the eye onto the faces; a border of wood is kept around every
face, measured on the wood. The page renders the towers at night with the LEDs behind the cuts,
reports wood islands, and exports one DXF per face.

## Decisions

- **The layout is the handoff file, not a solver** (agent, 2026-10-21). The page reads
  `layout/statue-layout.json` (fetched on GitHub Pages, a built-in copy as a fallback, or any
  loaded file) and only needs the towers' positions, heights, side, bench and eye. The artist
  edits placement in the layout tool and cut patterns here, so neither page duplicates the other.
- **The bench diameter is a control here too, and both tools must agree** (owner, 2026-10-21: the
  projection maker showed gaps that the layout tool did not, because the handoff file carried a
  bench placeholder while the artist's file had none). On GitHub Pages the page also reads the
  layout tool's saved state from the shared browser store when the towers were placed by hand, so
  the two pages show the same statue without a file round trip. One Load button takes either the
  layout file or this page's project file, and the project file embeds the layout it was made with.
- **Statue 2's viewpoints mirror statue 1's by default** (owner, 2026-10-21: "if I upload a file
  to one view it should look identical on the other view"). The bench and back viewpoints of
  statue 2 take statue 1's picture, insets, eye, distance and field of view, and their panels are
  hidden; unticking the switch copies the settings over and frees them. With a mirrored layout
  the result is identical; with a decoupled layout it is the same picture on different towers.
- **The back viewpoint's distance is measured behind the apex tower's outer corner, on the apex
  axis** (owner, 2026-10-21, chosen over the centre or the circle edge). Defaults: 3 m away,
  eye 1600 mm, field of view 100°, the same as the layout tool's eye view.
- **The picture fits the whole silhouette by default, with left / right / top / bottom shrink
  controls** (owner, 2026-10-21): one picture spans the statue with tower edges inside it, and
  the artist pulls it in from any side.
- **Raster threshold: a pixel is wood when its luminance is above 230 of 255, with transparency
  counted as white** (agent). Anti-aliased edges then cut cleanly. DXF shapes are filled with the
  even-odd rule after joining open chains by their endpoints, so a ring is a ring.
- **The unlit base and the face border are always wood** (agent). No LED sits behind the base,
  so a cut there would be a dark hole; the border is the plate's frame.
- **Wood islands are reported per face, never fixed** (owner: "say tower 1 face 3 has wood
  islands"). An island is a wood region not connected to the plate edge, found on the 2 mm mask
  with specks under ~4 mm² ignored. A face split into several edge-touching pieces is reported
  too. Faces are named A/B (inner, left/right from the bench) and C/D (outer, left/right from
  behind), so the message names a physical face.
- **LEDs are rendered as a diffuser one plate thickness behind the cut face** (owner: thickness
  6 mm default). Each LED lights the horizontal line opposite it and blends additively with the
  LEDs above and below (weight falls linearly over one LED pitch), in a shader fed by one small
  colour texture per tower, updated every frame. All four faces of a tower share the strip, as in
  the real wiring. The parallax through the holes is what shows the thickness.
- **Animations are a registry** (owner: "prepare for inserting the actual animations"). Each
  entry fills an RGBA array per tower per frame from `(t, tower, n)`; the rainbow is a full
  gradient by height drifting slowly, and "all white" shows the worst case. The real show goes in
  as further entries.
- **DXF export is R12 with POLYLINE/VERTEX, mm, two layers** (agent): OUTLINE is the plate
  rectangle, CUT the holes, because that minimal dialect is read by every laser program. Contours
  come from a 1 mm mask, traced along cell edges, simplified (0.45 mm) and smoothed once; each
  face is one file, bundled in a zip per viewpoint, tower, statue or everything, with a
  `manifest.json` that repeats sizes and island counts.
- **A project file keeps the pictures** (agent) as data URLs or DXF text, with the viewpoints,
  border and thickness, so the work survives a reload; the browser store keeps the last state.

## Gotchas

- From the back viewpoint the arms point at the viewer, so towers hide one another; the picture
  still lands on every outer face, hidden or not.
- A feature centred on a tower's axis is split across its two faces at the corner; a closed ring
  there makes no island, but the two halves are open arcs.
- Downloads (zip, PNG) work on GitHub Pages and from a local file, not inside the claude.ai viewer.

## Related

- [statue_geometry.md](statue_geometry.md) — the layout tool that produces the input file.
- [tower_layout.md](tower_layout.md) — faces, strips and the one-channel-per-tower rule the render assumes.
