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
# the other; T4 is the apex. Heights in mm: the artist's current sizes (2026-10-18).
TOWER_H = {"T1": 1100, "T2": 1400, "T3": 1700, "T4": 2000, "T5": 1700, "T6": 1400, "T7": 1100}  # artist, final, 2026-10-21
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

# Supplies per statue: name -> (box sits at, own tower, neighbour towers fed from it).
# C is inside the apex box. Neighbour towers have no electronics: power arrives
# on XT60 (3 x 2.5), data already buffered on a 22 AWG pair.
SUPPLIES = {
    "A": ("T2", "T2", ["T1"]),
    "B": ("T3", "T3", []),
    "C": ("T4", "T4", []),
    "D": ("T5", "T5", []),
    "E": ("T6", "T6", ["T7"]),
}


def box_of(tower):
    for n, (at, own, nb) in SUPPLIES.items():
        if tower == own or tower in nb:
            return n, at
    raise KeyError(tower)


def dest_of(tower):
    n, at = box_of(tower)
    if n == "C":
        return "T4 splitter, in this box"
    return f"to supply box {n} at {at}"


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


BUF_GATES = [("1A", 2, "1Y", 3), ("2A", 5, "2Y", 6), ("3A", 9, "3Y", 8), ("4A", 12, "4Y", 11)]
BUF_OE = [(1, "1OE"), (4, "2OE"), (10, "3OE"), (13, "4OE")]


def buffer_chip(d, x, top, used, title, gap=60):
    """74AHCT125 with all 14 pins. Gates 1..used carry signals; the rest get
    their input grounded and output left open. Returns ({gate: y}, bottom y)."""
    bw, pitch = 220, 26
    gy = {i: top + 50 + gap * i for i in range(4)}
    py0 = gy[3] + 60
    bot = py0 + pitch * 3 + 60
    d.rect(x, top, bw, bot - top, fill="#f3e5f5", stroke=DATA_5)
    for i, (a, pa, yn, py_) in enumerate(BUF_GATES):
        y = gy[i]
        d.pin(x, y), d.text(x + 10, y + 5, f"{pa} · {a}", size=14, weight="bold")
        d.pin(x + bw, y), d.text(x + bw - 10, y + 5, f"{yn} · {py_}", size=14, weight="bold", anchor="end")
        if i >= used:
            d.wire([(x, y), (x - 30, y)], BLACK, 2), d.flag(x - 30, y, "GND", "left")
            d.text(x + bw + 12, y + 5, "n/c", size=13, fill="#777")
    # output enables (active low): all tied to GND
    bus = x - 30
    for i, (pn, n) in enumerate(BUF_OE):
        y = py0 + pitch * i
        d.pin(x, y), d.text(x + 10, y + 5, f"{pn} · {n}", size=14, weight="bold")
        d.wire([(x, y), (bus, y)], BLACK, 2)
        if 0 < i < 3:
            d.dot(bus, y, BLACK, 4)
    d.wire([(bus, py0), (bus, py0 + pitch * 3)], BLACK, 2)
    d.flag(bus, py0 + pitch * 1.5, "GND", "left")
    # supply
    for i, (pn, n, net, col) in enumerate(((14, "VCC", "+5V", RED), (7, "GND", "GND", BLACK))):
        y = py0 + pitch * i
        d.pin(x + bw, y), d.text(x + bw - 10, y + 5, f"{n} · {pn}", size=14, weight="bold", anchor="end")
        d.wire([(x + bw, y), (x + bw + 40, y)], col, 2), d.flag(x + bw + 40, y, net, "right")
    d.text(x + bw / 2, bot - 22, title, size=15, anchor="middle", weight="bold", fill=DATA_5)
    return gy, bot


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
        for n, (_, own, nb) in SUPPLIES.items():
            if n != "C":
                d.wire([(bx, by), pos[own]], led, 2)
            for t in nb:
                d.wire([pos[own], pos[t]], "#c62828", 4)
        for t, (x, y) in pos.items():
            sz = 12 + TOWER_H[t] / 100
            d.rect(x - sz / 2, y - sz / 2, sz, sz, fill="#ffe0b2", stroke="#e65100", sw=2, rx=3)
            d.text(x + s * (sz / 2 + 6), y + 5, t, size=13, anchor="start" if s > 0 else "end", weight="bold")
            if any(own == t for _, own, _ in SUPPLIES.values()) and t != "T4":
                n = box_of(t)[0]
                d.rect(x - s * (sz / 2 + 30) - 11, y - 11, 22, 22, fill="#eceff1", stroke="#455a64", rx=3)
                d.text(x - s * (sz / 2 + 30), y + 5, n, size=12, anchor="middle", weight="bold", fill="#455a64")
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
    d.lines(80, 896, ["CTRL / BOX 2 = apex box (with supply C) in statue 1 / 2. Grey A, B, D, E = supply boxes at T2, T3, T5, T6.",
                      "Orange: data (DATA + GND) and 230 V from the apex box to supply boxes A, B, D, E. Red: power + data to T1, T7.",
                      "Purple: 3 data cables between the apex boxes. Placement and distances to be confirmed."],
            size=14)
    d.save("overview.svg", "Two statues of 7 towers, one controller, three data cables between the boxes.")


