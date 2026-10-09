# Building and configuring the boxes

[← README](../README.md) · [Wiring](wiring.md) · [Parts](parts.md)

Workshop steps. [Restore a backup](#restore-a-backup) and
[prepare a spare ESP32](#prepare-a-spare-esp32) also apply in the field.

## 1. Enclosures

Print from [MrMil/electronics-enclosure](https://github.com/MrMil/electronics-enclosure):
one `100W-masterbox` (controller) and three `100W-rj45` (statue boxes). Each enclosure's
`BOM.md` lists hardware and print notes. PETG or ASA, not PLA.

## 2. Boards

Follow [wiring.md](wiring.md) and the diagrams there.

**Controller box (two perfboards):**

- ESP32 board: female headers for the ESP32 (so it can be swapped), the 74AHCT125 in a
  socket, and two 100 Ω resistors on its outputs.
- Transmitter board: six MAX485 modules.

**Each statue box (one perfboard):** two MAX485 receivers, two pairs of 560 Ω bias
resistors, and two 100 Ω resistors.

Check each module's chip marking reads MAX485 (not 483/487/488/489). Build one extra
receiver board for the spares bag. The 74AHCT125 and the 100 Ω resistors are optional,
depending on perfboard space; without the 74AHCT125, wire GPIO 13/14 straight to the exit
DATA pins.

## 3. Power wiring (every box)

Per [box-power.svg](img/box-power.svg): mains inlet to the PSU, PSU to the two WAGO
connectors and the LED exits, and a separate thin pair to the perfboard. Ferrules on every
stranded wire.

## 4. Data cables

- Inside each box, cut a short patch cable for the pigtail. Plug it into the coupler and land
  its wires on the screw terminals using ferrules.
- With a meter, check every pin end to end, **through both couplers and the long cable**:
  pin N at the controller must reach pin N at the statue, and no pin may touch another.
  This also catches couplers that are crossover rather than straight-through.
- Label both ends of each long cable with its number (1, 2, 3).

## 5. Flash WLED

The installation's own effects will need a custom WLED build. Until it exists, flash the
standard release as below.

1. [install.wled.me](https://install.wled.me) from Chrome or Edge, USB to the ESP32, latest
   16.x release (16.0.1 or later).
2. Join **WLED-AP** (password `wled1234`), open `http://4.3.2.1`.

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

Eight outputs, **in this order**. The order makes all four statues one continuous strip
running 0 → 1 → 2 → 3.

| # | GPIO | Channel | LED count |
|---|---|---|---|
| 1 | 13 | S0-A | *TBD* |
| 2 | 14 | S0-B | *TBD* |
| 3 | 16 | S1-A | *TBD* |
| 4 | 17 | S1-B | *TBD* |
| 5 | 18 | S2-A | *TBD* |
| 6 | 19 | S2-B | *TBD* |
| 7 | 23 | S3-A | *TBD* |
| 8 | 25 | S3-B | *TBD* |

- Type WS281x, colour order **GRB** (check: preset 1 must show statue 0 *red*).
- LED count = strip 1 + strip 2 of that channel (they are chained).
- **Brightness limiter:** on, **3000 mA per output**. Each JST exit is rated 3 A. WLED limits
  the total for the output, not each strip, so 3000 mA is the value that guarantees neither
  strip's exit can go over 3 A.
- **Defaults → apply preset at boot:** the show playlist (once it exists).

### Presets

| Preset | Content |
|---|---|
| 1 · Test colours | 4 segments, one per statue: 0 red, 1 green, 2 blue, 3 white, solid |
| 2 · Test order | A single dot running along the whole strip |
| 10–99 | Workshop looks |
| the show | A playlist of the workshop looks, set as the boot preset |

## 7. Bench test

All four boxes, the three 10 m cables, test strips on every data exit. Presets 1 and 2, then
the show for an hour. With a scope: RO on one receiver at the end of a 10 m cable should
show clean 350/700 ns pulses with no ringing.

## 8. Back up

**Config → Security & Updates → Backup presets** and **Backup configuration**. Save them in
this repository under `wled/` as `presets.json` and `cfg.json`.

**Before committing `cfg.json`**, open it and blank out the AP password if it's in there.
This repository may be public.

## Restore a backup

Restores outputs, show and WiFi onto a mis-configured or replaced controller. Needs
`wled/cfg.json` and `wled/presets.json` already downloaded to the phone.

1. Join the controller's WiFi (or **WLED-AP** / `wled1234` on a freshly flashed ESP32) and
   open `http://4.3.2.1`.
2. **Config → Security & Updates → Restore configuration**: choose `cfg.json`. The
   controller restarts.
3. Re-join its WiFi (its name may have changed to the installation's), and set the AP
   password again under **WiFi Setup** if the backup had it blanked.
4. **Config → Security & Updates → Restore presets**: choose `presets.json`.
5. Run preset 1 to check.

## Prepare a spare ESP32

Flash it (step 5), restore both backups onto it, set the AP password, and label it
"SPARE, show loaded, <date>". Re-do it whenever the show changes.
