# Local outputs (statue 0)

Path: [docs](../README.md) › [controller](README.md) › **local_outputs**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`controller()`), `guide/img/controller-wiring.svg`
**Covers:** how statue 0's two channels reach its four strips without RS-485.

## What it does

GPIO 13 → 74AHCT125 gate 1 → 100 Ω → LED exit 1 (channel A). GPIO 14 → gate 2 → 100 Ω →
LED exit 3 (channel B). Gates 3 and 4 are unused, with their inputs (pins 9, 12) tied to GND.
All four OE̅ pins are tied to GND; VCC is the perfboard 5 V.

## Decisions

- **74AHCT125 as the level shifter** (owner). WS2812B VIH = 0.7 × VDD = 3.5 V at 5 V supply, so
  3.3 V GPIO is out of spec and fails intermittently (cold, longer lead, different LED batch).
  The AHCT family has TTL input thresholds, so 3.3 V in gives a clean 5 V out. It also
  protects the ESP32 GPIO from ESD and shorts on a lead that leaves the box. The ESP32 runs
  all four statues; the buffer is a socketed, cheap part. Plain 3.3 V usually works in
  practice (owner's experience), so the buffer and the 100 Ω resistors below are **drawn but
  fitted at the owner's discretion, depending on perfboard space** (owner, 2026-10-09).
  Without the buffer, GPIO 13/14 connect straight to the exit's DATA.
- **Statue 0 is not RS-485** (owner). Its strips are a short lead from the box; differential
  signalling buys nothing there.
- **One buffer gate per channel; unused gate inputs grounded** (agent, 2026-10-09). With the
  strips chained, each channel has one data exit
  ([../strips_and_power/strip_layout.md](../strips_and_power/strip_layout.md)). Floating CMOS
  inputs can oscillate and draw current, so the two spare gates' inputs go to GND.
  **Changed 2026-10-09:** previously one gate per strip (four used), for parallel strips.
- **100 Ω series resistor at every strip data output** (agent, 2026-10-09). The owner's design
  record suggested 33–100 Ω source termination for single-ended WS2812 runs. 100 Ω is close
  to the impedance of a strip lead, damping ringing on the 350 ns pulses, and limits current
  if a pinched lead shorts DATA to 5 V or GND. The same value is used on the receiver side
  ([../strips_and_power/strip_layout.md](../strips_and_power/strip_layout.md)) so one part
  serves every data exit. Optional at both ends, as with the buffer above: with short leads
  the ringing they damp is rarely visible.

## Related

- [gpio_assignment.md](gpio_assignment.md) — the two GPIOs.
- [../strips_and_power/strip_layout.md](../strips_and_power/strip_layout.md) — why each channel feeds two chained strips.
