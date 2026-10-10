"""Draws the OB-Xd main page's background (plate, section frames, labels, icons, the BANK / PATCH and BPM displays) and says where every
control goes. Used by make_skin.py. All coordinates are plugin-area pixels (1280 x 628).

The layout keeps the community skin's sections and order (MASTER, GLOBAL, OSCILLATORS, MIXER, CONTROL, FILTER, MODULATION, the two
ENVELOPES, VOICE VARIATION) but is laid out for the MPC screen: every knob is the same big size and every button the same size,
and the rows use the whole height of the screen.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 628
WOOD = 28                                    # the wooden cheeks at the sides stay as the theme draws them
HDR = 28                                     # section header: rule, title, rule
KF = 68                                      # knob picture (frame incl. shadow); the visible knob is ~4 px less
KROW, KROW2, TROW = 90, 102, 70              # row heights: knobs (one / two label lines), buttons only
BLUE = (50, 146, 252)
INK = (228, 230, 238)
DARK = (14, 15, 19)
FONT_LABEL = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
FONT_TITLE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _plate(bg, base):
    """The panel's plate: its colour with soft clouds like the theme's, over the whole width between the wooden cheeks."""
    rng = np.random.default_rng(7)

    def field(gw, gh, amp):
        g = rng.normal(0, 1, (gh, gw)).astype("float32")
        return np.asarray(Image.fromarray(g, mode="F").resize((W, H), Image.BICUBIC)) * amp

    n = field(13, 7, 3.2) + field(52, 26, 1.7) + field(210, 105, 0.8) + rng.normal(0, 0.6, (H, W))
    arr = np.clip(np.asarray(base, dtype="float32")[None, None, :] + n[:, :, None], 0, 255).astype("uint8")
    plate = Image.fromarray(arr, "RGB").convert("RGBA")
    bg.paste(plate.crop((WOOD, 0, W - WOOD, H)), (WOOD, 0))


def _text(d, cx, cy, s, font, fill=INK, track=0.5):
    """s centred on (cx, cy), letter-spaced; cy is the middle of the capitals."""
    ws = [font.getlength(c) for c in s]
    x = cx - (sum(ws) + track * (len(s) - 1)) / 2.0
    base = cy + round(font.size * 0.37)
    for c, w in zip(s, ws):
        d.text((x, base), c, font=font, fill=fill, anchor="ls")
        x += w + track


def _label(d, cx, cy, s, font):
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        _text(d, cx, cy + 12 * i, ln, font)


def _section(d, x0, x1, y, title, tfont):
    for yy in (y, y + 26):
        d.rectangle([x0, yy, x1, yy + 1], fill=BLUE)
    _text(d, (x0 + x1) / 2.0, y + 14, title, tfont, track=0.8)


def _divider(d, x, y0, y1):
    d.rectangle([x, y0, x + 1, y1], fill=DARK)
    d.rectangle([x + 2, y0, x + 2, y1], fill=(78, 80, 100))


def _icon(bg, kind, cx, cy):
    """Waveform icons (saw, pulse, sine, square, sample and hold), drawn 4x and scaled down."""
    k, w, h = 4, 22, 11
    pts = {
        "saw": [(0, 1), (0.5, 0), (0.5, 1), (1, 0)],
        "pulse": [(0, 1), (0.18, 1), (0.18, 0), (0.7, 0), (0.7, 1), (1, 1)],
        "square": [(0, 1), (0, 0), (0.5, 0), (0.5, 1), (1, 1), (1, 0)],
        "sine": [(t / 24.0, 0.5 - 0.5 * math.sin(2 * math.pi * t / 24.0)) for t in range(25)],
        "sh": [(0, 0.6), (0.2, 0.6), (0.2, 0.05), (0.4, 0.05), (0.4, 0.95), (0.6, 0.95), (0.6, 0.4), (0.8, 0.4), (0.8, 1), (1, 1)],
    }[kind]
    m = 3
    layer = Image.new("RGBA", ((w + 2 * m) * k, (h + 2 * m) * k), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    xy = [((m + x * w) * k, (m + y * h) * k) for x, y in pts]
    ld.line(xy, fill=INK + (255,), width=int(2.2 * k), joint="curve")
    layer = layer.resize((w + 2 * m, h + 2 * m), Image.LANCZOS)
    bg.alpha_composite(layer, (int(cx - (w + 2 * m) / 2), int(cy - (h + 2 * m) / 2)))


def draw(bg, base_rgb, logo, sel_groups, sel_dw, sel_bw, sel_gap, sel_y0, sel_h, tempo_box):
    """Paints the background into bg (RGBA, plugin-area size). Returns the list of control placements:
    dicts with kind (knob | toggle | legato | voices | vam | stop), key, cx, cy."""
    _plate(bg, base_rgb)
    d = ImageDraw.Draw(bg)
    fl, ft = _font(FONT_LABEL, 12), _font(FONT_TITLE, 15)
    P = []

    def knob(key, cx, cy):
        P.append(dict(kind="knob", key=key, cx=cx, cy=cy))

    def tog(key, cx, cy):
        P.append(dict(kind="toggle", key=key, cx=cx, cy=cy))

    def krow(y, items, cxs):
        """items: (kind, key, label) per column; knob / toggle centre at y+38, label at y+79 (two lines: +12)."""
        two = any("\n" in it[2] for it in items)
        for (kd, key, label), cx in zip(items, cxs):
            (knob if kd == "k" else tog)(key, cx, y + 38)
            _label(d, cx, y + 79 - (0 if not two else 0), label, fl)
        return y + (KROW2 if two else KROW)

    def trow(y, items, cxs):
        """buttons only: centre y+30, label (or icon) y+60"""
        for (key, label), cx in zip(items, cxs):
            tog(key, cx, y + 30)
            if label.startswith("@"):
                _icon(bg, label[1:], cx, y + 60)
            else:
                _label(d, cx, y + 60, label, fl)
        return y + TROW

    # ---- the top strip: logo, BANK / PATCH displays, BPM display
    bg.alpha_composite(logo, (160 - logo.width // 2, 5))
    d = ImageDraw.Draw(bg)
    for (x0, _k) in sel_groups:
        dx = x0 + sel_bw + sel_gap
        d.rounded_rectangle([dx, sel_y0, dx + sel_dw, sel_y0 + sel_h], radius=4, fill=(0, 0, 0), outline=(46, 46, 46))
    tx0, ty0, tx1, ty1 = tempo_box
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=4, fill=(0, 0, 0), outline=(46, 46, 46))

    # ---- dividers
    TOP, BOT = 60, 622
    _divider(d, 289, TOP, BOT)
    _divider(d, 649, TOP, BOT)
    _divider(d, 921, TOP, BOT)

    # ---- left column (x 36..284)
    lc = 160
    heights = [HDR + KROW, HDR + KROW, 72, 94]
    gap = min(40, (BOT - 8 - 70 - sum(heights)) // 3)
    y = 70
    _section(d, 40, 282, y, "MASTER", ft)
    krow(y + HDR, [("k", "volume", "VOLUME"), ("k", "tune", "FINE"), ("k", "octave", "COARSE")], [lc - 75, lc, lc + 75])
    y += heights[0] + gap
    _section(d, 40, 282, y, "GLOBAL", ft)
    krow(y + HDR, [("k", "udet", "SPREAD"), ("t", "unison", "UNISON"), ("k", "portamento", "GLIDE")], [lc - 75, lc, lc + 75])
    y += heights[1] + gap
    P.append(dict(kind="legato", key="legatomode", cx=122, cy=y + 28))
    P.append(dict(kind="voices", key="voice_count", cx=248, cy=y + 28))
    _label(d, 122, y + 62, "LEGATO MODE", fl)
    _label(d, 248, y + 62, "VOICES", fl)
    y += heights[2] + gap
    P.append(dict(kind="vam", key="asplayedallocation", cx=122, cy=y + 42))
    P.append(dict(kind="stop", key="stop", cx=198, cy=y + 42))
    _label(d, 122, y + 86, "VAM", fl)
    _label(d, 198, y + 86, "STOP", fl)

    # ---- OSCILLATORS (x 295..541) and MIXER (556..643), CONTROL under both
    oc = 418
    ox = [oc - 82, oc, oc + 82]
    y = 60
    _section(d, 295, 541, y, "OSCILLATORS", ft)
    y += HDR
    y = krow(y, [("k", "osc1p", "OSC1"), ("k", "pw", "PW"), ("k", "osc2p", "OSC2")], ox) + 6
    y = trow(y, [("osc1saw", "@saw"), ("osc1pul", "@pulse"), ("osc2saw", "@saw"), ("osc2pul", "@pulse")],
             [322, 378, 458, 514]) + 6
    y = krow(y, [("t", "osc2hs", "SYNC"), ("k", "xmod", "XMOD"), ("t", "oscquantize", "STEP")], ox) + 6
    y = krow(y, [("k", "brightness", "BRIGHT\nAMT"), ("k", "osc2_det", "DETUNE"), ("k", "envpitch", "PITCH\nENV AMT")], ox)
    osc_end = y
    _divider(d, 548, TOP, osc_end + 2)
    _section(d, 556, 640, 60, "MIXER", ft)
    my = 60 + HDR
    for key, label in (("osc1mix", "OSC1"), ("osc2mix", "OSC2"), ("noisemix", "NOISE")):
        krow(my, [("k", key, label)], [600])
        my += 100
    cy0 = osc_end + 12
    _section(d, 295, 640, cy0, "CONTROL", ft)
    krow(cy0 + HDR, [("t", "bendrange", "BEND\nOCTAVE"), ("t", "bendosc2", "BEND\nOSC2"), ("k", "bendlforate", "VIBRATO\nRATE"),
                     ("k", "vfltenv", "FLT ENV\nVELOCITY"), ("k", "vampenv", "AMP ENV\nVELOCITY")],
         [330, 400, 470, 540, 610])

    # ---- FILTER and MODULATION (x 654..914)
    fc = 784
    fx = [fc - 79, fc, fc + 79]
    y = 60
    _section(d, 656, 912, y, "FILTER", ft)
    y = krow(y + HDR, [("k", "cutoff", "CUTOFF"), ("k", "resonance", "RESONANCE"), ("k", "envelope_amt", "ENV AMT")], fx)
    y = krow(y, [("t", "flt_kf", "KEY"), ("t", "filter_warm", "HQ"), ("k", "multimode", "MULTI"),
                 ("t", "bandpass", "BP"), ("t", "fourpole", "24dB")],
             [fc - 108, fc - 61, fc, fc + 61, fc + 108]) + 14
    _section(d, 656, 912, y, "MODULATION", ft)
    y = krow(y + HDR, [("k", "lfofreq", "LFO RATE"), ("k", "lfo1amt", "FREQ AMT"), ("k", "lfo2amt", "PW AMT")], fx)
    cols = [[("lfosinwave", "@sine"), ("lfosquarewave", "@square"), ("lfoshwave", "@sh")],
            [("lfoosc1", "OSC1"), ("lfoosc2", "OSC2"), ("lfofilter", "FILTER")],
            [("lfopw1", "OSC1"), ("lfopw2", "OSC2"), ("lfo_sync", "SYNC")]]
    for r in range(3):
        y = trow(y, [cols[c][r] for c in range(3)], fx)

    # ---- right column (x 930..1238): the two envelopes and VOICE VARIATION
    rc = 1084
    rx = [rc - 114, rc - 38, rc + 38, rc + 114]
    heights = [HDR + KROW, HDR + KROW, HDR + 3 * KROW]
    gap = (BOT - 60 - sum(heights)) // 2
    y = 60
    _section(d, 930, 1238, y, "FILTER ENVELOPE", ft)
    krow(y + HDR, [("k", "fatk", "ATTACK"), ("k", "fdec", "DECAY"), ("k", "fsus", "SUSTAIN"), ("k", "frel", "RELEASE")], rx)
    y += heights[0] + gap
    _section(d, 930, 1238, y, "AMPLIFIER ENVELOPE", ft)
    krow(y + HDR, [("k", "latk", "ATTACK"), ("k", "ldec", "DECAY"), ("k", "lsus", "SUSTAIN"), ("k", "lrel", "RELEASE")], rx)
    y += heights[1] + gap
    _section(d, 930, 1238, y, "VOICE VARIATION", ft)
    yy = krow(y + HDR, [("k", "filterder", "FLT SLOP"), ("k", "portader", "GLD SLOP"), ("k", "envder", "ENV SLOP")], rx[:3])
    yy = krow(yy, [("k", "pan%d" % i, "V%d PAN" % i) for i in range(1, 5)], rx)
    krow(yy, [("k", "pan%d" % i, "V%d PAN" % i) for i in range(5, 9)], rx)
    return P
