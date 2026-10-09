# Troubleshooting

[← README](../README.md) · [Wiring](wiring.md) · [Setup](setup.md)

Fastest isolation: swap the suspect part with its twin (statue boxes, data cables, channels of
one statue) and see whether the fault moves.

## Nothing lights

1. Controller PSU LED on? If not: [box is dead](#a-box-is-dead).
2. Controller WiFi visible? If not, power-cycle the controller.
3. In WLED: power on, brightness above zero.
4. Preset 1 lights everything → the show playlist was stopped; start it from Presets.

## One remote statue dark

1. Box powered (PSU LED on)?
2. Re-seat the data cable at both ends.
3. Swap its cable to another controller jack:
   - fault moves to the other statue → controller side (that jack or transmitter);
   - fault stays → cable or statue box. Test with a spare cable on the surface, then swap the
     receiver board.

## One remote statue flickers or shows random colours

Bad data connection to that statue.

- Re-seat the data cable at both ends.
- Check the screw terminals in both boxes: A/B wires and the ground pins (4, 5, 7, 8). Look
  for loose wires or stray strands.
- Test with a spare cable on the surface. If that fixes it, the buried cable is damaged.

## One channel dark, the other works

Channel A = exits 1–2, channel B = exits 3–4.

- Statues 1–3: that channel's receiver, its terminals, or its pair in the cable.
- Statue 0: the 74AHCT125 or its wiring.

## Dark from some point along a chain

Strip 2 gets its data after strip 1, so one dead LED darkens everything after it on that
channel, including all of strip 2. The fault is at or just before the first dark LED.

## Show doesn't start after a power cut

Boot preset changed. **Config → LED Preferences → Defaults → apply preset at boot** = the
show playlist, or [restore the backup](build.md#restore-a-backup).

## A box is dead

The PSU shuts down on overload or over-temperature.

1. Unplug, let it cool, plug back in.
2. Still dead: check the 1 A fuse in the C14 inlet's drawer. A blown inlet fuse means a fault
   between the inlet and the PSU. If a new fuse blows again, leave the box unplugged.

## Spares

Bag: 2 data cables, 1 receiver board (2 receivers + jack pigtail), 1 ESP32 loaded with the
show, 1 74AHCT125, 1 A fuses.

- **Receiver board:** photograph the wiring, move the wires across, check against
  [statue-wiring.svg](img/statue-wiring.svg).
- **ESP32:** lifts out of its socket. Seat the spare the same way round (USB connector in
  the same position). It already holds the show; if not, [restore](build.md#restore-a-backup).
