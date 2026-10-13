#!/usr/bin/env python3
"""Turns the CC0 / public-domain factory patches of OB-Xf (https://github.com/surge-synthesizer/OB-Xf, assets/installer/.../Patches)
into OB-Xd .fxb banks for this plugin.

usage: convert_obxf_patches.py <OB-Xf checkout> <out folder> [--selftest]

OB-Xf is a fork of OB-Xd and its own importer maps OB-Xd values onto OB-Xf (src/state/ObxdImporter.cpp). This script applies the
inverse of those formulas. Only patches that
  * say "CC0" in their own license field, and
  * use nothing OB-Xd does not have (xpander filter, noise colour, inverted envelopes, ring mod, LFO 2, LFO to volume, a transpose
    that does not fit OB-Xd's octave switch)
are converted; the rest are skipped. Every converted patch keeps its name and author (credits file written next to the banks).
Not auditioned by ear: OB-Xf's engine differs from OB-Xd's, so a converted patch can sound a little different from the original.
"""
import glob
import math
import os
import re
import struct
import sys
import xml.sax.saxutils as sx

MOBY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "banks", "000 - Moby Pixel.fxb")

# OB-Xd parameter numbers (src/obxd/ParamsEnum.h)
P = dict(MIDILEARN=1, VOLUME=2, VOICE_COUNT=3, TUNE=4, OCTAVE=5, BENDRANGE=6, BENDOSC2=7, LEGATOMODE=8, BENDLFORATE=9, VFLTENV=10,
         VAMPENV=11, ASPLAYED=12, PORTAMENTO=13, UNISON=14, UDET=15, OSC2_DET=16, LFOFREQ=17, LFOSIN=18, LFOSQUARE=19, LFOSH=20,
         LFO1AMT=21, LFO2AMT=22, LFOOSC1=23, LFOOSC2=24, LFOFILTER=25, LFOPW1=26, LFOPW2=27, OSC2HS=28, XMOD=29, OSC1P=30, OSC2P=31,
         OSCQUANT=32, OSC1SAW=33, OSC1PUL=34, OSC2SAW=35, OSC2PUL=36, PW=37, BRIGHT=38, ENVPITCH=39, OSC1MIX=40, OSC2MIX=41,
         NOISEMIX=42, FLT_KF=43, CUTOFF=44, RESONANCE=45, MULTIMODE=46, FILTER_WARM=47, BANDPASS=48, FOURPOLE=49, ENVAMT=50,
         LATK=51, LDEC=52, LSUS=53, LREL=54, FATK=55, FDEC=56, FSUS=57, FREL=58, ENVDER=59, FILTERDER=60, PORTADER=61,
         PAN1=62, ECONOMY=71, LFO_SYNC=72, PW_ENV=73, PW_ENV_BOTH=74, ENV_PITCH_BOTH=75, FENV_INVERT=76, PW_OSC2_OFS=77,
         LEVEL_DIF=78, SELF_OSC_PUSH=79)
NPARAM = 80


def logsc(p, lo, hi, rolloff=19.0):
    return ((math.exp(p * math.log(rolloff + 1.0)) - 1.0) / rolloff) * (hi - lo) + lo


def inv_logsc(y, lo, hi, rolloff=19.0):
    if hi == lo:
        return 0.0
    t = rolloff * (y - lo) / (hi - lo) + 1.0
    return 0.0 if t <= 0 else min(1.0, max(0.0, math.log(t) / math.log(rolloff + 1.0)))


def inv_linsc(y, lo, hi):
    return 0.0 if hi == lo else min(1.0, max(0.0, (y - lo) / (hi - lo)))


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


XD_TO_XF_SYNC = [1, 4, 5, 7, 10, 11, 13, 15, 16]      # OB-Xd's 9 LFO sync buckets -> OB-Xf's 21


