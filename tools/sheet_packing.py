#!/usr/bin/env python3
"""Pack the 56 tower plates onto plywood sheets with the fewest sheets (docs/art/sheets.md).

The plates come from the layout file: per tower two short plates (400 wide) and two long ones
(400 + 2 x thickness), each as tall as its tower. A sheet is L x W (2440 x 1220 by default) and
is cut guillotine-style: bands across the full width along the length, each band either three
columns of plates stacked along the length or one plate turned sideways (only a plate shorter
than the sheet width can turn; plywood has no grain direction to keep, owner 2026-10-28).
Every band type and every combination of bands that fits a sheet is enumerated, and an integer
program picks the multiset of sheet patterns that covers the plate counts with the fewest sheets
(ties broken by the fewest spare plates).

  --kerf MM     material lost per cut (0 for a laser; 3 to 4 for a saw); it widens every plate
  --no-rotate   no sideways plates (for a material with a grain)
  --sheet L W   sheet size, mm

Writes <out>/sheet-packing.json (the plan, plate by plate) and <out>/sheet-packing.png.
Runs in the project's .venv (python3 -m venv .venv; .venv/bin/pip install -r requirements.txt).
"""
import argparse, itertools, json, os, sys
from collections import Counter

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds


def plates_from_layout(path):
    """Every plate as (statue, tower, face, height_mm, width_mm), from the handoff file."""
    d = json.load(open(path))
    out = []
    for s in d['layout']['statues']:
        for t in s['towers']:
            for face, w in sorted(t['plate_widths_mm'].items()):
                out.append((s['statue'], t['name'], face, int(t['height_mm']), int(w)))
    return out


def enumerate_patterns(sizes, L, W, kerf, rotate):
    """Sheet patterns: each a (bands, counter) where counter maps (h, w) to the plates it holds."""
    eff = lambda h, w: (h + kerf, w + kerf)
    heights = sorted({h for h, w in sizes}); widths = sorted({w for h, w in sizes})
    # stacks: multisets of plates one above the other in a column, total effective height <= L
    stacks = []
    for n in range(1, 4):
        for combo in itertools.combinations_with_replacement(sorted(sizes), n):
            if sum(eff(h, w)[0] for h, w in combo) <= L:
                stacks.append(tuple(combo))
    # bands of columns: up to 3 stacks across the width
    bands = {}
    for n in range(1, 4):
        for combo in itertools.combinations_with_replacement(range(len(stacks)), n):
            cols = [stacks[i] for i in combo]
            if sum(max(eff(h, w)[1] for h, w in st) for st in cols) > W:
                continue
            length = max(sum(eff(h, w)[0] for h, w in st) for st in cols)
            key = ('U', tuple(sorted(cols)))
            bands[key] = (length, Counter(p for st in cols for p in st), cols)
    if rotate:
        for h, w in sizes:
            if eff(h, w)[0] <= W:                     # the plate's height runs across the sheet
                bands[('R', ((h, w),))] = (eff(h, w)[1], Counter([(h, w)]), [((h, w),)])
    # drop a band dominated by another with the same length and a superset of plates
    keys = list(bands)
    # sheet patterns: multisets of bands with total length <= L
    blist = sorted(keys, key=lambda k: -bands[k][0])
    patterns = {}
    def rec(start, used, chosen):
        if chosen:
            cnt = Counter()
            for k in chosen: cnt += bands[k][1]
            key = tuple(sorted(cnt.items()))
            if key not in patterns or len(chosen) < len(patterns[key]):
                patterns[key] = list(chosen)
        for i in range(start, len(blist)):
            k = blist[i]; l = bands[k][0]
            if used + l <= L:
                chosen.append(k); rec(i, used + l, chosen); chosen.pop()
    rec(0, 0, [])
    return [(v, Counter(dict(k))) for k, v in patterns.items()], bands


def solve(demand, patterns):
    sizes = sorted(demand)
    n = len(patterns)
    A = np.array([[cnt.get(s, 0) for _, cnt in patterns] for s in sizes], dtype=float)
    # objective: sheets first (weight far above any plate count), then spare plates
    c = 1000.0 + A.sum(axis=0)
    res = milp(c, constraints=LinearConstraint(A, lb=[demand[s] for s in sizes], ub=np.inf),
               integrality=np.ones(n), bounds=Bounds(0, np.inf))
    if not res.success:
        sys.exit('no packing found: ' + res.message)
    x = np.round(res.x).astype(int)
    return [(patterns[i], x[i]) for i in range(n) if x[i] > 0]


def lay_out(plan, bands, plates, L, W, kerf):
    """Assign real plates to the slots and compute positions: a list of sheets, each a list of placed plates."""
    pool = {}
    for p in plates:
        pool.setdefault((p[3], p[4]), []).append(p)
    for v in pool.values():
        v.sort()
    sheets = []
    for (band_keys, _), count in plan:
        for _ in range(int(count)):
            y = 0; placed = []
            for k in band_keys:
                length, _, cols = bands[k]
                if k[0] == 'R':
                    (h, w), = cols[0]
                    p = pool[(h, w)].pop() if pool[(h, w)] else None
                    placed.append(dict(x=0, y=y, w=h, h=w, rotated=True, plate=p, size=(h, w)))
                    y += w + kerf
                else:
                    x = 0
                    for st in cols:
                        cw = max(w for h, w in st); yy = y
                        for h, w in st:
                            p = pool[(h, w)].pop() if pool[(h, w)] else None
                            placed.append(dict(x=x, y=yy, w=w, h=h, rotated=False, plate=p, size=(h, w)))
                            yy += h + kerf
                        x += cw + kerf
                    y += length
            sheets.append(placed)
    return sheets


