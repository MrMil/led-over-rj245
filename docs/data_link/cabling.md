# Cabling

Path: [docs](../README.md) › [data_link](README.md) › **cabling**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`RJ45`), `guide/wiring.md`, `guide/setup.md`, `guide/build.md`
**Covers:** the RJ45 pinout, connectors inside the boxes, the trench cable, and burial.

## What it does

Pin 1/2 (orange pair) = channel 1, A/B. Pin 3/6 (green pair) = channel 2, A/B. Pin 4/5 (blue
pair) = channel 3, A/B. Pins 7/8 (brown pair) = GND. Identical at both ends; cables are
straight-through. Three cables run between the controller box and box 2.

## Decisions

- **The striped wire of each pair is A, the solid one B, on every channel** (owner,
  2026-10-28: "white to A"). One rule for all seven channels and both boxes, so the crew
  lands wires by looking at them and A/B inversions cannot creep in channel by channel. The
  link only needs both ends to match; the rule picks which match. **Changed 2026-10-28:**
  channel 3 followed T568B pin order (pin 4 solid blue = A, pin 5 white/blue = B), which made
  it the one channel with the solid wire on A.
- **A and B of a channel are always the two wires of one twisted pair** (owner). Common-mode
  rejection only works if noise couples equally into both; split a pair and differential
  signalling stops protecting the link. That is why channel 2 is on 3/6 (one T568B pair,
  physically split in the connector) and channel 3 on 4/5.
- **GND on the brown pair of every cable, not just one** (owner, 2026-10-26). One ground
  conductor would satisfy the MAX485's common-mode window, and 7 channels + 1 ground fit in two
  cables' 8 pairs. Three cables with ground in each were kept because every cable then carries
  its own reference (one cable alone works, which matters when fault-finding), the ground path
  is tripled, the pair would otherwise be unused, and jacks 1 and 2 each keep a spare pair. Two cables
  would save one 20 m lead and nothing else.
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
- **All cables the same length** (owner, 2026-10-09). Identical lengths make every spare fit
  every run. **Changed 2026-10-21 (agent):** the length was 10 m, with reach open. The final
  layout puts the apexes 17.4 m apart (`layout/statue-layout.json`), so 10 m cannot reach;
  the guide now says 20 m (the straight trench between the apexes plus slack into both bases).
  The owner has not yet confirmed the purchase; the 10 m cables may exist already.
- **Cable lengths fit the runs; no large spools** (owner, 2026-10-09). Spare length is stored
  inside a statue base, which already holds the box and the tower wiring.
- **Mains shares the data trenches** (owner, 2026-10-09). Each trench is dug once; RS-485
  tolerates running alongside mains.
- **One straight trench between the statues** (owner, 2026-10-09/10). Digging hard desert
  soil in the heat is the most expensive labour in the build; cable length is chosen to fit
  the trench, never the other way round. Tower cables run in the trench under each statue.
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
