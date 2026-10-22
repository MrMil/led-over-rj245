#!/usr/bin/env python3
"""Generate the four viewpoint pictures that are cut into the tower faces, as vector cut files.

One picture per viewpoint of tools/statue_render.html (bench seat and back view of each statue).
Everything is polygon geometry (shapely): the figures are drawn in "design units" (the pixels of a
2048-wide picture), every face is a flat plate whose mapping from the picture plane is a homography
(art/viewpoints.json holds each face's corners in the picture, as the tool projects them), and a
homography maps polygons to polygons exactly, so each plate's cuts are composed and checked in
millimetres and written straight to DXF. No raster step is involved in the cuts (owner, 2026-10-22:
"do what is needed to avoid the pixelization issue"); the PNGs are only the tool's preview.

The pictures are dense on purpose (owner, 2026-10-22: the LED light and the animations must come
through, and the pattern must be intricate): a lattice of cut cells with MIN_WOOD_MM of wood between
them, in bands radiating from the picture's energy centre, figures as glowing shapes with a wood
contour and their own pattern inside, a circular maze in whatever wood is still blank and through
any cut area wider than MAX_SOLID_MM.

Every plate is cuttable from one sheet: no wood island (every wood region reaches the plate's
border through wood at least CORE_MM wide, else it is bridged), cuts no narrower than MIN_CUT_MM,
wood no narrower than MIN_WOOD_MM, nothing anchored at one end only.

Usage:  python3 tools/face_art.py [name ...] [-v]   (names: bench1 back1 bench2 back2; default all)
Needs numpy, pillow, scipy and shapely (python3 -m venv .venv; .venv/bin/pip install numpy pillow scipy shapely).
Output: art/dxf/S<statue>-T<n>-<face>.dxf (one per plate), art/<name>.png (the picture for the tool),
art/<name>-preview.png (the picture with the faces, their wood borders and unlit bases drawn in).
"""
import json, math, os, sys, random, time
import numpy as np
from PIL import Image, ImageDraw
import shapely, shapely.affinity
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, box
from shapely.ops import unary_union, nearest_points

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'art'); DXF = os.path.join(ART, 'dxf')
MAXDIM = 4096            # the preview PNG's long side (the tool's PICTURE_MAX)
TOWERS_DIM = 8192        # the towers-only render's long side (art/<name>-towers.png): the plates as seen from the viewpoint
DESIGN = 2048            # design units: pixels of a 2048-wide (or 2048-tall) picture
MIN_CUT_MM = 10.0        # narrowest cut: a 6 mm bit leaves a clean 10 mm slot
MIN_WOOD_MM = 15.0       # narrowest wood anywhere: 2.5 x the 6 mm plywood (general DFM rules allow half the thickness
                         # in sheet metal; plywood splits along the grain and these plates are handled and stand in wind)
LANE_MM = 18.0           # the lattice's wood lanes and bridges, a little over the minimum
CONTOUR = 1.5            # a figure's wood contour, in lanes (27 mm): reads as a line against the lattice without a blank band
MAX_SOLID_MM = 110.0     # no cut area wider than this without a wood lane through it (owner: a blank diffuser is as bad as blank wood)
ROUND_MM = 8.0           # corner radius of the maze's walls and corridors (owner: square corners look cyberpunk)
CORE_MM = 12.0           # wood counts as connected only through necks at least this wide
FILL_MARGIN_MM = 60.0    # the mandala fill keeps this far from every figure (owner, 2026-10-22: a mask with a margin)
MIN_PIECE_MM2 = 250.0    # a cut piece smaller than this is dropped whatever made it (owner, 2026-10-22)
BORDER_MM = 20.0         # the tool keeps this much wood around every face
BASE_MM = 150.0          # the unlit base at the foot of every face (no LEDs behind it): wood
SIDE_MM = 400.0
TAU = math.tau

# ---------------------------------------------------------------- geometry helpers (design units, y down)
def dirv(a):                        # angle in degrees, 0 = right, 90 = up
    r = math.radians(a); return (math.cos(r), -math.sin(r))

def lerp(a, b, t): return a + (b - a) * t

def bez(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n; s = 1 - t
        out.append((s*s*s*p0[0] + 3*s*s*t*p1[0] + 3*s*t*t*p2[0] + t*t*t*p3[0],
                    s*s*s*p0[1] + 3*s*s*t*p1[1] + 3*s*t*t*p2[1] + t*t*t*p3[1]))
    return out

def spline(pts, n=12):
    """Catmull-Rom through pts, n samples per segment."""
    if len(pts) < 3: return list(pts)
    P_ = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i-1], P_[i], P_[i+1], P_[i+2]
        for k in range(n):
            t = k / n; t2 = t*t; t3 = t2*t
            out.append((0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3),
                        0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)))
    out.append(pts[-1]); return out

def arc_pts(cx, cy, r, a0, a1, n=None):
    if n is None: n = max(6, int(abs(a1 - a0) / 2) + 1)
    return [(cx + r*dirv(lerp(a0, a1, i/n))[0], cy + r*dirv(lerp(a0, a1, i/n))[1]) for i in range(n + 1)]

def plen(pts): return sum(math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1))

def sub_path(pts, s0, s1):
    """Part of a polyline between arc lengths s0 and s1."""
    out = []; acc = 0.0
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i+1]; seg = math.hypot(x1-x0, y1-y0)
        if seg == 0: continue
        a, b = acc, acc + seg
        if b < s0 or a > s1: acc = b; continue
        t0 = max(0.0, (s0 - a) / seg); t1 = min(1.0, (s1 - a) / seg)
        if not out: out.append((x0 + (x1-x0)*t0, y0 + (y1-y0)*t0))
        out.append((x0 + (x1-x0)*t1, y0 + (y1-y0)*t1)); acc = b
    return out

def at_len(pts, s):
    q = sub_path(pts, s - 0.5, s + 0.5); return q[0] if q else pts[-1]

# ---------------------------------------------------------------- polygon makers (lists of shapely geometries)
def P(pts):
    p = Polygon(pts); return [p if p.is_valid else p.buffer(0)]

def dot(cx, cy, r): return [Point(cx, cy).buffer(r, 24)]

def ribbon(pts, widths, caps=True):
    """A polyline thickened to a polygon; widths per point (number or list). Round ends if caps."""
    n = len(pts)
    if n < 2: return []
    if not isinstance(widths, (list, tuple)): widths = [widths] * n
    L, R = [], []
    for i in range(n):
        if i == 0: dx, dy = pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]
        elif i == n-1: dx, dy = pts[-1][0]-pts[-2][0], pts[-1][1]-pts[-2][1]
        else: dx, dy = pts[i+1][0]-pts[i-1][0], pts[i+1][1]-pts[i-1][1]
        d = math.hypot(dx, dy) or 1; nx, ny = -dy/d, dx/d; w = widths[i] / 2
        L.append((pts[i][0] + nx*w, pts[i][1] + ny*w)); R.append((pts[i][0] - nx*w, pts[i][1] - ny*w))
    out = P(L + R[::-1])
    if caps:
        if widths[0] > 2: out += dot(pts[0][0], pts[0][1], widths[0]/2)
        if widths[-1] > 2: out += dot(pts[-1][0], pts[-1][1], widths[-1]/2)
    return out

def taper(pts, w0, w1, power=1.0):
    n = len(pts); return [lerp(w0, w1, (i/(n-1))**power) for i in range(n)]

def wedge(cx, cy, a, r0, r1, w0, w1, n=6):
    pts = [(cx + dirv(a)[0]*lerp(r0, r1, i/n), cy + dirv(a)[1]*lerp(r0, r1, i/n)) for i in range(n+1)]
    return ribbon(pts, taper(pts, w0, w1))

def dashed(pts, w, dash, gap, offset=0.0):
    """Dashes of length `dash` (round caps included) separated by gaps of exactly `gap` along a polyline."""
    total = plen(pts); s = offset; out = []
    while s < total:
        seg = sub_path(pts, s + w / 2, min(total, s + dash - w / 2))
        if len(seg) > 1 and plen(seg) > 1: out += ribbon(seg, w)
        s += dash + gap
    return out

def dashed_arc(cx, cy, r, w, dash, gap, a0=0, a1=360, offset=0.0):
    return dashed(arc_pts(cx, cy, r, a0, a1, max(24, int(r/4))), w, dash, gap, offset)

def rays(cx, cy, n, r0, r1, w0, w1, a0=0, a1=360, rot=0.0, full=True):
    out = []; span = a1 - a0
    for i in range(n if full else n + 1): out += wedge(cx, cy, a0 + rot + span * (i / n), r0, r1, w0, w1)
    return out

def lens(p0, p1, bulge, tip=0.5, blunt=1.0):
    """Leaf / lens shape between p0 and p1; bulge = half-width, tip = where along (0-1) the widest point is, blunt < 1
    fattens the ends (a feather, not a needle)."""
    pts = []; dx, dy = p1[0]-p0[0], p1[1]-p0[1]; d = math.hypot(dx, dy) or 1; nx, ny = -dy/d, dx/d
    N = 32; k = math.log(0.5) / math.log(tip) if 0 < tip < 1 else 1
    for side in (1, -1):
        rng = range(N + 1) if side == 1 else range(N, -1, -1)
        for i in rng:
            t = i / N; w = bulge * math.sin(math.pi * t ** k) ** blunt
            pts.append((p0[0] + dx*t + nx*w*side, p0[1] + dy*t + ny*w*side))
    return P(pts)

def spiral(cx, cy, r0, r1, turns, w0, w1, a0=0.0, ccw=True, n_per_turn=48):
    N = int(turns * n_per_turn); pts = []
    for i in range(N + 1):
        t = i / N; a = a0 + (1 if ccw else -1) * 360 * turns * t; r = lerp(r0, r1, t)
        pts.append((cx + r*dirv(a)[0], cy + r*dirv(a)[1]))
    return ribbon(pts, taper(pts, w0, w1))

