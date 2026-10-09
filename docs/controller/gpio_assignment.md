# GPIO assignment

Path: [docs](../README.md) › [controller](README.md) › **gpio_assignment**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`GPIO`), `guide/wiring.md`, `guide/build.md` (LED Preferences table)
**Covers:** the ESP32 pin for each of the 8 channels and the jack each remote channel leaves on.

## What it does

| GPIO | Channel | Path |
|---|---|---|
| 13 | S0-A | 74AHCT125 gates 1+2 → LED exits 1, 2 |
| 14 | S0-B | 74AHCT125 gates 3+4 → LED exits 3, 4 |
| 16 | S1-A | MAX485 → jack 1 pins 1/2 |
| 17 | S1-B | MAX485 → jack 1 pins 3/6 |
| 18 | S2-A | MAX485 → jack 2 pins 1/2 |
| 19 | S2-B | MAX485 → jack 2 pins 3/6 |
| 23 | S3-A | MAX485 → jack 3 pins 1/2 |
| 25 | S3-B | MAX485 → jack 3 pins 3/6 |

## Decisions

- **Pins avoid strapping (0, 2, 12, 15), flash (6–11) and input-only (34–39) pins** (owner).
  Strapping pins change boot mode if a strip or transceiver pulls them; flash pins are taken;
  input-only pins cannot drive data.
- **GPIO 16/17 are used, so the board must have no PSRAM** (owner). On WROVER/PSRAM modules
  they are the PSRAM bus.
- **WLED output order follows statue order 0→1→2→3, A before B** (owner: "define the 8 outputs
  as one continuous logical LED space in the order the wave should travel"). The GPIO numbers
  are ascending in the same order so the table reads straight.
- **Jack 1 is the coupler nearest the masterbox's LED exits** (agent, 2026-10-09). The
  masterbox has three couplers in its back wall at u = 96, 147, 200 mm and the LED exits at
  u = 14–68 (enclosure repo, `enclosures/100W-masterbox/enclosure.yaml`); numbering outward
  from the exits gives the crew a physical rule that needs no diagram.

## Gotchas

- The pin table exists in three places that must agree: `tools/wiring_diagrams.py`,
  `guide/wiring.md`, and the LED Preferences table in `guide/build.md`. Change all three
  together (the script regenerates the diagrams; the two guide tables are hand-written).
- Changing the order of WLED outputs reverses or scrambles travelling effects — see
  [../firmware/README.md](../firmware/README.md).

## Related

- [local_outputs.md](local_outputs.md) — what happens after GPIO 13/14.
- [../data_link/cabling.md](../data_link/cabling.md) — the RJ45 pinout the remote channels use.
