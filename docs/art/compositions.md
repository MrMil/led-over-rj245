# The compositions

Path: [docs](../README.md) › [art](README.md) › **compositions**
Parent: [README.md](README.md)
**Covers:** what each of the four pictures shows, where it lands on the towers, and the design decisions made on the way (fill, no mazes, figures, hands, feathers, cap, iris).

## Decisions

- **Dense everywhere: the whole picture is a lattice of cut cells, and figures are glowing shapes
  with a wood contour** (owner, 2026-10-22: "a lot of the wood stays blank — I want the LED light
  to come through and the animations to be visible, and the pattern to be really intricate";
  a blank diffuser is as bad as blank wood). Consequences in the script: a mandala of bands
  (rays, ring cells, petals) radiates from the picture's energy centre over the whole picture.
  (A maze filled whatever wood was left blank, and split cut areas wider than `MAX_SOLID_MM`,
  until the owner removed the mazes; see below.)
- **The filler is a maze, and not a perfect one** (owner, 2026-10-22: "I don't like the black
  dots, make it a more intricate pattern, maybe something like a maze", then "make sure it's not
  hanging by a thread"). A perfect maze's walls form a tree: every wall is a cantilever hanging
  from one joint, exactly the thread. So the maze starts from the full lattice of ring and radial
  walls around the picture's centre and removes walls at random only while both end joints keep
  at least two other walls: every wall segment stays anchored at both ends and the wood keeps its
  loops. The same rule governs the figures' internal wood: feather veins and tail ribs run tip to
  base, tear veins top to tip, dress lanes edge to edge, so no lane inside a cut shape is held at
  one end only.
  The maze's corners are rounded by an opening and a closing with an 8 mm disc (owner, 2026-10-22:
  square corners "look like a cyberpunk thing").
  **Changed 2026-10-22:** the filler was a dot lattice and the splitter a honeycomb; the owner
  rejected the dots the same day.
