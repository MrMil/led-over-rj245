#!/usr/bin/env python3
"""Check an artist's cut drawing against the real plates, and add minimal wood supports.

The drawing (a DXF in the artist's own units; filled shapes are the cuts, as the layout tool reads
it) is projected onto every plate of its viewpoint exactly as tools/statue_render.html projects it,
using the projection extracted from the tool (art/<viewpoint>/<viewpoint>-projection.json, see
docs/art/eye_final.md), then each plate is checked in millimetres:

  island   a wood region touching no plate edge: it falls out of the cut
  loose    a wood region that an opening by MIN_WOOD_MM separates from the plate edge: held by a
           neck thinner than MIN_WOOD_MM (the neck's width is measured), or by nothing
  speck    a wood pocket under FILL_ISLAND_MM2 held by under 2 mm, or a wedge of wood under PINCH_MM wide
           between two cuts that all but touch; cut away, with --support in the drawing and in the cut files regardless

With --support, every island and loose piece gets two bridges (wood lanes BRIDGE_MM wide, from the
piece to the nearest safe wood, on two different sides) and islands under FILL_ISLAND_MM2 are cut
away instead; the bridges are mapped back into the drawing and the check is run again until nothing
is left. --shrink-bottom applies the tool's "shrink from bottom" inset; --bake writes the output
drawing so that it needs no inset (the drawing's box is extended at the shrunk end by marker squares
that land outside every plate; --shrink-top works the same way). --cut DIR writes the per-plate cut files for the laser (S<statue>-T<n>-<face>.dxf,
R12, mm, layer OUTLINE the plate and CUT the holes), manifest.json and plates.png; it refuses a drawing that still
has islands or loose pieces. Outputs go to --out: <stem>-check.png (the drawing with every problem
circled), <stem>-plates.png (the 14 plates), and with --support <stem>-supported.dxf/.png.

Runs in the project's .venv (python3 -m venv .venv; .venv/bin/pip install -r requirements.txt).
"""
import argparse, json, math, os, sys
import numpy as np, shapely, shapely.affinity, ezdxf
from ezdxf import path as ezpath
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

MIN_WOOD_MM = 15.0        # wood thinner than this holds nothing (docs/art/cuttability.md)
BRIDGE_MM = 18.0          # a support is a lane of this width (the generator's LANE_MM)
OVERSHOOT_MM = 12.0       # a bridge runs this far into the wood at both ends
FILL_ISLAND_MM2 = 400.0   # an island smaller than this is cut away rather than bridged
FLAT = 0.0015             # flattening tolerance in drawing units (0.3 mm on the farthest plate when the unit is cm)
MIN_PIECE_MM2 = 4.0       # specks under this are ignored, as the tool's island report ignores them
PINCH_MM, PINCH_MM2 = 4, 60.0   # a wood wedge narrower than this and smaller than this between two cuts is cut away


def polys(g):
    return [p for p in getattr(g, 'geoms', [g]) if p.geom_type == 'Polygon' and not p.is_empty]


def opening(g, d):
    return g.buffer(-d / 2, 8).buffer(d / 2, 8)


def valid(g):
    return shapely.make_valid(shapely.set_precision(g, 1e-6))


def xform(g, f):
    """Map every polygon of g through f (an Nx2 -> Nx2 function), ring by ring. shapely.transform refuses a ring
    whose first and last points differ in the last bit, which set_precision can leave behind; Polygon() closes them."""
    out = []
    for p in polys(g):
        shell = f(np.asarray(p.exterior.coords))
        holes = [f(np.asarray(r.coords)) for r in p.interiors]
        if np.isfinite(shell).all() and all(np.isfinite(h).all() for h in holes):
            out.append(shapely.make_valid(Polygon(shell, holes)))
    return valid(unary_union(out)) if out else Polygon()


