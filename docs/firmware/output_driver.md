# Output driver

Path: [docs](../README.md) › [firmware](README.md) › **output_driver**
Parent: [README.md](README.md)
**Code:** `bench/step0.py` (bench step 0, MicroPython); the custom WLED build in `../WLED`, branch `led-over-rj245` (`wled00/bus_hpwit.*`, env `esp32dev_rj245`); its bench setup `bench/wled_bench.py` (writes `bench/wled-cfg.json`, `wled-presets.json`, `wled-ledmap.json` and a LittleFS image)
**Covers:** how the controller sends data to its 14 outputs at once, evidence that stock WLED
cannot do it cleanly, the alternatives, and the bench test that decides between them.

## What it does

Stock WLED hands each output (a "bus") to a NeoPixelBus driver: on classic ESP32 the first 8
go to the RMT peripheral, one RMT channel each, and the rest to I2S in parallel mode. All buses
start sending together every frame. The custom build replaces that with one parallel I2S stream
for every output ([parallel_i2s_bus.md](parallel_i2s_bus.md)).
**Chosen (owner, 2026-10-24): all 14 outputs in one parallel I2S stream, as a new bus in a
custom WLED build**, tested in that build rather than in the standalone sketch of step 2. It is
the only candidate with no skew between towers and a render-bound frame rate. It is untested:
the bench test below decides whether it holds under WiFi load.
**Changed 2026-10-24:** from 2026-10-17 no driver had been chosen.

## Evidence: stock WLED flickers with several outputs

From another of the owner's projects (owner, 2026-10-17): a classic ESP32 (ESP32-D0WD-V3),
4 outputs on GPIO 27, 26, 25, 33, 60 WS2812B each, 3.3 V data with no level shifter, WLED AP up.

| Firmware | Driver | Result |
|---|---|---|
| WLED 16.0.1 | RMT | Right colours, constant random flashes of other colours, all outputs |
| WLED 16.0.1 | I2S | No flashing; colours rotated (red→green, green→blue, blue→red); first LED of each strip wrong |
| WLED 0.14.4 | RMT | RMT channels 0–1 clean, 2–3 flash |
| WLED 0.14.4, outputs reordered | RMT | **The flashing followed the RMT channel, not the GPIO** |
| MicroPython 1.29 `neopixel`, one strip after another, AP up, ~40 fps | RMT | Clean, right colours |

- **The RMT flashing is the driver, not the wiring** (owner, 2026-10-17). It followed the
  channel when pins were swapped, and MicroPython was clean on the same wiring and power. The
  likely mechanism (unconfirmed): each RMT channel holds only a few LEDs of data and needs an
  interrupt to refill it; with several channels sending at once, the last channels serviced
  run dry when WiFi interrupts delay the refills. 8 channels at once would be worse than 4.
- **The I2S fault looks deterministic, not interference** (agent inference, 2026-10-17, not
  verified). Red→green with the first LED wrong fits two junk bytes at the start of each
  frame: the stream shifts by 2/3 of a pixel, so every LED reads the next colour byte. A
  logic analyser on one output would confirm it.
