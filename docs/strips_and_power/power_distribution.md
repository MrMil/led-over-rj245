# Power distribution

Path: [docs](../README.md) › [strips_and_power](README.md) › **power_distribution**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`SUPPLIES`, `power_box()`, `neighbour_base()`, `statue_power()`), `guide/img/statue-power.svg`, `guide/img/power-box.svg`, `guide/img/neighbour-base.svg`, `guide/wiring.md` (Power)
**Covers:** mains from the apex to five supplies per statue, and 5 V from each supply to its towers.

## What it does

Per statue, five S-100-5 supplies, each in a box with a C14 inlet:

| Power box in | Box | Own tower | Neighbour fed | Worst case |
|---|---|---|---|---|
| T2 | `100W` | T2 (1400) | T1 (1100) | 15.5 A |
| T3 | `100W` | T3 (1700) | — | 10.9 A |
| T4 | apex `100W-masterbox` | T4 (2000) | — | 13.1 A |
| T5 | `100W` | T5 (1700) | — | 10.9 A |
| T6 | `100W` | T6 (1400) | T7 (1100) | 15.5 A |

Mains: an outlet and power strip at the apex, and a C13 cord to each of the power boxes in T2,
T3, T5 and T6 (T4's is in the apex box). Each box drives its own tower's 4 strands on 4 JST-SM.
The power boxes in T2 and T6 also feed the
tip tower next to them: power on an XT60 run (3 × 2.5 cable) with a buffered data pair
alongside. The tip tower's base splits both passively to its 4 strands
([tower_base.md](tower_base.md)).

## Decisions

- **Power boxes are named by the tower they sit in: "power box in T2" … "power box in T6"**
  (owner, 2026-10-25: "I don't remember what ABC etc means"). A name that says where the box is
  needs no lookup, on site or in a diagram. **Changed 2026-10-25:** previously supplies A–E
  (A = T2, B = T3, C = T4, D = T5, E = T6), as older notes and git history still call them.

- **Five S-100-5 per statue, whole towers only, symmetric** (owner, 2026-10-18). At the
  artist's final heights (2026-10-21) and the measured 29.4 mA per LED
  ([led_power_budget.md](led_power_budget.md)), every supply stays under the 18 A ceiling at
  full white (max 15.5 A, in T2 and T6). Only the two tip towers are fed from a neighbour's box. The owner
  already has 10 supplies.
  **Changed 2026-10-18 (twice):** first five per statue with T4 and T5 split between two
  supplies (sized for 60 mA per LED); then four per statue with whole towers (at the earlier,
  smaller heights). The new heights put four towers' worth (23.6 A) on one supply in the
  four-supply grouping.
  **Rejected.** *4 per statue:* only by splitting the 2000 tower between the two 1700 supplies
  (17.5 A each): more XT60 runs (4 per statue) and a split tower. Four with whole towers exists
  on paper (T4 alone, T1 + T3, T5 + T7, T2 + T6 at 17.6 A each), but T2 + T6 is cabled across the
  inside of the V, where the trench to the other statue runs, and trenches never cross
  ([trenches.md](trenches.md)); the layout tool's calculator no longer offers it (owner,
  2026-10-22). *7 per statue* (one per
  tower): no 5 V between towers, but 14 supplies for no electrical need.
- **Each supply sits by the towers it feeds** (agent, 2026-10-10). Mains is easy to carry far;
  5 V at several amps is not.
- **Each supply in its own box with a C14 inlet** (agent proposal, 2026-10-10). This reuses the
  enclosure repo's `100W` design (S-100-5, C14, perfboard, 4 JST-SM exits), so no mains
  terminals are exposed in a tower base. C shares the apex `100W-masterbox` with the ESP32 or
  receivers. **Enclosure change pending:** data inputs on the power boxes in T2, T3, T5
  and T6; XT60 and neighbour data outputs in T2 and T6; a top-feed XT60 out on all five.
- **One JST-SM per strand, from the box straight to the strand** (owner, 2026-10-18). Every
  strand is ≤ 2.5 A at full white except the 2000 mm tower's 3.3 A. A JST-SM contact is rated
  3 A, and it also carries the strand's DATA, so no separate connector is needed. The 2000
  strands' top feed (below) brings their bottom current under 3 A.
- **XT60 only where a whole tower's current travels between towers** (owner, 2026-10-18): the
  runs from the power box in T2 → T1 and in T6 → T7, 2 per statue, 8 XT60 pairs in total. A tower's combined current
  (5.6 A on these runs) is over a JST-SM's 3 A.
