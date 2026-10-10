# Wiring

[← README](../README.md) · [Setup](setup.md) · [Build](build.md)

| Diagram | Covers |
|---|---|
| [System overview](img/overview.svg) | Both statues, boxes, cables |
| [Controller box](img/controller-wiring.svg) | Statue 1: ESP32, 2 × 74AHCT125, 7 transmitters, 3 jacks, 7 tower outputs |
| [Box 2](img/box2-wiring.svg) | Statue 2: 3 jacks, 7 receivers, 7 tower outputs |
| [Tower base](img/tower-base.svg) | All 14 towers: data in, 74AHCT125 split to the 4 faces |
| [Statue power](img/statue-power.svg) | Mains from the apex to 5 supplies; 5 V to the towers |
| [Supply box](img/box-power.svg) | All 10 supply boxes: C14, PSU, XT60 outputs |

`+5V` / `GND` flags are the perfboard rails. Crossing lines without a dot are not connected.
RJ45 pigtail wires are drawn in T568B colours (striped = white/colour).

---

## Controller box (statue 1)

![Controller box wiring](img/controller-wiring.svg)

### ESP32 pins

| GPIO | Channel | Path |
|---|---|---|
| 4 | S1-T1 | 74AHCT125 #1 gate 1 → tower T1 data |
| 13 | S1-T2 | 74AHCT125 #1 gate 2 → tower T2 data |
| 14 | S1-T3 | 74AHCT125 #1 gate 3 → tower T3 data |
| 16 | S1-T4 | 74AHCT125 #1 gate 4 → tower T4 data |
| 17 | S1-T5 | 74AHCT125 #2 gate 1 → tower T5 data |
| 18 | S1-T6 | 74AHCT125 #2 gate 2 → tower T6 data |
| 19 | S1-T7 | 74AHCT125 #2 gate 3 → tower T7 data |
| 21 | S2-T1 | transmitter → jack 1 pins 1/2 |
| 22 | S2-T2 | transmitter → jack 1 pins 3/6 |
| 23 | S2-T3 | transmitter → jack 1 pins 4/5 |
| 25 | S2-T4 | transmitter → jack 2 pins 1/2 |
| 26 | S2-T5 | transmitter → jack 2 pins 3/6 |
| 27 | S2-T6 | transmitter → jack 2 pins 4/5 |
| 32 | S2-T7 | transmitter → jack 3 pins 1/2 |
| 5V / VIN, GND | | perfboard rails |

GPIO 33 is spare.

### 74AHCT125 (×2, statue 1's towers)

| Pin | Connect to |
|---|---|
| 14 (VCC) | +5V |
| 7 (GND), 1/4/10/13 (OE) | GND |
| 2, 5, 9, 12 (1A–4A) | GPIOs per the table; on #2, pin 12 (unused 4A) → GND |
| 3, 6, 8, 11 (1Y–4Y) | 100 Ω → tower data output |

The 74AHCT125s and 100 Ω resistors are optional, depending on perfboard space; without them
the GPIO drives the tower data output directly.

### MAX485 transmitters (×7)

| Module pin | Connect to |
|---|---|
| VCC | +5V |
| GND | GND |
| DI | its GPIO |
| DE and RE | both to +5V |
| RO | not connected |
| A, B | jack pigtail, per the RJ45 table |

Leave the module's own 120 Ω resistor in place.

---

## Box 2 (statue 2)

![Box 2 wiring](img/box2-wiring.svg)

### MAX485 receivers (×7)

| Module pin | Connect to |
|---|---|
| A, B | jack pigtail, per the RJ45 table |
| VCC | +5V |
| GND | GND |
| DE and RE | both to GND |
| DI | not connected |
| RO | 100 Ω → tower data output |

**Idle bias, per receiver:** 560 Ω from **A to GND** and 560 Ω from **B to +5V**. Leave the
module's 120 Ω in place.

---

## RJ45 jacks and cables

Three channels per cable. Same pinout at both ends; cables are straight-through.

| Pin | Colour (T568B) | Signal |
|---|---|---|
| 1 | white/orange | channel 1, A |
| 2 | orange | channel 1, B |
| 3 | white/green | channel 2, A |
| 4 | blue | channel 3, A |
| 5 | white/blue | channel 3, B |
| 6 | green | channel 2, B |
| 7 | white/brown | GND |
| 8 | brown | GND |

| Jack | Channel 1 | Channel 2 | Channel 3 |
|---|---|---|---|
| 1 | S2-T1 | S2-T2 | S2-T3 |
| 2 | S2-T4 | S2-T5 | S2-T6 |
| 3 | S2-T7 | spare | spare |

Pins 3/6 and 4/5 are each one twisted pair. Verify pin-to-pin with a meter through both
jacks; don't rely on colours.

---

## Tower base (all 14 towers)

![Tower base wiring](img/tower-base.svg)

| Connection | To |
|---|---|
| Data cable DATA | 74AHCT125 pins 2, 5, 9, 12 (all four inputs), and 10 kΩ to GND |
| Data cable GND | GND |
| 74AHCT125 pin 14 | tower +5V |
| 74AHCT125 pins 7, 1, 4, 10, 13 | GND |
| Pins 3, 6, 8, 11 | 100 Ω → face 1–4 strip DIN |
| Strips 5V / GND | tower power feed |

All four faces get the same data. Strips run bottom to top.

---

## Power

![Statue power](img/statue-power.svg)

![Supply box](img/box-power.svg)

- **Mains:** apex outlet → power strip → a C13 cord to each supply box's C14. Buried cords:
  H07RN-F 3 × 1.5. In each box: L → PSU 1, N → 2, PE → 3 (FG).
- **5 V out:** PSU 4/5 (−V) and 6/7 (+V) → XT60 outputs, one per destination, NYAF 2.5 mm²
  inside (red +5 V, blue GND).
- **Buried 5 V:** 3-core cable, brown +5 V, blue GND, green/yellow unused or GND, XT60 both
  ends. 3 × 2.5.
- **Tower bases:** the incoming feed splits to the strand XT60s. At T4 and T5 the two
  supplies' +5 V stay separate (faces 1–2 / faces 3–4); GNDs may join.
- **T4:** a second feed to the top of each strand, up the post (faces 1–2 from C, 3–4
  from D).
- **Ground bond:** 1.5 mm² linking all supplies' −V along the trenches.
- **Supply C only:** PSU 5 (−V) / 7 (+V) → apex box perfboard rails, 0.5 mm².

---

## Notes

- Ferrules on stranded wire in screw terminals; stray strands short A to B. No tinned ends.
- Zip-tie the pigtails inside each box.
- Label box, jack, tower-output and tower numbers on both ends of every cable.
- MAX483/487/488/489 lookalikes are too slow for LED data; the chip must read MAX485.
