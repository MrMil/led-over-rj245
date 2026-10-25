# Parts, tools and spares

[← README](../README.md) · [Build](build.md)

## Electronics

| Item | Qty | Notes |
|---|---|---|
| ESP32 dev board, 30-pin, ESP32-WROOM-32, USB-C, CH340C (HW-394), **no PSRAM** | 1 + 1 spare | All 14 GPIOs in [wiring.md](wiring.md) must be broken out. Both arrive with the installation's WLED on them; do not reflash. Laptop needs the CH340 driver |
| Female header 1 × 15, 2.54 mm (Assmann A-BL254-EG-Z15D) | 2 + 2 spare | The ESP32 plugs into a socket so it can be swapped in the field |
| 74AHCT125 (DIP-14) + socket | 2 (controller, optional) + 14 (power boxes per statue: 2 each in T2 and T6, 1 each in T3, T4, T5) + 2 spare | SN74AHCT125N + Assmann A 14-LC-TT sockets. Replacements must be **AHCT** and DIP (N suffix; NSR is surface-mount) |
| MAX485 module, 5 V (blue board) | 7 + 7 + 2 spare | 7 transmitters (controller), 7 receivers (box 2). **Chip must read MAX485** |
| Resistor 560 Ω | 14 + spares | Idle bias, 2 per receiver |
| Resistor 100 Ω | 7 + 7 + 44 + spares | Controller outputs (optional), box 2 outputs, power-box outputs (optional) |
| Resistor 10 kΩ | 14 + spares | Pull-down on every tower data input |
| Perfboard, DIKAVS half-size (81 × 55) | 2 per apex box + 1 per power box + 1 spare | ESP32 board + transmitter board (box 2: receivers); power boxes: the tower's splitter |
| S-100-5 PSU (5 V 20 A) | 10 | 5 per statue |
| C14 inlet with fuse and switch | 10 | One per power box; 1 A fuse, + spares |
| Power strip | 2 | At each apex, ≥ 5 sockets |
| C13 cord, H07RN-F 3 × 1.5 (buried) | 8 | 4 per statue: to the power boxes in T2, T3, T5, T6 |
| C13 cord, short | 2 | 1 per statue: to the apex box (power box in T4) |
| 3-core cable 3 × 2.5 (flexible PVC, "פנדל") | per layout | 2 buried 5 V runs per statue: power box in T2 → T1, power box in T6 → T7. 5 top-feed cables per statue: tower height + the reach to its box |
| NYAF 2.5 mm², red + blue | ~20 m each | Inside boxes and neighbour bases; 8 short tails per top feed |
| XT60 pairs | 58 + 6 spare | 8: 2 buried runs per statue × 2 ends. 50: top-feed cables, 1 at the bottom + 4 at the top, T2–T6 (25 per statue) |
| JST-SM 3-pin pairs | 68 + spares | 28 strands + 6 data inputs per statue |
| WAGO 221-415 | 28 + spares | 2 per neighbour base (T1, T7), 2 at the top of each top feed (T2–T6) |
| 22 AWG 2-core | per layout | Tip-tower data: power box in T2 → T1, power box in T6 → T7 |
| Wire 0.5 mm², red + black | ~2 m each | PSU → perfboard |

## Cables and connectors

| Item | Qty | Notes |
|---|---|---|
| CAT5e (or better) patch lead, moulded plugs, 10 m | 3 + 2 spare | Between the boxes. One distinctive colour |
| RJ45 round threaded bulkhead coupler (24 mm hole) | 6 | 3 per box |
| Short patch cable | 2–3 | Cut up for the pigtails inside the boxes |
| Data cable (DATA + GND) | 12 lines | Apex box → power boxes, per statue: 2 each to T2 and T6, 1 each to T3 and T5 |

## Enclosures

Printed from [MrMil/electronics-enclosure](https://github.com/MrMil/electronics-enclosure)
in PETG or ASA (not PLA):

| Enclosure | Qty | For |
|---|---|---|
| `100W-masterbox` | 2 | Apex box per statue: the power box in T4, T4's splitter and its 4 JST-SM, + ESP32 (statue 1) or receivers (statue 2); needs data outputs to the power boxes in T2, T3, T5, T6 and a top-feed XT60 out (change pending) |
| `100W` | 8 | Power boxes in T2, T3, T5, T6 per statue: 4 JST-SM out; needs data inputs, a top-feed XT60 out, and in T2 and T6 an XT60 + tip-tower data output (change pending) |

## LED strips

WS2812B, 5 V, 60/m (bought). Supplied and mounted by the statue artist: 4 strips per tower,
one per face, 150 mm dark base. 74.8 m in all: 15 reels of 5 m cut, every face whole from one
reel ([cut list](build.md#cutting-the-led-strips)), + 1 reel spare.

## Consumables

Ferrule kit (0.25–1.5 mm²), zip ties, heat-shrink, labels.

## Tools

- Multimeter
- Screwdrivers for the screw terminals and PSU terminals
- Ferrule crimper, strippers, side cutters
- Soldering iron
- Pickaxe and shovel

## Spares bag (goes to the field)

- 2 CAT5e cables
- 1 MAX485 module
- 1 ESP32, flashed with the show
- 2 × 74AHCT125
- 1 A fuses for the C14 inlets
- Ferrules, zip ties