- **Buried 5 V runs use 3-core mains-type cable with XT60 at both ends** (owner, 2026-10-10).
  Brown +5 V, blue GND, green/yellow unused or joined to GND. 3 × 2.5 mm² (owner's choice,
  "כבל פנדל פלסטי 3*2.5"), well above the 5.6 A per run. Three cores although only two are
  used, because standard 3-core mains cable is sold in any hardware store and is far cheaper
  than 2-core cable of the same gauge (owner, 2026-10-11). **Rejected:** imported 2 × 12 AWG
  (Carol C2410A, E3062S): enough copper, but costlier, sold mostly on 305 m reels, and
  indoor-rated. No extra labelling: an XT60 can't be mistaken for mains (owner). H07RN-F
  (rubber) is the tougher jacket; PVC survives a week. Inside boxes and bases: NYAF 2.5 mm²,
  red +5 V, blue GND (owner's chosen wire; it has no black).
- **One 230 V cord per supply, from a power strip at the apex** (agent, 2026-10-10). Any supply
  can be unplugged on its own, and there are no mains joints in the field. Buried cords:
  H07RN-F 3 × 1.5 mm² with a C13 plug.
- **No separate ground bond** (agent, 2026-10-18). Each supply's 5 V output is isolated from
  mains, and every power box receives a data cable with its own GND from the apex box. That
  ties all supplies to one reference, and only leakage-level current flows through it.
  **Changed 2026-10-18:** previously a 1.5 mm² bond wire along each arm.
- **Every strand of 75 LEDs or more gets a second feed at its top, on an XT60** (owner,
  2026-10-25): the strands of T2–T6, 20 per statue, 40 in all. The tip towers' 57-LED strands
  are fed from the bottom only. The owner did not state the reason or why the line is at 75;
  the measured evidence on record is the bench reel that read 3 V at LED 111 fed from one end
  ([led_power_budget.md](led_power_budget.md)). Feeding both ends roughly halves the current
  through each end and the drop along the strip. The towers that get a top feed are exactly the
  ones with their own power box, so no top-feed current crosses between towers.
  **Changed 2026-10-25:** previously only T4's strands, and only if the strip voltage-drop
  test called for it (agent, 2026-10-10); that test no longer decides anything.
- **One top-feed cable per tower: one XT60 at the bottom, four at the top** (owner,
  2026-10-25: "a thick cable with 1 xt60 at the bottom and 4 at the top"). It plugs into an XT60
  out on the tower's own power box (all five, T2–T6), climbs the post, and splits at the top to
  the 4 strand tops. 10 cables, 10 box outputs, 50 XT60 pairs in all (10 bottom + 40 top).
  The cable is the buried runs' 3 × 2.5 mm² (agent, 2026-10-25): one cable type to stock, and
  a tower's top share (~6.6 A worst case at T4, half its 13.1 A) is well inside it. The split is
  two WAGO 221-415 at the top of the post, +5 V and GND, each with the cable core in and 4 short
  NYAF 2.5 mm² tails to the XT60s (agent, 2026-10-25): the same part and joint as the neighbour
  bases, and no soldered harness to make or repair.
- **XT60 gender: male on the strip, female on the feed cable** (agent, 2026-10-25). The
  powered side carries the shrouded female, so an unplugged live feed has no exposed contacts.
- **Logic power only from the power box in T4** (agent, 2026-10-09). The apex box perfboard
  gets its own pair from that PSU's second terminals, so tower current never flows through perfboard copper.
- **C14 fuse 1 A on the AC side** (owner, 2026-10-09). ~240 W of input for a 100 W PSU. The
  PSU's own fuse and over-temperature trip act first.
- **Mains colours brown L, blue N, green/yellow PE** — IEC colours, which Israel uses.

## Gotchas

- **The pre-wired switched C14 inlets shipped with the switch on N** (owner, 2026-10-28,
  found while wiring the two unwired inlets; 8 pre-wired and 2 self-wired in the boxes). With
  the switch on N the PSU's primary stays live with the switch off, and a PSU case or
  terminal that looks safe is not. The owner rewired them. Nothing about this goes in the
  guide (owner): the crew never opens a box
  ([../field_docs/README.md](../field_docs/README.md)). It is why the workshop handling rules
  in `guide/build.md` pull the cord first and discharge static on a data connector's GND pin,
  never on the PSU (owner's rule).
- Inlet fuses that blow at power-up need to be time-delay (T).
- Never parallel two supplies' +V outputs. The data inputs' 5V pins stay unconnected for this
  reason.

## Related

- [trenches.md](trenches.md) — what runs in each trench segment.
- [tower_base.md](tower_base.md) — the splitter in each power box and the passive neighbour bases.
- [led_power_budget.md](led_power_budget.md) — current per tower and the limiter ceilings.
