#!/usr/bin/env python3
"""The controller's WLED files, and the LittleFS image that puts them on the ESP32 over USB.

Writes wled/cfg.json (the 14 outputs with the real pins and LED counts, the rolled 2D map, the
access point, the show as boot preset) and wled/ledmap.json; wled/presets.json is the owner's
playlist and is not touched. With --image it also builds a LittleFS image of the three files
for WLED's filesystem partition, with the AP password from the WLED_AP_PASS environment
variable: the password goes only into the image, never into the repository.
Why: docs/firmware/controller_files.md.

    python3 tools/wled_image.py                        # wled/cfg.json, wled/ledmap.json
    WLED_AP_PASS=... python3 tools/wled_image.py --image out.bin
    esptool write_flash 0x310000 out.bin               # WLED's filesystem partition, 4 MB board
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from wiring_diagrams import GPIO, TOWER_H  # noqa: E402

BASE_MM = 150        # dark base below each strip
LEDS_PER_M = 60
MA_PER_LED = 118     # 4 × the measured 29.4 mA at full white: WLED sees one face per output, the tower has four
AP_SSID = "Layers-WLED"
AP_CHANNEL = 6
AP_ALWAYS = 2        # AP_BEHAVIOR_ALWAYS
BOOT_PRESET = 18     # the show playlist in wled/presets.json
FS_OFFSET = 0x310000  # spiffs partition in WLED's tools/WLED_ESP32_4MB_1MB_FS.csv
FS_SIZE = 0xF0000

towers = [(name, GPIO[name], (TOWER_H[name.split("-")[1]] - BASE_MM) * LEDS_PER_M // 1000)
          for name in GPIO]


def cfg(ap_pass=None):
    ins, start = [], 0
    for _, pin, n in towers:
        ins.append({"start": start, "len": n, "pin": [pin], "order": 0, "rev": False, "skip": 0,
                    "type": 22, "ref": False, "rgbwm": 0, "freq": 0, "drv": 0,
                    "ledma": MA_PER_LED, "maxpwr": 0})
        start += n
    ap = {"ssid": AP_SSID, "chan": AP_CHANNEL, "hide": 0, "behav": AP_ALWAYS}
    if ap_pass:
        ap["psk"] = ap_pass
    return {"ap": ap,
            # maxpwr 0: WLED's limiter off. No supply reaches its ceiling even at full white
            # (docs/strips_and_power/led_power_budget.md), and the limiter is per output, not per supply.
            "hw": {"led": {"maxpwr": 0, "ins": ins}},
            "light": {"aseg": False},
            "def": {"ps": BOOT_PRESET, "on": True, "bri": 255}}


def ledmap():
    height = max(n for *_, n in towers)
    starts, s = [], 0
    for *_, n in towers:
        starts.append(s)
        s += n
    cells = []
    for y in range(height):  # WLED's row 0 is the top
        h = height - 1 - y    # height above the bottom LED
        cells += [starts[x] + h if h < n else -1 for x, (*_, n) in enumerate(towers)]
    return {"n": "towers", "width": len(towers), "height": height, "map": cells}


def dump(data):
    return json.dumps(data, separators=(",", ":")) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--image", help="also write a LittleFS image here (needs WLED_AP_PASS)")
    args = ap.parse_args()
    out = ROOT / "wled"
    (out / "cfg.json").write_text(dump(cfg()))
    (out / "ledmap.json").write_text(dump(ledmap()))
    presets = out / "presets.json"
    if args.image:
        ap_pass = os.environ.get("WLED_AP_PASS")
        if not ap_pass:
            sys.exit("set WLED_AP_PASS to the access-point password (it goes only into the image)")
        mk = Path.home() / ".platformio/packages/tool-mklittlefs/mklittlefs"
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "cfg.json").write_text(dump(cfg(ap_pass)))
            (Path(d) / "ledmap.json").write_text(dump(ledmap()))
            (Path(d) / "presets.json").write_text(presets.read_text())
            subprocess.run([str(mk), "-c", d, "-b", "4096", "-p", "256", "-s", str(FS_SIZE),
                            args.image], check=True, stdout=subprocess.DEVNULL)
        print(f"image {args.image}: cfg.json, ledmap.json, presets.json for 0x{FS_OFFSET:X}")
    print(", ".join(f"{t}={n}" for t, _, n in towers), f"| {sum(n for *_, n in towers)} LEDs, boot preset {BOOT_PRESET}")


if __name__ == "__main__":
    main()
