# Parts, tools and spares

[← README](../README.md) · [Build](build.md)

## Electronics

| Item | Qty | Notes |
|---|---|---|
| ESP32 dev board, classic dual-core (ESP32-WROOM-32), **no PSRAM** | 1 + 1 spare | All 14 GPIOs in [wiring.md](wiring.md) must be broken out. The spare is flashed with the show |
| Female header strips | to fit the ESP32 | The ESP32 plugs into a socket so it can be swapped in the field |
| 74AHCT125 (DIP-14) + socket | 2 (controller, optional) + 14 (tower bases) + 2 spare | Must be **AHCT** |
| MAX485 module, 5 V (blue board) | 7 + 7 + 2 spare | 7 transmitters (controller), 7 receivers (box 2). **Chip must read MAX485** |
| Resistor 560 Ω | 14 + spares | Idle bias, 2 per receiver |
| Resistor 100 Ω | 7 + 7 + 56 + spares | Controller outputs (optional), box 2 outputs, tower faces (optional) |
| Resistor 10 kΩ | 14 + spares | Tower-base input pull-down |
| Perfboard, DIKAVS half-size (81 × 55) | 2 per box + 1 spare | ESP32 board + transmitter board; box 2: receiver board(s) |
| Small perfboard per tower base | 14 + 1 spare | 74AHCT125 splitter |
| S-100-5 PSU (5 V 20 A) | 10 | 5 per statue |
| C14 inlet with fuse and switch | 10 | One per supply box; 1 A fuse, + spares |
| Power strip | 2 | At each apex, ≥ 5 sockets |
| C13 cord, H07RN-F 3 × 1.5 (buried) | 6 | 3 per statue: to A, B, E |
| C13 cord, short | 4 | 2 per statue: to C, D |
| 3-core cable 3 × 2.5 (flexible PVC, "פנדל") | ~20–25 m | The 4 buried 5 V runs per statue, both statues |
| Wire 1.5 mm² | per layout | Ground bond along each arm |
| NYAF 2.5 mm², red + blue | ~10 m each | Inside boxes and tower bases |
| XT60 pairs | per layout | Supply outputs, buried runs, strand inputs |
| Wire 0.5 mm², red + black | ~2 m each | PSU → perfboard |

## Cables and connectors

| Item | Qty | Notes |
|---|---|---|
| CAT5e (or better) patch lead, moulded plugs, 10 m | 3 + 2 spare | Between the boxes. One distinctive colour |
| RJ45 round threaded bulkhead coupler (24 mm hole) | 6 | 3 per box |
| Short patch cable | 2–3 | Cut up for the pigtails inside the boxes |
| Tower data cable (DATA + GND) | 14 | Box → tower base; lengths per statue layout |

## Enclosures

Printed from [MrMil/electronics-enclosure](https://github.com/MrMil/electronics-enclosure)
in PETG or ASA (not PLA):

| Enclosure | Qty | For |
|---|---|---|
| `100W-masterbox` | 2 | Apex box per statue: supply C + ESP32 (statue 1) or receivers (statue 2); needs 7 tower data outputs and XT60 outputs (change pending) |
| `100W` | 8 | Supplies A, B, D, E per statue; needs XT60 outputs instead of JST-SM slots (change pending) |

## LED strips

WS2812B, 5 V, 60/m (bought). Supplied and mounted by the statue artist: 4 strips per tower,
one per face, 150 mm dark base.

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
- 1 MAX485 module, 1 tower-base board
- 1 ESP32, flashed with the show
- 2 × 74AHCT125
- 1 A fuses for the C14 inlets
- Ferrules, zip ties
