# Layout tool: spacings, arm methods, free positions, undo

Path: [docs](../../README.md) › [strips_and_power](../README.md) › [statue_geometry](README.md) › **controls**
Parent: [README.md](README.md)
**Covers:** the controls that place the towers: individual spacings, the arm methods, statue 2 on its own, dragging towers, undo. The solver itself is in [README.md](README.md).

## Individual spacings

The six pairs T1–T2 … T6–T7 each have their own control (owner, 2026-10-19). Until one is
touched they show the solved spacing; once the user edits one, the layout is "set by hand": the
solver no longer overwrites the pairs, and each arm is solved with its own three chords (left
arm T4→T3→T2→T1, right arm T4→T5→T6→T7), so the two arms may differ. Changing minimum, maximum
or optimum then asks before resetting the pairs, because hand-set values are deliberate; "keep
mine" also puts the three range values back. The page's own confirmation box is used because
`confirm()` returns false inside hosted viewers.

## Arm methods

"Arm shape → Method" chooses how the towers of each arm sit on the spacings. All three keep the
apex tower's far corner on the circle and the apex turned 45° to its axis, a corner at the centre.
- **Solved, touching** (`touch`; agent, 2026-10-19, reason under Decisions in
  [README.md](README.md)): each tower turned so one corner points at the centre; the next tower
  is placed at the chosen spacing where its silhouette touches the previous one from the eye,
  with every silhouette taken as the box's half-diagonal.
- **Straight arm at an angle** (`straight`): towers on a straight line at the angle slider's
  angle, kept for comparison.
- **Solved, all towers at 45° like the apex** (`parallel`, the default since the artist chose it
  on 2026-10-23, [final_layout.md](final_layout.md); owner, 2026-10-23, for the artist:
  "the rotation of all towers is like the apex, but the edges still touch from the POV"). Every
  tower of a statue has the apex tower's rotation, so its diagonals run along and across the
  apex axis. Because such a box shows a different width depending on where it stands, this
  method measures each tower's real corners from the eye and places the next tower where its
  left edge meets the previous one's right edge, still at the chosen spacing; the readout's gap
  column measures the same corners, so it reads 0.0 throughout. With her spacings the inner
  towers barely move (they stand almost on the axis) and the tips move up to 34 mm against
  `touch`. Free (dragged) towers also take the apex rotation in this mode. The export writes
  `arm.method: "parallel"`, `corner_towards_centre: false` and `box_yaw_deg` 45 (statue 1) or
  225 (statue 2) for every tower.
- **Switching the method keeps hand-set spacings and dragged positions** (agent, 2026-10-23).
  The method only changes how towers sit on the spacings, and the reset question that other
  solver settings ask made it impossible to try the artist's spacings with the 45° method: "keep
  mine" put the old method back. **Changed 2026-10-23:** previously the method was a solver
  setting like the spacing range and asked before re-solving.
- **The circle, free radius and bench checks use each box's real nearest and farthest point**
  (agent, 2026-10-23), not centre distance ± half-diagonal, which is only exact for a corner at
  the centre; for `touch` and `straight` the results are the same as before.

## Statue 2 on its own, free positions, undo

- **Statue 2 mirrors statue 1 until "Set statue 2 separately" is ticked** (owner, 2026-10-19, for
  the artist: move everything together first, then decouple). Ticking it copies statue 1's
  heights, pair spacings and positions into statue 2, which then has its own controls, its own
  mural projection, its own level-top heights and its own LED/supply side. Unticking asks first
  when statue 2 differs, because it loses those settings.
- **Towers can be dragged freely in the top-down view, and in the eye and drone views with the
  "Drag towers" toggle on** (owner, 2026-10-19; the toggle sits with the view buttons). The toggle
  takes the left button and the single finger away from the camera, so right-drag, the pad and
  the keys still move the camera while towers are being placed. The first drag
  snapshots the solved positions; from then on the solver is bypassed, the pair boxes only report
  distances, and the readout checks the circle and the free radius as before. Towers keep one
  corner to the centre wherever they stand, because the mural is still read from there (in the
  45° method they keep the apex rotation instead, above). Dragging
  a tower while coupled moves its mirror on statue 2. Any solver setting (spacing range, circle,
  free radius, side, wood thickness, arm angle) asks before re-solving, exactly as for hand-set
  pairs; "keep mine" puts the setting back. The arm method does not ask (above).
- **Hand-placed positions are labelled "placed by hand", not "moved"** (owner, 2026-10-21: the
  artist's file is a hand-placed layout, and "moved freely" on the default read as if the tool had
  moved her towers). A drag only switches a solved layout to hand placement once the tower actually
  moves; a plain click leaves it solved. While statue 2 mirrors statue 1, the export writes statue 2's
  positions as the mirror, never the snapshot taken when dragging began (her file carried such a
  stale snapshot; loading ignores it while mirrored, so nothing was lost).
- **Undo and redo keep a stack of parameter snapshots**, one per change that rebuilt the layout
  (owner, 2026-10-19). A slider drag collapses into one step (same control within 0.8 s). Undo
  restores through the same loader as the JSON file, so it is as complete as the export. The stack
  is per page load; the browser store keeps only the latest state.
- **Cameras** (owner, 2026-10-19: as in 3D software, with a pad so it works on a phone). Eye view:
  left-drag looks, right-drag or arrows/WASD walks; the eye height slider keeps the walked
  position. Drone: left-drag orbits, right-drag or arrows pans, wheel zooms. The on-screen pad
  does the same by touch. Pressing the active view's button, or ⟲, resets that camera.
- **The drone view opens zoomed to the circle** (owner, 2026-10-23: "zoomed in to include the
  circle. the outside viewpoint doesn't need to be there"). Its home looks from the same corner
  as before and moves in as far as the circle, and the tallest tower standing on it, still fit the
  window at its current shape; the back viewpoints' figures outside the circle may be cut off.
  The settings panel floats over the left of the view, so on a narrow window it can cover part of
  the circle; "Hide" folds it. **Changed 2026-10-23:** previously the home was a fixed position
  scaled with the circle, and a slip scaled it twice (once when set, again on the first layout),
  which opened the view about 56 m out with the whole scene small in the middle.

## Related

- [README.md](README.md) — what the tool solves and why.
- [final_layout.md](final_layout.md) — the defaults these controls start from.
