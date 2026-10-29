# Inventory

[← README](../README.md) · [Parts](parts.md) · [Setup](setup.md)

Everything that goes to the site, counted. [Parts](parts.md) is the shopping list by part;
this page is by thing.

## Boxes

| Box | Qty | Where | What is inside |
|---|---|---|---|
| Master box | 1 | Apex of statue 1 | ESP32 + WLED, 7 MAX485 transmitters, 3 RJ45 jacks, the power box for T4 |
| Slave box | 1 | Apex of statue 2 | 7 MAX485 receivers, 3 RJ45 jacks, the power box for T4 |
| 1 tower power box | 4 | T3 and T5 of each statue | PSU, 1 × 74AHCT125, 4 LED connectors out, top-feed XT60 out, data in |
| 2 tower power box | 4 | T2 and T6 of each statue | As the 1 tower power box, plus a second 74AHCT125, an XT60 out and a data out for the tip tower |

10 boxes, each with its own PSU and a kettle-lead socket with a switch.

## LED strips

56 face strips, each one piece, 4 per tower, labelled at the bottom end with their LED
count. Every strip has a 3-pin LED connector at the bottom. 75, 93 and 111 strips also have
a male XT60 at the top for the top feed; 57 strips do not.

| LEDs | Length | Towers | Pieces |
|---|---|---|---|
| 111 | 1.85 m | T4 | 8 |
| 93 | 1.55 m | T3, T5 | 16 |
| 75 | 1.25 m | T2, T6 | 16 |
| 57 | 0.95 m | T1, T7 | 16 |

## Cables

Buried cables are made about 1 m longer than the run, so nobody has to stretch them in the
trench; the extra is coiled inside a base.

### Mains

Mains goes tower to tower on bought extension cords, each ending in a power strip. Every box
plugs into the strip in its own tower with a kettle lead. All bought; lengths are the
minimum, buy the next size up.

Where the outlets are decides how the statues are fed, so the cables for both ways are
packed: either each apex gets its own cord from an outlet, or one apex is fed and a cord
runs on from it to the other apex through the trench between them.

| Cable | Qty | Length | Run |
|---|---|---|---|
| Extension cord, outlet → apex | 2 | ≥ 25 m | ~20 m, own trench; one per statue, or one for statue 1 only |
| Extension cord, apex 1 → apex 2 | 1 | ≥ 20 m | 17.4 m, the CAT5 trench; only if statue 2 has no outlet of its own |
| Extension cord, apex → T3 | 2 | ≥ 2.5 m | 1.3 m |
| Extension cord, T3 → T2 | 2 | ≥ 3 m | 1.7 m |
| Extension cord, apex → T5 | 2 | ≥ 3.5 m | 2.2 m |
| Extension cord, T5 → T6 | 2 | ≥ 2.5 m | 1.5 m |
| Power strip | 10 | — | at the end of every extension cord: both apexes and T2, T3, T5, T6 of each statue |
| Kettle lead | 10 | — | one per box, into the strip in its own tower |

### Bespoke: top-feed cables

3 × 2.5, male XT60 at the bottom, 4 female XT60 at the top
([wiring.md](wiring.md#power)). 10 in all, one per tower T2–T6, the tower's height plus
30 cm.

| Qty | Length | Towers |
|---|---|---|
| 4 | 1.7 m | T2, T6 (1.4 m towers) |
| 4 | 2.0 m | T3, T5 (1.7 m towers) |
| 2 | 2.3 m | T4 (2 m towers) |

### Bespoke: data cables

DATA + GND, 3-pin LED connector at both ends, master/slave box → power box, buried. 12 in all. A
2 tower power box gets two: its own tower's and the tip tower's.

| Qty | Length | Run |
|---|---|---|
| 4 | 4 m | apex → 2 tower power box in T2 (3.0 m), lines T2 and T1 |
| 2 | 2.5 m | apex → 1 tower power box in T3 (1.3 m) |
| 2 | 3.5 m | apex → 1 tower power box in T5 (2.2 m) |
| 4 | 5 m | apex → 2 tower power box in T6 (3.7 m), lines T6 and T7 |

### Bespoke: tip-tower cables (T1, T7)

3 × 2.5 + a thin data pair taped together, male XT60 and the bare pair at the box end, 4
3-pin LED connectors at the tower end ([tip-tower-cable.svg](img/tip-tower-cable.svg)),
buried. 4 in all.

| Qty | Length | Run |
|---|---|---|
| 2 | 2.5 m | 2 tower power box in T2 → T1 (1.2 m) |
| 2 | 2 m | 2 tower power box in T6 → T7 (1.0 m) |

### RJ45

| Cable | Qty | Length | Run |
|---|---|---|---|
| CAT5, moulded plugs, one distinctive colour | 3 + 2 spare | 20 m | master box → slave box, jacks 1–3 (apexes 17.4 m apart) |

The ports on the boxes are not Ethernet. Never plug these cables into network equipment: it
will fry the electronics in the boxes and this is unfixable.

## Spares

| Spare | Qty |
|---|---|
| ESP32, flashed with the show | 1 |
| MAX485 module (chip must read MAX485) | 2 |
| 74AHCT125 level shifter (AHCT, DIP) | 2 |
| CAT5 20 m | 2 |

**There are no spare LED strips and no spare bespoke cables, and nothing is repaired on
site.** A dead strip or a damaged cable: call the owner, who makes a new one and sends it.
