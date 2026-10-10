# Troubleshooting

[← README](../README.md) · [Wiring](wiring.md) · [Setup](setup.md)

Fastest isolation: swap the suspect part with its twin (towers of the same height, tower
cables, CAT5e cables, the two jacks' channels) and see whether the fault moves.

## Nothing lights

1. Controller PSU LED on? If not: [box is dead](#a-box-is-dead).
2. Controller WiFi visible? If not, power-cycle the controller.
3. In WLED: power on, brightness above zero.
4. Preset 1 lights everything → the show playlist was stopped; start it from Presets.

## All of statue 2 dark, statue 1 fine

1. Box 2 powered (PSU LED on)?
2. Re-seat the 3 CAT5e cables at both ends.

## Statue 2 flickers or shows random colours

Bad data connection between the boxes.

- Re-seat the CAT5e cables at both ends.
- Check the screw terminals in both boxes: A/B wires and the ground pins (7, 8). Look for
  loose wires or stray strands.
- Test with a spare cable on the surface. If that fixes it, the buried cable is damaged.

## Three statue-2 towers dark together

They share one CAT5e cable: T1–T3 = jack 1, T4–T6 = jack 2, T7 = jack 3. Re-seat or replace
that cable.

## One tower dark

1. Tower power connected?
2. Re-seat its data cable at both ends.
3. Swap its data cable with another tower's at the box:
   - fault moves → box side (that output's buffer or receiver);
   - fault stays → cable or tower base (its 74AHCT125).

## One face of a tower dark, the others fine

That face's strip, its connection to the tower-base 74AHCT125, or that gate of the chip.

## A face dark from some point upwards

One dead LED darkens everything above it on that face. The fault is at or just below the
first dark LED.

## Show doesn't start after a power cut

Boot preset changed. **Config → LED Preferences → Defaults → apply preset at boot** = the
show playlist, or [restore the backup](build.md#restore-a-backup).

## Some towers dark, matching one supply

A = T1 + T2 · B = T3 · C = T4 faces 1–2 · D = T4 faces 3–4 + T5 faces 1–2 · E = T5 faces 3–4
+ T6 + T7. Check that supply's mains cord at the apex strip, then see below.

## A box is dead

The PSU shuts down on overload or over-temperature.

1. Unplug, let it cool, plug back in.
2. Still dead: check the 1 A fuse in the C14 inlet's drawer. A blown inlet fuse means a fault
   between the inlet and the PSU. If a new fuse blows again, leave the box unplugged.

## Spares

Bag: 2 CAT5e cables, 1 receiver module, 1 tower-base board, 1 ESP32 loaded with the show,
2 × 74AHCT125, 1 A fuses.

- **Tower-base board / receiver:** photograph the wiring, move the wires across, check
  against [tower-base.svg](img/tower-base.svg) / [box2-wiring.svg](img/box2-wiring.svg).
- **ESP32:** lifts out of its socket. Seat the spare the same way round (USB connector in
  the same position). It already holds the show; if not, [restore](build.md#restore-a-backup).
