# Shift-out timing

Path: [docs](../README.md) › [strips_and_power](README.md) › **shift_out_timing**
Parent: [README.md](README.md)
**Code:** none (affects WLED output configuration)
**Covers:** the serial update time of WS2812 strips and why it no longer constrains the design.

## What it does

WS2812B data shifts at 30 µs per LED, so a strip's last pixel lights 30 µs × N after its first
(owner). All 14 outputs start together. The longest output is one face of the 2000 mm tower,
111 LEDs: 3.3 ms per frame, a ceiling near 300 fps.

## Decisions

- **One channel per tower keeps outputs short** (owner, 2026-10-10). Faces run in parallel off
  the tower-base splitter, so per-output length is one face.
  **Changed 2026-10-10:** previously the dominant timing error, with outputs of up to ~900
  LEDs (one strand per V arm) and a ~37 fps ceiling.
- **Measure with a scope during build** (owner) rather than predicting from the datasheet.

## Related

- [tower_layout.md](tower_layout.md) — why each output is one face.
- [../firmware/README.md](../firmware/README.md) — render throughput, the remaining frame-rate limit.
