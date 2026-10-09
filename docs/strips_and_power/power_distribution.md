# Power distribution

Path: [docs](../README.md) › [strips_and_power](README.md) › **power_distribution**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`power()`), `guide/img/box-power.svg`, `guide/wiring.md` (Power)
**Covers:** wiring from the C14 inlet through the S-100-5 to the LED exits and the perfboard.

## What it does

C14 L/N/PE → PSU terminals 1/2/3. PSU terminal 4 (−V) → a WAGO 221-415 → the GND wire of
all four exits; terminal 6 (+V) → a second WAGO → the 5 V wire of all four exits, both on
1.5 mm². Terminals 5 (−V) and 7 (+V) → perfboard GND and +5V rails on 0.5 mm².

## Decisions

- **Strip current never flows through the perfboard** (agent, 2026-10-09). Up to 12 A (4 exits ×
  3 A) would go through breadboard-pattern perfboard copper, which is rated for roughly
  1–2 A. Only the DATA wire of each exit lands on the perfboard.
- **WAGO 221-415 lever connectors as the 5 V and GND distribution** (agent, 2026-10-09). The
  S-100-5 has only two +V and two −V screw terminals; four exits plus a perfboard feed would
  put three wires under one screw. A 5-way lever connector takes one feed and four exit
  wires per polarity, is rated well above 12 A, and lets the field crew re-seat an exit
  without a screwdriver.
- **Perfboard fed from the PSU's second terminal pair, not from the WAGOs** (agent,
  2026-10-09). It keeps the logic feed on its own screw terminal, so disturbing the strip
  wiring cannot disconnect the logic, and the WAGOs keep exactly five ports' worth of wires.
- **Each JST-SM exit is limited to 3 A** (enclosure repo: 3 A per contact; the four exits
  carry at most 12 A of the PSU's 20 A).
- **The box is the statue's only power source** (owner, 2026-10-09). Everything the statue's
  LEDs draw comes through its four exits. There is no supply on the artist's side. How power is fed
  along the strips is the owner's decision, to be made from the LED counts.
- **Mains colours brown L, blue N, green/yellow PE** — IEC colours, which Israel uses.
- **C14 fuse 1 A on the AC side** (owner, 2026-10-09): ~240 W of input, well above the
  S-100-5's 100 W. The PSU has its own internal fuse and over-temperature trip, so a fault or
  overheating trips the PSU, not the inlet fuse. The C14 fuse is a backstop for wiring faults
  between inlet and PSU.

## Gotchas

- JST-SM pigtail wire colours vary by supplier (red/green/white is common, with green as
  DATA); the guide tells builders to identify 5 V/DATA/GND with a meter.
- A switching PSU draws a large inrush current at switch-on; if 1 A inlet fuses blow at
  power-up, they are fast-acting and need to be time-delay (T1A).

## Related

- [led_power_budget.md](led_power_budget.md) — how much current there will be.
- [../controller/README.md](../controller/README.md) — the logic load on the perfboard feed in the controller box.