def xf_to_xd(a):
    """OB-Xf patch attributes (dict of str -> float) -> list of 80 OB-Xd values, or (None, reason) when it can't be converted."""
    g = lambda k, d=0.0: float(a.get(k, d))
    for k in ("Filter4PoleXpander", "FilterXpanderMode", "NoiseColor", "LFO1ToVolume", "EnvToPitchInvert", "EnvToPWInvert",
              "RingModMix", "LFO2ToVolume", "LFO2ModAmount1", "LFO2ModAmount2"):
        if g(k) > 0.001:
            return None, "uses " + k
    v = list(INIT)
    # master
    v[P["VOLUME"]] = g("Volume")
    v[P["TUNE"]] = g("Tune", 0.5)
    t = (g("Transpose", 0.5) - 0.5) * 48.0                         # semitones
    o = round(t / 12.0) + 1                                         # OB-Xd's octave step; its reference pitch is 12 semitones high
    if o < 0 or o > 4:
        return None, "transpose out of OB-Xd's octave range"
    resid = t - (o - 1) * 12.0
    v[P["OCTAVE"]] = o / 4.0
    voices = min(32, max(1, int(g("Polyphony", 0.25) * 32) + 1))
    # The plugin's VOICES switch has 8 steps, which play 1, 5, 10, ... 32 engine voices. Stacked unison patches (every key plays
    # all voices) at the top steps used up the MPC's CPU, so converted patches stop at step 2 (10 voices), or step 1 (5 voices)
    # with unison on.
    step = round((voices - 1) / 31.0 * 7)
    step = min(step, 1 if g("Unison") > 0.5 else 2)
    v[P["VOICE_COUNT"]] = (step + 0.5) / 8.0
    v[P["FILTER_WARM"]] = g("HQMode")
    up = g("PitchBendUp", 2 / 48.0) * 48.0
    v[P["BENDRANGE"]] = 1.0 if up >= 7 else 0.0
    v[P["BENDOSC2"]] = g("BendOsc2Only")
    hz = 2.0 + g("VibratoRate", 0.0) * 10.0
    v[P["BENDLFORATE"]] = inv_logsc(hz, 3.0, 10.0)
    v[P["PORTAMENTO"]] = g("Portamento")
    v[P["UNISON"]] = g("Unison")
    v[P["UDET"]] = inv_logsc(logsc(g("UnisonDetune"), 0.001, 1.0), 0.001, 0.90)
    v[P["LEGATOMODE"]] = g("EnvLegatoMode")
    v[P["ASPLAYED"]] = 1.0 if g("NotePriority") < 0.25 else 0.0
    # oscillators (OB-Xd's pitch knob is 0..48 semitones, centre 24)
    p1 = g("Osc1Pitch", 0.5) * 48.0 + resid
    p2 = g("Osc2Pitch", 0.5) * 48.0 + resid
    if not (0 <= p1 <= 48 and 0 <= p2 <= 48):
        return None, "oscillator pitch out of range after the octave shift"
    v[P["OSC1P"]], v[P["OSC2P"]] = p1 / 48.0, p2 / 48.0
    v[P["OSC2_DET"]] = g("Osc2Detune")
    v[P["OSC1SAW"]], v[P["OSC1PUL"]] = g("Osc1SawWave"), g("Osc1PulseWave")
    v[P["OSC2SAW"]], v[P["OSC2PUL"]] = g("Osc2SawWave"), g("Osc2PulseWave")
    v[P["OSC2HS"]] = g("OscSync")
    v[P["XMOD"]] = clamp(g("OscCrossmod") * 2.0)
    v[P["PW"]] = g("OscPW", 0.5)
    v[P["PW_OSC2_OFS"]] = clamp(g("Osc2PWOffset") * (0.95 / 0.75))
    v[P["PW_ENV"]] = clamp(g("EnvToPWAmount") * (1.0555555555 / 0.85))
    v[P["PW_ENV_BOTH"]] = g("EnvToPWBothOscs")
    v[P["ENVPITCH"]] = clamp(g("EnvToPitchAmount") / (36.0 / 40.0))
    v[P["ENV_PITCH_BOTH"]] = g("EnvToPitchBothOscs")
    v[P["BRIGHT"]] = g("OscBrightness", 1.0)
    v[P["OSC1MIX"]], v[P["OSC2MIX"]] = g("Osc1Mix", 1.0), g("Osc2Mix", 1.0)
    v[P["NOISEMIX"]] = inv_logsc(g("NoiseMix"), 0.0, 1.0, 35.0)
    # filter
    v[P["CUTOFF"]], v[P["RESONANCE"]] = g("FilterCutoff", 1.0), g("FilterResonance")
    v[P["MULTIMODE"]] = g("FilterMode")
    v[P["BANDPASS"]] = g("Filter2PoleBPBlend")
    v[P["FOURPOLE"]] = g("Filter4PoleMode")
    v[P["SELF_OSC_PUSH"]] = g("Filter2PolePush")
    v[P["FLT_KF"]] = g("FilterKeyFollow")
    v[P["ENVAMT"]] = g("FilterEnvAmount")
    v[P["FENV_INVERT"]] = g("FilterEnvInvert")
    # envelopes (OB-Xf attack times are a third of OB-Xd's)
    for xf, xd, lo, hi in (("AmpEnvAttack", "LATK", 4.0, 60000.0), ("FilterEnvAttack", "FATK", 1.0, 60000.0)):
        ms_xf = logsc(g(xf), lo, hi, 900.0)
        v[P[xd]] = inv_logsc(ms_xf * 3.0, lo, hi, 900.0)
    v[P["LDEC"]], v[P["LSUS"]], v[P["LREL"]] = g("AmpEnvDecay"), g("AmpEnvSustain", 1.0), g("AmpEnvRelease")
    v[P["FDEC"]], v[P["FSUS"]], v[P["FREL"]] = g("FilterEnvDecay"), g("FilterEnvSustain", 1.0), g("FilterEnvRelease")
    v[P["VAMPENV"]], v[P["VFLTENV"]] = g("VelToAmpEnv"), g("VelToFilterEnv")
    # LFO
    sync = g("LFO1TempoSync") > 0.5
    v[P["LFO_SYNC"]] = 1.0 if sync else 0.0
    if sync:
        idx = round(g("LFO1Rate") * 20)
        k = min(range(9), key=lambda i: abs(XD_TO_XF_SYNC[i] - idx))
        v[P["LFOFREQ"]] = k / 8.0 + 0.001
    else:
        hz = logsc(g("LFO1Rate"), 0.0, 250.0, 3775.0)
        v[P["LFOFREQ"]] = inv_logsc(hz, 0.0, 50.0, 120.0)
    v[P["LFOSIN"]] = 1.0 if g("LFO1Wave1") < 0.25 else 0.0
    v[P["LFOSQUARE"]] = 1.0 if g("LFO1Wave2") < 0.25 else 0.0
    v[P["LFOSH"]] = 1.0 if g("LFO1Wave3") < 0.25 else 0.0
    v[P["LFO1AMT"]], v[P["LFO2AMT"]] = g("LFO1ModAmount1"), g("LFO1ModAmount2")
    for xf, xd in (("LFO1ToOsc1Pitch", "LFOOSC1"), ("LFO1ToOsc2Pitch", "LFOOSC2"), ("LFO1ToFilterCutoff", "LFOFILTER"),
                   ("LFO1ToOsc1PW", "LFOPW1"), ("LFO1ToOsc2PW", "LFOPW2")):
        v[P[xd]] = 1.0 if g(xf) >= 0.25 else 0.0
    # variation, pans
    v[P["PORTADER"]], v[P["FILTERDER"]] = g("PortamentoSlop"), g("FilterSlop")
    v[P["ENVDER"]], v[P["LEVEL_DIF"]] = g("EnvelopeSlop"), g("LevelSlop")
    for i in range(8):
        v[P["PAN1"] + i] = g("PanVoice%d" % (i + 1), 0.5)
    return v, None


