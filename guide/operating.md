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
| 1 · Test colours | Statue 0 red, 1 green, 2 blue, 3 white; all strips lit | Wrong colour on a statue: its cable is in the wrong controller jack |
| 2 · Test order | One dot running 0 → 1 → 2 → 3 → 0 | Dot jumps backwards: statues numbered in the wrong order |

## Presets

| Numbers | Content |
|---|---|
| 1–9 | Tests. Don't change. |
| 10–99 | Workshop looks |
| 100+ | Field looks |

- The show is a playlist, set as the boot preset. It starts by itself on every power-up.
- After changing presets: **Config → Security & Updates → Backup presets**, and send the file
  to the crew chat.

## Do not touch

- **Config → LED Preferences**: outputs, LED counts, colour order, and the 3000 mA per-output
  current limit that keeps each LED exit under its 3 A rating.
- **Config → WiFi Setup**: a wrong setting here takes the access point down.

To undo changes to either: [build.md → Restore a backup](build.md#restore-a-backup).
