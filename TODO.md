# TODO

[← README](README.md)

## Measure / confirm

- [x] **Layout and heights** — final from the artist, 2026-10-21: `layout/statue-layout.json`
  (heights 1100/1400/1700/2000, positions, segment lengths in
  [trenches](docs/strips_and_power/trenches.md)).
- [ ] **CAT5e length:** the apexes are 17.4 m apart, so the 10 m cables do not reach. Buy or
  make 3 × 20 m (plus spare), or decide otherwise ([cabling](docs/data_link/cabling.md)).
- [ ] **With the artist:** strips run bottom to top; 15 cm dark base; LED count per face as
  fitted; how the tower-base board connects to each strand's DIN.

## Test

- [ ] **ESP32 14-channel test:** stock WLED 16, 14 outputs, read FPS and free memory, probe
  every pin. Fallback: 12 channels.
- [ ] **Strip voltage drop** (decides whether T4's strands need a second feed at the top):
  1.85 m of the bought strip, full white, fed from one end only. Measure the voltage between
  5V and GND at the far end: ≥ 4.5 V → no top feed; ≤ 4.3 V → top feed needed.

## Build

- [ ] **Enclosure repo:** `100W` box with XT60 outputs (×8); `100W-masterbox` with 7 tower
  data outputs + XT60 outputs (×2).
- [ ] **SN74AHCT125N chips and A 14-LC-TT sockets:** ordered 2026-10-11, due about 2026-10-15.
- [ ] **Check parts:** every MAX485 chip reads MAX485 (not 483/487); every 74AHCT125 reads
  AHCT125 (cheap listings sometimes ship relabelled HC parts); the ESP32 has no PSRAM and breaks
  out all 14 pins.
- [ ] **Bench test** the whole system before the event ([build.md](guide/build.md)).
