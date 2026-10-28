# WLED effects in the browser

Path: [docs](../README.md) › [firmware](README.md) › **effects_in_browser**
Parent: [README.md](README.md)
**Code:** `tools/wled_wasm/` (`build.py`, `shim/`, `sim_main.cpp`, `test.js`, the built `wled_fx.js`), `tools/statue_render.html` (the Animations tab, the per-frame scatter to the towers)
**Covers:** running the controller firmware's effect code inside the layout tool's LED render, so animations are developed and judged on the 3D statues before they reach the controller. Not the layout tool itself ([../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md)) and not how effects get into the firmware build ([README.md](README.md), *Animations in C++ ahead of time*).

## What it does

`tools/wled_wasm/build.py` compiles the effect code of the WLED checkout at `../WLED` (the fork and branch the
controller runs, [README.md](README.md)) to WebAssembly with Emscripten and writes one file,
`tools/wled_wasm/wled_fx.js`, which the layout tool loads beside itself. Every effect the firmware registers (220
slots, 212 effects in 16.0.1: the 1D, 2D, audio-reactive and particle-system ones) appears in the Animations tab as
"WLED · name", with the controls its metadata string declares, the firmware's palette list, WLED's sound simulation
for the audio effects, and the segment laid out either as the controller's one logical strip (S1-T1 … S1-T7,
S2-T1 … S2-T7, bottom to top) or as the rolled matrix of 14 columns × the tallest tower
([README.md](README.md)). The page keeps the state in the shape of the controller's `/json/state` and shows it as JSON.

Compiled unchanged from the checkout: `FX.cpp` (every `mode_*` and the effect list), `FXparticleSystem.cpp`,
`palettes.cpp`, `wled_math.cpp`, `fontmanager.cpp`, `fastled_slim.cpp`, and the headers `FX.h`, `const.h`,
`colors.h`. Lifted at build time into `gen/` with their bus, file and JSON plumbing cut away: the Segment half of
`FX_fcn.cpp` (pixel access, blur, fades, palettes, mode defaults), `FX_2Dfcn.cpp` (the 2D drawing helpers),
`colors.cpp`, and from `util.cpp` the metadata parser, the beat generators, the sound simulator, the random helpers
and the Perlin noise. `shim/` stands in for `wled.h`, `Arduino.h` and `fcn_declare.h`; `sim_main.cpp` supplies the
firmware's globals, the strip set-up and one-frame service, and the exported calls.

## Decisions

### The real firmware code, compiled to WebAssembly; not a port (owner, 2026-10-25)

