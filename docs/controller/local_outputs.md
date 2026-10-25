# Local outputs (statue 1)

Path: [docs](../README.md) › [controller](README.md) › **local_outputs**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`controller()`), `guide/img/controller-wiring.svg`
**Covers:** how statue 1's 7 tower channels leave the controller box without RS-485.

## What it does

GPIOs 4, 13, 14, 16 → 74AHCT125 #1 gates 1–4; GPIOs 17, 18, 19 → 74AHCT125 #2 gates 1–3
(the unused 4A input tied to GND). Each output → 100 Ω → a tower data output (DATA + GND) to
that tower's base, through the trench under the statue.

## Decisions

- **74AHCT125 between the ESP32 and the tower cables** (owner design; optional per the owner,
  2026-10-09, depending on perfboard space). It gives a 5 V, strongly driven signal for the
  cable run, and it protects the ESP32 GPIOs from ESD and shorts on cables that leave the box.
  The ESP32 drives both statues, so losing a GPIO is expensive; the buffer is a socketed,
  cheap part. The tower-base 74AHCT125 accepts 3.3 V anyway (TTL thresholds), so without
  this buffer the link still works over short runs.
- **Unused gate inputs grounded** (agent). A floating CMOS input can oscillate and draw
  current.
- **100 Ω series resistor at each output** (agent, 2026-10-09; optional per the owner). It
  damps ringing on the cable and limits current if a pinched cable shorts DATA. The same
  value is used at box 2's outputs and in the power boxes.
- **The 100 Ω stands upright in the output pin's row, with the output wire soldered to its
  top lead** (owner, 2026-10-11). The ESP32 board has no room to lay resistors flat (see
  [README.md](README.md)). Upright, it still sits at the driver, where series termination
  works best. Heat shrink over the resistor and the joint stops it shorting to its
  neighbours. It goes in a free hole of the row, not on the chip leg, because the chips are
  socketed and must stay removable. The wires are tied down, or their pull would flex the
  resistor lead at the board until it breaks.
- **Statue 1 is not RS-485** (owner). Its towers are a few metres from the box inside the
  statue; differential signalling buys little there. Statue 2's channels cross the trench
  between the statues, which is the long, exposed run.

## Related

- [gpio_assignment.md](gpio_assignment.md) — the seven GPIOs.
- [../strips_and_power/tower_base.md](../strips_and_power/tower_base.md) — what receives these signals.
