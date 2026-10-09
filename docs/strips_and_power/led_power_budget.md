# LED power budget

Path: [docs](../README.md) › [strips_and_power](README.md) › **led_power_budget**
Parent: [README.md](README.md)
**Code:** `guide/build.md` (LED Preferences → brightness limiter)
**Covers:** WS2812B current, PSU sizing, voltage drop, and the firmware current cap.

## What it does

| Condition | Current per LED | Power |
|---|---|---|
| Full white (R=G=B=255) | ~60 mA | 0.3 W |
| One channel full | ~20 mA | 0.1 W |
| Idle, data quiet | ~0.6–1 mA | ~0.005 W |

Current scales linearly with PWM duty, so brightness maps almost directly to power. Worst case
is 60 mA × N; typical animated content averages 20–35 % of that (owner).

## Decisions

- **Size the PSU at ~50–60 % of worst case and enforce the cap in firmware** (owner). Sizing for
  full white everywhere wastes weight and money on a case that never happens in a show; the
  firmware cap makes the limit real rather than hoped for.
- **WLED's per-output limit is 3000 mA** (agent, 2026-10-09). Each output's two chained
  strips are powered through two exits rated 3 A each, but WLED limits the output's total,
  not each strip. Only a 3000 mA total guarantees that neither exit exceeds 3 A, whatever the
  content. It may be raised (up to 6000 mA) only if each strip's own full-white draw,
  60 mA × its LED count, is under 3 A, i.e. strips of 50 LEDs or fewer.
  **Consequence:** with longer strips, each statue gets at most 6 A ≈ 30 W, a third of its
  100 W PSU, because the box is the only power source
  ([power_distribution.md](power_distribution.md)). 
  **Changed 2026-10-09:** previously "half the real budget", because parallel strips made
  WLED under-count current by 2×.
- **Inject 5 V and GND at both ends of each strip, and every ~100 LEDs beyond that** (owner).
  At 5 V, visible red-shift starts after ~1.5–2 m of strip. How this is done on the
  statues is the owner's decision, pending LED counts.

## Gotchas

- The S-100-5 (20 A) is the enclosures' assumption, not a sizing result; it must be checked
  once LED counts exist (owner open question 3).

## Related

- [power_distribution.md](power_distribution.md) — where the current flows.
- [README.md](README.md) — the 5 V decision and the artist interface.
