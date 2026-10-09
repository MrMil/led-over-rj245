# Strip layout

Path: [docs](../README.md) › [strips_and_power](README.md) › **strip_layout**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`EXITS`, `statue()`, `controller()`, `power()`), `guide/setup.md` (exit table)
**Covers:** how the four LED exits of a box relate to its two data channels.

## What it does

Each data channel drives two strips in a chain, so every LED has its own address. Exit 1
(channel A) and exit 3 (channel B) carry 5 V, DATA and GND to strip 1. Exits 2 and 4 carry
5 V and GND; their DATA pin is not connected in the box. WLED's LED count per output is
strip 1 + strip 2. How the data gets from strip 1 to strip 2, and how power is fed along
the strips, is wiring on the statue side that the owner will decide once LED counts are
known (owner, 2026-10-09: there will be no jumpers on the artist's side).

## Decisions

### Four strips per box, two per channel, chained

**Why.** Four strips per statue, two per channel, matching the enclosures' four LED exits
(owner, 2026-10-09). Chained because the strips are **independently placed** on the statue
(owner, 2026-10-09). Every LED needs its own pixel address for geometry calibration to work
([../firmware/README.md](../firmware/README.md)): an effect defined on physical angle or
position must be able to light the two strips differently.
**Rejected.** *Parallel split* (both strips on one data line through separate 100 Ω
resistors). It halves per-output shift-out time, but the two strips show
identical pixels, so they cannot be calibrated independently.
**Changed 2026-10-09:** previously parallel (agent choice), because the 3-pin exits cannot
bring strip 1's DOUT back into the box. Changed because the owner confirmed the strips are
independently placed.
*Separate channels per strip:* 16 outputs is more than the ESP32's 8 RMT channels.
**Constrains.**
- Per-output length is the sum of both strips, which doubles shift-out time per output
  ([shift_out_timing.md](shift_out_timing.md)).
- Exits 2 and 4 are power-only for now. Their DATA pin stays unconnected in the box (agent,
  2026-10-09), so the box can never drive strip 2's input at the same time as strip 1's
  output. Revisit when the statue-side wiring is decided.
- One dead LED at the end of strip 1 darkens strip 2 as well.
- **Not to be designed by agents:** power feeding along the strips and the data path between
  strips. The owner decides these from the art and the LED counts and will say when.

## Related

- [../controller/local_outputs.md](../controller/local_outputs.md) — the data source in statue 0.
- [power_distribution.md](power_distribution.md) — how each exit gets 5 V.
- [led_power_budget.md](led_power_budget.md) — the brightness limit per output.
