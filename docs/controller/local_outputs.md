# Local outputs (statue 1)

Path: [docs](../README.md) › [controller](README.md) › **local_outputs**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`master_box()`), `guide/img/master-box-wiring.svg`
**Covers:** how statue 1's 7 tower channels leave the master box without RS-485.

## What it does

GPIOs 4, 13, 14, 16 → 74AHCT125 #1 gates 1–4; GPIOs 17, 18, 19 → 74AHCT125 #2 gates 1–3
(the unused 4A input tied to GND). Each output → 100 Ω → a tower data output (DATA + GND) to
that tower's base, through the trench under the statue.

## Decisions

- **74AHCT125 between the ESP32 and the tower cables** (owner design; optional per the owner,
  2026-10-09, depending on perfboard space). It gives a 5 V, strongly driven signal for the
  cable run, and it protects the ESP32 GPIOs from ESD and shorts on cables that leave the box.
  The ESP32 drives both statues, so losing a GPIO is expensive; the buffer is a socketed,
  cheap part. The tower-base 74AHCT125 accepts 3.3 V anyway (TTL thresholds), so without
  this buffer the link still works over short runs.
- **Unused gate inputs grounded** (agent). A floating CMOS input can oscillate and draw
  current.
- **100 Ω series resistor at each output** (agent, 2026-10-09; optional per the owner). It
  damps ringing on the cable and limits current if a pinched cable shorts DATA. The same
  value is used at the slave box's outputs and in the power boxes.
- **The 100 Ω stands upright in the output pin's row, with the output wire soldered to its
  top lead** (owner, 2026-10-11). The ESP32 board has no room to lay resistors flat (see
  [README.md](README.md)). Upright, it still sits at the driver, where series termination
  works best. Heat shrink over the resistor and the joint stops it shorting to its
  neighbours. It goes in a free hole of the row, not on the chip leg, because the chips are
  socketed and must stay removable. The wires are tied down, or their pull would flex the
  resistor lead at the board until it breaks.
- **Statue 1 is not RS-485** (owner). Its towers are a few metres from the box inside the
  statue; differential signalling buys little there. Statue 2's channels cross the trench
  between the statues, which is the long, exposed run.

## Gotchas

- **A 74AHCT125 with one dead gate cooks itself and loses the rest** (owner's bench,
  2026-10-27/28). Both controller chips ran hot after minutes and statue 1's towers went
  dark; the dead set then changed between power-ups and did not follow the chips or the ESP32s
  when they were swapped, because gates kept dying in whichever chip was fitted. The diode
  test (`guide/troubleshooting.md`, *Testing a 74AHCT125*) showed the dead gates' outputs
  shorted to GND inside the chip (0 Ω, 2.4 Ω, 85 Ω). Mechanism: a shorted output lets the
  gate's own pull-up source current into the short, inside the package, whenever the data
  drives it high; the heat takes the neighbouring gates. Ruled out by measurement before this
  was found: supply (5.2 V), ground path (0 V strip GND to PSU −V, 0 V across the 100 Ω),
  enables and unused input grounded, board shorts (none with the chip out), ESP32 (both
  boards drive all pins alike). **What killed the first gate is unknown.** Static during
  handling or a probe slip on a live chip pin are the agent's suspicions (dry air-conditioned
  room, several chip swaps), not confirmed. The owner rules out the earlier episode of chips
  falling out of their female headers (2026-10-25): the board was not powered then. The
  guide's handling rules follow from the suspicion (cord out, discharge on a data connector's
  GND pin, never on the PSU: see
  [../strips_and_power/power_distribution.md](../strips_and_power/power_distribution.md),
  Gotchas). Gate damage is progressive (one gate read 85 Ω, a partial short), so a chip that
  has been through a bad episode can pass the diode test and still warm up later; the
  finger test after an hour's run (`guide/build.md`, bench test) is the check that counts. A fresh pair of chips restored all seven channels.
- **The controller chips' inputs have no pull-downs** (unlike the power boxes'
  [../strips_and_power/tower_base.md](../strips_and_power/tower_base.md)). With the ESP32 out
  of its socket, or before its driver starts, the seven inputs float and both chips warm up.
  Harmless for a few seconds at boot; do not run the board powered without the ESP32.
  **Rejected (owner, 2026-10-28):** 10 kΩ pull-downs on the seven inputs. The ESP32 is meant
  to stay in its socket, a floating input warms a chip but does not kill it, and the 10 kΩ
  resistors bought were the power boxes' (since replaced there by 560 Ω,
  [../strips_and_power/tower_base.md](../strips_and_power/tower_base.md)). The power boxes'
  reason for 560 Ω, ending a metres-long cable, does not arise here: these inputs sit a few
  centimetres from the ESP32.

## Related

- [gpio_assignment.md](gpio_assignment.md) — the seven GPIOs.
- [../strips_and_power/tower_base.md](../strips_and_power/tower_base.md) — what receives these signals.
