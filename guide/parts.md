# Parts, tools and spares

[← README](../README.md) · [Build](build.md)

## Electronics

| Item | Qty | Notes |
|---|---|---|
| ESP32 dev board, classic dual-core (ESP32-WROOM-32), **no PSRAM** | 1 + 1 spare | GPIO 16/17 are only free on boards without PSRAM. The spare is flashed with the show. |
| Female header strips | to fit the ESP32 | The ESP32 plugs into a socket so it can be swapped in the field |
| 74AHCT125 (DIP-14) + DIP-14 socket | 1 + 1 spare | Optional (see build). Must be **AHCT** |
| MAX485 module, 5 V (blue board) | 12 + 2 spare | 6 transmitters at the controller, 2 receivers per statue box. **The chip must read MAX485**, not MAX483/487/488/489 |
| Resistor 560 Ω | 12 + spares | Idle bias, 2 per receiver |
| Resistor 100 Ω | 8 + spares | Optional. One per data exit (exits 1 and 3 of each box) |
| Perfboard, DIKAVS half-size (81 × 55) | 5 + 1 spare | 2 in the controller, 1 per statue box; the spare carries the spare receivers |
| S-100-5 power supply (5 V 20 A) | 4 | One per box |
| C14 inlet with fuse and switch | 4 | 1 A fuse, + spares |
| C13 mains cord | 4 | Long enough to reach the camp's power distribution |
| WAGO 221-415 (5-way lever connector) | 8 | 2 per box: one 5 V, one GND |
| Wire 1.5 mm², red + black | ~2 m each | PSU → WAGO |
| Wire 0.5 mm², red + black | ~2 m each | PSU → perfboard |
| JST-SM 3-pin pigtail pairs | 16 + spares | 4 LED exits per box |

## Data cables and connectors

| Item | Qty | Notes |
|---|---|---|
| CAT5e (or better) patch lead, **moulded plugs**, 10 m | 3 + 2 spare | All the same length, so any spare fits any run. One distinctive colour, used for nothing else |
| RJ45 round threaded bulkhead coupler (24 mm hole) | 6 | 3 in the controller, 1 per statue box; the enclosures are drilled for them |
| Short patch cable | 3–4 | Cut up for the pigtails inside the boxes |

## Enclosures

Printed from [MrMil/electronics-enclosure](https://github.com/MrMil/electronics-enclosure)
in PETG or ASA (not PLA). Each enclosure's `BOM.md` there lists its bolts and nuts.

| Enclosure | Qty | For |
|---|---|---|
| `100W-masterbox` | 1 | Controller, statue 0 |
| `100W-rj45` | 3 | Statues 1, 2, 3 |

## LED strips

WS2812B, 5 V. Supplied and mounted by the statue artist; this build provides the connectors.
Counts TBD.

## Consumables

Ferrule kit (0.25–1.5 mm²), zip ties, heat-shrink, labels.

## Tools

- Multimeter
- Screwdrivers for the screw terminals and PSU terminals
- Ferrule crimper, strippers, side cutters
- Soldering iron
- Pickaxe and shovel

## Spares bag (goes to the field)

- 2 data cables
- 1 receiver board: 2 MAX485 receivers with bias resistors and a jack pigtail
- 1 ESP32, flashed with the show
- 1 74AHCT125
- 1 A fuses for the C14 inlets
- Ferrules, zip ties
