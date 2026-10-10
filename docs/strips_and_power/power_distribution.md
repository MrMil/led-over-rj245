# Power distribution

Path: [docs](../README.md) › [strips_and_power](README.md) › **power_distribution**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`SUPPLIES`, `power()`, `statue_power()`), `guide/img/statue-power.svg`, `guide/img/box-power.svg`, `guide/wiring.md` (Power)
**Covers:** mains from the apex outlet to five supplies per statue, and 5 V from each supply to its towers.

## What it does

Per statue, five S-100-5 supplies, each in its own box with a C14 inlet:

| Supply | Box | Sits at | Feeds |
|---|---|---|---|
| A | `100W` | T2 base | T1 + T2, all faces |
| B | `100W` | T3 base | T3, all faces |
| C | apex `100W-masterbox` | T4 (apex) | T4 faces 1–2, + the box's electronics |
| D | `100W` | T4 (apex) | T4 faces 3–4, T5 faces 1–2 |
| E | `100W` | T6 base | T5 faces 3–4, T6 + T7 all faces |

Mains: an outlet and power strip at the apex; a C13 cord to each supply box. 5 V: one cable
per destination tower (or tower half) from the supply to the tower base, split there to the
strand XT60s.

## Decisions

- **Five S-100-5 per statue** (owner, 2026-10-10). See
  [led_power_budget.md](led_power_budget.md).
- **Clean grouping: each tower whole or halved (faces 1–2 / 3–4), neighbours along the V
  share a supply** (owner wanted clean splits, 2026-10-10; grouping by agent). Worked out
  with 60 mA per LED, under which whole towers could not fit (T4 alone 26.6 A). With the
  datasheet's 36 mA every supply stays under its ceiling at full white
  ([led_power_budget.md](led_power_budget.md)); the grouping stands because it is already
  wired that way.
  **Rejected.** *Arbitrary strand-level splits* (slightly better balance, messier wiring).
  *6 supplies:* same towers split (T4, T5), only slightly less dimming at full white.
  *7 supplies:* no longer needed with datasheet currents.
- **Each supply sits by the towers it feeds** (agent, 2026-10-10). Mains is easy to carry far;
  5 V at several amps is not.
- **Each supply in its own box with a C14 inlet** (agent proposal, 2026-10-10). This reuses the
  enclosure repo's `100W` design (S-100-5 + C14), so no mains terminals are exposed in a tower
  base. C shares the apex `100W-masterbox` with the ESP32 or receivers. **Enclosure change
  pending:** XT60 outputs instead of JST-SM slots.
- **One 230 V cord per supply, from a power strip at the apex** (agent, 2026-10-10). Any supply
  can be unplugged on its own, and there are no mains joints in the field. Buried cords:
  H07RN-F 3 × 1.5 mm² with a C13 plug.
- **One 5 V cable per destination, split at the tower base** (owner, 2026-10-10: "each power
  supply has 2 output ports — in the end it all combines"). That replaces a cable per strand.
- **Buried 5 V runs use 3-core mains-type cable with XT60 at both ends** (owner, 2026-10-10).
  Brown +5 V, blue GND, green/yellow unused or joined to GND. 3 × 2.5 mm² (owner's choice,
  "כבל פנדל פלסטי 3*2.5"), well above the ≤ 7.5 A per run at datasheet currents. No extra labelling: an XT60 can't be
  mistaken for mains (owner). H07RN-F (rubber) is the tougher jacket; PVC survives a week.
  Inside boxes and bases: NYAF 2.5 mm², red +5 V, blue GND (owner's chosen wire; it has no
  black).
- **Two supplies feeding one tower keep their +V separate** (agent, 2026-10-10). T4 (C/D) and T5
  (D/E): each supply's +V goes only to its own two faces, so supplies never back-feed each
  other. GNDs may join.
- **All supply −V tied together** (agent, 2026-10-10): a 1.5 mm² ground bond in the trench
  (A–B–apex–E; D and E also meet at T5). The data cables' GND then sees one reference.
- **T4's strands get a second feed at the top, up the post** (agent, 2026-10-10), faces 1–2
  from C and 3–4 from D. Voltage-drop estimate in [led_power_budget.md](led_power_budget.md);
  drop it if the strip measurement shows ≥ 4.5 V at the far end.
- **Logic power only from supply C** (agent, 2026-10-09). The apex box perfboard gets its own
  pair from C's second terminals, so tower current never flows through perfboard copper.
- **C14 fuse 1 A on the AC side** (owner, 2026-10-09). ~240 W of input for a 100 W PSU. The
  PSU's own fuse and over-temperature trip act first.
- **Mains colours brown L, blue N, green/yellow PE** — IEC colours, which Israel uses.

## Gotchas

- Five supplies per statue switching on together make a large inrush; check the outlet's
  breaker, or switch on in stages. Inlet fuses that blow at power-up need to be time-delay (T).
- Never parallel two supplies' +V outputs.

## Related

- [trenches.md](trenches.md) — what runs in each trench segment.
- [led_power_budget.md](led_power_budget.md) — current per group and the limiter ceilings.
