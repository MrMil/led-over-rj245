# Operating

[← README](../README.md) · [Troubleshooting](troubleshooting.md)

The controller runs [WLED](https://kno.wled.ge) 16.

## Connect

- WiFi name and password: from the installation lead. They are not on the hardware or in this
  repository.
- `http://4.3.2.1` in a browser, or the WLED app.
- At most about 4 phones can be connected at once (ESP32 access-point limit).

## Test presets

| Preset | Expected | If not |
|---|---|---|
| 1 · Test colours | Each tower one colour: T1 red, T2 orange, T3 yellow, T4 green, T5 cyan, T6 blue, T7 magenta; same in both statues, all 4 faces lit | Two towers swapped: their data cables are swapped. A face dark: see troubleshooting |
| 2 · Test order | A light runs up each tower in turn: statue 1 T1 → T7, then statue 2 T1 → T7 | Out of order: tower cables or CAT5e jacks swapped |

## Presets

| Numbers | Content |
|---|---|
| 1–9 | Tests. Don't change. |
| 10–99 | Workshop looks |
| 100+ | Field looks |

- The show is preset 18, a playlist of looks 10–17, set as the boot preset. It starts by itself on every power-up.
- After changing presets: **Config → Security & Updates → Backup presets**, and send the file
  to the crew chat.

## Do not touch

- **Config → LED Preferences**: the 14 outputs, LED counts, colour order and current
  settings. The current cap itself is fixed in the firmware and can't be raised from here.
- **Config → WiFi Setup**: a wrong setting here takes the access point down.

To undo changes to either: [build.md → Restore a backup](build.md#restore-a-backup).
