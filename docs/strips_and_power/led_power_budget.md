# LED power budget

Path: [docs](../README.md) › [strips_and_power](README.md) › **led_power_budget**
Parent: [README.md](README.md)
**Code:** `guide/build.md` (LED Preferences → current), firmware current ceiling (not built)
**Covers:** current per tower, per supply and per statue, and the cap.

## What it does

WS2812B datasheet (Worldsemi): **12 mA per channel, so 36 mA per LED at full white**. Some
datasheet revisions give 16 mA (48 mA per LED). Typical animated content is ~30 % of that,
plus ~1 mA idle. Per statue at 60/m, 1656 LEDs:

| Tower | LEDs (4 faces) | Worst, 36 mA | Worst, 48 mA |
|---|---|---|---|
| 2000 | 444 | 16.0 A | 21.3 A |
| 1550 | 336 | 12.1 A | 16.1 A |
| 1150 (×2) | 240 each | 8.6 A | 11.5 A |
| 800 (×2) | 156 each | 5.6 A | 7.5 A |
| 500 | 84 | 3.0 A | 4.0 A |
| **Statue** | **1656** | **59.6 A · 298 W** | **79.5 A · 397 W** |

Typical content: ~20–26 A per statue. Whole installation from the wall (both statues, ~85 %
PSU efficiency): ~700–935 W worst case, inside the 1.5 kW generator budget (owner, 2026-10-10).

## Decisions

- **LED current from the datasheet, not a rule of thumb** (owner, 2026-10-10: "this is
  ws2812b. check the data sheet").
  **Changed 2026-10-10:** previously 60 mA per LED (20 mA per channel, from the original
  design notes), which overstated every current here by 25–40 %.
- **Five S-100-5 (100 W) per statue** (owner, 2026-10-10). Three per statue would already be
  extra work, and five is marginally more. With datasheet currents, 500 W per statue covers
  the worst case with margin.
- **Every strand (one face's strip) has its own XT60 at its start** (owner, 2026-10-10).
- **Supply grouping** (see [power_distribution.md](power_distribution.md)), worst case at
  full white, 15 cm base:

  | Supply | Feeds | 36 mA | 48 mA |
  |---|---|---|---|
  | A | T1 + T2 | 14.3 A | 19.0 A |
  | B | T3 | 12.1 A | 16.1 A |
  | C | T4 faces 1–2 | 8.0 A | 10.7 A |
  | D | T4 faces 3–4 + T5 faces 1–2 | 12.3 A | 16.4 A |
  | E | T5 faces 3–4 + T6 + T7 | 13.0 A | 17.3 A |

  Firmware ceiling **18 A per supply** (90 % of rating). At 36 mA no supply reaches it, even
  at full white. At 48 mA only supply A would, at full white, by ~5 %. The limiter then scales
  the whole frame evenly. Each strand draws exactly a quarter of its tower, because all faces
  show the same pixels, so each supply's load follows directly from the frame.
- **Voltage drop: the 2000 mm strands may need a second feed** (agent estimate, 2026-10-10).
  Fed at the bottom only, at full white, a 1.85 m strand (4.0–5.3 A) drops ~0.45–1.2 V, given
  strip copper of ~0.12–0.24 Ω/m round trip. The 1400 mm strands drop ~0.25–0.7 V; shorter
  ones less. Measure the bought strip to decide (see `TODO.md`).
- **Size PSUs at 80–90 % of rating** (agent, 2026-10-10). Generic S-series clones run
  continuously inside a closed box.
- **WLED's current estimate is corrected 4×** (agent, 2026-10-10). Each output is configured
  with one face's LEDs while four faces draw. Set WLED's custom LED current to 4 × 36 mA =
  144 mA.
- **The cap cannot be raised from the UI** (owner, 2026-10-10): firmware ceiling, see
  [../firmware/README.md](../firmware/README.md).
- **Overall brightness is set in WLED, not decided by a mock-up** (owner, 2026-10-10). If
  it's too bright, turn it down.

## Related

- [power_distribution.md](power_distribution.md) — where the current flows.
- [tower_layout.md](tower_layout.md) — LED counts per tower.
- [statue_geometry.md](statue_geometry.md) — the LED/reel/supply calculator in `tools/statue_render.html`, which uses these numbers.
