#!/usr/bin/env python3
"""Evens out the loudness of tools/make_classics.py's patches (same method and targets as make_cc0_levels.py) and writes
tools/classics_levels.json, one Volume per patch in bank order.   usage: make_classics_levels.py"""
import json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET, PEAK_MAX = 0.09, 0.7
LV = os.path.join(HERE, "classics_levels.json")
if os.path.exists(LV):
    os.remove(LV)
for it in range(4):
    tmp = tempfile.mkdtemp()
    subprocess.check_call([sys.executable, os.path.join(HERE, "make_classics.py"), os.path.join(tmp, "banks")], stdout=subprocess.DEVNULL) \
        if os.makedirs(os.path.join(tmp, "banks")) is None else None
    shutil.copy(os.path.join(HERE, "..", "banks", "000 - Moby Pixel.fxb"), os.path.join(tmp, "banks"))
    # the audit plays banks 1..N by position: Moby is 1, Classics is 2
    rows = [l.split("|") for l in subprocess.check_output(["bash", os.path.join(HERE, "level_audit.sh"), tmp, "2"]).decode().splitlines()]
    out, worst = [], 0.0
    for bank, num, name, vol, rms, peak, cpu in rows:
        if bank != "Classics":
            continue
        vol, rms, peak = float(vol), float(rms), float(peak)
        worst = max(worst, peak)
        k = min(TARGET / max(rms, 1e-4), PEAK_MAX / max(peak, 1e-4))
        out.append(round(min(1.0, max(0.02, vol * k)), 4))
        if it == 3:
            print("%-18s vol %.3f rms %.4f peak %.3f cpu %s" % (name, vol, rms, peak, cpu.strip()))
    json.dump(out, open(LV, "w"))
    print("pass %d: highest peak %.3f" % (it + 1, worst))
    shutil.rmtree(tmp)