def read_moby_init():
    d = open(MOBY, "rb").read()
    x = d[168:168 + struct.unpack("<I", d[164:168])[0]].decode("utf-8", "replace")
    m = re.search(r'<program programName="Init Preset"[^>]*>', x)
    vals = [0.0] * NPARAM
    for k, val in re.findall(r' Val_(\d+)="([^"]*)"', m.group(0)):
        if int(k) < NPARAM:
            vals[int(k)] = float(val)
    return vals


INIT = read_moby_init()


def read_xf_patch(path):
    d = open(path, "rb").read()
    i = d.find(b"<?xml")
    x = d[i:].split(b"\0")[0].decode("utf-8", "replace")
    a = dict(re.findall(r' ([A-Za-z0-9]+)="([^"]*)"', x))
    return a


def unent(s):
    return re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), s).replace("&amp;", "&")


def write_bank(path, programs):
    """programs: list of (name, [80 values]); no padding, so the PATCH selector only steps through real patches."""
    progs = list(programs)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<discoDSP currentProgram="1"><programs>'
    for name, vals in progs:
        xml += '<program programName=%s voiceCount="32"' % sx.quoteattr(name)
        xml += "".join(' Val_%d="%r"' % (i, float(vals[i])) for i in range(NPARAM)) + "/>"
    xml += "</programs></discoDSP>"
    raw = xml.encode("utf-8") + b"\0"
    chunk = struct.pack("<II", 0x21324356, len(raw)) + raw
    head = b"CcnK" + struct.pack(">I", 0) + b"FBCh" + struct.pack(">I", 1) + b"Obxd" + struct.pack(">III", 1, len(progs), 0) + b"\0" * 124
    body = head[:156] + struct.pack(">I", len(chunk)) + chunk
    body = body[:4] + struct.pack(">I", len(body) - 8) + body[8:]
    open(path, "wb").write(body)


