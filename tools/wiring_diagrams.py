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

# One channel per tower. Statue 1 is local to the master box; statue 2's
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
    4: ("blue", BLUE, False, ("B", 3)),
    5: ("w/blue", BLUE, True, ("A", 3)),
    6: ("green", GREEN, False, ("B", 2)),
    7: ("w/brown", BROWN, True, ("GND", None)),
    8: ("brown", BROWN, False, ("GND", None)),
}
CH_PINS = {1: (1, 2), 2: (3, 6), 3: (5, 4)}   # channel in a cable -> (A pin, B pin); striped wire = A
# jack -> statue-2 tower per channel (orange, green, blue pair; None = spare), as built (owner, 2026-10-28)
JACKS = {1: ["T6", "T7", None], 2: ["T4", "T5", None], 3: ["T3", "T2", "T1"]}

# Power boxes per statue, named by the tower they sit in (owner, 2026-10-25; formerly A-E):
# name -> (box sits at, own tower, tip towers fed from it). T4's is inside the master/slave box. A tip tower has no electronics: one cable
# from the box (XT60 power on 3 x 2.5, data already buffered on a 22 AWG pair) ends in its 4 JST-SM.
SUPPLIES = {
    "T2": ("T2", "T2", ["T1"]),
    "T3": ("T3", "T3", []),
    "T4": ("T4", "T4", []),
    "T5": ("T5", "T5", []),
    "T6": ("T6", "T6", ["T7"]),
}


def box_of(tower):
    for n, (at, own, nb) in SUPPLIES.items():
        if tower == own or tower in nb:
            return n, at
    raise KeyError(tower)


def dest_of(tower):
    n, at = box_of(tower)
    if n == "T4":
        return "T4 splitter, in this box"
    return f"to the power box in {at}"


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
        # 230 V: extension cords chained tower to tower along each arm, a power strip at each (owner, 2026-10-29)
        for a, b in (("T4", "T3"), ("T3", "T2"), ("T4", "T5"), ("T5", "T6")):
            d.wire([pos[a], pos[b]], "#8b5a2b", 5)
        for n, (_, own, nb) in SUPPLIES.items():
            if n != "T4":
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
                d.text(x - s * (sz / 2 + 30), y + 5, "P", size=12, anchor="middle", weight="bold", fill="#455a64")
        d.rect(bx - 34, by - 22, 68, 44, fill=box_col, stroke="#333")
        d.text(bx, by + 5, box_label, size=12, anchor="middle", weight="bold", fill="#fff")
        d.text(apex_x, cy - 230, label, size=17, anchor="middle", weight="bold")
        return bx, by

    b1 = statue(cx - r + 40, 1, "Statue 1", "#2e7d32", "MASTER")
    b2 = statue(cx + r - 40, -1, "Statue 2", "#1565c0", "SLAVE")
    for dy in (-12, 0, 12):
        d.wire([(b1[0] - 34, b1[1] + dy), (b1[0] - 60, b1[1] + dy), (b1[0] - 60, cy + 300 + dy),
                (b2[0] + 60, cy + 300 + dy), (b2[0] + 60, b2[1] + dy), (b2[0] + 34, b2[1] + dy)], cable, 4)
    d.rect(cx - 150, cy + 312, 300, 30, fill="#fff", stroke=cable, sw=1.5)
    d.text(cx, cy + 333, "3 × CAT5e, jacks 1–3 → jacks 1–3", size=14, anchor="middle", fill=cable, weight="bold")
    d.rect(60, 862, 1080, 112, fill="#fafafa", stroke="#bbb", sw=1)
    d.lines(80, 886, ["MASTER / SLAVE = the master box (statue 1) / slave box (statue 2), each with the power box in T4 inside. Grey P = the power box in T2, T3, T5, T6.",
                      "Orange: data (DATA + GND) from the master/slave box to each power box. Red: the tip-tower cables to T1, T7.",
                      "Brown: 230 V on extension cords chained tower to tower (apex → T3 → T2, apex → T5 → T6), a power strip at each tower with a box.",
                      "Purple: 3 data cables between the master and slave boxes. Placement and distances to be confirmed."],
            size=14)
    d.save("overview.svg", "Two statues of 7 towers, one controller, three data cables between the boxes.")


# --------------------------------------------------------------------------
# 2. Master box (statue 1)
# --------------------------------------------------------------------------

