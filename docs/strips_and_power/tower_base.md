# Tower base

Path: [docs](../README.md) › [strips_and_power](README.md) › **tower_base**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`tower_base()`), `guide/img/tower-base.svg`, `guide/wiring.md` (Tower base)
**Covers:** the small board in the 15 cm dark space at the bottom of each of the 14 towers.

## What it does

The tower data cable (DATA + GND) enters; DATA goes to all four inputs of a 74AHCT125 and
through 10 kΩ to GND. Each of the four outputs goes through 100 Ω to one face's strip DIN.
VCC comes from the tower's +5 V feed; OE pins to GND.

## Decisions

- **A 74AHCT125 per tower, one gate per face** (agent, 2026-10-10). One input drives four
  strips with separate drivers. A shorted or damaged strip lead takes out only its own face.
  The cable sees one load, not four. It also re-buffers the signal after the cable run. Its TTL
  inputs accept 3.3 V or 5 V, so it works whether or not the controller's buffers are fitted.
- **10 kΩ pull-down on the input** (agent, 2026-10-10). With the data cable unplugged or the
  box off, the floating input would make the strips show garbage; the pull-down holds it low,
  the WS2812 idle state.
- **100 Ω per face output** (agent; optional per the owner). It damps ringing on the strip
  lead.
- **Data cable: any standard 2-core copper cable, DATA + GND** (owner, 2026-10-10). The runs
  are a few metres inside each statue's trench, buffered at both ends, so nothing special
  is needed.
- **Data cable carries its own GND wire** (agent, 2026-10-10). The data needs a reference
  that runs alongside it. Relying on the separate power feed's ground puts the data return
  through a high-current path and a larger loop.
- **Mounted in the 15 cm dark base** (owner: "15 cm dark space at the bottom for the
  electronics").

## Related

- [tower_layout.md](tower_layout.md) — why all four faces share one channel.
- [../controller/local_outputs.md](../controller/local_outputs.md) — what drives the cable from statue 1's box.
