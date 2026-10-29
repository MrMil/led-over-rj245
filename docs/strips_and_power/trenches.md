# Trenches

Path: [docs](../README.md) › [strips_and_power](README.md) › **trenches**
Parent: [README.md](README.md)
**Code:** `guide/img/statue-power.svg`, `guide/setup.md`
**Covers:** every trench and what runs in it, per statue and between the statues.

## What it does

Per statue, one trench along each arm of the V: T1 – T2 – T3 – T4 (apex) – T5 – T6 – T7.

| Segment | 230 V (extension cord, strip at its end) | 5 V (tip-tower cable, 3 × 2.5) | Data (DATA + GND) |
|---|---|---|---|
| T4 → T3 | apex strip → T3 strip | — | apex → T3 box: T3 · apex → T2 box: T2, T1 |
| T3 → T2 | T3 strip → T2 strip | — | apex → T2 box: T2, T1 |
| T2 → T1 | — | T2 box → T1 (tip-tower cable) | in the same tip-tower cable (buffered, 22 AWG pair) |
| T4 → T5 | apex strip → T5 strip | — | apex → T5 box: T5 · apex → T6 box: T6, T7 |
| T5 → T6 | T5 strip → T6 strip | — | apex → T6 box: T6, T7 |
| T6 → T7 | — | T6 box → T7 (tip-tower cable) | in the same tip-tower cable (buffered, 22 AWG pair) |

The two arms are mirror images.

Between the statues: apex of statue 1 → apex of statue 2, 3 × CAT5e, 17.4 m apart in the
final layout ([statue_geometry/final_layout.md](statue_geometry/final_layout.md)); the 10 m cables do not reach,
see [../data_link/cabling.md](../data_link/cabling.md), and, when statue 2 has no outlet of
its own, the mains extension cord from apex 1 to apex 2. Each apex with an outlet in reach
gets its own trench from the outlet, ~20 m (owner).

## Decisions

- **Mains arrives at an apex through a trench the owner digs from an outlet, ~20 m away; an
  apex with no outlet in reach is fed from the other apex on an extension cord in the
  apex-to-apex trench** (owner, 2026-10-10 and 2026-10-29: "extention chords going from
  statue to statue", "they should have the cables for both options based on where there are
  outlets"). The statues stand in the deep playa; there is no camp supply, only outlets
  whose places are not known in advance (owner, 2026-10-29). The apex power strip is the
  start of the statue's power distribution; from it the cords chain tower to tower
  ([power_distribution.md](power_distribution.md)). Generator budget 1.5 kW; the installation's worst case is ~0.7 kW from
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

- **Buried cable lengths in `guide/inventory.md` are the centre-to-centre run plus 1 m,
  rounded up to the half metre; top-feed cables are the tower height plus 0.3 m** (owner,
  2026-10-29). The buried ones get the full metre because they go into the ground and the
  crew must not have to stretch them in the trench; the slack is coiled inside a base
  (`guide/setup.md`: nothing above ground). The top feed runs up a post in the open, so 30 cm
  is enough ("the 1.7 m tower doesn't need 2.5 m of top feed cable"). Extension cords are
  bought, so the inventory gives the run plus 1 m as a minimum and the next size sold is
  taken; the outlet → apex 1 cord is the ~20 m run plus 5 m (agent). **Changed 2026-10-29:** the agent's first
  figures gave the top feed 0.5 m rounded up to the half metre (2.5 m for a 1.7 m tower); the
  owner cut it.

- Segment lengths, centre to centre, from the final layout (`layout/statue-layout.json`,
  2026-10-23; statue 2 mirrors statue 1; drawn to scale in `guide/img/site-map.svg`, the README's site map, which
  gives the corner-to-corner legs the crew measures): T4→T3 1300, T3→T2 1700, T2→T1 1200, T4→T5 2200,
  T5→T6 1500, T6→T7 1000 mm. The arms are not symmetric. Cable runs along an arm add up:
  apex → A (T2) 3.0 m, apex → B (T3) 1.3 m, apex → D (T5) 2.2 m, apex → E (T6) 3.7 m, plus
  slack into each base. The 5 V runs are T2 → T1 1.2 m and T6 → T7 1.0 m.
  **Changed 2026-10-23:** previously from the 2026-10-21 layout (T4→T3 2200, T3→T2 1590,
  T2→T1 1120, T4→T5 1340, T5→T6 1760, T6→T7 1102 mm); changed because the artist sent the final
  layout.

## Related

- [power_distribution.md](power_distribution.md) — the supply grouping these runs implement.
- [tower_base.md](tower_base.md) — why the tip tower's data comes back from the power box.
- [../data_link/cabling.md](../data_link/cabling.md) — the CAT5e between the statues.