# --------------------------------------------------------------------------
# 2. Controller box (statue 1)
# --------------------------------------------------------------------------

def controller():
    d = Drawing(1600, 2460, "Controller box wiring (statue 1)")
    header(d, "Controller box — statue 1 (enclosure 100W-masterbox)",
           ["Signals only. Power: statue-power.svg, supply-box.svg.",
            "14 channels: statue 1's 7 towers through 2 × 74AHCT125,",
            "statue 2's 7 towers as RS-485 on 3 RJ45 jacks."])
    legend(d, 960, 20, [("stripe", ORANGE, "RJ45 pigtail wires, T568B colours (striped = white/colour)")])

    ex, ew, etop, ebot = 150, 230, 220, 2310
    d.rect(ex, etop, ew, ebot - etop, fill="#eef7ee", stroke="#2e7d32")
    d.lines(ex + ew / 2, 1000, ["ESP32", "dev board", "classic, no PSRAM", "runs WLED"],
            size=16, anchor="middle", fill="#2e7d32", weight="bold")
    d.lines(ex + ew / 2, 1100, ["USB: flashing", "and debug only"], size=13, anchor="middle", fill="#555")
    for name, y in (("5V / VIN", 300), ("GND", 340)):
        d.pin(ex, y), d.text(ex + 10, y + 5, name, size=14, weight="bold")
    d.flag(ex, 300, "+5V", "left"), d.flag(ex, 340, "GND", "left")

    def gpio(ch, y):
        d.pin(ex + ew, y)
        d.text(ex + ew - 10, y + 5, f"GPIO {GPIO[ch]}", size=15, weight="bold", anchor="end")
        return (ex + ew, y)

    # statue 1: two buffers
    bx = 560
    top = 220
    for chip, towers in (("74AHCT125 #1", TOWERS[:4]), ("74AHCT125 #2", TOWERS[4:])):
        gy, bot = buffer_chip(d, bx, top, len(towers), chip)
        for i, t in enumerate(towers):
            y = gy[i]
            ch = f"S1-{t}"
            d.wire([gpio(ch, y), (bx, y)], DATA_33, 3)
            d.wire([(bx + 220, y), (1150, y)], DATA_5, 3)
            d.resistor(950, y, "100 Ω", color=DATA_5)
            tower_exit(d, 1150, y, f"Tower {t} data", f"{dest_of(t)} · + GND")
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
           ["Signals only. Power: statue-power.svg, supply-box.svg.",
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
        tower_exit(d, 1390, ro[1], f"Tower {t} data", f"{dest_of(t)} · + GND")
    for j in (1, 2, 3):
        jack_table(d, 40, 300 + (j - 1) * 560, f"RJ45 jack {j} ← controller jack {j}", j)
        d.text(190, 300 + (j - 1) * 560 + 48 + 26 * 8 + 22, "pins 7, 8 → GND", size=13, anchor="middle", fill="#555")
    d.lines(40, 2005, ["Each receiver: 560 Ω A→GND and B→+5V hold the line idle-low when the controller is off, so the towers stay dark instead of flickering."],
            size=14, fill="#333")
    d.save("box2-wiring.svg", "Three RJ45 jacks, seven MAX485 receivers with idle bias, and seven tower data outputs in box 2.")


# --------------------------------------------------------------------------
# 4. Tower base
# --------------------------------------------------------------------------

def jst_block(d, x, y, title, sub, pins, w=300):
    """JST-SM 3-pin block; pins: list of (label, net) top to bottom. Returns {label: (x, y)}."""
    h = 40 + 24 * len(pins)
    d.rect(x, y, w, h, fill="#fff8e1", stroke="#b58900")
    d.text(x + 14, y + 22, title, size=15, weight="bold")
    if sub:
        d.text(x + w - 12, y + 22, sub, size=12, anchor="end", fill="#555")
    pts = {}
    for i, (lbl, net) in enumerate(pins):
        py = y + 44 + 24 * i
        d.pin(x, py), d.text(x + 14, py + 5, lbl, size=13, weight="bold")
        if net:
            d.text(x + 90, py + 5, net, size=12, fill="#555")
        pts[lbl] = (x, py)
    return pts


def supply_box():
    d = Drawing(1600, 1640, "Supply box wiring")
    header(d, "Supply box — A, B, D, E (and C, inside the apex box)",
           ["Mains in, the box's own tower out on 4 JST-SM (one per face) and a top feed (XT60), and for",
            "boxes A and E the neighbouring tip tower's power (XT60) and buffered data. Same pixels on all 4 faces."])
    # own tower: data in -> pull-down -> buffer #1 -> 4 faces
    din = jst_block(d, 40, 190, "JST-SM in · own tower data", "from apex box",
                    [("DATA", ""), ("GND", ""), ("5V", "not connected")], w=330)
    d.wire([din["GND"], (400, din["GND"][1])], BLACK, 2), d.flag(400, din["GND"][1], "GND", "right")
    dy = din["DATA"][1]
    x0 = 640
    gy, bot = buffer_chip(d, x0, 170, 4, "74AHCT125 #1 · own tower", gap=90)
    d.wire([din["DATA"], (540, dy)], DATA_5, 3)
    d.dot(460, dy, DATA_5), d.wire([(460, dy), (460, dy + 70)], BLACK, 2)
    d.resistor(460, dy + 40, "10 kΩ", vertical=True), d.flag(460, dy + 70, "GND", "down")
    d.wire([(540, gy[0]), (540, gy[3])], DATA_5, 3)
    for i in range(4):
        d.wire([(540, gy[i]), (x0, gy[i])], DATA_5, 3)
    d.dot(540, dy, DATA_5)
    for i in range(4):
        y = gy[i]
        d.wire([(x0 + 220, y), (1200, y)], DATA_5, 3)
        d.resistor(1060, y, "100 Ω", color=DATA_5)
        d.rect(1200, y - 24, 360, 48, fill="#fff8e1", stroke="#b58900")
        d.pin(1200, y)
        d.text(1214, y - 3, f"JST-SM out · face {i + 1} strand", size=15, weight="bold")
        d.text(1214, y + 16, "DATA here · 5V/GND from the +5V/GND rails", size=12, fill="#555")
    # neighbours (A: T1; D: T5, T7)
    top2 = bot + 60
    d.rect(30, top2 - 30, 1540, 3, fill="#bbb", stroke="none", rx=0)
    d.text(40, top2 - 6, "Boxes A and E only: the neighbouring tip tower (A → T1; E → T7)", size=15, weight="bold", fill="#555")
    gy2, bot2 = buffer_chip(d, x0, top2 + 20, 1, "74AHCT125 #2 · neighbour", gap=60)
    for k, (lbl, which) in enumerate((("neighbour", "A: T1 · E: T7"),)):
        yy = top2 + 30 + 130 * k
        pin = jst_block(d, 40, yy, f"JST-SM in · {lbl} data", which, [("DATA", ""), ("GND", "")], w=330)
        d.wire([pin["GND"], (400, pin["GND"][1])], BLACK, 2), d.flag(400, pin["GND"][1], "GND", "right")
        py = pin["DATA"][1]
        d.dot(470, py, DATA_5), d.wire([(470, py), (470, py + 60)], BLACK, 2)
        d.resistor(470, py + 34, "10 kΩ", vertical=True), d.flag(470, py + 60, "GND", "down")
        d.wire([pin["DATA"], (560, py), (560, gy2[k]), (x0, gy2[k])], DATA_5, 3)
        y = gy2[k]
        d.wire([(x0 + 220, y), (1200, y)], DATA_5, 3)
        d.resistor(1060, y, "100 Ω", color=DATA_5)
        d.rect(1200, y - 24, 360, 48, fill="#fff8e1", stroke="#b58900")
        d.pin(1200, y)
        d.text(1214, y - 3, f"Data out · {lbl}", size=15, weight="bold")
        d.text(1214, y + 16, "22 AWG pair (DATA + GND) to its tower", size=12, fill="#555")
    # power
    top3 = bot2 + 50
    d.rect(30, top3 - 30, 1540, 3, fill="#bbb", stroke="none", rx=0)
    d.rect(40, top3, 220, 90, fill="#fff3e0", stroke="#e65100")
    d.lines(150, top3 + 38, ["C14 inlet", "1 A fuse + switch"], size=15, anchor="middle", weight="bold", fill="#e65100")
    d.rect(420, top3, 420, 110, fill="#eceff1", stroke="#455a64")
    d.text(630, top3 + 50, "S-100-5 · 5 V 20 A", size=18, anchor="middle", weight="bold", fill="#455a64")
    d.text(630, top3 + 74, "L · N · FG   |   −V −V +V +V", size=13, anchor="middle", fill="#555")
    for k, (col, lbl) in enumerate((("#8b5a2b", "L"), (BLUE, "N"), ("#2e9e44", "PE"))):
        yy = top3 + 25 + 22 * k
        d.wire([(260, yy), (420, yy)], col, 4)
        d.text(340, yy - 4, lbl, size=12, anchor="middle", weight="bold")
    d.wire([(840, top3 + 30), (920, top3 + 30)], RED, 6), d.flag(920, top3 + 30, "+5V", "right")
    d.wire([(840, top3 + 80), (920, top3 + 80)], BLUE, 6), d.flag(920, top3 + 80, "GND", "right")
    d.text(930, top3 + 60, "rails: NYAF 2.5 mm², red / blue", size=12, fill="#555")
    d.rect(1200, top3 - 10, 360, 130, fill="#fde3e3", stroke=RED)
    d.lines(1214, top3 + 16, ["XT60 out · neighbour power", "A: to T1 · E: to T7",
                              "3 × 2.5 cable, brown +5 V, blue GND", "B, C, D: none"], size=13, fill="#333")
    d.rect(1200, top3 + 140, 360, 130, fill="#fde3e3", stroke=RED)
    d.lines(1214, top3 + 166, ["XT60 out · top feed, own tower", "3 × 2.5 cable up the post, WAGOs",
                               "at the top → 4 × XT60 to the strand tops", "every box: A, B, C, D, E"], size=13, fill="#333")
    d.lines(40, top3 + 310, ["All flags with the same label are the same wire. The data inputs' 5V pins stay unconnected so two supplies never join on +5 V.",
                             "Box C: the same circuit inside the apex box (its own tower is T4), plus the perfboard feed for the ESP32 / transceivers.",
                             "100 Ω resistors optional. The neighbours' data shares one buffer gate per tower; it is split to 4 faces at that tower's base."],
            size=14, fill="#333")
    d.save("supply-box.svg", "Supply box: mains, S-100-5, own tower's 74AHCT125 to 4 JST-SM strands, neighbour power and data.")


def neighbour_base():
    d = Drawing(1400, 620, "Neighbour tower base (T1, T7)")
    header(d, "Neighbour tower base — T1, T7 (no electronics)",
           ["Power and buffered data arrive from the supply box next door and are split to the 4 faces.",
            "Inside the 15 cm dark space at the bottom of the tower."])
    d.rect(40, 180, 300, 110, fill="#fde3e3", stroke=RED)
    d.lines(56, 210, ["XT60 in · from supply box", "+5V (brown)", "GND (blue)"], size=15, weight="bold", fill=RED)
    d.pin(340, 237), d.pin(340, 262)
    d.rect(40, 340, 300, 110, fill="#fff8e1", stroke="#b58900")
    d.lines(56, 370, ["Data in · 22 AWG pair", "DATA", "GND"], size=15, weight="bold")
    d.pin(340, 397), d.pin(340, 422)
    # WAGO rails
    d.rect(470, 200, 120, 40, fill="#fff", stroke=RED), d.text(530, 226, "WAGO +5V", size=13, anchor="middle", fill=RED, weight="bold")
    d.rect(470, 260, 120, 40, fill="#fff", stroke=BLUE), d.text(530, 286, "WAGO GND", size=13, anchor="middle", fill=BLUE, weight="bold")
    d.wire([(340, 237), (420, 237), (420, 220), (470, 220)], RED, 5)
    d.wire([(340, 262), (420, 262), (420, 280), (470, 280)], BLUE, 5)
    d.wire([(340, 422), (440, 422), (440, 300)], BLACK, 2), d.dot(440, 300, BLACK)
    d.wire([(440, 300), (470, 300)], BLACK, 2)
    d.text(352, 445, "joins GND", size=11, fill="#555")
    # data bus
    d.wire([(340, 397), (700, 397)], DATA_5, 3)
    ys = [170, 260, 350, 440]
    d.wire([(700, ys[0]), (700, ys[-1])], DATA_5, 3), d.dot(700, 397, DATA_5)
    for i, y in enumerate(ys):
        d.wire([(700, y), (1000, y)], DATA_5, 3)
        d.rect(1000, y - 28, 360, 56, fill="#fff8e1", stroke="#b58900")
        d.pin(1000, y)
        d.text(1014, y - 6, f"JST-SM out · face {i + 1} strand", size=15, weight="bold")
        d.text(1014, y + 14, "DATA here · 5V/GND from the WAGOs", size=12, fill="#555")
    d.wire([(590, 220), (640, 220)], RED, 3), d.flag(640, 220, "+5V", "right")
    d.wire([(590, 280), (640, 280)], BLUE, 3), d.flag(640, 280, "GND", "right")
    d.lines(40, 520, ["The 4 faces share one buffered data line from the supply box (a short on one face's data lead darkens all 4).",
                      "+5V / GND flags: the WAGO outputs to each face's JST-SM (22 AWG pigtails are fine over < 0.5 m)."],
            size=14, fill="#333")
    d.save("neighbour-base.svg", "Neighbour tower base: XT60 power and buffered data split passively to four JST-SM strands.")


def statue_power():
    d = Drawing(1600, 920, "Statue power and data distribution")
    header(d, "Statue power and data — the same at both statues",
           ["Mains from the apex to 5 supply boxes; each box drives its own tower, A and E also the tip towers.",
            "Thick lines run in the trench; thin lines stay inside a base."])
    tx = {"T1": 150, "T2": 360, "T3": 570, "T4": 800, "T5": 1030, "T6": 1240, "T7": 1450}
    ty = 540
    for t, x in tx.items():
        own = any(own == t for _, own, _ in SUPPLIES.values())
        d.rect(x - 60, ty, 120, 90, fill="#ffe0b2", stroke="#e65100")
        d.text(x, ty + 30, f"{t} · {TOWER_H[t]}", size=15, anchor="middle", weight="bold")
        d.text(x, ty + 52, "4 × JST-SM", size=12, anchor="middle", fill="#555")
        d.text(x, ty + 72, "own box" if own else "passive base", size=11, anchor="middle", fill="#777")
    sx = {n: tx[own] for n, (_, own, _) in SUPPLIES.items()}
    sy0, sy1 = 320, 400
    for n, x in sx.items():
        d.rect(x - 75, sy0, 150, sy1 - sy0, fill="#eceff1", stroke="#455a64")
        d.text(x, sy0 + 28, f"Supply box {n}", size=15, anchor="middle", weight="bold", fill="#455a64")
        d.text(x, sy0 + 50, "apex box" if n == "C" else "100W box", size=12, anchor="middle", fill="#555")
        d.text(x, sy0 + 68, "S-100-5", size=12, anchor="middle", fill="#555")
    MAINS = "#8b5a2b"
    d.rect(700, 135, 200, 50, fill="#fff3e0", stroke="#e65100")
    d.lines(800, 156, ["230 V in + strip", "at the apex"], size=14, anchor="middle", weight="bold", fill="#e65100")
    d.wire([(800, 185), (800, sy0)], MAINS, 2)
    left = sorted([n for n in sx if sx[n] < 800], key=lambda n: -sx[n])
    right = sorted([n for n in sx if sx[n] > 800], key=lambda n: sx[n])
    for side, names in ((-1, left), (1, right)):
        for k, n in enumerate(names):
            x0, y = 800 + side * (25 + 18 * k), 245 - 30 * k
            d.wire([(x0, 185), (x0, y), (sx[n], y), (sx[n], sy0)], MAINS, 6)
            d.text((x0 + sx[n]) / 2, y - 7, f"230 V → {n}", size=13, anchor="middle", fill=MAINS, weight="bold")
    # own towers (thin) and neighbours (thick)
    for n, (_, own, nb) in SUPPLIES.items():
        x = sx[n]
        d.wire([(x, sy1), (x, ty)], RED, 2)
        for t in nb:
            off = -40 if tx[t] < x else 40
            d.wire([(x + off, sy1), (x + off, 470), (tx[t], 470), (tx[t], ty)], RED, 6)
            d.text((x + off + tx[t]) / 2, 462, "XT60 · 3×2.5 + data", size=12, anchor="middle", fill=RED, weight="bold")
    d.rect(60, 700, 1480, 200, fill="#fafafa", stroke="#bbb", sw=1)
    rows = [(MAINS, 6, "230 V, buried: H07RN-F 3×1.5 cord with C13 → the supply box's C14"),
            (MAINS, 2, "230 V inside the apex base (box C)"),
            (RED, 6, "to a neighbour tower, buried: 5 V on 3×2.5 with XT60 both ends, plus a 22 AWG data pair"),
            (RED, 2, "own tower: 4 JST-SM from the box straight to the 4 strands (5V, DATA, GND)")]
    for i, (col, w, txt) in enumerate(rows):
        y = 730 + 34 * i
        d.wire([(80, y), (150, y)], col, w)
        d.text(170, y + 5, txt, size=14)
    d.text(80, 880, "Data to boxes A, B, D, E: one DATA + GND line per tower from the apex box, in the same trenches (see the trench table).",
           size=14, fill="#333")
    d.save("statue-power.svg", "Mains from the apex to five supply boxes per statue; own towers and the tip towers.")


if __name__ == "__main__":
    overview()
    controller()
    box2()
    supply_box()
    neighbour_base()
    statue_power()
