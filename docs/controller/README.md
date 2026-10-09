# Controller

Path: [docs](../README.md) › **controller**
Parent: [../README.md](../README.md)

**Covers:** the controller box at statue 0 — one classic ESP32 producing all 8 WS2812 data
channels, the 74AHCT125 for statue 0's own strips, the six MAX485 transmitters for statues
1–3, and the logic power for all of it.
**Code:** `tools/wiring_diagrams.py` (controller diagram, `GPIO` table), `guide/img/controller-wiring.svg`, `guide/wiring.md`; enclosure `100W-masterbox` in the enclosure repo.

## Design

### Decisions

- **Classic dual-core ESP32 (WROOM-32), no PSRAM** (owner). It has 8 RMT channels — exactly the
  8 outputs — and WLED supports up to 10 digital outputs on it. No-PSRAM is required because
  GPIO 16/17 are used ([gpio_assignment.md](gpio_assignment.md)). An ESP32-S3 would have only 4
  RMT TX channels and would need the I2S/LCD parallel path.
- **Six MAX485 transmitters, two per remote statue** (owner, 2026-10-09). Two of the 8
  channels are local (statue 0) and go through the 74AHCT125 instead. The enclosure repo
  (`100W-masterbox`) only has to fit an ESP32 perfboard and a MAX485 perfboard; its module
  count follows this design, not the other way round.
- **Transmitter DE and RE̅ hard-wired to 5 V** (owner). Each end only ever does one job, so no
  direction switching, no GPIO spent on it, and no timing hazard from software toggling.
- **MAX485 DI is driven straight from 3.3 V GPIO** (owner). The MAX485 is a 5 V part with
  TTL-threshold inputs (VIH 2.0 V), so no level shifter is needed on the RS-485 side.
- **ESP32 sits in a socket (female headers) on its perfboard** (agent, 2026-10-09). The ESP32
  is the one component whose failure stops all four statues; a socket lets the field crew
  swap in the pre-flashed spare without soldering ([guide/troubleshooting.md](../../guide/troubleshooting.md#spares)).
- **Logic power from the same S-100-5 that feeds statue 0's strips, on its own wire pair**
  (agent, 2026-10-09). The masterbox houses one PSU only. The summary's "separate logic rail"
  is implemented as a separate *wire run* from the PSU's second +V/−V terminals, so strip
  current never flows through the perfboard. Budget ~500 mA (owner): six transmitters each
  sourcing 20–40 mA into terminated line, plus the ESP32's WiFi peaks. See
  [../strips_and_power/power_distribution.md](../strips_and_power/power_distribution.md).

### Gotchas

- GPIO 14 outputs a PWM signal during boot; statue 0's channel B may flash briefly at
  power-up. Harmless; not worth a pin change.
- The dev board's USB port is for flashing/debug. Powering from USB while the PSU is also
  connected relies on the board's VBUS diode; do not back-feed the PSU from USB for long.
- Generator power is dirty: WLED must resume the show on reboot by itself (boot preset, see
  [../firmware/README.md](../firmware/README.md)).

## Contents

### Pages

- [`gpio_assignment.md`](gpio_assignment.md) — which GPIO drives which channel, and why those pins.
- [`local_outputs.md`](local_outputs.md) — statue 0's four strips through the 74AHCT125.

### Not yet documented

- **Transmitter board** — `guide/img/controller-wiring.svg` — six MAX485 TX modules on one perfboard; the chip-level decisions are in [../data_link/transceivers.md](../data_link/transceivers.md).
- **Link-alive indicator** — not built — the owner wants something on each enclosure showing the link is alive, readable without opening the box. No design yet.
- **Hardware watchdog** — not built — owner note: "hardware watchdog" for dirty generator power. Whether WLED's own task watchdog suffices is unknown.

## Related

- [../data_link/README.md](../data_link/README.md) — what the six transmitters drive.
- [../firmware/README.md](../firmware/README.md) — how the 8 outputs are configured in WLED.
