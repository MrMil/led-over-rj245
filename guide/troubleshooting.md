# Troubleshooting

[← README](../README.md) · [Wiring](wiring.md) · [Setup](setup.md)

**Call Ofer on the phone before opening any box. There is live 230 V inside; it is
dangerous. If Ofer doesn't pick up, don't open the box.**

Fastest isolation: swap the suspect part with its twin (towers of the same height, tower
cables, CAT5e cables, the two jacks' channels) and see whether the fault moves.

## Nothing lights

1. Controller PSU LED on? If not: [box is dead](#a-box-is-dead).
2. Controller WiFi visible? If not, power-cycle the controller.
3. In WLED: power on, brightness above zero.
4. Any single look from Presets lights everything → the show playlist was stopped; start preset 18.

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

They share one CAT5e cable: T1–T3 = jack 3, T4–T5 = jack 2, T6–T7 = jack 1. Re-seat or
replace that cable.

## One tower dark

1. Tower power connected?
2. Re-seat its data cable at both ends.
3. Swap its data cable with another tower's at the box:
   - fault moves → box side (that output's buffer or receiver);
   - fault stays → cable or the tower's power box (its 74AHCT125).

## Several statue-1 towers dark, and which ones changes

Dead gates in the controller's 74AHCT125s. Channels 1–4 are chip #1's gates 1–4, channels
5–7 are chip #2's gates 1–3. A chip with one dead gate heats up and loses the rest, so the
dead set grows and changes between power-ups. A tower where only the first few LEDs show
random colours is the same thing. Replace the chip ([below](#a-74ahct125-is-warm-or-hot)).

## A 74AHCT125 is warm or hot

A healthy one is cold, in any weather. Warm means a gate has failed short inside it, and the
heat is killing the others. Box off, pull it, [test it](#testing-a-74ahct125), fit a tested
spare the same way round. Bin the chip; a chip with one dead gate does not stay at one.

Mains cord out first (one hand on the C13 plug, the other on the far side of the box; never
touch the PSU). Then touch the GND pin of a data connector before you touch a chip, a socket
or a data connector. Static is what kills these gates.

## Testing a 74AHCT125

Chip out of its socket, meter on the diode setting. Red probe on pin 7 (GND, the corner pin
on the side away from the notch), black on each output pin: 3, 6, 8, 11. Good: a diode,
0.5–0.7 V. Dead: about 0.00 V. Then red on pin 14 (VCC, the corner pin by the notch), black on
each output: good reads open. The controller needs four good gates in chip #1 and gates 1–3
good in chip #2; a power box needs all four in its chip #1 and gate 1 in chip #2.

## One face of a tower dark, the others fine

That face's strip, its JST-SM, or that gate of the 74AHCT125 in its power box. On T1 or T7,
the face's JST-SM at the base's WAGO split.

## A face dark from some point upwards

One dead LED darkens everything above it on that face. The fault is at or just below the
first dark LED.

## Show doesn't start after a power cut

Boot preset changed. **Config → LED Preferences → Defaults → apply preset at boot** = the
show playlist, or [restore the backup](build.md#restore-a-backup).

## Some towers dark, matching one power box

Each power box feeds the tower it sits in; the one in T2 also feeds T1, the one in T6 also
T7. Check that box's mains cord at the apex strip, then see below. Only T1 (or T7) dark: its
XT60 run or data pair from the power box in T2 (T6).

## A box is dead

The PSU shuts down on overload or over-temperature.

1. Unplug, let it cool, plug back in.
2. Still dead: check the 1 A fuse in the C14 inlet's drawer. A blown inlet fuse means a fault
   between the inlet and the PSU. If a new fuse blows again, leave the box unplugged.

## Spares

Bag: 2 CAT5e cables, 1 receiver module, 1 ESP32 loaded with the show, 2 × 74AHCT125, 1 A
fuses, XT60 pairs, JST-SM pairs.

- **74AHCT125:** [test the spare](#testing-a-74ahct125) first, pull the old one from its
  socket and seat the spare the same way round. Cord out and discharge yourself on a data
  connector's GND pin before handling either; never touch the PSU.
- **Receiver:** photograph the wiring, move the wires across, check against
  [box2-wiring.svg](img/box2-wiring.svg).
- **ESP32:** lifts out of its socket. Seat the spare the same way round (USB connector in
  the same position). It already holds the show; if not, [restore](build.md#restore-a-backup).
