# Firmware

Path: [docs](../README.md) › **firmware**
Parent: [../README.md](../README.md)

**Covers:** the software on the controller ESP32 — WLED, configured (not compiled) for this
installation — and how the show is built and changed.
**Code:** `guide/build.md` (flash + configure), `guide/operating.md` (field use); backups will live in `wled/` (not yet created)

## Design

### Decisions

- **WLED, configured at runtime** (owner). It runs its own WiFi AP with no
  router or internet, is controlled from any phone browser (or its native apps), supports
  multiple outputs configured at runtime with no recompile, and has presets and playlists for
  building a show in advance. Every field fix is a settings change, not a toolchain.
- **WLED 16.x, 16.0.1 or later** (agent, 2026-10-09). Current release line as of 2026-10
  ([release notes](https://github.com/wled/WLED/releases/tag/v16.0.1)); 16.0.1 fixes a
  ledmap parser overrun, and 0.15.4 fixed a preset-file corruption bug.
- **14 outputs, one per tower: 8 on RMT + 6 on I2S** (owner/agent, 2026-10-10). WLED 16
  supports up to 8 RMT + 8 parallel I2S outputs on classic ESP32. All I2S buses must be the
  same LED type (all WS2812B), and I2S uses DMA memory proportional to the largest bus.
  Source: `wled00/const.h` on WLED main, WLED issue #5266. **In doubt (2026-10-17):** the
  owner saw both drivers fail with 4 outputs on another project (RMT flashes, I2S shifts
  colours), and the 12-output fallback uses the same drivers. Alternatives and the bench test
  are in [output_driver.md](output_driver.md).
  **Changed 2026-10-10:** previously 8 outputs, all RMT.
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
  privately. The SSID avoids the word "WLED" for the same reason (agent, 2026-10-09): the
  WLED app and passers-by looking for WLED networks would otherwise spot it.
  **Changed 2026-10-09:** briefly "on the controller box label"; the owner rejected labelling
  the hardware.
- **Preset numbering: 1–9 tests, 10–99 workshop looks, 100+ field looks; the show playlist is
  the boot preset** (agent, 2026-10-09). Tests at fixed numbers let the troubleshooting guide
  refer to "preset 1"; separate ranges stop field edits overwriting workshop work; the boot
  preset makes the show resume unattended after generator dropouts (owner requirement:
  "a reboot should rejoin the show cleanly").
- **Test presets: 1 = solid colour per tower (T1 red … T7 magenta, both statues), 2 = a single
  light running the whole strip** (agent, 2026-10-10). Preset 1 checks every channel, every
  face and the colour order (T1 must be red under GRB). Preset 2 checks tower order and
  cable-to-jack mapping.

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
  render cost. A `ledmap.json` with one column per tower can still be generated so WLED's
  built-in 2D effects work.
- *Calibration through effect sliders:* only 8-bit resolution, stored per preset rather than
  once for the installation.
- *Field programming tools (MoonLight, Pixelblaze, ARTI-FX):* not needed once nobody
  programs in the field.
**Constrains.** A custom WLED build (PlatformIO) instead of the stock binary.

**Pre-rendered playback** (discussed 2026-10-10, not planned). Frames rendered offline (e.g.
xLights FSEQ) and played from a microSD card would remove render cost entirely. It costs live
parameters, needs a playback module (not in stock WLED; an FSEQ PR was open as of
2026-10-09), and needs 4 GPIOs, which 14 outputs don't leave. With one face rendered per tower
the frame-rate reason for it is gone.

### The current cap cannot be changed from the UI

**Why.** The owner requires it (2026-10-10). The cap protects the PSUs and wiring, and it must
survive a mistake made by a crew member with full access.
**Planned shape** (agent, 2026-10-10, not built). The custom build knows which strands feed
from which PSU (a compile-time table) and each PSU's ceiling. Every frame it estimates each
PSU group's current, takes the most constrained group's ratio (ceiling ÷ demand), and scales
**the whole frame by that one factor**. No PSU can be overloaded, and relative brightness
between towers is preserved: a bright scene never leaves the tall tower dimmer than the rest
(owner requirement, 2026-10-10). The ceilings cannot be changed from the UI, a restored backup
or the JSON API; only re-flashing changes them.
**Rejected.** *WLED's per-output limiter* (each tower capped at a fraction of its worst
case): even in uniformly bright scenes, but in uneven scenes it clips only the towers above
the limit, flattening contrast. It also can't see PSU groups that span towers. *WLED's global
limiter alone:* scales uniformly but only against the total, so one bright PSU group can
still overload while the total looks fine.
**Rejected.** *WLED Settings PIN* (owner, 2026-10-10): the people with the WiFi password would
have the PIN, so it does not prevent their mistakes. *PSU overload protection as the cap:* it
trips the supply into shutdown, a dark statue rather than a dimmer one.

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

- [`output_driver.md`](output_driver.md) — sending to 14 outputs at once: evidence against stock WLED, candidate drivers, the bench test.

### Not yet documented

- **WLED configuration backup** — `wled/cfg.json`, `wled/presets.json` (to be created) — the restorable state of the controller; the AP password must be blanked before commit.
- **Optional `ledmap.json`** — not built — one column per tower, so WLED's built-in 2D effects can be used.
- **Tower-position settings** — not built — see *Animations in C++ ahead of time* above.
- **Firmware current ceiling** — not built — see *The current cap cannot be changed from the UI*.
- **Custom effects** — not built — the installation's own animations, written in C++ as WLED effects.

## Related

- [output_driver.md](output_driver.md) — why the 14-output configuration above is in doubt.
- [../controller/gpio_assignment.md](../controller/gpio_assignment.md) — the pins behind the 14 outputs.
- [../field_docs/README.md](../field_docs/README.md) — the operating guide written for this configuration.
