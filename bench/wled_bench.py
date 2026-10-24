#!/usr/bin/env python3
"""Write the bench WLED setup (docs/firmware/output_driver.md, Bench test) as files, and
optionally a LittleFS image of them to flash over USB.

The 14 outputs have the real towers' LED counts and pins, and ledmap.json lays them out as
the rolled 2D map of docs/firmware/README.md: one column per tower, S1-T1 ... S1-T7 then
S2-T1 ... S2-T7, LED 0 at the bottom, shorter towers bottom-aligned (all strips start 150 mm
above the base), empty cells above them.

    python3 bench/wled_bench.py              # bench/wled-*.json
    python3 bench/wled_bench.py --image X    # also a LittleFS image, for
    esptool write-flash 0x310000 X           # WLED's filesystem partition (4 MB board)
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from wiring_diagrams import GPIO, TOWER_H  # noqa: E402

BASE_MM = 150    # dark base below each strip
LEDS_PER_M = 60
FS_SIZE = 0xF0000  # spiffs partition in WLED's tools/WLED_ESP32_4MB_1MB_FS.csv

towers = [(name, GPIO[name], (TOWER_H[name.split("-")[1]] - BASE_MM) * LEDS_PER_M // 1000)
          for name in GPIO]


def cfg():
    ins, start = [], 0
    for _, pin, n in towers:
        # maxpwr 0: WLED's limiter counts 1 mA standby for every configured LED, which leaves
        # nothing for the one strip on the bench.
        ins.append({"start": start, "len": n, "pin": [pin], "order": 0, "rev": False, "skip": 0,
                    "type": 22, "ref": False, "rgbwm": 0, "freq": 0, "drv": 0, "maxpwr": 0})
        start += n
    return {"hw": {"led": {"maxpwr": 0, "ins": ins}},
            "light": {"aseg": False},
            "def": {"ps": 0, "on": True, "bri": 255}}  # owner: 100%; one strip on full white draws ~3.6 A


def ledmap():
    height = max(n for *_, n in towers)
    starts, s = [], 0
    for *_, n in towers:
        starts.append(s)
        s += n
    cells = []
    for y in range(height):  # WLED's row 0 is the top
        h = height - 1 - y  # height above the bottom LED
        cells += [starts[x] + h if h < n else -1 for x, (*_, n) in enumerate(towers)]
    return {"n": "towers", "width": len(towers), "height": height, "map": cells}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--image", help="also write a LittleFS image here")
    args = ap.parse_args()
    files = {"cfg.json": cfg(), "presets.json": {"0": {}}, "ledmap.json": ledmap()}
    for name, data in files.items():
        (HERE / f"wled-{name}").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    if args.image:
        mk = Path.home() / ".platformio/packages/tool-mklittlefs/mklittlefs"
        with tempfile.TemporaryDirectory() as d:
            for name, data in files.items():
                (Path(d) / name).write_text(json.dumps(data, separators=(",", ":")))
            subprocess.run([str(mk), "-c", d, "-b", "4096", "-p", "256", "-s", str(FS_SIZE),
                            args.image], check=True, stdout=subprocess.DEVNULL)
    print(", ".join(f"{t}={n}" for t, _, n in towers), f"| {sum(n for *_, n in towers)} LEDs")


if __name__ == "__main__":
    main()
