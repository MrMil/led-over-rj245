# LED power budget

Path: [docs](../README.md) › [strips_and_power](README.md) › **led_power_budget**
Parent: [README.md](README.md)
**Code:** `guide/build.md` (LED Preferences → current), firmware current ceiling (not built)
**Covers:** current per tower, per supply and per statue, and the cap.

## What it does

**Measured on the bought strip: 29.4 mA per LED at full white, 0.5 mA idle** (owner,
2026-10-18). Method: a 5 m reel (300 LEDs) on a lab supply at 5.0 V, driven from MicroPython
`neopixel` with `(255, 255, 255)` (no global brightness). All off: 0.14–0.15 A. First 60 LEDs
white: 1.87–1.89 A. (1.88 − 0.145) / 60 + 0.145 / 300 = 29.4 mA. Typical animated content is
~30 % of full white, plus idle. Per statue at 60/m, 2244 LEDs (final heights, 2026-10-21):

| Tower | LEDs per face | Strand (one face), full white | LEDs (4 faces) | Tower, full white | Tower, typical |
|---|---|---|---|---|---|
| 2000 | 111 | 3.3 A | 444 | 13.1 A | 4.1 A |
| 1700 (×2) | 93 | 2.7 A | 372 each | 10.9 A | 3.5 A |
| 1400 (×2) | 75 | 2.2 A | 300 each | 8.8 A | 2.8 A |
| 1100 (×2) | 57 | 1.7 A | 228 each | 6.7 A | 2.1 A |
| **Statue** | | | **2244** | **66.0 A · 330 W** | **20.9 A · 104 W** |

Typical = ~30 % of full white + 0.5 mA idle per LED (≈ 9.3 mA per LED). All off: ~1.0 A per
statue. Whole installation from the wall (both statues, ~85 %
PSU efficiency): ~575 W worst case, inside the 1.5 kW generator budget (owner, 2026-10-10).

## Decisions

- **LED current measured, not estimated** (owner, 2026-10-18). The strips are unbranded
  WS2812B and the label gives no current.
  **Changed 2026-10-18:** previously 36–48 mA from a web-search summary of WS2812B datasheets
  that was never checked against the primary document. Before that (2026-10-10), 60 mA from
  the original design notes.
- **Five S-100-5 (100 W) per statue** (owner, 2026-10-18). 500 W per statue against a 302 W
  worst case.
- **Every strand (one face's strip) has its own XT60 at its start** (owner, 2026-10-10).
- **Supply grouping** (see [power_distribution.md](power_distribution.md)), worst case at
  full white, 15 cm base:

  | Supply | Feeds | Worst case |
  |---|---|---|
  | A | T1 + T2 (1100 + 1400) | 15.5 A |
  | B | T3 (1700) | 10.9 A |
  | C | T4 (2000) | 13.1 A |
  | D | T5 (1700) | 10.9 A |
  | E | T6 + T7 (1400 + 1100) | 15.5 A |

  Firmware ceiling **18 A per supply** (90 % of rating). No supply reaches it, even at full
  white. If one ever did, the limiter would scale the whole frame evenly.
- **Voltage drop: the 2000 mm strands may need a second feed** (agent estimate, 2026-10-10).
  Fed at the bottom only, at full white, a 1.85 m strand (3.3 A) drops ~0.35–0.7 V, given
  strip copper of ~0.12–0.24 Ω/m round trip. The 1700 mm towers' strands (1.55 m, 2.7 A) drop
  ~0.25–0.5 V; shorter ones less. Measure the bought strip to decide (see `TODO.md`).
- **Size PSUs at 80–90 % of rating** (agent, 2026-10-10). Generic S-series clones run
  continuously inside a closed box.
- **WLED's current estimate is corrected 4×** (agent, 2026-10-10). Each output is configured
  with one face's LEDs while four faces draw. Set WLED's custom LED current to 4 × 29.4 mA ≈
  118 mA.
- **The cap cannot be raised from the UI** (owner, 2026-10-10): firmware ceiling, see
  [../firmware/README.md](../firmware/README.md).
- **Overall brightness is set in WLED, not decided by a mock-up** (owner, 2026-10-10). If
  it's too bright, turn it down.

## Related

- [power_distribution.md](power_distribution.md) — where the current flows.
- [tower_layout.md](tower_layout.md) — LED counts per tower.
- [statue_geometry.md](statue_geometry.md) — the LED/reel/supply calculator in `tools/statue_render.html`, which uses these numbers.
