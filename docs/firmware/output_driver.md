# Output driver

Path: [docs](../README.md) › [firmware](README.md) › **output_driver**
Parent: [README.md](README.md)
**Code:** none yet (stock WLED; test firmware not yet written)
**Covers:** how the controller sends data to its 14 outputs at once, evidence that stock WLED
cannot do it cleanly, the alternatives, and the bench test that decides between them.

## What it does

WLED hands each output (a "bus") to a NeoPixelBus driver: on classic ESP32 the first 8 go to
the RMT peripheral, one RMT channel each, and the rest to I2S in parallel mode
([README.md](README.md), *14 outputs*). All buses start sending together every frame.
**No driver has been chosen yet** (2026-10-17): stock WLED's mix is in doubt and the
alternatives below are untested.

## Evidence: stock WLED flickers with several outputs

From another of the owner's projects (owner, 2026-10-17): a classic ESP32 (ESP32-D0WD-V3),
4 outputs on GPIO 27, 26, 25, 33, 60 WS2812B each, 3.3 V data with no level shifter, WLED AP up.

| Firmware | Driver | Result |
|---|---|---|
| WLED 16.0.1 | RMT | Right colours, random flashes of other colours, all outputs |
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
so replacing the output layer inside it is a contained change (agent, 2026-10-17; not yet
confirmed by the owner).
**Rejected (for now).** *Dropping WLED for FastLED + a web UI* — the owner's earlier fallback,
rejected as too much work; it stays the last resort.

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
  once is plausible but untested. 513 LEDs ≈ 15.4 ms per statue. Needs each statue's 7 towers
  sent in turn on one RMT channel, switching GPIO between towers (not stock WLED).

## Bench test

Answers [../README.md](../README.md) open question 1. Run in this order; each step decides
whether the next is needed.

| # | Firmware | Outputs | Decides |
|---|---|---|---|
| 0 | MicroPython, one output after another | 14 × 60 LEDs | Rig is sound. If this flickers, fix power/data before anything else |
| 1 | Stock WLED 16.0.1 | 14 × 60 LEDs (8 RMT + 6 I2S) | Confirms the evidence on this board and pins; which outputs fail and how |
| 2 | Test sketch, I2SClocklessLedDriver + AP + web traffic | 14 × 60 LEDs | Whether parallel I2S is clean under WiFi |
| 3 | Stock WLED, 2 outputs (RMT 0 + 1) | 2 × 513 configured | Whether two RMT channels at once are clean (needed only if 2 fails) |

- **Every output 60 LEDs, all at once** (agent, 2026-10-17). It keeps all 14 channels busy
  for the whole frame, which is harsher than the real lengths (21–111, short ones finish
  early), so a pass carries over. 60 LEDs is one T2/T5 face, so 1 m pieces cut for the test
  are reused in the towers (16 such faces are needed).
- **The real GPIO table** (agent, 2026-10-17), so a pass carries over pin for pin.
- **WiFi under load during every test** (agent, 2026-10-17): a phone on the AP with WLED's
  live preview open (or the test sketch's page refreshing). The suspected cause is WiFi
  interrupts; an idle AP could pass a driver that fails in the field.
- **Pass: 10 minutes of a different solid colour per output plus 10 minutes of a moving
  effect, no flash, right colours, right first LED** (agent, 2026-10-17). The flashes were
  random, so a short look can miss them.
- **3.3 V data straight to the strips** (agent, 2026-10-17): the 74AHCT125s had not arrived.
  WS2812B wants 0.7 × VDD (3.5 V at 5 V), so 3.3 V is out of spec; step 0 shows whether it
  is good enough on the bench. Trimming the supply to ~4.6 V brings the threshold under
  3.3 V if it is not.

## Related

- [README.md](README.md) — the 14-output decision this page puts in doubt.
- [../controller/gpio_assignment.md](../controller/gpio_assignment.md) — the pins under test.
- [../strips_and_power/tower_layout.md](../strips_and_power/tower_layout.md) — real output lengths, and the 12-channel fallback.
