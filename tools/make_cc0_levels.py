#!/usr/bin/env python3
"""Evens out the loudness of the converted CC0 patches (they came out anywhere from very quiet to clipping next to the Moby bank).
Converts, plays every patch as a six-note chord in the offline engine (tools/level_audit.sh) and writes tools/cc0_levels.json: a
Volume per patch that brings its level to TARGET without peaking above PEAK_MAX. It repeats a few times because the engine is not
exactly linear. convert_obxf_patches.py applies the file.

usage: make_cc0_levels.py <OB-Xf checkout>
"""
import json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET, PEAK_MAX = 0.09, 0.7          # a six-note chord: level (rms) to aim for, and the highest peak allowed (1.0 clips)
FILES = {n: "%s - %s.fxb" % (k, n) for k, n in (("010", "Keys"), ("011", "Bass+Lead"), ("012", "Pads+FX"), ("013", "Keys 2"), ("014", "Bass+Lead 2"), ("015", "Pads+FX 2"))}
LV = os.path.join(HERE, "cc0_levels.json")
src = sys.argv[1]
KEEP = {}
if os.path.exists(LV):
    KEEP = {k: v for k, v in json.load(open(LV)).items() if k in ("010 - Keys.fxb", "011 - Bass+Lead.fxb", "012 - Pads+FX.fxb")}
    os.remove(LV)
for it in range(4):
    tmp = tempfile.mkdtemp()
    subprocess.check_call([sys.executable, os.path.join(HERE, "convert_obxf_patches.py"), src, os.path.join(tmp, "banks")],
                          stdout=subprocess.DEVNULL)
    shutil.copy(os.path.join(HERE, "..", "banks", "000 - Moby Pixel.fxb"), os.path.join(tmp, "banks"))   # bank 0, as installed
    rows = [l.split("|") for l in subprocess.check_output(["bash", os.path.join(HERE, "level_audit.sh"), tmp, "7"]).decode().splitlines()]
    out = {}
    worst = 0.0
    for bank, num, name, vol, rms, peak, cpu in rows:
        if bank not in FILES:
            continue
        vol, rms, peak = float(vol), float(rms), float(peak)
        k = min(TARGET / max(rms, 1e-4), PEAK_MAX / max(peak, 1e-4))
        worst = max(worst, peak)
        out.setdefault(FILES[bank], []).append(round(min(1.0, max(0.02, vol * k)), 4))
    out.update(KEEP)                         # patches already in users' hands keep the Volume they shipped with
    json.dump(out, open(LV, "w"), indent=0)
    print("pass %d: highest peak before this pass %.3f" % (it + 1, worst))
