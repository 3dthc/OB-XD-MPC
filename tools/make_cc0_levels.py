#!/usr/bin/env python3
"""Evens out the loudness of the converted CC0 patches (they came out anywhere from very quiet to clipping next to the Moby bank).
Converts, plays every patch as a six-note chord in the offline engine (tools/level_audit.sh) and writes tools/cc0_levels.json: a
Volume per patch that brings its level to TARGET without peaking above PEAK_MAX. It repeats a few times because the engine is not
exactly linear. convert_obxf_patches.py applies the file.

usage: make_cc0_levels.py <OB-Xf checkout>
"""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET, PEAK_MAX = 0.09, 0.7          # a six-note chord: level (rms) to aim for, and the highest peak allowed (1.0 clips)
FILES = {"CC0 Keys": "010 - CC0 Keys.fxb", "CC0 Bass+Lead": "011 - CC0 Bass+Lead.fxb", "CC0 Pads+FX": "012 - CC0 Pads+FX.fxb"}
LV = os.path.join(HERE, "cc0_levels.json")
src = sys.argv[1]
if os.path.exists(LV):
    os.remove(LV)
for it in range(4):
    tmp = tempfile.mkdtemp()
    subprocess.check_call([sys.executable, os.path.join(HERE, "convert_obxf_patches.py"), src, os.path.join(tmp, "banks")],
                          stdout=subprocess.DEVNULL)
    rows = [l.split("|") for l in subprocess.check_output([os.path.join(HERE, "level_audit.sh"), tmp]).decode().splitlines()]
    out = {}
    worst = 0.0
    for bank, num, name, vol, rms, peak, cpu in rows:
        vol, rms, peak = float(vol), float(rms), float(peak)
        k = min(TARGET / max(rms, 1e-4), PEAK_MAX / max(peak, 1e-4))
        worst = max(worst, peak)
        out.setdefault(FILES[bank], []).append(round(min(1.0, max(0.02, vol * k)), 4))
    json.dump(out, open(LV, "w"), indent=0)
    print("pass %d: highest peak before this pass %.3f" % (it + 1, worst))
