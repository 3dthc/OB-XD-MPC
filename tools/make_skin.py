#!/usr/bin/env python3
"""Build the OB-Xd panel skin for the MPC from an OB-Xd theme folder.

  python3 tools/make_skin.py skin-source/"Default Skin" [--width 1280]      # the bundled community skin (CC BY-SA 3.0)
  python3 tools/make_skin.py "<...>/discoDSP/OB-Xd/Themes/discoDSP Classic"  # a theme from your own install (private use only)

Reads the theme's own artwork (main, knob, button, voices, legato; the @4x versions when the theme has
them) and coords.xml, scales it ONCE to the exact size the MPC will show (so nothing is resampled on
the device and text stays sharp), writes vst/layout.conf and vst/images/*, and points vst.json at them
("layout", "art": "html").
The artwork belongs to its authors. The bundled community skin (gitterdude, CC BY-SA 3.0) may be redistributed with credit;
anything built from a theme of your own install (e.g. discoDSP Classic) must stay on your computer.
"""
import argparse, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VST = os.path.join(ROOT, "vst")

AREA_W, AREA_H = 1280, 628     # MPC plugin area (the screen is 1280x800; the top bar and tabs take the rest)
Y_OFF = 86                     # layout y of the plugin area's top edge (layouts are 1280x800)
LZ = Image.LANCZOS

# coords.xml NAME -> (param key, kind). kind: knob | toggle | voices | legato
MAP = {
 "volumeKnob": ("volume", "knob"), "tuneKnob": ("tune", "knob"), "transposeKnob": ("octave", "knob"),
 "voiceDetuneKnob": ("udet", "knob"), "unisonButton": ("unison", "toggle"), "portamentoKnob": ("portamento", "knob"),
 "legatoSwitch": ("legatomode", "legato"), "voiceSwitch": ("voice_count", "voices"),
 "asPlayedAllocButton": ("asplayedallocation", "toggle"),
 "bendOsc2OnlyButton": ("bendosc2", "toggle"), "bendRangeButton": ("bendrange", "toggle"),
 "bendLfoRateKnob": ("bendlforate", "knob"), "veloFltEnvKnob": ("vfltenv", "knob"), "veloAmpEnvKnob": ("vampenv", "knob"),
 "osc1PitchKnob": ("osc1p", "knob"), "pulseWidthKnob": ("pw", "knob"), "osc2PitchKnob": ("osc2p", "knob"),
 "xmodKnob": ("xmod", "knob"), "osc2DetuneKnob": ("osc2_det", "knob"), "pitchQuantButton": ("oscquantize", "toggle"),
 "envPitchModKnob": ("envpitch", "knob"), "brightnessKnob": ("brightness", "knob"),
 "osc1MixKnob": ("osc1mix", "knob"), "osc2MixKnob": ("osc2mix", "knob"), "noiseMixKnob": ("noisemix", "knob"),
 "cutoffKnob": ("cutoff", "knob"), "resonanceKnob": ("resonance", "knob"), "filterEnvelopeAmtKnob": ("envelope_amt", "knob"),
 "multimodeKnob": ("multimode", "knob"), "filterKeyFollowButton": ("flt_kf", "toggle"),
 "filterBPBlendButton": ("bandpass", "toggle"), "fourPoleButton": ("fourpole", "toggle"), "filterHQButton": ("filter_warm", "toggle"),
 "attackKnob": ("latk", "knob"), "decayKnob": ("ldec", "knob"), "sustainKnob": ("lsus", "knob"), "releaseKnob": ("lrel", "knob"),
 "fattackKnob": ("fatk", "knob"), "fdecayKnob": ("fdec", "knob"), "fsustainKnob": ("fsus", "knob"), "freleaseKnob": ("frel", "knob"),
 "lfoFrequencyKnob": ("lfofreq", "knob"), "lfoAmt1Knob": ("lfo1amt", "knob"), "lfoAmt2Knob": ("lfo2amt", "knob"),
 "lfoSinButton": ("lfosinwave", "toggle"), "lfoSquareButton": ("lfosquarewave", "toggle"), "lfoSHButton": ("lfoshwave", "toggle"),
 "lfoOsc1Button": ("lfoosc1", "toggle"), "lfoOsc2Button": ("lfoosc2", "toggle"), "lfoFilterButton": ("lfofilter", "toggle"),
 "lfoPwm1Button": ("lfopw1", "toggle"), "lfoPwm2Button": ("lfopw2", "toggle"),
 "hardSyncButton": ("osc2hs", "toggle"), "osc1SawButton": ("osc1saw", "toggle"), "osc2SawButton": ("osc2saw", "toggle"),
 "osc1PulButton": ("osc1pul", "toggle"), "osc2PulButton": ("osc2pul", "toggle"),
 "filterDetuneKnob": ("filterder", "knob"), "envelopeDetuneKnob": ("envder", "knob"), "portamentoDetuneKnob": ("portader", "knob"),
}
for i in range(1, 9):
    MAP["pan%dKnob" % i] = ("pan%d" % i, "knob")

# not on the panel: the second page (same knobs and buttons as the panel, bigger)
MORE_KNOBS = [("master_hz", "FREQUENCY (HZ)"), ("pw_env", "PW ENV"), ("pw_osc2_ofs", "PW OSC2 OFS"), ("level_dif", "LEVEL DIFF")]
MORE_TOGGLES = [("pw_env_both", "PW ENV BOTH"), ("env_pitch_both", "PITCH ENV BOTH"), ("fenv_invert", "FENV INVERT"),
                ("self_osc_push", "SELF-OSC PUSH"), ("lfo_sync", "LFO SYNC"), ("economy_mode", "ECONOMY")]

# LFO SYNC button + TEMPO display (the project's tempo), in the MODULATION section's free slot and the strip under it. Panel-image px.
SYNC_CX, SYNC_CY, SYNC_LABEL_CY = 860, 532, 565         # the button's centre and its label's centre
TEMPO_CX, TEMPO_CY, TEMPO_W, TEMPO_H = 1167, 36, 154, 64        # top right corner
LFO_WORD_BOX, SYNC_WORD_BOX = (680, 356, 706, 371), (320, 311, 369, 327)    # where the theme prints "LFO RATE" and "SYNC"

