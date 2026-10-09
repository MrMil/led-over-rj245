# Strips and power

Path: [docs](../README.md) › **strips_and_power**
Parent: [../README.md](../README.md)

**Covers:** what happens in every box (controller and statue boxes alike) between the PSU,
the data signal and the LED strips: how strips hang off channels, how 5 V is distributed,
the current budget, and the timing cost of shifting data out along a strip.
**Code:** `tools/wiring_diagrams.py` (`power()`, `EXITS`), `guide/img/box-power.svg`, `guide/wiring.md`, `guide/build.md`

## Design

### Decisions

- **The power side is identical in all four boxes** (agent, 2026-10-09). Both enclosure types
  hold the same S-100-5, C14 inlet and four JST-SM LED exits, so one diagram
  (`guide/img/box-power.svg`) and one set of rules serve all of them; only the data source
  differs (74AHCT125 vs MAX485 receivers).
- **LED exits are numbered 1–4 from the end nearest the mains inlet** (agent, 2026-10-09). In
  both enclosures the C14 is at one end of the back-wall stretch that holds the exits
  (enclosure repo, `docs/enclosures/100w.md`, `100w-masterbox.md`), so the rule is the same
  in every box. Exits 1, 2 = channel A; 3, 4 = channel B; exits 1 and 3 carry data.
- **5 V WS2812B — decided** (owner; confirmed 2026-10-09 as a long-standing decision, not
  open). WS2815 (12 V, three LEDs per addressable segment, ~18 mA per pixel, backup data line)
  was considered and not chosen. Do not reopen it on voltage-drop or diffuser grounds without
  the owner.
- **The interface with the statue artist is the connector at each LED exit** (owner,
  2026-10-09). The artist builds the statues and mounts the LEDs and diffusers. Her deliverable
  is a connector per strip; this project supplies 5 V power and data to it and the animations.
  Mounting, diffusion and strip routing on the statue are hers; all of it is powered only through the box's exits. This project needs from her: LED counts per strip, strip order, and LED positions for
  the map ([../firmware/README.md](../firmware/README.md)). The connector spec (JST-SM 3-pin,
  pinout, 3 A per exit) must be agreed with her. Power feeding along the strips and the data
  path between chained strips are the owner's to decide later (owner, 2026-10-09).

## Contents

### Pages

- [`strip_layout.md`](strip_layout.md) — four strips per box, two per channel, chained on the statue; exits 2 and 4 power-only.
- [`power_distribution.md`](power_distribution.md) — PSU terminals → WAGO → LED exits; separate perfboard feed.
- [`led_power_budget.md`](led_power_budget.md) — WS2812B current, PSU sizing rule, injection, the brightness limiter.
- [`shift_out_timing.md`](shift_out_timing.md) — 30 µs per LED, and what it does to effects across statues.

### Not yet documented

- **Physical strip layout per statue** — the artist's scope — this project receives LED counts, strip order and LED positions from her.
- **LED count per statue** — not decided (owner open question).

## Related

- [../controller/local_outputs.md](../controller/local_outputs.md) — the data source in statue 0.
- [../data_link/README.md](../data_link/README.md) — the data source in statues 1–3.
