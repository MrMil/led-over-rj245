# Tower data splitting

Path: [docs](../README.md) › [strips_and_power](README.md) › **tower_base**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`power_box()`, `neighbour_base()`), `guide/img/power-box.svg`, `guide/img/neighbour-base.svg`, `guide/wiring.md`
**Covers:** how each tower's one data line reaches its 4 strands: in the power box for a box's
own tower, passively at the base of a neighbouring tower.

## What it does

- **Own tower** (T2–T6). The tower's data line enters the power box on a JST-SM
  (DATA + GND; the 5V pin is not connected), with 10 kΩ to GND. It drives all four inputs of a
  74AHCT125. Each output goes through 100 Ω to one JST-SM out (5V, DATA, GND) to one strand.
- **Tip tower** (T1 from the power box in T2; T7 from the one in T6). Its data line enters the power box on its
  own JST-SM (10 kΩ to GND) and drives one gate of a second 74AHCT125. That buffered line
  leaves as a 22 AWG DATA + GND pair beside the XT60 power run. At the neighbour's base there
  are no electronics: XT60 into two WAGOs (+5V, GND), the data pair joined to all four JST-SM
  DATA pins, and 4 JST-SM to the strands.

## Decisions

- **One 74AHCT125 gate per strand for a box's own tower** (agent, 2026-10-10). A shorted or
  damaged strand lead takes out only its own face. One chip has four gates, so it costs nothing.
- **Neighbour towers get their data already buffered from the power box, with no electronics
  in their base** (owner, 2026-10-18: "I can take it out of the last power box and not have a
  small perfboard in the towers that don't have power boxes"). The trade-off: the
  neighbour's four faces share one buffer gate, so a short on one face's data lead darkens
  all four.
  **Rejected.** *A small 74AHCT125 board in each neighbour base:* more boards to build.
  *4 JST-SM cables per neighbour from the box:* each face independent and no XT60, but 22 AWG
  over ~2 m loses 0.2–0.4 V, and the boxes would need 8–12 JST exits.
- **10 kΩ pull-down on every data input** (agent, 2026-10-10). With the data cable unplugged or
  the sender off, the floating input would make the strips show garbage; the pull-down holds
  it low, the WS2812 idle state.
- **100 Ω per buffer output** (agent; optional per the owner). It damps ringing on the lead.
- **Data cables: any standard copper, DATA + its own GND wire** (owner, 2026-10-10/18). Apex box
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