LEVELS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cc0_levels.json")
LEVELS = {}
if os.path.exists(LEVELS_FILE) and "--no-levels" not in sys.argv:
    import json
    LEVELS = json.load(open(LEVELS_FILE))

GROUPS = [("010 - CC0 Keys.fxb", ("Keys", "Plucks", "Mallets", "Bells", "Guitars", "Organs")),
          ("011 - CC0 Bass+Lead.fxb", ("Basses", "Leads")),
          ("012 - CC0 Pads+FX.fxb", ("Pads", "Strings", "Brass", "Winds", "Soundscapes", "FX", "Percussion", "Drums"))]


def selftest():
    # forward-map a few OB-Xd patches with OB-Xf's importer formulas, then check the inverse returns them
    import random
    random.seed(3)
    for _ in range(200):
        x = random.random()
        assert abs(inv_logsc(logsc(x, 3.0, 10.0), 3.0, 10.0) - x) < 1e-6
        ms = logsc(x, 4.0, 60000.0, 900.0)
        assert abs(inv_logsc(ms, 4.0, 60000.0, 900.0) - x) < 1e-6
        assert abs(inv_logsc(logsc(x, 0.0, 1.0, 35.0), 0.0, 1.0, 35.0) - x) < 1e-6
        assert abs(inv_linsc(2.0 + x * 10.0, 2.0, 12.0) - x) < 1e-6
    for octv in range(4):                                           # OB-Xd octave -> OB-Xf transpose -> back
        t_norm = (min(4, round(octv) + 1)) * 0.25
        a = {"Transpose": str(t_norm)}
        v, why = xf_to_xd(a)
        assert why is None and abs(v[P["OCTAVE"]] * 4 - octv) < 1e-6, (octv, v and v[P["OCTAVE"]], why)
    v, why = xf_to_xd({})
    assert why is None
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    src, out = sys.argv[1], sys.argv[2]
    pats = sorted(glob.glob(os.path.join(src, "assets", "installer", "**", "Patches", "**", "*.fxp"), recursive=True))
    ok, skipped = [], {}
    for f in pats:
        a = read_xf_patch(f)
        if "CC0" not in a.get("license", ""):
            skipped[f] = "license is not CC0"
            continue
        v, why = xf_to_xd(a)
        if v is None:
            skipped[f] = why
            continue
        ok.append((a.get("category", ""), unent(a.get("programName", os.path.basename(f))), unent(a.get("author", "")), v))
    os.makedirs(out, exist_ok=True)
    credits = ["# CC0 patches: who made them\n",
               "These patches come from the factory patch set of [OB-Xf](https://github.com/surge-synthesizer/OB-Xf) (Surge Synth Team), where every one is marked "
               "`CC0 / Public Domain` in its own file. They were converted to OB-Xd's bank format by `tools/convert_obxf_patches.py` "
               "(the inverse of OB-Xf's own OB-Xd importer), with two changes for the MPC: the voice count stops at 10 (5 with unison) so the CPU keeps up, and each "
               "patch's Volume is set so they play at a similar level without clipping (`tools/make_cc0_levels.py`). CC0 asks for no credit; it is given here anyway.\n"]
    for fname, cats in GROUPS:
        sel = sorted((p for p in ok if p[0] in cats), key=lambda p: (cats.index(p[0]), p[1].lower()))
        sel = sel[:128]
        lv = LEVELS.get(fname)
        if lv and len(lv) == len(sel):                       # loudness evened out by tools/make_cc0_levels.py
            sel = [(c, n, au, v[:P["VOLUME"]] + [lv[i]] + v[P["VOLUME"] + 1:]) for i, (c, n, au, v) in enumerate(sel)]
        write_bank(os.path.join(out, fname), [(n, v) for _, n, _, v in sel])
        credits.append("\n## %s (%d patches)\n\n| Patch | Author | Category |\n|---|---|---|\n" % (fname[:-4].split(" - ", 1)[1], len(sel)))
        credits.append("".join("| %s | %s | %s |\n" % (n.replace("|", "/"), au, c) for c, n, au, _ in sel))
    open(os.path.join(out, "CREDITS-CC0.md"), "w").write("".join(credits))
    print("converted %d of %d patches; skipped %d" % (len(ok), len(pats), len(skipped)))
    import collections
    print(collections.Counter(skipped.values()).most_common(8))


if __name__ == "__main__":
    main()