def evenodd(rings):
    """Rings (point lists) filled even-odd: a ring inside an odd number of others is a hole."""
    ps = [Polygon(r) for r in rings if len(r) >= 3]
    ps = [shapely.make_valid(p) for p in ps if p.area > 0]
    if not ps:
        return Polygon()
    tree = STRtree(ps)
    # depth by containment of the whole ring, not of a sample point: an outer ring's representative point can fall
    # inside one of its own holes (the artist's loop glyphs did), which would turn the outer ring into a hole
    depth = [sum(1 for i in tree.query(p, predicate='within') if ps[i] is not p) for p in ps]
    outer = [p for p, d in zip(ps, depth) if d % 2 == 0]
    holes = unary_union([p for p, d in zip(ps, depth) if d % 2 == 1]) if any(d % 2 for d in depth) else None
    g = unary_union(outer)
    return valid(g.difference(holes)) if holes is not None else valid(g)


def read_drawing(path):
    """The filled shapes of a DXF as one polygon set in drawing units, plus the unit code.
    HATCH entities when the file has them (Illustrator exports every filled shape as a HATCH plus its
    outline spline), else every closed outline filled even-odd, as the layout tool reads a DXF."""
    doc = ezdxf.readfile(path)
    units = doc.header.get('$INSUNITS', 0)
    ents = []
    for e in doc.modelspace():
        if e.dxftype() == 'INSERT':          # Illustrator puts the drawing in one block at the origin
            ents += list(doc.blocks.get(e.dxf.name))
        else:
            ents.append(e)
    hatches = [e for e in ents if e.dxftype() == 'HATCH']
    if hatches:
        shapes = []
        for e in hatches:
            rings = [[(v.x, v.y) for v in sp.flattening(FLAT)] for p in ezpath.from_hatch(e) for sp in p.sub_paths()]
            shapes.append(evenodd(rings))
        return valid(unary_union(shapes)), units
    rings = []
    for e in ents:
        if e.dxftype() in ('SPLINE', 'LWPOLYLINE', 'POLYLINE', 'CIRCLE', 'ELLIPSE'):
            p = ezpath.make_path(e)
            pts = [(v.x, v.y) for v in p.flattening(FLAT)]
            if len(pts) >= 3 and (p.is_closed or math.dist(pts[0], pts[-1]) < 1e-6):
                rings.append(pts)
    return evenodd(rings), units


