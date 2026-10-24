# Parallel I2S bus

Path: [docs](../README.md) › [firmware](README.md) › **parallel_i2s_bus**
Parent: [README.md](README.md)
**Code:** `../WLED`, branch `led-over-rj245` (commit `2fd53d6` on WLED 16.0.1): `wled00/bus_hpwit.h`, `wled00/bus_hpwit.cpp`, the `I_32_HP_NEO_3` cases in `wled00/bus_wrapper.h`, env `esp32dev_rj245` in `platformio.ini`
**Covers:** the WLED output driver chosen in [output_driver.md](output_driver.md): all 14 tower
outputs sent as one parallel I2S stream by hpwit's
[I2SClocklessLedDriver](https://github.com/hpwit/I2SClocklessLedDriver), inside a custom WLED build.

## What it does

With `WLED_USE_HPWIT_PARALLEL` defined, every WS2812 RGB output in LED Preferences becomes one
slot (up to 16) of a single driver. WLED still renders, applies brightness, colour order and the
current limiter per output as usual. Each output writes into its own buffer, in wire order
(G, R, B). WLED shows its outputs one after another; when the last one has been shown, the
buffers are copied into one block and the driver clocks it out on all pins at once, by DMA. A
frame takes as long as the longest output (111 LEDs, about 3.3 ms); shorter outputs go quiet
after their last LED.

Build and flash (from `../WLED`, with PlatformIO):

    pio run -e esp32dev_rj245 -t upload --upload-port <port>

The bench setup (outputs, 2D map) goes on separately as a filesystem image:
`bench/wled_bench.py` ([output_driver.md](output_driver.md), *Bench test*).

## Decisions

All agent, 2026-10-24, unless marked otherwise.

- **A new internal bus type inside WLED's `PolyBus`, not a new `Bus` class.** Outputs stay
  `BusDigital`, so brightness, colour order, skipped LEDs and the current limiter work
  unchanged. A separate `Bus` class would break WLED, which casts every digital bus to
  `BusDigital` (`BusManager::applyABL()`, `initializeABL()`).
- **Every WS2812 RGB output joins the stream, whatever driver the LED settings page shows.**
  `PolyBus::getI()` returns the new type before WLED counts RMT and I2S channels, so 14
  outputs pass WLED's 8 RMT + 8 I2S checks and the stock settings page needs no change.
- **Type id 47, an odd number.** WLED treats even ids as I2S (`BusDigital::isI2S()`) and
  reserves DMA memory for them; this bus has its own, small DMA ring.
- **One buffer per output plus one send buffer, written only while the driver is idle.** WLED
  has no "all outputs done" hook, so the send happens on the last output's `show()`. The driver
  reads the send buffer from its interrupt while sending, so writing it mid-frame would tear;
  the per-output buffers let WLED render the next frame meanwhile. Memory: 6 bytes per LED,
  about 6.7 KB for 1122 LEDs.
- **The driver starts on the first output's `begin()`.** WLED creates every output before it
  begins any, so the pin and length lists are complete by then.
- **The driver sends bytes as stored (`ORDER_RGB`).** WLED has already put each output in its
  own colour order (GRB for these strips), so the driver must not reorder again.
- **16 DMA buffers instead of the driver's 6.** The driver refills its DMA ring one LED per
  buffer from an interrupt; its README reports artifacts "especially when using wi-fi", and more
  buffers give the interrupt more time before the ring runs dry. Cost about 1.4 KB. Not
  measured against 6. `-D HPWIT_DMA_BUFFERS=n` changes it.
- **No audioreactive usermod.** Its setup resets the I2S0 peripheral, which this driver uses.
- **AsyncTCP's task pinned to core 0, with WiFi.** WLED runs its loop, LED sending included,
  on core 1 and WiFi on core 0 (owner); AsyncTCP's default is any core. The driver's interrupt
  is allocated on core 1, where its first `begin()` runs.
- **The driver pinned to commit `a736f5e` (2026-04-06)** so a rebuild gets the code that was
  tested.
- **The build env lives in `platformio.ini`.** WLED's `.gitignore` excludes
  `platformio_override.ini`, so an env there would not be in the branch.

## Gotchas

- **The source is only on this machine:** branch `led-over-rj245` in `../WLED`, not pushed
  anywhere. How the build reaches the field and the spare ESP32 is not settled.
- The LED settings page still labels outputs RMT or I2S. The label is ignored.
- At most 16 outputs; the 17th fails to create.
- The driver's interrupt is not in IRAM, so it is masked while flash is written (saving
  presets or config). Whether that glitches a frame is untested.
- WLED's default frame cap is 42 fps; the bench reads 43 fps, which is the cap, not the
  driver's limit.

## Related

- [output_driver.md](output_driver.md) — why stock WLED's drivers were replaced, and the bench test.
- [../controller/gpio_assignment.md](../controller/gpio_assignment.md) — the 14 pins in the stream.
- [../strips_and_power/shift_out_timing.md](../strips_and_power/shift_out_timing.md) — frame time of the longest output.
