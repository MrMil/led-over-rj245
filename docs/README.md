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

The system: four statues in an 8 m circle at Midburn (Negev desert), WS2812B strips on each,
running one show with effects that travel between statues. Outdoors for the event: dust,
40 °C+ days, near-freezing nights, generator power, heavy 2.4 GHz congestion, Leave No Trace.
This repository holds the electronics, firmware configuration, wiring diagrams and the field
documentation; the enclosures live in another repository (below).

**The artwork is anamorphic** (owner, 2026-10-09). From outside, the circle looks like nothing.
Standing at its centre, the viewer sees the statues' forms resolve into human figures in
different poses (e.g. a person making the om hand gesture). **The shapes come from the
sculpture, not from the LEDs.** The LEDs sit on the parts that make up each figure. The
animation is a 2D image wrapped around the viewer, and each LED shows the colour of the point
in that image where the LED appears from the centre, like projection mapping with LEDs as the
projector's pixels. What matters for every LED is therefore its **direction as seen from the
centre** (azimuth around the circle, elevation), not its 3D position. This drives the mapping
and calibration design in [firmware/](firmware/README.md).
The statues' detailed needs are still being worked out with the statue builders.

Most of the design is hardware, so "code" paths below are often diagrams
(`tools/wiring_diagrams.py`) or human guide pages (`guide/`).

### Decisions

- **The design record is a design conversation summarised by the owner (2026-10-09).** Reasons
  in this tree marked "(owner)" come from it; reasons marked "(agent, date)" were chosen by an
  agent and have not been confirmed by the owner — treat them as reversible.
- **Enclosures are designed in [MrMil/electronics-enclosure](https://github.com/MrMil/electronics-enclosure)**
  (checked out locally at `../electronics-enclosure`), not here: `100W-masterbox` for the
  controller, `100W-rj45` for statues 1–3 (owner). This repo only consumes their geometry —
  wall positions of jacks and LED exits. Do not copy enclosure decisions here; link to them.
- **Power stays local; only data crosses between statues** (owner). Each box has its own
  mains-fed 5 V PSU. Sending 5 V at LED currents over 8–10 m would need heavy cable and still
  drop volts; data needs one CAT5e cable.
- **Grounds are common across all four boxes**, via the spare CAT5e conductors (owner). See
  [data_link/](data_link/README.md) for why the receiver needs it.
- **Human documentation is separate from this tree** (owner, 2026-10-09): `README.md` and
  `guide/` are for the field crew, who will build and run the installation without the owner
  present, reading on a phone on GitHub. See [field_docs/](field_docs/README.md).

### One controller, no synchronisation

**Why.** At 8 m, one ESP32 can drive every strip of all four statues directly (owner). One
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
**Constrains.** Total LED count and frame rate are bounded by one ESP32's 8 outputs and
render throughput ([firmware/](firmware/README.md)). The controller is a single point of
failure — mitigated by a pre-flashed spare ESP32 in a socket ([controller/](controller/README.md)).

### Open questions (owner, not yet decided)

1. LED count per statue — drives PSU load, frame rate, shift-out compensation, and whether 2
   channels per statue suffice.
2. ~~Physical strip layout per statue~~ — the statue artist's scope; this project receives LED
   counts, strip order and positions from her ([strips_and_power/](strips_and_power/README.md)).
3. PSU sizing per statue once counts are known (the enclosures assume S-100-5, 5 V 20 A).
4. ~~How artists author animations in the field~~ — decided 2026-10-09: C++ WLED effects
   written ahead of time, with only parameters and geometry calibration changed in the field
   ([firmware/](firmware/README.md)).

## Areas

- [`controller/`](controller/README.md) — the ESP32 box at statue 0: GPIO map, local strip outputs, transmitters, logic power.
- [`data_link/`](data_link/README.md) — RS-485 over buried CAT5e to statues 1–3: transceivers, cabling, termination and bias.
- [`strips_and_power/`](strips_and_power/README.md) — what every box does with 5 V and LED data: strip arrangement, power distribution, current budget, shift-out timing.
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
