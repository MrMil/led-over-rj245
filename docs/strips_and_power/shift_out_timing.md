# Shift-out timing

Path: [docs](../README.md) › [strips_and_power](README.md) › **shift_out_timing**
Parent: [README.md](README.md)
**Code:** none yet (affects WLED output configuration and any future custom effects)
**Covers:** the one timing error left in a single-controller design.

## What it does

WS2812B data shifts serially at 30 µs per LED: a 300-LED strip takes 9 ms to update, so its
last pixel lights 9 ms after its first (owner). All 8 outputs start together, so statues are
aligned at frame start; the error is within each strip.

## Decisions

- **This is now the dominant timing error and the reason for parallel outputs** (owner). It is
  larger than any sync budget the rejected multi-controller designs aimed for. Splitting each
  statue across two channels keeps per-output length, and so skew and frame time, down. Each
  channel's two strips are chained ([strip_layout.md](strip_layout.md)), so per-output length
  is strip 1 + strip 2.
- **Keep per-statue LED counts equal where possible** (owner). With unequal counts the longer
  strip's tail lands later and statue-to-statue alignment drifts at the ends.
- **Mitigations if it shows:** offset each channel's content in software by its known
  shift-out delay (a natural field of the geometry calibration,
  [../firmware/README.md](../firmware/README.md)); orient strips so travelling effects move *with* the shift-out direction
  (a wave running against it fights the delay) (owner).
- **Measure with a scope during build** (owner) rather than predicting from the datasheet.

## Gotchas

- Frame rate ceiling per output is roughly 1 / (30 µs × LEDs): 1000 LEDs on one output caps
  near 33 fps before rendering cost is counted ([../firmware/README.md](../firmware/README.md)).

## Related

- [strip_layout.md](strip_layout.md) — why each output is two chained strips.
- [../README.md](../README.md) — why there is no inter-statue sync error to worry about.
