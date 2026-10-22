# Cuttability rules

Path: [docs](../README.md) › [art](README.md) › **cuttability**
Parent: [README.md](README.md)
**Covers:** what makes a plate cuttable from 6 mm plywood and how the generator enforces it on the polygons: minimum widths, islands, cantilevers, needles, seams, the final small-piece pass.

## Decisions

- **Minimum wood 15 mm, minimum cut 10 mm, lanes drawn at 18 mm** (agent, 2026-10-22, after the
  owner asked for the plywood minimum to be looked up). The general sheet-metal rule is half the
  material thickness for bridges and holes ([SendCutSend](https://sendcutsend.com/guidelines/cnc-machining/)),
  i.e. 3 mm for 6 mm stock; plywood splits along the grain, the plates are 2 m tall, handled by a
  crew and stand in wind, so 2.5 × the thickness is used instead. 10 mm cut is what a 6 mm bit
  leaves clean. Confirm with whoever cuts.
- **Cuttability is enforced on the polygons in millimetres without deforming them** (agent,
  2026-10-22). A cut piece that a MIN_CUT_MM disc does not fit into, or under 150 mm², is dropped
  whole; wood thinner than MIN_WOOD_MM (found by an opening of the wood) is cut; islands are the
  components of the wood's core (an opening by CORE_MM, so a region held only by a thinner neck
  counts as loose) that do not touch the plate's 20 mm border or its 150 mm base, and each gets a
  straight LANE_MM bridge to the nearest safe wood, overshooting both joints by a core radius;
  wood crumbs under 40 mm² are cut away. Two rounds. Any wood still loose is printed as LOOSE
  WOOD; none is in the current files.
  **Changed 2026-10-22:** the first vector version opened the cuts and the wood themselves, which
  rounded and fused every shape into blobs and pinched necks (owner: "a tangled mess of fuzzy
  shapes", "rendering errors"); shapes are now left as drawn and only whole pieces are removed.
- **The lattices keep a lane at every seam, and cells are clipped, not dropped** (agent,
  2026-10-22). A lattice drawn inside a region (a hand's mandala, the iris, the gills) is clipped
  to the region shrunk by a lane; a cell the edge leaves under 40 % of its area is dropped, the
  rest kept, so long rays survive and no slivers remain. (Dropping every touched cell whole left
  the gills empty and blank bands at every region edge.)
- **The figure contour is 1.5 lanes (27 mm)** (agent, 2026-10-22). At 2.6 lanes it left a blank
  band of wood around every figure, the mushroom's rim band 150 mm tall.
- **A final pass drops every cut piece under `MIN_PIECE_MM2` (250 mm²) or too thin for a 10 mm
  disc, whatever made it** (owner, 2026-10-22: "go over the dxf; if there are black pieces that
  are less than a certain small surface area, remove them entirely, no matter the source; this
  goes for really thin black lines as well"). It runs on the finished plate after all other passes.
- **Figures: cut shapes with a wood contour, and every wood lane inside a figure runs from
  contour to contour** (agent, 2026-10-22; owner: "the bird's eye will absolutely break off"
  when an eye hung from a single brow lane). A wood feature inside a cut region is an island
  unless it touches wood that reaches the plate edge, and a lane held at one end is a cantilever,
  so every lane inside a head crosses it edge to edge (eye-level lane carrying the eye almond,
  beak-base lane top to bottom, brow arc from beak to crown), feather veins run tip to base, dress
  lanes edge to edge. The contour is 1.5 lanes (27 mm) wide so the figure reads as a line against the lattice.
- **Figures are kept clear of lattices and of each other by a lane** (agent, 2026-10-22, after the
  owner's "look at how unclean the image is"). Every knob and hook in the renders was the thin-wood
  step fusing two cut shapes that came within 15 mm: lashes rooted below the lid, the iris rim
  dashes against the lids, lattice cells against the lid strokes, cap cells clipped by the plate's
  corner, the dome halo. So: the iris fits the eye opening with its rim a lane clear of both lids
  (iris 200 mm, eye 300 up and 255 down); lattices around the eye are clipped to the almond
  shrunk or grown by 16 units beyond the lane; lashes are clipped flush with the eye white;
  the cap is built as whole crackle cells and cells that the plate's corner would leave as slivers
  are dropped; the halo is gone. Feathers are blunt lenses with a vein and a small eye spot on it,
  no barbs (the barbs crossed the feather edge at shallow angles and left saw teeth).
- **Cut needles are removed by shape, and nothing else is cleaned by morphology** (agent,
  2026-10-22, after the owner's crops of slivers, notches and loose lane ends). A needle is a part
  of a cut narrower than the bit hanging off a wider cut (a lens tip, a cell clipped to a sliver):
  candidates are what an opening by MIN_CUT_MM would remove, and only the long thin ones go
  (extent over 14 mm, mean width over 1.5 mm), because the same opening also lists every corner
  rounding and hair-thin crescents along curved edges. A pass that removed short wood fragments
  was tried and reverted the same hour: it broke lattice lanes between crossings and the island
  bridging then re-joined them with round blobs. Loose lane ends are fixed at the source: the
  arm's centre lane runs from its first bracelet to its last.
- **A lane's width is taken where each of its points lands** (agent, 2026-10-22). The dress's
  chevrons were sized at the apex tower and ran onto the neighbours, where a near-horizontal lane
  maps through the finer vertical scale and came out under 15 mm, so the thin-wood step removed
  them, leaving nubs on the verticals.
- **Cantilevers are detected and cut off** (owner, 2026-10-22: "many lines don't end where you
  meant them to end", "I'm sure you can check automatically if there are any parts that will break
  off"). A lane (wood no wider than a lane and a bit) that touches the rest of the wood at one
  place only hangs from that place: nodes are the wood wider than LANE_MM + 8 plus the plate's
  frame, every lane fragment between nodes must touch them at two or more separate places, else
  it is cut away. The pass runs before and after island bridging (bridges overshoot their joints
  and leave stubs). It is the general answer to loose lane ends; the design-side rules remain:
  a figure's lanes are clipped to the figure plus its contour so they never run on into the
  lattice, face features are drawn in proportion to the head radius with every lane edge to edge,
  and lattice cells that a figure's contour would leave under 40 % are dropped whole.

## Related

- [README.md](README.md) — the hub: status, what the pictures are, the other pages.
