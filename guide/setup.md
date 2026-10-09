# Setup and teardown

[← README](../README.md) · [Wiring](wiring.md) · [Troubleshooting](troubleshooting.md)

## Statue numbering

Statue **0** has the controller box (`100W-masterbox`). Statues **1, 2, 3** have statue boxes
(`100W-rj45`), numbered **clockwise from statue 0, seen from above**. Effects travel
0 → 1 → 2 → 3, so the numbering must match the physical order.

![System overview](img/overview.svg)

## Connections

| From | To | Cable |
|---|---|---|
| Controller jack 1 | Statue 1 box jack | 10 m data cable |
| Controller jack 2 | Statue 2 box jack | 10 m data cable |
| Controller jack 3 | Statue 3 box jack | 10 m data cable |
| Each box, C14 inlet | Mains | C13 cord |
| Each box, LED exits 1–4 | That statue's strips | see below |

Controller jack 1 is the one nearest the LED exits.

LED exits (JST-SM 3-pin, back wall), numbered from the end nearest the mains inlet. Same in
all four boxes:

| Exit | Channel | Strip | Pins live |
|---|---|---|---|
| 1 | A | 1 | 5V, DATA, GND |
| 2 | A | 2 | 5V, GND |
| 3 | B | 1 | 5V, DATA, GND |
| 4 | B | 2 | 5V, GND |

**The data cables are not Ethernet.** Never connect them to network equipment. PoE puts 48 V
on the pairs and destroys the transceivers at both ends.

## Order

1. Place each box in its statue's base.
2. Lay the data cables and mains cords on the surface and connect everything per the tables
   above. Power up and run test presets 1 and 2
   ([operating.md](operating.md#test-presets)). Fix anything wrong now.
3. Trench each run (20–30 cm). Data cable and mains cord share the trench. **No cable above
   ground**: cables surface inside the bases. Coil any spare length inside the base.
4. Reconnect, power up, run presets 1 and 2 again.
5. Slide the lids shut and put a zip tie through each lid's lock lug.
6. Switch the controller off and on. The show must start by itself within about 10 s.

## Teardown

1. Switch off and unplug all mains.
2. Disconnect strips and data cables at both ends.
3. Dig out the 3 data cables and the mains cords.
