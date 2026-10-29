# Tower data splitting

Path: [docs](../README.md) › [strips_and_power](README.md) › **tower_base**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`power_box(two)`, `tip_tower_cable()`), `guide/img/power-box-1-tower.svg`, `guide/img/power-box-2-tower.svg`, `guide/img/tip-tower-cable.svg`, `guide/wiring.md`
**Covers:** how each tower's one data line reaches its 4 strands: in the power box for a box's
own tower, passively at the end of the tip-tower cable for a tip tower.

## What it does

- **The board** is the same in all ten power boxes (T4's inside the master/slave box): one
  74AHCT125, gates 1 and 2 each with 10 kΩ from the input to GND and 100 Ω on the output,
  gates 3 and 4 with their inputs to GND. The two kinds of box differ only in which
  connectors are fitted to gate 2.
- **Own tower** (T2–T6). The tower's data line enters the power box on a JST-SM
  (DATA + GND; the 5V pin is not connected), onto gate 1's pull-down and input. The output
  goes through its 100 Ω and is then joined to the DATA leads of the 4 JST-SM out (5V, DATA,
  GND), one per strand.
- **Tip tower** (T1 from the power box in T2; T7 from the one in T6). Its data line enters the power box on its
  own JST-SM onto gate 2's pull-down and input. That buffered line
  leaves as a 22 AWG DATA + GND pair, taped to the XT60 power run as one tip-tower cable. The
  tip tower has no electronics and nothing wired in its base: the cable itself ends in the
  4 strand JST-SMs, their 5V and GND leads in two soldered joints with the power cores (the
  data GND in the GND joint), their DATA leads soldered to the data wire, heat shrink over
  every joint ([power_distribution.md](power_distribution.md)). In a 1 tower power box gate 2
  has no connectors: its pull-down holds the input at 0 V and the 100 Ω ends open.

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
- **One identical board in every power box: gate 2's 10 kΩ and 100 Ω are fitted even where
  nothing connects to them** (owner, 2026-10-29: "if i put a pull down resistor to pin 6 on
  all of them, is that a problem? in general - if the circuit is the same - is that a
  problem?", then "Yes, one board"). Eight boxes to build by hand is easier as one board
  learned once than as two, any board then fits any box (a spare serves both kinds, and a
  1 tower power box becomes a 2 tower power box by adding connectors), and the drawings and
  parts list differ only in connectors. It costs four 10 kΩ and four 100 Ω across the set. An
  unused AHCT input through 10 kΩ to GND is as good as a direct tie (the input draws about
  1 µA, so it sits microvolts above ground), so the idle gate is safe; the pull-down must be
  on the input (pin 5), because a resistor on the output (pin 6) would leave the input
  floating, the one thing an unused CMOS gate must not do. **Changed 2026-10-29:** the
  one-chip decision above first had the 1 tower power box with pin 5 tied straight to GND
  and nothing on pin 6, so the two kinds of box had different boards.
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
- **10 kΩ pull-down on every data input** (agent, 2026-10-10). With the data cable unplugged or
  the sender off, the floating input would make the strips show garbage; the pull-down holds
  it low, the WS2812 idle state.
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
  0 V by the input's 10 kΩ, the WS2812 idle state. The box's GND stays tied to the sender's
  through the data cable's GND wire whether the PSU is on or off, so the input never floats
  against a missing reference.

## Gotchas

- The same chip's dead-gate failure and the handling rules for it are recorded in
  [../controller/local_outputs.md](../controller/local_outputs.md) (Gotchas); they apply to
  every power-box chip too.

## Related

- [power_distribution.md](power_distribution.md) — which box feeds which towers.
- [tower_layout.md](tower_layout.md) — why all four faces share one channel.
