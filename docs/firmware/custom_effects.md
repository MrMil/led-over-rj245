# Custom effects

Path: [docs](../README.md) › [firmware](README.md) › **custom_effects**
Parent: [README.md](README.md)
**Code:** the fork's `wled00/FX.cpp` (the `tower_only` block before `setupEffectData()`, registered at its end) and
`wled00/FX.h` (`FX_MODE_TOWER_ONLY_1` … `_14`, `MODE_COUNT`), [MrMil/WLED](https://github.com/MrMil/WLED/tree/led-over-rj245)
branch `led-over-rj245`, checked out at `../WLED`; previewed through `tools/wled_wasm/` ([effects_in_browser.md](effects_in_browser.md))
**Covers:** the effects written for this installation, beyond stock WLED. Not how effects are previewed
([effects_in_browser.md](effects_in_browser.md)) and not the show itself ([README.md](README.md), *The show*).

## The effects

| WLED id | Name | What it does |
|---|---|---|
| 220–226 | Statue 1 tower 1 only … Statue 1 tower 7 only | That tower alone: red, green, blue, black, one second each. Everything else dark. |
| 227–233 | Statue 2 tower 1 only … Statue 2 tower 7 only | The same for statue 2. |

No sliders, no colours, no palette: the metadata string is `Statue 1 tower 1 only@;;;12`, so the phone shows
nothing to set. The colours are fixed at pure red, green and blue because the check is also a colour-order check: a
strip configured in the wrong order shows the three in the wrong sequence.

## Decisions

### Wiring is checked with per-tower effects, not presets or segments (owner, 2026-10-26)

**Why.** The owner wants to pick a tower by name on the phone and see it alone, to confirm which real tower is on
which jack, with nothing that can break in the field. Stock WLED cannot name an output or switch one off
([README.md](README.md), *Changed 2026-10-26* under preset numbering). The alternatives were all state on the
controller that the show has to undo:
- *Test presets* (agent, 2026-10-10, dropped by the owner 2026-10-26): never built, and *Restore presets* means
  every preset has to travel in `wled/presets.json`.
- *A preset of 14 named segments with per-segment on/off*: rejected by the owner ("something that would break in
  the field"), because the show's presets apply to segment 0 only, so the 14 segments would have to be collapsed
  back to one afterwards or the show runs on one tower.
- *A per-output switch in the LED settings*: does not exist in WLED, and that page is one the crew must not touch.
An effect carries no state: select it, look, select the show again. Fourteen named entries rather than one effect
with a tower slider (owner's request: "14 animations … Statue 1 tower 1 only"), so the crew chooses by name and
sets nothing.
**Constrains.** 14 entries in the effect list; they are at the end (ids 220–233), after stock WLED's 220 slots,
so a stock preset's effect ids are unchanged.

### A tower is an output on the strip, or a column on the 2D map (agent, 2026-10-26)

**Why.** The controller runs either as one logical strip of 14 outputs ([README.md](README.md)) or, with a
`ledmap.json`, as the rolled 14-column matrix the particle effects of the show need. The effect handles both: in 2D
it lights column *t*; in 1D it lights output *t*'s LEDs, read from `BusManager::getBus(t)` at run time, so the LED
counts corrected in LED Preferences on site are the ones used, with no table to keep in step. If output or column
*t* does not exist, nothing lights.
**Constrains.** The simulator has no busses of its own, so it now takes a table of outputs from the page
(`sim_set_bus`, [effects_in_browser.md](effects_in_browser.md)); without it the tower effects show nothing in the
strip layout.

## Adding an effect

Write it in the fork's `FX.cpp` with its metadata string, give it the next id in `FX.h` and raise `MODE_COUNT`,
register it in `setupEffectData()`, then rebuild and sweep ([effects_in_browser.md](effects_in_browser.md),
*Rebuilding*) and commit the new `wled_fx.js` with the change. The fork is its own repository: commit there too,
and note the fork commit in this repository's commit message.

## Related

- [README.md](README.md) — animations are written in C++ ahead of time; the preset numbering and the show.
- [effects_in_browser.md](effects_in_browser.md) — where these effects are previewed and tested.
- [../field_docs/README.md](../field_docs/README.md) — the guide page that tells the crew to use them (`guide/operating.md`, *Check a tower*).
