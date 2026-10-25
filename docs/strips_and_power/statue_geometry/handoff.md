# Layout tool: handoff file, LED calculator, hosting

Path: [docs](../../README.md) › [strips_and_power](../README.md) › [statue_geometry](README.md) › **handoff**
Parent: [README.md](README.md)
**Covers:** the JSON file the tool exports and loads, the LED / reel / supply calculator, and where the page is published.

## The JSON handoff file

**Export / Load** writes `led-over-rj245/statue-layout` version 2 and reads versions 1 and 2
(owner, 2026-10-19: the artist has saved version 1 files, so they must keep loading; a version 1
file simply has no `statue2` and no `free_positions_mm`, which read as "mirrors" and "solved").
Version 2 adds `params.statue2` (null while mirrored), `params.free_positions_mm` (plan x/y per
tower, null while solved), per-statue `level_top_heights_mm` and `leds_power.side_2`. The file
comes back into this repository for the field blueprints and the LED order. It holds
every input under `params` (so a load restores the page exactly), the solved layout under
`layout` (per tower: height, lit length, LEDs per face, `r_mm`, `azimuth_deg`, plan `x_mm`/`y_mm`
with statue 1's apex on +y and azimuth clockwise from it, box yaw, spacing to the next tower,
full-white current) and the per-side and both-sides totals under `leds_power`. Since 2026-10-25 `params.projection.glow` carries the LED glow slider ([pictures.md](pictures.md)),
`params.projection.playlist` the playlist of presets ([../../firmware/effects_in_browser.md](../../firmware/effects_in_browser.md)) and
`params.projection.wled` carries the WLED state of the Animations tab in the
controller's `/json/state` shape (`bri` and one segment), merged key by key on load so older
files keep the defaults ([../../firmware/effects_in_browser.md](../../firmware/effects_in_browser.md)).
Derived values
are ignored on load. The current export lives at `layout/statue-layout.json`; regenerate it
with `?dump=1` (see the Hosting section's headless command in git history, or the dump line in
the page) rather than by hand. **Not done yet:** `tools/wiring_diagrams.py` still carries its own
`TOWER_H`; reading heights from this file is the natural next step once the artist's layout is
final.

## LEDs and power supplies

The **Compute LEDs and power supplies** button (owner, 2026-10-19) takes the current heights and
its own inputs (unlit base per face, LEDs per metre, mA per LED, current ceiling per supply, reel
length; defaults from [led_power_budget.md](../led_power_budget.md): 150 mm, 60/m, 29.4 mA, 18 A,
5 m) and reports per side and for both sides: metres of strip, reels, and supplies.
- **Reels are bin-packed with whole face strips** because every face is cut whole from one reel,
  no joins ([tower_layout.md](../tower_layout.md)); first-fit decreasing, so a 2.6 m tower takes 4
  reels. The both-sides figure also shows what pooling offcuts across the sides would save.
- **Supplies are bin-packed with whole towers**: no tower may be fed by two supplies (owner,
  2026-10-19).
- **Towers sharing a supply are neighbours along the V** (owner, 2026-10-22). The count is the
  fewest runs of consecutive towers in trench order T1 … T7 that each stay under the ceiling, and
  the groups shown are those runs. 5 V cable runs only in the trench along the V; the trench to the
  other statue leaves the apex through the inside of the V; and trenches never cross
  ([trenches.md](../trenches.md)), so a supply can never feed a tower on the far arm.
  **Changed 2026-10-22:** before, the count was the minimum over free pairings and the same-count
  neighbour grouping was only preferred. At the final heights and 18 A that gave 4 supplies per
  statue with T2 + T6 (and T1 + T3, T5 + T7) on one supply, cabled across the V, and the handoff
  file carried that plan.

## Hosting

**Published on GitHub Pages from the `main` branch root** (owner, 2026-10-19: the artist uses
it). `index.html` at the repo root only redirects to `tools/statue_render.html`, and `.nojekyll`
stops Jekyll from processing the site, since nothing here is a Jekyll site and it would only add
build time and surprises. The same file is also published as a private claude.ai artifact; since 2026-10-25 the page loads
`tools/wled_wasm/wled_fx.js` beside it, published as the artifact's supporting file; republish both
together whenever either changes ([../../firmware/effects_in_browser.md](../../firmware/effects_in_browser.md)).
Locally, `.claude/launch.json` serves the repository root on 127.0.0.1:8765 (`python3 -m
http.server`) for Claude Code's preview browser, so agents can open the page, `?load=` the layout
file and run `?dump=1` against it; a bare `file://` page cannot fetch the layout file (agent,
2026-10-23; committed at the owner's request).

## Related

- [README.md](README.md) — the tool.
- [../led_power_budget.md](../led_power_budget.md) — the numbers the calculator uses.
- [../trenches.md](../trenches.md) — why supplies are shared only along the V.
- [../../firmware/effects_in_browser.md](../../firmware/effects_in_browser.md) — the WLED state block in the file.