def polys(g):
    """The Polygon parts of any geometry (collections expanded, lines and points dropped)."""
    if g is None or g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    if hasattr(g, 'geoms'): return [q for part in g.geoms for q in polys(part)]
    return []

def U(geos):
    """Union of a list of geometries (or a geometry), always a valid Polygon or MultiPolygon, snapped to 0.01 so
    later boolean operations never trip over near-coincident vertices."""
    if hasattr(geos, 'geom_type'):
        if geos.geom_type in ('Polygon', 'MultiPolygon'): return geos
        geos = polys(geos)
    geos = [q for g in geos if g is not None for q in polys(g)]
    if not geos: return Polygon()
    try: g = unary_union(geos)
    except Exception: g = unary_union([shapely.set_precision(q, 0.01) for q in geos])
    g = shapely.make_valid(g)
    return g if g.geom_type in ('Polygon', 'MultiPolygon') else unary_union(polys(g))

def clipped(geos, region): return [U(geos).intersection(U(region))]


def snap(g): return shapely.make_valid(shapely.set_precision(g, 0.01))
def opening(g, d): return snap(g).buffer(-d / 2, 6).buffer(d / 2, 6)
def closing(g, d): return g.buffer(d / 2, 6).buffer(-d / 2, 6)

# ---------------------------------------------------------------- the picture: viewpoint geometry and ops
class Pic:
    """A picture for one viewpoint: a list of ops in design units, executed per plate in millimetres."""
    def __init__(self, name, geom_key, statue):
        self.name, self.statue = name, statue
        self.geom = json.load(open(os.path.join(ART, 'viewpoints.json')))[geom_key]
        asp = self.geom['aspect']
        self.DW, self.DH = (DESIGN, DESIGN / asp) if asp >= 1 else (DESIGN * asp, DESIGN)     # design units
        self.W, self.H = (MAXDIM, round(MAXDIM / asp)) if asp >= 1 else (round(MAXDIM * asp), MAXDIM)   # preview pixels
        self.S = self.W / self.DW
        self.ops = []; self.maze_seed = 1; self.maze_centre = None; self.keep_solid = None
    # picture coordinates: u right, v up, both 0..1 -> design units (y down)
    def P(self, u, v): return (u * self.DW, (1 - v) * self.DH)
    def mm(self, u, v):
        """mm per design unit at a picture point: the finest scale of every face that shows the point (from behind the
        side towers overlap the apex tower, and a stroke drawn there is cut on all of them, so it must be wide enough on
        the finest), the finer of the two directions."""
        best = None; fallback = None
        for f in self.geom['faces']:
            c = f['corners']; m = min(1000.0 / (f['u_per_m'] * self.DW), 1000.0 / (f['v_per_m'] * self.DH))
            if min(p[0] for p in c) - 1e-6 <= u <= max(p[0] for p in c) + 1e-6:
                if min(p[1] for p in c) <= v <= max(p[1] for p in c): best = m if best is None else min(best, m)
                else: fallback = m if fallback is None else min(fallback, m)
        return best or fallback or 2.0
    def wood_w(self, u, v, want=0.0): return max(want, LANE_MM / self.mm(u, v))
    def cut_w(self, u, v, want=0.0): return max(want, MIN_CUT_MM / self.mm(u, v))
    # ops
    def polar(self, centre, types, band_mm=120, pitch_mm=50, r0_mm=0.0, rot=0.0, region=None):
        self.ops.append(('polar', centre, dict(types=types, band_mm=band_mm, pitch_mm=pitch_mm, r0_mm=r0_mm, rot=rot), region))
    def ray_field(self, centre, pitch_mm, r0_mm, region=None): self.ops.append(('rays', centre, dict(pitch_mm=pitch_mm, r0_mm=r0_mm), region))
    def sub_region(self, region): self.ops.append(('sub', region, None, None))
    def add(self, geos): self.ops.append(('add', U(geos), None, None))
    def figure(self, geos): self.ops.append(('figure', U(geos), None, None))
    def lanes(self, geos): self.ops.append(('lanes', U(geos), None, None))
    def maze(self, centre, seed): self.maze_centre, self.maze_seed = centre, seed
    def fill(self, centre, types, band_mm=120, pitch_mm=50, r0_mm=0.0, rot=0.0):
        """A mandala over the large wood only: applied after every figure, clipped to the mask of the plate's cut domain
        minus every figure grown by FILL_MARGIN_MM (the slivers the clip leaves are removed by the final small-piece pass)."""
        self.ops.append(('fill', centre, dict(types=types, band_mm=band_mm, pitch_mm=pitch_mm, r0_mm=r0_mm, rot=rot), None))
    @staticmethod
    def disc_mm(centre, r_mm):
        """A region spec: points within r_mm of centre in the plate's local mm frame (resolved per plate)."""
        return ('disc_mm', centre, r_mm)

# ---------------------------------------------------------------- lattices in a plate's local mm frame
def sector(r0, r1, t0, t1, lane_mm):
    """An annular sector between angles t0..t1 (turns, counter-clockwise, y up in the local frame) and radii r0..r1,
    narrowed by lane_mm/2 on each side so neighbours leave a lane of exactly lane_mm."""
    if r1 - r0 < 1 or (t1 - t0) * TAU * r0 <= lane_mm + 1: return None
    n = max(3, int((t1 - t0) * TAU * r1 / 8)); rs = [lerp(r0, r1, i / 8) for i in range(9)]
    off = lambda r: (lane_mm / 2) / (TAU * r)
    pt = lambda r, t: (r * math.cos(TAU * t), r * math.sin(TAU * t))          # local frame: y up, angles counter-clockwise
    left = [pt(r, t0 + off(r)) for r in rs]; right = [pt(r, t1 - off(r)) for r in rs]
    outer = [pt(r1, lerp(t0 + off(r1), t1 - off(r1), i / n)) for i in range(n + 1)]
    inner = [pt(r0, lerp(t1 - off(r0), t0 + off(r0), i / n)) for i in range(n + 1)]
    p = Polygon(left + outer + right[::-1] + inner)
    if not p.is_valid: p = p.buffer(0)
    return p if p.area > 1 else None

