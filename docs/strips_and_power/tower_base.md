# Tower data splitting

Path: [docs](../README.md) › [strips_and_power](README.md) › **tower_base**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`power_box(two)`, `tip_tower_cable()`), `guide/img/power-box-1-tower.svg`, `guide/img/power-box-2-tower.svg`, `guide/img/tip-tower-cable.svg`, `guide/wiring.md`
**Covers:** how each tower's one data line reaches its 4 strands: in the power box for a box's
own tower, passively at the end of the tip-tower cable for a tip tower.

## What it does

- **Own tower** (T2–T6). The tower's data line enters the power box on a JST-SM
  (DATA + GND; the 5V pin is not connected), with 10 kΩ to GND. It drives gate 1 of the box's
  one 74AHCT125. The output goes through 100 Ω and is then joined to the DATA leads of the 4
  JST-SM out (5V, DATA, GND), one per strand.
- **Tip tower** (T1 from the power box in T2; T7 from the one in T6). Its data line enters the power box on its
  own JST-SM (10 kΩ to GND) and drives gate 2 of the same 74AHCT125. That buffered line
  leaves as a 22 AWG DATA + GND pair, taped to the XT60 power run as one tip-tower cable. The
  tip tower has no electronics and nothing wired in its base: the cable itself ends in the
  4 strand JST-SMs, their 5V and GND leads in two soldered joints with the power cores (the
  data GND in the GND joint), their DATA leads soldered to the data wire, heat shrink over
  every joint ([power_distribution.md](power_distribution.md)).

## Decisions

- **One 74AHCT125 per power box; one gate drives all 4 strands of its own tower, and in a
  2 tower power box a second gate drives the tip-tower cable** (owner, 2026-10-29: "there
  should be no tip-tower electronics. the 2 level shifters are at the t6/t2, the 1.5m chord
  doesn't require a level shifter. so 2 channels are used in the level shifter", then "One
  chip, 2 gates used"). The owner's model of the box is one level shifter with one channel per
  data line leaving it; the four strand leads are short and in parallel, so one gate drives
  them. A 1 tower power box uses gate 1 only.
  **Changed 2026-10-29:** previously one gate per strand for the box's own tower (agent,
  2026-10-10), so that a shorted strand lead took out only its own face, and a second chip
  for the tip tower (agent, 2026-10-18). Changed because the owner, about to build the eight
  boxes, wants one chip per box, and the per-face isolation was the agent's idea, never
  confirmed. The trade-off the tip tower already had now holds for every tower: a short on
  one face's data lead darkens all four; `guide/troubleshooting.md` says so.
- **Neighbour towers get their data already buffered from the power box, with no electronics
  in their base** (owner, 2026-10-18: "I can take it out of the last power box and not have a
  small perfboard in the towers that don't have power boxes"; 2026-10-29: "T1 and T7 just get
  a cable that has 4 jst-SM outputs at the end"). The split lives at the end of the cable,
  made up on the bench, so there is nothing to wire on site in T1 or T7. The trade-off: the
  tip tower's four faces share one buffer gate, so a short on one face's data lead darkens
  all four.
  **Rejected.** *A small 74AHCT125 board in each tip tower's base:* more boards to build.
  *4 JST-SM cables per neighbour from the box:* each face independent and no XT60, but 22 AWG
  over ~2 m loses 0.2–0.4 V, and the boxes would need 8–12 JST exits.
- **10 kΩ pull-down on every data input** (agent, 2026-10-10). With the data cable unplugged or
  the sender off, the floating input would make the strips show garbage; the pull-down holds
  it low, the WS2812 idle state.
- **100 Ω per buffer output** (agent; optional per the owner). It damps ringing on the lead.
- **Data cables: any standard copper, DATA + its own GND wire** (owner, 2026-10-10/18). Master/slave box
  → power box, and power box → neighbour as a 22 AWG pair. Runs are a few metres between
  buffers, so nothing special is needed. The GND wire gives the signal its reference and ties
  the supplies' grounds together ([power_distribution.md](power_distribution.md)).
- **Data inputs' 5V pin left unconnected** (agent, 2026-10-18), so the sender's supply and the
  box's supply never join on +5 V.

## Gotchas

- The same chip's dead-gate failure and the handling rules for it are recorded in
  [../controller/local_outputs.md](../controller/local_outputs.md) (Gotchas); they apply to
  every power-box chip too.

## Related

- [power_distribution.md](power_distribution.md) — which box feeds which towers.
- [tower_layout.md](tower_layout.md) — why all four faces share one channel.