class Plate:
    """One face: the exact map between its millimetres and the drawing, as the tool projects it."""

    def __init__(self, face, proj, insets, bounds):
        c = face['coef']
        self.name = f"{face['tower']}-{face['face']}"
        self.pw, self.h = float(face['width_mm']), float(face['height_mm'])
        self.border, self.unlit = proj['border_mm'], proj['unlit_mm']
        self.H = np.array([[c['rR'], c['uR'], c['oR']], [c['rU'], c['uU'], c['oU']], [c['rF'], c['uF'], c['oF']]])
        self.Hinv = np.linalg.inv(self.H)
        b = proj['box']
        bw, bh = b['x1'] - b['x0'], b['y1'] - b['y0']
        self.x0, self.x1 = b['x0'] + bw * insets['l'], b['x1'] - bw * insets['r']
        self.y0, self.y1 = b['y0'] + bh * insets['b'], b['y1'] - bh * insets['t']
        self.xmin, self.ymin, self.xmax, self.ymax = bounds
        self.plate = box(0, 0, self.pw, self.h)
        self.region = box(self.border, max(self.border, self.unlit), self.pw - self.border, self.h - self.border)
        self.edge = self.plate.exterior.buffer(0.5)
        self.quad = Polygon(self.to_pic(np.array([[0, 0], [self.pw, 0], [self.pw, self.h], [0, self.h]], float)))

    def to_plate(self, a):
        U = (a[:, 0] - self.xmin) / (self.xmax - self.xmin); V = (a[:, 1] - self.ymin) / (self.ymax - self.ymin)
        p = np.column_stack([self.x0 + U * (self.x1 - self.x0), self.y0 + V * (self.y1 - self.y0), np.ones(len(a))]) @ self.Hinv.T
        return np.column_stack([p[:, 0] / p[:, 2] * self.pw, p[:, 1] / p[:, 2] * 1000])

    def to_pic(self, a):
        p = np.column_stack([a[:, 0] / self.pw, a[:, 1] / 1000, np.ones(len(a))]) @ self.H.T
        sx, sy = p[:, 0] / p[:, 2], p[:, 1] / p[:, 2]
        return np.column_stack([self.xmin + (sx - self.x0) / (self.x1 - self.x0) * (self.xmax - self.xmin),
                                self.ymin + (sy - self.y0) / (self.y1 - self.y0) * (self.ymax - self.ymin)])

    def scale(self):
        """Millimetres on the plate per drawing unit, horizontal and vertical, at the plate's centre."""
        c = self.to_pic(np.array([[self.pw / 2, self.h / 2]]))
        d = 0.1
        return (np.linalg.norm(self.to_plate(c + [[d, 0]]) - self.to_plate(c)) / d,
                np.linalg.norm(self.to_plate(c + [[0, d]]) - self.to_plate(c)) / d)

    def cuts(self, black):
        g = black.intersection(self.quad.buffer(0.05))
        g = xform(g, self.to_plate).intersection(self.region)
        return shapely.set_precision(valid(g), 0.01)

    def check(self, black):
        cuts = self.cuts(black)
        wood = self.plate.difference(cuts)
        cores = {w: opening(wood, w) for w in range(2, int(MIN_WOOD_MM) + 1)}
        core = cores[int(MIN_WOOD_MM)]
        safe = unary_union([p for p in polys(core) if p.intersects(self.edge)])
        islands = [p for p in polys(wood) if not p.intersects(self.edge) and p.area >= MIN_PIECE_MM2]
        loose = []
        for p in polys(core):
            if p.intersects(self.edge) or p.area < MIN_PIECE_MM2:
                continue
            held = None
            for w in range(int(MIN_WOOD_MM) - 1, 1, -1):
                comp = [q for q in polys(cores[w]) if q.intersects(p)]
                if comp and any(q.intersects(self.edge) for q in comp):
                    held = w
                    break
            loose.append((p, held))
        thin = [p for p in polys(wood.difference(core.buffer(0.3)))
                if max(p.bounds[2] - p.bounds[0], p.bounds[3] - p.bounds[1]) > 25 and p.area > 30]
        # specks: wood pockets between strokes that all but touch, held by a hairline (under 2 mm); the tool's 2 mm
        # raster reports them as islands and a laser would burn the hairline, so they are cut away
        specks = [p for p in polys(cores[2]) if not p.intersects(self.edge) and p.area < FILL_ISLAND_MM2
                  and not any(p.intersects(q) for q, _ in loose) and not any(p.intersects(q) for q in islands)]
        # pinches: a wedge of wood under PINCH_MM wide and under PINCH_MM2 between two cut shapes that all but touch; the
        # tool's 2 mm raster shows it as an island and a laser leaves a charred hair, so the two cuts are joined there
        cut_polys = polys(cuts)
        for p in polys(wood.difference(cores[PINCH_MM].buffer(0.3))):
            if p.area >= PINCH_MM2 or p.intersects(self.edge):
                continue
            extent = max(p.bounds[2] - p.bounds[0], p.bounds[3] - p.bounds[1])
            # between two cuts, or a spike of one cut's wood curling back on itself; the opening's own corner roundings are
            # a few mm across and stay
            if len([q for q in cut_polys if q.distance(p) < 0.5]) >= 2 or extent > 8:
                specks.append(p)
        return dict(cuts=cuts, wood=wood, core=core, safe=safe, islands=islands, loose=loose, thin=thin, specks=specks)

    def supports(self, chk):
        """Bridges (plate mm) that hold every island and loose piece from two sides, and islands to fill."""
        safe, bridges, fills = chk['safe'], [], []
        pieces = list(chk['loose'])
        for sp in chk['specks']:
            fills.append(sp.buffer(1.5))
        for isl in chk['islands']:
            if isl.area < FILL_ISLAND_MM2:
                fills.append(isl.buffer(0.5))
            elif not any(isl.intersects(p) for p, _ in pieces):
                pieces.append((isl, None))
        if safe.is_empty:
            return bridges, fills
        for p, _ in pieces:
            c = np.array(p.centroid.coords[0])
            ring = p.exterior
            n = max(12, int(ring.length / 4))
            cands = []
            for k in range(n):
                q = ring.interpolate(k / n, normalized=True)
                s = shapely.ops.nearest_points(q, safe)[1]
                ang = math.atan2(q.y - c[1], q.x - c[0])
                cands.append((q.distance(s), q, s, ang))
            cands.sort(key=lambda t: t[0])
            chosen = []
            for min_sep in (100, 60, 0):
                for d, q, s, ang in cands:
                    if len(chosen) >= 2:
                        break
                    if all(abs((ang - a + math.pi) % (2 * math.pi) - math.pi) >= math.radians(min_sep) and q.distance(q0) > 40
                           for _, q0, _, a in chosen) or not chosen:
                        chosen.append((d, q, s, ang))
                if len(chosen) >= 2:
                    break
            for d, q, s, ang in chosen:
                v = np.array([s.x - q.x, s.y - q.y])
                if np.linalg.norm(v) < 1e-6:
                    v = np.array([q.x - c[0], q.y - c[1]])
                v = v / (np.linalg.norm(v) or 1)
                a, b = np.array([q.x, q.y]) - v * OVERSHOOT_MM, np.array([s.x, s.y]) + v * OVERSHOOT_MM
                bridges.append(LineString([a, b]).buffer(BRIDGE_MM / 2, cap_style='flat'))
        return bridges, fills


