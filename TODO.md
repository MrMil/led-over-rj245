# TODO

[← README](README.md)

## Measure / confirm

- [ ] **Layout:** tower spacing along each arm, and the distance between the two apexes.
  Gives the lengths of the 5 V runs, data cables, mains cords, and whether 10 m CAT5e
  reaches. See [trenches](docs/strips_and_power/trenches.md).
  3D sightline check and the spacing/height conflict: [statue geometry](docs/strips_and_power/statue_geometry.md).
- [ ] **Tower heights and order** with the artist: current sizes 2 × 2000, 4 × 1600,
  4 × 1250, 4 × 950 mm; order along the V assumed 950, 1250, 1600, 2000, 1600, 1250, 950.
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
