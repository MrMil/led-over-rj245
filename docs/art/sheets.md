# Sheet packing: the 56 plates on 2440 × 1220 plywood

Path: [docs](../README.md) › [art](README.md) › **sheets**
Parent: [README.md](README.md)
**Covers:** how many 2440 × 1220 mm sheets of 4 mm plywood the 56 tower plates need and where each
plate sits, as computed by `tools/sheet_packing.py` into `art/sheets/sheet-packing.png` and
`sheet-packing.json`.
**Code:** `tools/sheet_packing.py` (reads `layout/statue-layout.json` for the plate sizes).

## What it does

The plates are two 400 mm and two 408 mm pieces per tower, as tall as the tower
([../strips_and_power/statue_geometry/final_layout.md](../strips_and_power/statue_geometry/final_layout.md#the-box-two-short-and-two-long-pieces-owner-2026-10-23)):
16 each of 1100, 1400 and 1700 mm tall, 8 of 2000 mm, half of each 400 and half 408 wide; 33.6 m²
of plate on 2.98 m² sheets, so 12 sheets is the area bound. The script enumerates every guillotine
sheet layout (bands across the full width along the sheet's length, each band three columns of
plates stacked along the length, or one plate turned sideways) and an integer program picks the
fewest sheets that cover the plate counts, spare plates as the tie-break. It writes a picture of
every sheet with the plate names (`S1-T4-C` …) and a JSON with each plate's position.

## Results (2026-10-28, the 4 mm layout)

| Cuts | Turned 1100 plates allowed | Sheets | Wood used |
|---|---|---|---|
| laser, no kerf | yes | **14** | 80.7 % |
| laser, no kerf | no | 16 | 70.6 % (not needed: plywood has no grain direction to keep) |
| saw, 3 mm kerf | yes | 15 | 75.3 % |
| saw, 3 mm kerf | no | 18 | 62.7 % |

The 14-sheet plan is the one in `art/sheets/`. No plan reaches the area bound because the sheet
width takes only three plates (3 × 400 = 1200; two 408s and one 400 = 1216, three 408s do not fit)
and the sheet length pairs badly with the heights: 1400 + 1100 is 2500, so the only two-high column
is 1100 + 1100, and under a 1400 or 1700 column only a turned 1100 plate fits.

## Decisions

- **Turned 1100 plates are allowed, and the 14-sheet plan is the plan** (owner, 2026-10-28: "it's
  plywood, the grain direction changes from sheet to sheet", so a plate's orientation on the sheet
  does not matter). The 1100 plates are the only ones shorter than the sheet width; turning 12 of
  the 16 saves two sheets. `--no-rotate` remains for a material with a grain.
- **Kerf is 0 by default** because the plates are laser cut ([eye_final.md](eye_final.md)); `--kerf 3`
  is the plan for a table saw. With any kerf the 400 + 408 + 408 band no longer fits across the
  width, which is where the saw plans lose their sheets.
- **Guillotine bands only** (agent, 2026-10-28): every layout the script considers can be cut with
  straight through-cuts, which is how a sheet is broken down on a saw or a laser bed smaller than
  the sheet. A free (non-guillotine) layout was not searched; the hand estimate above says it could
  not reach 13 anyway, since the waste under the 1400 and 1700 columns cannot be filled by anything
  but a turned 1100.
- **The plan assigns real plate names** so a sheet can be cut and labelled in one go; the names are
  the cut files' (`art/eye/cut/`, `art/praying/cut/`) and, for the bench faces A and B, the faces
  that still await the artist's drawings.

## Running it

```bash
.venv/bin/python tools/sheet_packing.py
```

```bash
.venv/bin/python tools/sheet_packing.py --no-rotate
```

```bash
.venv/bin/python tools/sheet_packing.py --kerf 3 --out /tmp/saw
```

## Related

- [eye_final.md](eye_final.md) — the cut files the plates are cut with.
- [../strips_and_power/tower_layout.md](../strips_and_power/tower_layout.md) — the box and its plate sizes.
