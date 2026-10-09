# Cabling

Path: [docs](../README.md) › [data_link](README.md) › **cabling**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`RJ45`), `guide/wiring.md`, `guide/setup.md`, `guide/build.md`
**Covers:** the RJ45 pinout, connectors inside the boxes, the trench cable, and burial.

## What it does

Pin 1/2 (orange pair) = channel A, A/B. Pin 3/6 (green pair) = channel B, A/B. Pins 4/5/7/8
(blue and brown pairs) = GND. Identical at both ends; cables are straight-through.

## Decisions

- **A and B of a channel are always the two wires of one twisted pair** (owner). Common-mode
  rejection only works if noise couples equally into both; split a pair and differential
  signalling stops protecting the link. That is why channel B is on 3/6 (one T568B pair,
  physically split in the connector) rather than the adjacent 3/4.
- **Panel-mount coupler in the enclosure wall, short cut patch-cable pigtail inside landing
  on the MAX485 screw terminals** (owner). The trench run is then a factory patch lead: no
  field wiring, and a failed run is a cable swap. The enclosures use a round threaded Cat6A
  coupler in a 24 mm hole (enclosure repo, `components/panel/rj45-bulkhead.yaml`); that part
  supersedes the "IP67 coupler" in the original design record. Its sealing is unverified.
- **Factory-moulded outdoor/UV-rated CAT5e patch leads, never hand-crimped plugs** (owner).
  Badly crimped RJ45s are the most common intermittent field failure: they pass a bench
  continuity test and fail after thermal cycling and vibration. If crimping ever becomes
  necessary: solid-core cable with solid-core plugs, stranded with stranded.
- **Plain UTP, not shielded** (owner). At 8 m the twisting does the work; a shield grounded
  at both ends would create a ground loop and make things worse.
- **Pigtail over an RJ45 breakout board** (owner). The patch lead's conductors are already the
  right gauge and strain-relieved at the plug.
- **Direct burial in a pickaxe-dug trench, no conduit** (owner, 2026-10-09). Standard practice
  at burns; the owner has not seen conduit used in over 50. Depth (20–30 cm) handles vehicles
  and foot traffic.
  **Changed 2026-10-09:** previously conduit (drip-irrigation tubing), so a damaged cable could
  be swapped without re-digging and removed cleanly at teardown. Dropped as unnecessary
  practice for a one-week installation. Consequence: a cable fault means digging it up, and the
  spare can be laid on the surface to test first.
- **No cable above ground** (owner, 2026-10-09). The police safety check before the event
  fails an installation with exposed cables, which would mean tearing it down. Each box is
  hidden inside its statue's base, and the cables come up out of the ground inside the base.
- **All cables 10 m** (owner, 2026-10-09). This covers the 8 m run with the rise into both
  bases. The ~2.5 m extra on the near runs is acceptable, and identical lengths make every
  spare fit every run.
- **Cable lengths fit the runs; no large spools** (owner, 2026-10-09). Any spare length has
  to be stored inside a statue base, and the controller's base already holds the LED and
  power wiring for statue 0. Three long coils there would be a rat's nest.
- **Mains shares the data trenches** (owner, 2026-10-09). Each trench is dug once; RS-485
  tolerates running alongside mains.
- **Trenches are the straight runs only: 8 m to the far statue, ~5.7 m to the two near ones**
  (owner, 2026-10-09). The controller sits at one statue of an 8 m circle; digging hard desert
  soil in the heat is the most expensive labour in the build. Cable length is chosen to fit
  those trenches, never the other way round.
- **A distinctive cable colour used for nothing else, and labels on everything** (owner). The
  cables look exactly like Ethernet; PoE on A/B would put 48 V into the transceivers at both
  ends.
- **Ferrules on stranded conductors in screw terminals; no tinning** (owner). Escaping strands
  cause intermittent A–B shorts; solder-tinned ends cold-flow under screw pressure and loosen.

## Gotchas

- Patch-cable colour codes are not guaranteed: verify end to end with a meter, through both
  couplers, and confirm the couplers are straight-through.
- The plug seated in the coupler is the mechanical weak point: zip-tie the pigtail inside.

## Related

- [README.md](README.md) — why the ground pairs are there.
- [../field_docs/wiring_diagrams.md](../field_docs/wiring_diagrams.md) — the pinout is drawn from the `RJ45` table.
