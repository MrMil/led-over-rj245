# Controller

Path: [docs](../README.md) › **controller**
Parent: [../README.md](../README.md)

**Covers:** the controller box in statue 1's base: one classic ESP32 producing all 14 tower
channels, two 74AHCT125 for statue 1's 7 towers, seven MAX485 transmitters for statue 2's 7
towers, and the logic power for all of it.
**Code:** `tools/wiring_diagrams.py` (`controller()`, `GPIO`), `guide/img/controller-wiring.svg`, `guide/wiring.md`; enclosure `100W-masterbox` in the enclosure repo.

## Design

### Decisions

- **Classic dual-core ESP32 (WROOM-32), no PSRAM** (owner). GPIO 16/17 are used, which are
  the PSRAM bus on WROVER modules. 14 outputs need more than the 8 RMT channels;
  how they are driven is open ([../firmware/output_driver.md](../firmware/output_driver.md)).
- **Seven MAX485 transmitters, one per statue-2 tower** (owner, 2026-10-10). Statue 2's
  channels cross the trench as RS-485 ([../data_link/README.md](../data_link/README.md)).
  **Changed 2026-10-10:** previously six (two per remote statue, three remote statues).
- **Transmitter DE and RE̅ hard-wired to 5 V** (owner). Each end only ever does one job, so no
  direction switching, no GPIO spent on it, and no timing hazard from software toggling.
- **MAX485 DI is driven straight from 3.3 V GPIO** (owner). The MAX485 is a 5 V part with
  TTL-threshold inputs (VIH 2.0 V), so no level shifter is needed on the RS-485 side.
- **ESP32 sits in a socket (female headers) on its perfboard** (agent, 2026-10-09). It is the
  one component whose failure stops both statues; a socket lets the crew swap in the
  pre-flashed spare without soldering.
- **Board: 30-pin HW-394 dev board (WROOM-32, USB-C, CH340C)** (owner, 2026-10-11). It is the
  board the owner bought; it breaks out all 15 usable output pins
  ([gpio_assignment.md](gpio_assignment.md)), and a WROOM-32 has no PSRAM. Its socket is two
  1 × 15 female headers (Assmann A-BL254-EG-Z15D); a 38-pin board would need 1 × 19 instead.
  **Checked 2026-10-24** on two boards: ESP32-D0WD-V3 (rev 3.1), 4 MB flash, no PSRAM; the
  first shipped with Espressif's AT firmware.
- **ESP32 board layout: ESP32 over one mounting hole, 74AHCT125 #2 in its socket over the
  other** (owner, 2026-10-11; socket and bolt changed 2026-10-25). The DIKAVS board is
  breadboard-style: every DIP-width part straddles the centre channel, and both M3 mounting
  holes are in that channel. The ESP32 (15 rows) and two chips (7 each) take 29 of the 30
  rows, so nothing can be moved off the holes.
- **The ESP32 board is held by one bolt, under the ESP32; the hole under chip #2 has none**
  (owner, 2026-10-25). An M3 socket head is 3 mm tall and a DIP socket sits < 1 mm off the
  board, so a bolt there would block chip #2's socket. Under the ESP32 the 8.5 mm female
  headers clear the head, and pulling the ESP32 gives the hex key a way in: its two strips are
  a dev-board width apart, far more than the 5.5 mm head (the old worry about filing applied
  to chip-width strips, ~5.1 mm apart). The unbolted end rests on its printed standoff (the
  enclosure still prints both). One bolt is enough for a board of light parts whose wires are
  tied down (agent, 2026-10-25; unverified in the field). Pulling chip #2 lifts that end, so
  the crew holds it down.
  **Changed 2026-10-25:** chip #2 sat on two 1 × 7 female headers over a second bolt (owner,
  2026-10-11). The chip's DIP legs, ~0.5 × 0.25 mm at the tip, are too thin for female-header
  contacts sized for 0.64 mm square posts: the chips fell out, and a loose leg can also lose
  contact without falling, so tape or hot glue would not have fixed it.
  **Rejected (2026-10-25):** *machined-pin female headers* or *a wire-wrap socket plugged into
  the headers* (no parts on hand and no time to buy them before the event); *dropping
  chip #2* and driving T5–T7 at 3.3 V (the signal would survive the ≤ 5 m runs to the supply
  boxes, but it leaves three GPIOs of the one ESP32 wired to cables that leave the box);
  *a countersunk bolt under the socket* (breaks the enclosure repo's one-bolt-type rule).
- **Logic power from the box's PSU on its own wire pair** (agent, 2026-10-09), so tower
  current never flows through the perfboard. Budget ≤ 0.75 A: ESP32 with its access point
  (~0.25 A average, ~0.5 A peak) plus 7 MAX485 at ~40 mA into the 60 Ω terminated line.
  See [../strips_and_power/power_distribution.md](../strips_and_power/power_distribution.md).

### Gotchas

- The dev board's USB port is for flashing/debug. Powering from USB while the PSU is also
  connected relies on the board's VBUS diode; do not back-feed the PSU from USB for long.
- **Opening the HW-394's USB serial port resets the ESP32**, even with DTR and RTS held off
  (seen 2026-10-24 on macOS). Reading its serial output restarts it, and a test running on
  the board starts over.
- Generator power is dirty: WLED must resume the show on reboot by itself (boot preset, see
  [../firmware/README.md](../firmware/README.md)).

## Contents

### Pages

- [`gpio_assignment.md`](gpio_assignment.md) — which GPIO drives which tower, and why those pins.
- [`local_outputs.md`](local_outputs.md) — statue 1's 7 tower outputs through two 74AHCT125.

### Not yet documented

- **Transmitter board** — `guide/img/controller-wiring.svg` — seven MAX485 TX modules on one perfboard; chip-level decisions in [../data_link/transceivers.md](../data_link/transceivers.md).
- **Link-alive indicator** — not built — the owner wants something on each enclosure showing the link is alive, readable without opening the box.
- **Hardware watchdog** — not built — owner note for dirty generator power; whether WLED's own task watchdog suffices is unknown.

## Related

- [../data_link/README.md](../data_link/README.md) — what the seven transmitters drive.
- [../firmware/README.md](../firmware/README.md) — how the 14 outputs are configured in WLED.
