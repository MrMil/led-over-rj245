# Setup and teardown

[← README](../README.md) · [Wiring](wiring.md) · [Troubleshooting](troubleshooting.md)

## Layout

Two statues, each a V of 7 towers. Towers are numbered **T1–T7 from one tip of the V to the
other**; T4 is the apex.

| Tower | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
|---|---|---|---|---|---|---|---|
| Height (mm) | 800 | 1150 | 1550 | 2000 | 1150 | 800 | 500 |

- **Statue 1** has the **controller box** (ESP32) in its base.
- **Statue 2** has **box 2** (receivers only) in its base.
- Effects run statue 1 T1 → T7, then statue 2 T1 → T7. Tower numbering must match the
  physical order.

![System overview](img/overview.svg)

## Connections

| From | To | Cable |
|---|---|---|
| Controller jack 1 | Box 2 jack 1 | 10 m CAT5e |
| Controller jack 2 | Box 2 jack 2 | 10 m CAT5e |
| Controller jack 3 | Box 2 jack 3 | 10 m CAT5e |
| Apex box, tower data outputs T1–T7 | Tower base T1–T7, data in | DATA + GND |
| Apex power strip | Supply boxes A–E (C14) | C13 cords |
| Supply boxes | Towers, per the power table below | 5 V, XT60 |

**The CAT5e cables are not Ethernet.** Never connect them to network equipment. PoE puts
48 V on the pairs and destroys the transceivers at both ends.

## Power

Five supply boxes per statue, mains from the outlet and strip at the apex
([statue-power.svg](img/statue-power.svg)):

| Supply | Sits at | Feeds |
|---|---|---|
| A | T2 base | T1, T2 |
| B | T3 base | T3 |
| C | apex box | T4 faces 1–2 |
| D | apex | T4 faces 3–4, T5 faces 1–2 |
| E | T6 base | T5 faces 3–4, T6, T7 |

T4 and T5 each take two supplies: keep each supply's +5 V on its own two faces. All supply
GNDs are tied together by the ground bond.

## Trenches

| Segment | Contents |
|---|---|
| T4 → T3 | 230 V to B and to A · data T3, T2, T1 · ground bond |
| T3 → T2 | 230 V to A · data T2, T1 · ground bond |
| T2 → T1 | 5 V A → T1 · data T1 |
| T4 → T5 | 230 V to E · 5 V D → T5 · data T5, T6, T7 · ground bond |
| T5 → T6 | 230 V to E · 5 V E → T5 · data T6, T7 · ground bond |
| T6 → T7 | 5 V E → T7 · data T7 |
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
3. Dig out all buried cables: per statue 3 mains cords, 4 × 5 V, 7 data, 2 ground bonds;
   plus the 3 CAT5e between the statues.
