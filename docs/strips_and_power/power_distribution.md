# Power distribution

Path: [docs](../README.md) › [strips_and_power](README.md) › **power_distribution**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`SUPPLIES`, `power_box(two)`, `tip_tower_cable()`, `statue_power()`), `guide/img/statue-power.svg`, `guide/img/power-box-1-tower.svg`, `guide/img/power-box-2-tower.svg`, `guide/img/tip-tower-cable.svg`, `guide/wiring.md` (Power)
**Covers:** mains from the apex to five supplies per statue, and 5 V from each supply to its towers.

## What it does

Per statue, five S-100-5 supplies, each in a box with a C14 inlet:

| Power box in | Box | Own tower | Neighbour fed | Worst case |
|---|---|---|---|---|
| T2 | 2 tower power box (`100W`) | T2 (1400) | T1 (1100) | 15.5 A |
| T3 | 1 tower power box (`100W`) | T3 (1700) | — | 10.9 A |
| T4 | apex `100W-masterbox` | T4 (2000) | — | 13.1 A |
| T5 | 1 tower power box (`100W`) | T5 (1700) | — | 10.9 A |
| T6 | 2 tower power box (`100W`) | T6 (1400) | T7 (1100) | 15.5 A |

Mains: extension cords from the outlet to statue 1's apex and on to statue 2's, then chained
tower to tower along each arm (apex → T3 → T2, apex → T5 → T6), a power strip at the end of
every cord. Each box plugs into the strip in its own tower with one short C13 cord (T4's box
is at the apex strip). Each box drives its own tower's 4 strands on 4 JST-SM.
The power boxes in T2 and T6 also feed the
tip tower next to them through one tip-tower cable: an XT60 run (3 × 2.5) with the buffered
22 AWG data pair taped to it, ending in the tip tower's 4 strand JST-SMs, soldered on
([tower_base.md](tower_base.md)). T1 and T7 have nothing else.

## Decisions

- **Power boxes are named by the tower they sit in: "power box in T2" … "power box in T6"**
  (owner, 2026-10-25: "I don't remember what ABC etc means"). A name that says where the box is
  needs no lookup, on site or in a diagram. **Changed 2026-10-25:** previously supplies A–E
  (A = T2, B = T3, C = T4, D = T5, E = T6), as older notes and git history still call them.
