# Trenches

Path: [docs](../README.md) › [strips_and_power](README.md) › **trenches**
Parent: [README.md](README.md)
**Code:** `guide/img/statue-power.svg`, `guide/setup.md`
**Covers:** every trench and what runs in it, per statue and between the statues.

## What it does

Per statue, one trench along each arm of the V: T1 – T2 – T3 – T4 (apex) – T5 – T6 – T7.

| Segment | 230 V | 5 V (3 × 2.5, XT60) | Data (DATA + GND) |
|---|---|---|---|
| T4 → T3 | 2 cords: to B, to A | — | apex → B: T3 · apex → A: T2, T1 |
| T3 → T2 | 1 cord: to A | — | apex → A: T2, T1 |
| T2 → T1 | — | A → T1 | A → T1 (buffered, 22 AWG pair) |
| T4 → T5 | 2 cords: to D, to E | — | apex → D: T5 · apex → E: T6, T7 |
| T5 → T6 | 1 cord: to E | — | apex → E: T6, T7 |
| T6 → T7 | — | E → T7 | E → T7 (buffered, 22 AWG pair) |

The two arms are mirror images.

Between the statues: apex of statue 1 → apex of statue 2, 3 × CAT5e (10 m). Mains reaches
each apex from the camp's supply, ~20 m away, in its own trench (owner).

## Decisions

- **Mains arrives at each statue's apex through a trench the owner digs from the camp supply,
  ~20 m away** (owner, 2026-10-10). The apex power strip is the start of the statue's power
  distribution. Generator budget 1.5 kW; the installation's worst case is ~0.6 kW from
  the wall ([led_power_budget.md](led_power_budget.md)).
- **Trenches only along the arms and between the apexes** (agent, 2026-10-10). Every cable
  follows the V. The box sits at the apex, so data cables fan out along the arms with the
  power.
- **Nothing above ground** (owner, 2026-10-09; police safety check). Cables surface inside
  the tower bases.

## Gotchas

- Segment lengths depend on tower spacing along each arm (not yet known); cable lengths
  follow from it.

## Related

- [power_distribution.md](power_distribution.md) — the supply grouping these runs implement.
- [tower_base.md](tower_base.md) — why neighbour data comes back from the supply box.
- [../data_link/cabling.md](../data_link/cabling.md) — the CAT5e between the statues.