def load_projection(path, shrink_bottom=None, shrink_top=None):
    proj = json.load(open(path))
    insets = dict(proj.get('insets') or {'l': 0, 'r': 0, 't': 0, 'b': 0})
    if shrink_bottom is not None:
        insets['b'] = shrink_bottom
    if shrink_top is not None:
        insets['t'] = shrink_top
    return proj, insets


def run_check(black, proj, insets):
    plates = [Plate(f, proj, insets, black.bounds) for f in proj['faces']]
    return plates, {p.name: p.check(black) for p in plates}


def report(plates, checks, out):
    rows = []
    for p in plates:
        c = checks[p.name]
        sc = p.scale()
        out(f"{p.name}: {p.pw:.0f}x{p.h:.0f} mm, 1 drawing unit = {sc[0]:.0f}x{sc[1]:.0f} mm, {len(polys(c['cuts']))} cuts, "
            f"{len(c['islands'])} islands, {len(c['loose'])} loose pieces, {len(c['specks'])} specks, {len(c['thin'])} thin walls")
        for sp in c['specks']:
            pic = p.to_pic(np.array([sp.centroid.coords[0]]))[0]
            rows.append((p.name, 'SPECK', sp.area, sp.centroid.coords[0], pic, 1))
        for isl in c['islands']:
            pic = p.to_pic(np.array([isl.centroid.coords[0]]))[0]
            rows.append((p.name, 'ISLAND', isl.area, isl.centroid.coords[0], pic, None))
        for q, held in c['loose']:
            if any(q.intersects(i) for i in c['islands']):
                continue
            pic = p.to_pic(np.array([q.centroid.coords[0]]))[0]
            rows.append((p.name, 'LOOSE', q.area, q.centroid.coords[0], pic, held))
    rows.sort(key=lambda r: (r[5] is not None, r[5] or 0))
    for name, kind, a, cp, pic, held in rows:
        out(f"  {name:5s} {kind:6s} {a:6.0f} mm2  plate x={cp[0]:4.0f} y={cp[1]:4.0f}  drawing ({pic[0]:.2f},{pic[1]:.2f})  "
            f"held by {'nothing' if held is None else f'<= {held} mm'}")
    return rows


def write_dxf(black, path, units, bake=None):
    doc = ezdxf.new('R2010')
    doc.header['$INSUNITS'] = units
    doc.layers.add('CUT')
    msp = doc.modelspace()
    for p in polys(black):
        for ring in [p.exterior, *p.interiors]:
            pts = list(shapely.simplify(ring, FLAT).coords)[:-1]
            if len(pts) >= 3:
                msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'CUT'})
    if bake:
        doc.layers.add('BOX')
        sq = bake[-1]
        for x, y in bake[:-1]:
            msp.add_lwpolyline([(x, y), (x + sq, y), (x + sq, y + sq), (x, y + sq)], close=True, dxfattribs={'layer': 'BOX'})
    doc.saveas(path)


