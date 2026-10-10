#!/usr/bin/env python3
"""Run by gen_vst.py after the skin is built (vst.json "skin_post"): `skin_post.py <skin dir>`.
The panel's knobs use the 'side' knob layout (picture + a value box). The panel already prints every
name, and the value box is only 2 px wide, so drop it: nothing stray can draw next to a knob."""
import glob, json, os, sys

def bounds_of(c):
    b = c.get("bounds")
    if isinstance(b, dict):
        b = b.get("bounds")
    try:
        return [float(v) for v in str(b).split()]
    except ValueError:
        return None

removed = 0
for path in glob.glob(os.path.join(sys.argv[1], "**", "TUI.json"), recursive=True):
    d = json.load(open(path))
    page = d.get("pageData", {}).get("componentDefinitions", {})
    for ld in page.get("localComponentDefinitions", []):
        if not str(ld.get("key", "")).startswith("shKnobSide"):
            continue
        kids = ld["value"].get("componentsData", [])
        keep = []
        for c in kids:
            b = bounds_of(c)
            if b and len(b) == 4 and b[0] > 0 and b[2] <= 4:     # the 2 px wide value label to the right of the picture
                removed += 1
                continue
            keep.append(c)
        ld["value"]["componentsData"] = keep
    json.dump(d, open(path, "w"), indent=2)
print("skin_post: removed %d value label(s) from side knobs" % removed)