- **No mazes for now** (owner, 2026-10-22: "the mazes are sometimes applied to an area and
  sometimes not, the inconsistency looks bad; remove all the mazes and I'll tell you where to add
  mazes"). The maze class stays in the generator but nothing uses it.
- **The mandala fills the large wood only, through a mask with a margin** (owner, 2026-10-22,
  after a round with no fill at all: "wherever there is a large section of wood bring back the
  mandalas; create a mask of where you're allowed to put the mandalas, with a margin so they don't
  interfere with the drawing"). Each picture has one `fill` op (its mandala bands from the
  picture's centre), applied after every figure and clipped to the plate's cut domain minus every
  figure grown by `FILL_MARGIN_MM` (60 mm). It is clipped, not restricted to whole cells (the owner
  rejected whole cells): the slivers the clip leaves are the next rule's business. The fill is
  computed cell by cell against the mask, because one union of the whole mandala per plate took
  minutes.
- **Feathers: a masked vane with barbs running past the outline, layered so each hides the ones
  behind it** (owner's construction, 2026-10-22: "leave the rectangles in, mask them and make the
  spines go to infinity"; and "it should look like the feathers hide each other, right now it
  looks like they are tangled"). The vane outline is the mask; inside it a wood rachis and wood
  barbs at 55° towards the tip run from far beyond one edge to far beyond the other, so every cell
  is a parallelogram cut off by the outline, pointed where the outline meets it, never a rectangle;
  the quill (the first 16 %) is a solid cut. Eight feathers per wing, bases down the body's side,
  tips on an arc, listed back (top) to front (bottom): each feather's cuts minus the vanes of the
  feathers in front of it grown by 1.2 lanes, so the front one hides the back one with a wood
  contour between them. The tail is five such feathers, the middle one in front (owner: "I like
  the small tail, it looks good"). Earlier fans (leaf-shaped cells; spacing-capped vanes with
  barbs out past the edge) were rejected as tangled or blunt.
- **The fill's mask is every cut so far, not only the figures** (agent, 2026-10-22). The gills and
  the eye white are lattices, not figures; with a figure-only mask the mandala fill ran over the
  gills, two lattices crossed, and the thin-wood and cantilever passes turned the apex plate's gills
  into a slab.
- **The woman spans the three middle towers** (owner, 2026-10-22: "the human figure is a tiny
  thing in the middle and most of what we see is just arms"). Her head is 210 design units across
  (the apex tower's slot is 157), so it runs onto the tops of T3 and T5, the shoulders sit at the
  neighbours' edges and the dress fills T3 to T5; the hands and the face are exempt from the
  solid-area splitting so they stay whole shapes.
- **The woman's hands bless palms down, fingers out and slightly down** (owner, 2026-10-22:
  palms up, fingers up "looks like she surrenders"). The arms follow the arms of the V, so the
  hands land on the tip towers, each inside its own mandala.
- **The picture's axis is the apex tower's corner, and the design accounts for the borders
  there** (owner, 2026-10-22). Each face keeps a 20 mm wood border, so a 40 mm wood strip runs
  down the middle of every picture (and along every tower edge). The cut domain of a plate is the
  rectangle inside the border and above the base; the previews draw both; features on the axis are
  wide enough to read on both sides of the strip (the pupil splits like a cat's eye; the third eye
  is a lens, not a dot).
- **A wing is a cleared region** (owner, 2026-10-22: "the bird's feathers look like you didn't
  look at them"). The mandala lattice ran between and under the feathers, so near the body, where
  the feathers nearly touch, its rays read as more feathers and the clipped cells as shards. The
  lattice is cleared from each wing's convex hull and the feathers stand on wood.
- **The mushroom cap keeps every crackle cell** that is at least 12 mm wide (agent, 2026-10-22):
  dropping the small and edge cells left the dome ragged (owner: "the top of the mushroom is all
  broken up and doesn't have the oval shape it had").
- **The iris is 140 mm** (owner, 2026-10-22: "the eye has a huge part that is solid wood around
  the middle"): with a 200 mm iris the eye white had no room for its rays between the rim and the
  lids after the clearances, and came out solid.
- **Hands are one clean shape each** (owner, 2026-10-22: "the woman's thumbs are on the wrong
  side"). Thumbs on the upper side, four fingers close together and wide, no palm lines, and the
  arm's bracelet and centre lanes stop 110 units short of the hand.
- **The mushroom cap's crackle keeps its large blocks** (owner, 2026-10-22: "I liked the large
  blocks in the big mushroom, keep them"). The cap is exempt from the solid-area splitting
  (`keep_solid`), so its Voronoi cells stay whole even where they pass `MAX_SOLID_MM`.

### The compositions

Where things land, from the silhouettes in `art/viewpoints.json`. From the bench the picture is
an arch: the near tip towers reach the bottom of the picture, the far apex tower only its top
40 %, and the apex tower is a slot 8 % of the width. From behind, the apex tower fills the
middle half of a tall picture and the other towers show only a band around mid-height.

- **bench1, the woman:** head across the apex tower and its neighbours' tops (hair as flame rays,
  wood eyes, nose and smile), a dress over T3 to T5 with a chevron-and-vertical lattice and a wheel
  at the heart, arms down the V with bracelet cells, hands on the tip towers with palm lines, a
  mandala from the heart behind everything and one from each palm.
- **back1, the eye:** iris on the apex tower's corner (pupil, two spoked rings, dashed rim), the
  eye white as rays from the iris, lids that stop short of the corners so the eye white reaches
  the outside, lashes, brow, three tears below, spirals and flowing lines beyond the corners on
  the tip towers, a mandala from the iris outside the almond.
- **bench2, the bird:** a head in profile turned to the left with a hooked beak, an eye and the
  third eye (owner, 2026-10-22: "the bird looks like a moth, make the body bigger, make it look to
  one side and give it a beak"), a crest, a breast twice the apex slot's width with a herringbone,
  wings as fans of eleven feathers with veins, barbs and eye spots reaching the tip towers, covert
  rows at the shoulders, a seven-feather tail, a mandala from the third eye.
- **back2, the mushroom:** the cap's dome on the apex tower with a Voronoi crackle of wood lanes,
  its rim sweeping down over the side towers with the gills (a ray field from the stem top) and a
  dashed collar, a stem with fibre and cross lanes and its ring, small mushrooms and mycelium at
  the foot, spirals of spores on the side towers' band, a mandala from the cap's centre.

## Related

- [README.md](README.md) — the hub: status, what the pictures are, the other pages.
