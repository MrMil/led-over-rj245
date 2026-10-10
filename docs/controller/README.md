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
  the PSRAM bus on WROVER modules. 14 outputs need the RMT + I2S mix of WLED 16
  ([../firmware/README.md](../firmware/README.md)).
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
- **Logic power from the box's PSU on its own wire pair** (agent, 2026-10-09), so tower
  current never flows through the perfboard. Budget ≤ 0.75 A: ESP32 with its access point
  (~0.25 A average, ~0.5 A peak) plus 7 MAX485 at ~40 mA into the 60 Ω terminated line.
  See [../strips_and_power/power_distribution.md](../strips_and_power/power_distribution.md).

### Gotchas

- The dev board's USB port is for flashing/debug. Powering from USB while the PSU is also
  connected relies on the board's VBUS diode; do not back-feed the PSU from USB for long.
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
