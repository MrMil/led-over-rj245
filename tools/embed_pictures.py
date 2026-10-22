#!/usr/bin/env python3
"""Put the four viewpoint pictures (art/<viewpoint>.png) into the layout handoff file.

The layout tool carries the pictures inside layout/statue-layout.json (format version 3), so the artist's
file and the cut masks travel together. This writes the pictures as data URLs into that file and switches
statue 2 to its own pictures (it mirrors statue 1 by default). Everything else in the file is kept. Run
tools/face_art.py first; afterwards the tool's `?load=layout/statue-layout.json` shows the real cuts.
"""
import base64, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT = os.path.join(ROOT, 'layout', 'statue-layout.json')
NAMES = {'bench1': 'woman blessing', 'back1': 'open eye', 'bench2': 'bird with a third eye', 'back2': 'magic mushroom'}

doc = json.load(open(LAYOUT))
proj = doc['params'].setdefault('projection', {})
proj['statue2_mirrors_statue1'] = False
vps = {v['key']: v for v in proj.get('viewpoints', [])}
for key, name in NAMES.items():
    png = os.path.join(ROOT, 'art', key + '.png')
    if not os.path.exists(png): sys.exit(f'missing {png}: run tools/face_art.py first')
    src = 'data:image/png;base64,' + base64.b64encode(open(png, 'rb').read()).decode()
    v = vps.setdefault(key, {'key': key, 'fit': 'full', 'insets': {'l': 0, 'r': 0, 't': 0, 'b': 0}})
    if key.startswith('back'): v.setdefault('distance_mm', 3000); v.setdefault('eye_mm', 1600); v.setdefault('fov_deg', 100)
    v['picture'] = {'name': f'{key}: {name} (art/{key}.png)', 'type': 'raster', 'source': src}
proj['viewpoints'] = [vps[k] for k in ('bench1', 'bench2', 'back1', 'back2') if k in vps]
doc['format'] = doc.get('format', 'led-over-rj245/statue-layout'); doc['version'] = max(3, doc.get('version', 3))
json.dump(doc, open(LAYOUT, 'w'), indent=1)
print(f'wrote {os.path.relpath(LAYOUT, ROOT)}: {os.path.getsize(LAYOUT) // 1024} kB')