def draw(sheets, L, W, path, title):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    n = len(sheets); cols = min(n, 6); rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.6, rows * 5.0), dpi=110, squeeze=False)
    for i, ax in enumerate(axes.flat):
        ax.axis('off')
        if i >= n: continue
        ax.set_xlim(-30, W + 30); ax.set_ylim(-30, L + 30); ax.set_aspect('equal')
        ax.add_patch(Rectangle((0, 0), W, L, facecolor='#f1e6cf', edgecolor='#5a4a30', lw=1))
        for q in sheets[i]:
            col = '#c9b48a' if q['plate'] else '#e0d0d0'
            ax.add_patch(Rectangle((q['x'], q['y']), q['w'], q['h'], facecolor=col, edgecolor='#2a1a0e', lw=0.8))
            label = f"S{q['plate'][0]}-{q['plate'][1]}-{q['plate'][2]}" if q['plate'] else 'spare'
            size = f"{q['size'][1]}x{q['size'][0]}" + (' turned' if q['rotated'] else '')
            ax.text(q['x'] + q['w'] / 2, q['y'] + q['h'] / 2, f"{label}\n{size}", ha='center', va='center', fontsize=6.5, rotation=0 if q['rotated'] else 90)
        used = sum(q['size'][0] * q['size'][1] for q in sheets[i] if q['plate'])
        ax.set_title(f"sheet {i + 1}: {used / (L * W) * 100:.0f} % used", fontsize=9)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout(); fig.savefig(path, bbox_inches='tight', facecolor='white'); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--layout', default=os.path.join(os.path.dirname(__file__), '..', 'layout', 'statue-layout.json'))
    ap.add_argument('--sheet', nargs=2, type=int, default=[2440, 1220], metavar=('L', 'W'), help='sheet length and width, mm')
    ap.add_argument('--kerf', type=float, default=0.0, help='mm lost per cut; added to every plate')
    ap.add_argument('--no-rotate', action='store_true', help='no plate turned sideways (for a material with a grain)')
    ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', 'art', 'sheets'))
    a = ap.parse_args()
    L, W = a.sheet
    plates = plates_from_layout(a.layout)
    demand = Counter((p[3], p[4]) for p in plates)
    sizes = sorted(demand)
    area = sum(h * w for (h, w), n in demand.items() for _ in range(n))
    print(f"{len(plates)} plates, {area / 1e6:.2f} m2; sheet {L} x {W} = {L * W / 1e6:.3f} m2; area bound {area / (L * W):.2f} sheets")
    for (h, w), n in sorted(demand.items()):
        print(f"  {n:2d} x {w} wide x {h} tall")
    patterns, bands = enumerate_patterns(sizes, L, W, a.kerf, not a.no_rotate)
    print(f"{len(bands)} band types, {len(patterns)} sheet patterns")
    plan = solve(demand, patterns)
    total = int(sum(c for _, c in plan))
    spare = int(sum(sum(cnt.values()) * c for (_, cnt), c in plan)) - len(plates)
    print(f"\n{total} sheets, {spare} spare plates, {area / (total * L * W) * 100:.1f} % of the wood used")
    sheets = lay_out(plan, bands, plates, L, W, a.kerf)
    os.makedirs(a.out, exist_ok=True)
    out = []
    for i, s in enumerate(sheets, 1):
        desc = ', '.join(f"{q['size'][1]}x{q['size'][0]}" + ('T' if q['rotated'] else '') for q in s)
        print(f"  sheet {i}: {desc}")
        out.append(dict(sheet=i, plates=[dict(id=(f"S{q['plate'][0]}-{q['plate'][1]}-{q['plate'][2]}" if q['plate'] else None), width_mm=q['size'][1], height_mm=q['size'][0],
                                              x_mm=int(q['x']), y_mm=int(q['y']), turned=bool(q['rotated'])) for q in s]))
    json.dump(dict(sheet_mm=[L, W], kerf_mm=a.kerf, rotate=not a.no_rotate, sheets_used=total, spare_plates=spare,
                   note='x across the sheet width, y along its length; a turned plate has its height across the sheet', sheets=out),
              open(os.path.join(a.out, 'sheet-packing.json'), 'w'), indent=1)
    draw(sheets, L, W, os.path.join(a.out, 'sheet-packing.png'), f"{len(plates)} plates on {total} sheets of {L} x {W} mm (kerf {a.kerf:g} mm)")
    print('wrote', os.path.join(a.out, 'sheet-packing.json'), os.path.join(a.out, 'sheet-packing.png'))


if __name__ == '__main__':
    main()