def master_box():
    d = Drawing(1600, 2460, "Master box wiring (statue 1)")
    header(d, "Master box — statue 1 (enclosure 100W-masterbox)",
           ["Signals only. Power: statue-power.svg, power-box-1-tower.svg, power-box-2-tower.svg.",
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
        jack_table(d, 1260, jt, f"RJ45 jack {j} → slave box jack {j}", j)
        d.text(1410, jt + 48 + 26 * 8 + 22, "pins 7, 8 → GND", size=13, anchor="middle", fill="#555")
    d.save("master-box-wiring.svg", "ESP32, two 74AHCT125, seven MAX485 transmitters and three RJ45 jacks in the master box.")


# --------------------------------------------------------------------------
# 3. Slave box (statue 2)
# --------------------------------------------------------------------------

def slave_box():
    d = Drawing(1700, 2030, "Slave box wiring (statue 2)")
    header(d, "Slave box — statue 2 (enclosure 100W-masterbox, no ESP32)",
           ["Signals only. Power: statue-power.svg, power-box-1-tower.svg, power-box-2-tower.svg.",
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
        jack_table(d, 40, 300 + (j - 1) * 560, f"RJ45 jack {j} ← master box jack {j}", j)
        d.text(190, 300 + (j - 1) * 560 + 48 + 26 * 8 + 22, "pins 7, 8 → GND", size=13, anchor="middle", fill="#555")
    d.lines(40, 2005, ["Each receiver: 560 Ω A→GND and B→+5V hold the line idle-low when the controller is off, so the towers stay dark instead of flickering."],
            size=14, fill="#333")
    d.save("slave-box-wiring.svg", "Three RJ45 jacks, seven MAX485 receivers with idle bias, and seven tower data outputs in the slave box.")


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


def power_box(two):
    """One drawing per kind of power box, so the builder sees only what goes into the
    box in front of them: two=False is the 1 tower power box (T3, T5), two=True the
    2 tower power box (T2, T6), which also drives the tip-tower cable from gate 2 of
    the same 74AHCT125. One chip per box; gate 1's output is joined to all 4 faces
    (owner, 2026-10-29)."""
    kind = "2 tower power box" if two else "1 tower power box"
    where = "in T2 and T6 of each statue, 4 to build" if two else "in T3 and T5 of each statue, 4 to build"
    bot = 170 + 248 + 3 * 60          # buffer_chip is 248 + 3*gap tall
    top3 = bot + 50
    H = top3 + (640 if two else 520)
    d = Drawing(1600, H, f"{kind} wiring")
    if two:
        header(d, f"{kind} — {where}",
               ["Mains in. One 74AHCT125, 2 gates used: gate 1 → its own tower's 4 JST-SM (one per face), gate 2 → the tip tower",
                "next door (in T2: T1 · in T6: T7) through the tip-tower cable, which also carries its power from a second XT60."])
    else:
        header(d, f"{kind} — {where}",
               ["Mains in. One 74AHCT125, 1 gate used: gate 1 → its own tower's 4 JST-SM (one per face). One XT60 out for the top feed.",
                "Nothing for a tip tower. (T4's power box is this same circuit inside the master/slave box.)"])
    x0 = 640
    gy, b1 = buffer_chip(d, x0, 170, 2 if two else 1, f"74AHCT125 · {'2 gates' if two else '1 gate'} used", gap=60)
    assert b1 == bot
    # own tower: data in -> pull-down -> gate 1 -> joined -> 4 faces
    din = jst_block(d, 40, 190, "JST-SM in · own tower data", "",
                    [("DATA", ""), ("GND", ""), ("5V", "not connected")], w=330)
    d.text(40, 322, "the data cable from the master/slave box", size=13, fill="#555")
    d.wire([din["GND"], (400, din["GND"][1])], BLACK, 2), d.flag(400, din["GND"][1], "GND", "right")
    dy = din["DATA"][1]
    d.wire([din["DATA"], (540, dy), (540, gy[0]), (x0, gy[0])], DATA_5, 3)
    d.dot(460, dy, DATA_5), d.wire([(460, dy), (460, dy + 70)], BLACK, 2)
    d.resistor(460, dy + 40, "10 kΩ", vertical=True), d.flag(460, dy + 70, "GND", "down")
    y1 = gy[0]
    face_y = [y1 + 70 * i for i in range(4)]
    d.wire([(x0 + 220, y1), (1100, y1)], DATA_5, 3)
    d.resistor(960, y1, "100 Ω", color=DATA_5)
    d.wire([(1100, y1), (1100, face_y[-1])], DATA_5, 3)
    for i, y in enumerate(face_y):
        d.wire([(1100, y), (1200, y)], DATA_5, 3)
        if 0 < i < 3:
            d.dot(1100, y, DATA_5)
        d.rect(1200, y - 24, 360, 48, fill="#fff8e1", stroke="#b58900")
        d.pin(1200, y)
        d.text(1214, y - 3, f"JST-SM out · face {i + 1} strand", size=15, weight="bold")
        d.text(1214, y + 16, "DATA here · 5V/GND from the +5V/GND rails", size=12, fill="#555")
    d.dot(1100, y1, DATA_5)
    d.lines(1110, face_y[-1] + 40, ["joined: gate 1 drives all 4 faces,", "one wire per face from this point"], size=12, fill="#555")
    if two:
        # the tip tower next door: its own data in -> gate 2 -> data out into the tip-tower cable
        yy = 350
        pin = jst_block(d, 40, yy, "JST-SM in · tip tower data", "", [("DATA", ""), ("GND", "")], w=330)
        d.lines(40, yy + 108, ["the tip tower's own data cable from the", "master/slave box (in T2: T1 · in T6: T7)"], size=13, fill="#555")
        d.wire([pin["GND"], (400, pin["GND"][1])], BLACK, 2), d.flag(400, pin["GND"][1], "GND", "right")
        py = pin["DATA"][1]
        d.dot(470, py, DATA_5), d.wire([(470, py), (470, py + 60)], BLACK, 2)
        d.resistor(470, py + 34, "10 kΩ", vertical=True), d.flag(470, py + 60, "GND", "down")
        d.wire([pin["DATA"], (520, py), (520, gy[1]), (x0, gy[1])], DATA_5, 3)
        y2 = gy[1]
        yt = face_y[-1] + 110
        d.wire([(x0 + 220, y2), (1000, y2), (1000, yt), (1200, yt)], DATA_5, 3)
        d.resistor(1100, yt, "100 Ω", color=DATA_5)
        d.rect(1200, yt - 24, 360, 48, fill="#fff8e1", stroke="#b58900")
        d.pin(1200, yt)
        d.text(1214, yt - 3, "Data out · tip tower (gate 2)", size=15, weight="bold")
        d.text(1214, yt + 16, "22 AWG pair (DATA + GND), part of the tip-tower cable", size=12, fill="#555")
    # power
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
    d.lines(1214, top3 + 16, ["XT60 out · top feed, own tower", "3 × 1.5 cable up the post, soldered",
                              "at the top → 4 × XT60 to the strand tops", "+5V / GND rails, NYAF 2.5 mm²"], size=13, fill="#333")
    if two:
        d.rect(1200, top3 + 140, 360, 130, fill="#fde3e3", stroke=RED)
        d.lines(1214, top3 + 166, ["XT60 out · tip-tower cable", "in T2: to T1 · in T6: to T7",
                                   "3 × 2.5 cable, brown +5 V, blue GND", "+5V / GND rails, NYAF 2.5 mm²"], size=13, fill="#333")
    # what goes into this box
    parts = [("1", "100W enclosure"),
             ("1", "C14 inlet with switch and fuse"),
             ("1", "S-100-5 PSU"),
             ("1", "half-size perfboard"),
             ("1", "74AHCT125 in a DIP socket" + (" (2 gates used)" if two else " (1 gate used)")),
             ("2" if two else "1", "10 kΩ resistor (one per data in)"),
             ("2" if two else "1", "100 Ω resistor (one per gate used)"),
             ("2" if two else "1", "JST-SM in: own tower data" + (" + tip tower data" if two else "")),
             ("4", "JST-SM out: faces 1–4, all from gate 1"),
             ("2" if two else "1", "XT60 out: top feed" + (" + tip-tower cable" if two else ""))]
    if two:
        parts.append(("1", "data out for the tip-tower cable's 22 AWG pair (gate 2)"))
    else:
        parts.append(("—", "no second data in, no second XT60, no tip-tower data out"))
    px, py0 = 40, top3 + (300 if two else 160)
    d.rect(px, py0, 560, 44 + 24 * len(parts), fill="#f1f8e9", stroke="#558b2f")
    d.text(px + 14, py0 + 26, f"What goes into one {kind}", size=16, weight="bold", fill="#33691e")
    for i, (n, what) in enumerate(parts):
        yy = py0 + 52 + 24 * i
        grey = n == "—"
        d.text(px + 40, yy, n, size=14, anchor="end", weight="bold", fill="#777" if grey else "#222")
        d.text(px + 56, yy, what, size=14, fill="#777" if grey else "#222")
    notes = ["All flags with the same label are the same wire. The data inputs' 5V pins stay",
             "unconnected so two supplies never join on +5 V. 100 Ω resistors optional.",
             "Unused gates: input to GND, output open. No electronics anywhere in a tower:"]
    if two:
        notes += ["the tip tower's 4 faces are joined at the far end of the tip-tower cable",
                  "(tip-tower-cable.svg), the same way gate 1 is joined to the 4 faces here."]
    else:
        notes += ["the 4 faces are joined on the perfboard, after the 100 Ω.",
                  "T4's power box: this same circuit inside the master/slave box, plus the",
                  "perfboard feed for the ESP32 / transceivers."]
    d.lines(660, py0 + 26, notes, size=14, fill="#333")
    name = "power-box-2-tower.svg" if two else "power-box-1-tower.svg"
    d.save(name, f"{kind}: mains, S-100-5, one 74AHCT125 (gate 1 joined to the 4 JST-SM strands), top-feed XT60" + (", and gate 2 + an XT60 into the tip-tower cable." if two else "."))


def tip_tower_cable():
    d = Drawing(1500, 640, "Tip-tower cable (power box in T2 → T1, in T6 → T7)")
    header(d, "Tip-tower cable — power box in T2 → T1, power box in T6 → T7",
           ["One made-up cable: XT60 and the data pair at the box end, 4 JST-SM at the tower end. T1 and T7 have nothing else:",
            "no box, no base wiring. The cable surfaces inside the 15 cm dark space at the bottom of the tower."])
    # box end
    d.rect(40, 180, 280, 110, fill="#fde3e3", stroke=RED)
    d.lines(56, 210, ["XT60 · into the box's XT60 out", "+5V (brown)", "GND (blue)"], size=15, weight="bold", fill=RED)
    d.pin(320, 237), d.pin(320, 262)
    d.rect(40, 340, 280, 110, fill="#fff8e1", stroke="#b58900")
    d.lines(56, 370, ["Data · from the box's data out", "DATA", "GND"], size=15, weight="bold")
    d.pin(320, 397), d.pin(320, 422)
    # the buried run
    d.rect(380, 150, 300, 320, fill="#f5f5f5", stroke="#bbb", sw=1.5)
    d.lines(530, 176, ["buried", "3 × 2.5 (+5V, GND) + 22 AWG pair (DATA, GND)", "taped together · T2 → T1 1.2 m, T6 → T7 1.0 m"],
            size=12, anchor="middle", fill="#555")
    d.wire([(320, 237), (760, 237), (760, 220), (800, 220)], RED, 5)
    d.wire([(320, 262), (760, 262), (760, 280), (800, 280)], BLUE, 5)
    d.wire([(320, 422), (780, 422), (780, 300)], BLACK, 2), d.dot(780, 300, BLACK)
    d.wire([(780, 300), (800, 300)], BLACK, 2)
    d.text(690, 440, "data GND joins GND", size=11, fill="#555")
    # tower end: two soldered joints, heat shrink over each
    d.rect(800, 200, 120, 40, fill="#fff", stroke=RED), d.text(860, 226, "solder +5V", size=13, anchor="middle", fill=RED, weight="bold")
    d.rect(800, 260, 120, 40, fill="#fff", stroke=BLUE), d.text(860, 286, "solder GND", size=13, anchor="middle", fill=BLUE, weight="bold")
    d.wire([(320, 397), (1000, 397)], DATA_5, 3)
    ys = [170, 260, 350, 440]
    d.wire([(1000, ys[0]), (1000, ys[-1])], DATA_5, 3), d.dot(1000, 397, DATA_5)
    for i, y in enumerate(ys):
        d.wire([(1000, y), (1100, y)], DATA_5, 3)
        d.rect(1100, y - 28, 360, 56, fill="#fff8e1", stroke="#b58900")
        d.pin(1100, y)
        d.text(1114, y - 6, f"JST-SM out · face {i + 1} strand", size=15, weight="bold")
        d.text(1114, y + 14, "DATA here · 5V/GND from the joints", size=12, fill="#555")
    d.wire([(920, 220), (970, 220)], RED, 3), d.flag(970, 220, "+5V", "right")
    d.wire([(920, 280), (970, 280)], BLUE, 3), d.flag(970, 280, "GND", "right")
    d.lines(40, 520, ["Tower end, made up on the bench: the cable's +5V core, GND core and the data GND meet the 4 JST-SM pigtails in two soldered joints;",
                      "the DATA wire is soldered to the 4 DATA pigtails. Heat shrink over every joint. The 4 faces share one buffered data line from the",
                      "power box, so a short on one face's data lead darkens all 4. 22 AWG pigtails are fine over < 0.5 m."],
            size=14, fill="#333")
    d.save("tip-tower-cable.svg", "Tip-tower cable: XT60 and data pair at the power box, split by soldered joints to four JST-SM strands at the tower.")


def statue_power():
    d = Drawing(1600, 920, "Statue power and data distribution")
    header(d, "Statue power and data — the same at both statues",
           ["Mains from the apex to 5 power boxes; each drives the tower it sits in, the 2 tower power boxes (T2, T6) also the tip towers.",
            "Thick lines run in the trench; thin lines stay inside a base."])
    tx = {"T1": 150, "T2": 360, "T3": 570, "T4": 800, "T5": 1030, "T6": 1240, "T7": 1450}
    ty = 540
    for t, x in tx.items():
        own = any(own == t for _, own, _ in SUPPLIES.values())
        d.rect(x - 60, ty, 120, 90, fill="#ffe0b2", stroke="#e65100")
        d.text(x, ty + 30, f"{t} · {TOWER_H[t]}", size=15, anchor="middle", weight="bold")
        d.text(x, ty + 52, "4 × JST-SM", size=12, anchor="middle", fill="#555")
        d.text(x, ty + 72, "own box" if own else "cable end", size=11, anchor="middle", fill="#777")
    sx = {n: tx[own] for n, (_, own, _) in SUPPLIES.items()}
    sy0, sy1 = 320, 400
    for n, x in sx.items():
        d.rect(x - 75, sy0, 150, sy1 - sy0, fill="#eceff1", stroke="#455a64")
        d.text(x, sy0 + 28, f"Power box in {n}", size=15, anchor="middle", weight="bold", fill="#455a64")
        d.text(x, sy0 + 50, "master/slave box" if n == "T4" else ("2 tower power box" if SUPPLIES[n][2] else "1 tower power box"), size=12, anchor="middle", fill="#555")
        d.text(x, sy0 + 68, "S-100-5", size=12, anchor="middle", fill="#555")
    MAINS = "#8b5a2b"
    d.rect(600, 135, 400, 50, fill="#fff3e0", stroke="#e65100")
    d.lines(800, 156, ["230 V in + strip at the apex", "from the outlet, or from the other statue"], size=13, anchor="middle", weight="bold", fill="#e65100")
    d.wire([(800, 185), (800, sy0)], MAINS, 2)
    # extension cords chained tower to tower, a power strip at the end of each (owner, 2026-10-29)
    y = 245
    d.wire([(800, 185), (800, y)], MAINS, 6)
    d.wire([(sx["T2"], y), (sx["T6"], y)], MAINS, 6)
    for n in sx:
        if n == "T4":
            continue
        d.wire([(sx[n], y), (sx[n], sy0)], MAINS, 6)
        d.rect(sx[n] - 26, y - 10, 52, 20, fill="#fff3e0", stroke="#e65100", sw=1.5)
        d.text(sx[n], y + 4, "strip", size=11, anchor="middle", fill="#e65100", weight="bold")
    for a, b in (("T4", "T3"), ("T3", "T2"), ("T4", "T5"), ("T5", "T6")):
        d.text((sx[a] + sx[b]) / 2, y - 9, f"cord {'apex' if a == 'T4' else a} → {b}", size=12, anchor="middle", fill=MAINS, weight="bold")
    # own towers (thin) and neighbours (thick)
    for n, (_, own, nb) in SUPPLIES.items():
        x = sx[n]
        d.wire([(x, sy1), (x, ty)], RED, 2)
        for t in nb:
            off = -40 if tx[t] < x else 40
            d.wire([(x + off, sy1), (x + off, 470), (tx[t], 470), (tx[t], ty)], RED, 6)
            d.text((x + off + tx[t]) / 2, 462, "tip-tower cable", size=12, anchor="middle", fill=RED, weight="bold")
    d.rect(60, 700, 1480, 200, fill="#fafafa", stroke="#bbb", sw=1)
    rows = [(MAINS, 6, "230 V, buried: extension cords chained tower to tower, a power strip at each; a short C13 cord from the strip into the box"),
            (MAINS, 2, "230 V inside the apex base (power box in T4)"),
            (RED, 6, "tip-tower cable, buried: 3×2.5 + 22 AWG data pair; XT60 + data at the box, 4 JST-SM at the tower"),
            (RED, 2, "own tower: 4 JST-SM from the box straight to the 4 strands (5V, DATA, GND)")]
    for i, (col, w, txt) in enumerate(rows):
        y = 730 + 34 * i
        d.wire([(80, y), (150, y)], col, w)
        d.text(170, y + 5, txt, size=14)
    d.text(80, 880, "Data to the power boxes in T2, T3, T5, T6: one DATA + GND line per tower from the master/slave box, in the same trenches (see the trench table).",
           size=14, fill="#333")
    d.save("statue-power.svg", "Mains from the apex to five power boxes per statue; own towers and the tip towers.")


# --------------------------------------------------------------------------
# 7. Site map, to scale, from layout/statue-layout.json
# --------------------------------------------------------------------------

LAYOUT = Path(__file__).resolve().parent.parent / "layout" / "statue-layout.json"
ARM_PAIRS = (("T1", "T2"), ("T2", "T3"), ("T3", "T4"), ("T4", "T5"), ("T5", "T6"), ("T6", "T7"))
DATA_RUNS = (("T4", "T2"), ("T4", "T3"), ("T4", "T5"), ("T4", "T6"))


def site_distances():
    """Steps between neighbouring towers of statue 1, from the layout file, measured between the
    facing corners (owner, 2026-10-29): every tower is turned 45°, so a corner points at the next
    tower along the apex line. Returns (st, rows, params, half_diag_mm) where rows are
    (a, b, dx_mm, dy_corner_mm, straight_corner_mm); dx is between centres (the corners sit on the
    centre line), dy is the clear gap along the apex line. Statue 2 is statue 1 turned 180° about
    the centre, so its steps are the same."""
    import json, math
    lay = json.loads(LAYOUT.read_text())
    st = {s["statue"]: {t["name"]: (t["x_mm"], t["y_mm"]) for t in s["towers"]} for s in lay["layout"]["statues"]}
    outside = lay["layout"]["statues"][0]["towers"][0]["outside_mm"]
    half = outside / math.sqrt(2)
    pos = st[1]
    rows = []
    for a, b in ARM_PAIRS:
        dx, dy = abs(pos[b][0] - pos[a][0]), abs(pos[b][1] - pos[a][1]) - 2 * half
        rows.append((a, b, dx, dy, math.hypot(dx, dy)))
    dx, dy = abs(st[2]["T4"][0] - pos["T4"][0]), abs(st[2]["T4"][1] - pos["T4"][1]) - 2 * half
    rows.append(("apex 1", "apex 2", dx, dy, math.hypot(dx, dy)))
    return st, rows, lay["params"], half


def site_map():
    import json
    st, rows, prm, half = site_distances()
    lay = json.loads(LAYOUT.read_text())
    tw = {sn: {t["name"]: t for s_ in lay["layout"]["statues"] if s_["statue"] == sn for t in s_["towers"]} for sn in st}
    W, H = 1500, 1420
    d = Drawing(W, H, "Site map, to scale")
    header(d, "Site map — top view, to scale",
           ["Left: the whole site on a 1 m grid. Right: one statue enlarged. Every step is measured CORNER TO CORNER, between the two corners",
            "that face each other, as two legs: ACROSS (x) and ALONG the apex-to-apex line (y), dashed, in metres. Lay it out with a tape and a",
            "right angle. The brown number is the straight tape from corner to corner. Statue 2 is statue 1 turned 180° about the centre: the same steps.",
            "From the bench facing either statue, T1 is on your left."])
    MAINS, LEG = "#8b5a2b", "#1565c0"

    def tower(px, py, t, sz, label_dx, label_size=14):
        fill = "#ffcc80" if t["name"] in SUPPLIES else "#ffe0b2"
        d.add(f'<rect x="{px - sz / 2:.1f}" y="{py - sz / 2:.1f}" width="{sz:.1f}" height="{sz:.1f}" '
              f'fill="{fill}" stroke="#e65100" stroke-width="2" transform="rotate({t["box_yaw_deg"]} {px:.1f} {py:.1f})"/>')
        d.text(px + label_dx, py + 5, t["name"], size=label_size, anchor="end" if label_dx < 0 else "start", weight="bold")

    # ---- left panel: the whole site, 40 px per metre
    sc = 40 / 1000.0
    cx, cy = 60 + 9000 * sc, 200 + 9000 * sc
    R = prm["circle_diameter_mm"] / 2 * sc
    def P(x_mm, y_mm):
        return cx + x_mm * sc, cy - y_mm * sc
    g = int(prm["circle_diameter_mm"] / 2000)
    for k in range(-g, g + 1):
        col, sw = ("#ccc", 1.2) if k % 5 == 0 else ("#eee", 0.8)
        x1, y1 = P(k * 1000, -g * 1000); x2, y2 = P(k * 1000, g * 1000)
        d.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}"/>')
        x1, y1 = P(-g * 1000, k * 1000); x2, y2 = P(g * 1000, k * 1000)
        d.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{R:.1f}" fill="none" stroke="#999" stroke-width="2" stroke-dasharray="10 8"/>')
    d.text(cx - R + 10, cy - R + 60, f'circle Ø {prm["circle_diameter_mm"] / 1000:g} m · 1 m grid', size=13, fill="#777")
    rb = prm["bench_diameter_mm"] / 2 * sc
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{rb:.1f}" fill="#f3e9d8" stroke="#a0865a" stroke-width="2"/>')
    d.text(cx, cy + 5, f'bench Ø {prm["bench_diameter_mm"] / 1000:g} m', size=12, anchor="middle", fill="#7a6240")
    a1, a2 = P(*st[1]["T4"]), P(*st[2]["T4"])
    d.add(f'<line x1="{a1[0]:.1f}" y1="{a1[1]:.1f}" x2="{a2[0]:.1f}" y2="{a2[1]:.1f}" stroke="#bbb" stroke-width="1.5" stroke-dasharray="4 6"/>')
    d.text(cx + 8, cy - 3000 * sc, f"apex to apex {rows[-1][4] / 1000:.2f} m corner to corner", size=12, fill="#777")
    x0, y0 = P(-8500, -8700)
    d.wire([(x0, y0), (x0 + 5000 * sc, y0)], "#333", 4)
    for k in range(6):
        d.wire([(x0 + k * 1000 * sc, y0 - 5), (x0 + k * 1000 * sc, y0 + 5)], "#333", 2)
    d.text(x0 + 2500 * sc, y0 - 10, "5 m", size=12, anchor="middle", weight="bold")
    for sn, pos in st.items():
        for a, b in ARM_PAIRS:
            d.wire([P(*pos[a]), P(*pos[b])], MAINS, 3)
        for n, (x, y) in pos.items():
            px, py = P(x, y)
            tower(px, py, tw[sn][n], tw[sn][n]["outside_mm"] * sc, -18 if x < 0 else 18, 12)
        ax_, ay_ = P(*pos["T4"])
        d.text(ax_, ay_ - 20 if sn == 1 else ay_ + 30, f"Statue {sn} · " + ("MASTER box" if sn == 1 else "SLAVE box"), size=14, anchor="middle", weight="bold",
               fill="#2e7d32" if sn == 1 else "#1565c0")
    site_bottom = cy + R

    # ---- right panel: one statue enlarged, 150 px per metre, with the legs of every step
    sc2 = 150 / 1000.0
    pos = st[1]
    xs = [x for x, _ in pos.values()]; ys = [y for _, y in pos.values()]
    px0 = 900
    ox, oy = px0 - min(xs) * sc2, 260 + max(ys) * sc2
    def Q(x_mm, y_mm):
        return ox + x_mm * sc2, oy - y_mm * sc2
    d.text(px0 - 30, 170, "One statue, enlarged (both are the same)", size=16, weight="bold")
    axx, axy = Q(max(xs) + 450, max(ys) - 1600)
    d.wire([(axx, axy), (axx, axy - 1000 * sc2)], "#555", 2)
    d.add(f'<polygon points="{axx - 6},{axy - 1000 * sc2 + 12} {axx + 6},{axy - 1000 * sc2 + 12} {axx},{axy - 1000 * sc2 - 2}" fill="#555"/>')
    d.wire([(axx, axy), (axx + 1000 * sc2, axy)], "#555", 2)
    d.add(f'<polygon points="{axx + 1000 * sc2 - 12},{axy - 6} {axx + 1000 * sc2 - 12},{axy + 6} {axx + 1000 * sc2 + 2},{axy}" fill="#555"/>')
    d.lines(axx + 10, axy - 1000 * sc2 + 14, ["y · ALONG the", "apex line, 1 m"], size=12, fill="#555")
    d.text(axx + 1000 * sc2 / 2, axy + 18, "x · ACROSS, 1 m", size=12, anchor="middle", fill="#555")
    for a, b, dx, dy, straight in rows[:len(ARM_PAIRS)]:
        (xa, ya), (xb, yb) = pos[a], pos[b]
        lower, upper = ((xa, ya), (xb, yb)) if ya < yb else ((xb, yb), (xa, ya))
        c_low = (lower[0], lower[1] + half)        # the lower tower's corner that points at the upper one
        c_up = (upper[0], upper[1] - half)         # the upper tower's corner that points back
        outer_is_lower = abs(lower[0]) > abs(upper[0])
        o, i = (c_low, c_up) if outer_is_lower else (c_up, c_low)
        corner = (o[0], i[1])
        po, pi, pc = Q(*o), Q(*i), Q(*corner)
        d.add(f'<polyline points="{po[0]:.1f},{po[1]:.1f} {pc[0]:.1f},{pc[1]:.1f} {pi[0]:.1f},{pi[1]:.1f}" fill="none" stroke="{LEG}" stroke-width="2.5" stroke-dasharray="7 5"/>')
        for q in (po, pi):
            d.dot(q[0], q[1], LEG, 4)
        ql, qu = Q(*c_low), Q(*c_up)
        d.add(f'<line x1="{ql[0]:.1f}" y1="{ql[1]:.1f}" x2="{qu[0]:.1f}" y2="{qu[1]:.1f}" stroke="{MAINS}" stroke-width="3"/>')
        side = -1 if o[0] < 0 else 1
        d.text(pc[0] + side * 10, (po[1] + pc[1]) / 2 + 5, f"{dy / 1000:.2f} along", size=14, anchor="end" if side < 0 else "start", fill=LEG, weight="bold")
        d.text(pc[0] + side * 10, pc[1] - 8, f"{dx / 1000:.2f} across", size=13, anchor="end" if side < 0 else "start", fill=LEG, weight="bold")
        mx, my = (ql[0] + qu[0]) / 2, (ql[1] + qu[1]) / 2
        d.text(mx - side * 14, my + 5, f"{straight / 1000:.2f}", size=14, anchor="start" if side < 0 else "end", fill=MAINS, weight="bold")
    for n, (x, y) in pos.items():
        px, py = Q(x, y)
        tower(px, py, tw[1][n], tw[1][n]["outside_mm"] * sc2, -52 if x < 0 else 52, 16)
    d.text(Q(0, max(ys))[0], Q(0, max(ys))[1] - 48, "T4 · apex · master/slave box", size=14, anchor="middle", weight="bold", fill="#2e7d32")
    d.lines(px0 - 30, Q(0, min(ys))[1] + 70, [f"Towers are {tw[1]['T4']['outside_mm']} × {tw[1]['T4']['outside_mm']} mm, turned 45°: a corner points along the apex line.",
                                              f"Blue dots: the corners measured between. Centre to centre is {2 * half / 1000:.2f} m more along y."], size=12, fill="#555")

    # ---- table
    ty = site_bottom + 50
    d.rect(60, ty, 18000 * sc, 30 + 24 * (len(rows) + 1), fill="#fafafa", stroke="#bbb", sw=1)
    d.text(80, ty + 22, "Step, corner to corner", size=13, weight="bold"), d.text(330, ty + 22, "straight", size=13, weight="bold", anchor="end")
    d.text(420, ty + 22, "across x", size=13, weight="bold", anchor="end"), d.text(510, ty + 22, "along y", size=13, weight="bold", anchor="end")
    d.text(540, ty + 22, "what runs there", size=13, weight="bold")
    what = {("T1", "T2"): "tip-tower cable", ("T2", "T3"): "cord T3 → T2 · data to T2 (2 lines)",
            ("T3", "T4"): "cord apex → T3 · data to T3 and T2", ("T4", "T5"): "cord apex → T5 · data to T5 and T6",
            ("T5", "T6"): "cord T5 → T6 · data to T6 (2 lines)", ("T6", "T7"): "tip-tower cable",
            ("apex 1", "apex 2"): "3 × CAT5 and the apex-to-apex cord"}
    for i, (a, b, dx, dy, straight) in enumerate(rows):
        y = ty + 46 + 24 * i
        d.text(80, y, f"{a} → {b}", size=13)
        d.text(330, y, f"{straight / 1000:.2f}", size=13, anchor="end"), d.text(420, y, f"{dx / 1000:.2f}", size=13, anchor="end")
        d.text(510, y, f"{dy / 1000:.2f}", size=13, anchor="end"), d.text(540, y, what.get((a, b), ""), size=13, fill="#555")
    d.text(60, ty + 30 + 24 * (len(rows) + 1) + 20, "Metres, between the facing corners. x is across the site, y is along the apex-to-apex line.", size=12, fill="#555")
    d.save("site-map.svg", "Both statues to scale from layout/statue-layout.json, one statue enlarged with every step drawn corner to corner as its across and along legs.")


if __name__ == "__main__":
    site_map()
    overview()
    master_box()
    slave_box()
    power_box(two=False)
    power_box(two=True)
    tip_tower_cable()
    statue_power()