# BANK / PATCH selector geometry (plugin-area pixels): display width, button width, strip top and height; groups = (x0, key)
SEL_DW, SEL_BW, SEL_GAP, SEL_Y0, SEL_H = 250, 56, 4, 4, 64
# a group is the stacked up/down button (left) then the display; x0 is the group's left edge. Two groups, 16 px apart, centred on x=640
SEL_GROUPS = [(287, "bank"), (673, "patch")]      # group = left arrow (56), display (192), right arrow (56); 16 px apart, centred on x=640

# Bigger controls for big hands (0.3.0). The theme's pictures are scaled up by these factors; the buttons' pictures carry a
# transparent margin, which is the extra touch area (a toggle's touch box is its picture); knobs get a bigger touch box.
KNOB_UP = 1.36           # knob picture (frame incl. shadow) 50 -> 68 px; every knob has this size
BTN_UP = 1.61            # button pictures 41 -> 66 px; every button has this size (VAM and STOP: BIG_BTN)
LEG_UP = 1.5             # the legato and voices displays
BIG_BTN = 84             # VAM and STOP are a little bigger than the other buttons
PAD_X, PAD_Y = 1, 4      # transparent margin round each button picture (px each side)
# The OB-Xd logo is drawn smaller and higher, and the left column's sections (MASTER, GLOBAL, LEGATO/VOICES) move up by these
# amounts (plugin-area px) so the whole panel has more air for the bigger controls. Slabs are (y0, y1, dy) of the panel image.
LOGO_BOX, LOGO_SCALE, LOGO_TOP = (40, 58, 280, 150), 0.66, 12
# (y0, y1, dy, band): the band is the run of blank panel rows (y0, y1) that fills the gap above the slab (mirrored back and forth)
LEFT_SLABS = [(160, 208, -62, (150, 162)), (208, 260, -36, (199, 207)), (260, 285, -25, (199, 207)), (296, 348, -26, (276, 288)),
              (348, 394, -21, (338, 347)), (394, 420, -8, (338, 347)), (425, 495, 4, (408, 420)), (548, 580, 14, (500, 510))]
TAIL_BAND = (500, 510)
LEFT_X = (30, 287)
KEY_DY = {"volume": -36, "tune": -36, "octave": -36, "udet": -21, "unison": -21, "portamento": -21,
          "legatomode": 4, "voice_count": 4}
# the two knobs squeezed between buttons (OSC2 DETUNE, MULTIMODE) are a little smaller, and their neighbours move out a few px
# MASTER and GLOBAL have the room: bigger knobs, centred between the section line and the printed labels
BIG_UP = 1.35
KNOB_UP_KEY = {}     # (per-control knob sizes: none, all knobs are the same size)
KNOB_EXTRA = {"volume": 4, "tune": 4, "octave": 4, "udet": 3, "portamento": 3, "unison": 3}   # px down, to centre them
KEY_DX = {"osc1saw": -3, "osc1pul": -5, "osc2saw": 5, "osc2pul": 3,       # the rows with a knob between four buttons:
          "flt_kf": -3, "filter_warm": -5, "bandpass": 5, "fourpole": 3}   # spread out so nothing overlaps
BIG_Y = 541              # area y of the VAM / STOP buttons' centre
UP_SHIFT = 2             # px the bigger controls move up, to keep the printed labels clear below them

QLINKS = ["cutoff", "resonance", "envelope_amt", "multimode", "fatk", "fdec", "fsus", "frel",
          "latk", "ldec", "lsus", "lrel", "volume", "lfofreq", "lfo1amt", "osc2_det"]


def pick(theme, name):
    """The theme's sharpest copy of an image: @4x, then @2x, then the base file."""
    for suffix in ("@4x", "@2x", ""):
        p = os.path.join(theme, name.replace(".png", suffix + ".png"))
        if os.path.isfile(p):
            return p
    sys.exit("theme is missing %s" % name)


def frames_of(path, n):
    """Cut a filmstrip into n equal frames, top to bottom."""
    im = Image.open(path).convert("RGBA")
    h = im.height // n
    return [im.crop((0, i * h, im.width, (i + 1) * h)) for i in range(n)]



# ---------------------------------------------------------------------------------------------------------------
# Re-labelling the GLOBAL panel's bottom row. The theme prints "VAM  LEARN  CLEAR" into main.png. The port has no
# MIDI learn, so the row becomes two centred buttons, "VAM" and "STOP". The letters are lifted from the theme's own
# printed labels (STEP, OSC1, VAM) so the font matches. Pure Python on small crops (no numpy needed).
# ---------------------------------------------------------------------------------------------------------------
def _lum(px):
    return 0.299 * px[0] + 0.587 * px[1] + 0.114 * px[2]


