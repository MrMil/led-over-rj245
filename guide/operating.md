# Operating

[← README](../README.md) · [Troubleshooting](troubleshooting.md)

The controller runs [WLED](https://kno.wled.ge) 16.

## Connect

- WiFi name: **Layers-WLED**. Password: from the installation lead. It is not on the hardware
  or in this repository.
- `http://4.3.2.1` in a browser, or the WLED app.
- At most about 4 phones can be connected at once (ESP32 access-point limit).

## Presets

| Numbers | Content |
|---|---|
| 10–99 | Workshop looks |
| 100+ | Field looks |

- The show is preset 18, a playlist of looks 10–17, set as the boot preset. It starts by itself on every power-up.
- After changing presets: **Config → Security & Updates → Backup presets**, and send the file
  to the crew chat.

## Check a tower

In the effect list, pick **Statue 1 tower 1 only** … **Statue 2 tower 7 only**. That tower alone
blinks red, green, blue, dark, one second each; everything else is off.

- The wrong tower blinks: that tower's data cable is in the wrong jack on the box.
- Nothing blinks: see [troubleshooting](troubleshooting.md).
- The colours come in another order than red, green, blue: the colour order in LED Preferences is wrong for that output.

Afterwards start the show again (preset 18).

## Do not touch

- **Config → LED Preferences**: the 14 outputs, LED counts, colour order and current
  settings.
- **Config → WiFi Setup**: a wrong setting here takes the access point down.

To undo changes to either: [build.md → Restore a backup](build.md#restore-a-backup).
