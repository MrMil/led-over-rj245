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

![System overview](img/overview.svg)

## Connections

| From | To | Cable |
|---|---|---|
| Controller jack 1 | Box 2 jack 1 | 20 m CAT5e (apexes are 17.4 m apart) |
| Controller jack 2 | Box 2 jack 2 | 20 m CAT5e |
| Controller jack 3 | Box 2 jack 3 | 20 m CAT5e |
| Apex box, tower data outputs | Supply boxes A (T1, T2), B (T3), D (T5), E (T6, T7); T4 stays inside the apex box | DATA + GND, JST-SM |
| Apex power strip | Supply boxes A, B, D, E (C14) | C13 cords |
| Each supply box, 4 × JST-SM out | Its own tower's 4 strands | JST-SM |
| Box A, E: XT60 + data out | Tip towers T1 (A), T7 (E) | 3 × 2.5 + 22 AWG pair |

**The CAT5e cables are not Ethernet.** Never connect them to network equipment. PoE puts
48 V on the pairs and destroys the transceivers at both ends.

## Power

Five supply boxes per statue, mains from the strip at the apex
([statue-power.svg](img/statue-power.svg)):

| Supply | Sits at | Own tower | Also feeds |
|---|---|---|---|
| A | T2 base | T2 | T1 |
| B | T3 base | T3 | — |
| C | apex box | T4 | — |
| D | T5 base | T5 | — |
| E | T6 base | T6 | T7 |

T1 and T7 have no box: their base only splits the incoming power and data to the 4
strands ([neighbour-base.svg](img/neighbour-base.svg)).

## Trenches

| Segment | Contents |
|---|---|
| T4 → T3 | 230 V to B and to A · data to B (T3) and to A (T2, T1) |
| T3 → T2 | 230 V to A · data to A (T2, T1) |
| T2 → T1 | 5 V A → T1 · data A → T1 |
| T4 → T5 | 230 V to D and to E · data to D (T5) and to E (T6, T7) |
| T5 → T6 | 230 V to E · data to E (T6, T7) |
| T6 → T7 | 5 V E → T7 · data E → T7 |
| Apex 1 → apex 2 | 3 × CAT5e |

## Order

1. Place each box in its statue's base.
2. Lay the 3 CAT5e cables and the mains cords on the surface and connect everything. Power
   up and run test presets 1 and 2 ([operating.md](operating.md#test-presets)). Fix anything
   wrong now.
3. Dig the trenches (20–30 cm) and bury the runs per the table. **No cable above ground**:
   cables surface inside the bases. Coil spare length inside the base.
4. Reconnect, power up, run presets 1 and 2 again.
5. Slide the lids shut and zip-tie each lid's lock lug.
6. Switch the controller off and on. The show must start by itself within about 10 s.

## Teardown

1. Switch off and unplug all mains.
2. Disconnect the tower cables and the CAT5e cables at both ends.
3. Dig out all buried cables: per statue 4 mains cords, 2 × 5 V, and the data cables; plus
   the 3 CAT5e between the statues.