def _letters(img, box, thr=40):
    """Letters inside box (x0,y0,x1,y1) of an RGB image: [(RGBA glyph, (x0,y0,x1,y1) in img coords)], left to right.
    A letter is an 8-connected blob brighter than its row's background; alpha comes from that brightness."""
    x0, y0, x1, y1 = box
    c = img.crop(box).convert("RGB")
    w, h = c.size
    px = c.load()
    bg = []
    for y in range(h):
        row = sorted(_lum(px[x, y]) for x in range(w))
        bg.append(row[len(row) // 2])
    on = [[(_lum(px[x, y]) - bg[y]) > thr for x in range(w)] for y in range(h)]
    seen = [[False] * w for _ in range(h)]
    blobs = []
    for y in range(h):
        for x in range(w):
            if on[y][x] and not seen[y][x]:
                stack, pts = [(x, y)], []
                seen[y][x] = True
                while stack:
                    cx, cy = stack.pop()
                    pts.append((cx, cy))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h and on[ny][nx] and not seen[ny][nx]:
                                seen[ny][nx] = True
                                stack.append((nx, ny))
                if len(pts) > 60:
                    blobs.append(pts)
    ink_pts = [px[x, y] for pts in blobs for (x, y) in pts]
    if not ink_pts:
        return []
    ink_pts.sort(key=_lum)
    top = ink_pts[-max(1, len(ink_pts) // 5):]
    ink = tuple(int(sum(p[i] for p in top) / len(top)) for i in range(3))
    span = max(1.0, _lum(ink) - sum(bg) / len(bg))
    out = []
    for pts in sorted(blobs, key=lambda b: min(p[0] for p in b)):
        bx0, bx1 = min(p[0] for p in pts) - 3, max(p[0] for p in pts) + 4
        by0, by1 = min(p[1] for p in pts) - 3, max(p[1] for p in pts) + 4
        near = set()
        for (x, y) in pts:                                  # the blob and its anti-aliased fringe, not neighbouring letters
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    near.add((x + dx, y + dy))
        g = Image.new("RGBA", (bx1 - bx0, by1 - by0), ink + (0,))
        gp = g.load()
        for (x, y) in near:
            if bx0 <= x < bx1 and by0 <= y < by1 and 0 <= x < w and 0 <= y < h:
                a = (_lum(px[x, y]) - bg[y]) / span
                gp[x - bx0, y - by0] = ink + (int(max(0.0, min(1.0, a)) * 255),)
        out.append((g, (x0 + bx0, y0 + by0, x0 + bx1, y0 + by1)))
    return out


def _word(img, box, thr=18):
    """The printed word inside box (x0,y0,x1,y1) of an RGB image as an RGBA picture trimmed to its ink (alpha = brightness over the
    row's background), or None. Unlike _letters it does not split into letters."""
    x0, y0, x1, y1 = box
    c = img.crop(box).convert("RGB")
    w, h = c.size
    px = c.load()
    bgl = []
    for y in range(h):
        row = sorted(_lum(px[x, y]) for x in range(w))
        bgl.append(row[len(row) // 2])
    al = [[_lum(px[x, y]) - bgl[y] for x in range(w)] for y in range(h)]
    pts = [(x, y) for y in range(h) for x in range(w) if al[y][x] > thr]
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    ink_src = sorted((px[x, y] for (x, y) in pts), key=_lum)
    top = ink_src[-max(1, len(ink_src) // 5):]
    ink = tuple(int(sum(p[i] for p in top) / len(top)) for i in range(3))
    span = max(1.0, max(al[y][x] for (x, y) in pts))
    m = 3
    bx0, bx1, by0, by1 = max(0, min(xs) - m), min(w, max(xs) + m + 1), max(0, min(ys) - m), min(h, max(ys) + m + 1)
    out = Image.new("RGBA", (bx1 - bx0, by1 - by0), ink + (0,))
    op = out.load()
    for y in range(by0, by1):
        for x in range(bx0, bx1):
            op[x - bx0, y - by0] = ink + (int(max(0.0, min(1.0, al[y][x] / span)) * 255),)
    return out


# Where the label glyphs we reuse sit in each theme's main image, in the theme's own base pixels (x0, y0, x1, y1).
GLYPHS = {
    # letters of STOP, each lifted from a label the theme prints itself: (box in base px, index among the letters found there, how many are expected)
    "classic": dict(squares=False, vam_dy=True,
                    S=((398, 214, 448, 234), 0, 4), T=((398, 214, 448, 234), 1, 4), O=((276, 86, 320, 104), 0, 4), P=((398, 214, 448, 234), 3, 4)),
    "default": dict(squares=True, vam=(100, 462, 142, 481),
                    S=((968, 86, 1028, 102), 0, 7),    # SUSTAIN
                    T=((968, 86, 1028, 102), 3, 7),    # SUSTAIN
                    O=((292, 90, 332, 108), 0, 4),     # OSC1
                    P=((358, 90, 396, 108), 0, 2)),    # PW
}


def relabel_global(im, items):
    """im: the theme's main image (RGB, any resolution). Returns (new image, (vam_x, stop_x) button centres in base px, theme kind)."""
    kind = "default" if "menu" in items else "classic"
    cfg = GLYPHS[kind]
    k = im.width / float(items["guisize"]["x"])
    def B(*v):
        return tuple(int(round(t * k)) for t in v)
    names = [n for n in ("menu", "asPlayedAllocButton", "midiLearnButton", "midiUnlearnButton") if n in items]
    vam = items["asPlayedAllocButton"]
    bw = float(vam.get("w", 28))
    bh = float(vam.get("h", 35))
    row_y0 = float(vam["y"]) + bh + 1                               # just under the buttons
    left = min(float(items[n]["x"]) for n in names)
    right = max(float(items[n]["x"]) for n in names) + bw
    vbox = B(*cfg["vam"]) if "vam" in cfg else B(left - 4, row_y0, left + 40, row_y0 + 22)
    vam_l = _letters(im, vbox)
    glyph = {}
    for ch in "STOP":
        box, idx, n = cfg[ch]
        found = _letters(im, B(*box))
        if len(found) != n:
            glyph = None
            break
        glyph[ch] = found[idx][0]
    if len(vam_l) != 3 or glyph is None:
        sys.stderr.write("note: the theme's labels were not where the known themes have them: leaving the bottom row as printed\n")
        return im, None, kind
    S_, T_, O_, P_ = (glyph[c] for c in "STOP")
    (vy0, vy1) = (min(b[1] for _, b in vam_l), max(b[3] for _, b in vam_l))
    cy = (vy0 + vy1) // 2
    # erase the old row (labels, and for some themes the button recesses): every pixel row is blended between the clean
    # panel texture just left and just right of the group
    if cfg["squares"]:
        sy0, sy1 = B(0, float(vam["y"]) - 4, 0, 0)[1], B(0, row_y0 + 30, 0, 0)[1]
    else:
        sy0, sy1 = B(0, row_y0, 0, 0)[1], B(0, row_y0 + 22, 0, 0)[1]
    ex0, ex1 = B(left - 8, 0, 0, 0)[0], B(right + 8, 0, 0, 0)[0]
    out = im.copy()
    op, ip = out.load(), im.load()
    wlen = max(2, int(3 * k))
    for y in range(sy0, min(sy1, im.height)):
        lc = [ip[x, y] for x in range(ex0 - wlen - int(4 * k), ex0 - int(4 * k))]
        rc = [ip[x, y] for x in range(ex1 + int(4 * k), ex1 + int(4 * k) + wlen)]
        ml = tuple(sum(c[i] for c in lc) // len(lc) for i in range(3))
        mr = tuple(sum(c[i] for c in rc) // len(rc) for i in range(3))
        for x in range(ex0, ex1):
            t = (x - ex0) / float(max(1, ex1 - ex0 - 1))
            op[x, y] = tuple(int(ml[i] * (1 - t) + mr[i] * t) for i in range(3))
    # two buttons, centred on the old group: the group's middle, +-32 base px
    mid = (left + right) / 2.0
    vam_cx, stop_cx = mid - 32.0, mid + 32.0
    out = out.convert("RGBA")
    # VAM: keep the printed word exactly as drawn (V, A, M at their original offsets)
    x_first, x_last = vam_l[0][1][0], vam_l[-1][1][2]
    w_vam = x_last - x_first
    ox = int(round(vam_cx * k)) - w_vam // 2
    for g, b in vam_l:
        out.alpha_composite(g, (ox + b[0] - x_first, b[1]))
    # STOP: S T O P with the theme's own letter spacing
    gap = int(round(0.5 * k))
    word = [S_, T_, O_, P_]
    ww = sum(g.width for g in word) + gap * 3 - 6 * 3                # glyphs carry 3 px of margin each side
    ox = int(round(stop_cx * k)) - ww // 2
    for g in word:
        gy = cy - g.height // 2
        out.alpha_composite(g, (ox, gy))
        ox += g.width + gap - 6
    return out.convert("RGB"), (vam_cx, stop_cx), kind


def gradient_column(im, items, x_base, y0_base, y1_base):
    """A vertical run of the panel's own body colours (list of RGB), to paint matching panels elsewhere."""
    k = im.width / float(items["guisize"]["x"])
    px = im.convert("RGB").load()
    x = int(x_base * k)
    return [px[x, y] for y in range(int(y0_base * k), int(y1_base * k))]


def arrow_png(left, pressed):
    """A raised, bevelled key with an arrow (the BANK / PATCH selector's buttons), SEL_BW x SEL_H, rounded on the outer side only.
    Pressed: the key sinks (darker, shading inverted, arrow nudged down). Drawn 4x and scaled down."""
    import numpy as np
    from PIL import ImageDraw as D, ImageFilter
    k = 4
    w, h = SEL_BW * k, SEL_H * k
    R = 9 * k
    corners = (True, False, False, True) if left else (False, True, True, False)

    def shape(inset, fill_alpha=255):
        m = Image.new("L", (w, h), 0)
        dd = D.Draw(m)
        dd.rounded_rectangle([inset, inset, w - 1 - inset, h - 1 - inset], radius=max(2, R - inset), fill=fill_alpha, corners=corners)
        return m

    def vgrad(top, bot, y0, y1):
        t = np.clip((np.arange(h, dtype="float32") - y0) / max(1.0, (y1 - y0)), 0, 1)[:, None, None]
        arr = np.asarray(top, dtype="float32")[None, None, :] * (1 - t) + np.asarray(bot, dtype="float32")[None, None, :] * t
        return Image.fromarray(np.repeat(arr, w, axis=1).astype("uint8"), "RGB")

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rim = shape(0)
    out.paste(Image.new("RGBA", (w, h), (10, 9, 8, 255)), (0, 0), rim)                          # dark outline
    ins = 2 * k
    if not pressed:
        body_t, body_b, hi, lo = (104, 100, 92), (30, 28, 25), (150, 146, 136), (8, 7, 6)
    else:
        body_t, body_b, hi, lo = (30, 28, 25), (62, 59, 53), (12, 11, 10), (84, 80, 72)
    # bevel: a light edge top-left, a dark edge bottom-right, then the face
    bevel = vgrad(hi, lo, 0, h).convert("RGBA")
    out.paste(bevel, (0, 0), shape(1 * k))
    face_m = shape(3 * k if not pressed else 3 * k)
    face = vgrad(body_t, body_b, 3 * k, h - 3 * k).convert("RGBA")
    out.paste(face, (0, 0), face_m)
    # a soft gloss over the upper third of the face (not when pressed)
    if not pressed:
        gm = Image.new("L", (w, h), 0)
        gd = D.Draw(gm)
        gd.rounded_rectangle([5 * k, 4 * k, w - 5 * k, h // 2], radius=6 * k, fill=44)
        gm = gm.filter(ImageFilter.GaussianBlur(6 * k))
        out.paste(Image.new("RGBA", (w, h), (255, 255, 255, 255)), (0, 0), Image.composite(gm, Image.new("L", (w, h), 0), face_m))
    else:                                                     # a shadow along the top inside edge of a pressed key
        sm = Image.new("L", (w, h), 0)
        D.Draw(sm).rectangle([0, 0, w, 7 * k], fill=150)
        sm = sm.filter(ImageFilter.GaussianBlur(3 * k))
        out.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (0, 0), Image.composite(sm, Image.new("L", (w, h), 0), face_m))
    # the arrow: a drop shadow, then a lit triangle
    dy = 3 * k if pressed else 0
    cx_, cy_ = w / 2 + (-1 if left else 1) * 1.5 * k, h / 2 + dy
    tw, th = 12 * k, 15 * k
    if left:
        tri = [(cx_ + tw / 2, cy_ - th), (cx_ + tw / 2, cy_ + th), (cx_ - tw, cy_)]
    else:
        tri = [(cx_ - tw / 2, cy_ - th), (cx_ - tw / 2, cy_ + th), (cx_ + tw, cy_)]
    if not pressed:
        sh = Image.new("L", (w, h), 0)
        D.Draw(sh).polygon([(x, y + 3 * k) for x, y in tri], fill=200)
        sh = sh.filter(ImageFilter.GaussianBlur(1.5 * k))
        out.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (0, 0), sh)
    am = Image.new("L", (w, h), 0)
    D.Draw(am).polygon(tri, fill=255)
    ytop, ybot = cy_ - th, cy_ + th
    ag = vgrad((236, 238, 244) if not pressed else (170, 174, 184), (160, 164, 176) if not pressed else (110, 114, 124),
               int(ytop), int(ybot)).convert("RGBA")
    out.paste(ag, (0, 0), am)
    return out.resize((SEL_BW, SEL_H), LZ)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("theme")
    ap.add_argument("--width", type=int, default=AREA_W,
                    help="panel width in px (default 1280 = the whole screen width; use ~1020 to stay clear of the Q-Link sidebar)")
    a = ap.parse_args()
    theme = a.theme

    txt = open(os.path.join(theme, "coords.xml"), encoding="latin-1").read()
    txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
    items = {}
    for m in re.finditer(r"<VALUE\s+([^>]*?)/>", txt):
        d = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        items[d["NAME"]] = d
    gw, gh = float(items["guisize"]["x"]), float(items["guisize"]["y"])
    S = a.width / gw
    PW, PH = round(gw * S), round(gh * S)
    X0 = (AREA_W - PW) / 2.0                    # panel left edge (layout x)
    ypad = (AREA_H - PH) // 2                   # panel top inside the plugin area
    Y0 = Y_OFF + ypad

    img = os.path.join(VST, "images")
    shutil.rmtree(img, ignore_errors=True)
    os.makedirs(img)

    # background: the panel at its exact size; the strip above/below (and beside, for a narrow panel) is the panel's own edge
    raw_main = Image.open(pick(theme, "main.png")).convert("RGB")
    raw_main, btn_pos, kind = relabel_global(raw_main, items)          # VAM + STOP instead of VAM / LEARN / CLEAR
    main_img = raw_main.convert("RGBA").resize((PW, PH), LZ)
    bg = Image.new("RGBA", (AREA_W, AREA_H))
    px = int(X0)
    bg.paste(main_img, (px, ypad))
    if ypad > 0:
        # extend the panel up and down with its own edge texture, mirrored back and forth (a stretched 1 px row would streak)
        bh_ = max(4, int(9 * S))
        def idx(d):
            j = d % (2 * bh_)
            return j if j < bh_ else 2 * bh_ - 1 - j
        for d in range(ypad):
            bg.paste(main_img.crop((0, idx(d), PW, idx(d) + 1)), (px, ypad - 1 - d))
        for d in range(AREA_H - ypad - PH):
            bg.paste(main_img.crop((0, PH - 1 - idx(d), PW, PH - idx(d))), (px, ypad + PH + d))
    if px > 0:
        bg.paste(bg.crop((px, 0, px + 1, AREA_H)).resize((px, AREA_H)), (0, 0))
        bg.paste(bg.crop((px + PW - 1, 0, px + PW, AREA_H)).resize((AREA_W - px - PW, AREA_H)), (px + PW, 0))
    from PIL import ImageDraw as _D
    # the logo, lifted from the theme's picture as a mask (alpha = how much brighter than the plate each pixel is) and drawn smaller,
    # in each colour theme's own ink, on the redrawn panels
    import numpy as np
    lgc = bg.crop(LOGO_BOX).convert("RGB")
    lw_, lh_ = int(lgc.width * LOGO_SCALE), int(lgc.height * LOGO_SCALE)
    lgc = lgc.resize((lw_, lh_), LZ)
    L_ = np.asarray(lgc.convert("L"), dtype="float32")
    bgl = float(np.median(np.concatenate([L_[0], L_[-1], L_[:, 0], L_[:, -1]])))
    topl = float(np.percentile(L_, 99.7))
    a_ = np.clip((L_ - bgl) / max(1.0, topl - bgl), 0, 1) ** 0.85
    ex = np.minimum(np.arange(lw_), lw_ - 1 - np.arange(lw_))[None, :]
    ey = np.minimum(np.arange(lh_), lh_ - 1 - np.arange(lh_))[:, None]
    e_ = np.minimum(ex, ey)
    a_ = a_ * np.clip(e_ / 6.0, 0, 1)
    logo_mask = Image.fromarray((a_ * 255).astype("uint8"), "L")
    base_px = [bg.convert("RGB").getpixel(pt) for pt in ((300, 610), (160, 610), (1000, 610), (640, 610), (1180, 612))]
    base_rgb = tuple(sorted(c[i] for c in base_px)[len(base_px) // 2] for i in range(3))
    import panel_draw

    # knobs: the theme's picture is 48 px for a 42 px knob (the rest is its shadow). Each knob size gets its own
    # strip whose frame is F x F, F = 2r+8, which is exactly the box the skin builder draws a frame into: 1:1, no resampling.
    knob_frames = frames_of(pick(theme, "knob.png"), 128)
    rK = (panel_draw.KF - 8) // 2                                   # every knob has this size
    FK = 2 * rK + 8
    o = Image.new("RGBA", (FK, FK * 128))
    for i, fr in enumerate(knob_frames):
        o.paste(fr.resize((FK, FK), LZ), (0, i * FK))
    o.save(os.path.join(img, "knob_%d.png" % FK))
    knob_path = "images/knob_%d.png" % FK

    # buttons (on/off)
    bw0, bh0 = float(items["unisonButton"].get("w", 28)), float(items["unisonButton"].get("h", 35))
    BW, BH = round(bw0 * S), round(bh0 * S)
    off, on = frames_of(pick(theme, "button.png"), 2)
    TW, TH = round(BW * BTN_UP), round(BH * BTN_UP)               # the visible button
    BW, BH = TW + 2 * PAD_X, TH + 2 * PAD_Y                       # the picture: the button plus a transparent margin (= touch area)
    for fr, nm in ((off, "btn_off.png"), (on, "btn_on.png")):
        pic = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        pic.alpha_composite(fr.resize((TW, TH), LZ), (PAD_X, PAD_Y))
        pic.save(os.path.join(img, nm))

    LBW, LBH = BIG_BTN + 2 * PAD_X, BIG_BTN + 2 * PAD_Y                  # VAM and STOP
    for fr, nm in ((off, "btn_big_off.png"), (on, "btn_big_on.png")):
        pic = Image.new("RGBA", (LBW, LBH), (0, 0, 0, 0))
        pic.alpha_composite(fr.resize((BIG_BTN, BIG_BTN), LZ), (PAD_X, PAD_Y))
        pic.save(os.path.join(img, nm))

    # voice count digits (OB-Xd 2.10 has 8 voices) and legato labels (4)
    vw, vh = float(items["voiceSwitch"].get("w", 38)), float(items["voiceSwitch"].get("h", 32))
    VW, VH = round(vw * S * LEG_UP), round(vh * S * LEG_UP)
    vf = frames_of(pick(theme, "voices.png"), 32)[:8]
    o = Image.new("RGBA", (VW, VH * 8))
    for i, fr in enumerate(vf):
        o.paste(fr.resize((VW, VH), LZ), (0, i * VH))
    voices_strip = o
    lw, lh = float(items["legatoSwitch"].get("w", 89)), float(items["legatoSwitch"].get("h", 32))
    LW, LH = round(lw * S * LEG_UP), round(lh * S * LEG_UP)
    lf = frames_of(pick(theme, "legato.png"), 4)
    o = Image.new("RGBA", (LW, LH * 4))
    for i, fr in enumerate(lf):
        o.paste(fr.resize((LW, LH), LZ), (0, i * LH))
    legato_strip = o
    def tinted(strip, th):
        """The red LED display strip in a theme's colours: its black becomes the well's tint, its red the display colour."""
        arr = np.asarray(strip.convert("RGBA"), dtype="float32")
        I = np.clip(arr[:, :, 0:1] / 215.0, 0, 1)
        tint = np.asarray(th["well"][0], dtype="float32")[None, None, :]
        disp = np.asarray([int(th["disp"][i:i + 2], 16) for i in (0, 2, 4)], dtype="float32")[None, None, :]
        rgb = tint * (1 - I) + disp * I
        return Image.fromarray(np.concatenate([rgb, arr[:, :, 3:4]], axis=2).astype("uint8"), "RGBA")
    for ti, th in enumerate(panel_draw.THEMES):
        tinted(voices_strip, th).save(os.path.join(img, "voices8_%d.png" % ti))
        tinted(legato_strip, th).save(os.path.join(img, "legato_%d.png" % ti))

    # the pages' backgrounds, drawn now that the control pictures' sizes are known
    dims = dict(btn_h=BH, leg_w=LW, leg_h=LH, vox_w=VW, big_h=LBH)
    tempo_box = (TEMPO_CX - TEMPO_W // 2, TEMPO_CY - TEMPO_H // 2, TEMPO_CX + TEMPO_W // 2, TEMPO_CY + TEMPO_H // 2)
    placements_by_page = {}
    first_bg = None
    theme_pb = {}
    for ti in range(len(panel_draw.THEMES)):
        for page in panel_draw.PAGES:
            pb = bg.copy()
            pl = panel_draw.draw(page, ti, pb, base_rgb, logo_mask, SEL_GROUPS, SEL_DW, SEL_BW, SEL_GAP, SEL_Y0, SEL_H, tempo_box, dims)
            placements_by_page.setdefault(page, pl)             # the same controls in every theme
            pb.convert("RGB").save(os.path.join(img, "panel_%s_%d.png" % (page, ti)))
            first_bg = first_bg or pb
            if page == "osc":
                theme_pb[ti] = pb
    bg = first_bg
    from PIL import ImageDraw as _D
    for left in (True, False):
        for pressed in (False, True):
            arrow_png(left, pressed).save(os.path.join(img, "sel_%s_%s.png" % ("left" if left else "right", "on" if pressed else "off")))
    plate = "%02x%02x%02x" % bg.getpixel((AREA_W // 2, 2))[:3]

    # MORE page: the same knobs and buttons as the other pages, on a plate with panels like theirs
    # panel body colours from the theme (a clean strip inside the GLOBAL panel), stretched over each MORE panel
    if kind == "default":
        col = gradient_column(raw_main, items, 33, 20, 460)        # the clean strip between the wood and the first section
        n3 = max(1, len(col) // 3)
        c0 = tuple(sum(c[i] for c in col[:n3]) // n3 for i in range(3))
        c1 = tuple(sum(c[i] for c in col[-n3:]) // n3 for i in range(3))
        # the texture wobbles; use a smooth top-to-bottom gradient of the same colours
        grad = [tuple(int(c0[i] + (c1[i] - c0[i]) * t / 99.0) for i in range(3)) for t in range(100)]
        kk = raw_main.width / float(items["guisize"]["x"])
        rp = raw_main.convert("RGB").load()
        blue = max((rp[x, y] for x in range(int(60 * kk), int(240 * kk), 3) for y in range(int(100 * kk), int(160 * kk))),
                   key=lambda c: c[2] - c[0])
    else:
        grad = gradient_column(raw_main, items, float(items["midiUnlearnButton"]["x"]) + bw0 + 22, 312, 428)
    plate_rgb = bg.convert("RGB").getpixel((AREA_W // 2, 2))
    if kind == "default":
        plate_rgb = tuple(int(v * 0.78) for v in plate_rgb)            # a darker plate so the lighter panels stand out
    mbg = bg.convert("RGB").copy()
    from PIL import ImageDraw
    dr = ImageDraw.Draw(mbg)
    dr.rectangle([px, 0, px + PW - 1, AREA_H], fill=plate_rgb)
    more_panels = [(60, 40, 1220, 280), (60, 312, 1220, 560)]            # x0, y0, x1, y1 inside the plugin area
    for (x0, y0, x1, y1) in more_panels:
        hh = y1 - y0
        for yy in range(hh):
            t = yy * (len(grad) - 1) / float(max(1, hh - 1))
            c0, c1 = grad[int(t)], grad[min(len(grad) - 1, int(t) + 1)]
            f = t - int(t)
            col = tuple(int(c0[i] * (1 - f) + c1[i] * f) for i in range(3))
            dr.line([x0, y0 + yy, x1, y0 + yy], fill=col)
    if kind == "default":                                  # the theme's blue rule along the top of each panel
        for (x0, y0, x1, y1) in more_panels:
            dr.rectangle([x0, y0, x1, y0 + 2], fill=blue)
            dr.rectangle([x0, y1 - 1, x1, y1], fill=tuple(max(0, v - 14) for v in grad[-1]))
    WOOD = 28 if kind == "default" else 32                                               # the wooden side cheeks of the panel image
    mbg.paste(bg.convert("RGB").crop((0, 0, WOOD, AREA_H)), (0, 0))
    mbg.paste(bg.convert("RGB").crop((AREA_W - WOOD, 0, AREA_W, AREA_H)), (AREA_W - WOOD, 0))
    mbg.save(os.path.join(img, "more_bg.png"))

    # one MORE background per theme: the theme's plate, panels with its rule colour, and the control labels drawn in its ink
    from PIL import ImageFont as _F
    lab_font = _F.truetype(panel_draw.FONT_LABEL, 18)
    col_w = lambda n_: 1160 // n_ - 26
    nk_, nt_ = len(MORE_KNOBS), len(MORE_TOGGLES)
    for ti, th in enumerate(panel_draw.THEMES):
        tb = Image.new("RGBA", (AREA_W, AREA_H), (0, 0, 0, 255))
        panel_draw._plate(tb, th["base"] or plate_rgb, th["noise"])
        panel_draw._sheen(tb)
        tb = tb.convert("RGB")
        pl_rgb = tb.getpixel((AREA_W // 2, 2))
        dark = sum(pl_rgb) < 300
        pan = tuple(min(255, v + 16) if dark else max(0, v - 20) for v in pl_rgb)
        d_ = ImageDraw.Draw(tb)
        panel_draw.CUR.update(th)
        for (x0, y0, x1, y1) in more_panels:
            d_.rectangle([x0, y0, x1, y1], fill=pan)
            panel_draw._hline(tb, x0, x1, y0, th["rule"], h=2)
            panel_draw._hline(tb, x0, x1, y0 + 2, th["div_l"] if th["key"] != "slate" else (120, 126, 150), h=1, peak=90)
            panel_draw._hline(tb, x0, x1, y1 - 1, tuple(max(0, v - 14) for v in pan), h=2, peak=255, fade=1)
        tb.paste(theme_pb[ti].convert("RGB").crop((0, 0, 28, AREA_H)), (0, 0))
        tb.paste(theme_pb[ti].convert("RGB").crop((AREA_W - 28, 0, AREA_W, AREA_H)), (AREA_W - 28, 0))
        d_ = ImageDraw.Draw(tb)
        ink = th["ink"]
        def put(cx, cy, txt, maxw=None):
            panel_draw.CUR.update(th)
            if maxw and d_.textlength(txt, font=lab_font) + 0.5 * len(txt) > maxw and " " in txt:   # too wide for its column: two lines
                words = txt.split(" "); h = len(words) // 2 + (len(words) > 2)
                txt = " ".join(words[:h]) + "\n" + " ".join(words[h:])
            for j, ln in enumerate(txt.split("\n")):
                panel_draw._text(d_, cx, cy + 21 * j, ln, lab_font)
        for i, (key, label) in enumerate(MORE_KNOBS):
            put(round(60 + 1160 * (i + 0.5) / nk_), 134 + rK + 50, label, col_w(nk_))
        for i, (key, label) in enumerate(MORE_TOGGLES):
            put(round(60 + 1160 * (i + 0.5) / nt_), 421 + BH // 2 + 20, label, col_w(nt_))
        tb.save(os.path.join(img, "more_bg_%d.png" % ti))

    params = {p["key"]: p for p in json.load(open(os.path.join(VST, "params.json")))["params"]}
    L = ["# OB-Xd panel for the MPC, generated by tools/make_skin.py from the theme's coords.xml (scale %.3f)" % S,
         "theme_bg=%s" % plate,
         "qlinks_track = " + ",".join(QLINKS)]
    used = set()

    def header_text(ti):
        """The BPM display's and the BANK / PATCH displays' text, in theme ti's colours (shown only while that theme is chosen)."""
        th = panel_draw.THEMES[ti]
        wh = " when=theme:%d" % ti
        H_ = []
        H_.append('text cx=%d cy=%d label="BPM" size=1.35 color=%s%s' % (TEMPO_CX, Y_OFF + TEMPO_CY - 20, th["cap"], wh))
        H_.append('readout cx=%d cy=%d w=%d h=%d label="" key=tempo_text box=0 tsize=30 tcolor=%s talign=center tpad=0%s' % (
            TEMPO_CX, Y_OFF + TEMPO_CY + 12, TEMPO_W - 20, 34, th["disp"], wh))
        for (x0, key) in SEL_GROUPS:
            top = Y_OFF + SEL_Y0
            dx = x0 + SEL_BW + SEL_GAP                       # the display's left edge
            H_.append('text cx=%d cy=%d label="%s" size=1.1 color=%s%s' % (dx + 34, top + 12, key.upper(), th["cap"], wh))
            H_.append('readout cx=%d cy=%d w=56 h=28 label="" key=%s box=0 tsize=22 tcolor=%s talign=right tpad=2%s' % (
                dx + SEL_DW - 32, top + 13, key, th["dim"], wh))
            H_.append('readout cx=%d cy=%d w=%d h=%d label="" key=%s_name box=0 tsize=32 tcolor=%s talign=left tpad=8%s' % (
                dx + SEL_DW // 2, top + 42, SEL_DW - 4, 42, key, th["disp"], wh))
        return H_

    def header_buttons():
        """The BANK / PATCH arrows (the same keys in every theme). The engine reads the .fxb banks in the "banks" folder next to the
        plugin (src/obxd_banks.h). The right arrow steps to the next bank/patch, the left to the previous (wraps)."""
        H_ = []
        for (x0, key) in SEL_GROUPS:
            top = Y_OFF + SEL_Y0
            dx = x0 + SEL_BW + SEL_GAP
            H_.append('button cx=%d cy=%d label="" key=%s_prev img=images/sel_left_off.png img_on=images/sel_left_on.png w=%d h=%d' % (
                x0 + SEL_BW // 2, top + SEL_H // 2, key, SEL_BW, SEL_H))
            H_.append('button cx=%d cy=%d label="" key=%s_next img=images/sel_right_off.png img_on=images/sel_right_on.png w=%d h=%d' % (
                dx + SEL_DW + SEL_GAP + SEL_BW // 2, top + SEL_H // 2, key, SEL_BW, SEL_H))
        return H_

    TAB_NAMES = {"osc": "OSC", "filter": "FILTER"}
    # Q-Links: one line = pages of 4 (the MPC's four knobs), in the order of the panel, left to right and top to bottom
    PAGE_QLINKS = {                      # one set per screen: a second set would show the same panel again
        "osc": [("OSC", ["osc1p", "pw", "osc2p", "xmod",                       # oscillators
                         "osc1mix", "osc2mix", "noisemix", "volume",           # mixer + volume
                         "latk", "ldec", "lsus", "lrel",                       # amp envelope
                         "osc2_det", "brightness", "tune", "octave"])],        # tone, tuning
        "filter": [("FILTER", ["cutoff", "resonance", "envelope_amt", "multimode",
                               "fatk", "fdec", "fsus", "frel",                  # filter envelope
                               "lfofreq", "lfo1amt", "lfo2amt", "-",            # modulation
                               "filterder", "portader", "envder", "-"])],       # slop
    }
    for page in panel_draw.PAGES:
        placements = placements_by_page[page]
        nth = len(panel_draw.THEMES)
        L += ["[tab %s]" % TAB_NAMES[page], "art file=images/panel_%s_0.png" % page,
              'picture x=0 y=%d w=%d h=%d key=theme files="%s" fit=stretch' % (
                  Y_OFF, AREA_W, AREA_H, ",".join("images/panel_%s_%d.png" % (page, i) for i in range(nth)))]
        spots = []
        for pl in placements:
            hw = {"knob": panel_draw.KF // 2, "toggle": BW // 2, "legato": LW // 2, "voices": VW // 2, "vam": LBW // 2, "stop": LBW // 2}[pl["kind"]]
            spots.append((pl["key"], pl["cx"], pl["cy"], hw, pl["kind"]))
        for pl in placements:
            kd, key, cx, cy = pl["kind"], pl["key"], pl["cx"], pl["cy"]
            if key not in params:
                sys.exit("no parameter %s" % key)
            lcy = Y_OFF + cy
            if kd == "knob":
                s_ = 2 * rK + 10
                room = s_ + 10                      # a wider touch box where there is room, but not into a neighbour's picture
                for (k2, cx2, cy2, hw2, kind2) in spots:
                    if k2 != key and abs(cy2 - cy) < s_ and cx2 != cx:
                        room = min(room, abs(cx2 - cx) if kind2 == "knob" else 2 * (abs(cx2 - cx) - hw2))
                bw_ = max(s_ + 2, room // 2 * 2)    # the box must be wider than the picture, or MPC clips its right edge
                bh_ = s_ + 6
                L.append('knob cx=%d cy=%d r=%d label="" key=%s strip=%s lay=side bw=%d bh=%d vs=1' % (
                    cx + (bw_ - s_) // 2, lcy, rK, key, knob_path, bw_, bh_))
            elif kd == "toggle":
                if "options" not in params[key]:
                    sys.exit("%s is not an on/off parameter" % key)
                L.append('toggle cx=%d cy=%d label="" key=%s img=images/btn_off.png img_on=images/btn_on.png w=%d h=%d ns=0 bw=%d' % (
                    cx, lcy, key, BW, BH, BW - 6))
            elif kd == "vam":
                L.append('toggle cx=%d cy=%d label="" key=%s img=images/btn_big_off.png img_on=images/btn_big_on.png w=%d h=%d ns=0 bw=%d' % (
                    cx, lcy, key, LBW, LBH, LBW - 6))
            elif kd == "stop":
                L.append('button cx=%d cy=%d label="" key=stop img=images/btn_big_off.png img_on=images/btn_big_on.png w=%d h=%d' % (
                    cx, lcy, LBW, LBH))
            elif kd == "voices":
                for ti in range(nth):
                    L.append('slider_h cx=%d cy=%d w=%d h=%d label="" key=%s strip=images/voices8_%d.png frames=8 ns=0 vs=1 bw=%d when=theme:%d' % (
                        cx, lcy, VW, VH, key, ti, VW + 4, ti))
            elif kd == "legato":
                for ti in range(nth):
                    L.append('slider_h cx=%d cy=%d w=%d h=%d label="" key=%s strip=images/legato_%d.png frames=4 ns=0 vs=1 bw=%d when=theme:%d' % (
                        cx, lcy, LW, LH, key, ti, LW + 4, ti))
            used.add(key)
        L += header_buttons()
        for ti in range(nth):
            L += header_text(ti)
        used |= {"tempo_text", "bank", "patch", "bank_name", "patch_name", "bank_next", "bank_prev", "patch_next", "patch_prev"}
        for qt, qk in PAGE_QLINKS[page]:
            L.append('qlinks "%s" = %s' % (qt, ",".join(qk)))

    # last page: no title, no frame; the same knobs and buttons on panels like the others'
    L += ["[tab MORE]", "art file=images/more_bg_0.png",
          'picture x=0 y=%d w=%d h=%d key=theme files="%s" fit=stretch' % (
              Y_OFF, AREA_W, AREA_H, ",".join("images/more_bg_%d.png" % i for i in range(nth)))]
    nk = len(MORE_KNOBS)
    VAL = {"slate": "96cdff", "grey": "22242a", "black": "ffb040", "retro": "3a2a20"}     # the live value's colour on each theme's panel
    for i, (key, label) in enumerate(MORE_KNOBS):
        for ti, th in enumerate(panel_draw.THEMES):
            L.append('knob cx=%d cy=%d r=%d label="" key=%s strip=%s ns=0 vs=30 ink_dim=%s when=theme:%d' % (
                round(60 + 1160 * (i + 0.5) / nk), Y_OFF + 134, rK, key, knob_path, VAL[th["key"]], ti))
    nt = len(MORE_TOGGLES)
    for i, (key, label) in enumerate(MORE_TOGGLES):
        L.append('toggle cx=%d cy=%d label="" key=%s img=images/btn_off.png img_on=images/btn_on.png w=%d h=%d ns=0' % (
            round(60 + 1160 * (i + 0.5) / nt), Y_OFF + 421, key, BW, BH))
    L.append('enum_h cx=640 cy=%d label="" key=theme sw=222 sh=54' % (Y_OFF + 592))      # the colour theme: swaps every page's pictures
    L.append('qlinks "MORE" = ' + ",".join(k for k, _ in MORE_KNOBS + MORE_TOGGLES) + ",theme")

    bank_keys = {"theme", "tempo_text", "bank", "patch", "bank_name", "patch_name", "bank_prev", "bank_next", "patch_prev", "patch_next"}
    missing = [k for k in params if k not in used and k not in bank_keys and k not in {e[0] for e in MORE_KNOBS + MORE_TOGGLES}]
    open(os.path.join(VST, "layout.conf"), "w").write("\n".join(L) + "\n")

    cfg_path = os.path.join(VST, "vst.json")
    cfg = json.load(open(cfg_path))
    cfg["layout"] = "layout.conf"
    cfg["art"] = "html"
    cfg["skin_post"] = "skin_post.py"
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print("wrote vst/layout.conf (%d panel controls, scale %.3f, panel %dx%d) and vst/images/" % (len(used), S, PW, PH))
    print("no control for: %s" % (", ".join(missing) or "nothing"))


if __name__ == "__main__":
    main()
