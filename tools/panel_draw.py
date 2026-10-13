"""Draws the OB-Xd pages' backgrounds (plate, section frames, labels, icons, the BANK / PATCH and BPM displays) and says where every
control goes. Used by make_skin.py. All coordinates are plugin-area pixels (1280 x 628).

The community skin's sections and their order are kept (MASTER, GLOBAL, OSCILLATORS, MIXER, CONTROL, FILTER, MODULATION, the two
ENVELOPES, VOICE VARIATION), but they are spread over two pages so everything can be big for a touchscreen:

  OSC     MASTER, GLOBAL (with LEGATO / VOICES and VAM / STOP), OSCILLATORS, MIXER, CONTROL, AMPLIFIER ENVELOPE
  FILTER  FILTER, FILTER ENVELOPE, MODULATION, VOICE VARIATION

Every knob is the same size and every button the same size on both pages (VAM and STOP are a little bigger). The logo, the BANK /
PATCH displays and the BPM display are on both pages.

THEMES are colour schemes for the whole panel (plate, labels, section lines, the display wells and their text), drawn by the same
code, so every page exists once per theme and the THEME option on the MORE page swaps them:
  Slate      the community skin's blue-grey slate, ice-blue displays
  MPC Grey   a light grey body with red accents and a green LCD (the classic grey MPC look)
  MPC Black  a matte black body with red accents and amber displays (the black MPCs)
  Retro      a cream body with orange accents and dark smoked displays (the Live II Retro Edition's classic feel)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 628
WOOD = 28                                    # the wooden cheeks at the sides stay as the theme draws them
HDR = 28                                     # section header: rule, title, rule
KF = 96                                      # knob picture (frame incl. shadow); the visible knob is ~4 px less
LAB = 16                                     # label size
LINE = 17                                    # line spacing of a two-line label
KROW = KF + 30                               # a row of knobs / buttons with one label line
KROW2 = KROW + LINE - 2                      # ... with two label lines
TOP, BOT = 74, 622                           # the dividers run from TOP to BOT
Y0, YMAX = 82, 618                           # the sections start at Y0 and the last row ends by YMAX
FONT_LABEL = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
FONT_TITLE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PAGES = ("osc", "filter")
THEMES = [
    dict(key="slate", name="Slate", base=None, noise=1.0, ink=(228, 230, 238), rule=(50, 146, 252), div_d=(14, 15, 19), div_l=(78, 80, 100),
         logo=(232, 234, 242), well=((12, 22, 44), 215, 26, (0, 0, 0)), disp="96cdff", dim="6994c8", cap="b4d2f0"),
    dict(key="grey", name="MPC Grey", base=(168, 170, 174), noise=0.55, ink=(34, 36, 42), rule=(198, 52, 40), div_d=(78, 80, 86), div_l=(214, 216, 220),
         logo=(40, 42, 50), well=((112, 134, 94), 246, 22, (30, 40, 24)), disp="1c2a14", dim="3c4e30", cap="2c3a22"),
    dict(key="black", name="MPC Black", base=(34, 35, 38), noise=0.8, ink=(234, 230, 220), rule=(214, 56, 44), div_d=(6, 6, 8), div_l=(76, 78, 84),
         logo=(236, 232, 222), well=((16, 11, 6), 225, 22, (0, 0, 0)), disp="ffb040", dim="b07832", cap="d9b27a"),
    dict(key="retro", name="Retro", base=(202, 194, 174), noise=0.55, ink=(54, 42, 32), rule=(226, 118, 34), div_d=(84, 70, 54), div_l=(232, 226, 210),
         logo=(58, 46, 36), well=((30, 25, 21), 232, 22, (0, 0, 0)), disp="ff9632", dim="b46e32", cap="e8cfa8"),
]
CUR = dict(THEMES[0])                          # the theme being drawn


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _plate(bg, base, amp=1.0):
    """The panel's plate: its colour with soft clouds like the theme's, over the whole width between the wooden cheeks."""
    rng = np.random.default_rng(7)

    def field(gw, gh, amp):
        g = rng.normal(0, 1, (gh, gw)).astype("float32")
        return np.asarray(Image.fromarray(g, mode="F").resize((W, H), Image.BICUBIC)) * amp

    n = (field(13, 7, 3.2) + field(52, 26, 1.7) + field(210, 105, 0.8) + rng.normal(0, 0.6, (H, W))) * amp
    arr = np.clip(np.asarray(base, dtype="float32")[None, None, :] + n[:, :, None], 0, 255).astype("uint8")
    plate = Image.fromarray(arr, "RGB").convert("RGBA")
    bg.paste(plate.crop((WOOD, 0, W - WOOD, H)), (WOOD, 0))


def _text(d, cx, cy, s, font, fill=None, track=0.5):
    """s centred on (cx, cy), letter-spaced; cy is the middle of the capitals."""
    fill = fill or CUR["ink"]
    ws = [font.getlength(c) for c in s]
    x = cx - (sum(ws) + track * (len(s) - 1)) / 2.0
    base = cy + round(font.size * 0.37)
    for c, w in zip(s, ws):
        d.text((x, base), c, font=font, fill=fill, anchor="ls")
        x += w + track


def _label(d, cx, cy, s, font):
    for i, ln in enumerate(s.split("\n")):
        _text(d, cx, cy + LINE * i, ln, font)


def _hline(bg, x0, x1, y, rgb, h=1, peak=255, fade=48):
    """A hairline that fades out towards both ends (a modern, quieter rule than a solid bar)."""
    n = x1 - x0 + 1
    t = np.arange(n, dtype="float32")
    a = np.clip(np.minimum(t, n - 1 - t) / float(fade), 0, 1) ** 0.8 * (peak / 255.0)
    for k in range(h):
        row = np.asarray(bg.crop((x0, y + k, x1 + 1, y + k + 1)).convert("RGB"), dtype="float32")
        c = np.asarray(rgb, dtype="float32")[None, None, :]
        out = row * (1 - a[None, :, None]) + c * a[None, :, None]
        bg.paste(Image.fromarray(out.astype("uint8"), "RGB").convert(bg.mode), (x0, y + k))


def _section(bg, d, x0, x1, y, title, tfont):
    rule = CUR["rule"]
    _hline(bg, x0, x1, y + 1, rule, h=2)
    _hline(bg, x0, x1, y + 3, CUR["div_l"] if CUR["key"] != "slate" else (120, 126, 150), h=1, peak=90)      # a soft highlight under it
    _hline(bg, x0, x1, y + 26, rule, h=1, peak=170)
    _text(d, (x0 + x1) / 2.0, y + 14, title, tfont, track=2.0)


def _sheen(bg):
    """A quiet finish over the plate: a lit top edge, a darker foot and corners (a soft vignette) and one faint diagonal highlight."""
    a = np.asarray(bg.convert("RGB"), dtype="float32")
    yy, xx = np.mgrid[0:H, 0:W].astype("float32")
    top = np.clip(1 - yy / (H * 0.40), 0, 1) ** 1.6 * 9
    foot = np.clip((yy - H * 0.62) / (H * 0.38), 0, 1) ** 1.3 * -8
    cx, cy = W / 2.0, H / 2.0
    r = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.78)) ** 2)
    vig = -np.clip(r - 0.55, 0, 1) ** 1.6 * 26
    dg = np.exp(-(((xx - W * 0.30) + (yy - H * 0.5) * 0.9) / 150.0) ** 2) * 4.5
    g = (top + foot + vig + dg)[:, :, None]
    out = np.clip(a + g, 0, 255).astype("uint8")
    keep = bg.convert("RGB").copy()
    res = Image.fromarray(out, "RGB")
    res.paste(keep.crop((0, 0, WOOD, H)), (0, 0))                  # the wooden cheeks stay as they were
    res.paste(keep.crop((W - WOOD, 0, W, H)), (W - WOOD, 0))
    bg.paste(res.convert(bg.mode), (0, 0))


def _divider(d, x, y0, y1):
    d.rectangle([x, y0, x + 1, y1], fill=CUR["div_d"])
    d.rectangle([x + 2, y0, x + 2, y1], fill=CUR["div_l"])


def _well(bg, x0, y0, x1, y1):
    """A display well drawn as tinted glass: the plate shows through, darkened by the theme's tint, with an inner shadow along the
    top, a faint gloss over the upper half and a light edge below."""
    from PIL import ImageFilter
    tint, alpha, gloss, rim = CUR["well"]
    w, h = x1 - x0, y1 - y0
    zero = Image.new("L", (w, h), 0)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=5, fill=255)
    layer = Image.new("RGBA", (w, h), tuple(tint) + (255,))
    bg.paste(layer, (x0, y0), m.point(lambda v: v * alpha // 255))
    sh = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sh).rectangle([0, 0, w, 4], fill=140)
    sh = sh.filter(ImageFilter.GaussianBlur(2))
    bg.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (x0, y0), Image.composite(sh, zero, m))
    gl = Image.new("L", (w, h), 0)
    ImageDraw.Draw(gl).rounded_rectangle([3, 6, w - 4, h // 2], radius=6, fill=gloss)
    gl = gl.filter(ImageFilter.GaussianBlur(5))
    bg.paste(Image.new("RGBA", (w, h), (255, 255, 255, 255)), (x0, y0), Image.composite(gl, zero, m))
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=5, outline=tuple(rim) + (210,))
    d.line([x0 + 4, y1, x1 - 5, y1], fill=(CUR["div_l"] if CUR["key"] != "slate" else (150, 160, 190)) + (110,))


def _icon(bg, kind, cx, cy):
    """Waveform icons (saw, pulse, sine, square, sample and hold), drawn 4x and scaled down."""
    k, w, h = 4, 28, 14
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
    ld.line(xy, fill=CUR["ink"] + (255,), width=int(2.6 * k), joint="curve")
    layer = layer.resize((w + 2 * m, h + 2 * m), Image.LANCZOS)
    bg.alpha_composite(layer, (int(cx - (w + 2 * m) / 2), int(cy - (h + 2 * m) / 2)))


def _flow(blocks, y0=Y0, ymax=YMAX):
    """Tops of the blocks of one column, [(kind, height)], kind 'sec' (a section header) or 'row'. The column's spare height is spread
    over the gaps (more between sections than between rows, none between a header and its first row), so the column ends at ymax."""
    base = {("sec", "row"): 0, ("row", "row"): 4, ("row", "sec"): 14, ("sec", "sec"): 14}
    wgt = {("sec", "row"): 0.3, ("row", "row"): 1.0, ("row", "sec"): 2.5, ("sec", "sec"): 2.5}
    pairs = list(zip(blocks, blocks[1:]))
    spare = ymax - y0 - sum(h for _, h in blocks) - sum(base[(a[0], b[0])] for a, b in pairs)
    if spare < 0:
        raise SystemExit("panel_draw: a column is %d px too tall" % -spare)
    tw = sum(wgt[(a[0], b[0])] for a, b in pairs) or 1.0
    ys, y = [], float(y0)
    for i, (k, h) in enumerate(blocks):
        ys.append(int(round(y)))
        if i < len(pairs):
            key = (k, blocks[i + 1][0])
            y += h + base[key] + min(spare * wgt[key] / tw, 60)
    return ys


def _columns(widths, x0=40, x1=1240):
    """Left edges of columns of the given widths spread over x0..x1, and the x of each gap's middle (for the dividers)."""
    gap = (x1 - x0 - sum(widths)) // (len(widths) - 1)
    xs, x = [], x0
    for w in widths:
        xs.append(x)
        x += w + gap
    return xs, [xs[i] + widths[i] + gap // 2 - 1 for i in range(len(widths) - 1)]


def draw(page, theme, bg, base_rgb, logo_mask, sel_groups, sel_dw, sel_bw, sel_gap, sel_y0, sel_h, tempo_box, dims):
    """Paints one page's background into bg (RGBA, plugin-area size). dims: sizes of the pictures the controls use
    (btn_h = a button picture's height, leg_w/leg_h = the LEGATO display, vox_w = the VOICES display, big_h = VAM / STOP's picture).
    Returns the list of control placements: dicts with kind (knob | toggle | legato | voices | vam | stop), key, cx, cy."""
    CUR.clear()
    CUR.update(THEMES[theme])
    _plate(bg, CUR["base"] or base_rgb, CUR["noise"])
    _sheen(bg)
    logo = Image.new("RGBA", logo_mask.size, tuple(CUR["logo"]) + (0,))
    logo.putalpha(logo_mask)
    d = ImageDraw.Draw(bg)
    fl, ft = _font(FONT_LABEL, LAB), _font(FONT_TITLE, 18)
    P = []
    BH = dims["btn_h"]
    TROW = BH + 26                                   # a row of buttons with a label (or icon) under each

    def knob(key, cx, cy):
        P.append(dict(kind="knob", key=key, cx=cx, cy=cy))

    def tog(key, cx, cy):
        P.append(dict(kind="toggle", key=key, cx=cx, cy=cy))

    def krow(y, items, cxs):
        """items: (kind, key, label) per column; the knob / button is centred at y+KF/2+2, its label under it. Returns the row's bottom."""
        two = any("\n" in it[2] for it in items)
        for (kd, key, label), cx in zip(items, cxs):
            (knob if kd == "k" else tog)(key, cx, y + KF // 2 + 2)
            _label(d, cx, y + KF + 11, label, fl)
        return y + (KROW2 if two else KROW)

    def trow(y, items, cxs):
        """buttons only: centre y+BH/2+2, label (or icon) under it"""
        for (key, label), cx in zip(items, cxs):
            tog(key, cx, y + BH // 2 + 2)
            if label.startswith("@"):
                _icon(bg, label[1:], cx, y + BH + 12)
            else:
                _label(d, cx, y + BH + 12, label, fl)
        return y + TROW

    # ---- the top strip: logo, BANK / PATCH displays, BPM display (on every page)
    bg.alpha_composite(logo, (160 - logo.width // 2, 8))
    d = ImageDraw.Draw(bg)
    for (x0, _k) in sel_groups:
        dx = x0 + sel_bw + sel_gap
        _well(bg, dx, sel_y0, dx + sel_dw, sel_y0 + sel_h)
    _well(bg, *tempo_box)
    d = ImageDraw.Draw(bg)

    def col(blocks):
        """blocks: (kind, height, draw(y)) -> the draw callbacks are called with their block's top"""
        ys = _flow([(k, h) for k, h, _ in blocks])
        for y, (_k, _h, fn) in zip(ys, blocks):
            fn(y)

    def sec(x0, x1, title):
        return ("sec", HDR, lambda y: _section(bg, d, x0, x1, y, title, ft))

    def kr(items, cxs):
        two = any("\n" in it[2] for it in items)
        return ("row", KROW2 if two else KROW, lambda y: krow(y, items, cxs))

    def tr(items, cxs):
        return ("row", TROW, lambda y: trow(y, items, cxs))

    if page == "osc":
        # ---- four columns: MASTER / GLOBAL | OSCILLATORS | MIXER | CONTROL / AMPLIFIER ENVELOPE
        cw = [312, 312, 112, 416]
        xs, divs = _columns(cw)
        for x in divs:
            _divider(d, x, TOP, BOT)
        sl = 104                                              # distance between knob centres
        # column 1
        x0, x1 = xs[0], xs[0] + cw[0]
        c = (x0 + x1) // 2
        leg_row = dims["leg_h"] + 30
        big_row = dims["big_h"] + 24
        lx, vx = x0 + 6 + dims["leg_w"] // 2, x1 - 6 - dims["vox_w"] // 2

        def legrow(y):
            ly = y + dims["leg_h"] // 2 + 2
            P.append(dict(kind="legato", key="legatomode", cx=lx, cy=ly))
            P.append(dict(kind="voices", key="voice_count", cx=vx, cy=ly))
            _label(d, lx, y + dims["leg_h"] + 16, "LEGATO MODE", fl)
            _label(d, vx, y + dims["leg_h"] + 16, "VOICES", fl)

        def bigrow(y):
            by = y + dims["big_h"] // 2 + 2
            P.append(dict(kind="vam", key="asplayedallocation", cx=c - 64, cy=by))
            P.append(dict(kind="stop", key="stop", cx=c + 64, cy=by))
            _label(d, c - 64, y + dims["big_h"] + 12, "VAM", fl)
            _label(d, c + 64, y + dims["big_h"] + 12, "STOP", fl)

        col([sec(x0, x1, "MASTER"),
             kr([("k", "volume", "VOLUME"), ("k", "tune", "FINE"), ("k", "octave", "COARSE")], [c - sl, c, c + sl]),
             sec(x0, x1, "GLOBAL"),
             kr([("k", "udet", "SPREAD"), ("t", "unison", "UNISON"), ("k", "portamento", "GLIDE")], [c - sl, c, c + sl]),
             ("row", leg_row, legrow), ("row", big_row, bigrow)])
        # column 2: OSCILLATORS
        x0, x1 = xs[1], xs[1] + cw[1]
        c = (x0 + x1) // 2
        ox = [c - sl, c, c + sl]
        col([sec(x0, x1, "OSCILLATORS"),
             kr([("k", "osc1p", "OSC1"), ("k", "pw", "PW"), ("k", "osc2p", "OSC2")], ox),
             tr([("osc1saw", "@saw"), ("osc1pul", "@pulse"), ("osc2saw", "@saw"), ("osc2pul", "@pulse")],
                [c - 120, c - 46, c + 46, c + 120]),
             kr([("t", "osc2hs", "SYNC"), ("k", "xmod", "XMOD"), ("t", "oscquantize", "STEP")], ox),
             kr([("k", "brightness", "BRIGHT\nAMT"), ("k", "osc2_det", "DETUNE"), ("k", "envpitch", "PITCH\nENV AMT")], ox)])
        # column 3: MIXER
        x0, x1 = xs[2], xs[2] + cw[2]
        c = (x0 + x1) // 2
        col([sec(x0, x1, "MIXER")] + [kr([("k", key, label)], [c]) for key, label in
                                       (("osc1mix", "OSC1"), ("osc2mix", "OSC2"), ("noisemix", "NOISE"))])
        # column 4: CONTROL, AMPLIFIER ENVELOPE
        x0, x1 = xs[3], xs[3] + cw[3]
        c = (x0 + x1) // 2
        col([sec(x0, x1, "CONTROL"),
             kr([("t", "bendrange", "BEND\nOCTAVE"), ("t", "bendosc2", "BEND\nOSC2"), ("k", "bendlforate", "VIBRATO\nRATE")],
                [c - sl, c, c + sl]),
             kr([("k", "vfltenv", "FLT ENV\nVELOCITY"), ("k", "vampenv", "AMP ENV\nVELOCITY")], [c - sl // 2, c + sl // 2]),
             sec(x0, x1, "AMPLIFIER ENVELOPE"),
             kr([("k", "latk", "ATTACK"), ("k", "ldec", "DECAY"), ("k", "lsus", "SUSTAIN"), ("k", "lrel", "RELEASE")],
                [c - 3 * sl // 2, c - sl // 2, c + sl // 2, c + 3 * sl // 2])])
    else:
        # ---- three columns: FILTER / FILTER ENVELOPE | MODULATION | VOICE VARIATION
        cw = [416, 312, 416]
        xs, divs = _columns(cw)
        for x in divs:
            _divider(d, x, TOP, BOT)
        sl = 104
        x0, x1 = xs[0], xs[0] + cw[0]
        c = (x0 + x1) // 2
        col([sec(x0, x1, "FILTER"),
             kr([("k", "cutoff", "CUTOFF"), ("k", "resonance", "RESONANCE"), ("k", "envelope_amt", "ENV AMT")], [c - sl, c, c + sl]),
             kr([("t", "flt_kf", "KEY"), ("t", "filter_warm", "HQ"), ("k", "multimode", "MULTI"), ("t", "bandpass", "BP"),
                 ("t", "fourpole", "24dB")], [c - 165, c - 91, c, c + 91, c + 165]),
             sec(x0, x1, "FILTER ENVELOPE"),
             kr([("k", "fatk", "ATTACK"), ("k", "fdec", "DECAY"), ("k", "fsus", "SUSTAIN"), ("k", "frel", "RELEASE")],
                [c - 3 * sl // 2, c - sl // 2, c + sl // 2, c + 3 * sl // 2])])
        # MODULATION
        x0, x1 = xs[1], xs[1] + cw[1]
        c = (x0 + x1) // 2
        fx = [c - sl, c, c + sl]
        cols = [[("lfosinwave", "@sine"), ("lfosquarewave", "@square"), ("lfoshwave", "@sh")],
                [("lfoosc1", "OSC1"), ("lfoosc2", "OSC2"), ("lfofilter", "FILTER")],
                [("lfopw1", "OSC1"), ("lfopw2", "OSC2"), ("lfo_sync", "SYNC")]]
        col([sec(x0, x1, "MODULATION"),
             kr([("k", "lfofreq", "LFO RATE"), ("k", "lfo1amt", "FREQ AMT"), ("k", "lfo2amt", "PW AMT")], fx)] +
            [tr([cols[cc][r] for cc in range(3)], fx) for r in range(3)])
        # VOICE VARIATION
        x0, x1 = xs[2], xs[2] + cw[2]
        c = (x0 + x1) // 2
        qx = [c - 3 * sl // 2, c - sl // 2, c + sl // 2, c + 3 * sl // 2]
        col([sec(x0, x1, "VOICE VARIATION"),
             kr([("k", "filterder", "FLT SLOP"), ("k", "portader", "GLD SLOP"), ("k", "envder", "ENV SLOP")], [c - sl, c, c + sl]),
             kr([("k", "pan%d" % i, "V%d PAN" % i) for i in range(1, 5)], qx),
             kr([("k", "pan%d" % i, "V%d PAN" % i) for i in range(5, 9)], qx)])
    return P