- **The four kinds of box are the "master box" (statue 1's apex: ESP32 and transmitters),
  the "slave box" (statue 2's apex: receivers), the "1 tower power box" (T3, T5) and the
  "2 tower power box" (T2, T6), everywhere in the repo** (owner, 2026-10-29: "the terms are
  master box and slave box, 1 tower power box and 2 tower power box. everywhere in the
  repo"). The only difference between the two power boxes is that a 2 tower power box also
  feeds the tip tower next to it, so it carries a second data in, the tip-tower data out from
  gate 2 of its chip and a second XT60 out (the board inside is the same,
  [tower_base.md](tower_base.md)); the name states that difference and is clear on
  first hearing. "Apex
  box" survives only as the generic for the master or slave box, written "master/slave box".
  **Changed 2026-10-29:** the agent first wrote "one-tower / two-tower box", "controller
  box" and "slave box"; the owner fixed the spelling and the apex names the same day.
  **Rejected:** *single box / double box* (shorter, but "double" does not say double what);
  *plain box / feeder box* (which is which needs a lookup).

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
  receivers. **Enclosure change pending:** a data input on the 1 tower and 2 tower power
  boxes; an XT60 and a tip-tower data output on the 2 tower power boxes; a top-feed XT60 out on
  all five.
- **One JST-SM per strand, from the box straight to the strand** (owner, 2026-10-18). Every
  strand is ≤ 2.5 A at full white except the 2000 mm tower's 3.3 A. A JST-SM contact is rated
  3 A, and it also carries the strand's DATA, so no separate connector is needed. The 2000
  strands' top feed (below) brings their bottom current under 3 A.
- **XT60 only where a whole tower's current travels between towers** (owner, 2026-10-18): the
  runs from the power box in T2 → T1 and in T6 → T7, 2 per statue, 4 XT60 pairs in total, at
  the box end. A tower's combined current (5.6 A on these runs) is over a JST-SM's 3 A.
- **The tip-tower run is one made-up cable: XT60 and the data pair at the box end, the 4 strand
  JST-SMs soldered on at the tower end** (owner, 2026-10-29: "T1 and T7 just get a cable that
  has 4 jst-SM outputs at the end"). Nothing is wired on site in T1 or T7; the cable plugs
  into the box and the strands plug into the cable. The 3 × 2.5 and the 22 AWG pair are taped
  together into the one cable (agent, 2026-10-29): the owner did not say whether the data
  should instead ride the 3-core's third core, so the conductors stay as they were.
  **Changed 2026-10-29:** previously XT60 at both ends and a passive split in the tip tower's
  base (owner, 2026-10-10 / 2026-10-18), so the run could be unplugged at the tower as well.
  Changed because the owner makes the split part of the cable; an XT60 at the tower end would
  join two pieces of the same cable. 8 XT60 pairs became 4.
- **Buried 5 V runs use 3-core mains-type cable** (owner, 2026-10-10).
  Brown +5 V, blue GND, green/yellow unused or joined to GND. 3 × 2.5 mm² (owner's choice,
  "כבל פנדל פלסטי 3*2.5"), well above the 5.6 A per run. Three cores although only two are
  used, because standard 3-core mains cable is sold in any hardware store and is far cheaper
  than 2-core cable of the same gauge (owner, 2026-10-11). **Rejected:** imported 2 × 12 AWG
  (Carol C2410A, E3062S): enough copper, but costlier, sold mostly on 305 m reels, and
  indoor-rated. No extra labelling: an XT60 can't be mistaken for mains (owner). H07RN-F
  (rubber) is the tougher jacket; PVC survives a week. Inside boxes and bases: NYAF 2.5 mm²,
  red +5 V, blue GND (owner's chosen wire; it has no black).
- **Mains runs tower to tower on bought extension cords with a power strip at the end of each,
  and every box plugs into its tower's strip with one short C13 cord, all ten identical**
  (owner, 2026-10-29: "there is only 1 type of c13 cable - i told the artist to get the
  shortest one she can buy - there will be extention chords going from statue to statue and a
  power strip in the end of each"; the tower-to-tower chain confirmed by the owner the same
  day). Nothing on the mains side is made up: every cord is bought, and one C13 type means no
  lengths to match to boxes. The cost: a tower's strip also feeds the next tower out, so a
  dead cord or strip at T3 darkens T2 too (`guide/troubleshooting.md` says so), and there are
  10 strips and their plug joints in the bases, under the lids. Any supply can still be
  unplugged on its own at its strip.
  **Changed 2026-10-29:** previously one buried H07RN-F 3 × 1.5 C13 cord per supply from a
  power strip at the apex (agent, 2026-10-10), chosen so that any supply could be unplugged
  alone and no mains joint lay in the field; the owner replaced it with bought cords.
- **The crew carries the cords for both ways of feeding the apexes: two outlet → apex cords
  and one apex 1 → apex 2 cord** (owner, 2026-10-29: "they should have the cables for both
  options based on where there are outlets"). Where the outlets will be is not known before
  the crew is on site, so each apex is fed from its own outlet if there is one in reach, and
  otherwise statue 2 is fed from statue 1's apex strip through the apex-to-apex trench.
- **No separate ground bond** (agent, 2026-10-18). Each supply's 5 V output is isolated from
  mains, and every power box receives a data cable with its own GND from the master/slave box. That
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
  The cable is 3 × 1.5 mm² (owner, 2026-10-29: "it doesn't matter on the top feed cables"):
  a tower's top share (~6.6 A worst case at T4, half its 13.1 A) is far inside 1.5 mm², and the
  drop over 2.3 m at that current is ~0.36 V against ~0.23 V for 2.5 mm², a difference that
  only shows at full white, which the show never reaches. The owner's 25 m of 3 × 2.5 is kept
  for the tip-tower cables, where the whole tower's current travels and the drop matters.
  **Changed 2026-10-29:** previously the buried runs' 3 × 2.5 mm² (agent, 2026-10-25), for one
  cable type to stock; the owner asked why 2.5 was needed at all, since 1.5 mm² carries 16 A
  and nothing here exceeds 6.7 A, and chose to spend the 2.5 only where the drop counts. The split is
  two soldered joints at the top of the post, +5 V and GND, each the cable core with 4 short
  NYAF 2.5 mm² tails to the XT60s, heat shrink over each (owner, 2026-10-29): the same joint
  as the tip-tower cable's end.
  **Changed 2026-10-29:** previously two WAGO 221-415 lever connectors per split (agent,
  2026-10-25), because they needed no soldered harness to make or repair. Changed because the
  owner is not using WAGOs anywhere ("whenever it calls for that i'm just welding everything
  together and putting a shrink on it"); the part leaves the list.
- **XT60 gender: male on the strip, female on the feed cable** (agent, 2026-10-25). The
  powered side carries the shrouded female, so an unplugged live feed has no exposed contacts.
- **Logic power only from the power box in T4** (agent, 2026-10-09). The master/slave box perfboard
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
- [tower_base.md](tower_base.md) — the splitter in each power box and the passive split at the tip-tower cable's end.
- [led_power_budget.md](led_power_budget.md) — current per tower and the 18 A sizing ceiling per supply.