MIN_CUT_PIECE_MM2 = 10.0   # a cut piece smaller than this (a sliver the plate border clipped off a stroke) is not cut


def write_plate_dxf(plate, cuts, path):
    """One plate's cut file as the generator and the tool write them: R12, mm, layer OUTLINE the plate rectangle,
    layer CUT every closed contour (holes inside a cut region are separate closed contours on the same layer)."""
    doc = ezdxf.new('R12')                        # R12: every laser program reads it; no $INSUNITS in R12, the files are mm
    if '$INSUNITS' in doc.header: del doc.header['$INSUNITS']
    doc.layers.add('OUTLINE', color=7); doc.layers.add('CUT', color=1)
    msp = doc.modelspace()
    msp.add_polyline2d([(0, 0), (plate.pw, 0), (plate.pw, plate.h), (0, plate.h)], close=True, dxfattribs={'layer': 'OUTLINE'})
    n = 0
    for p in polys(cuts):
        for ring in [p.exterior, *p.interiors]:
            pts = [(round(x, 3), round(y, 3)) for x, y in shapely.simplify(ring, 0.05).coords[:-1]]
            if len(pts) >= 3:
                msp.add_polyline2d(pts, close=True, dxfattribs={'layer': 'CUT'}); n += 1
    doc.header['$EXTMIN'] = (0, 0, 0); doc.header['$EXTMAX'] = (plate.pw, plate.h, 0)
    doc.saveas(path)
    return n


def cut_files(plates, checks, out_dir, statue=1, drawing=''):
    """The per-plate cut files, their manifest and one picture of all the plates, as seen from the viewpoint."""
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    for p in plates:
        c = checks[p.name]
        cuts = unary_union([q for q in polys(c['cuts']) if q.area >= MIN_CUT_PIECE_MM2])
        dropped = len(polys(c['cuts'])) - len(polys(cuts))
        if c['specks']:
            cuts = valid(cuts.union(unary_union([sp.buffer(1.5) for sp in c['specks']])))
        wood = p.plate.difference(cuts)
        name = f"S{statue}-{p.name}.dxf"
        n = write_plate_dxf(p, cuts, os.path.join(out_dir, name))
        manifest.append(dict(file=name, statue=statue, tower=p.name.split('-')[0], face=p.name.split('-')[1], width_mm=p.pw, height_mm=p.h,
                             cuts=len(polys(cuts)), contours=n, cut_mm2=round(cuts.area), cut_fraction=round(cuts.area / p.plate.area, 3),
                             wood_pieces=len(polys(wood)), wood_islands=len(c['islands']), loose_pieces=len(c['loose']), specks_cut_away=len(c['specks']), slivers_dropped=dropped))
        c['cuts_final'] = cuts
    json.dump(dict(drawing=os.path.basename(drawing), units='mm', format='R12, layer OUTLINE = plate, layer CUT = holes, closed POLYLINE contours',
                   border_mm=plates[0].border, unlit_base_mm=plates[0].unlit, plates=manifest), open(os.path.join(out_dir, 'manifest.json'), 'w'), indent=1)
    # the picture: the outer faces in the order seen from behind (T7 on the left, C before D), feet on one line
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch; from matplotlib.path import Path
    def patch(g, **kw):
        verts, codes = [], []
        for q in polys(g):
            for ring in [q.exterior, *q.interiors]:
                cc = np.asarray(ring.coords); verts += list(cc); codes += [Path.MOVETO] + [Path.LINETO] * (len(cc) - 1)
        return PathPatch(Path(verts, codes), **kw) if verts else None
    order = sorted(plates, key=lambda p: (-int(p.name[1]), p.name[-1]))
    gap, x = 60.0, 0.0
    fig, ax = plt.subplots(figsize=(26, 9), dpi=110)
    for p in order:
        c = checks[p.name]
        ax.add_patch(patch(shapely.affinity.translate(p.plate, x, 0), facecolor='#e8d7b0', edgecolor='#5a4a30', lw=0.6))
        pc = patch(shapely.affinity.translate(c['cuts_final'], x, 0), facecolor='#111111', edgecolor='none')
        if pc: ax.add_patch(pc)
        ax.plot([x, x + p.pw], [p.unlit, p.unlit], color='#5a4a30', lw=0.4, ls=':')
        ax.text(x + p.pw / 2, -40, f"S{statue}-{p.name}\n{p.pw:.0f} x {p.h:.0f}", ha='center', va='top', fontsize=8)
        x += p.pw + gap
    ax.set_xlim(-gap, x); ax.set_ylim(-160, max(p.h for p in plates) + 40); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(f"the {len(plates)} outer faces of statue {statue} as seen from behind, cut from {os.path.basename(drawing)} (wood tan, cuts black, dotted = unlit base)", fontsize=10)
    fig.savefig(os.path.join(out_dir, 'plates.png'), bbox_inches='tight', facecolor='white'); plt.close(fig)
    return manifest


