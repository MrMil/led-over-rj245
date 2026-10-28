# Firmware

Path: [docs](../README.md) › **firmware**
Parent: [../README.md](../README.md)

**Covers:** the software on the controller ESP32 — WLED, configured (not compiled) for this
installation — and how the show is built and changed.
**Code:** `guide/build.md` (flash + configure), `guide/operating.md` (field use); `wled/` (the controller's files, [controller_files.md](controller_files.md)); the custom build's source is [MrMil/WLED](https://github.com/MrMil/WLED/tree/led-over-rj245), branch `led-over-rj245` (checked out at `../WLED`) ([parallel_i2s_bus.md](parallel_i2s_bus.md)); bench setup in `bench/`

## Design

### Decisions

- **WLED, configured at runtime** (owner). It runs its own WiFi AP with no
  router or internet, is controlled from any phone browser (or its native apps), supports
  multiple outputs configured at runtime with no recompile, and has presets and playlists for
  building a show in advance. Every field fix is a settings change, not a toolchain.
- **WLED 16.x, 16.0.1 or later** (agent, 2026-10-09). Current release line as of 2026-10
  ([release notes](https://github.com/wled/WLED/releases/tag/v16.0.1)); 16.0.1 fixes a
  ledmap parser overrun, and 0.15.4 fixed a preset-file corruption bug.
- **14 outputs, one per tower, all in one parallel I2S stream in a custom WLED build**
  (owner, 2026-10-24). Stock WLED's RMT and I2S drivers both failed with 4 outputs on the
  owner's other project (RMT flashes, I2S shifts colours), and the 12-output fallback uses the
  same drivers ([output_driver.md](output_driver.md)). The replacement bus is in
  [parallel_i2s_bus.md](parallel_i2s_bus.md); it passed the bench test: all 14 pins clean
  with a phone loading the AP (2026-10-24).
  **Changed 2026-10-24:** from 2026-10-10, 8 outputs on RMT + 6 on I2S (owner/agent), WLED 16's
  own mix for classic ESP32. **Changed 2026-10-10:** previously 8 outputs, all RMT.
- **Each output's LED count is one face** (agent, 2026-10-10). All 4 faces of a tower get the
  same data in parallel ([../strips_and_power/tower_layout.md](../strips_and_power/tower_layout.md)),
  so WLED renders 561 pixels per statue, 1122 total: around 60–80 fps of render capacity.
- **One continuous logical strip, outputs ordered S1-T1 … S1-T7, S2-T1 … S2-T7** (agent,
  2026-10-10). Effects that move along the strip sweep across each statue's V in order.
- **AP mode "Always", fixed channel, password changed from default** (owner + agent). The
  default only raises the AP when no known network is found, so behaviour would depend on
  what WiFi is in range (owner). A fixed channel (1/6/11) avoids the AP hopping in congested
  2.4 GHz (agent, 2026-10-09).
- **The AP password is never written on the hardware or committed to this repository**
  (owner, 2026-10-09). Many people at Midburn carry WLED on their phones and would join and
  change the show; the repo is meant to be public. The installation lead hands it to the crew
  privately. The SSID is "Layers-WLED" (owner, 2026-10-26; [controller_files.md](controller_files.md)).
  **Changed 2026-10-26:** it was to avoid the word "WLED" (agent, 2026-10-09: the WLED app
  and passers-by looking for WLED networks would spot it); the owner chose the name.
  **Changed 2026-10-09:** briefly "on the controller box label"; the owner rejected labelling
  the hardware.
- **Preset numbering: 10–99 workshop looks, 100+ field looks; the show playlist is the boot
  preset** (agent, 2026-10-09). Separate ranges stop field edits overwriting workshop work;
  the boot preset makes the show resume unattended after generator dropouts (owner
  requirement: "a reboot should rejoin the show cleanly").
  **Changed 2026-10-26:** 1–9 were reserved for test presets (agent, 2026-10-10: preset 1 a
  solid colour per tower, preset 2 a single light running the strip, so the troubleshooting
  guide could say "run preset 1"). Dropped by the owner (2026-10-26); they were never built,
  and the crew checks wiring with the per-tower effects in [custom_effects.md](custom_effects.md)
  instead (owner, 2026-10-26).
- **The show is `wled/presets.json`, and it is what gets flashed when the owner asks to burn
  the final WLED, unless the owner asks for something else** (owner, 2026-10-26). The file is
  the owner's playlist as exported from the Animations tab
  ([effects_in_browser.md](effects_in_browser.md)): presets 10–17 (PS Fire, PS Waterfall,
  Rainbow, Colored Bursts, Palette, Soap, Hiphotic, Octopus, 60 s each; Fire and Waterfall
  with 2 s and 3 s fades because both start empty and fill from the base) and the playlist as
  preset 18, which is the boot preset. The owner updates it by exporting again and asking for
  a commit; the file in `wled/` is the record, the controller is a copy of it. *Restore
  presets* replaces every preset on the controller, so the file must hold everything the
  controller should have.

### Animations in C++ ahead of time; only parameters and calibration in the field

**Why.** The owner does not want anyone programming in the field (owner, 2026-10-09).
Complex animations are written beforehand as WLED effects in C++. Each exposes its creative
knobs as WLED effect controls (speed, intensity, up to 3 custom sliders, 3 checkboxes, colours,
palette), so artists tune, save and sequence them from a phone. What the field does need is
**geometry**: effects must know where each pixel is.
**Coordinate system: a rolled 2D map, x = tower, y = height** (owner direction 2026-10-09;
simplified 2026-10-10). Each output is one tower and each pixel's index is its height (strips
run bottom to top, 60/m, starting 150 mm above the base). An effect computes
f(tower position, height, time), so a ground-to-sky wash lights the bottom of each face before
the top. Tower position along the mural is T1–T7 per statue, optionally with each tower's
horizontal position or angle as seen from the centre. That is a short table, not per-LED
mapping.
**Field calibration** reduces to tower order and LED counts. They live in WLED's LED
Preferences, plus at most one position number per tower as a usermod setting.
**Rejected.**
- *Per-LED positions from camera or 3D-model mapping* (planned 2026-10-09): needed for strips
  following figures; with vertical strips on rectangular towers, position follows from tower
  and LED index.
- *An azimuth/elevation panorama with WLED's `ledmap.json`:* 255 cells per side and per-cell
  render cost.
- *A `ledmap.json` with columns spaced by each tower's position seen from the centre*
  (owner, 2026-10-24): the empty columns between towers would swallow part of every stock 2D
  effect. The map keeps one column per tower, side by side; real positions are for the
  custom effects. A `ledmap.json` with one column per tower can still be generated so WLED's
  built-in 2D effects work.
- *Calibration through effect sliders:* only 8-bit resolution, stored per preset rather than
  once for the installation.
- *Field programming tools (MoonLight, Pixelblaze, ARTI-FX):* not needed once nobody
  programs in the field.
**Constrains.** A custom WLED build (PlatformIO) instead of the stock binary; it now exists
for the output driver ([parallel_i2s_bus.md](parallel_i2s_bus.md)), and the effects go in the
same build. Effects are previewed in the browser from the same source
([effects_in_browser.md](effects_in_browser.md)): write them in the fork's `FX.cpp`, register them in
`setupEffectData()`, and rebuild the module. The ones written so far: [custom_effects.md](custom_effects.md).

**Pre-rendered playback** (discussed 2026-10-10, not planned). Frames rendered offline (e.g.
xLights FSEQ) and played from a microSD card would remove render cost entirely. It costs live
parameters, needs a playback module (not in stock WLED; an FSEQ PR was open as of
2026-10-09), and needs 4 GPIOs, which 14 outputs don't leave. With one face rendered per tower
the frame-rate reason for it is gone.

### No current limiting

**Why.** The supplies cannot be overloaded, so nothing needs to limit (owner, 2026-10-26). Ten
power boxes, five per statue, each feed whole towers, and the worst case on any one is 15.5 A at
full white against an 18 A sizing ceiling
([../strips_and_power/led_power_budget.md](../strips_and_power/led_power_budget.md)). WLED's own
limiter is off in the shipped config (`maxpwr` 0, [controller_files.md](controller_files.md)).
**Changed 2026-10-26.** Until then the plan was a firmware ceiling the UI could not change
(owner requirement, 2026-10-10): a compile-time table of which strands feed from which supply, and
every frame scaled **as a whole** by the most constrained supply's ceiling ÷ demand, so no supply
could be overloaded and the towers kept their relative brightness. The reason was fewer supplies:
the design then had four per statue, or split towers, and one supply could reach its rating in a
bright scene. The owner built ten power boxes to make that impossible instead, so the ceiling lost
its reason and was never built.
**Rejected (2026-10-10, still rejected should a limiter ever be needed).** *WLED's per-output
limiter:* in uneven scenes it clips only the towers above the limit, flattening contrast, and it
can't see supply groups that span towers. *WLED's global limiter alone:* scales against the total,
so one bright supply group can still overload while the total looks fine. *WLED Settings PIN:* the
people with the WiFi password would have the PIN. *PSU overload protection as the cap:* it trips
the supply into shutdown, a dark statue rather than a dimmer one.

### Custom firmware — rejected for now

**Why.** WLED covers multi-output, AP, phone UI, presets and playlists with no code to maintain
in the field (owner).
**Rejected.** FastLED + ESPUI/ESPAsyncWebServer: total control, much more work; the fallback if
WLED's effects are insufficient (owner).
**Constrains (if ever revived; owner).** Set `CONFIG_FREERTOS_HZ=1000` and drive rendering from a
hardware timer (default 100 Hz tick makes `vTaskDelay` 10 ms granular). Disable
`CONFIG_PM_ENABLE`, frequency scaling and light sleep. Render as `frame = f(now)`, never
`phase += elapsed` (accumulation integrates rounding into permanent phase error). Classic ESP32
has exactly 8 RMT channels; `FASTLED_ESP32_I2S` gives headroom.

### Gotchas

- **Throughput:** WLED renders ~65–85 k LEDs/s on ESP32
  ([kno.wled.ge multi-strip](https://kno.wled.ge/features/multi-strip/)); 1122 rendered
  pixels is comfortable. Heavier custom effects cost more; check FPS on the Info page.
- **About 4 phones max on the AP:** WLED calls `softAP` without `max_connection`, so the ESP32
  default of 4 clients applies (`wled00/wled.cpp`).
- **The web UI is disabled while a realtime stream (DDP/Art-Net/E1.31) is active.**
- **Limits:** preset IDs 1–250; playlists up to 100 entries; `ledmap.json` + `ledmap1…15`.
- **Current estimate is 4× low** unless LED current per LED is set to 4× the real value:
  each output is configured as one face but drives four.
  See [../strips_and_power/led_power_budget.md](../strips_and_power/led_power_budget.md).

## Contents

### Pages

- [`output_driver.md`](output_driver.md) — sending to 14 outputs at once: evidence against stock WLED, candidate drivers, the bench test and its results.
- [`parallel_i2s_bus.md`](parallel_i2s_bus.md) — the chosen driver: one parallel I2S stream for all outputs, as a bus in the custom WLED build.
- [`effects_in_browser.md`](effects_in_browser.md) — the firmware's effect code compiled to WebAssembly and run in the layout tool's 3D LED render, to develop animations before they reach the controller.
- [`custom_effects.md`](custom_effects.md) — the installation's own effects in the fork: the 14 tower-only wiring checks.
- [`controller_files.md`](controller_files.md) — `wled/`: the config, 2D map and presets on the controller, and how a controller is flashed over USB.

### Not yet documented

- **Tower-position settings** — not built — see *Animations in C++ ahead of time* above.

## Related

- [output_driver.md](output_driver.md) — why stock WLED's drivers were replaced.
- [parallel_i2s_bus.md](parallel_i2s_bus.md) — the bus that drives the 14 outputs.
- [effects_in_browser.md](effects_in_browser.md) — where animations are developed and previewed.
- [custom_effects.md](custom_effects.md) — the effects written for this installation.
- [controller_files.md](controller_files.md) — what is on the controller and how it gets there.
- [../controller/gpio_assignment.md](../controller/gpio_assignment.md) — the pins behind the 14 outputs.
- [../field_docs/README.md](../field_docs/README.md) — the operating guide written for this configuration.
