# Wiring diagrams

Path: [docs](../README.md) › [field_docs](README.md) › **wiring_diagrams**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py`, `guide/img/*.svg`
**Covers:** how the four diagrams are produced and the drawing conventions they follow.

## What it does

`python3 tools/wiring_diagrams.py` writes `overview.svg`, `controller-wiring.svg`,
`statue-wiring.svg` and `box-power.svg` into `guide/img/`. Standard library only. The pin
tables (`GPIO`, `RJ45`, `EXITS`) at the top of the script feed every diagram.

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
  wiring on the signal diagrams doubled their line count; power is identical in all four boxes,
  so it is drawn once. Signal diagrams reach the perfboard rails through `+5V`/`GND` net-label
  flags, the standard schematic convention.
- **RJ45 pigtail wires drawn in T568B colours, striped for white/colour** (agent, 2026-10-09).
  The builder lands those exact wires on screw terminals; matching colours removes a lookup.
- **Real module pin names (RO, RE, DE, DI, VCC, GND, A, B) and 74AHCT125 pin numbers** so the
  diagram can be followed against the physical part.
- **Vertical layout for the controller diagram** (agent, 2026-10-09). Phones scroll vertically
  much more comfortably than they pan sideways.

## Gotchas

- Never hand-edit the SVGs; re-run the script.
- `guide/wiring.md` and the LED Preferences table in `guide/build.md` restate the pin tables in
  prose and are **not** generated; update them alongside the script.
- Coordinates are hand-placed to avoid wire crossings. After changing a table, render and look
  (e.g. `qlmanage -t -s 1600 -o <dir> guide/img/<name>.svg` on macOS; it renders square, so
  wide diagrams appear cropped unless width = height).

## Related

- [../controller/gpio_assignment.md](../controller/gpio_assignment.md) — source of the `GPIO` table.
- [../data_link/cabling.md](../data_link/cabling.md) — source of the `RJ45` table.
