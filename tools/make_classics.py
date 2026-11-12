#!/usr/bin/env python3
"""Writes banks/018 - Classics.fxb: patches programmed from scratch for this plugin (not converted from anything), covering the
sounds people reach for on a polysynth that the OB-Xf set has little of: brass stabs and swells, string machines, PWM pads, acid
and sub basses, sync and portamento leads, and short plucks that suit the MPC's arpeggiator. Released under the plugin's licence.

usage: make_classics.py [--no-levels]      (levels come from tools/classics_levels.json, made by tools/make_classics_levels.py)
Not auditioned by ear: the values are set by hand from how the synth behaves; run the level audit and listen before relying on one.
"""
import json, os, sys
sys.argv_saved = list(sys.argv); sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a != "--no-levels"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_obxf_patches as c
P = c.P
HERE = os.path.dirname(os.path.abspath(__file__))
FILE = "018 - Classics.fxb"
LEVELS_FILE = os.path.join(HERE, "classics_levels.json")


def ms(x, lo=4.0):                 # a time in milliseconds -> envelope knob
    return c.inv_logsc(x, lo, 60000.0, 900.0)


def semi(n):                       # an oscillator pitch offset in semitones -> knob (centre = 0)
    return (24 + n) / 48.0


def base():
    v = list(c.INIT)
    v[P["OCTAVE"]] = 0.25; v[P["OSC1P"]] = v[P["OSC2P"]] = 0.5; v[P["PW"]] = 0.0; v[P["OSC2_DET"]] = 0.0
    v[P["UDET"]] = 0.25; v[P["VOICE_COUNT"]] = 2.5 / 8; v[P["VOLUME"]] = 0.5
    v[P["OSC1SAW"]] = v[P["OSC2SAW"]] = 1.0; v[P["OSC1PUL"]] = v[P["OSC2PUL"]] = 0.0
    v[P["OSC1MIX"]] = v[P["OSC2MIX"]] = 1.0; v[P["BRIGHT"]] = 1.0; v[P["CUTOFF"]] = 1.0; v[P["RESONANCE"]] = 0.0
    v[P["FOURPOLE"]] = 0.0; v[P["MULTIMODE"]] = 0.0; v[P["ENVAMT"]] = 0.0; v[P["FLT_KF"]] = 0.4
    v[P["LATK"]] = ms(5); v[P["LDEC"]] = ms(300); v[P["LSUS"]] = 1.0; v[P["LREL"]] = ms(250)
    v[P["FATK"]] = ms(1); v[P["FDEC"]] = ms(300); v[P["FSUS"]] = 0.0; v[P["FREL"]] = ms(250)
    v[P["ENVDER"]] = v[P["FILTERDER"]] = v[P["PORTADER"]] = 0.25
    v[P["BENDRANGE"]] = 0.0; v[P["LFOFREQ"]] = 0.0
    for i in range(8):
        v[P["PAN1"] + i] = 0.5 + (0.18 if i % 2 else -0.18) * (i // 2 + 1) / 4.0   # a little spread between voices
    return v


def patch(name, **kw):
    v = base()
    for k, x in kw.items():
        v[P[k]] = x
    return name, v


LFO_SIN = dict(LFOSIN=1.0)
PATCHES = [
    # --- brass -------------------------------------------------------------------------------------------------------------
    patch("Poly Brass Stab", OSC2_DET=0.14, FOURPOLE=1.0, CUTOFF=0.28, RESONANCE=0.1, ENVAMT=0.55, FATK=ms(45), FDEC=ms(420), FSUS=0.25,
          LATK=ms(18), LDEC=ms(500), LSUS=0.8, LREL=ms(160), UNISON=0.0, VFLTENV=0.2),
    patch("Soft Brass", OSC2_DET=0.1, FOURPOLE=1.0, CUTOFF=0.24, ENVAMT=0.4, FATK=ms(120), FDEC=ms(700), FSUS=0.4, LATK=ms(70), LSUS=1.0,
          LREL=ms(220), LFOFREQ=0.45, LFOSIN=1.0, LFOOSC1=1.0, LFOOSC2=1.0, LFO1AMT=0.04),
    patch("Brass Swell", OSC2_DET=0.16, FOURPOLE=1.0, CUTOFF=0.18, RESONANCE=0.08, ENVAMT=0.6, FATK=ms(900), FDEC=ms(1200), FSUS=0.5,
          LATK=ms(500), LREL=ms(500)),
    patch("Sforzando Brass", OSC2_DET=0.12, FOURPOLE=1.0, CUTOFF=0.2, ENVAMT=0.7, FATK=ms(25), FDEC=ms(900), FSUS=0.15, LATK=ms(12),
          LDEC=ms(1500), LSUS=0.7, LREL=ms(300), VFLTENV=0.4),
    patch("Octave Brass", OSC2P=semi(12), OSC2_DET=0.08, FOURPOLE=1.0, CUTOFF=0.3, ENVAMT=0.5, FATK=ms(60), FDEC=ms(500), FSUS=0.3,
          LATK=ms(20), LREL=ms(200)),
    patch("Detuned Stab", OSC2_DET=0.3, UNISON=1.0, UDET=0.3, VOICE_COUNT=1.5 / 8, FOURPOLE=1.0, CUTOFF=0.35, ENVAMT=0.45,
          FDEC=ms(260), FSUS=0.0, LDEC=ms(320), LSUS=0.0, LREL=ms(220)),
    patch("Organ Stab", OSC1SAW=0.0, OSC1PUL=1.0, OSC2SAW=0.0, OSC2PUL=1.0, OSC2P=semi(12), CUTOFF=0.6, ENVAMT=0.2, FDEC=ms(150), FSUS=0.0,
          LDEC=ms(260), LSUS=0.0, LREL=ms(120)),
    patch("Minor Chord Hit", OSC2_DET=0.2, FOURPOLE=1.0, CUTOFF=0.3, ENVAMT=0.5, FDEC=ms(350), FSUS=0.0, LDEC=ms(700), LSUS=0.0, LREL=ms(400),
          RESONANCE=0.15),
    # --- string machines and pads -----------------------------------------------------------------------------------------
    patch("String Machine", OSC2_DET=0.22, UNISON=0.0, CUTOFF=0.55, LATK=ms(350), LREL=ms(700), LFOFREQ=0.35, LFOSIN=1.0, LFOOSC1=1.0,
          LFOOSC2=1.0, LFO1AMT=0.03, OSC2P=semi(0)),
    patch("Analog Strings", OSC2_DET=0.28, CUTOFF=0.5, FOURPOLE=1.0, ENVAMT=0.15, FATK=ms(500), FDEC=ms(2000), FSUS=0.6, LATK=ms(280),
          LREL=ms(900)),
    patch("Warm Poly Pad", OSC2_DET=0.18, FOURPOLE=1.0, CUTOFF=0.32, RESONANCE=0.08, ENVAMT=0.3, FATK=ms(1100), FDEC=ms(2500), FSUS=0.5,
          LATK=ms(900), LREL=ms(1800), FLT_KF=0.5),
    patch("PWM Pad", OSC1SAW=0.0, OSC1PUL=1.0, OSC2SAW=0.0, OSC2PUL=1.0, OSC2_DET=0.15, PW=0.3, LFOFREQ=0.3, LFOSIN=1.0, LFOPW1=1.0,
          LFOPW2=1.0, LFO2AMT=0.6, CUTOFF=0.5, FOURPOLE=1.0, LATK=ms(700), LREL=ms(1500)),
    patch("Sweep Pad", OSC2_DET=0.2, FOURPOLE=1.0, CUTOFF=0.15, RESONANCE=0.35, ENVAMT=0.75, FATK=ms(2800), FDEC=ms(3500), FSUS=0.4,
          LATK=ms(1400), LREL=ms(2200)),
    patch("Glass Pad", OSC1SAW=0.0, OSC1PUL=1.0, OSC2P=semi(19), OSC2_DET=0.07, PW=0.2, CUTOFF=0.7, RESONANCE=0.12, LATK=ms(1500),
          LREL=ms(2500), LFOFREQ=0.25, LFOSIN=1.0, LFOFILTER=1.0, LFO1AMT=0.12),
    patch("Choir-ish Pad", OSC2_DET=0.1, MULTIMODE=0.5, BANDPASS=1.0, CUTOFF=0.45, RESONANCE=0.3, LATK=ms(900), LREL=ms(1400),
          LFOFREQ=0.3, LFOSIN=1.0, LFOOSC1=1.0, LFOOSC2=1.0, LFO1AMT=0.025),
    patch("Dark Drone", OSC1P=semi(-12), OSC2P=semi(-12), OSC2_DET=0.12, FOURPOLE=1.0, CUTOFF=0.2, RESONANCE=0.2, LATK=ms(2500),
          LREL=ms(3000), LFOFREQ=0.15, LFOSIN=1.0, LFOFILTER=1.0, LFO1AMT=0.2),
    # --- basses ---------------------------------------------------------------------------------------------------------
    patch("Sub Bass", OCTAVE=0.0, OSC1SAW=0.0, OSC1PUL=1.0, OSC2SAW=0.0, OSC2PUL=1.0, FOURPOLE=1.0, CUTOFF=0.25, FLT_KF=0.6, LATK=ms(3),
          LDEC=ms(400), LSUS=1.0, LREL=ms(90), VOICE_COUNT=0.5 / 8),
    patch("Acid Squelch", OCTAVE=0.0, OSC1SAW=1.0, OSC2MIX=0.0, FOURPOLE=1.0, CUTOFF=0.18, RESONANCE=0.7, ENVAMT=0.65, FDEC=ms(220),
          FSUS=0.0, LDEC=ms(500), LSUS=0.8, LREL=ms(80), VOICE_COUNT=0.5 / 8, LEGATOMODE=1.0, PORTAMENTO=0.12),
    patch("Fat Saw Bass", OCTAVE=0.0, OSC2_DET=0.12, OSC2P=semi(-12), FOURPOLE=1.0, CUTOFF=0.3, RESONANCE=0.15, ENVAMT=0.4, FDEC=ms(280),
          FSUS=0.2, LDEC=ms(600), LSUS=0.85, LREL=ms(120), VOICE_COUNT=0.5 / 8),
    patch("Pluck Bass", OCTAVE=0.0, OSC1SAW=0.0, OSC1PUL=1.0, PW=0.25, OSC2SAW=0.0, OSC2PUL=1.0, OSC2P=semi(-12), OSC2MIX=0.7, FOURPOLE=1.0, CUTOFF=0.2, ENVAMT=0.5, FDEC=ms(180),
          FSUS=0.0, LDEC=ms(260), LSUS=0.0, LREL=ms(100), VOICE_COUNT=0.5 / 8),
    patch("Rubber Bass", OCTAVE=0.0, OSC2_DET=0.06, FOURPOLE=1.0, CUTOFF=0.22, RESONANCE=0.4, ENVAMT=0.55, FDEC=ms(150), FSUS=0.1,
          LDEC=ms(350), LSUS=0.5, LREL=ms(90), VOICE_COUNT=0.5 / 8),
    # --- leads ----------------------------------------------------------------------------------------------------------
    patch("Sync Lead", OSC2P=semi(7), OSC2HS=1.0, OSC2_DET=0.0, CUTOFF=0.65, RESONANCE=0.1, ENVAMT=0.2, FDEC=ms(500), FSUS=0.3,
          ENVPITCH=0.12, ENV_PITCH_BOTH=0.0, FATK=ms(1), VOICE_COUNT=0.5 / 8, LFOFREQ=0.4, LFOSIN=1.0, LFOOSC1=1.0, LFOOSC2=1.0, LFO1AMT=0.03,
          LATK=ms(8), LREL=ms(150)),
    patch("Glide Lead", OSC2_DET=0.1, CUTOFF=0.6, RESONANCE=0.18, ENVAMT=0.25, FDEC=ms(400), FSUS=0.4, PORTAMENTO=0.3, LEGATOMODE=1.0,
          VOICE_COUNT=0.5 / 8, LATK=ms(6), LREL=ms(180), LFOFREQ=0.45, LFOSIN=1.0, LFOOSC1=1.0, LFOOSC2=1.0, LFO1AMT=0.035),
    patch("Fat Unison Lead", OSC2_DET=0.1, UNISON=1.0, UDET=0.35, VOICE_COUNT=1.5 / 8, FOURPOLE=1.0, CUTOFF=0.5, RESONANCE=0.12, ENVAMT=0.3,
          FDEC=ms(450), FSUS=0.4, LATK=ms(6), LREL=ms(200)),
    patch("Soft Square Lead", OSC1SAW=0.0, OSC1PUL=1.0, OSC2SAW=0.0, OSC2PUL=1.0, OSC2_DET=0.05, CUTOFF=0.4, FOURPOLE=1.0, ENVAMT=0.25,
          FDEC=ms(500), FSUS=0.5, LATK=ms(12), LREL=ms(220), VOICE_COUNT=0.5 / 8, LFOFREQ=0.4, LFOSIN=1.0, LFOOSC1=1.0, LFOOSC2=1.0, LFO1AMT=0.03),
    # --- short sounds that work with the arpeggiator ----------------------------------------------------------------------------
    patch("Arp Pluck", OSC2_DET=0.08, FOURPOLE=1.0, CUTOFF=0.3, RESONANCE=0.1, ENVAMT=0.5, FDEC=ms(170), FSUS=0.0, LDEC=ms(260), LSUS=0.0,
          LREL=ms(120)),
    patch("Arp Square", OSC1SAW=0.0, OSC1PUL=1.0, OSC2SAW=0.0, OSC2PUL=1.0, OSC2P=semi(12), CUTOFF=0.4, FOURPOLE=1.0, ENVAMT=0.4, FDEC=ms(140),
          FSUS=0.0, LDEC=ms(220), LSUS=0.0, LREL=ms(110)),
    patch("Arp Bell", OSC1SAW=0.0, OSC1PUL=1.0, OSC2SAW=0.0, OSC2PUL=1.0, OSC2P=semi(19), XMOD=0.4, CUTOFF=0.8, RESONANCE=0.1, LDEC=ms(900),
          LSUS=0.0, LREL=ms(700), FDEC=ms(400), FSUS=0.0, ENVAMT=0.2),
    patch("Arp Saw Stab", OSC2_DET=0.12, FOURPOLE=1.0, CUTOFF=0.4, ENVAMT=0.4, FDEC=ms(110), FSUS=0.0, LDEC=ms(180), LSUS=0.0, LREL=ms(100)),
    patch("Clav Pluck", OSC1SAW=0.0, OSC1PUL=1.0, PW=0.35, OSC2MIX=0.0, CUTOFF=0.35, RESONANCE=0.12, ENVAMT=0.45, FDEC=ms(130), FSUS=0.0,
          LDEC=ms(230), LSUS=0.0, LREL=ms(90), FLT_KF=0.6),
    patch("Pulse Keys", OSC1SAW=0.0, OSC1PUL=1.0, PW=0.15, OSC2SAW=1.0, OSC2MIX=0.4, OSC2_DET=0.06, CUTOFF=0.5, FOURPOLE=1.0, ENVAMT=0.3,
          FDEC=ms(500), FSUS=0.1, LDEC=ms(900), LSUS=0.3, LREL=ms(260)),
    # --- effects ---------------------------------------------------------------------------------------------------------
    patch("Laser Zap", OSC2_DET=0.0, ENVPITCH=0.9, ENV_PITCH_BOTH=1.0, FDEC=ms(120), FSUS=0.0, CUTOFF=0.7, FENV_INVERT=0.0, LDEC=ms(260),
          LSUS=0.0, LREL=ms(100), VOICE_COUNT=0.5 / 8),
    patch("Wind Noise", OSC1MIX=0.0, OSC2MIX=0.0, NOISEMIX=0.8, MULTIMODE=0.5, BANDPASS=1.0, CUTOFF=0.5, RESONANCE=0.45, LATK=ms(1800),
          LREL=ms(2500), LFOFREQ=0.2, LFOSIN=1.0, LFOFILTER=1.0, LFO1AMT=0.35),
    patch("Riser", OSC2_DET=0.3, FOURPOLE=1.0, CUTOFF=0.1, RESONANCE=0.4, ENVAMT=0.9, FATK=ms(6000), FDEC=ms(8000), FSUS=1.0, LATK=ms(1500),
          LREL=ms(1200), NOISEMIX=0.15),
    patch("Sci-Fi Sweep", OSC2P=semi(7), OSC2_DET=0.25, XMOD=0.5, FOURPOLE=1.0, CUTOFF=0.2, RESONANCE=0.5, ENVAMT=0.6, FATK=ms(1500),
          FDEC=ms(2500), FSUS=0.2, LATK=ms(600), LREL=ms(1500), LFOFREQ=0.5, LFOSIN=1.0, LFOOSC2=1.0, LFO1AMT=0.1),
]


def main():
    names = [n for n, _ in PATCHES]
    assert len(set(names)) == len(names), "duplicate patch names"
    progs = [(n, list(v)) for n, v in PATCHES]
    if "--no-levels" not in sys.argv_saved and os.path.exists(LEVELS_FILE):
        lv = json.load(open(LEVELS_FILE))
        if len(lv) == len(progs):
            for (n, v), x in zip(progs, lv):
                v[P["VOLUME"]] = x
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "banks")
    c.write_bank(os.path.join(out, FILE), progs)
    print("%d patches -> %s" % (len(progs), os.path.join(out, FILE)))


if __name__ == "__main__":
    main()
