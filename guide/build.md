# Building and configuring the boxes

[← README](../README.md) · [Wiring](wiring.md) · [Parts](parts.md)

Workshop steps. [Restore a backup](#restore-a-backup) and
[prepare a spare ESP32](#prepare-a-spare-esp32) also apply in the field.

## 1. Enclosures

Print from [MrMil/electronics-enclosure](https://github.com/MrMil/electronics-enclosure):
two `100W-masterbox` (controller and box 2). Each needs 3 RJ45 couplers, 7 tower data outputs
and 7 tower power outputs. PETG or ASA, not PLA.

## 2. Boards

Follow [wiring.md](wiring.md) and the diagrams there.

**Controller box:**
- ESP32 board (breadboard-style, 30 rows), in this order along the board:
  - ESP32 on 2 × 1×15 female headers, at one end, over a mounting hole.
  - 74AHCT125 #1 in a socket.
  - 74AHCT125 #2 in a socket, at the other end, over the other mounting hole.
  The board is held by **one bolt**, in the hole under the ESP32. The hole under chip #2
  gets no bolt: that end rests on its standoff. To bolt or unbolt the board, pull the ESP32;
  the hex key goes in between its header strips. When pulling chip #2, hold that end of the
  board down.
- 7 × 100 Ω, standing upright: one lead in a free hole of the chip output's row (not on the
  chip leg, which must stay removable), the wire to the tower data output soldered to the
  top lead. Heat shrink over the resistor and that joint. Tie the 7 wires down so they don't
  pull on the resistors.
- Transmitter board: 7 MAX485 modules.

**Box 2:** 7 MAX485 receivers, 7 pairs of 560 Ω bias resistors, 7 × 100 Ω.

**Supply boxes (A, B, D, E per statue; C's part sits in the apex box):** 74AHCT125 #1 in a
socket with a 10 kΩ pull-down on its input and 4 × 100 Ω to the 4 strand JST-SMs. A and E
also: 74AHCT125 #2 for the tip tower's data (one input with 10 kΩ, one 100 Ω on the output).

**Neighbour bases (T1, T7 per statue):** no electronics: 2 WAGO 221-415 and 4 JST-SM.

Check each module's chip marking reads MAX485 (not 483/487/488/489). The controller's
74AHCT125s and all 100 Ω resistors are optional, depending on space. Keep a spare receiver
module and spare 74AHCT125s.

## 3. Power wiring (10 supply boxes)

Per [supply-box.svg](img/supply-box.svg) and [statue-power.svg](img/statue-power.svg): C14 to
the PSU, PSU to the 4 strand JST-SMs and (A, E) the XT60 output, and in the apex box a
separate thin pair to the perfboard. Make up the buried 5 V cables (3 × 2.5) with XT60s at
both ends. Ferrules on every stranded wire.

## 4. Data cables

- Inside each box, cut a short patch cable for each of the 3 couplers and land its wires on
  the screw terminals using ferrules.
- With a meter, check every pin end to end, through both couplers and the long cable: pin N
  at the controller must reach pin N at box 2, and no pin may touch another.
- Label both ends of each CAT5e cable (1, 2, 3) and each tower cable (S1-T1 … S2-T7).

## 5. WLED is already on the ESP32s

The controller ESP32 and its spare arrive with the installation's own WLED on them. **Do not
flash them**, not even from install.wled.me: the standard release flickers with 14 outputs.

Join **WLED-AP** (password `wled1234`), open `http://4.3.2.1`.

## 6. Configure WLED

### WiFi Setup

| Setting | Value |
|---|---|
| Network (client) | leave empty |
| AP SSID | the installation's name, nothing that says "WLED" |
| AP password | a new, strong password. Give it to the installation lead. **Never on the hardware, never in this repository.** |
| AP opens | **Always** (the default only opens it when no known network is found) |
| AP channel | a fixed channel: 1, 6 or 11 |

### LED Preferences

Fourteen outputs, **in this order**: statue 1 T1 → T7, then statue 2 T1 → T7, all type
WS281x. The installation's build sends all 14 together; ignore the RMT/I2S label on each
output.

| # | GPIO | Channel | LED count (one face) |
|---|---|---|---|
| 1 | 4 | S1-T1 | 57 |
| 2 | 13 | S1-T2 | 75 |
| 3 | 14 | S1-T3 | 93 |
| 4 | 16 | S1-T4 | 111 |
| 5 | 17 | S1-T5 | 93 |
| 6 | 18 | S1-T6 | 75 |
| 7 | 19 | S1-T7 | 57 |
| 8 | 21 | S2-T1 | 57 |
| 9 | 22 | S2-T2 | 75 |
| 10 | 23 | S2-T3 | 93 |
| 11 | 25 | S2-T4 | 111 |
| 12 | 26 | S2-T5 | 93 |
| 13 | 27 | S2-T6 | 75 |
| 14 | 32 | S2-T7 | 57 |

- LED count = **one face**: lit height (tower − 150 mm) × 60/m. All 4 faces get the same data.
  Correct the counts to the strips as fitted.
- Colour order **GRB** (check: preset 1 must show T1 red).
- **Current:** WLED sees one face per output, the real draw is 4×. Set **LED current per LED
  (custom) to 118 mA** (4 × the measured 29.4 mA at full white), so WLED's estimate
  matches reality. Per-output limits: each tower's share of its box's LED
  budget; the firmware ceiling enforces the maximum.
- **Defaults → apply preset at boot:** the show playlist (once it exists).

### Presets

| Preset | Content |
|---|---|
| 1 · Test colours | One segment per output, solid: T1 red, T2 orange, T3 yellow, T4 green, T5 cyan, T6 blue, T7 magenta, both statues |
| 2 · Test order | A single light running along the whole strip (up each tower in turn) |
| 10–99 | Workshop looks |
| the show | A playlist of the workshop looks, set as the boot preset |

## 7. Bench test

Both boxes, the three 20 m cables, a tower-base board with test strips on each tower output
in turn. Presets 1 and 2, then the show for an hour. With a scope: RO on one receiver at the end of a 20 m cable should
show clean 350/700 ns pulses with no ringing.

## 8. Back up

**Config → Security & Updates → Backup presets** and **Backup configuration**. Save them in
this repository under `wled/` as `presets.json` and `cfg.json`.

**Before committing `cfg.json`**, open it and blank out the AP password if it's in there.
This repository may be public.

## Restore a backup

Restores outputs, show and WiFi onto a mis-configured or replaced controller. Needs
`wled/cfg.json` and `wled/presets.json` already downloaded to the phone.

1. Join the controller's WiFi (or **WLED-AP** / `wled1234` on an ESP32 not set up yet) and
   open `http://4.3.2.1`.
2. **Config → Security & Updates → Restore configuration**: choose `cfg.json`. The
   controller restarts.
3. Re-join its WiFi (its name may have changed to the installation's), and set the AP
   password again under **WiFi Setup** if the backup had it blanked.
4. **Config → Security & Updates → Restore presets**: choose `presets.json`.
5. Run preset 1 to check.

## Keep the spare ESP32 ready

It arrives with WLED on it. Restore both backups onto it, set the AP password, and label it
"SPARE, show loaded, <date>". Re-do it whenever the show changes.
