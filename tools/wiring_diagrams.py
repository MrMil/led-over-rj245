#!/usr/bin/env python3
"""Generate the wiring diagrams in guide/img/ as plain SVG.

Usage:  python3 tools/wiring_diagrams.py

The tables below are the single source for every diagram: change a GPIO, a
jack pin or a tower here, re-run, and all diagrams follow. Do not hand-edit the
SVGs. Standard library only.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "guide" / "img"

# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------

# Two statues, each a V of 7 towers T1..T7 numbered from one tip of the V to
# the other; T4 is the apex. Heights in mm, from the model photo (confirm).
TOWER_H = {"T1": 800, "T2": 1150, "T3": 1550, "T4": 2000, "T5": 1150, "T6": 800, "T7": 500}
TOWERS = list(TOWER_H)

# One channel per tower. Statue 1 is local to the controller box; statue 2's
# channels cross to the second box as RS-485.
GPIO = {
    "S1-T1": 4, "S1-T2": 13, "S1-T3": 14, "S1-T4": 16, "S1-T5": 17, "S1-T6": 18, "S1-T7": 19,
    "S2-T1": 21, "S2-T2": 22, "S2-T3": 23, "S2-T4": 25, "S2-T5": 26, "S2-T6": 27, "S2-T7": 32,
}

ORANGE, GREEN, BLUE, BROWN = "#f08a24", "#2e9e44", "#1f5fbf", "#8b5a2b"
# RJ45 pin -> (T568B colour name, colour, striped, role)
RJ45 = {
    1: ("w/orange", ORANGE, True, ("A", 1)),
    2: ("orange", ORANGE, False, ("B", 1)),
    3: ("w/green", GREEN, True, ("A", 2)),
    4: ("blue", BLUE, False, ("A", 3)),
    5: ("w/blue", BLUE, True, ("B", 3)),
    6: ("green", GREEN, False, ("B", 2)),
    7: ("w/brown", BROWN, True, ("GND", None)),
    8: ("brown", BROWN, False, ("GND", None)),
}
CH_PINS = {1: (1, 2), 2: (3, 6), 3: (4, 5)}   # channel in a cable -> (A pin, B pin)
# jack -> statue-2 tower per channel (None = spare)
JACKS = {1: ["T1", "T2", "T3"], 2: ["T4", "T5", "T6"], 3: ["T7", None, None]}


def jack_of(tower):
    for j, chans in JACKS.items():
        if tower in chans:
            return j, chans.index(tower) + 1
    raise KeyError(tower)


DATA_33 = "#1565c0"   # 3.3 V logic
DATA_5 = "#7b1fa2"    # 5 V logic
RED = "#d32f2f"
BLACK = "#222222"
FONT = "Helvetica, Arial, sans-serif"


# --------------------------------------------------------------------------
# Tiny SVG helper
# --------------------------------------------------------------------------

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Drawing:
    def __init__(self, w, h, title):
        self.w, self.h, self.items = w, h, []
        self.title = title
        self.rect(0, 0, w, h, fill="#ffffff", stroke="none", rx=0)

    def add(self, s):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="#ffffff", stroke="#333", sw=2, rx=8, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=16, anchor="start", weight="normal", fill="#222", italic=False):
        st = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
                 f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}"{st}>{esc(s)}</text>')

    def lines(self, x, y, rows, size=16, anchor="start", gap=None, **kw):
        gap = gap or round(size * 1.35)
        for i, r in enumerate(rows):
            self.text(x, y + i * gap, r, size=size, anchor=anchor, **kw)

    def wire(self, pts, color=BLACK, width=3, stripe=False):
        p = " ".join(f"{x},{y}" for x, y in pts)
        if stripe:
            self.add(f'<polyline points="{p}" fill="none" stroke="#777" stroke-width="{width + 2}" '
                     f'stroke-linejoin="round"/>')
        self.add(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width}" '
                 f'stroke-linejoin="round"/>')
        if stripe:
            self.add(f'<polyline points="{p}" fill="none" stroke="#ffffff" stroke-width="{width}" '
                     f'stroke-dasharray="8 8" stroke-linejoin="round"/>')

    def dot(self, x, y, color=BLACK, r=5):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

    def pin(self, x, y):
        self.add(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#fff" stroke="#333" stroke-width="2"/>')

    def flag(self, x, y, label, direction="left", kind=None):
        """Net label. Every flag with the same text is the same wire."""
        kind = kind or ("p5" if "5V" in label else "gnd" if "GND" in label else "sig")
        fill, stroke, tc = {"p5": ("#fde3e3", RED, RED), "gnd": ("#e6e6e6", BLACK, BLACK),
                            "sig": ("#ede3f5", DATA_5, DATA_5)}[kind]
        w = len(label) * 9 + 16
        if direction in ("left", "right"):
            s = -1 if direction == "left" else 1
            pts = [(x, y), (x + s * 10, y - 12), (x + s * (10 + w), y - 12),
                   (x + s * (10 + w), y + 12), (x + s * 10, y + 12)]
            tx, ty = x + s * (10 + w / 2), y + 5
        else:
            s = -1 if direction == "up" else 1
            pts = [(x, y), (x + w / 2, y + s * 10), (x + w / 2, y + s * 34),
                   (x - w / 2, y + s * 34), (x - w / 2, y + s * 10)]
            tx, ty = x, y + s * 22 + 5
        p = " ".join(f"{a},{b}" for a, b in pts)
        self.add(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        self.text(tx, ty, label, size=14, anchor="middle", weight="bold", fill=tc)

    def resistor(self, x, y, label, vertical=False, color=BLACK):
        """Box resistor centred on (x, y); the caller draws the wire through it."""
        if vertical:
            self.rect(x - 8, y - 22, 16, 44, fill="#fff", stroke=color, sw=2, rx=2)
            self.text(x + 14, y + 5, label, size=14, weight="bold")
        else:
            self.rect(x - 22, y - 8, 44, 16, fill="#fff", stroke=color, sw=2, rx=2)
            self.text(x, y - 14, label, size=14, anchor="middle", weight="bold")

    def save(self, name, desc):
        body = "\n".join(self.items)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}">\n<title>{esc(self.title)}</title>\n'
               f'<desc>{esc(desc)} Generated by tools/wiring_diagrams.py; do not edit.</desc>\n'
               f'{body}\n</svg>\n')
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / name).write_text(svg)
        print("wrote", OUT / name)


def header(d, title, sub):
    d.text(40, 50, title, size=28, weight="bold")
    d.lines(40, 82, sub, size=16, fill="#444")


def legend(d, x, y, extra=()):
    rows = [("flag", "+5V", "perfboard 5 V rail (fed from the PSU, see power diagram)"),
            ("flag", "GND", "perfboard GND rail (same wire everywhere it appears)"),
            ("line", DATA_33, "data, 3.3 V (from the ESP32)"),
            ("line", DATA_5, "data, 5 V (to the LED strips)")] + list(extra)
    d.rect(x, y, 600, 34 + 30 * len(rows), fill="#fafafa", stroke="#bbb", sw=1)
    d.text(x + 14, y + 24, "Legend · lines that cross without a dot are not connected",
           size=14, weight="bold", fill="#444")
    for i, (kind, a, txt) in enumerate(rows):
        yy = y + 52 + 30 * i
        if kind == "flag":
            d.flag(x + 20, yy, a, "right")
        elif kind == "stripe":
            d.wire([(x + 16, yy), (x + 80, yy)], a, 6, stripe=True)
        else:
            d.wire([(x + 16, yy), (x + 80, yy)], a, 4)
        d.text(x + 100, yy + 5, txt, size=14)


def max485(d, x, y0, title, left, right, w=220, pitch=26):
    """Blue MAX485 module. left/right: list of pin names top to bottom.
    Returns {name: (x, y)}."""
    h = pitch * (max(len(left), len(right)) + 1) + 18
    d.rect(x, y0, w, h, fill="#e3edf9", stroke="#1f5fbf")
    d.text(x + w / 2, y0 + h - 8, "120 Ω on board: leave it", size=12, anchor="middle", fill="#1f5fbf")
    d.text(x + w / 2, y0 + h / 2 - 4, "MAX485", size=17, anchor="middle", weight="bold", fill="#1f5fbf")
    d.text(x + w / 2, y0 + h / 2 + 16, title, size=13, anchor="middle", fill="#1f5fbf")
    pts = {}
    for i, n in enumerate(left):
        y = y0 + pitch * (i + 1)
        d.pin(x, y), d.text(x + 10, y + 5, n, size=14, weight="bold")
        pts[n] = (x, y)
    for i, n in enumerate(right):
        y = y0 + pitch * (i + 1)
        d.pin(x + w, y), d.text(x + w - 10, y + 5, n, size=14, weight="bold", anchor="end")
        pts[n] = (x + w, y)
    return pts




def swatch(d, x, y, pin):
    cname, col, stripe, _ = RJ45[pin]
    d.add(f'<rect x="{x}" y="{y - 6}" width="34" height="12" fill="{col}" stroke="#777"/>')
    if stripe:
        d.add(f'<rect x="{x + 8}" y="{y - 6}" width="9" height="12" fill="#fff"/>'
              f'<rect x="{x + 25}" y="{y - 6}" width="9" height="12" fill="#fff"/>')


def jack_table(d, x, top, title, j):
    """RJ45 coupler pin table. Pigtail wires are joined by matching labels."""
    w, pitch = 300, 26
    d.rect(x, top, w, 48 + pitch * 8, fill="#f4f4f4", stroke="#333")
    d.text(x + w / 2, top + 28, title, size=16, anchor="middle", weight="bold")
    for n in range(1, 9):
        cname, col, stripe, (fn, ch) = RJ45[n]
        y = top + 52 + pitch * (n - 1)
        d.text(x + 16, y + 5, n, size=14, weight="bold")
        swatch(d, x + 40, y, n)
        d.text(x + 84, y + 5, cname, size=13, fill="#555")
        if fn == "GND":
            label = "GND"
        else:
            t = JACKS[j][ch - 1]
            label = f"{fn} · S2-{t}" if t else f"{fn} · spare"
        d.text(x + 170, y + 5, label, size=14, weight="bold")


def pair_label(d, x, y, pin, j, side):
    """Short coloured pigtail stub plus 'jack j · pin n' label."""
    cname, col, stripe, _ = RJ45[pin]
    if side == "right":
        d.wire([(x, y), (x + 60, y)], col, 5, stripe=stripe)
        d.text(x + 70, y + 5, f"jack {j} · pin {pin} ({cname})", size=13, weight="bold")
    else:
        d.wire([(x - 60, y), (x, y)], col, 5, stripe=stripe)
        d.text(x - 70, y + 5, f"jack {j} · pin {pin} ({cname})", size=13, weight="bold", anchor="end")


def tower_exit(d, x, y, name, sub):
    d.rect(x, y - 24, 260, 48, fill="#fff8e1", stroke="#b58900")
    d.pin(x, y)
    d.text(x + 14, y - 3, name, size=15, weight="bold")
    d.text(x + 14, y + 16, sub, size=13, fill="#555")


def buffer_chip(d, x, top, gates, title, unused_note):
    """74AHCT125. gates: list of (A pin, A name, Y name, Y pin, y). Returns bottom y."""
    bw = 220
    bot = top + 30 + 60 * len(gates) + 60
    d.rect(x, top, bw, bot - top, fill="#f3e5f5", stroke=DATA_5)
    for (pa, a, yname, py_, y) in gates:
        d.pin(x, y), d.text(x + 10, y + 5, f"{pa} · {a}", size=14, weight="bold")
        d.pin(x + bw, y), d.text(x + bw - 10, y + 5, f"{yname} · {py_}", size=14, weight="bold", anchor="end")
    d.text(x + bw / 2, bot - 40, title, size=15, anchor="middle", weight="bold", fill=DATA_5)
    d.text(x + bw / 2, bot - 22, "VCC 14→+5V · GND 7 · OE→GND", size=11, anchor="middle", fill="#555")
    if unused_note:
        d.text(x + bw / 2, bot - 8, unused_note, size=11, anchor="middle", fill="#555")
    return bot


# --------------------------------------------------------------------------
# 1. Overview
# --------------------------------------------------------------------------

def overview():
    d = Drawing(1200, 980, "System overview")
    header(d, "System overview — top view (schematic, not to scale)",
           ["One controller drives both statues: one channel per tower, 14 in total.",
            "Each statue is a V of 7 towers, T1–T7 from tip to tip, T4 the apex."])
    cx, cy, r = 600, 500, 320
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#bbb" stroke-width="2" stroke-dasharray="8 8"/>')
    d.add(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#555"/>')
    d.text(cx, cy + 32, "viewing point", size=14, anchor="middle", fill="#555")
    cable, led = "#6a1b9a", "#e65100"

    def statue(apex_x, s, label, box_col, box_label):
        # s = +1: V opens to the right (towards the centre); -1: to the left
        pos = {}
        for i, t in enumerate(TOWERS):
            k = abs(i - 3)
            side = -1 if i < 3 else 1
            pos[t] = (apex_x + s * 55 * k, cy + side * 60 * k)
        bx, by = apex_x - s * 70, cy
        for t, (x, y) in pos.items():
            d.wire([(bx, by), (x, y)], led, 2)
        for t, (x, y) in pos.items():
            sz = 12 + TOWER_H[t] / 100
            d.rect(x - sz / 2, y - sz / 2, sz, sz, fill="#ffe0b2", stroke="#e65100", sw=2, rx=3)
            d.text(x + s * (sz / 2 + 6), y + 5, t, size=13, anchor="start" if s > 0 else "end", weight="bold")
        d.rect(bx - 34, by - 22, 68, 44, fill=box_col, stroke="#333")
        d.text(bx, by + 5, box_label, size=12, anchor="middle", weight="bold", fill="#fff")
        d.text(apex_x, cy - 230, label, size=17, anchor="middle", weight="bold")
        return bx, by

    b1 = statue(cx - r + 40, 1, "Statue 1", "#2e7d32", "CTRL")
    b2 = statue(cx + r - 40, -1, "Statue 2", "#1565c0", "BOX 2")
    for dy in (-12, 0, 12):
        d.wire([(b1[0] - 34, b1[1] + dy), (b1[0] - 60, b1[1] + dy), (b1[0] - 60, cy + 300 + dy),
                (b2[0] + 60, cy + 300 + dy), (b2[0] + 60, b2[1] + dy), (b2[0] + 34, b2[1] + dy)], cable, 4)
    d.rect(cx - 150, cy + 312, 300, 30, fill="#fff", stroke=cable, sw=1.5)
    d.text(cx, cy + 333, "3 × CAT5e, jacks 1–3 → jacks 1–3", size=14, anchor="middle", fill=cable, weight="bold")
    d.rect(60, 870, 1080, 96, fill="#fafafa", stroke="#bbb", sw=1)
    d.lines(80, 896, ["CTRL = controller box (ESP32) in statue 1's base. BOX 2 = receiver box in statue 2's base.",
                      "Orange: per-tower data cable (DATA + GND) and 2-pin power feed from the box, in the trench under the statue.",
                      "Purple: 3 data cables between the boxes, buried with the mains. Placement and distances to be confirmed."],
            size=14)
    d.save("overview.svg", "Two statues of 7 towers, one controller, three data cables between the boxes.")


# --------------------------------------------------------------------------
# 2. Controller box (statue 1)
# --------------------------------------------------------------------------

def controller():
    d = Drawing(1600, 2200, "Controller box wiring (statue 1)")
    header(d, "Controller box — statue 1 (enclosure 100W-masterbox)",
           ["Signals only. Power: box-power.svg.",
            "14 channels: statue 1's 7 towers through 2 × 74AHCT125,",
            "statue 2's 7 towers as RS-485 on 3 RJ45 jacks."])
    legend(d, 960, 20, [("stripe", ORANGE, "RJ45 pigtail wires, T568B colours (striped = white/colour)")])

    ex, ew, etop, ebot = 150, 230, 220, 2050
    d.rect(ex, etop, ew, ebot - etop, fill="#eef7ee", stroke="#2e7d32")
    d.lines(ex + ew / 2, 860, ["ESP32", "dev board", "classic, no PSRAM", "runs WLED"],
            size=16, anchor="middle", fill="#2e7d32", weight="bold")
    d.lines(ex + ew / 2, 960, ["USB: flashing", "and debug only"], size=13, anchor="middle", fill="#555")
    for name, y in (("5V / VIN", 300), ("GND", 340)):
        d.pin(ex, y), d.text(ex + 10, y + 5, name, size=14, weight="bold")
    d.flag(ex, 300, "+5V", "left"), d.flag(ex, 340, "GND", "left")

    def gpio(ch, y):
        d.pin(ex + ew, y)
        d.text(ex + ew - 10, y + 5, f"GPIO {GPIO[ch]}", size=15, weight="bold", anchor="end")
        return (ex + ew, y)

    # statue 1: two buffers
    names = [("1A", 2, "1Y", 3), ("2A", 5, "2Y", 6), ("3A", 9, "3Y", 8), ("4A", 12, "4Y", 11)]
    bx = 560
    top = 220
    rows = []
    for chip, towers in (("74AHCT125 #1", TOWERS[:4]), ("74AHCT125 #2", TOWERS[4:])):
        gates = [(names[i][1], names[i][0], names[i][2], names[i][3], top + 50 + 60 * i) for i in range(len(towers))]
        note = "unused 4A (pin 12) → GND" if len(towers) < 4 else ""
        bot = buffer_chip(d, bx, top, gates, chip, note)
        for (pa, a, yn, py_, y), t in zip(gates, towers):
            ch = f"S1-{t}"
            d.wire([gpio(ch, y), (bx, y)], DATA_33, 3)
            d.wire([(bx + 220, y), (1150, y)], DATA_5, 3)
            d.resistor(950, y, "100 Ω", color=DATA_5)
            tower_exit(d, 1150, y, f"Tower {t} data", f"statue 1 · {TOWER_H[t]} mm tower · + GND")
        top = bot + 30

    # statue 2: transmitters
    G = top + 30
    for i, t in enumerate(TOWERS):
        y0 = G + i * 160
        mp = max485(d, 560, y0, f"TX · S2-{t}", ["RO", "RE", "DE", "DI"], ["VCC", "GND", "A", "B"])
        d.text(548, mp["RO"][1] + 5, "n/c", size=13, anchor="end", fill="#777")
        d.wire([mp["RE"], (530, mp["RE"][1]), (530, mp["DE"][1]), mp["DE"]], RED, 2)
        d.dot(530, mp["RE"][1], RED, 4), d.dot(530, mp["DE"][1], RED, 4)
        d.flag(530, (mp["RE"][1] + mp["DE"][1]) / 2, "+5V", "left")
        d.wire([gpio(f"S2-{t}", mp["DI"][1]), mp["DI"]], DATA_33, 3)
        d.wire([mp["VCC"], (800, mp["VCC"][1])], RED, 2), d.flag(800, mp["VCC"][1], "+5V", "right")
        d.wire([mp["GND"], (800, mp["GND"][1])], BLACK, 2), d.flag(800, mp["GND"][1], "GND", "right")
        j, ch = jack_of(t)
        pa, pb = CH_PINS[ch]
        pair_label(d, mp["A"][0], mp["A"][1], pa, j, "right")
        pair_label(d, mp["B"][0], mp["B"][1], pb, j, "right")
    for j in (1, 2, 3):
        jt = G + (j - 1) * 480 + 20
        jack_table(d, 1260, jt, f"RJ45 jack {j} → box 2 jack {j}", j)
        d.text(1410, jt + 48 + 26 * 8 + 22, "pins 7, 8 → GND", size=13, anchor="middle", fill="#555")
    d.save("controller-wiring.svg", "ESP32, two 74AHCT125, seven MAX485 transmitters and three RJ45 jacks in the controller box.")


# --------------------------------------------------------------------------
# 3. Box 2 (statue 2)
# --------------------------------------------------------------------------

def box2():
    d = Drawing(1700, 2030, "Box 2 wiring (statue 2)")
    header(d, "Box 2 — statue 2 (enclosure 100W-masterbox, no ESP32)",
           ["Signals only. Power: box-power.svg.",
            "7 receivers, one per tower. Jack N here = jack N at the controller",
            "(straight-through cables)."])
    legend(d, 960, 20, [("stripe", ORANGE, "RJ45 pigtail wires, T568B colours (striped = white/colour)")])
    mx = 820
    G = 300
    for i, t in enumerate(TOWERS):
        y0 = G + i * 240
        mp = max485(d, mx, y0, f"RX · S2-{t}", ["A", "B"], ["RO", "RE", "DE", "DI", "VCC", "GND"], w=200)
        j, ch = jack_of(t)
        pa, pb = CH_PINS[ch]
        ya, yb = mp["A"][1], mp["B"][1]
        pair_label(d, 640, ya, pa, j, "left"), d.wire([(640, ya), (mx, ya)], RJ45[pa][1], 5, stripe=RJ45[pa][2])
        pair_label(d, 640, yb, pb, j, "left"), d.wire([(640, yb), (mx, yb)], RJ45[pb][1], 5, stripe=RJ45[pb][2])
        # bias: A -> 560 -> GND (up), B -> 560 -> +5V (down)
        d.dot(700, ya), d.wire([(700, ya), (700, ya - 66)], BLACK, 2)
        d.resistor(700, ya - 36, "560 Ω", vertical=True)
        d.flag(700, ya - 66, "GND", "up")
        d.dot(760, yb), d.wire([(760, yb), (760, yb + 66)], RED, 2)
        d.resistor(760, yb + 36, "560 Ω", vertical=True, color=RED)
        d.flag(760, yb + 66, "+5V", "down")
        rx = mx + 200
        d.wire([mp["RE"], (rx + 30, mp["RE"][1]), (rx + 30, mp["DE"][1]), mp["DE"]], BLACK, 2)
        d.dot(rx + 30, mp["RE"][1], BLACK, 4), d.dot(rx + 30, mp["DE"][1], BLACK, 4)
        d.wire([(rx + 30, (mp["RE"][1] + mp["DE"][1]) / 2), (rx + 60, (mp["RE"][1] + mp["DE"][1]) / 2)], BLACK, 2)
        d.flag(rx + 60, (mp["RE"][1] + mp["DE"][1]) / 2, "GND", "right")
        d.text(rx + 12, mp["DI"][1] + 5, "n/c", size=13, fill="#777")
        d.wire([mp["VCC"], (rx + 30, mp["VCC"][1])], RED, 2), d.flag(rx + 30, mp["VCC"][1], "+5V", "right")
        d.wire([mp["GND"], (rx + 30, mp["GND"][1])], BLACK, 2), d.flag(rx + 30, mp["GND"][1], "GND", "right")
        ro = mp["RO"]
        d.wire([ro, (1390, ro[1])], DATA_5, 3)
        d.resistor(1300, ro[1], "100 Ω", color=DATA_5)
        tower_exit(d, 1390, ro[1], f"Tower {t} data", f"statue 2 · {TOWER_H[t]} mm tower · + GND")
    for j in (1, 2, 3):
        jack_table(d, 40, 300 + (j - 1) * 560, f"RJ45 jack {j} ← controller jack {j}", j)
        d.text(190, 300 + (j - 1) * 560 + 48 + 26 * 8 + 22, "pins 7, 8 → GND", size=13, anchor="middle", fill="#555")
    d.lines(40, 2005, ["Each receiver: 560 Ω A→GND and B→+5V hold the line idle-low when the controller is off, so the towers stay dark instead of flickering."],
            size=14, fill="#333")
    d.save("box2-wiring.svg", "Three RJ45 jacks, seven MAX485 receivers with idle bias, and seven tower data outputs in box 2.")


# --------------------------------------------------------------------------
# 4. Tower base
# --------------------------------------------------------------------------

def tower_base():
    d = Drawing(1500, 760, "Tower base wiring (all 14 towers)")
    header(d, "Tower base — the same in all 14 towers",
           ["One data channel in, split to the 4 faces. All 4 faces show the same pixels.",
            "Mounted in the 15 cm dark space at the bottom of the tower."])
    # cable in
    d.rect(40, 250, 230, 120, fill="#fff8e1", stroke="#b58900")
    d.lines(56, 280, ["Data cable from box", "DATA", "GND"], size=15, weight="bold")
    d.pin(270, 307), d.pin(270, 334)
    d.rect(40, 420, 230, 110, fill="#fde3e3", stroke=RED)
    d.lines(56, 450, ["Tower power (2-pin)", "+5V", "GND"], size=15, weight="bold", fill=RED)
    d.text(56, 515, "connector and wiring: TBD", size=12, fill="#555")
    d.wire([(270, 334), (330, 334)], BLACK, 3), d.flag(330, 334, "GND", "right")
    # pull-down + buffer
    x0 = 620
    ys = [240, 330, 420, 510]
    d.wire([(270, 307), (520, 307)], DATA_5, 3)
    d.dot(440, 307, DATA_5), d.wire([(440, 307), (440, 380)], BLACK, 2)
    d.resistor(440, 350, "10 kΩ", vertical=True)
    d.flag(440, 380, "GND", "down")
    d.wire([(520, ys[0]), (520, ys[-1])], DATA_5, 3)
    for y in ys:
        d.wire([(520, y), (x0, y)], DATA_5, 3)
    d.dot(520, 307, DATA_5)
    names = [("1A", 2, "1Y", 3), ("2A", 5, "2Y", 6), ("3A", 9, "3Y", 8), ("4A", 12, "4Y", 11)]
    gates = [(names[i][1], names[i][0], names[i][2], names[i][3], ys[i]) for i in range(4)]
    buffer_chip(d, x0, 190, gates, "74AHCT125", "")
    for i, y in enumerate(ys):
        d.wire([(x0 + 220, y), (1150, y)], DATA_5, 3)
        d.resistor(980, y, "100 Ω", color=DATA_5)
        d.rect(1150, y - 22, 300, 44, fill="#fff8e1", stroke="#b58900")
        d.pin(1150, y)
        d.text(1164, y - 2, f"Face {i + 1} strip · DIN", size=15, weight="bold")
        d.text(1164, y + 15, "5V / GND from the tower power", size=12, fill="#555")
    d.lines(40, 660, ["Strips run bottom to top: LED 0 at the base. 10 kΩ pull-down keeps the buffer input low (strips dark) if the data cable is unplugged.",
                      "74AHCT125 VCC from the tower's +5V; OE pins to GND. 100 Ω resistors optional."], size=14, fill="#333")
    d.save("tower-base.svg", "Tower base: data cable in, 10 k pull-down, 74AHCT125 splitting to four face strips.")


# --------------------------------------------------------------------------
# 5. Supply box (all 10)
# --------------------------------------------------------------------------

# Supplies per statue: name -> (sits at, feeds [(tower, faces)])
SUPPLIES = {
    "A": ("T2", [("T1", "1–4"), ("T2", "1–4")]),
    "B": ("T3", [("T3", "1–4")]),
    "C": ("T4", [("T4", "1–2")]),
    "D": ("T4", [("T4", "3–4"), ("T5", "1–2")]),
    "E": ("T6", [("T5", "3–4"), ("T6", "1–4"), ("T7", "1–4")]),
}


def power():
    d = Drawing(1400, 640, "Supply box wiring (all 10 supplies)")
    header(d, "Supply box — the same for all 10 supplies (5 per statue)",
           ["Mains into the box's C14; 5 V out to XT60 outputs, one pair per destination tower.",
            "Supply C sits in the apex box and also feeds the perfboard (ESP32 / transceivers)."])
    d.rect(180, 170, 260, 100, fill="#fff3e0", stroke="#e65100")
    d.lines(310, 205, ["C14 inlet", "1 A fuse + switch"], size=16, anchor="middle", weight="bold", fill="#e65100")
    d.rect(200, 440, 760, 140, fill="#eceff1", stroke="#455a64")
    d.text(580, 520, "S-100-5 · 5 V 20 A", size=18, anchor="middle", weight="bold", fill="#455a64")
    terms = [(260, "1 L"), (320, "2 N"), (380, "3 FG"), (520, "4 −V"), (580, "5 −V"), (660, "6 +V"), (720, "7 +V")]
    for x, lbl in terms:
        d.pin(x, 440), d.text(x, 470, lbl, size=13, anchor="middle", weight="bold")
    for x, col, lbl in ((260, "#8b5a2b", "L"), (320, BLUE, "N"), (380, "#2e9e44", "PE")):
        d.pin(x, 270), d.text(x, 262, lbl, size=13, anchor="middle", weight="bold")
        d.wire([(x, 270), (x, 440)], col, 5)
    d.wire([(380, 275), (380, 435)], "#f9d71c", 5)
    d.add('<polyline points="380,275 380,435" fill="none" stroke="#2e9e44" stroke-width="5" stroke-dasharray="10 10"/>')
    d.text(170, 340, "230 V AC", size=18, anchor="end", weight="bold", fill="#c62828")
    d.wire([(580, 440), (580, 400)], BLACK, 3), d.flag(580, 400, "GND", "up")
    d.wire([(720, 440), (720, 400)], RED, 3), d.flag(720, 400, "+5V", "up")
    d.text(770, 390, "← supply C only: perfboard rails, 0.5 mm²", size=13, fill="#555")
    d.wire([(520, 440), (520, 240), (1000, 240)], BLUE, 6)
    d.wire([(660, 440), (660, 290), (1000, 290)], RED, 6)
    d.text(700, 232, "−V (blue), 2.5 mm²", size=13, fill=BLUE)
    d.text(700, 314, "+5 V (red), 2.5 mm²", size=13, fill=RED)
    d.rect(1000, 200, 360, 130, fill="#fafafa", stroke="#999")
    d.lines(1016, 228, ["XT60 outputs: one per destination", "tower (or tower half), split to",
                        "that tower's strand XT60s at its base.", "Which outputs: statue-power.svg"],
            size=14, fill="#333")
    d.save("box-power.svg", "Supply box: C14 inlet, S-100-5, XT60 outputs per destination tower.")


# --------------------------------------------------------------------------
# 6. Statue power distribution
# --------------------------------------------------------------------------

def statue_power():
    d = Drawing(1600, 900, "Statue power distribution")
    header(d, "Statue power — the same at both statues",
           ["230 V from the outlet at the apex to 5 supply boxes; 5 V from each supply to its towers.",
            "Thick lines run in the trench; thin lines stay inside a base. Data cables: see the box diagrams."])
    tx = {"T1": 150, "T2": 360, "T3": 570, "T4": 800, "T5": 1030, "T6": 1240, "T7": 1450}
    ty = 520
    # towers
    split_note = {"T4": "1–2 ← C · 3–4 ← D", "T5": "1–2 ← D · 3–4 ← E"}
    for t, x in tx.items():
        d.rect(x - 60, ty, 120, 90, fill="#ffe0b2", stroke="#e65100")
        d.text(x, ty + 30, f"{t} · {TOWER_H[t]}", size=15, anchor="middle", weight="bold")
        d.text(x, ty + 52, split_note.get(t, "all 4 faces"), size=12, anchor="middle", fill="#555")
        d.text(x, ty + 72, "XT60 per face", size=11, anchor="middle", fill="#777")
    d.text(800, ty + 110, "T4: + top feed up the post (faces 1–2 from C, 3–4 from D)", size=13, anchor="middle", fill=RED)
    # supplies
    sx = {"A": 360, "B": 570, "C": 735, "D": 865, "E": 1240}
    sw = {"A": 150, "B": 150, "C": 110, "D": 110, "E": 150}
    sy0, sy1 = 300, 380
    for n, x in sx.items():
        box = "apex box" if n == "C" else "100W box"
        d.rect(x - sw[n] / 2, sy0, sw[n], sy1 - sy0, fill="#eceff1", stroke="#455a64")
        d.text(x, sy0 + 28, f"Supply {n}", size=15, anchor="middle", weight="bold", fill="#455a64")
        d.text(x, sy0 + 50, box, size=12, anchor="middle", fill="#555")
        d.text(x, sy0 + 68, "S-100-5", size=12, anchor="middle", fill="#555")
    # ground bond between supplies
    bond = [(sx["A"] + 75, 340), (sx["B"] - 75, 340)], [(sx["B"] + 75, 340), (sx["C"] - 55, 340)], \
           [(sx["C"] + 55, 340), (sx["D"] - 55, 340)], [(sx["D"] + 55, 340), (sx["E"] - 75, 340)]
    for seg in bond:
        d.add(f'<polyline points="{seg[0][0]},{seg[0][1]} {seg[1][0]},{seg[1][1]}" fill="none" stroke="{BLACK}" '
              f'stroke-width="3" stroke-dasharray="8 6"/>')
    # mains
    d.rect(700, 135, 200, 50, fill="#fff3e0", stroke="#e65100")
    d.lines(800, 156, ["230 V outlet + strip", "at the apex"], size=14, anchor="middle", weight="bold", fill="#e65100")
    MAINS = "#8b5a2b"
    d.wire([(760, 185), (760, sy0)], MAINS, 2), d.wire([(840, 185), (840, sy0)], MAINS, 2)
    d.wire([(720, 185), (720, 235), (sx["B"], 235), (sx["B"], sy0)], MAINS, 6)
    d.wire([(705, 185), (705, 210), (sx["A"], 210), (sx["A"], sy0)], MAINS, 6)
    d.wire([(880, 185), (880, 220), (sx["E"], 220), (sx["E"], sy0)], MAINS, 6)
    d.text(470, 203, "230 V → A", size=13, anchor="middle", fill=MAINS, weight="bold")
    d.text(640, 253, "230 V → B", size=13, anchor="middle", fill=MAINS, weight="bold")
    d.text(1060, 213, "230 V → E", size=13, anchor="middle", fill=MAINS, weight="bold")
    # 5 V
    def feed(pts, thick, label=None, lx=None, ly=None):
        d.wire(pts, RED, 6 if thick else 2)
        if label:
            d.text(lx, ly, label, size=12, anchor="middle", fill=RED, weight="bold")
    feed([(sx["A"] + 20, sy1), (sx["A"] + 20, ty)], False)
    feed([(sx["A"] - 40, sy1), (sx["A"] - 40, 450), (tx["T1"], 450), (tx["T1"], ty)], True, "3×2.5", 230, 442)
    feed([(sx["B"], sy1), (sx["B"], ty)], False)
    feed([(sx["C"] + 35, sy1), (sx["C"] + 35, ty)], False)
    feed([(sx["D"] - 20, sy1), (sx["D"] - 20, ty)], False)
    feed([(sx["D"] + 30, sy1), (sx["D"] + 30, 440), (tx["T5"] - 30, 440), (tx["T5"] - 30, ty)], True, "3×2.5", 960, 432)
    feed([(sx["E"] - 50, sy1), (sx["E"] - 50, 450), (tx["T5"] + 30, 450), (tx["T5"] + 30, ty)], True, "3×2.5", 1130, 442)
    feed([(sx["E"], sy1), (sx["E"], ty)], False)
    feed([(sx["E"] + 50, sy1), (sx["E"] + 50, 450), (tx["T7"], 450), (tx["T7"], ty)], True, "3×2.5", 1370, 442)
    # legend
    d.rect(60, 690, 1480, 190, fill="#fafafa", stroke="#bbb", sw=1)
    rows = [(MAINS, 6, False, "230 V, buried: H07RN-F 3×1.5 cord with C13 → C14 inlet of the supply box"),
            (MAINS, 2, False, "230 V inside the apex base"),
            (RED, 6, False, "5 V, buried: 3-core cable, brown +5 V, blue GND, green/yellow unused or GND; XT60 at both ends"),
            (RED, 2, False, "5 V inside a base"),
            (BLACK, 3, True, "ground bond: all supply −V tied together (1.5 mm², in the trench)")]
    for i, (col, w, dash, txt) in enumerate(rows):
        y = 720 + 34 * i
        if dash:
            d.add(f'<polyline points="80,{y} 150,{y}" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="8 6"/>')
        else:
            d.wire([(80, y), (150, y)], col, w)
        d.text(170, y + 5, txt, size=14)
    d.save("statue-power.svg", "Mains from the apex to five supplies per statue, and 5 V from each supply to its towers.")


if __name__ == "__main__":
    overview()
    controller()
    box2()
    tower_base()
    power()
    statue_power()
