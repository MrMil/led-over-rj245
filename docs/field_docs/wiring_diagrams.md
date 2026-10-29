# Wiring diagrams

Path: [docs](../README.md) › [field_docs](README.md) › **wiring_diagrams**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py`, `guide/img/*.svg`
**Covers:** how the eight diagrams are produced and the drawing conventions they follow.

## What it does

`python3 tools/wiring_diagrams.py` writes `site-map.svg`, `overview.svg`, `master-box-wiring.svg`,
`slave-box-wiring.svg`, `power-box-1-tower.svg`, `power-box-2-tower.svg`, `tip-tower-cable.svg` and
`statue-power.svg` into `guide/img/`.
Standard library only. The tables in the script (`TOWER_H`, `GPIO`, `RJ45`, `CH_PINS`, `JACKS`,
`SUPPLIES`) feed the diagrams; the site map reads `layout/statue-layout.json`.

## Decisions

- **Generated, not hand-drawn** (agent, 2026-10-09). The GPIO map and RJ45 pinout appear in
  two diagrams each; generating from one table means they cannot disagree. A future agent can
  change a pin by editing one line, which it cannot reliably do in a drawing tool's file.
- **Plain SVG** (agent, 2026-10-09). GitHub renders it inline on phones and desktops, it
  zooms without blurring, and it diffs as text. Rejected: KiCad/Fritzing (need a desktop app
  to view or edit; exported PNGs blur when zoomed), Mermaid (cannot draw pin-level wiring).
- **Explicit white background** (agent, 2026-10-09). GitHub's dark mode would otherwise put
  black wires and text on a dark page.
- **Signals and power in separate diagrams** (agent, 2026-10-09). Drawing strip-current
  wiring on the signal diagrams doubled their line count; power is the same in both boxes,
  so it is drawn once. Signal diagrams reach the perfboard rails through `+5V`/`GND` net-label
  flags, the standard schematic convention.
- **RJ45 pigtail wires drawn in T568B colours, striped for white/colour** (agent, 2026-10-09).
  The builder lands those exact wires on screw terminals; matching colours removes a lookup.
- **RJ45 connections shown by matching labels, not drawn wires** (agent, 2026-10-10). With three
  channels per jack, channel 2 (pins 3/6) straddles channel 3 (pins 4/5), so drawn wires
  would have to cross. Each module's A/B pin is labelled "jack N · pin P (colour)", and the
  jack table lists the same.
- **Real module pin names (RO, RE, DE, DI, VCC, GND, A, B) and 74AHCT125 pin numbers** so the
  diagram can be followed against the physical part.
- **All 14 pins of every 74AHCT125 drawn, power and enables included** (owner asked,
  2026-10-11). VCC, GND and the four OE pins used to be a one-line note inside the chip; the
  builder solders all 14 pins, the OE pins (1, 4, 10, 13) are scattered round the package, and
  a missed one leaves a face dark. Each is now a pin with a `+5V`/`GND` flag, as on the MAX485
  modules. An unused gate shows its input to GND and its output "n/c".
- **A to-scale site map in the main README, generated from `layout/statue-layout.json`,
  every step between towers drawn corner to corner as its across and along legs** (owner,
  2026-10-29: "a separate to-scale map of the towers with orientation, direct distances and
  manhattan distances", then "in the main readme"; "by manhattan distance i meant show the x
  and y graphically. this is to help them in the field"; "do the distances from bottom corner
  to top corner", the facing corners). `site_map()` draws the whole site on a 1 m grid and
  one statue enlarged, where each step is a dashed right angle from the lower tower's corner
  that points at the next tower to that tower's corner pointing back: the across leg (x) and
  the along leg (y) in metres, plus the straight corner-to-corner tape. Corners, not centres,
  because the crew measures from the wood with a tape and cannot find a centre; the legs,
  because a tape and a right angle are what they have in the field. The table repeats the
  numbers and the README restates it in Markdown for phones. Orientation is relative to the
  site, not the compass: the apex-to-apex line, T1 on the left when facing a statue from the
  bench, and the 45° turn of every tower, because no compass bearing is recorded anywhere in
  the repo. Reading the layout file means the map cannot drift from the positions the tool
  exports. **Changed 2026-10-29 (twice, the same day):** first centre to centre with a
  Manhattan column, then with the legs drawn, then corner to corner.
- **The overview draws mains and data as separate lines: brown cords chained tower to tower
  along the arms, orange data lines fanning from the master/slave box** (owner, 2026-10-29).
  One orange line per box labelled "data and 230 V" read as one power cord from the apex to
  each box, which is not how mains runs
  ([../strips_and_power/power_distribution.md](../strips_and_power/power_distribution.md)).
- **One drawing per kind of power box, each ending in a "what goes into one box" count**
  (owner, 2026-10-29: "separate the diagrams of the 1 tower power box and the 2 tower power
  box? i don't understand what I need to make and it's really stressful"). `power_box(two)`
  draws the same board in both (one chip, gates 1 and 2 with their resistors): the 1 tower
  power box with one XT60 and gate 2's connectors as dashed grey outlines saying what is
  not there, the 2 tower power box with the tip tower's data in/out and second XT60 fitted
  ([../strips_and_power/tower_base.md](../strips_and_power/tower_base.md)). The builder
  has one box in front of them and should see only that box, with its part count beside it;
  `guide/wiring.md` has a section and a connection table per kind for the same reason. The
  dashed outlines, rather than leaving the space blank, are so that a builder who has just
  made a 2 tower power box sees the same board and knows the gap is deliberate.
  **Changed 2026-10-29:** previously one `power-box.svg` for all ten boxes, with the tip-tower
  parts in a band marked "2 tower power boxes only" (agent, 2026-10-18), to draw the shared
  circuit once. Changed because the owner, about to build eight boxes, could not tell from it
  what to make. The first split still showed a second chip labelled "tip tower", which the
  owner read as electronics in the tip tower; the label now names the gate, not a place.
  **Changed 2026-10-29 (later):** the 1 tower drawing first showed gate 2 as an unused gate
  (input to GND, output n/c); it now shows gate 2 with its resistors and dashed connectors,
  since the owner settled on one board for every box.
- **Vertical layout for the controller diagram** (agent, 2026-10-09). Phones scroll vertically
  much more comfortably than they pan sideways.

## Gotchas

- Never hand-edit the SVGs; re-run the script.
- `guide/wiring.md` and the LED Preferences table in `guide/build.md` restate the pin tables in
  prose and are **not** generated; update them alongside the script.
- Coordinates are hand-placed to avoid wire crossings. After changing a table, render and look
  (e.g. `qlmanage -t -s 1600 -o <dir> guide/img/<name>.svg` on macOS; it fills a square and
  crops, so first copy the SVG with `width`, `height` and the `viewBox` set to the larger of
  the two, render that, and crop the PNG back).

## Related

- [../controller/gpio_assignment.md](../controller/gpio_assignment.md) — source of the `GPIO` table.
- [../data_link/cabling.md](../data_link/cabling.md) — source of the `RJ45` table.
