# Documentation Hub

**Audience: LLM coding agents working in this repository. Not human onboarding material.**
Optimise for a reader with no memory of previous sessions, who can read files fast, and who needs
to know *why* the code is the way it is before changing it.

This tree mirrors the system as a recursive hub-and-spoke: every directory is a part of the system,
its `README.md` indexes what is inside it, and the nesting goes as deep as the system does. Each
page explains its piece and records the reason behind every choice made there. The code is the
source of truth for what happens. These docs are the source of truth for why.

## How to use this tree

1. Start here and navigate down, one index at a time, to the page covering what you are about to change. Never guess paths.
2. **Read every `README.md` on the way down.** Decisions recorded at a level apply to everything beneath it. The reason a leaf behaves as it does may be recorded two levels up.
3. Before finishing work, run the documentation pass in [CONVENTIONS.md](CONVENTIONS.md#the-documentation-pass).

## Design

The system: **two statues** in an 8 m circle at Midburn (Negev desert), each a V of 7 towers
(500–2000 mm tall, 40 × 40 cm, CNC-cut faces with a diffuser behind, a structural post in the
middle). WS2812B 60/m strips inside, 4 per tower (one per face, on the post, facing out), run
one show from one controller. Outdoors for the event: dust,
40 °C+ days, near-freezing nights, generator power, heavy 2.4 GHz congestion, Leave No Trace.
This repository holds the electronics, firmware configuration, wiring diagrams and the field
documentation; the enclosures live in another repository (below).

**The artwork is a mural** (owner, 2026-10-09/10). The CNC cuts on the tower faces form a
picture when viewed from the centre; tower edges fall in the middle of the picture. **The
shapes come from the cuts, not from the LEDs**; the LEDs light the faces from behind. People
look from all angles, so every face is lit. All 4 faces of a tower show the same pixels.
The animation is a rolled 2D map: x = tower, y = height ([firmware/](firmware/README.md)).

**Status: the two-statue layout is pending Midburn approval** (owner, 2026-10-10). The
approved design has **four statues** of 7 towers. Art pieces above a certain size need
approval from the Midburn authorities, and the change to two statues (3 weeks before the event,
for less work) has been requested but not granted. This tree describes the two-statue
variant because the owner asked for it. Do not treat it as final.
**If it stays at four statues:** 28 towers with one channel each would need 28 outputs. One
ESP32 in WLED tops out at 16 (8 RMT + 8 I2S), so towers would have to share channels, or the
single-controller decision would have to be revisited. Earlier four-statue design: four
statues star-wired from a controller at statue 0, two channels each over one CAT5e per statue
(see git history before 2026-10-10).

Most of the design is hardware, so "code" paths below are often diagrams
(`tools/wiring_diagrams.py`) or human guide pages (`guide/`).

### Decisions

- **The design record is a design conversation summarised by the owner (2026-10-09).** Reasons
  in this tree marked "(owner)" come from it; reasons marked "(agent, date)" were chosen by an
  agent and have not been confirmed by the owner — treat them as reversible.
- **Enclosures are designed in [MrMil/electronics-enclosure](https://github.com/MrMil/electronics-enclosure)**
  (checked out locally at `../electronics-enclosure`), not here: `100W-masterbox` for both
  boxes (owner, 2026-10-10; each needs 7 tower data + 7 tower power outputs, enclosure change
  pending). This repo only consumes their geometry —
  wall positions of jacks and tower outputs. Do not copy enclosure decisions here; link to them.
- **Power stays local; only data crosses between statues** (owner). Each box has its own
  mains-fed 5 V PSU feeding its 7 towers. Sending 5 V at LED currents between statues would
  need heavy cable and still drop volts; data needs three CAT5e cables.
- **Grounds are common across both boxes**, via pins 7/8 of each CAT5e (owner). See
  [data_link/](data_link/README.md) for why the receiver needs it.
- **Human documentation is separate from this tree** (owner, 2026-10-09): `README.md` and
  `guide/` are for the field crew, who will build and run the installation without the owner
  present, reading on a phone on GitHub. See [field_docs/](field_docs/README.md).

### One controller, no synchronisation

**Why.** One ESP32 can drive every tower of both statues directly (owner; reconfirmed
2026-10-10 for the two-statue layout: "2 controllers give us a synchronisation problem and
that's the big reason we did the cat5"). One
controller means one clock, one framebuffer and one render loop, so the statues are
frame-perfect by construction: no drift, no clock discipline, no cue protocol, no failure modes
from nodes disagreeing. Distributing controllers would *create* a synchronisation problem that
otherwise does not exist.
**Rejected** (owner; all for an architecture with one ESP32 per statue):
- *One ESP32 per statue + wireless sync.* Right at 80 m, or if statues had to run standalone;
  neither applies.
- *Clock sync over WiFi/ESP-NOW with future-scheduled cues.* Correct technique (shared clock
  not low latency; schedule cues ~500 ms ahead so jitter is irrelevant), 0.5–2 ms accuracy, but
  2.4 GHz at a burn is effectively unusable and it needs resync every 20–30 s.
- *GPS PPS discipline per statue* (u-blox NEO-M8N, <100 ns, slow PI loop on the 40 MHz XTAL).
  Robust and radio-free; unnecessary once there is one controller. Note for any revisit: the
  ESP32's bad drift reputation belongs to the 150 kHz RTC RC oscillator, not the main XTAL;
  the outdoor enemy is temperature coefficient (±10–20 ppm across a desert day).
- *DS3231 TCXO + radio phase sync.* Fixes rate but not phase, so still needs radio; GPS gives
  phase for the same cost.
- *A wired 60 Hz frame clock on a dedicated pair* with RS-485 frame numbers. Sub-µs, trivial
  code — rejected only because at 8 m the LED data itself fits down the cable, deleting three
  ESP32s. **Revisit this first if the installation ever grows in distance.**
**Constrains.** One output per tower means 14 outputs, beyond the ESP32's 8 RMT channels:
WLED 16's RMT + I2S mix must carry it (bench test pending; fallback 12 channels by sharing
two towers' channels). Frame rate is bounded by render throughput
([firmware/](firmware/README.md)). The controller is a single point of
failure — mitigated by a pre-flashed spare ESP32 in a socket ([controller/](controller/README.md)).

### Open questions

0. **Two or four statues**: awaiting Midburn approval (owner, 2026-10-10).
1. **14 outputs on one ESP32 in WLED 16**: bench test pending (owner, 2026-10-10).
2. ~~PSU size per statue~~ — decided 2026-10-10: 5 × S-100-5 per statue; strand-to-PSU
   grouping proposed in [strips_and_power/led_power_budget.md](strips_and_power/led_power_budget.md).
3. ~~Tower power wiring~~ — decided 2026-10-10: see
   [strips_and_power/power_distribution.md](strips_and_power/power_distribution.md). Pending: the
   enclosure repo's `100W` box with XT60 outputs, and the strip voltage-drop measurement.
4. **Tower order and heights** T1–T7 were read off the model photo; confirm on site.
5. **Distance between the statues**: sets whether 10 m CAT5e reaches.

## Areas

- [`controller/`](controller/README.md) — the ESP32 box at statue 1: GPIO map, statue 1's tower outputs, transmitters for statue 2, logic power.
- [`data_link/`](data_link/README.md) — RS-485 over 3 buried CAT5e cables to box 2: transceivers, cabling, termination and bias.
- [`strips_and_power/`](strips_and_power/README.md) — towers, strips and power: tower layout, tower-base splitter, power distribution, current budget, timing.
- [`firmware/`](firmware/README.md) — WLED on the controller: configuration, logical LED order, presets, animation authoring.
- [`field_docs/`](field_docs/README.md) — the human guide (`README.md`, `guide/`) and the generated wiring diagrams.

## Files

- [CONVENTIONS.md](CONVENTIONS.md) — the rules for writing and maintaining these docs. Read before adding anything here.

## Invariants

These hold at every depth. If you find one broken, fix it before continuing your task.

- Every directory under `docs/` contains a `README.md` listing every subdirectory and every `.md` file beside it, each with a one-line description.
- Every page and every index links to its parent, carries its breadcrumb path, and links to at least one related page.
- No statement of a design choice appears anywhere in this tree without its reason.
- Every decision is recorded at the lowest level that contains everything it governs.
- No code change ships without the corresponding documentation change in the same commit.
