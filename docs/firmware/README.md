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
- **All 8 outputs on the RMT driver** (agent, 2026-10-09). WLED 16 offers per-output RMT or
  parallel I2S on classic ESP32 (8 + 8); 8 outputs fit in RMT, and parallel I2S needs all I2S
  buses to be the same type and DMA memory proportional to the largest bus. Source:
  `wled00/const.h` on WLED main, WLED issue #5266.
- **One continuous logical strip, outputs ordered S0-A, S0-B, S1-A … S3-B** (owner). Effects
  that move along the strip then travel around the circle with no synchronisation logic
  anywhere.
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
- **Test presets: 1 = solid colour per statue (0 red, 1 green, 2 blue, 3 white), 2 = a single
  dot running the whole strip** (agent, 2026-10-09). Preset 1 checks every channel and the
  colour order (statue 0 must be red under GRB); preset 2 checks statue numbering and output
  order, which a wrong cable-to-jack mapping would scramble.

### Animations in C++ ahead of time; only parameters and calibration in the field

**Why.** The owner does not want anyone programming in the field (owner, 2026-10-09).
Complex animations are written beforehand as WLED effects in C++. Each exposes its creative
knobs as WLED effect controls (speed, intensity, up to 3 custom sliders, 3 checkboxes, colours,
palette), so artists tune, save and sequence them from a phone. What the field does need is
**calibration**: the strips are independently placed, so an effect such as "something
travelling around the circle" only looks right if every LED's physical angle or position is
known.
**Coordinate system** (owner direction, 2026-10-09, pending the statue builders): a panorama
seen from the circle's centre, with x = azimuth and y = elevation, so effects are written as
"a round screen around the viewer" (see the anamorphic note in [../README.md](../README.md)).
WLED's `ledmap.json` can express this as a 2D grid. Its limits:
- At most 255 cells per side, so azimuth resolution is at best 360/255 ≈ 1.4° (≈10 cm at 4 m).
- One LED per cell.
- Render cost is per cell, not per LED: about 65–85 k cells/s, so a 120 × 30 grid runs at
  roughly 20 fps.

Because many LEDs on one part of a figure see nearly the same point of the image, a coarse
WLED grid leaves most of them unmapped, and a fine one is slow.
**Planned shape** (owner direction + agent proposal, 2026-10-09, not built). **A rolled 2D
map**: x = angle around the circle, y = height. Animations are written as 2D images f(x, y, t)
on this unrolled cylinder. **Every LED has its own continuous (x, y)**, not a grid cell, so a
ground-to-sky wash still lights the bottom of a hand before its top (owner's example).
Calibration is split by when it can be done:
- **Workshop, per statue:** each LED's position in the statue's own frame (sideways offset,
  height), mapped once when the LEDs are fitted. A statue is rigid, so this never changes in
  the field. Methods: export from the builders' 3D model if one exists, camera mapping from
  the design viewpoint with binary-coded LED patterns (about log₂(N) photos), or marked LEDs
  measured along each strip and interpolated. Stored as a file on the ESP32 (int16, ~4 bytes
  per LED).
- **Field, per statue, a few numbers in Config → Usermods:** angle on the circle, distance
  from centre, rotation about its own axis, height offset. Each LED's x is then the statue's
  angle + atan(sideways offset / distance). The statues must be placed precisely for the
  anamorphic illusion anyway, so these come from the same placement measurements. A
  calibration effect (a vertical line at a slider-set angle, a horizontal line at a set
  height) verifies them by eye from the centre.
**Rejected.**
- *A few numbers per strip (start/end angle, height range):* a strip curving round a hand
  can't be described by its ends (owner's example, 2026-10-09).
- *Reusing WLED's built-in 2D effects by sampling a small virtual grid:* every LED in one cell
  gets the same colour, so a ground-to-sky wash could not light the bottom of a hand before
  its top (owner, 2026-10-09).
- *Calibration through effect sliders:* only 8-bit resolution, stored per preset rather than
  once for the installation, and too few controls.
- *WLED's `ledmap.json` alone:* integer grid of at most 255 cells per side, every empty cell
  costs render time, and it only serves 2D effects. It can still be generated from the same
  geometry for the built-in 2D effects.
- *Field programming tools (MoonLight, Pixelblaze, ARTI-FX):* not needed once nobody
  programs in the field.
**Constrains.** Every LED must be individually addressable, which is why the strips are
chained, not parallel
([../strips_and_power/strip_layout.md](../strips_and_power/strip_layout.md)). It also means a
custom WLED build (PlatformIO) instead of the stock binary from install.wled.me. Whether saved
usermod settings apply without a reboot in WLED 16 is unverified.

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

- **Throughput:** WLED renders ~65–85 k LEDs/s on ESP32; ~4000 LEDs total gives ~18 fps.
  WLED's docs call 4 outputs × 512–800 LEDs the sweet spot; at 8 outputs check frame rate
  early ([kno.wled.ge multi-strip](https://kno.wled.ge/features/multi-strip/)). Target
  ~2000–2500 LEDs total for ~30 fps.
- **About 4 phones max on the AP:** WLED calls `softAP` without `max_connection`, so the ESP32
  default of 4 clients applies (`wled00/wled.cpp`).
- **The web UI is disabled while a realtime stream (DDP/Art-Net/E1.31) is active.**
- **Limits:** preset IDs 1–250; playlists up to 100 entries; `ledmap.json` + `ledmap1…15`.
- **Brightness limiter: 3000 mA per output**, so neither of an output's two strip exits can
  exceed 3 A: [../strips_and_power/led_power_budget.md](../strips_and_power/led_power_budget.md).

## Contents

### Not yet documented

- **WLED configuration backup** — `wled/cfg.json`, `wled/presets.json` (to be created) — the restorable state of the controller; the AP password must be blanked before commit.
- **Spatial mapping (ledmap)** — not built — a 2D `ledmap.json` over all outputs; depends on strip layout (owner open question 2).
- **Geometry usermod and calibration effect** — not built — see *Animations in C++ ahead of time* above.
- **Custom effects** — not built — the installation's own animations, written in C++ as WLED effects.

## Related

- [../controller/gpio_assignment.md](../controller/gpio_assignment.md) — the pins behind the 8 outputs.
- [../field_docs/README.md](../field_docs/README.md) — the operating guide written for this configuration.