**Why.** The owner asked for the C++ itself, a compiled form, or a middleware form of it, so that animations developed
in the browser are the animations the controller runs. A first attempt (agent, 2026-10-25, same day) wrote a
JavaScript imitation of WLED's Segment API and transcribed "Solid" into it by hand; the owner rejected it: every
further effect would have been another hand transcription, a second implementation to keep in step with the
firmware, which is the thing the sim exists to avoid. Of what exists online (surveyed 2026-10-25),
[Aceftwspades/wled-effects-studio](https://github.com/Aceftwspades/wled-effects-studio) is the one real-C++ route
(Emscripten against a hand-written Segment shim, pinned to the author's own fork); hand ports such as
[wiillownet/wled-fx-sim](https://github.com/wiillownet/wled-fx-sim) cannot run an effect they have not ported; WLED
itself has no effect simulation (Peek streams from the device; issue wled/WLED#2688 was closed "not planned").
**Rejected.** *Reimplementing `Segment` in the shim*, as wled-effects-studio does: the firmware's own `Segment`
(pixel mapping, blur, fades, palette loading, `setMode` defaults) is what the effects are tuned against, so the
build lifts the real `Segment` methods out of `FX_fcn.cpp` and uses the real `FX.h`, and stubs only the busses,
files and JSON that have nothing to do with how an effect looks. *The hand-written JavaScript shim*: deleted the
same day; nothing of it remains.
**Constrains.** The page talks to the module through a fixed contract (`sim_init`, `sim_set_mode`, `sim_set`,
`sim_set_color`, `sim_set_bus`, `sim_frame`, `sim_mode_data`, `sim_palette_names`, …, `sim_main.cpp`). A new effect for the
installation is written in the fork's `FX.cpp`, registered in `setupEffectData()`, and appears in the page after
`python3 tools/wled_wasm/build.py`; nothing in the page is edited per effect. The built `wled_fx.js` is committed,
because the page is published as it is (GitHub Pages, a file on the owner's machine, the claude.ai artifact) and
none of those can build it; rebuild it whenever the fork's effects change.

- **Emscripten runs from the `emscripten/emsdk` Docker image, not an install** (owner, 2026-10-25: "you have
  docker"). `build.py` uses `em++` from the PATH when there is one and the image otherwise, mounting the common
  parent of this repository and the WLED checkout. Nothing is installed on the machine.
- **The real headers are masked with their own include guards** (agent, 2026-10-25). A quoted `#include "wled.h"`
  inside the checkout's files resolves to the real `wled00/wled.h` before any include path, so the shim defines
  `WLED_H` (and `WLED_FCN_DECLARE_H`) and is force-included ahead of every source; the real headers then compile to
  nothing. This keeps the checkout untouched and the firmware's `FX.h`, `const.h` and `colors.h` in use as they are.
- **One file, the wasm embedded (`SINGLE_FILE`)** (agent, 2026-10-25): a browser refuses `fetch()` of a `.wasm`
  from a `file://` page, and the owner opens the layout tool as a file. The module also runs under Node for
  `test.js`. Cost: 240 KB in one script instead of 220 KB in two.
- **Objects are cached in `tools/wled_wasm/build/` and `gen/` is regenerated; both are git-ignored** (agent,
  2026-10-25). `gen/` is the checkout's code with cuts, reproducible from it; `build/` is a compile cache so an
  edit to `sim_main.cpp` does not recompile the 11 000-line `FX.cpp`.
- **The segment is laid out by the page as strip or matrix, automatically by the effect's flags** (agent,
  2026-10-25). WLED's effect flags (`;;!;2` 2D-only, `1` 1D, `12` either) decide: a 2D-only effect gets the
  14 × tallest matrix (what a `ledmap.json` with one column per tower would give the firmware,
  [README.md](README.md)), everything else the controller's strip; the "Segment" select overrides. WLED's matrix
  has row 0 at the top, so LED *i* of tower *x* is pixel (*x*, H − 1 − *i*); the firmware drops nothing for short
  towers because the page reads the segment's own buffer and only copies the LEDs that exist.
- **Effect defaults are applied by the firmware and read back** (agent, 2026-10-25): selecting an effect, and the
  "Restore effect defaults" button, call `Segment::setMode(fx, true)` in the module, the same code the controller
  runs when a preset names an effect, and the page copies the resulting sliders, checkboxes and palette into its
  state. One addition to the firmware's rule (owner, 2026-10-25: the button must restore the palette too): an
  effect whose string names no `pal=` default goes back to "Default", which the firmware resolves to the effect's
  own palette; the controller would keep whatever palette was set. Colours are left alone, as on the controller.
- **The palette list shows the colours** (owner, 2026-10-25): a gradient swatch under the list, the 16 entries as
  `Segment::loadPalette()` loads them for the current effect, and the "Default" entry names what it resolves to
  (`Default (Aurora)`), from the same rule `setMode` uses. Both come from the module (`sim_palette`,
  `sim_default_palette` in `sim_main.cpp`), not from a copy of the tables.
- **The sim's state is the controller's `/json/state` shape, saved as `params.projection.wled` in the handoff
  JSON** (agent, 2026-10-25; [../strips_and_power/statue_geometry/handoff.md](../strips_and_power/statue_geometry/handoff.md)):
  `bri` and one segment (`fx, sx, ix, c1, c2, c3, o1–o3, col, pal, si`), plus the page's own `layout`. What the sim
  shows can be posted to the controller as it is, and a preset from the controller pasted into the sim. Loading
  merges key by key so a file from before a key existed keeps the default. Master brightness defaults to 255
  (WLED's own default is 128) because the render is judged at full scale; the `Diffuser brightness` gain is the
  calibration knob.
- **Controls are generated from the metadata string with the rules of WLED's own UI** (`setEffectParameters` in
  `wled00/data/index.js`, replicated in the page; agent, 2026-10-25), so an effect shows exactly the sliders,
  checkboxes, colour slots and palette it shows on a phone. Colour slots use the browser's native colour picker:
  no dependency, and the value is the `[r, g, b]` the controller takes.
- **Transitions are off, the random source is seeded, the busses are a table** (agent, 2026-10-25). The strip's
  transition time is 0, so a change shows on the next frame as a preset does; `hw_random` is a seeded xorshift so
  a run can be repeated; gamma at the output, segment grouping and mirroring across busses, and the
  `Copy Segment` effect's second segment do not exist. **Changed 2026-10-26:** busses used to be absent; now the
  page hands the module one output per tower with its LED count (`sim_set_bus`), starts following in order as on
  the controller, because the tower-only effects ([custom_effects.md](custom_effects.md)) find their tower through
  `BusManager::getBus()` and must find the same one here. Nothing else about a bus (type, pin, colour order) exists. `WLED_FS` is empty, so only the built-in fonts of
  Scrolling Text work. The audio effects get the firmware's own `simulateSound()`; there is no microphone.
- **`test.js` sweeps every effect** (agent, 2026-10-25): both layouts, the installation's LED counts, a few seconds
  of frames each; it fails on a trap and lists effects that stayed dark. Run it after a rebuild. 2026-10-25: 365
  runs, no traps.

## Playlists and presets.json

The Animations tab keeps a playlist: the current effect with its settings is added as an entry, each entry has a
name, a duration and a transition in seconds, the list plays in order in the sim, and it exports as the
controller's `presets.json` (owner, 2026-10-25: "the user can change the animation parameters and then add them to
the playlist, we can then export the playlist as json from the browser and upload them to the real WLED").

- **The export is the firmware's own file, not a format of ours** (agent, 2026-10-25): one preset per entry
  (`n, on, bri, transition, mainseg, seg:[{id:0, on, col, fx, sx, ix, pal, c1, c2, c3, o1–o3, si}]`, as
  `wled00/presets.cpp` writes them) and the playlist as the next preset (`playlist:{ps, dur, transition, repeat:0,
  end:0, r:false}`, times in tenths of a second, as `wled00/playlist.cpp` reads them). It goes onto the controller
  with Config → Security & Updates → Restore presets, which replaces every preset there; the same file loads back
  into the page, so the controller's presets can be brought to the sim.
- **Entries are numbered from a chosen first preset, 10 by default, and the playlist preset follows them**:
  10–99 is the workshop range of the preset-numbering decision in [README.md](README.md), and the boot preset the
  crew needs is then one known number, the last one.
- **The segment of a preset carries no bounds** (`start`/`stop` left out), so it applies to whatever segment the
  controller is configured with; the sim's strip-or-matrix choice is not exported, because on the controller it is
  the LED map's business ([README.md](README.md)).
- **Previous / Next while playing, and "From here" on every entry** (owner, 2026-10-26): playback is a clock
  offset into the loop, so a jump only moves the clock to the entry's start; the entry then runs its full duration.
- **A caret on every entry unfolds its parameters** (owner, 2026-10-26), named as the controls name them, with the
  palette resolved and the colours as swatches; the fold state is per page load, not saved.
- **The sim cuts hard between entries; the controller cross-fades** over the transition time. The firmware's
  cross-fade runs the old effect alongside the new one in `WS2812FX::service()`'s blending, which the sim does not
  compile; the durations and the order are what a playlist is judged on.
- **The show is the default playlist** (owner, 2026-10-28: "add the playlist to the default settings as well"):
  a page whose playlist is still empty after the browser store and `?load=` were applied fetches
  `wled/presets.json` next to itself and loads it as the Load button would, so the sim opens playing the show
  when the repository is served (GitHub Pages or a local server) and empty as a bare file, like the default
  pictures ([../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md)).
  `layout/statue-layout.json` carries the same playlist, read from the page after loading that file, so the
  handoff file and the page defaults agree. Change the show in `wled/presets.json`, then put it into the handoff file
  the same way (`?load=../layout/statue-layout.json&dump=1` after clearing the file's playlist, or Load then Export).
- **The playlist travels in the browser store and in the handoff JSON** (`params.projection.playlist`,
  [../strips_and_power/statue_geometry/handoff.md](../strips_and_power/statue_geometry/handoff.md)) so it survives
  a reload; `presets.json` is the record that leaves the page.

## Gotchas

- **The segment's light capabilities must be refreshed after it is created** (`refreshLightCapabilities()` in
  `finalizeInit()`, `sim_main.cpp`). The firmware does it from its bus list in `setGeometry()`; the sim creates its
  segment directly, and without the call `_isRGB` stays false and `color_from_palette()` returns the segment colour
  for every palette. Until 2026-10-25 every effect that takes its colours from the palette (Aurora, Pacifica, the
  noise effects, …) showed orange in the sim; the owner noticed on Aurora.
- **"Default" in the palette list is the firmware's rule, not a palette**: with palette 0 an effect asking for one
  of the three colour slots gets that colour, and an effect asking for the palette gets its own `pal=` default
  (Party when it has none). Selecting an effect loads its `pal=` default into the list, as the phone does.

## Licence

WLED is EUPL-1.2 and `wled_fx.js` is compiled from it, so the built file is a derivative distributed by this
public repository; the source is the fork linked from [README.md](README.md). No licence file is added for this
one-off project (owner, 2026-10-25); do not propose one.

## Rebuilding

**The agent rebuilds the module; the owner does not** (owner, 2026-10-25). Whenever an effect in the fork's
`FX.cpp` changes, or the fork is updated, run both and commit the new `wled_fx.js` with the change that caused it:

```
python3 tools/wled_wasm/build.py      # needs ../WLED (or WLED_ROOT) and Docker or em++
node tools/wled_wasm/test.js          # every effect, both layouts
```

The claude.ai artifact copy of the page carries `wled_wasm/wled_fx.js` as a supporting file and is republished
with it (owner, 2026-10-25).

## Related

- [README.md](README.md) — animations are written in C++ ahead of time; this page is the preview of that work.
- [parallel_i2s_bus.md](parallel_i2s_bus.md) — the other half of the custom build, which the sim does not touch.
- [custom_effects.md](custom_effects.md) — the installation's own effects, previewed and tested here.
- [../strips_and_power/statue_geometry/pictures.md](../strips_and_power/statue_geometry/pictures.md) — the LED render and the page's own show registry the WLED entries sit beside.
- [../strips_and_power/statue_geometry/handoff.md](../strips_and_power/statue_geometry/handoff.md) — where the WLED state travels in the JSON file.
