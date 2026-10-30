# Tower data splitting

Path: [docs](../README.md) › [strips_and_power](README.md) › **tower_base**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`power_box(two)`, `tip_tower_cable()`), `guide/img/power-box-1-tower.svg`, `guide/img/power-box-2-tower.svg`, `guide/img/tip-tower-cable.svg`, `guide/wiring.md`
**Covers:** how each tower's one data line reaches its 4 strands: in the power box for a box's
own tower, passively at the end of the tip-tower cable for a tip tower.

## What it does

- **The board** is the same in all ten power boxes (T4's inside the master/slave box): one
  74AHCT125, gates 1 and 2 each with 560 Ω from the input to GND and 100 Ω on the output,
  gates 3 and 4 with their inputs to GND. The two kinds of box differ only in which
  connectors are fitted to gate 2. Boards built before 2026-10-31 have 10 kΩ on the inputs
  with a 560 Ω soldered across it (530 Ω; below).
- **Own tower** (T2–T6). The tower's data line enters the power box on a JST-SM
  (DATA + GND; the 5V pin is not connected), onto gate 1's 560 Ω and input. The output
  goes through its 100 Ω and is then joined to the DATA leads of the 4 JST-SM out (5V, DATA,
  GND), one per strand.
- **Tip tower** (T1 from the power box in T2; T7 from the one in T6). Its data line enters the power box on its
  own JST-SM onto gate 2's 560 Ω and input. That buffered line
  leaves as a 22 AWG DATA + GND pair, taped to the XT60 power run as one tip-tower cable. The
  tip tower has no electronics and nothing wired in its base: the cable itself ends in the
  4 strand JST-SMs, their 5V and GND leads in two soldered joints with the power cores (the
  data GND in the GND joint), their DATA leads soldered to the data wire, heat shrink over
  every joint ([power_distribution.md](power_distribution.md)). In a 1 tower power box gate 2
  has no connectors: its 560 Ω holds the input at 0 V and the 100 Ω ends open.

## Decisions

- **One 74AHCT125 per power box; one gate drives all 4 strands of its own tower, and in a
  2 tower power box a second gate drives the tip-tower cable** (owner, 2026-10-29: "there
  should be no tip-tower electronics. the 2 level shifters are at the t6/t2, the 1.5m chord
  doesn't require a level shifter. so 2 channels are used in the level shifter", then "One
  chip, 2 gates used"). The owner's model of the box is one level shifter with one channel per
  data line leaving it; the four strand leads are short and in parallel, so one gate drives
  them. A 1 tower power box connects gate 1 only.
  **Changed 2026-10-29:** previously one gate per strand for the box's own tower (agent,
  2026-10-10), so that a shorted strand lead took out only its own face, and a second chip
  for the tip tower (agent, 2026-10-18). Changed because the owner, about to build the eight
  boxes, wants one chip per box, and the per-face isolation was the agent's idea, never
  confirmed. The trade-off the tip tower already had now holds for every tower: a short on
  one face's data lead darkens all four; `guide/troubleshooting.md` says so.
- **One identical board in every power box: gate 2's input resistor and 100 Ω are fitted even
  where nothing connects to them** (owner, 2026-10-29: "if i put a pull down resistor to pin 6 on
  all of them, is that a problem? in general - if the circuit is the same - is that a
  problem?", then "Yes, one board"). Eight boxes to build by hand is easier as one board
  learned once than as two, any board then fits any box (a spare serves both kinds, and a
  1 tower power box becomes a 2 tower power box by adding connectors), and the drawings and
  parts list differ only in connectors. It costs four input resistors and four 100 Ω across
  the set. An unused AHCT input through a resistor to GND is as good as a direct tie (the
  input draws about 1 µA, so it sits microvolts above ground through 560 Ω, as it did
  through the earlier 10 kΩ), so the idle gate is safe; the resistor must be on the input
  (pin 5), because a resistor on the output (pin 6) would leave the input floating, the one
  thing an unused CMOS gate must not do. **Changed 2026-10-29:** the one-chip decision above
  first had the 1 tower power box with pin 5 tied straight to GND and nothing on pin 6, so
  the two kinds of box had different boards.
- **Neighbour towers get their data already buffered from the power box, with no electronics
  in their base** (owner, 2026-10-18: "I can take it out of the last power box and not have a
  small perfboard in the towers that don't have power boxes"; 2026-10-29: "T1 and T7 just get
  a cable that has 4 jst-SM outputs at the end"). The split lives at the end of the cable,
  made up on the bench, so there is nothing to wire on site in T1 or T7. The trade-off: the
  tip tower's four faces share one buffer gate, so a short on one face's data lead darkens
  all four.
  **Rejected.** *A small 74AHCT125 board in each tip tower's base:* more boards to build.
  *4 JST-SM cables per neighbour from the box:* each face independent and no XT60, but 22 AWG
  over ~2 m loses 0.2–0.4 V, and the boxes would need 8–12 JST exits.
- **560 Ω from every data input to GND, not 10 kΩ** (owner, 2026-10-31, on the bench). The
  resistor does two jobs. It holds the input low when the data cable is unplugged or the
  sender is off, so the strips show the WS2812 idle state instead of garbage (the original
  reason for a pull-down, agent, 2026-10-10). And at 560 Ω it ends the data cable: with
  10 kΩ the cable's far end is open, and the 74AHCT125 misread what arrived over 4 m.
  **The bench record (owner, 2026-10-30/31).** The first two boxes, built alike to the
  drawings with 10 kΩ, both made their strands flash at random about every second or two,
  from the master box over a 4 m data cable, on a solid colour as much as on an effect. The
  same strands at the end of the same cable with no box in between, powered from the box's
  top-feed XT60, were clean; the same box on a 15 cm data cable was clean; 100 nF across
  the chip's VCC and GND changed nothing. A 560 Ω soldered across the 10 kΩ (530 Ω) cured it
  at once, and the design value is 560 Ω alone on new boards. The mechanism was not seen on
  a scope (the owner has none); the agent's reading is that a 5 V edge arriving at an open
  line end into a fast CMOS input with no hysteresis and a 1.5 V threshold re-crosses that
  threshold on the ring or on picked-up noise, where a strip's slow DIN does not, and 560 Ω
  absorbs most of the reflection and makes the input eighteen times less sensitive to
  pickup. The chip itself is not at fault: the same part drives the line cleanly at the
  master end, and the box reads a short cable cleanly.
  **What it costs the sender.** A 74AHCT125 output high into 560 Ω + 100 Ω sources about
  7 mA, inside its 8 mA rating, and the box input sees about 4.1 V against a 2 V threshold.
  Statue 2's senders are MAX485 receiver outputs (RO), specified at 4 mA for 3.5 V high;
  into this load the high level drops to roughly 3 V, still above the 2 V threshold. **The
  statue 2 path with 560 Ω is untested** (agent, 2026-10-31): the bench ran from the master
  box's 74AHCT125. The bench test in `guide/build.md` covers it.
  **Changed 2026-10-31:** from 2026-10-10, 10 kΩ (agent), chosen only as a pull-down, with
  nothing recorded about terminating the cable because the runs were "a few metres between
  buffers" and thought short enough not to matter. They are not, for this input.
  **Rejected (owner, 2026-10-31; the crew was on the ground and the boxes had to work that
  day).** *Twisted-pair data cables* (a CAT5e pair would sit near the 100 Ω series resistor
  at the sender and end the ring at the source): none on hand. *74HCT125 in place of the
  74AHCT125* (its input tolerates edges five times slower): none on hand, and the part is not
  what is wrong. *Removing the buffer and driving the strands straight from the cable* (it
  worked on the bench): it reopens the path by which a running master box back-powers an
  unpowered strip through its first LED, below, and sends a shorted strand lead to the
  master box's chip instead of the box's.
- **No decoupling capacitor at the chip** (agent, 2026-10-31). The design never had one; the
  owner added 100 nF across VCC and GND on one bench box while chasing the flicker and it
  made no difference, so it is not added to the drawings. The box that has one keeps it:
  it is harmless.
- **100 Ω per buffer output** (agent; optional per the owner). It damps ringing on the lead.
- **Data cables: any standard copper, DATA + its own GND wire** (owner, 2026-10-10/18). Master/slave box
  → power box, and power box → neighbour as a 22 AWG pair. Runs are a few metres between
  buffers, so nothing special is needed. The GND wire gives the signal its reference and ties
  the supplies' grounds together ([power_distribution.md](power_distribution.md)).
- **Data inputs' 5V pin left unconnected** (agent, 2026-10-18), so the sender's supply and the
  box's supply never join on +5 V.
- **The buffer runs on the strips' own 5 V rail, so a power box may be off, or ramping,
  while the master/slave box keeps sending** (owner asked 2026-10-29: "if the power box is
  turned off and data is pushed into the level shifter - does that pose a risk to the level
  shifter? will anything go to the data of the leds and destroy the first led?"; recorded on
  the owner's "Yes, record it"). Two facts make it safe. The 74AHCT125's inputs have no
  diode to VCC: the datasheet's absolute-maximum input voltage is −0.5 to 7 V independent of
  VCC (the AHCT family's 5 V tolerant inputs), so 5 V data on pin 2 or 5 of an unpowered chip
  is within ratings, draws about 1 µA, and cannot back-power the chip or reach its output. And
  the chip's VCC is the same rail as the strips' VDD, so the gate's output high can never be
  above the first LED's supply in any state, off, on or mid-ramp. What kills a first LED is
  data on DIN while its VDD is off: DIN's protection diode then feeds the whole strip through
  the data pin. That path would exist if the master/slave box drove the strips directly over
  the cable (5 V on DIN with VDD at 0 V, limited only by the sender's 100 Ω); the buffer in the
  box is what removes it. The reverse case, box on and sender off or unplugged, is held at
  0 V by the input's 560 Ω, the WS2812 idle state. The box's GND stays tied to the sender's
  through the data cable's GND wire whether the PSU is on or off, so the input never floats
  against a missing reference.

## Gotchas

- The same chip's dead-gate failure and the handling rules for it are recorded in
  [../controller/local_outputs.md](../controller/local_outputs.md) (Gotchas); they apply to
  every power-box chip too.

## Related

- [power_distribution.md](power_distribution.md) — which box feeds which towers.
- [tower_layout.md](tower_layout.md) — why all four faces share one channel.
