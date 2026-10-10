# Termination and bias

Path: [docs](../README.md) › [data_link](README.md) › **termination_and_bias**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`box2()`), `guide/img/box2-wiring.svg`, `guide/wiring.md`
**Covers:** the resistors across and onto each A/B pair.

## What it does

Each pair has 120 Ω across A/B at both ends (already on the modules). At the receiver only,
560 Ω pulls B to 5 V and 560 Ω pulls A to GND.

## Decisions

- **Terminate, at both ends** (owner). Rule of thumb: terminate when propagation delay
  (~5 ns/m) exceeds ~⅓ of the rise time; 8 m ≈ 40 ns against ~15 ns edges, so yes. Both ends
  is what RS-485 specifies and two 120 Ω in parallel (60 Ω) is within the MAX485's 54 Ω drive
  rating, so the controller-side resistor on the module stays.
- **Idle bias 560 Ω / 560 Ω at the receiver** (owner). With the controller off or rebooting
  the line floats and RO is indeterminate, so the towers show garbage. The bias holds the
  differential at about −250 mV (5 V × 60 Ω / 1180 Ω with both terminations), which the
  receiver reads as logic 0 and the strip sees as idle-low.
- **B to 5 V and A to GND, not the reverse** (owner). That polarity reads as logic 0. A low
  line is the WS2812's reset/latch state, the same thing it sees between frames, so an idle
  link looks like "no new data" rather than noise.

## Gotchas

- The bias is only at the receiving end. The transmitter always drives while powered, so it
  needs none.
- If a module ships with its own weak line bias in the opposite sense, the 560 Ω pair
  dominates; if it ships with strong bias, measure the idle differential before trusting it.

## Related

- [transceivers.md](transceivers.md) — the parts these resistors surround.
- [../field_docs/wiring_diagrams.md](../field_docs/wiring_diagrams.md) — where they are drawn.
