# Data link

Path: [docs](../README.md) › **data_link**
Parent: [../README.md](../README.md)

**Covers:** getting statue 2's 7 tower channels from the master box to the slave box: RS-485 on
three buried CAT5e cables, three channels per cable, received back to single-ended 5 V data
in the slave box.
**Code:** `tools/wiring_diagrams.py` (`RJ45`, `JACKS`, `slave_box()`, `master_box()`), `guide/img/slave-box-wiring.svg`, `guide/img/master-box-wiring.svg`, `guide/wiring.md`

## Design

### Decisions

- **Raw WS2812 waveform over RS-485, not a protocol** (owner). The transmitter just converts
  the 800 kHz WS2812 bitstream to differential and the receiver converts it back. Nothing is
  decoded, buffered or re-timed, so there is no firmware in the slave box and no added latency.
- **Three channels per cable, three cables between the boxes** (owner, 2026-10-10: "we can pass
  9 channels over the rj45 cables"). Three of a CAT5e's four pairs carry data, one carries
  ground; 9 channels for 7 towers leaves 2 spare. As built (owner, 2026-10-28): jack 3 =
  S2-T1–T3 (blue, green, orange pairs in that order), jack 2 = T4–T5, jack 1 = T6–T7; the blue
  pair of jacks 1 and 2 is spare. The owner did not state why this order; the recorded plan was
  jack 1 = T1–T3, jack 2 = T4–T6, jack 3 = T7. A bad cable darkens at most three towers.
  **Changed 2026-10-10:** previously two channels per cable (two ground pairs), one cable per
  remote statue, star from the controller to three statues.
- **Ground travels with the data, on pins 7/8** (owner; one pair since 2026-10-10). The ground conductors carry no
  signal; they hold the two boxes' grounds close enough that A and B stay inside the
  receiver's −7 V … +12 V common-mode window. Without them, leakage and capacitive coupling
  from independent mains-fed PSUs can push the inputs out of range — the likely cause of
  "statue 2 works until the generator load changes". The offset only has to be small, not zero.

### Differential, not single-ended

**Why.** Single-ended WS2812 data over 8–10 m with a 74AHCT125, series termination, twisted
pair and a dedicated ground would *probably* work (owner). "Probably" is not good enough for a
cable buried in a desert trench next to generators, dust-driven static and vehicles. The bit
rate is trivial; the hard part is edge fidelity — 350/700 ns pulses against cable capacitance,
reflections, and a 10 m ground return acting as an antenna. RS-485 reads V(A) − V(B) with a
±200 mV threshold, so noise that couples equally into both twisted conductors cancels. The
differential version costs about ₪2 per run.
**Rejected.** Single-ended (above). *DMX-to-WS2812 decoder boards* (RJ45/XLR in, WS2812 out):
they expect DMX512 framing at 250 kbps and 512 channels per universe, which would mean
restructuring the whole show around DMX for no benefit (owner).
**Constrains.** Every transceiver in the path must pass 350 ns pulses cleanly
([transceivers.md](transceivers.md)); A and B of a channel must share one twisted pair
([cabling.md](cabling.md)).

## Contents

### Pages

- [`transceivers.md`](transceivers.md) — why MAX485, which parts are banned, and how each end is strapped.
- [`cabling.md`](cabling.md) — RJ45 pinout, couplers and pigtails, cable type, burial, labelling.
- [`termination_and_bias.md`](termination_and_bias.md) — 120 Ω termination at both ends and the 560 Ω idle bias at the receiver.

## Related

- [../controller/README.md](../controller/README.md) — the transmitting end.
- [../strips_and_power/tower_base.md](../strips_and_power/tower_base.md) — what the receiver output drives.