def render_drawing(black, path, bounds, extra=(), title=''):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch; from matplotlib.path import Path
    def patch(g, **kw):
        verts, codes = [], []
        for p in polys(g):
            for ring in [p.exterior, *p.interiors]:
                c = np.asarray(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 1)
        return PathPatch(Path(verts, codes), **kw) if verts else None
    xmin, ymin, xmax, ymax = bounds
    fig, ax = plt.subplots(figsize=(10, 10 * (ymax - ymin) / (xmax - xmin)), dpi=120)
    pb = patch(black, facecolor='black', edgecolor='none')
    if pb: ax.add_patch(pb)
    for g, col in extra:
        pg = patch(g, facecolor=col, edgecolor='none') if g is not None and not g.is_empty else None
        if pg: ax.add_patch(pg)
    ax.set_xlim(xmin - 0.3, xmax + 0.3); ax.set_ylim(ymin - 0.3, ymax + 0.3); ax.set_aspect('equal')
    ax.set_title(title, fontsize=9); ax.grid(True, alpha=0.25)
    fig.savefig(path, bbox_inches='tight', facecolor='white'); plt.close(fig)
    return patch


def render_check(black, rows, path, bounds, title):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    patch = render_drawing(black, path, bounds, title=title)
    fig, ax = plt.subplots(figsize=(10, 10 * (bounds[3] - bounds[1]) / (bounds[2] - bounds[0])), dpi=120)
    ax.add_patch(patch(black, facecolor='black', edgecolor='none'))
    seen, k = [], 0
    for name, kind, a, cp, pic, held in rows:
        if any(abs(pic[0] - s[0]) < 0.3 and abs(pic[1] - s[1]) < 0.3 for s in seen):
            continue
        seen.append(pic); k += 1
        col = 'red' if held is None else ('orange' if held <= 10 else 'gold')
        ax.add_patch(plt.Circle(pic, 0.5, fill=False, ec=col, lw=2.2))
        ax.text(pic[0] + 0.55, pic[1] + 0.35, str(k), color=col, fontsize=11, fontweight='bold')
    ax.set_xlim(bounds[0] - 0.3, bounds[2] + 0.3); ax.set_ylim(bounds[1] - 0.3, bounds[3] + 0.3); ax.set_aspect('equal')
    ax.set_title(title + '\nred = island, orange = held by <= 10 mm, yellow = held by 11-14 mm', fontsize=9); ax.grid(True, alpha=0.25)
    fig.savefig(path, bbox_inches='tight', facecolor='white'); plt.close(fig)


