# GPIO assignment

Path: [docs](../README.md) › [controller](README.md) › **gpio_assignment**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`GPIO`), `guide/wiring.md`, `guide/build.md` (LED Preferences table)
**Covers:** the ESP32 pin for each of the 14 tower channels.

## What it does

| GPIO | Channel | GPIO | Channel |
|---|---|---|---|
| 4 | S1-T1 | 21 | S2-T1 |
| 13 | S1-T2 | 22 | S2-T2 |
| 14 | S1-T3 | 23 | S2-T3 |
| 16 | S1-T4 | 25 | S2-T4 |
| 17 | S1-T5 | 26 | S2-T5 |
| 18 | S1-T6 | 27 | S2-T6 |
| 19 | S1-T7 | 32 | S2-T7 |

GPIO 33 is spare. Statue 1 channels go to the 74AHCT125s; statue 2 channels to the MAX485
transmitters.

## Decisions

- **Pins avoid strapping (0, 2, 5, 12, 15), flash (6–11), UART0 (1, 3) and input-only (34–39)
  pins** (owner for the original 8; agent, 2026-10-10 for the 6 added). Strapping pins change
  boot mode if a buffer or transceiver pulls them; flash pins are taken; input-only pins cannot
  drive data. That leaves exactly 15 output pins; 14 are used.
- **GPIO 16/17 are used, so the board must have no PSRAM** (owner).
- **WLED output order follows the show order: statue 1 T1 → T7, then statue 2 T1 → T7**
  (agent, 2026-10-10). Effects that run along the logical strip then sweep across each
  statue's V in order. GPIOs ascend in the same order so the table reads straight.

## Gotchas

- The pin table exists in three places that must agree: `tools/wiring_diagrams.py`,
  `guide/wiring.md`, and the LED Preferences table in `guide/build.md`.
- A microSD card for pre-rendered playback (possible later) needs 4 pins; with 14 outputs only
  GPIO 33 and strapping pins remain. Going to 12 channels would free two pins for it.
- Changing the order of WLED outputs scrambles travelling effects.

## Related

- [local_outputs.md](local_outputs.md) — what happens after statue 1's GPIOs.
- [../data_link/cabling.md](../data_link/cabling.md) — the RJ45 pinout statue 2's channels use.
