#!/usr/bin/env python3
"""Preview of the main page: panel.png plus the knob / button / selector pictures at their layout positions.
usage: mock_render.py out.png   (run from the repo root after make_skin.py). Knobs are shown at frame 40, every 3rd toggle lit."""
import re, sys, os
from PIL import Image, ImageDraw, ImageFont
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vst")
src = open(os.path.join(H, "layout.conf")).read().split("[tab MORE]")[0]
bg = Image.open(os.path.join(H, "images/panel.png")).convert("RGBA")
Y_OFF = 86
def kv(l, k, d=None):
    m = re.search(r'(?:^| )%s=("[^"]*"|\S+)' % k, l)
    return m.group(1).strip('"') if m else d
def img(p): return Image.open(os.path.join(H, p)).convert("RGBA")
lit = 0
dr = ImageDraw.Draw(bg)
try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17); f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
except Exception: f = f2 = None
for l in src.splitlines():
    t = l.split(" ")[0]
    if t == "text" and f2:
        dr.text((int(kv(l, "cx")) - 14, int(kv(l, "cy")) - Y_OFF - 7), kv(l, "label"), font=f2, fill=(255, 255, 255)); continue
    if t not in ("knob", "toggle", "button", "slider_h", "readout"): continue
    cx, cy = int(kv(l, "cx")), int(kv(l, "cy")) - Y_OFF
    if t == "knob":
        s = img(kv(l, "strip")); F = s.width; fr = s.crop((0, 40 * F, F, 41 * F)); bg.alpha_composite(fr, (cx - F // 2, cy - F // 2))
    elif t in ("toggle", "button"):
        lit += 1; p = kv(l, "img_on") if (lit % 3 == 0) else kv(l, "img"); i = img(p); bg.alpha_composite(i, (cx - i.width // 2, cy - i.height // 2))
    elif t == "slider_h":
        s = img(kv(l, "strip")); n = int(kv(l, "frames", "8")); h = s.height // n; fr = s.crop((0, h, s.width, 2 * h)); bg.alpha_composite(fr, (cx - fr.width // 2, cy - h // 2))
    elif t == "readout" and f:
        k = kv(l, "key")
        if k == "bank_name": dr.text((cx - int(kv(l, "w")) // 2 + 6, cy - 11), "Mellow Poly", font=f, fill=(252, 36, 40))
        if k == "bank": dr.text((cx - 14, cy - 7), "6", font=f2, fill=(160, 36, 40))
        if k == "patch_name": dr.text((cx - int(kv(l, "w")) // 2 + 6, cy - 11), "Mellow Poly", font=f, fill=(252, 36, 40))
        if k == "tempo_text": dr.text((cx + 50 - 62, cy - 11), "120.0", font=f, fill=(252, 36, 40))
        if k == "patch": dr.text((cx - 14, cy - 7), "17", font=f2, fill=(160, 36, 40))
bg.convert("RGB").save(sys.argv[1])
