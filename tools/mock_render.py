#!/usr/bin/env python3
"""Preview of the panel pages: each tab's background plus the knob / button / selector pictures at their layout positions.
usage: mock_render.py out_prefix [theme]   (run from the repo root after make_skin.py; writes out_prefix-osc.png, out_prefix-filter.png, ...; theme = 0..3, default 0)
Knobs are shown at frame 40, every 3rd button lit; the text widgets are stand-ins."""
import re, sys, os
from PIL import Image, ImageDraw, ImageFont
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vst")
Y_OFF = 86
THEME = int(sys.argv[2]) if len(sys.argv) > 2 else 0
conf = open(os.path.join(H, "layout.conf")).read()
tabs = re.split(r"^\[tab (.+)\]$", conf, flags=re.M)[1:]       # name, body, name, body, ...


def kv(l, k, d=None):
    m = re.search(r'(?:^| )%s=("[^"]*"|\S+)' % k, l)
    return m.group(1).strip('"') if m else d


def img(p):
    return Image.open(os.path.join(H, p)).convert("RGBA")


try:
    B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f = ImageFont.truetype(B, 26)          # patch / bank names
    f2 = ImageFont.truetype(B, 13)         # captions
    f3 = ImageFont.truetype(B, 17)         # numbers
    f4 = ImageFont.truetype(B, 27)         # tempo
except Exception:
    f = f2 = f3 = f4 = None

for name, src in zip(tabs[0::2], tabs[1::2]):
    art = kv(next(l for l in src.splitlines() if l.startswith("art ")), "file")
    pic = [l for l in src.splitlines() if l.startswith("picture ")]
    if pic:
        art = kv(pic[0], "files").split(",")[THEME]
    bg = img(art)
    dr = ImageDraw.Draw(bg)
    lit = 0
    for l in src.splitlines():
        t = l.split(" ")[0]
        wh = kv(l, "when")
        if wh and wh.startswith("theme:") and int(wh.split(":")[1]) != THEME:
            continue
        col = tuple(int(kv(l, "tcolor", kv(l, "color", "ffffff"))[i:i + 2], 16) for i in (0, 2, 4))
        if t == "text" and f2:
            w_ = dr.textlength(kv(l, "label"), font=f2); dr.text((int(kv(l, "cx")) - w_ / 2, int(kv(l, "cy")) - Y_OFF - 8), kv(l, "label"), font=f2, fill=col)
            continue
        if t not in ("knob", "toggle", "button", "slider_h", "readout"):
            continue
        cx, cy = int(kv(l, "cx")), int(kv(l, "cy")) - Y_OFF
        if t == "knob":
            s = img(kv(l, "strip")); F = s.width; fr = s.crop((0, 40 * F, F, 41 * F))
            if kv(l, "bw"):
                s_ = 2 * int(kv(l, "r")) + 10
                cx -= (int(kv(l, "bw")) - s_) // 2
            bg.alpha_composite(fr, (cx - F // 2, cy - F // 2))
            if kv(l, "ink_dim") and f4:                     # the live value under the knob (MORE page)
                vs = int(kv(l, "vs", "22")); vf = ImageFont.truetype(B, vs)
                txt = "440" if kv(l, "key") == "master_hz" else "0.0"
                vc = tuple(int(kv(l, "ink_dim")[i:i + 2], 16) for i in (0, 2, 4))
                dr.text((cx - dr.textlength(txt, font=vf) / 2, cy + int(kv(l, "r")) + 6 + int(vs * 0.6) - vs // 2 - 2), txt, font=vf, fill=vc)
        elif t in ("toggle", "button"):
            lit += 1
            i = img(kv(l, "img_on") if (lit % 3 == 0) else kv(l, "img"))
            bg.alpha_composite(i, (cx - i.width // 2, cy - i.height // 2))
        elif t == "slider_h":
            s = img(kv(l, "strip")); n = int(kv(l, "frames", "8")); h = s.height // n
            fr = s.crop((0, h, s.width, 2 * h)); bg.alpha_composite(fr, (cx - fr.width // 2, cy - h // 2))
        elif t == "readout" and f:
            k = kv(l, "key")
            if k in ("bank_name", "patch_name"):
                dr.text((cx - int(kv(l, "w")) // 2 + 6, cy - 13), "Mellow Poly", font=f, fill=col)
            if k == "bank":
                dr.text((cx - 4, cy - 10), "6", font=f3, fill=col)
            if k == "tempo_text":
                dr.text((cx - 38, cy - 17), "120.0", font=f4, fill=col)
            if k == "patch":
                dr.text((cx - 12, cy - 10), "17", font=f3, fill=col)
    out = sys.argv[1]
    base, ext = os.path.splitext(out)
    bg.convert("RGB").save("%s-%s%s" % (base, name.lower(), ext or ".png"))