- WLED issues [#5264](https://github.com/wled/WLED/issues/5264) and
  [#4805](https://github.com/wled/WLED/issues/4805) report the same multi-output flicker,
  unresolved. The replacement "WLED Pixel Bus" driver
  ([PR #5704](https://github.com/wled/WLED/pull/5704)) was unreleased with reported hangs as
  of 2026-10, so waiting for it is not an option before the event.

**Consequence:** the planned 8 RMT + 6 I2S mix uses both failing drivers, and the 12-output
fallback (two towers sharing a channel) uses the same drivers, so it does not help.

## Decisions

### WLED stays; only the output layer is in question

**Why.** WLED's value here is the access point, phone UI, presets, playlists and boot preset
([README.md](README.md)), which would take the longest to rebuild; the failure is confined to
the bus drivers. A custom WLED build is already required for the effects and the current cap,
so replacing the output layer inside it is a contained change (agent, 2026-10-17; confirmed
by the owner 2026-10-24, choosing a custom WLED build).
**Rejected (for now).** *Dropping WLED for FastLED + a web UI* — the owner's earlier fallback,
rejected as too much work; it stays the last resort.

- **The custom WLED source is the fork [MrMil/WLED](https://github.com/MrMil/WLED/tree/led-over-rj245)**
  (owner, 2026-10-24/25), branch `led-over-rj245` on WLED tag v16.0.1, checked out at
  `../WLED`. The build reaches the field on the ESP32s themselves: the controller and its spare
  are flashed here before they are sent (owner, 2026-10-25), so no firmware file is published.
  **Changed 2026-10-25:** from 2026-10-24 a local clone only.

### Candidate drivers

| Option | Frame rate | Skew first→last tower | Work |
|---|---|---|---|
| All 14 outputs in one parallel I2S stream | ~80–100 fps (render-bound) | none | most: new WLED bus |
| One output after another (as MicroPython) | ~26–28 fps; ~40 if sending runs in its own task | ~25 ms | least |
| One statue per RMT channel, the two at once | ~50–80 fps | ~12 ms | as above |

- **Parallel I2S candidate: hpwit's
  [I2SClocklessLedDriver](https://github.com/hpwit/I2SClocklessLedDriver)** (agent,
  2026-10-17). Up to 16 parallel outputs on arbitrary GPIOs, so the
  [GPIO table](../controller/gpio_assignment.md) stays; per-output lengths; GRB; DMA, so no
  per-LED interrupt. Its README itself mentions artifacts "especially when using wi-fi", so
  it is only a candidate until it passes the bench test under WiFi load. All outputs are
  clocked out together, so a frame takes as long as the longest output (111 LEDs, ~3.3 ms,
  see [../strips_and_power/shift_out_timing.md](../strips_and_power/shift_out_timing.md)).
- **One after another** — 1026 LEDs × 30 µs ≈ 31 ms on the wire. No reset gap is needed
  between outputs, since each strip latches on its own pin. If sending blocks the render loop,
  WLED's ~12–16 ms render for 1026 pixels adds on top (~45 ms, ~22 fps). It brings back the
  skew that one-channel-per-tower removed.
- **One statue per channel** — RMT channels 0 and 1 stayed clean with 4 running, so 2 at
  once is plausible but untested. 561 LEDs ≈ 16.8 ms per statue. Needs each statue's 7 towers
  sent in turn on one RMT channel, switching GPIO between towers (not stock WLED).

## Bench test

Answers [../README.md](../README.md) open question 1. Run in this order; each step decides
whether the next is needed.

| # | Firmware | Outputs | Decides |
|---|---|---|---|
| 0 | MicroPython, one output after another | 14 × 60 configured | Rig is sound. If this flickers, fix power/data before anything else |
| 1 | Stock WLED 16.0.1 | 14 × 60 configured (8 RMT + 6 I2S) | Confirms the evidence on this board and pins; which outputs fail and how |
| 2 | Test sketch, I2SClocklessLedDriver + AP + web traffic | 14 × 60 configured | Whether parallel I2S is clean under WiFi |
| 3 | Stock WLED, 2 outputs (RMT 0 + 1) | 2 × 561 configured | Whether two RMT channels at once are clean (needed only if 2 fails) |

- **One strip, moved from pin to pin; all 14 outputs configured and sending** (owner,
  2026-10-24). Its data lead is touched to each of the 14 GPIOs in turn, with the GND always
  connected. The driver sends the same waveform on a pin whether or not a strip is attached,
  so the RMT/I2S and interrupt load is that of 14 strips, and one strip shows what each pin
  is sending (agent's reading of why, 2026-10-24). A different solid colour per output tells
  which pin the strip is on; in step 0 statue 2's pins repeat the 7 test colours on every
  other LED, since 14 solid colours would be hard to tell apart (agent, 2026-10-24).
  **Changed 2026-10-24:** from 2026-10-17 the test called for
  14 strips of 60 LEDs wired at once (agent).
- **Every output configured with its real tower's LED count, laid out as the 2D map**
  (owner, 2026-10-24: the bench should look like the installation). `bench/wled_bench.py`
  takes the counts (57–111) and pins from `tools/wiring_diagrams.py` and writes a
  `ledmap.json` 14 towers wide and 111 tall, bottom-aligned, so WLED's 2D effects run as on
  the statues. The parallel stream clocks every output for the longest one's length (shorter
  ones send nothing after their last LED), so real lengths load the driver as much as 111 on
  every output would (agent, 2026-10-24).
  **Changed 2026-10-24:** from 2026-10-17 every output was 60 LEDs (agent), harsher than the
  real lengths for separate RMT channels, where short outputs finish early; that does not
  hold for one parallel stream.
- **The real GPIO table** (agent, 2026-10-17), so a pass carries over pin for pin.
- **WiFi under load during every test** (agent, 2026-10-17): a phone on the AP with WLED's
  live preview open (or the test sketch's page refreshing). The suspected cause is WiFi
  interrupts; an idle AP could pass a driver that fails in the field.
  **Step 0's page opens as the network's sign-in page**, as WLED's does (owner, 2026-10-24:
  the phone opens it by itself, which is convenient): `bench/step0.py` answers every DNS
  name with the board's address. **Step 0 is not WLED's core split:** WLED runs WiFi on
  core 0 and its loop, LED sending included, on core 1 (owner, 2026-10-24). MicroPython runs
  all Python on one core, so step 0's web server shares the LED core and only the WiFi
  driver is on the other (agent, 2026-10-24, from memory of the MicroPython port, not
  checked for 1.29). The phone never loaded step 0's page: first with the web server in a
  thread, then serving from the LED loop between frames; cause not found. The sign-in page
  version passed a self-test on the board (DNS and HTTP from the board to itself) but was not
  tried on the phone before step 0 was dropped.
- **Pass: a different solid colour on every pin with the phone loading the AP, no flash,
  right colours, right first LED** (owner, 2026-10-24). The flashes on the owner's other
  project were constant, so a look at each pin shows them; and with one parallel stream a
  fault would hit every pin at once, so there is nothing per pin that a long watch adds.
  **Changed 2026-10-24:** from 2026-10-17, 10 minutes solid plus 10 minutes of a moving effect
  per output (agent), meant to catch rare flashes, which the flashes turned out not to be.
- **3.3 V data straight to the strips** (agent, 2026-10-17): the 74AHCT125s had not arrived.
  WS2812B wants 0.7 × VDD (3.5 V at 5 V), so 3.3 V is out of spec; step 0 shows whether it
  is good enough on the bench. Trimming the supply to ~4.6 V brings the threshold under
  3.3 V if it is not.

### Results

- **Step 0, 2026-10-24** (owner): HW-394 board (ESP32-D0WD-V3, 4 MB flash), MicroPython
  1.29.0, `bench/step0.py`, 24.9 fps, 3.3 V data straight to the strip. **All 14 pins showed
  their expected colour** (pin order and colour order right; 3.3 V data drives the strip).
  **No phone was on the AP** (AP up but idle), so this run does not meet *WiFi under load*
  above. Repeating it with the phone was dropped (owner, 2026-10-24) in favour of testing in
  a custom WLED build. Not recorded: how long each pin was watched, and whether any flash or
  wrong first LED was seen.
- **Custom WLED, parallel I2S, 2026-10-24** (owner): the parallel-I2S bus (a since-removed bench build of it), 14 outputs × 60
  from `bench/wled-cfg.json`, test colours as boot preset 1, 43 fps (WLED's default frame
  cap), 124 KB free heap. **Passed:** all 14 pins showed their expected colour
  and the right first LED, with no flashing, with a phone on the AP and the live preview open
  (owner). The bench config then became the 2D map above (1122 LEDs, 14 × 111 matrix),
  no boot preset, brightness 48; WLED reports 43 fps and 121 KB free heap with it. Start-up
  brightness then went to 100% (owner), with the bench supply's limit raised from 1 A to 3 A
  first: WLED's default orange on one strip draws about 1.9 A.
- **The bench config turns WLED's current limiter off** (agent, 2026-10-24). Its 850 mA
  default is shared across all 840 configured LEDs, and WLED counts 1 mA standby per LED, so
  it left almost nothing for one real strip. The real show needs it set properly.
- **The bench config goes in as a LittleFS image over USB** (agent, 2026-10-24): `cfg.json`
  and `presets.json` built with PlatformIO's `mklittlefs` and written to the filesystem
  partition (0x310000, 0xF0000 bytes, from `tools/WLED_ESP32_4MB_1MB_FS.csv`). WLED 16.0.1
  accepts only state JSON over serial, not config, and joining the AP from the development
  machine would cut its internet.
- **Step 1 skipped** (owner, 2026-10-24): stock WLED was already tested on the owner's other
  project with 4 outputs (*Evidence* above), and both its drivers failed; 14 outputs would
  only load them harder. The next test is a custom WLED build with a replacement driver.

## Related

- [README.md](README.md) — the 14-output decision.
- [parallel_i2s_bus.md](parallel_i2s_bus.md) — the chosen driver, as built.
- [../controller/gpio_assignment.md](../controller/gpio_assignment.md) — the pins under test.
- [../strips_and_power/tower_layout.md](../strips_and_power/tower_layout.md) — real output lengths, and the 12-channel fallback.
