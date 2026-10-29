# Setup and teardown

[← README](../README.md) · [Wiring](wiring.md) · [Troubleshooting](troubleshooting.md)

## Layout

Two statues, each a V of 7 towers. Towers are numbered **T1–T7 from one tip of the V to the
other**; T4 is the apex.

| Tower | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
|---|---|---|---|---|---|---|---|
| Height (mm) | 1100 | 1400 | 1700 | 2000 | 1700 | 1400 | 1100 |

- **Statue 1** has the **controller box** (ESP32) in its base.
- **Statue 2** has **box 2** (receivers only) in its base.
- Effects run statue 1 T1 → T7, then statue 2 T1 → T7. Tower numbering must match the
  physical order.

Where each tower stands, in mm from the centre of the circle, is in
[`layout/statue-layout.json`](../layout/statue-layout.json) (open it in the
[layout tool](https://mrmil.github.io/led-over-rj245/) for a top-down plan with a 1 m grid).
**Every tower faces the same way as its statue's apex tower (T4):** one corner points straight
along the line between the two apexes, towards the other statue.

![System overview](img/overview.svg)

## Connections

| From | To | Cable |
|---|---|---|
| Controller jack 1 | Box 2 jack 1 | 20 m CAT5 (apexes are 17.4 m apart) |
| Controller jack 2 | Box 2 jack 2 | 20 m CAT5 |
| Controller jack 3 | Box 2 jack 3 | 20 m CAT5 |
| Apex box, tower data outputs | Power boxes in T2 (data for T1, T2), T3, T5, T6 (data for T6, T7); T4's stays inside the apex box | DATA + GND, 3-pin LED connector |
| Apex power strip | Strips in T3 and T5, from those on to T2 and T6 | Extension cords, one strip at the end of each |
| Strip in each tower | The box in that tower | Kettle lead |
| Each power box, 4 × LED connector out | Its own tower's 4 strands | 3-pin LED connector |
| Each power box, top-feed XT60 | Up its own tower's post → 4 × XT60 to the strand tops | 3 × 2.5 |
| Two-tower boxes (T2, T6): XT60 + data out | Tip towers T1 (from T2), T7 (from T6): the tip-tower cable, 4 LED connectors at its end | 3 × 2.5 + 22 AWG pair |

**The ports on the boxes are not Ethernet.** The cables are ordinary network cables; never
plug one into network equipment. It will fry the electronics in the boxes and this is
unfixable (PoE puts 48 V on the pairs).

## Power

Five power boxes per statue. Each apex gets a strip, fed from an outlet by its own extension
cord, or, if only one outlet is in reach, from the other apex's strip by the apex-to-apex
cord. From the apex strip, mains runs on extension cords chained tower to tower, a strip at
each box ([statue-power.svg](img/statue-power.svg)):

| Power box in | Box | Also feeds |
|---|---|---|
| T2 | two-tower box | T1 |
| T3 | one-tower box | — |
| T4 | inside the apex box | — |
| T5 | one-tower box | — |
| T6 | two-tower box | T7 |

T1 and T7 have no box and nothing to wire: the tip-tower cable from the power box next door
ends in their 4 strands' LED connectors ([tip-tower-cable.svg](img/tip-tower-cable.svg)).

## Trenches

| Segment | Contents |
|---|---|
| T4 → T3 | extension cord apex → T3; data to the power boxes in T3 and T2 |
| T3 → T2 | extension cord T3 → T2; data to the power box in T2 |
| T2 → T1 | 5 V and data, power box in T2 → T1 |
| T4 → T5 | extension cord apex → T5; data to the power boxes in T5 and T6 |
| T5 → T6 | extension cord T5 → T6; data to the power box in T6 |
| T6 → T7 | 5 V and data, power box in T6 → T7 |
| Apex 1 → apex 2 | 3 × CAT5, and the extension cord to statue 2 if statue 2 has no outlet of its own |

## Order

1. Place each box in its statue's base.
2. Lay the 3 CAT5 cables and the extension cords on the surface and connect everything. Power
   up and start the show. Every tower of both statues must light, all 4 faces. Then run the
   tower checks ([operating.md](operating.md#check-a-tower)) to confirm each jack drives the
   right tower. Fix anything wrong now.
3. Dig the trenches (20–30 cm) and bury the runs per the table. **Trenches never cross each
   other** (a pickaxe into a buried 230 V cord), and no cable leaves the table's trenches.
   **No cable above ground**: cables surface inside the bases. Coil spare length inside the base.
4. Reconnect, power up, check every tower lights again.
5. Slide the lids shut and zip-tie each lid's lock lug.
6. Switch the controller off and on. The show must start by itself within about 10 s.

## Teardown

1. Switch off and unplug all mains.
2. Disconnect the tower cables and the CAT5 cables at both ends.
3. Dig out all buried cables: per statue 4 extension cords, 2 tip-tower cables, and the
   data cables; plus the 3 CAT5 and, if used, the extension cord between the statues.
