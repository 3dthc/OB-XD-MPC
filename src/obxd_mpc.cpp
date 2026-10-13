// OB-Xd 2.10 (GPLv3, discoDSP / 2Dat) as an mpc_engine_t, for the MPC OS VST2 wrapper.
// The DSP is the unmodified engine from reales/OB-Xd at tag 2.10 (see VENDORED.md).
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <cmath>
#include <string.h>
extern "C" {
#include "engine.h"
}
#include "obxd/SynthEngine.h"
#include "obxd_dispatch.h"
#include "obxd_banks.h"

namespace {
struct Inst {
    SynthEngine synth;
    float vals[PARAM_COUNT];
    float hz = 440.f;          // A4 reference (master_hz), applied as a semitone offset on top of the Tune knob
    int pbend14 = 8192;
    // banks: the .fxb files in <plugin folder>/banks, parsed one at a time when picked
    std::vector<obxdbank::BankFile> banks;
    std::vector<obxdbank::Patch> patches;    // the current bank's patches (unnamed "Default" ones left out)
    int bank = 0, patch = 0;
    int theme = 0;                           // the panel's colour theme (the THEME option on the MORE page); the skin swaps pictures, the engine just remembers it
    double bpm = 0;                          // host tempo ("lfo_bpm"; 0 = not told yet, 120 is used)
    double secs = 0;                         // seconds since the transport last started (free-running when stopped)
    int rev = 1;                             // bumped when a bank or patch loads, so the wrapper redraws every control
};

// The panel shows voice count (8 digits) and legato mode (4 labels) as pictures: snap the engine to the same
// step the picture shows, so what is displayed is what plays.
// OB-Xd's Tune is processTune(p): oscillator pitch offset = p*2-1 semitones. A reference of hz Hz is
// 12*log2(hz/440) semitones, i.e. +semis/2 on p. processTune does no clamping, so p may leave 0..1.
void apply_tune(Inst *s) {
    float semis = 12.f * log2f(s->hz / 440.f);
    s->synth.processTune(s->vals[TUNE] + semis * 0.5f);
}

void apply(Inst *s, int id, float f) {
    s->vals[id] = f;
    if (id == TUNE) { apply_tune(s); return; }
    if (id == VOICE_COUNT) { int n = (int)(f * 8.f); n = n < 0 ? 0 : (n > 7 ? 7 : n); f = n / 7.f; }
    else if (id == LEGATOMODE) { int n = (int)(f * 4.f); n = n < 0 ? 0 : (n > 3 ? 3 : n); f = n / 3.f; }
    obxd_dispatch(s->synth, id, f);
}

int find_key(const char *key) {
    for (int i = 0; i < kObxdParamCount; i++) if (!strcmp(kObxdParams[i].key, key)) return i;
    return -1;
}

// A name for the display: at most 14 characters so it stays inside its box; a longer one ends in ".."
static int fit_name(char *buf, int n, const std::string &name) {
    if (name.size() <= 14) return snprintf(buf, n, "%s", name.c_str());
    return snprintf(buf, n, "%.12s..", name.c_str());
}

std::string tidy_name(std::string n) {
    size_t k = n.find("Pusler");                           // a typo in discoDSP's own factory bank
    if (k != std::string::npos) n.replace(k, 6, "Pulser");
    while (!n.empty() && (n.back() == ' ' || n.back() == '\t')) n.pop_back();
    return n;
}

bool unnamed(const std::string &n) {
    std::string t;
    for (size_t i = 0; i < n.size(); i++) t += (char)tolower((unsigned char)n[i]);
    while (!t.empty() && t.back() == ' ') t.pop_back();
    return t.empty() || t == "default" || t == "init";
}

// Parse bank number b (clamped) and make its named patches the current list. Does not change the sound.
void select_bank(Inst *s, int b) {
    int n = (int)s->banks.size();
    s->patches.clear();
    if (n == 0) { s->bank = 0; return; }
    b = b < 0 ? 0 : (b >= n ? n - 1 : b);
    s->bank = b;
    std::vector<obxdbank::Patch> all;
    if (!obxdbank::load_bank(s->banks[b].path, PARAM_COUNT, all)) return;
    for (size_t i = 0; i < all.size(); i++) {
        all[i].name = tidy_name(all[i].name);
        if (!unnamed(all[i].name)) s->patches.push_back(all[i]);
    }
    if (s->patches.empty()) s->patches = all;              // a bank of unnamed patches: show them all
}

void load_patch(Inst *s, int idx) {
    int n = (int)s->patches.size();
    if (n == 0) return;
    idx = idx < 0 ? 0 : (idx >= n ? n - 1 : idx);
    s->patch = idx;
    const obxdbank::Patch &p = s->patches[idx];
    for (int i = 0; i < kObxdParamCount; i++) {
        int id = kObxdParams[i].id;
        float v = (id >= 0 && id < (int)p.v.size() && !std::isnan(p.v[id])) ? p.v[id] : kObxdParams[i].def;
        if (id == VOICE_COUNT && !p.voice_count_new) v *= 0.25f;     // 1.x banks store 0..1 steps of 4
        v = v < 0 ? 0 : (v > 1 ? 1 : v);
        apply(s, id, v);
    }
    s->synth.allNotesOff();
    s->rev++;
}

void *create(const char *data_dir) {
    Inst *s = new Inst();
    memset(s->vals, 0, sizeof s->vals);
    s->synth.setSampleRate(44100.0f);
    for (int i = 0; i < kObxdParamCount; i++) {
        apply(s, kObxdParams[i].id, kObxdParams[i].def);
    }
    s->banks = obxdbank::scan_dir(data_dir);                    // <plugin folder>/banks: shipped with the plugin, replaced on every install
    {
        std::string dd = data_dir ? data_dir : "";               // <plugin folder>/my-banks: yours, kept across upgrades
        size_t k = dd.rfind('/');
        if (k != std::string::npos) {
            std::vector<obxdbank::BankFile> mine = obxdbank::scan_dir((dd.substr(0, k) + "/my-banks").c_str());
            s->banks.insert(s->banks.end(), mine.begin(), mine.end());
        }
    }
    if (!s->banks.empty()) { select_bank(s, 0); load_patch(s, 0); }
    return s;
}
void destroy(void *p) { delete (Inst *)p; }

void midi(void *p, const uint8_t *m, int len) {
    Inst *s = (Inst *)p;
    if (len < 2) return;
    int st = m[0] & 0xF0, d1 = m[1], d2 = len > 2 ? m[2] : 0;
    switch (st) {
    case 0x90: if (d2) s->synth.procNoteOn(d1, d2 / 127.0f); else s->synth.procNoteOff(d1); break;
    case 0x80: s->synth.procNoteOff(d1); break;
    case 0xE0: s->synth.procPitchWheel((((d2 << 7) | d1) - 8192) / 8192.0f); break;
    case 0xB0:
        if (d1 == 1) s->synth.procModWheel(d2 / 127.0f);
        else if (d1 == 64) { if (d2 >= 64) s->synth.sustainOn(); else s->synth.sustainOff(); }
        else if (d1 == 123) s->synth.allNotesOff();
        else if (d1 == 120) s->synth.allSoundOff();
        break;
    default: break;
    }
}

void set_param(void *p, const char *key, const char *val) {
    Inst *s = (Inst *)p;
    if (!strcmp(key, "stop")) {                            // STOP button: panic (all notes off, all sound off)
        if (atof(val) > 0.5) s->synth.allSoundOff();
        return;
    }
    if (!strcmp(key, "bank") || !strcmp(key, "patch") || !strncmp(key, "bank_", 5) || !strncmp(key, "patch_", 6)) {
        int nb = (int)s->banks.size(), np = (int)s->patches.size();
        int v = (int)(atof(val) + 0.5) - 1;                  // the controls count from 1
        if (!strcmp(key, "bank")) {
            if (nb && v != s->bank) { select_bank(s, v); load_patch(s, 0); }
        } else if (!strcmp(key, "patch")) {
            if (np && v != s->patch) load_patch(s, v);
        } else if (atof(val) > 0.5) {                       // arrows: step and wrap around
            if (!strcmp(key, "bank_next") && nb) { select_bank(s, (s->bank + 1) % nb); load_patch(s, 0); }
            else if (!strcmp(key, "bank_prev") && nb) { select_bank(s, (s->bank + nb - 1) % nb); load_patch(s, 0); }
            else if (!strcmp(key, "patch_next") && np) load_patch(s, (s->patch + 1) % np);
            else if (!strcmp(key, "patch_prev") && np) load_patch(s, (s->patch + np - 1) % np);
        }
        return;
    }
    if (!strcmp(key, "theme")) {
        int t = atoi(val);
        s->theme = t < 0 ? 0 : (t > 3 ? 3 : t);
        return;
    }
    if (!strcmp(key, "lfo_bpm")) {
        double b = atof(val);
        if (fabs(b - s->bpm) > 0.05) s->rev++;                            // the TEMPO display follows the project tempo
        s->bpm = b;
        return;
    }          // the wrapper passes the host tempo (HAS_LFO_BPM)
    if (!strcmp(key, "transport")) {                                      // and play/stop (HAS_TRANSPORT)
        if (atoi(val)) s->secs = 0;                                       // play starts at the start of the synced LFO cycle
        return;
    }
    if (!strcmp(key, "master_hz")) {                       // in Hz, not 0..1
        float h = (float)atof(val);
        s->hz = h < 400.f ? 400.f : (h > 480.f ? 480.f : h);
        apply_tune(s);
        return;
    }
    int i = find_key(key);
    if (i < 0) return;
    float f = (float)atof(val);
    f = f < 0 ? 0 : (f > 1 ? 1 : f);
    apply(s, kObxdParams[i].id, f);
}

int get_param(void *p, const char *key, char *buf, int n) {
    Inst *s = (Inst *)p;
    if (!strcmp(key, "master_hz")) return snprintf(buf, n, "%.1f", s->hz);
    if (!strcmp(key, "stop")) return snprintf(buf, n, "0");
    if (!strcmp(key, "theme")) return snprintf(buf, n, "%d", s->theme);
    if (!strcmp(key, "tempo_text")) {
        if (s->bpm > 1.0) return snprintf(buf, n, "%.1f", s->bpm);
        return snprintf(buf, n, "---");
    }
    if (!strcmp(key, "display_rev")) return snprintf(buf, n, "%d", s->rev);
    if (!strcmp(key, "bank")) return snprintf(buf, n, "%d", s->bank + 1);
    if (!strcmp(key, "patch")) return snprintf(buf, n, "%d", s->patch + 1);
    if (!strncmp(key, "bank_", 5) || !strncmp(key, "patch_", 6)) {
        if (!strcmp(key, "bank_name")) {
            if (s->banks.empty()) return snprintf(buf, n, "no banks folder");
            return fit_name(buf, n, s->banks[s->bank].label);
        }
        if (!strcmp(key, "patch_name")) {
            if (s->patches.empty()) return snprintf(buf, n, "-");
            return fit_name(buf, n, s->patches[s->patch].name);
        }
        return snprintf(buf, n, "0");                       // the arrows
    }
    if (!strncmp(key, "patch:", 6)) {                       // a patch's name without loading it (the PRESET menu)
        int k = atoi(key + 6) - 1;
        if (k >= 0 && k < (int)s->patches.size()) return snprintf(buf, n, "%s", s->patches[k].name.c_str());
        return snprintf(buf, n, "-");
    }
    int i = find_key(key);
    if (i < 0) return -1;
    return snprintf(buf, n, "%g", s->vals[kObxdParams[i].id]);
}

void render(void *p, int16_t *out, int frames) {
    Inst *s = (Inst *)p;
    // The synced LFO (LFO SYNC on the MORE page) follows the host tempo: tell the engine the tempo and where the LFO is, once per
    // block. Lfo::hostSyncRetrigger() sets phase = (bpm/60 * division) * position, so the position that gives exactly
    // "division cycles per beat" is the time in seconds (OB-Xd's own plugin passes quarter notes there, which makes the rate go
    // with the square of the tempo). Without a tempo from the host it runs at 120.
    double bpm = s->bpm > 1.0 ? s->bpm : 120.0;
    s->synth.setPlayHead((float)bpm, (float)s->secs);
    s->secs += frames / 44100.0;
    if (s->secs > 3600.0) s->secs -= 3600.0;                  // keep float precision; an hour is whole beats at nearly any tempo
    for (int i = 0; i < frames; i++) {
        float l = 0, r = 0;
        s->synth.processSample(&l, &r);
        l = l > 1.f ? 1.f : (l < -1.f ? -1.f : l);
        r = r > 1.f ? 1.f : (r < -1.f ? -1.f : r);
        out[2 * i] = (int16_t)(l * 32767.f);
        out[2 * i + 1] = (int16_t)(r * 32767.f);
    }
}
const mpc_engine_t g_engine = { create, destroy, midi, set_param, get_param, render, NULL };
} // namespace

extern "C" const mpc_engine_t *mpc_engine(void) { return &g_engine; }
