# Strips and power

Path: [docs](../README.md) › **strips_and_power**
Parent: [../README.md](../README.md)

**Covers:** the towers and what feeds them: how a tower's 4 strips hang off its channel, the
tower-base splitter, power from each box to its 7 towers, the current and brightness budget,
and timing.
**Code:** `tools/wiring_diagrams.py` (`power_box()`, `neighbour_base()`, `statue_power()`, `SUPPLIES`, `TOWER_H`), `tools/statue_render.html`, `renders/`, `guide/img/power-box.svg`, `guide/img/neighbour-base.svg`, `guide/img/statue-power.svg`, `guide/wiring.md`, `guide/build.md`

## Design

### Decisions

- **Power is the same at both statues** (agent, 2026-10-10): five supplies per statue fed
  from the apex. One distribution diagram (`guide/img/statue-power.svg`), one power-box
  diagram (`guide/img/power-box.svg`) and one neighbour-base diagram
  (`guide/img/neighbour-base.svg`) serve both.
- **60 LEDs/m — bought** (owner, 2026-10-10). If rendering were too slow, WLED segment
  **Grouping 2** halves effect calculation with every LED still lit. Not needed with one face
  rendered per tower ([tower_layout.md](tower_layout.md)). *Spacing* (every other LED off) was
  rejected: it would look like a gappy 30/m strip.
- **5 V WS2812B — decided** (owner; long-standing). WS2815 (12 V, three LEDs per segment,
  backup data line) was considered and not chosen. Do not reopen it without the owner.
- **The interface with the statue artist** (owner, 2026-10-09/10). The artist builds the
  towers and mounts the strips and diffusers. This project delivers data and power to each
  tower base and the animations. This project needs from her: strip LED counts per face and
  the tower order. The power feeding of the strips is the owner's to design.

## Contents

### Pages

- [`tower_layout.md`](tower_layout.md) — 7 towers per statue, 4 faces per tower, same data on all faces, strips on the central post, no dividers.
- [`statue_geometry/`](statue_geometry/README.md) — where the towers stand in the 18 m circle (the final layout, the 400 / 412 mm box), what the eye at the bench sees, the 3D sightline check (`tools/statue_render.html`, `renders/`).
- [`tower_base.md`](tower_base.md) — tower data splitting: 74AHCT125 in each power box for its own tower; neighbour towers' bases are passive.
- [`power_distribution.md`](power_distribution.md) — five supplies per statue, mains from the apex, JST-SM per strand, XT60 runs to the tip towers, cable types.
- [`trenches.md`](trenches.md) — what runs in each trench segment.
- [`led_power_budget.md`](led_power_budget.md) — current per tower, PSU sizing, brightness estimates, the current cap.
- [`shift_out_timing.md`](shift_out_timing.md) — 30 µs per LED; why it no longer limits anything.

## Related

- [../controller/local_outputs.md](../controller/local_outputs.md) — the data source for statue 1's towers.
- [../data_link/README.md](../data_link/README.md) — the data source for statue 2's towers.
