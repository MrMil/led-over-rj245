# Transceivers

Path: [docs](../README.md) › [data_link](README.md) › **transceivers**
Parent: [README.md](README.md)
**Code:** `tools/wiring_diagrams.py` (`max485()`), `guide/wiring.md`, `guide/parts.md`
**Covers:** the RS-485 chip choice and how the modules are strapped at each end.

## What it does

12 common blue 5 V MAX485 modules: 6 transmitters at the controller (DE = RE̅ = 5 V, DI from
GPIO, RO unused) and 2 receivers per statue box (DE = RE̅ = GND, RO to the strips, DI unused).

## Decisions

- **MAX485, a 5 V part** (owner). Its RO swings to 5 V, meeting the WS2812B's 3.5 V VIH; its DI
  has TTL thresholds, so 3.3 V GPIO drives it directly. Rated 2.5 Mbps — ample for 800 kHz.
- **Acceptable substitutes:** SP485E, SN75176B, SN65HVD11, ADM485 (owner) — all 5 V and not
  slew-limited.
- **Enables hard-wired, never driven by software** (owner). Each end only does one job.

### Never a slew-rate-limited part

**Why.** MAX483, MAX487, MAX488, MAX489, THVD1450 and anything sold as "low EMI" or
"slew-rate limited" cap at 250–500 kbps by deliberately smearing edges, turning 350 ns pulses
into mush (owner). Lookalike modules sometimes carry these; the field guide tells the builder
to read the chip marking.
**Rejected.** *3.3 V transceivers (SP3485, Waveshare RS485 board).* Better edge margin on paper
(10 Mbps), but RO never reaches the WS2812B's 3.5 V VIH — the classic "works on the bench,
flickers in the field" failure that shows up cold, on longer leads, or with a different LED
batch (owner). *Integrated "RS-485 + RJ45" modules:* built for Modbus at 9600–115200 baud,
rarely name the transceiver, and often add auto-direction logic that would interfere with a
continuous 800 kHz stream (owner).
**Constrains.** Any replacement chip must be 5 V, ≥ ~2 Mbps, and not slew-limited.

## Gotchas

- Blue modules commonly carry pull-up resistors on their logic pins; the exact values are not
  verified for the modules bought. Hard-wiring DE/RE̅ to a rail overrides any pull-up. The
  560 Ω bias at the receiver overrides weak (10–20 kΩ) line bias resistors if present
  ([termination_and_bias.md](termination_and_bias.md)).

## Related

- [termination_and_bias.md](termination_and_bias.md) — the passives around the receivers.
- [../controller/README.md](../controller/README.md) — transmitter power budget.
