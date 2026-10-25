# Trenches

Path: [docs](../README.md) › [strips_and_power](README.md) › **trenches**
Parent: [README.md](README.md)
**Code:** `guide/img/statue-power.svg`, `guide/setup.md`
**Covers:** every trench and what runs in it, per statue and between the statues.

## What it does

Per statue, one trench along each arm of the V: T1 – T2 – T3 – T4 (apex) – T5 – T6 – T7.

| Segment | 230 V | 5 V (3 × 2.5, XT60) | Data (DATA + GND) |
|---|---|---|---|
| T4 → T3 | 2 cords: to the boxes in T3, T2 | — | apex → T3 box: T3 · apex → T2 box: T2, T1 |
| T3 → T2 | 1 cord: to the T2 box | — | apex → T2 box: T2, T1 |
| T2 → T1 | — | T2 box → T1 | T2 box → T1 (buffered, 22 AWG pair) |
| T4 → T5 | 2 cords: to the boxes in T5, T6 | — | apex → T5 box: T5 · apex → T6 box: T6, T7 |
| T5 → T6 | 1 cord: to the T6 box | — | apex → T6 box: T6, T7 |
| T6 → T7 | — | T6 box → T7 | T6 box → T7 (buffered, 22 AWG pair) |

The two arms are mirror images.

Between the statues: apex of statue 1 → apex of statue 2, 3 × CAT5e, 17.4 m apart in the
final layout ([statue_geometry/final_layout.md](statue_geometry/final_layout.md)); the 10 m cables do not reach,
see [../data_link/cabling.md](../data_link/cabling.md). Mains reaches
each apex from the camp's supply, ~20 m away, in its own trench (owner).

## Decisions

- **Mains arrives at each statue's apex through a trench the owner digs from the camp supply,
  ~20 m away** (owner, 2026-10-10). The apex power strip is the start of the statue's power
  distribution. Generator budget 1.5 kW; the installation's worst case is ~0.7 kW from
  the wall ([led_power_budget.md](led_power_budget.md)).
- **Trenches only along the arms and between the apexes** (agent, 2026-10-10). Every cable
  follows the V. The box sits at the apex, so data cables fan out along the arms with the
  power.
- **Trenches never cross each other, so nothing is cabled across the inside of the V** (owner,
  2026-10-22). The trench between the apexes leaves each apex through the inside of its V, and
  cutting a second trench across a first one puts a pickaxe into a buried 230 V line. So a 5 V
  run from a supply reaches only towers next to it along the arm trench, and a supply can never
  be shared by towers on the two arms: the fewest supplies is counted over runs of neighbours
  in trench order, not over free pairings (`tools/statue_render.html`,
  [statue_geometry/handoff.md](statue_geometry/handoff.md)). Running such a cable the long way round through the
  apex would cross nothing, but 7 m of 5 V at 9 A is not an option either.
- **Nothing above ground** (owner, 2026-10-09; police safety check). Cables surface inside
  the tower bases.

## Gotchas

- Segment lengths, centre to centre, from the final layout (`layout/statue-layout.json`,
  2026-10-23; statue 2 mirrors statue 1): T4→T3 1300, T3→T2 1700, T2→T1 1200, T4→T5 2200,
  T5→T6 1500, T6→T7 1000 mm. The arms are not symmetric. Cable runs along an arm add up:
  apex → A (T2) 3.0 m, apex → B (T3) 1.3 m, apex → D (T5) 2.2 m, apex → E (T6) 3.7 m, plus
  slack into each base. The 5 V runs are T2 → T1 1.2 m and T6 → T7 1.0 m.
  **Changed 2026-10-23:** previously from the 2026-10-21 layout (T4→T3 2200, T3→T2 1590,
  T2→T1 1120, T4→T5 1340, T5→T6 1760, T6→T7 1102 mm); changed because the artist sent the final
  layout.

## Related

- [power_distribution.md](power_distribution.md) — the supply grouping these runs implement.
- [tower_base.md](tower_base.md) — why neighbour data comes back from the power box.
- [../data_link/cabling.md](../data_link/cabling.md) — the CAT5e between the statues.