def render_support_sheet(black, added, removed, path, win=1.0):
    """Every support in the drawing, one close-up each (a 2*win square of drawing units), supports red, specks cut away blue."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch; from matplotlib.path import Path
    def patch(g, **kw):
        verts, codes = [], []
        for p in polys(g):
            for ring in [p.exterior, *p.interiors]:
                c = np.asarray(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 1)
        return PathPatch(Path(verts, codes), **kw) if verts else None
    groups = []
    for p in sorted(polys(added) + polys(removed), key=lambda p: -p.area):
        for k, g in enumerate(groups):
            if g.distance(p) < 0.3 * win:
                groups[k] = g.union(p); break
        else:
            groups.append(p)
    n = len(groups); cols = 6; rows = max(1, (n + cols - 1) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(3.0 * cols, 3.0 * rows), dpi=100); axes = np.atleast_1d(axes).ravel()
    for k, (ax, g) in enumerate(zip(axes, groups), 1):
        cx, cy = g.centroid.coords[0]; w = box(cx - win, cy - win, cx + win, cy + win)
        for geom, col in ((black, 'black'), (added, 'red'), (removed, '#3060ff')):
            pp = patch(geom.intersection(w), facecolor=col, edgecolor='none')
            if pp: ax.add_patch(pp)
        ax.set_xlim(cx - win, cx + win); ax.set_ylim(cy - win, cy + win); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f'#{k} ({cx:.1f}, {cy:.1f})', fontsize=8)
    for ax in axes[n:]: ax.axis('off')
    fig.suptitle(f'every support in the drawing ({n} spots), {2 * win:g} x {2 * win:g} drawing units each; red = wood added, blue = speck cut away', fontsize=10)
    fig.savefig(path, bbox_inches='tight', facecolor='white'); plt.close(fig)
    return n


def render_plates(plates, checks, path, supports_pic=None):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch; from matplotlib.path import Path
    def patch(g, **kw):
        verts, codes = [], []
        for p in polys(g):
            for ring in [p.exterior, *p.interiors]:
                c = np.asarray(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 1)
        return PathPatch(Path(verts, codes), **kw) if verts else None
    fig, axes = plt.subplots(1, len(plates), figsize=(1.6 * len(plates), 7), dpi=130)
    for ax, p in zip(axes, plates):
        c = checks[p.name]
        ax.add_patch(patch(p.plate, facecolor='#e8d7b0', edgecolor='k', lw=0.5))
        pc = patch(c['cuts'], facecolor='black', edgecolor='none')
        if pc: ax.add_patch(pc)
        if supports_pic is not None and not supports_pic.is_empty:
            sp = xform(supports_pic.intersection(p.quad.buffer(0.05)), p.to_plate).intersection(p.region)
            ps = patch(sp, facecolor='red', edgecolor='none')
            if ps: ax.add_patch(ps)
        for q in c['islands']: ax.add_patch(patch(q.buffer(10), facecolor='none', edgecolor='red', lw=1.5))
        for q, held in c['loose']: ax.add_patch(patch(q.buffer(8), facecolor='none', edgecolor='orange', lw=1.2))
        ax.set_xlim(-5, p.pw + 5); ax.set_ylim(-5, 2005); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(p.name, fontsize=8)
    fig.savefig(path, bbox_inches='tight', facecolor='white'); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('drawing')
    ap.add_argument('--projection', default=os.path.join(os.path.dirname(__file__), '..', 'art', 'eye', 'back1-projection.json'))
    ap.add_argument('--shrink-bottom', type=float, default=None, help="the tool's shrink-from-bottom inset, e.g. 0.13")
    ap.add_argument('--shrink-top', type=float, default=None, help="the tool's shrink-from-top inset, e.g. 0.2")
    ap.add_argument('--support', action='store_true', help='add bridges until nothing is loose, write <stem>-supported.dxf/.png')
    ap.add_argument('--bake', action='store_true', help='write the supported drawing so that it needs no bottom inset')
    ap.add_argument('--out', default=None, help='output directory (default: next to the drawing)')
    ap.add_argument('--stem', default=None, help="output file stem (default: the drawing's own name), e.g. EyeFinal-4mm for EyeFinal-4mm-supported.dxf")
    ap.add_argument('--rounds', type=int, default=4)
    ap.add_argument('--cut', default=None, metavar='DIR', help='write the per-plate cut files (R12 DXF, mm) and plates.png into DIR; the drawing is cut as given, with --shrink-bottom if any')
    a = ap.parse_args()
    out_dir = a.out or os.path.dirname(os.path.abspath(a.drawing)); os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, a.stem or os.path.splitext(os.path.basename(a.drawing))[0])
    black, units = read_drawing(a.drawing)
    bounds = black.bounds
    print(f"{a.drawing}: {len(polys(black))} cut shapes, units code {units}, box {bounds[2]-bounds[0]:.2f} x {bounds[3]-bounds[1]:.2f}")
    proj, insets = load_projection(a.projection, a.shrink_bottom, a.shrink_top)
    print('insets', insets)
    plates, checks = run_check(black, proj, insets)
    rows = report(plates, checks, print)
    tag = ''.join(f' (shrink {k} {insets[v]})' for k, v in (('bottom', 'b'), ('top', 't')) if insets[v])
    render_check(black, rows, stem + '-check.png', bounds, os.path.basename(a.drawing) + tag)
    render_plates(plates, checks, stem + '-plates.png')
    if a.cut:
        if [r for r in rows if r[1] != 'SPECK']:
            print(f'NOT CUTTABLE: {len(rows)} islands or loose pieces, fix the drawing first (--support)'); sys.exit(1)
        statue = int(proj['viewpoint'][-1]) if proj.get('viewpoint', '')[-1:].isdigit() else 1   # 'back2' -> statue 2
        man = cut_files(plates, checks, a.cut, statue=statue, drawing=a.drawing)
        for m in man:
            print(f"  {m['file']}: {m['width_mm']:.0f}x{m['height_mm']:.0f} mm, {m['cuts']} cuts ({m['cut_fraction']*100:.0f}% of the plate), {m['wood_pieces']} wood piece(s), {m['slivers_dropped']} slivers dropped")
        print('wrote', os.path.join(a.cut, 'manifest.json'), os.path.join(a.cut, 'plates.png'))
    if not a.support:
        return
    orig = black
    for rnd in range(1, a.rounds + 1):
        todo = [p for p in plates if checks[p.name]['islands'] or checks[p.name]['loose'] or checks[p.name]['specks']]
        if not todo:
            break
        print(f"--- support round {rnd}: {len(todo)} plates")
        for p in todo:
            chk = p.check(black)                      # re-check: earlier plates' bridges may already hold it
            bridges, fills = p.supports(chk)
            if not bridges and not fills:
                continue
            print(f"  {p.name}: {len(bridges)} bridges, {len(fills)} islands cut away")
            if bridges:
                black = valid(black.difference(xform(unary_union(bridges), p.to_pic)))
            if fills:
                black = valid(black.union(xform(unary_union(fills), p.to_pic)))
        plates, checks = run_check(black, proj, insets)
    rows = report(plates, checks, print)
    added = valid(orig.difference(black)); removed = valid(black.difference(orig))
    print(f"supports: {len(polys(added))} bridges added, {len(polys(removed))} islands cut away; {len(rows)} problems left")
    bake = None
    if a.bake and (insets['b'] or insets['t']):
        b, t = insets['b'], insets['t']; full = (bounds[3] - bounds[1]) / (1 - b - t)   # the whole box's height in drawing units
        y0, y1, sq = bounds[1] - full * b, bounds[3] + full * t, 0.05
        bake = [(x, y) for y in ([y0] if b else []) + ([y1 - sq] if t else []) for x in (bounds[0], bounds[2] - sq)] + [sq]
        print(f"baked: drawing box extended to y={y0:.3f}..{y1:.3f} by marker squares on layer BOX, load it with no insets")
    write_dxf(black, stem + '-supported.dxf', units, bake)
    render_drawing(black, stem + '-supported.png', bounds, extra=[(added, 'red'), (removed, '#3060ff')],
                   title=f"{os.path.basename(a.drawing)}{tag}: red = wood support added, blue = speck cut away")
    render_plates(plates, checks, stem + '-supported-plates.png', supports_pic=added)
    n = render_support_sheet(black, added, removed, stem + '-supports-sheet.png')
    print(f'{n} support spots; wrote', stem + '-supported.dxf', stem + '-supported.png', stem + '-supported-plates.png', stem + '-supports-sheet.png')


if __name__ == '__main__':
    main()
