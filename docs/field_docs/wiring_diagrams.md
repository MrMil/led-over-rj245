# Wiring diagrams

Path: [docs](../README.md) › [field_docs](README.md) › **wiring_diagrams**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py`, `guide/img/*.svg`
**Covers:** how the six diagrams are produced and the drawing conventions they follow.

## What it does

`python3 tools/wiring_diagrams.py` writes `overview.svg`, `controller-wiring.svg`,
`box2-wiring.svg`, `power-box.svg`, `neighbour-base.svg` and `statue-power.svg` into `guide/img/`.
Standard library only. The tables in the script (`TOWER_H`, `GPIO`, `RJ45`, `CH_PINS`, `JACKS`,
`SUPPLIES`) feed the diagrams.

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
