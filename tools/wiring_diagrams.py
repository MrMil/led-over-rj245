#!/usr/bin/env python3
"""Generate the wiring diagrams in guide/img/ as plain SVG.

Usage:  python3 tools/wiring_diagrams.py

The pin tables below are the single source for every diagram: change a GPIO or
an RJ45 pin here, re-run, and all diagrams follow. Do not hand-edit the SVGs.
Standard library only.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "guide" / "img"

# --------------------------------------------------------------------------
# Pin tables
# --------------------------------------------------------------------------

# Channel -> ESP32 GPIO. S0 is local (74AHCT125); S1-S3 go out over RS-485.
GPIO = {
    "S0-A": 13, "S0-B": 14,
    "S1-A": 16, "S1-B": 17,
    "S2-A": 18, "S2-B": 19,
    "S3-A": 23, "S3-B": 25,
}

# RJ45 pin -> (function, T568B colour name, colour, striped-with-white)
ORANGE, GREEN, BLUE, BROWN = "#f08a24", "#2e9e44", "#1f5fbf", "#8b5a2b"
RJ45 = {
    1: ("A", "ch A", "w/orange", ORANGE, True),
    2: ("B", "ch A", "orange", ORANGE, False),
    3: ("A", "ch B", "w/green", GREEN, True),
    4: ("GND", "", "blue", BLUE, False),
    5: ("GND", "", "w/blue", BLUE, True),
    6: ("B", "ch B", "green", GREEN, False),
    7: ("GND", "", "w/brown", BROWN, True),
    8: ("GND", "", "brown", BROWN, False),
}
RJ45_GND = [4, 5, 7, 8]

# Physical LED exits (JST-SM, back wall) in every box: two strips per channel,
# chained. Strip 1 takes the channel's data; strip 2 takes its data from strip
# 1's DOUT on the statue, so its exit carries power only.
# (exit number, channel, strip, carries data)
EXITS = [(1, "A", 1, True), (2, "A", 2, False), (3, "B", 1, True), (4, "B", 2, False)]

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


def jack(d, x, top, title, pins_on, channel_names):
    """RJ45 coupler pigtail. Returns {pin: (x, y)} attachment points."""
    w, pitch = 250, 26
    d.rect(x, top, w, 40 + pitch * 8 + 4, fill="#f4f4f4", stroke="#333")
    d.text(x + w / 2, top + 26, title, size=16, anchor="middle", weight="bold")
    pts = {}
    for n in range(1, 9):
        fn, ch, cname, col, stripe = RJ45[n]
        y = top + 40 + pitch * (n - 1) + 14
        px = x if pins_on == "left" else x + w
        sx = x + 34 if pins_on == "left" else x + 14
        d.add(f'<rect x="{sx}" y="{y - 6}" width="34" height="12" fill="{col}" stroke="#777"/>')
        if stripe:
            d.add(f'<rect x="{sx + 8}" y="{y - 6}" width="9" height="12" fill="#fff"/>'
                  f'<rect x="{sx + 25}" y="{y - 6}" width="9" height="12" fill="#fff"/>')
        label = f"{fn} · {channel_names[ch]}" if ch else "GND"
        if pins_on == "left":
            d.text(x + 14, y + 5, n, size=14, weight="bold")
            d.text(x + 76, y + 5, f"{cname:<9}", size=13, fill="#555")
            d.text(x + 150, y + 5, label, size=14, weight="bold")
        else:
            d.text(x + w - 14, y + 5, n, size=14, weight="bold", anchor="end")
            d.text(x + 56, y + 5, cname, size=13, fill="#555")
            d.text(x + 126, y + 5, label, size=14, weight="bold")
        d.pin(px, y)
        pts[n] = (px, y)
    return pts


def gnd_brackets(d, pts, side):
    """Join RJ45 pins 4+5 and 7+8 to GND with short stubs in their own colours."""
    s = -1 if side == "left" else 1
    for pair in ((4, 5), (7, 8)):
        bx = pts[pair[0]][0] + s * 26
        for n in pair:
            px, py = pts[n]
            d.wire([(px, py), (bx, py)], RJ45[n][3], 4, stripe=RJ45[n][4])
        y0, y1 = pts[pair[0]][1], pts[pair[1]][1]
        d.wire([(bx, y0), (bx, y1)], BLACK, 3)
        d.dot(bx, y0), d.dot(bx, y1)
        d.flag(bx, (y0 + y1) / 2, "GND", side)


def pair_wire(d, n, pts):
    _, _, _, col, stripe = RJ45[n]
    d.wire(pts, col, 5, stripe=stripe)


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


def jst_exit(d, x, y, n, statue, ch, strip, data=True):
    if data:
        d.rect(x, y - 24, 250, 48, fill="#fff8e1", stroke="#b58900")
        d.pin(x, y)
        d.text(x + 14, y - 3, f"LED exit {n} · DATA", size=15, weight="bold")
        d.text(x + 14, y + 16, f"{statue}-{ch} strip {strip} → chains to strip 2", size=14, fill="#555")
    else:
        d.rect(x, y - 24, 250, 48, fill="#fafafa", stroke="#b58900", dash="6 4")
        d.text(x + 14, y - 3, f"LED exit {n} · power only", size=15, weight="bold", fill="#777")
        d.text(x + 14, y + 16, f"{statue}-{ch} strip 2 · DATA pin n/c", size=14, fill="#777")


# --------------------------------------------------------------------------
# 1. Controller box (statue 0)
# --------------------------------------------------------------------------

def controller():
    d = Drawing(1600, 1640, "Controller box wiring (statue 0)")
    header(d, "Controller box — statue 0 (enclosure 100W-masterbox)",
           ["Signals only. Power wiring: box-power.svg.",
            "8 channels: 2 for statue 0 through the 74AHCT125,",
            "6 over RS-485 to statues 1–3 (2 per RJ45 jack)."])
    legend(d, 960, 20, [("stripe", ORANGE, "RJ45 pigtail wires, T568B colours (striped = white/colour)")])

    # ESP32
    ex, ew, etop, ebot = 150, 230, 210, 1600
    d.rect(ex, etop, ew, ebot - etop, fill="#eef7ee", stroke="#2e7d32")
    d.lines(ex + ew / 2, 570, ["ESP32", "dev board", "classic, no PSRAM", "runs WLED"],
            size=16, anchor="middle", fill="#2e7d32", weight="bold")
    d.lines(ex + ew / 2, 770, ["USB: flashing", "and debug only"], size=13,
            anchor="middle", fill="#555")
    for name, y in (("5V / VIN", 300), ("GND", 340)):
        d.pin(ex, y), d.text(ex + 10, y + 5, name, size=14, weight="bold")
    d.flag(ex, 300, "+5V", "left"), d.flag(ex, 340, "GND", "left")

    def gpio(ch, y):
        d.pin(ex + ew, y)
        d.text(ex + ew - 10, y + 5, f"GPIO {GPIO[ch]}", size=15, weight="bold", anchor="end")
        return (ex + ew, y)

    # 74AHCT125 for statue 0
    bx, bw, btop, bbot = 560, 220, 210, 520
    d.rect(bx, btop, bw, bbot - btop, fill="#f3e5f5", stroke=DATA_5)
    d.lines(bx + bw / 2, btop + 140, ["74AHCT125", "3.3 V → 5 V", "buffer"], size=16,
            anchor="middle", weight="bold", fill=DATA_5)
    # Gates 1 and 2 are used; 3 and 4 have their inputs grounded.
    gates = {"S0-A": ("1A", 2, "1Y", 3, 260), "S0-B": ("2A", 5, "2Y", 6, 420)}
    for (a, pa, yname, py_, y) in gates.values():
        d.pin(bx, y), d.text(bx + 10, y + 5, f"{pa} · {a}", size=14, weight="bold")
        d.pin(bx + bw, y), d.text(bx + bw - 10, y + 5, f"{yname} · {py_}", size=14, weight="bold", anchor="end")
    for px, flag in ((590, "+5V"), (650, "GND"), (710, "GND"), (770, "GND")):
        d.pin(px, bbot)
        d.wire([(px, bbot), (px, bbot + 18)], BLACK, 2)
        d.flag(px, bbot + 18, flag, "down")
    d.lines(bx + bw / 2, bbot - 46, ["14 VCC · 7 GND · OE 1,4,10,13", "unused inputs 9, 12 → GND"],
            size=12, anchor="middle", fill="#555")
    d.text(bx + bw / 2, bbot - 8, "VCC     GND     OE     9,12", size=12, anchor="middle", fill="#555")

    for ch, (_, _, _, _, y) in gates.items():
        d.wire([gpio(ch, y), (bx, y)], DATA_33, 3)
        d.wire([(bx + bw, y), (1150, y)], DATA_5, 3)
        d.resistor(940, y, "100 Ω", color=DATA_5)
    for (n, ch, strip, data) in EXITS:
        y = gates[f"S0-{ch}"][4] + (0 if data else 70)
        jst_exit(d, 1150, y, n, "S0", ch, strip, data)

    # MAX485 transmitters + RJ45 jacks, one group per remote statue
    for k, statue in enumerate(("S1", "S2", "S3")):
        G = 590 + k * 330
        names = {"ch A": f"{statue}-A", "ch B": f"{statue}-B"}
        jp = jack(d, 1150, G + 24, f"RJ45 jack {k + 1} → statue {k + 1}", "left", names)
        gnd_brackets(d, jp, "left")
        for m, ch in enumerate(("A", "B")):
            y0 = G + m * 170
            mp = max485(d, 560, y0, f"TX · {statue}-{ch}", ["RO", "RE", "DE", "DI"], ["VCC", "GND", "A", "B"])
            d.text(548, mp["RO"][1] + 5, "n/c", size=13, anchor="end", fill="#777")
            d.wire([mp["RE"], (530, mp["RE"][1]), (530, mp["DE"][1]), mp["DE"]], RED, 2)
            d.dot(530, mp["RE"][1], RED, 4), d.dot(530, mp["DE"][1], RED, 4)
            d.flag(530, (mp["RE"][1] + mp["DE"][1]) / 2, "+5V", "left")
            d.wire([gpio(f"{statue}-{ch}", mp["DI"][1]), mp["DI"]], DATA_33, 3)
            d.wire([mp["VCC"], (800, mp["VCC"][1])], RED, 2), d.flag(800, mp["VCC"][1], "+5V", "right")
            d.wire([mp["GND"], (800, mp["GND"][1])], BLACK, 2), d.flag(800, mp["GND"][1], "GND", "right")
            if ch == "A":
                pair_wire(d, 1, [mp["A"], jp[1]])
                pair_wire(d, 2, [mp["B"], jp[2]])
            else:
                ax, bx2 = 1010, 1040
                pair_wire(d, 3, [mp["A"], (ax, mp["A"][1]), (ax, jp[3][1]), jp[3]])
                pair_wire(d, 6, [mp["B"], (bx2, mp["B"][1]), (bx2, jp[6][1]), jp[6]])

    d.save("controller-wiring.svg", "ESP32, 74AHCT125, six MAX485 transmitters and three RJ45 jacks in the controller box.")


# --------------------------------------------------------------------------
# 2. Statue box (statues 1-3)
# --------------------------------------------------------------------------

def statue():
    d = Drawing(1600, 960, "Statue box wiring (statues 1-3)")
    header(d, "Statue box — statues 1, 2, 3 (enclosure 100W-rj45)",
           ["Signals only. Power wiring: box-power.svg.",
            "Same in all three boxes. In the labels, S# is this statue's number.",
            "Pin 1 here = pin 1 at the controller (straight-through cable)."])
    legend(d, 960, 20, [("stripe", ORANGE, "RJ45 pigtail wires, T568B colours (striped = white/colour)")])

    jp = jack(d, 60, 300, "RJ45 jack ← from controller", "right", {"ch A": "S#-A", "ch B": "S#-B"})
    gnd_brackets(d, jp, "right")

    mx = 700
    for m, ch in enumerate(("A", "B")):
        y0 = 328 + m * 272
        mp = max485(d, mx, y0, f"RX · S#-{ch}", ["A", "B"], ["RO", "RE", "DE", "DI"], w=200)
        # power pins on the bottom edge (module drawn taller to make room)
        yb = y0 + 190
        d.add(f'<rect x="{mx + 2}" y="{y0 + 120}" width="196" height="{yb - y0 - 121}" fill="#e3edf9" stroke="none"/>')
        d.add(f'<polyline points="{mx},{y0 + 140} {mx},{yb} {mx + 200},{yb} {mx + 200},{y0 + 140}" '
              f'fill="none" stroke="#1f5fbf" stroke-width="2"/>')
        d.text(mx + 100, yb - 34, "120 Ω on board: leave it", size=12, anchor="middle", fill="#1f5fbf")
        for px, lbl, flag in ((mx + 50, "VCC", "+5V"), (mx + 150, "GND", "GND")):
            d.pin(px, yb), d.text(px, yb - 10, lbl, size=13, anchor="middle", weight="bold")
            d.wire([(px, yb), (px, yb + 16)], BLACK, 2), d.flag(px, yb + 16, flag, "down")
        # cable to module, with idle bias
        if ch == "A":
            pa, pb = 1, 2
            pair_wire(d, pa, [jp[pa], mp["A"]])
            pair_wire(d, pb, [jp[pb], mp["B"]])
        else:
            pa, pb = 3, 6
            pair_wire(d, pa, [jp[pa], (420, jp[pa][1]), (420, mp["A"][1]), mp["A"]])
            pair_wire(d, pb, [jp[pb], (400, jp[pb][1]), (400, mp["B"][1]), mp["B"]])
        # bias: A -> 560 -> GND (drawn upward), B -> 560 -> +5V (drawn downward)
        ya, yb = mp["A"][1], mp["B"][1]
        d.dot(560, ya), d.wire([(560, ya), (560, ya - 70)], BLACK, 2)
        d.resistor(560, ya - 38, "560 Ω")
        d.flag(560, ya - 70, "GND", "up")
        d.dot(620, yb), d.wire([(620, yb), (620, yb + 80)], RED, 2)
        d.resistor(620, yb + 40, "560 Ω", vertical=True, color=RED)
        d.flag(620, yb + 80, "+5V", "down")
        # RE + DE to GND, DI unused
        rx = mx + 200
        d.wire([mp["RE"], (rx + 30, mp["RE"][1]), (rx + 30, mp["DE"][1]), mp["DE"]], BLACK, 2)
        d.dot(rx + 30, mp["RE"][1], BLACK, 4), d.dot(rx + 30, mp["DE"][1], BLACK, 4)
        d.wire([(rx + 30, (mp["RE"][1] + mp["DE"][1]) / 2), (rx + 60, (mp["RE"][1] + mp["DE"][1]) / 2)], BLACK, 2)
        d.flag(rx + 60, (mp["RE"][1] + mp["DE"][1]) / 2, "GND", "right")
        d.text(rx + 12, mp["DI"][1] + 5, "n/c", size=13, fill="#777")
        # RO splits to two strips
        ro = mp["RO"]
        d.wire([ro, (1250, ro[1])], DATA_5, 3)
        d.resistor(1160, ro[1], "100 Ω", color=DATA_5)
        for (n, ech, strip, data) in EXITS:
            if ech == ch:
                jst_exit(d, 1250, ro[1] + (0 if data else 80), n, "S#", ch, strip, data)

    d.lines(60, 880, ["Bias resistors (560 Ω) are soldered on the perfboard, one pair per module. They hold the",
                      "line at a defined 'idle low' when the controller is off or rebooting, so the strips stay dark",
                      "instead of flickering. Check the module: if it has its own bias resistors, these still win."],
            size=15, fill="#333")
    d.save("statue-wiring.svg", "RJ45 jack, two MAX485 receivers with idle bias, and four LED exits in a statue box.")


# --------------------------------------------------------------------------
# 3. Power (every box)
# --------------------------------------------------------------------------

def power():
    d = Drawing(1560, 720, "Box power wiring (all four boxes)")
    header(d, "Power — the same in all four boxes",
           ["Mains to the PSU; strip power straight from the PSU, never through the perfboard.",
            "Perfboard (+5V / GND rails) gets its own pair from the PSU's second +V / −V terminals."])

    # C14
    d.rect(180, 170, 260, 100, fill="#fff3e0", stroke="#e65100")
    d.lines(310, 205, ["C14 inlet", "fuse + switch"], size=16, anchor="middle", weight="bold", fill="#e65100")
    # PSU
    d.rect(200, 440, 760, 140, fill="#eceff1", stroke="#455a64")
    d.lines(580, 520, ["S-100-5 power supply · 5 V 20 A"], size=18, anchor="middle", weight="bold", fill="#455a64")
    d.text(580, 548, "V-ADJ pot: not touched in the field", size=13, anchor="middle", fill="#555")
    terms = [(260, "1 L"), (320, "2 N"), (380, "3 FG"), (520, "4 −V"), (580, "5 −V"), (660, "6 +V"), (720, "7 +V")]
    for x, lbl in terms:
        d.pin(x, 440), d.text(x, 470, lbl, size=13, anchor="middle", weight="bold")
    d.text(320, 500, "AC side", size=13, anchor="middle", fill="#e65100")
    d.text(620, 500, "DC side", size=13, anchor="middle", fill="#455a64")
    for x, col, stripe, lbl in ((260, "#8b5a2b", False, "L"), (320, BLUE, False, "N"), (380, "#2e9e44", False, "PE")):
        d.pin(x, 270), d.text(x, 262, lbl, size=13, anchor="middle", weight="bold")
        d.wire([(x, 270), (x, 440)], col, 5)
    d.wire([(380, 275), (380, 435)], "#f9d71c", 5)
    d.add('<polyline points="380,275 380,435" fill="none" stroke="#2e9e44" stroke-width="5" stroke-dasharray="10 10"/>')
    d.text(170, 340, "230 V AC", size=18, anchor="end", weight="bold", fill="#c62828")
    d.text(170, 362, "brown L · blue N", size=13, anchor="end", fill="#555")
    d.text(170, 380, "green/yellow PE", size=13, anchor="end", fill="#555")

    # perfboard feed: flags
    d.wire([(580, 440), (580, 400)], BLACK, 3), d.flag(580, 400, "GND", "up")
    d.wire([(720, 440), (720, 400)], RED, 3), d.flag(720, 400, "+5V", "up")
    d.text(770, 390, "← both to perfboard rails, 0.5 mm²", size=13, fill="#555")

    # heavy buses
    d.wire([(520, 440), (520, 240), (1460, 240)], BLACK, 6)
    d.wire([(660, 440), (660, 290), (1460, 290)], RED, 6)
    d.text(560, 230, "GND · WAGO 221-415, fed with 1.5 mm²", size=13, fill="#222")
    d.text(690, 314, "+5 V · WAGO 221-415, fed with 1.5 mm²", size=13, fill=RED)

    # exits along the back wall
    for i, (n, ch, strip, data) in enumerate(EXITS):
        x = 1000 + i * 125
        d.rect(x, 100, 110, 70, fill="#fff8e1", stroke="#b58900")
        d.text(x + 55, 122, f"LED exit {n}", size=14, anchor="middle", weight="bold")
        d.text(x + 55, 140, f"{ch} strip {strip}" + ("" if data else " (power)"), size=12, anchor="middle", fill="#555")
        for dx, lbl in ((20, "5V"), (55, "DAT"), (90, "GND")):
            d.pin(x + dx, 170), d.text(x + dx, 160, lbl, size=10, anchor="middle", fill="#555")
        d.wire([(x + 20, 290), (x + 20, 170)], RED, 3), d.dot(x + 20, 290, RED)
        d.wire([(x + 90, 240), (x + 90, 170)], BLACK, 3), d.dot(x + 90, 240, BLACK)
        if data:
            d.wire([(x + 55, 170), (x + 55, 200)], DATA_5, 3)
            d.text(x + 55, 216, "data", size=11, anchor="middle", fill=DATA_5)
        else:
            d.text(x + 55, 192, "n/c", size=11, anchor="middle", fill="#777")
    d.lines(1000, 380, ["Each JST-SM exit carries at most 3 A.",
                        "These four exits are the statue's only power;",
                        "the controller's brightness limit keeps each under 3 A.",
                        "Data wire: from the perfboard, see the",
                        "box's signal diagram."], size=14, fill="#333")
    d.lines(200, 620, ["Mains wiring is done in the workshop and checked before the event. In the field, never open a box",
                       "while its C14 cord is plugged in. JST pigtail colours vary by supplier — check 5V / DATA / GND with a meter."],
            size=15, fill="#c62828")
    d.save("box-power.svg", "Mains inlet, PSU terminals and 5 V distribution to the LED exits and perfboard.")


# --------------------------------------------------------------------------
# 4. Overview
# --------------------------------------------------------------------------

def overview():
    d = Drawing(1200, 940, "System overview")
    header(d, "System overview — top view", ["One controller (statue 0) drives all four statues.",
                                             "Only data crosses the ground; each statue has its own mains-powered PSU."])
    cx, cy, r = 600, 470, 240
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#bbb" stroke-width="2" stroke-dasharray="8 8"/>')
    d.text(cx - 80, cy + 6, "8 m circle", size=16, anchor="middle", fill="#999")
    pos = {0: (cx, cy - r), 1: (cx + r, cy), 2: (cx, cy + r), 3: (cx - r, cy)}
    cable = "#6a1b9a"
    for k in (1, 2, 3):
        x0, y0 = pos[0]
        x1, y1 = pos[k]
        if k == 2:
            pts = [(x0 + 40, y0 + 40), (x0 + 40, y1 - 40)]
        else:
            pts = [(x0 + (25 if k == 1 else -25), y0 + 30), (x1 + (-30 if k == 1 else 30), y1 - 30)]
        d.wire(pts, cable, 6)
        mx, my = (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2
        d.rect(mx - 70 + (55 if k == 2 else 0), my - 16, 140, 30, fill="#fff", stroke=cable, sw=1.5)
        d.text(mx + (55 if k == 2 else 0), my + 5, f"cable {k} · jack {k}", size=14, anchor="middle", fill=cable, weight="bold")
    for k, (x, y) in pos.items():
        col = "#2e7d32" if k == 0 else "#1565c0"
        d.add(f'<circle cx="{x}" cy="{y}" r="46" fill="#fff" stroke="{col}" stroke-width="4"/>')
        d.text(x, y - 4, f"Statue {k}", size=17, anchor="middle", weight="bold", fill=col)
        d.text(x, y + 16, "controller" if k == 0 else "statue box", size=13, anchor="middle", fill="#555")
    # phone + mains notes
    d.rect(800, 150, 330, 92, fill="#eef7ee", stroke="#2e7d32")
    d.lines(816, 176, ["WiFi access point from the controller.", "Phones connect to it to run the show.",
                       "No internet needed."], size=14)
    d.wire([(800, 196), (650, 236)], "#2e7d32", 2)
    d.rect(60, 790, 1080, 120, fill="#fafafa", stroke="#bbb", sw=1)
    d.lines(80, 818, ["Purple = 10 m CAT5e patch lead, buried in a trench. Carries LED data + ground only. NOT Ethernet.",
                      "Mains cords are buried in the same trenches. No cable above ground: boxes sit inside the bases.",
                      "Wave order around the circle: statue 0 → 1 → 2 → 3 (clockwise in this drawing).",
                      "Which physical statue is 0–3 is set at install: label boxes and cables to match."], size=15)
    d.save("overview.svg", "Four statues in a circle, star-wired from the controller at statue 0.")


if __name__ == "__main__":
    overview()
    controller()
    statue()
    power()
