# TODO

[← README](README.md)

## Measure / confirm

- [x] **Layout and heights** — final from the artist, 2026-10-23: `layout/statue-layout.json`
  (heights 1100/1400/1700/2000, positions, segment lengths in
  [trenches](docs/strips_and_power/trenches.md)).
- [ ] **CAT5e length:** the apexes are 17.4 m apart, so the 10 m cables do not reach. Buy or
  make 3 × 20 m (plus spare), or decide otherwise ([cabling](docs/data_link/cabling.md)).
- [ ] **With the artist:** strips run bottom to top; 15 cm dark base; LED count per face as
  fitted; how the tower-base board connects to each strand's DIN.

## Test

- [x] **ESP32 14-channel test** ([output_driver.md](docs/firmware/output_driver.md)): custom
  WLED build, one parallel I2S stream. Passed 2026-10-24: right colour and first LED on all
  14 pins, no flashing, phone on the AP with the live preview, 43 fps, 121 KB free.
- [x] ~~**Strip voltage drop**~~ — no longer decides anything: the owner chose a top feed on
  every strand of 75 LEDs or more (2026-10-25). Was (decides whether T4's strands need a second feed at the top):
  1.85 m of the bought strip, full white, fed from one end only. Measure the voltage between
  5V and GND at the far end: ≥ 4.5 V → no top feed; ≤ 4.3 V → top feed needed.
  Measure the input end too, on the cut T4 strip (owner, 2026-10-24): a coiled reel read 3 V
  at LED 111 with the input end unmeasured ([led_power_budget.md](docs/strips_and_power/led_power_budget.md)).

## Build

- [ ] **Enclosure repo:** every `100W` and `100W-masterbox` also needs a top-feed XT60 out (×10).
- [ ] **Enclosure repo:** `100W` box with XT60 outputs (×8); `100W-masterbox` with 7 tower
  data outputs + XT60 outputs (×2).
- [ ] **SN74AHCT125N chips and A 14-LC-TT sockets:** ordered 2026-10-11, due about 2026-10-15.
- [ ] **Check parts:** every MAX485 chip reads MAX485 (not 483/487); every 74AHCT125 reads
  AHCT125 (cheap listings sometimes ship relabelled HC parts); the ESP32 has no PSRAM and breaks
  out all 14 pins (one HW-394 checked 2026-10-24: no PSRAM, all 14 pins drive a strip).
- [ ] **Bench test** the whole system before the event ([build.md](guide/build.md)).
