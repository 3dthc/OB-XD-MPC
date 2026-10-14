#!/usr/bin/env python3
"""Preview of the panel pages: each tab's background plus the knob / button / selector pictures at their layout positions.
usage: mock_render.py out_prefix [theme]   (run from the repo root after make_skin.py; writes out_prefix-osc.png, out_prefix-filter.png, ...; theme = 0..3, default 0)
Knobs are shown at frame 40, every 3rd button lit; the text widgets are stand-ins."""
import re, sys, os
from PIL import Image, ImageDraw, ImageFont
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vst")
Y_OFF = 86
THEME = int(sys.argv[2]) if len(sys.argv) > 2 else 0
LOADER = os.environ.get('MOCK_LOADER', '')      # 'bank' / 'preset' / 'open': preview the file loader's states
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
            w_ = dr.textlength(kv(l, "label"), font=f2)
            x_ = int(kv(l, "cx")) - (0 if kv(l, "align") == "left" else w_ / 2)
            dr.text((x_, int(kv(l, "cy")) - Y_OFF - 8), kv(l, "label"), font=f2, fill=col)
            continue
        if t == "list":
            if kv(l, "when") and kv(l, "when") != "theme:%d" % THEME and False: pass                                      # the BROWSE tiles, with sample names; the 6th one lit
            x0, y0, w0 = int(kv(l, "x")), int(kv(l, "y")) - Y_OFF, int(kv(l, "w"))
            cols_, rows_, th_, gap_ = int(kv(l, "cols")), int(kv(l, "rows")), int(kv(l, "th")), int(kv(l, "gap"))
            tw_ = (w0 - (cols_ - 1) * gap_) // cols_
            off, on = img(kv(l, "img")), img(kv(l, "img_on"))
            names = (["Moby Pixel", "CC0 Keys", "CC0 Bass+Lead", "CC0 Pads+FX"] if kv(l, "key") == "bk" else
                     ["Acoustic Pia..", "An Ocean Swift", "CP Seventy", "E. Piano 2", "Everything", "Harpkies", "Harpsi", "Harpsichord",
                      "It's an OB-X!", "J60 Neon Main", "J60 Neon PW 1", "MelloWow", "OB Piano", "OBX Clavinet", "Smoothful", "Subtle",
                      "Sweet Spot", "Twindlin'", "J60 PWM Pluck", "J60 Saw Pluck", "Pizzi", "Simple Saw P..", "Glockenspiel", "Tubular Bells"])
            lit_i = 1 if kv(l, "key") == "bk" else 3
            if LOADER in ("bank", "preset"):
                ext = ".fxb" if LOADER == "bank" else ".fxp"
                names = (["PLUGIN", "INTERNAL", "USB / SD", "ALL FILES"] if kv(l, "key") == "bk" else
                         ["^ UP", "> Banks", "> Downloads", "> Old Projects", "Vintage Pads" + ext, "Friends Bank" + ext, "Bright Leads" + ext, "Warm Basses" + ext])
                lit_i = 1 if kv(l, "key") == "bk" else -1
            for i in range(cols_ * rows_):
                if kv(l, "order") == "cols":
                    k_ = (i % cols_) * rows_ + i // cols_
                else:
                    k_ = i
                x_, y_ = x0 + (i % cols_) * (tw_ + gap_), y0 + (i // cols_) * (th_ + gap_)
                t_ = (on if k_ == lit_i else off).resize((tw_, th_))
                bg.alpha_composite(t_, (x_, y_))
                if k_ < len(names) and f:
                    ts = int(kv(l, "tsize", "22")); tf = ImageFont.truetype(B, ts)
                    dr.text((x_ + int(kv(l, "tx", "12")), y_ + (th_ - ts) // 2 - 3), names[k_], font=tf, fill=col)
            continue
        if t == "popup" and f2:                               # the THEME drop-down: caption above, field with an arrow
            cx_, cy_, w_, h_ = int(kv(l, "cx")), int(kv(l, "cy")) - Y_OFF, int(kv(l, "w")), int(kv(l, "h"))
            if kv(l, "field") != "none":
                dr.rounded_rectangle([cx_ - w_ // 2, cy_ - h_ // 2, cx_ + w_ // 2, cy_ + h_ // 2], 6, fill=(18, 22, 30), outline=(110, 125, 150), width=2)
            dr.text((cx_ - w_ // 2 + 14, cy_ - 11), (("PATCHES" if LOADER in ("", "open") else ("BANK (.FXB)" if LOADER == "bank" else "PRESET (.FXP)")) if kv(l, "key") == "load_mode" else ["Slate", "MPC Grey", "MPC Black", "Retro"][THEME]), font=f3, fill=(235, 240, 250))
            if LOADER == "open" and kv(l, "key") == "load_mode":
                n_, rh_ = 3, 40
                ph_ = n_ * rh_ + 12
                py_ = cy_ - h_ // 2 - 4 - ph_
                dr.rounded_rectangle([cx_ - w_ // 2, py_, cx_ + w_ // 2, py_ + ph_], 6, fill=(14, 18, 26), outline=(110, 125, 150), width=2)
                for i_, o_ in enumerate(["PATCHES", "BANK (.FXB)", "PRESET (.FXP)"]):
                    y_ = py_ + 6 + i_ * rh_
                    if i_ == 0:
                        dr.rounded_rectangle([cx_ - w_ // 2 + 6, y_, cx_ + w_ // 2 - 6, y_ + rh_ - 4], 4, fill=(40, 64, 92))
                    dr.text((cx_ - w_ // 2 + 20, y_ + 8), o_, font=f3, fill=(235, 240, 250))
            if kv(l, "field") != "none":
                dr.polygon([(cx_ + w_ // 2 - 34, cy_ - 5), (cx_ + w_ // 2 - 16, cy_ - 5), (cx_ + w_ // 2 - 25, cy_ + 7)], fill=(235, 240, 250))
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
                dr.text((cx - int(kv(l, "w")) // 2 + 6, cy - 13), "CC0 Keys" if k == "bank_name" else "E. Piano 2", font=f, fill=col)
            if k in ("br_bank", "br_patch"):
                txt = ("CC0 Keys" if k == "br_bank" else "E. Piano 2") if not LOADER or LOADER == "open" else (
                    ("LOAD BANK" if LOADER == "bank" else "LOAD PRESET") if k == "br_bank" else "/sdcard/Downloads")
                dr.text((cx - int(kv(l, "w")) // 2 + 6, cy - 13), txt, font=f, fill=col)
            if k in ("br_bank_cap", "br_patch_cap"):
                if LOADER in ("bank", "preset"):
                    ct = "TAP A FILE TO ADD IT" if k == "br_bank_cap" else "FOLDER"
                else:
                    ct = "PLAYING BANK" if k == "br_bank_cap" else "PLAYING PATCH"
                dr.text((cx - int(kv(l, "w")) // 2 + 8, cy - 8), ct, font=f2, fill=col)
            if k in ("ui_cap_theme", "ui_cap_page"):
                tt = "THEME" if k == "ui_cap_theme" else "PAGE"
                ff = ImageFont.truetype(B, int(kv(l, "tsize", "20")))
                dr.text((cx - int(kv(l, "w")) // 2 if kv(l, "talign") == "left" else cx - dr.textlength(tt, font=ff) / 2, cy - int(kv(l, "tsize", "20")) // 2 - 2), tt, font=ff, fill=col)
            if k in ("br_bank_title", "br_patch_title"):
                tt = ("BANKS" if k == "br_bank_title" else "PATCHES") if LOADER in ("", "open") else (
                    "PLACES" if k == "br_bank_title" else ("BANK FILES (.FXB)" if LOADER == "bank" else "PRESET FILES (.FXP)"))
                dr.text((cx - dr.textlength(tt, font=f3) / 2, cy - 11), tt, font=f3, fill=col)
            if k == "pt_page":
                dr.text((cx - 36, cy - 14), "1 / 2", font=f3, fill=col)
            if k == "bank":
                dr.text((cx - 4, cy - 10), "2", font=f3, fill=col)
            if k == "tempo_text":
                dr.text((cx - 38, cy - 17), "120.0", font=f4, fill=col)
            if k == "patch":
                dr.text((cx - 12, cy - 10), "4", font=f3, fill=col)
    out = sys.argv[1]
    base, ext = os.path.splitext(out)
    bg.convert("RGB").save("%s-%s%s" % (base, name.lower(), ext or ".png"))