class Frame:
    """A plate's local frame: X = (x - cx) * mm_h, Y = (cy - y) * mm_v from design units (y down) to local mm (y up),
    so lattices are drawn in physical millimetres at the face's own scale, then mapped exactly by the homography."""
    def __init__(self, mm_h, mm_v): self.mm_h, self.mm_v = mm_h, mm_v
    def local(self, cx, cy, x, y): return ((x - cx) * self.mm_h, (cy - y) * self.mm_v)
    def to_design(self, cx, cy, g):
        return shapely.transform(g, lambda a: np.column_stack([cx + a[:, 0] / self.mm_h, cy - a[:, 1] / self.mm_v]))
    def to_local(self, cx, cy, g):
        return shapely.transform(g, lambda a: np.column_stack([(a[:, 0] - cx) * self.mm_h, (cy - a[:, 1]) * self.mm_v]))
    def window(self, cx, cy, quad):
        """Radius and angle range (turns) of the plate's quad (design units) seen from (cx, cy), in local mm."""
        pts = [self.local(cx, cy, x, y) for x, y in quad]
        poly = Polygon(pts); rmin = 0.0 if poly.contains(Point(0, 0)) else poly.exterior.distance(Point(0, 0))
        rmax = max(math.hypot(x, y) for x, y in pts)
        if rmin < 1.0: return 0.0, rmax, 0.0, 1.0
        mid = math.atan2(sum(y for x, y in pts), sum(x for x, y in pts)) / TAU
        rel = [((math.atan2(y, x) / TAU - mid + 0.5) % 1.0) - 0.5 for x, y in pts]
        pad = 0.01 + 30 / (TAU * rmin)
        return rmin, rmax, mid + min(rel) - pad, mid + max(rel) + pad
    def polar(self, cx, cy, quad, types, band_mm, pitch_mm, r0_mm, rot, lane_mm=LANE_MM, maze=None):
        rmin, rmax, ta, tb = self.window(cx, cy, quad); out = []
        k0 = max(0, int((rmin - r0_mm) // band_mm) - 1); k1 = int((rmax - r0_mm) // band_mm) + 1
        for k in range(k0, k1 + 1):
            ra = r0_mm + k * band_mm; rb = ra + band_mm - lane_mm
            if rb <= 2: continue
            rm = ra + band_mm / 2; n = max(6, round(TAU * rm / pitch_mm)); typ = types[k % len(types)]
            j0 = int(math.floor((ta - rot) * n)) - 1; j1 = int(math.ceil((tb - rot) * n)) + 1
            for j in range(j0, j1 + 1):
                t0 = j / n + rot; t1 = t0 + 1 / n
                if typ == 'maze':
                    if j == j0 and maze is not None:                                   # once per band: the maze's corridors inside this annulus
                        ring = Point(0, 0).buffer(rb, 64).difference(Point(0, 0).buffer(max(ra, 1), 64))
                        out.append(self.to_local(cx, cy, maze.corridors(self, cx, cy, quad, ra, rb)).intersection(ring))
                    continue
                if typ == 'rays': out.append(sector(max(ra, 1), rb, t0, t1, lane_mm))
                elif typ == 'cells':
                    m = 0
                    while ra + m * pitch_mm < rb:
                        q0 = ra + m * pitch_mm; q1 = min(rb, q0 + pitch_mm - lane_mm); o = 0.5 / n if m % 2 else 0.0
                        out.append(sector(max(q0, 1), q1, t0 + o, t1 + o, lane_mm)); m += 1
                elif typ == 'petals':
                    tc = (t0 + t1) / 2; pts = []
                    for side in (1, -1):
                        for i in (range(25) if side == 1 else range(24, -1, -1)):
                            tt = i / 24; r = max(1.0, lerp(ra, rb, tt)); pitch_here = TAU * r / n
                            half = max(0.0, pitch_here / 2 - lane_mm / 2) * math.sin(math.pi * tt)
                            a = tc + side * half / (TAU * r); pts.append((r * math.cos(TAU * a), r * math.sin(TAU * a)))
                    p = Polygon(pts); out.append(p if p.is_valid else p.buffer(0))
        return [self.to_design(cx, cy, g) for g in out if g is not None and not g.is_empty]
    def ray_field(self, cx, cy, quad, pitch_mm, r0_mm, lane_mm=LANE_MM):
        rmin, rmax, ta, tb = self.window(cx, cy, quad); n = max(6, round(TAU * max(r0_mm, 60) / pitch_mm)); out = []
        for j in range(int(math.floor(ta * n)) - 1, int(math.ceil(tb * n)) + 2):
            out.append(sector(max(r0_mm, 1), rmax + 10, j / n, (j + 1) / n, lane_mm))
        return [self.to_design(cx, cy, g) for g in out if g is not None and not g.is_empty]
    def disc(self, cx, cy, r_mm): return self.to_design(cx, cy, Point(0, 0).buffer(r_mm, 48))

class Maze:
    """A circular maze: rings pitch_mm apart, sectors that double as the rings grow. Not a perfect maze (whose walls
    form a tree, every branch a cantilever hanging from one joint: owner, 2026-10-22, "make sure it's not hanging by
    a thread"): the full lattice of ring and radial walls loses walls at random, each only while both end joints keep
    at least two other walls, so every wall stays anchored at both ends and the wood keeps its loops."""
    def __init__(self, seed, pitch_mm=46, wall_mm=LANE_MM, r_max_mm=3200.0, remove=0.55):
        rnd = random.Random(seed); self.P, self.wall = pitch_mm, wall_mm; P_ = pitch_mm
        N = int(math.ceil(r_max_mm / P_)) + 1; self.N = N
        self.n = n = [max(4, 1 << int(round(math.log2(TAU * ((i + 0.5) * P_) / P_)))) for i in range(N)]
        self.ring = [np.ones(n[min(i + 1, N - 1)], bool) for i in range(N)]      # outer ring wall of ring i, per sector of ring i+1
        self.rad = [np.ones(n[i], bool) for i in range(N)]                        # radial walls of ring i at its sector boundaries
        ring, rad = self.ring, self.rad
        def joint_degree(i, b):
            d = 0
            if i > 0:
                m = n[i]; d += int(ring[i - 1][b % m]) + int(ring[i - 1][(b - 1) % m]); k = n[i] // n[i - 1]
                if b % k == 0: d += int(rad[i - 1][(b // k) % n[i - 1]])
            if i < N: d += int(rad[i][b % n[i]])
            return d
        cands = [('ring', i, c) for i in range(N - 1) for c in range(n[i + 1])] + [('rad', i, b) for i in range(1, N) for b in range(n[i])]
        rnd.shuffle(cands)
        for kind, i, x in cands[:int(len(cands) * remove)]:
            if kind == 'ring':
                if joint_degree(i + 1, x) >= 3 and joint_degree(i + 1, x + 1) >= 3: ring[i][x] = False
            else:
                k = n[min(i + 1, N - 1)] // n[i]
                if joint_degree(i, x) >= 3 and (i + 1 >= N or joint_degree(i + 1, x * k) >= 3): rad[i][x] = False
    def corridors(self, frame, cx, cy, quad, r_lo=None, r_hi=None):
        """Corridor polygons (local mm, mapped to design units) inside the plate's window: every cell as an annular sector
        narrowed by half a wall on each side, plus a passage polygon wherever a wall was removed. Walls are what is left
        between them, exactly wall_mm wide, with no morphology, so the lines stay crisp."""
        rmin, rmax, ta, tb = frame.window(cx, cy, quad); P_, w = self.P, self.wall; out = []
        i0 = max(0, int(rmin // P_) - 1); i1 = min(self.N - 1, int(rmax // P_) + 1)
        if r_lo is not None: i0 = max(i0, int(r_lo // P_))
        if r_hi is not None: i1 = min(i1, int(r_hi // P_))
        for i in range(i0, i1 + 1):
            ni = self.n[i]; n1 = self.n[min(i + 1, self.N - 1)]
            for j in range(int(math.floor(ta * ni)) - 1, int(math.ceil(tb * ni)) + 2):
                ra, rb = max(i * P_ + w / 2, 1), (i + 1) * P_ - w / 2
                out.append(sector(ra, rb, j / ni, (j + 1) / ni, w))                       # the cell
                if not self.rad[i][j % ni]:                                               # passage sideways into cell j-1
                    out.append(sector(ra + 0.1, rb - 0.1, j / ni - (w * 0.75) / (TAU * rb), j / ni + (w * 0.75) / (TAU * rb), 0))
                if i + 1 < self.N:
                    k = n1 // ni
                    for c in range(j * k, (j + 1) * k):
                        if not self.ring[i][c % n1]:                                      # passage outward into child c
                            out.append(sector(rb - 0.1, rb + w + 0.1, c / n1 + (w / 2) / (TAU * rb), (c + 1) / n1 - (w / 2) / (TAU * rb), 0))
        g = U([x for x in out if x is not None and not x.is_empty])
        return frame.to_design(cx, cy, g)
MAZES = {}

# ---------------------------------------------------------------- a plate
class Plate:
    def __init__(self, pic, fi):
        f = pic.geom['faces'][fi]; self.pic, self.tower, self.letter, self.h = pic, f['tower'], f['face'], float(f['h_mm'])
        self.quad = [pic.P(u, v) for u, v in f['corners']]           # design units: bottom-left, bottom-right, top-right, top-left
        self.frame = Frame(1000.0 / (f['u_per_m'] * pic.DW), 1000.0 / (f['v_per_m'] * pic.DH))
        src = np.array(self.quad, float); dst = np.array([(0, 0), (SIDE_MM, 0), (SIDE_MM, self.h), (0, self.h)], float)
        self.Hm = self._homography(src, dst); self.quad_poly = Polygon(self.quad).buffer(2)
        self.plate = box(0, 0, SIDE_MM, self.h)
        self.domain = box(BORDER_MM, max(BORDER_MM, BASE_MM), SIDE_MM - BORDER_MM, self.h - BORDER_MM)   # where cuts may be
        self.frame_wood = self.plate.difference(self.domain)
    @staticmethod
    def _homography(src, dst):
        A = []
        for (x, y), (X, Y) in zip(src, dst):
            A.append([x, y, 1, 0, 0, 0, -X * x, -X * y]); A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
        h = np.linalg.solve(np.array(A, float), dst.reshape(-1)); return np.append(h, 1.0).reshape(3, 3)
    def to_mm(self, g):
        """Design units -> plate mm (y up), exactly, vertex by vertex. Clipped to the plate's quad first: a lattice
        drawn far outside the quad can reach the homography's horizon, where points go to infinity."""
        g = shapely.set_precision(U(g), 0.001).intersection(self.quad_poly)
        if g.is_empty: return Polygon()
        def fn(a):
            a = np.asarray(a, float)[:, :2]; p = np.column_stack([a, np.ones(len(a))]) @ self.Hm.T; return p[:, :2] / p[:, 2:3]
        out = []
        for part in (g.geoms if hasattr(g, 'geoms') else [g]):
            if part.geom_type != 'Polygon' or part.is_empty: continue
            shell = fn(part.exterior.coords); holes = [fn(r.coords) for r in part.interiors]
            q = Polygon(shell, holes); out.append(q if q.is_valid else q.buffer(0))
        return U(out)
    def design_region(self, region):
        if region is None: return None
        if isinstance(region, tuple) and region[0] == 'disc_mm': return self.frame.disc(region[1][0], region[1][1], region[2])
        return U(region)
    # ---- composition
    def compose(self):
        pic = self.pic; D = self.domain; cuts = Polygon(); quad = self.quad
        maze = MAZES.get((pic.name, pic.maze_seed)); figs = Polygon(); fills = []
        for kind, a, kw, region in pic.ops:
            if kind == 'fill': fills.append((a, kw)); continue
            if kind in ('polar', 'rays'):
                geos = self.frame.polar(a[0], a[1], quad, maze=maze, **kw) if kind == 'polar' else self.frame.ray_field(a[0], a[1], quad, **kw)
                if region is not None:                                   # clip to the region (a lane inside its edge); drop cells the edge leaves under 40 %
                    reg = self.design_region(region).buffer(-LANE_MM / self.frame.mm_h, 8); kept = []
                    for g in geos:
                        for c in polys(g):
                            ci = c.intersection(reg)
                            if ci.area >= 0.4 * c.area: kept += polys(ci)
                    geos = kept
                cuts = cuts.union(self.to_mm(U(geos)).intersection(D))
            elif kind == 'sub': cuts = cuts.difference(self.to_mm(self.design_region(a)))
            elif kind == 'add': cuts = cuts.union(self.to_mm(a).intersection(D))
            elif kind == 'figure':
                fig = self.to_mm(a).intersection(D); figs = figs.union(fig); grown = fig.buffer(CONTOUR * LANE_MM, 8)
                keep = []                                                 # lattice cells the contour would leave under 40 %: dropped whole, no slivers
                for c in polys(cuts):
                    if not c.intersects(grown): keep.append(c); continue
                    rest = c.difference(grown)
                    if rest.area >= 0.4 * c.area: keep += polys(rest)
                cuts = U(keep).union(fig)
            elif kind == 'lanes': cuts = cuts.difference(self.to_mm(a).intersection(figs.buffer(CONTOUR * LANE_MM, 8)))   # a figure's lanes end in its contour, never beyond
        cuts = U(polys(cuts.intersection(D)))
        if fills:                                                        # the mandala fill, clipped to the mask (the small-piece pass cleans the edge)
            allowed = D.buffer(-LANE_MM / 2).difference(cuts.union(figs).buffer(FILL_MARGIN_MM, 8))   # margin round every cut so far: figures, gills, eye white
            if not allowed.is_empty:
                for centre, kw in fills:                                 # cell by cell against the mask: far cheaper than one big union
                    kept = [c for g in self.frame.polar(centre[0], centre[1], quad, maze=maze, **kw) for c in polys(self.to_mm(g)) if c.intersects(allowed)]
                    cuts = cuts.union(U([c.intersection(allowed) for c in kept]))
        if pic.maze_centre is not None:                              # the maze: corridors in blank wood and through solid cut
            corr = self.to_mm(maze.corridors(self.frame, pic.maze_centre[0], pic.maze_centre[1], quad))
            wood = self.plate.difference(cuts); blank = wood.buffer(-LANE_MM, 8).intersection(D)
            cuts = cuts.union(corr.intersection(blank))
            deep = cuts.buffer(-MAX_SOLID_MM / 2, 8)
            if not deep.is_empty:
                big = deep.buffer(MAX_SOLID_MM / 2 + 1, 8).intersection(cuts)
                if pic.keep_solid is not None: big = big.difference(self.to_mm(U(pic.keep_solid)))
                cuts = cuts.difference(big).union(corr.intersection(big))
        return U(polys(cuts))
    # ---- cuttability
    def cut_cantilevers(self, cuts):
        """A lane (wood no wider than a lane and a bit) that touches the rest of the wood at one place only hangs from
        that place and will break off (owner, 2026-10-22): cut it away. Nodes are the wood wider than a lane plus the
        plate's frame; every lane fragment between nodes must touch them at two or more separate places."""
        wood = self.plate.difference(cuts); nodes = opening(wood, LANE_MM + 8).union(self.frame_wood); hang = []
        for fr in polys(wood.difference(nodes)):
            if fr.area < 40: continue
            if len(polys(fr.buffer(0.8, 4).intersection(nodes))) <= 1: hang.append(fr.buffer(0.6, 4))
        if not hang: return cuts, 0
        return U(polys(cuts.union(U(hang)).intersection(self.domain))), len(hang)
    def enforce(self, cuts):
        """Cuttability without deforming the shapes: cut pieces too thin for the bit or too small to matter are dropped
        whole, wood too thin is cut, wood islands get bridges; nothing else is touched, so lines stay crisp."""
        D, plate = self.domain, self.plate; st = {'bridged': 0, 'thin_cut': 0.0, 'thin_wood': 0.0}
        cuts = snap(cuts.simplify(0.1))
        for rnd in range(2):
            parts = polys(cuts)
            keep = [p for p in parts if p.area >= 150 and not p.buffer(-MIN_CUT_MM / 2, 4).is_empty]
            st['thin_cut'] += sum(p.area for p in parts) - sum(p.area for p in keep); cuts = U(keep)
            wood = snap(plate.difference(cuts))                           # thin wood: what an opening removes, less a 2.5 mm tolerance so
            thin = wood.difference(snap(wood.buffer(-MIN_WOOD_MM / 2, 16).buffer(MIN_WOOD_MM / 2 + 2.5, 16))).intersection(D)   # inside corners are not bitten
            thin = U([p.buffer(1.0, 8).buffer(-1.0, 8) for p in polys(thin) if p.area > 60])
            st['thin_wood'] += thin.area; cuts = cuts.union(thin)
            # needles: parts of a cut narrower than the bit that hang off a wider cut (a lens tip, a cell clipped to a
            # sliver). Candidates are what an opening by MIN_CUT_MM removes; only the long, thin ones count (extent over
            # 14 mm, mean width over 1.5 mm): corner roundings are short and edge crescents are hair-thin
            cuts = snap(cuts); cand = polys(cuts.difference(snap(cuts.buffer(-MIN_CUT_MM / 2, 16).buffer(MIN_CUT_MM / 2, 16))))
            def needle(q):
                x0, y0, x1, y1 = q.bounds; ext = math.hypot(x1 - x0, y1 - y0)
                return ext > 14 and q.area / ext > 1.5
            needles = U([q.buffer(0.6, 4) for q in cand if needle(q)])
            if not needles.is_empty:
                needles = shapely.set_precision(needles, 0.01); cuts = shapely.set_precision(cuts, 0.01)
                st['thin_cut'] += needles.intersection(cuts).area; cuts = U(polys(cuts.difference(needles)))
            cuts, n_h = self.cut_cantilevers(cuts); st['cantilevers'] = st.get('cantilevers', 0) + n_h
            for it in range(4):
                wood = plate.difference(cuts); core = opening(wood, CORE_MM)
                parts = polys(core)
                safe = U([p for p in parts if p.intersects(self.frame_wood)]); isl = [p for p in parts if not p.intersects(self.frame_wood) and p.area > 25]
                if not isl: break
                bridges = []
                for island in isl:
                    a, b = nearest_points(island, safe)
                    dx, dy = b.x - a.x, b.y - a.y; L = math.hypot(dx, dy) or 1.0; ux, uy = dx / L, dy / L; e = CORE_MM
                    bridges.append(LineString([(a.x - ux * e, a.y - uy * e), (b.x + ux * e, b.y + uy * e)]).buffer(LANE_MM / 2, 6))
                cuts = cuts.difference(U(bridges)); st['bridged'] += len(bridges)
            else: st['stuck'] = True
            cuts, n_h = self.cut_cantilevers(cuts); st['cantilevers'] = st.get('cantilevers', 0) + n_h   # bridges overshoot their joints: the stubs go
        cuts = U(polys(shapely.set_precision(cuts, 0.01)))
        ok = lambda q: q.area >= MIN_PIECE_MM2 and not q.buffer(-MIN_CUT_MM / 2, 4).is_empty     # final pass: tiny or thin pieces go, whatever made them
        parts = polys(cuts); st['dropped'] = sum(1 for q in parts if not ok(q)); cuts = U([q for q in parts if ok(q)])
        wood = plate.difference(cuts); specks = [p for p in polys(wood) if not p.intersects(self.frame_wood) and p.area <= 40]
        if specks: cuts = U(polys(cuts.union(U(specks))))          # wood crumbs under the cutter's reach: cut them away
        wood = plate.difference(cuts); parts = polys(wood)
        loose = [p for p in parts if not p.intersects(self.frame_wood) and p.area > 4]
        return cuts, st, loose
    # ---- outputs
    def dxf(self, cuts):
        w, h = SIDE_MM, self.h; L = []
        push = lambda *a: L.extend(a)
        push('0', 'SECTION', '2', 'HEADER', '9', '$ACADVER', '1', 'AC1009', '9', '$EXTMIN', '10', '0', '20', '0', '30', '0', '9', '$EXTMAX', '10', f'{w:.3f}', '20', f'{h:.3f}', '30', '0', '0', 'ENDSEC')
        push('0', 'SECTION', '2', 'TABLES', '0', 'TABLE', '2', 'LAYER', '70', '2', '0', 'LAYER', '2', 'OUTLINE', '70', '0', '62', '7', '6', 'CONTINUOUS', '0', 'LAYER', '2', 'CUT', '70', '0', '62', '1', '6', 'CONTINUOUS', '0', 'ENDTAB', '0', 'ENDSEC')
        push('0', 'SECTION', '2', 'ENTITIES')
        def poly(layer, pts):
            push('0', 'POLYLINE', '8', layer, '66', '1', '70', '1')
            for x, y in pts: push('0', 'VERTEX', '8', layer, '10', f'{x:.3f}', '20', f'{y:.3f}')
            push('0', 'SEQEND')
        poly('OUTLINE', [(0, 0), (w, 0), (w, h), (0, h)])
        n = 0
        for p in polys(cuts):
            p = p.simplify(0.05)
            for ring in [p.exterior] + list(p.interiors):
                pts = list(ring.coords)[:-1]
                if len(pts) >= 3: poly('CUT', pts); n += 1
        push('0', 'ENDSEC', '0', 'EOF')
        return '\r\n'.join(L) + '\r\n', n
    def svg(self, cuts):
        """The same cuts as an SVG (mm units, y up), to inspect the vectors in any browser."""
        w, h = SIDE_MM, self.h
        d = ''
        for p in polys(cuts):
            for ring in [p.exterior] + list(p.interiors):
                d += 'M' + ' '.join(f'{x:.2f},{h - y:.2f}' for x, y in list(ring.coords)[:-1]) + 'Z '
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">'
                f'<rect width="{w}" height="{h}" fill="#d9b382"/><path d="{d}" fill="#222" fill-rule="evenodd"/></svg>')
    def raster(self, cuts, res=1.0):
        """The plate's cut mask at res mm, row 0 at the foot (for the preview picture)."""
        cols, rows = int(round(SIDE_MM / res)), int(round(self.h / res))
        im = Image.new('L', (cols, rows), 0); d = ImageDraw.Draw(im)
        for p in polys(cuts):
            d.polygon([(x / res, rows - y / res) for x, y in p.exterior.coords], fill=1)
            for r in p.interiors: d.polygon([(x / res, rows - y / res) for x, y in r.coords], fill=0)
        return np.array(im, bool)[::-1]

# ================================================================ figure parts (design units)
def hand(pic, cx, cy, a_dir, size, mirror=False):
    """A blessing hand seen from the front: the back of the hand an oval along the arm's direction a_dir, four fingers
    continuing outward and curling a little down, the thumb on the upper side. Returns (geos, wrist point)."""
    out = []; d = dirv(a_dir)
    out.append(shapely.affinity.rotate(shapely.affinity.scale(Point(cx, cy).buffer(1, 24), size * 0.5, size * 0.36), -a_dir, origin=(cx, cy)))
    for sp, L in ((-30, 0.8), (-10, 0.95), (10, 0.92), (30, 0.76)):
        a = a_dir + (sp if not mirror else -sp); dd = dirv(a)
        r0 = size * 0.4; base = (cx + dd[0]*r0, cy + dd[1]*r0); r1 = r0 + size * L
        tip = (cx + dd[0]*r1, cy + dd[1]*r1 + size * 0.22)            # the tip drops: the hand blesses what is below
        mid = (lerp(base[0], tip[0], 0.55), lerp(base[1], tip[1], 0.55) - size * 0.03)
        pts = spline([base, mid, tip], 10); w = size * 0.19; out += ribbon(pts, taper(pts, w * 1.1, w * 0.85))
    ta = a_dir - (75 if not mirror else -75); dd = dirv(ta)          # thumb on the upper side (owner, 2026-10-22)
    base = (cx + dd[0]*size*0.25, cy + dd[1]*size*0.25); tip = (cx + dd[0]*size*0.7 + d[0]*size*0.15, cy + dd[1]*size*0.7 + d[1]*size*0.15)
    out += ribbon([base, tip], [size * 0.16, size * 0.13])
    return out, (cx - d[0]*size*0.48, cy - d[1]*size*0.48)

def feather(pic, base, tip, half_w, W, H, sp0=None, sp1=None):
    """A feather from base to tip (owner's construction, 2026-10-22): the vane outline is the mask; inside it, a wood
    rachis down the middle and wood barbs at 55° towards the tip running from far beyond one edge to far beyond the
    other, so every cell is a parallelogram cut off by the outline, pointed where the outline meets it, never a
    rectangle. The quill (first 16 %) is a solid cut. Returns (cut geos, lane geos (none), the vane's region)."""
    dx, dy = tip[0] - base[0], tip[1] - base[1]; L = math.hypot(dx, dy) or 1; ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    def wv(t): return half_w * (0.16 + 0.84 * min(1.0, t / 0.3)) if t < 0.3 else half_w * (1.0 if t < 0.8 else math.sqrt(max(0.0, 1 - ((t - 0.8) / 0.2) ** 2)))
    region = []; Nr = 40
    for side in (1, -1):
        for i in (range(Nr + 1) if side == 1 else range(Nr, -1, -1)):
            t = i / Nr; w = wv(t); region.append((base[0] + dx * t + nx * w * side, base[1] + dy * t + ny * w * side))
    region = P(region)[0]
    lw = pic.wood_w(min(1, max(0, tip[0] / W)), 1 - tip[1] / H)
    lanes = ribbon([(base[0] + ux * 0.16 * L, base[1] + uy * 0.16 * L), (tip[0] + ux * 10, tip[1] + uy * 10)], lw, caps=False)   # rachis, from the quill to past the tip
    a = math.radians(55); fwd, out = math.cos(a), math.sin(a); far = 4 * half_w
    s_ = 0.16 * L + lw; step = max(2.2 * lw, 34)                                        # the quill is the first 16 %
    while s_ < L:                                                                        # barbs through the whole vane, both sides
        sx, sy = base[0] + ux * s_, base[1] + uy * s_
        for side in (1, -1):
            lanes += ribbon([(sx, sy), (sx + (ux * fwd + nx * side * out) * far, sy + (uy * fwd + ny * side * out) * far)], lw, caps=False)
        s_ += step
    cut = polys(region.difference(U(lanes)))
    return cut, [], region

def layered(items, lane):
    """Feathers listed back to front: each one hides the ones behind it, with a wood contour of `lane` between."""
    out = []; front = None
    for cut, _, region in reversed(items):
        c = U(cut) if front is None else U(cut).difference(front.buffer(lane, 6))
        out += polys(c); front = region if front is None else front.union(region)
    return out


def face_lanes(cx, cy, hr, lw, third_eye=True):
    """Wood features inside a cut (glowing) head of radius hr, every one a lane from contour to contour so nothing hangs
    from one end: an eye-level lane carrying the two eye almonds, a brow arc, a centre lane from the crown down to the
    smile (nose) carrying the third-eye lens, and the smile arc. All sizes in proportion to hr."""
    out = []; R = hr + 6
    ey = cy - 0.08 * hr
    out += ribbon([(cx - R, ey), (cx + R, ey)], lw, caps=False)                                            # eye level
    for s in (-1, 1):
        ex = cx + s * 0.45 * hr; out += lens((ex - 0.26 * hr, ey), (ex + 0.26 * hr, ey), 0.15 * hr)        # the eyes
    out += ribbon(spline([(cx - R, cy - 0.25 * hr), (cx - 0.45 * hr, cy - 0.42 * hr), (cx, cy - 0.3 * hr), (cx + 0.45 * hr, cy - 0.42 * hr), (cx + R, cy - 0.25 * hr)], 8), lw, caps=False)   # brow
    out += ribbon(spline([(cx - R, cy + 0.28 * hr), (cx - 0.5 * hr, cy + 0.48 * hr), (cx, cy + 0.55 * hr), (cx + 0.5 * hr, cy + 0.48 * hr), (cx + R, cy + 0.28 * hr)], 8), lw, caps=False)   # smile
    out += ribbon([(cx, cy - R), (cx, cy + 0.55 * hr)], lw, caps=False)                                     # crown to smile: the nose line
    if third_eye: out += lens((cx - 0.16 * hr, cy - 0.66 * hr), (cx + 0.16 * hr, cy - 0.66 * hr), 0.09 * hr)
    return out

# ================================================================ compositions
def woman_blessing(pic):
    """bench1: a woman blessing with her arms stretched to the sides. Head and torso on the apex tower (a narrow, tall
    slot in the picture), arms along the descending arms of the V, open hands on the tip towers, each with its own
    mandala of light; everything else a mandala radiating from her heart."""
    W, H, Pt = pic.DW, pic.DH, pic.P
    uc = 0.5543; heart = Pt(uc, 0.64)
    pic.fill(heart, ('rays', 'cells', 'petals', 'rays', 'cells'), band_mm=130, pitch_mm=52, r0_mm=40)
    hand_l, hand_r = Pt(0.105, 0.47), Pt(0.905, 0.47)
    head = Pt(uc, 0.875); hr = 105                           # the head spans the apex tower and the tops of its neighbours
    sh_l, sh_r = Pt(uc - 0.085, 0.72), Pt(uc + 0.085, 0.72)
    hand_g_l, wrist_l = hand(pic, hand_l[0], hand_l[1], 200, 175)
    hand_g_r, wrist_r = hand(pic, hand_r[0], hand_r[1], 340, 175, mirror=True)
    arm_l = spline([sh_l, Pt(0.40, 0.68), Pt(0.30, 0.62), Pt(0.21, 0.555), wrist_l], 14)
    arm_r = spline([sh_r, Pt(0.71, 0.68), Pt(0.78, 0.62), Pt(0.82, 0.555), wrist_r], 14)
    def arm_width(pts):
        n = len(pts); return [max(44, 70 / pic.mm(x / W, 1 - y / H)) * lerp(1.0, 0.78, i / max(1, n - 1)) for i, (x, y) in enumerate(pts)]
    waist_y = Pt(0, 0.60)[1]; hem_y = Pt(0, 0.44)[1]
    body = [sh_l, (sh_l[0] + 20, waist_y - 40), (sh_l[0] + 30, waist_y), (Pt(0.40, 0.44)[0], hem_y), (Pt(0.71, 0.44)[0], hem_y),
            (sh_r[0] - 30, waist_y), (sh_r[0] - 20, waist_y - 40), sh_r]
    fig = ribbon(arm_l, arm_width(arm_l)) + ribbon(arm_r, arm_width(arm_r)) + P(body)
    fig += ribbon([(head[0], head[1] + hr - 10), (head[0], sh_l[1] + 10)], 60) + dot(head[0], head[1], hr)
    lane_head = pic.wood_w(uc, 0.9)
    for i in range(20):                                     # hair: flame rays round the head, a lane away from it
        a = 90 + (i - 9.5) * (300 / 19)
        L = 150 * (0.55 + 0.45 * math.cos(math.radians(a - 90)) ** 2 * (1 if abs(a - 90) < 100 else 0.6))
        d = dirv(a); r0 = hr + lane_head + 4
        p0 = (head[0] + d[0]*r0, head[1] + d[1]*r0); p1 = (head[0] + d[0]*(r0 + L), head[1] + d[1]*(r0 + L))
        bend = dirv(a + (18 if i % 2 else -14)); mid = (lerp(p0[0], p1[0], 0.55) + bend[0]*16, lerp(p0[1], p1[1], 0.55) + bend[1]*16)
        pts = spline([p0, mid, p1], 10); fig += ribbon(pts, taper(pts, 24, 9))
    fig += hand_g_l + hand_g_r
    pic.figure(fig)
    pic.keep_solid = hand_g_l + hand_g_r + dot(head[0], head[1], hr)     # hands and face stay whole shapes (their own lanes suffice)
    lanes = face_lanes(head[0], head[1], hr, lane_head * 1.3)
    lw = pic.wood_w(uc, 0.65); chev = []; y = sh_l[1] + 30
    while y < hem_y + 30:                                          # chevrons and verticals between them: cells, no acute crossings
        depth = 34; pts = [(Pt(0.38, 0)[0], y - depth), (head[0] - 80, y - depth * 0.4), (head[0], y), (head[0] + 80, y - depth * 0.4), (Pt(0.73, 0)[0], y - depth)]
        sp = spline(pts, 8); chev += ribbon(sp, [pic.wood_w(x / W, 1 - y / H) for x, y in sp], caps=False); y += 38   # width from where each point lands
    for k in range(-7, 8):
        x = head[0] + k * 34 + (17 if k % 2 else 0); vp = [(x, sh_l[1] + 20), (lerp(x, x + k * 12, 0.5), lerp(sh_l[1] + 20, hem_y + 30, 0.5)), (x + k * 12, hem_y + 30)]
        chev += ribbon(vp, [pic.wood_w(px / W, 1 - py / H) for px, py in vp], caps=False)
    lanes += clipped(chev, P(body))
    hy = waist_y - 110
    lw_h = pic.wood_w(uc - 0.03, 0.66)                              # the wheel reaches the neighbours' plates: their lane width
    lanes += ribbon(arc_pts(head[0], hy, 46, 0, 360, 48), lw_h, caps=False)
    for i in range(8): d = dirv(i * 45); lanes += ribbon([(head[0] + d[0]*18, hy + d[1]*18), (head[0] + d[0]*46, hy + d[1]*46)], lw_h, caps=False)
    for arm in (arm_l, arm_r):
        total = plen(arm); s = 40
        last = 40 + 45 * int((total - 110 - 40) // 45)
        core = sub_path(arm, 40, last); lanes += ribbon(core, [pic.wood_w(x / W, 1 - y / H) for x, y in core], caps=False)   # first bracelet to last
        while s <= last:                                           # the lanes stop short of the hand, which stays one clean shape                                      # bracelets every 45 units, a lane along the middle: cells
            (x0, y0), (x1, y1) = at_len(arm, s - 2), at_len(arm, s + 2)
            dx, dy = x1-x0, y1-y0; d = math.hypot(dx, dy) or 1; nx, ny = -dy/d, dx/d; w = arm_width([(x0, y0)])[0] / 2 + 8
            lanes += ribbon([(x0 - nx*w, y0 - ny*w), (x0 + nx*w, y0 + ny*w)], pic.wood_w(x0 / W, 1 - y0 / H), caps=False); s += 45
    pic.lanes(lanes)
    return pic

def open_eye(pic):
    """back1: an open eye. The apex tower fills the middle of this tall picture, so the iris sits on it, the lids reach the
    side towers in the band they show; the eye white radiates from the iris, and everything around is a mandala."""
    W, H, Pt = pic.DW, pic.DH, pic.P
    cx, cy = Pt(0.5418, 0.60)
    pic.fill((cx, cy), ('cells', 'rays', 'petals', 'rays', 'cells'), band_mm=120, pitch_mm=50, r0_mm=60)
    xl, xr = 60, 1040; top, bot = cy - 300, cy + 255
    def lid(yt):
        left = bez((xl, cy), (xl + 0.55*(cx - xl), yt), (cx - 0.25*(cx - xl), yt), (cx, yt), 30)
        right = bez((cx, yt), (cx + 0.25*(xr - cx), yt), (xr - 0.55*(xr - cx), yt), (xr, cy), 30)
        return left + right[1:]
    upper, lower = lid(top), lid(bot)
    almond = P(upper + lower[::-1]); whole = box(-10, -10, W + 10, H + 10)
    iris_mm = 140; iris_r = 125                                  # the iris must clear both lids by a lane, rim dashes included                                  # the iris must fit the eye opening (300 up, 255 down); its rim was over the lid
    pic.polar((cx, cy), ('rays',), band_mm=120, pitch_mm=44, r0_mm=iris_mm + 40, region=[U(almond).buffer(-16)])   # clear of the lid strokes
    pic.sub_region(Pic.disc_mm((cx, cy), iris_mm))
    fig = dot(cx, cy, 72) + dashed_arc(cx, cy, iris_r + 30, 16, 70, 19, offset=5)
    gap = pic.wood_w(0.08, 0.6) + 10
    def trimmed(pts): L = plen(pts); return sub_path(pts, gap, L - gap)
    up, lo = trimmed(upper), trimmed(lower)
    fig += ribbon(up, [lerp(14, 24, math.sin(math.pi * i / (len(up) - 1))) for i in range(len(up))])
    fig += ribbon(lo, [lerp(12, 20, math.sin(math.pi * i / (len(lo) - 1))) for i in range(len(lo))])
    def lashes(pts, n, length, w0, w1, sign, s0, s1, bendk=0.35):
        """Clean tapered strokes rooted 30 units inside the lid (no cap at the base), curving towards the corners."""
        out = []; L = plen(pts)
        for i in range(n):
            t = lerp(s0, s1, i / (n - 1)); (x0, y0), (x1, y1) = at_len(pts, t*L - 2), at_len(pts, t*L + 2)
            dx, dy = x1-x0, y1-y0; d = math.hypot(dx, dy) or 1; nx, ny = sign * dy / d, -sign * dx / d
            k = length * (0.6 + 0.4 * math.sin(math.pi * t)); lean = (t - 0.5) * 2
            tip = (x0 + nx*k + dx/d*k*bendk*lean, y0 + ny*k + dy/d*k*bendk*lean)
            lidw = lerp(14, 24, math.sin(math.pi * t)); root = (x0 + nx*2, y0 + ny*2); mid = (lerp(root[0], tip[0], 0.5), lerp(root[1], tip[1], 0.5))
            pts2 = spline([root, mid, tip], 12); out += ribbon(pts2, taper(pts2, min(w0, lidw * 0.9), w1), caps=False) + dot(tip[0], tip[1], w1 / 2)
        return out
    fig += [U(lashes(upper, 7, 130, 24, 12, +1, 0.14, 0.86)).difference(U(almond))]   # whatever pokes into the eye white is cut flush
    brow = [(x, y - 195 - 70 * math.sin(math.pi * i / (len(upper) - 1))) for i, (x, y) in enumerate(upper)]
    brow = sub_path(brow, 200, plen(brow) - 200)
    fig += ribbon(brow, [lerp(16, 30, math.sin(math.pi * i / (len(brow) - 1)) ** 0.5) for i in range(len(brow))])
    TEARS = ((-150, 95), (-50, 130), (50, 130), (150, 95))                              # off the axis, which is a plate border
    for dx_, L in TEARS: fig += lens((cx + dx_, bot + 125), (cx + dx_, bot + 125 + L), 26, tip=0.7)
    flour = []
    for sgn, x0 in ((-1, xl), (1, xr)):
        flour += spiral(x0 + sgn*40, cy - 75, 6, 50, 1.6, 9, 15, a0=180 if sgn < 0 else 0, ccw=sgn > 0)
        for k, (dy0, L, curl) in enumerate(((-70, 1.0, 0.6), (70, 0.9, -0.5), (0, 1.25, 0.1))):
            pts = spline([(x0 + sgn*40, cy + dy0*0.6 + (20 if k == 2 else 0)), (x0 + sgn*90, cy + dy0*1.0), (x0 + sgn*(130 + 90*L), cy + dy0*1.6 + curl*60), (x0 + sgn*(170 + 170*L), cy + dy0*2.0 + curl*140)], 12)
            flour += ribbon(pts, taper(pts, 14, 8)) + dot(pts[-1][0] + sgn*18, pts[-1][1] + curl*14, 9)
    fig += clipped(flour, [box(0, cy - 240, W, cy + 240)])
    pic.figure(fig)
    pupil = ribbon([(cx - 90, cy), (cx + 90, cy)], pic.wood_w(0.54, 0.6), caps=False)   # with the plates' border down the middle: a cross
    for dx_, L in TEARS:
        pupil += ribbon([(cx + dx_, bot + 125 - 4), (cx + dx_, bot + 125 + L + 4)], pic.wood_w(0.54, 0.45), caps=False)   # top to tip
    cw_ = pic.wood_w(0.05, 0.6) + 6
    pupil += ribbon([(xl - 10, cy), (0, cy)], cw_, caps=False) + ribbon([(xr + 10, cy), (W, cy)], cw_, caps=False)   # the eye white reaches the outside through each corner
    pic.lanes(pupil)
    return pic

def bird_third_eye(pic):
    """bench2: a bird with open wings and a radiant third eye. Head and breast on the apex tower, each wing a fan of
    feathers along one arm of the V to the tip tower, the third eye's energy as a mandala over the whole picture."""
    W, H, Pt = pic.DW, pic.DH, pic.P
    uc = 0.5543; xc = Pt(uc, 0)[0]; eye = Pt(uc, 0.948)
    pic.fill(eye, ('rays', 'cells', 'petals', 'rays', 'cells'), band_mm=130, pitch_mm=50, r0_mm=60)
    def mirror(pt): return (xc + (xc - pt[0]) * 0.82, pt[1])     # the right side of the picture is narrower
    def wing(side):
        """Eight feathers in a fan: bases on a short line down the body's side, tips on an arc from above the shoulder
        round to below; the base-to-tip angle changes monotonically, so no two feathers cross, and the vane widths follow
        the local spacing (feather()), so no two overlap."""
        M = (lambda q: q) if side < 0 else mirror
        bases = [M(q) for q in [(1000, 235), (990, 275), (978, 318), (964, 364), (950, 412), (936, 462), (922, 512), (908, 560)]]
        tips = [M(q) for q in spline([(600, 110), (380, 190), (210, 340), (130, 530), (140, 720), (230, 880), (380, 990), (560, 1040)], 1)]
        items = [feather(pic, b, tp, 70, W, H) for b, tp in zip(bases, tips)]      # back (top) to front (bottom)
        feathers = layered(items, 1.2 * pic.wood_w(0.3, 0.6)); veins = []; coverts = []
        hull = U(feathers).convex_hull
        return feathers + coverts, veins, hull
    fl, vl, hl = wing(-1); fr, vr, hr_ = wing(+1)
    hr = 70; head = (xc - 10, Pt(uc, 0.915)[1])                 # the head, turned to the left, with a beak
    neck_top = (xc, head[1] + hr - 6); breast_bot = Pt(uc, 0.70)        # the body ends above the apex tower's unlit base (v 0.61)
    fig = fl + fr + lens(neck_top, breast_bot, 118, tip=0.42) + dot(head[0], head[1], hr)
    bx = head[0] - hr + 16                                        # the beak: a hooked parrot beak, big enough to read from the bench
    beak = spline([(bx, head[1] - 40), (bx - 70, head[1] - 48), (bx - 135, head[1] - 10), (bx - 120, head[1] + 40), (bx - 60, head[1] + 22), (bx, head[1] + 44)], 6)
    fig += P(beak)
    tail = []
    tails = []; titems = []
    for k, a in enumerate((236, 253, 270, 287, 304)):
        d = dirv(a); b = (xc, breast_bot[1] - 70); L = 150 if k in (1, 3) else (175 if k == 2 else 120)
        titems.append(feather(pic, (b[0] + d[0] * 40, b[1] + d[1] * 40), (b[0] + d[0]*L, b[1] + d[1]*L), 30, W, H))
    fig += layered(titems[:3] + titems[4:] + [titems[2]] if False else [titems[0], titems[4], titems[1], titems[3], titems[2]], 1.2 * pic.wood_w(uc, 0.62))   # the middle feather in front
    for a in (60, 75, 90, 105):                                   # crest, leaning back from the beak
        d = dirv(a); r0 = hr + pic.wood_w(uc, 0.93) + 2
        fig += ribbon([(head[0] + d[0]*r0, head[1] + d[1]*r0), (head[0] + d[0]*(r0 + 70), head[1] + d[1]*(r0 + 70))], [16, 7])
    pic.figure(fig)
    pic.keep_solid = dot(head[0], head[1], hr) + P(beak)
    lw = pic.wood_w(uc, 0.75); lh = pic.wood_w(uc, 0.93)
    # face: every wood lane runs from contour to contour, so nothing in the head hangs from one end (owner: "the bird's eye
    # will absolutely break off"). A horizontal lane at eye level carries the eye (a wood almond on it), a vertical lane
    # closes the beak's base, a brow arc goes from the beak's base up to the top of the head, the third eye sits on it.
    ex, ey = head[0] - hr * 0.3, head[1] - hr * 0.12
    lanes = ribbon([(head[0] - hr - 6, ey), (head[0] + hr + 6, ey)], lh, caps=False)                       # eye level, edge to edge
    lanes += lens((ex - hr * 0.3, ey), (ex + hr * 0.3, ey), hr * 0.17)
    lanes += ribbon([(bx, head[1] - hr - 6), (bx, head[1] + hr + 6)], lh, caps=False)                       # beak base, top to bottom
    lanes += ribbon(spline([(bx, head[1] - hr * 0.45), (ex + hr * 0.15, head[1] - hr * 0.62), (head[0] + hr * 0.35, head[1] - hr * 0.45), (head[0] + hr + 6, head[1] - hr * 0.1)], 8), lh, caps=False)   # brow arc
    lanes += ribbon([(head[0], head[1] - hr - 6), (head[0], head[1] - hr * 0.5)], lh, caps=False)            # top of the head down to the brow
    lanes += lens((head[0] - hr * 0.12, head[1] - hr * 0.78), (head[0] + hr * 0.12, head[1] - hr * 0.78), hr * 0.09)   # the third eye, on that lane
    lanes += vl + vr
    lanes += ribbon([(xc, neck_top[1] + 10), (xc, breast_bot[1] - 10)], lw, caps=False)
    y = neck_top[1] + 30; herring = []
    while y < breast_bot[1] - 20:
        for sgn in (-1, 1): herring += ribbon([(xc, y), (xc + sgn*135, y + 40)], lw, caps=False)
        y += 30
    lanes += clipped(herring, [box(xc - 135, neck_top[1], xc + 135, breast_bot[1])])
    lanes += tails
    pic.lanes(lanes)
    return pic

def magic_mushroom(pic):
    """back2: a magical mushroom. The cap's dome on the apex tower, its rim sweeping down over the side towers with the
    gills beneath, the stem with its ring, spores and small mushrooms around the foot, energy radiating from the cap."""
    from scipy.spatial import Voronoi
    W, H, Pt = pic.DW, pic.DH, pic.P
    xc = Pt(0.5418, 0)[0]
    pic.fill((xc, 700), ('cells', 'rays', 'petals', 'rays', 'cells'), band_mm=120, pitch_mm=50, r0_mm=60)
    cap_top = spline([(0, 1000), (120, 700), (300, 380), (450, 160), (xc, 60), (740, 160), (890, 380), (1000, 700), (W, 1000)], 10)
    rim = spline([(0, 1000), (150, 870), (350, 770), (xc, 730), (840, 770), (950, 870), (W, 1000)], 10)
    under = spline([(0, 1000), (200, 1040), (400, 1072), (xc, 1085), (790, 1072), (900, 1040), (W, 1000)], 10)
    cap_poly = P(cap_top + rim[::-1]); gill_poly = P(rim + under[::-1])
    focus = (xc, 1100); stem_top, stem_bot = 1090, 1800
    stem = P(spline([(482, stem_top), (470, 1250), (478, 1450), (462, 1650), (440, stem_bot), (750, stem_bot), (728, 1650), (712, 1450), (720, 1250), (708, stem_top)], 8))
    rnd = random.Random(7); seeds = []                                # cap: a crackle of wood lanes (Voronoi edges) through a cut dome
    for gy in range(40, 1000, 92):
        for gx in range(-40, int(W) + 60, 92): seeds.append((gx + rnd.uniform(-30, 30) + (46 if (gy // 92) % 2 else 0), gy + rnd.uniform(-28, 28)))
    vor = Voronoi(np.array(seeds)); crack = []
    for (a, b) in vor.ridge_vertices:
        if a < 0 or b < 0: continue
        pa, pb = vor.vertices[a], vor.vertices[b]
        if max(abs(pa[0]), abs(pa[1]), abs(pb[0]), abs(pb[1])) > 4000: continue
        crack += ribbon([tuple(pa), tuple(pb)], pic.wood_w(min(1, max(0, (pa[0] + pb[0]) / 2 / W)), 1 - (pa[1] + pb[1]) / 2 / H))
    cells = polys(U(cap_poly).difference(U(crack + ribbon(rim, pic.wood_w(0.54, 0.62), caps=False))))   # the cap as crackle cells
    med = sorted(c.area for c in cells)[len(cells) // 2]
    cells = [c for c in cells if not c.buffer(-6).is_empty]                               # only true slivers go
    pic.figure(cells)
    pic.keep_solid = cells                                       # the crackle's large blocks stay (owner, 2026-10-22)
    pic.polar(focus, ('rays',), band_mm=150, pitch_mm=48, r0_mm=150, region=gill_poly)   # banded: the pitch stays 48 mm out to the rim
    collar = dashed_arc(focus[0], focus[1], 98, 13, 44, 19, a0=4, a1=176) + dashed_arc(focus[0], focus[1], 132, 13, 50, 19, a0=4, a1=176, offset=22)
    pic.figure(clipped(collar, gill_poly) + stem)
    fibres = []
    for k in range(5):
        x0 = 505 + k * 45; pts = [(x0 + 14 * math.sin(k + y / 90), y) for y in range(stem_top + 60, stem_bot + 20, 20)]
        fibres += ribbon(pts, pic.wood_w(0.54, 0.3), caps=False)
    for y in range(stem_top + 110, stem_bot - 40, 95): fibres += ribbon([(420, y + 18), (xc, y), (780, y + 18)], pic.wood_w(0.54, 0.3), caps=False)
    ring_y = 1230
    ring = P([(430, ring_y - 10), (760, ring_y - 10), (790, ring_y + 70), (720, ring_y + 55), (xc, ring_y + 40), (470, ring_y + 55), (400, ring_y + 70)])
    pic.add(ring)
    pic.lanes(clipped(fibres, stem) + ribbon([(400, ring_y + 22), (xc, ring_y + 6), (790, ring_y + 22)], pic.wood_w(0.54, 0.4), caps=False)
              + ribbon([(430, ring_y - 10), (760, ring_y - 10)], pic.wood_w(0.54, 0.4), caps=False))
    extra = []
    for (mx, my, mr, h) in ((372, 1700, 46, 98), (805, 1655, 58, 143), (335, 1765, 28, 36)):
        extra += P(arc_pts(mx, my, mr, 0, 180, 24)) + ribbon([(mx, my + 2), (mx, my + h)], 26)
    for k in range(7):
        x0 = 300 + k * 85; pts = spline([(x0, stem_bot - 6), (x0 + rnd.uniform(-40, 40), stem_bot + 50), (x0 + rnd.uniform(-70, 70), stem_bot + 110)], 8)
        extra += ribbon(pts, taper(pts, 12, 6))
    for sgn, x0 in ((-1, 215), (1, 885)):                        # on T6 and T2, below the gills, inside the lit area
        extra += spiral(x0, 1110, 6, 42, 1.6, 10, 16, ccw=sgn > 0)
    pic.figure(extra)
    return pic

# ================================================================ run a picture: every plate, DXF, preview
def write_picture(pic, plates, masks):
    """The preview PNG for the tool: every pixel inside a face's quad takes that plate's cut at 1 mm (nearest cell)."""
    W, H, S = pic.W, pic.H, pic.S
    img = np.zeros((H, W), bool); face_id = np.full((H, W), -1, np.int16)
    order = sorted(range(len(plates)), key=lambda i: -pic.geom['faces'][i]['u_per_m'])     # the nearer plate wins where faces overlap
    for fi in order:
        pl, m = plates[fi], masks[fi]
        q = [(x * S, y * S) for x, y in pl.quad]
        im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).polygon(q, fill=1); reg = np.array(im, bool) & (face_id < 0)
        ys, xs = np.nonzero(reg)
        if not len(ys): continue
        pts = np.column_stack([xs + 0.5, ys + 0.5]) / S
        p = np.column_stack([pts, np.ones(len(pts))]) @ pl.Hm.T; fx, fy = p[:, 0] / p[:, 2], p[:, 1] / p[:, 2]
        ci = np.clip(fx.astype(int), 0, m.shape[1] - 1); cj = np.clip(fy.astype(int), 0, m.shape[0] - 1)
        img[ys, xs] = m[cj, ci]; face_id[ys, xs] = fi
    Image.fromarray(np.where(img, 0, 255).astype(np.uint8)).convert('1').save(os.path.join(ART, pic.name + '.png'), optimize=True)
    a = np.where(img, 0, 255).astype(np.uint8); rgb = np.stack([a, a, a], -1); off = face_id < 0; rgb[off] = (rgb[off] * 0.55 + 70).astype(np.uint8)
    im = Image.fromarray(rgb); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for pl in plates:
        c = [(x * S, y * S) for x, y in pl.quad]
        def at(fu, fv):
            bx, by = lerp(c[0][0], c[1][0], fu), lerp(c[0][1], c[1][1], fu); tx, ty = lerp(c[3][0], c[2][0], fu), lerp(c[3][1], c[2][1], fu)
            return (lerp(bx, tx, fv), lerp(by, ty, fv))
        fu, fv = BORDER_MM / SIDE_MM, BORDER_MM / pl.h; fb = BASE_MM / pl.h
        d.polygon(c, fill=(120, 120, 120, 150)); d.polygon([at(fu, max(fv, fb)), at(1 - fu, max(fv, fb)), at(1 - fu, 1 - fv), at(fu, 1 - fv)], fill=(0, 0, 0, 0))
        d.polygon(c, outline=(40, 120, 255, 255), width=3); d.text((sum(p[0] for p in c) / 4 - 12, min(p[1] for p in c) + 6), pl.tower + pl.letter, fill=(40, 120, 255, 255))
    Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB').save(os.path.join(ART, pic.name + '-preview.png'), optimize=True)

def _plate_job(args):
    name, fi = args
    pic = PICS[name]()
    if pic.maze_centre is not None and (pic.name, pic.maze_seed) not in MAZES: MAZES[(pic.name, pic.maze_seed)] = Maze(pic.maze_seed)
    pl = Plate(pic, fi); cuts = pl.compose(); cuts, st, loose = pl.enforce(cuts)
    txt, n = pl.dxf(cuts); fn = f'S{pic.statue}-{pl.tower}-{pl.letter}.dxf'
    open(os.path.join(DXF, fn), 'w').write(txt); open(os.path.join(DXF, fn[:-4] + '.svg'), 'w').write(pl.svg(cuts))
    flag = (' LOOSE WOOD: ' + ', '.join(f'{p.area:.0f} mm2' for p in loose)) if loose else ''
    line = f'{fn}: {cuts.area / pl.domain.area * 100:.0f} % cut, {n} contours, {st["bridged"]} bridge(s), thin cut {st["thin_cut"]:.0f} mm2 and thin wood {st["thin_wood"]:.0f} mm2 removed' + (' STUCK' if st.get('stuck') else '') + flag
    return fi, pl.raster(cuts), cuts.area, pl.domain.area, line, pl.raster(cuts, 0.5)

def write_towers(pic, plates, masks, res=0.5):
    """art/<name>-towers.png: only what is on the plates, as seen from the viewpoint, at TOWERS_DIM on the long side,
    from the plates' cuts rasterised at `res` mm: wood in plywood colour, cuts dark, everything else transparent.
    Anti-aliased by four sub-pixel samples per pixel (a 2x image and a resize took over a minute per picture)."""
    k = TOWERS_DIM / max(pic.DW, pic.DH); W, H = int(round(pic.DW * k)), int(round(pic.DH * k))
    cov = np.zeros((H, W), np.float32); face_id = np.full((H, W), -1, np.int16)
    order = sorted(range(len(plates)), key=lambda i: -pic.geom['faces'][i]['u_per_m'])
    for fi in order:
        pl, m = plates[fi], masks[fi]
        q = [(x * k, y * k) for x, y in pl.quad]
        im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).polygon(q, fill=1); reg = np.array(im, bool) & (face_id < 0)
        ys, xs = np.nonzero(reg)
        if not len(ys): continue
        acc = np.zeros(len(ys), np.float32)
        for ox, oy in ((0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)):
            pts = np.column_stack([xs + ox, ys + oy]) / k
            p = np.column_stack([pts, np.ones(len(pts))]) @ pl.Hm.T; fx, fy = p[:, 0] / p[:, 2], p[:, 1] / p[:, 2]
            ci = np.clip((fx / res).astype(int), 0, m.shape[1] - 1); cj = np.clip((fy / res).astype(int), 0, m.shape[0] - 1)
            acc += m[cj, ci]
        cov[ys, xs] = acc / 4; face_id[ys, xs] = fi
    c = cov[..., None]
    rgb = (np.array([217, 179, 130], np.float32) * (1 - c) + np.array([22, 22, 22], np.float32) * c).astype(np.uint8)
    alpha = np.where(face_id >= 0, 255, 0).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, alpha]), 'RGBA').save(os.path.join(ART, pic.name + '-towers.png'), optimize=True)

def write_design(pic):
    """art/<name>-design.png: the composition as drawn, in the picture plane, before any plate: figures and lanes as
    polygons in design units (lattices at the apex plate's scale), with the towers' outlines over it. What the plates
    would get if there were no borders, bases, contours or cuttability rules; for judging the design itself."""
    k = MAXDIM / max(pic.DW, pic.DH); W, H = int(round(pic.DW * k)), int(round(pic.DH * k))
    apex = next(fi for fi, f in enumerate(pic.geom['faces']) if f['tower'] == 'T4'); pl = Plate(pic, apex)
    quad_all = [(0, 0), (pic.DW, 0), (pic.DW, pic.DH), (0, pic.DH)]; cuts = Polygon()
    maze = MAZES.get((pic.name, pic.maze_seed))
    for kind, a, kw, region in sorted(pic.ops, key=lambda op: op[0] == 'fill'):          # the fill last, as on the plates
        if kind in ('polar', 'rays'):
            g = U(pl.frame.polar(a[0], a[1], quad_all, maze=maze, **kw) if kind == 'polar' else pl.frame.ray_field(a[0], a[1], quad_all, **kw))
            if region is not None: g = g.intersection(pl.design_region(region))
            cuts = cuts.union(g)
        elif kind == 'sub': cuts = cuts.difference(pl.design_region(a))
        elif kind == 'add': cuts = cuts.union(a)
        elif kind == 'figure': cuts = cuts.difference(a.buffer(CONTOUR * LANE_MM / pl.frame.mm_h, 8)).union(a)
        elif kind == 'lanes': cuts = cuts.difference(a)
        elif kind == 'fill':
            allowed = box(0, 0, pic.DW, pic.DH).difference(cuts.buffer(FILL_MARGIN_MM / pl.frame.mm_h, 8))
            cuts = cuts.union(U(pl.frame.polar(a[0], a[1], quad_all, maze=maze, **kw)).intersection(allowed))
    im = Image.new('RGB', (W, H), (217, 179, 130)); d = ImageDraw.Draw(im)
    for p in polys(cuts):
        d.polygon([(x * k, y * k) for x, y in p.exterior.coords], fill=(22, 22, 22))
        for r in p.interiors: d.polygon([(x * k, y * k) for x, y in r.coords], fill=(217, 179, 130))
    for f in pic.geom['faces']:
        d.polygon([(u * W, (1 - v) * H) for u, v in f['corners']], outline=(40, 120, 255), width=4)
    im.save(os.path.join(ART, pic.name + '-design.png'), optimize=True)

def run(name, verbose):
    """One picture: its 14 plates in parallel across the cores (each plate is independent), then the preview."""
    import multiprocessing as mp
    t0 = time.time(); pic = PICS[name](); n_faces = len(pic.geom['faces'])
    os.makedirs(DXF, exist_ok=True)
    with mp.get_context('fork').Pool(min(n_faces, max(1, os.cpu_count() or 1))) as pool:
        results = pool.map(_plate_job, [(name, fi) for fi in range(n_faces)])
    results.sort(); plates = [Plate(pic, fi) for fi in range(n_faces)]
    masks = [r[1] for r in results]; total_cut = sum(r[2] for r in results); total_area = sum(r[3] for r in results)
    write_picture(pic, plates, masks)
    write_towers(pic, plates, [r[5] for r in results])
    write_design(pic)
    print(f'{name}: {total_cut / total_area * 100:.0f} % of the plates cut, {n_faces} DXF files in art/dxf, {time.time() - t0:.0f} s', flush=True)
    for r in results:
        if verbose or 'LOOSE' in r[4] or 'STUCK' in r[4]: print('  ' + r[4])

PICS = {   # statue 2's viewpoints see the same silhouette as statue 1's, so they share the geometry
    'bench1': (lambda: woman_blessing(Pic('bench1', 'bench1', 1))),
    'back1': (lambda: open_eye(Pic('back1', 'back1', 1))),
    'bench2': (lambda: bird_third_eye(Pic('bench2', 'bench1', 2))),
    'back2': (lambda: magic_mushroom(Pic('back2', 'back1', 2))),
}

if __name__ == '__main__':
    verbose = '-v' in sys.argv; names = [a for a in sys.argv[1:] if not a.startswith('-')] or list(PICS)
    for n in names: run(n, verbose)
