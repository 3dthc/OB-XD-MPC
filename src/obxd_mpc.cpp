// OB-Xd 2.10 (GPLv3, discoDSP / 2Dat) as an mpc_engine_t, for the MPC OS VST2 wrapper.
// The DSP is the unmodified engine from reales/OB-Xd at tag 2.10 (see VENDORED.md).
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <cmath>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
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
    // The BROWSE page: a bank list and a patch grid. It looks at one bank (bb) and one page of its patches (ppage) without
    // loading anything; only a patch tap or the patch knob changes the sound.
    std::vector<std::vector<std::string> > names;   // every bank's patch names (what select_bank() would list), read once at start
    std::vector<int> cum;                           // patches before bank b, over all banks
    int bb = 0, ppage = 0;
    // The loader (LOAD BANK / LOAD PRESET on the BROWSE page): the same two lists show places and files instead of banks and patches
    struct FEnt { std::string name; bool dir; };
    std::string data_dir;                            // <plugin folder>/banks
    int fmode = 0;                                   // 0 patches, 1 pick a bank file (.fxb), 2 pick a program file (.fxp)
    std::string cwd, note;                           // the folder being looked at; the last result ("ADDED: ...")
    std::vector<FEnt> ents;
    int fpage = 0;
    std::vector<std::pair<std::string, std::string> > roots;   // label, path
};
static const int BK_TILES = 8, PT_TILES = 24;       // tiles on the BROWSE page: bank rows, patch grid cells

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

// The same for a BROWSE tile, which is wider: up to 18 characters, so it stays inside the tile
static int fit_tile(char *buf, int n, const std::string &name) {
    if (name.size() <= 18) return snprintf(buf, n, "%s", name.c_str());
    return snprintf(buf, n, "%.16s..", name.c_str());
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
    s->bb = s->bank;                                       // the BROWSE page follows what is playing
    s->ppage = s->patch / PT_TILES;
    s->rev++;
}

// BROWSE: look at bank b (no sound change); the grid shows the playing patch's page when that is the bank being played
void browse_bank(Inst *s, int b) {
    int n = (int)s->banks.size();
    if (!n) return;
    b = b < 0 ? 0 : (b >= n ? n - 1 : b);
    s->bb = b;
    s->ppage = (b == s->bank && !s->patches.empty()) ? s->patch / PT_TILES : 0;
    s->rev++;
}

int bank_patches(Inst *s, int b) { return (b >= 0 && b < (int)s->names.size()) ? (int)s->names[b].size() : 0; }

// BROWSE: play patch idx of bank b. A bank change loads that bank's list first.
void play_patch(Inst *s, int b, int idx) {
    if (b < 0 || b >= (int)s->banks.size()) return;
    if (b != s->bank || s->patches.empty()) select_bank(s, b);
    load_patch(s, idx);
}

// BROWSE patch knob: one running number through every patch of every bank, so it carries on into the next bank at the end of a list
void scroll_patch(Inst *s, int i) {                          // i = position inside the bank being looked at; never leaves it
    int n = bank_patches(s, s->bb);
    if (n <= 0) return;
    i = i < 0 ? 0 : (i >= n ? n - 1 : i);
    if (s->bb == s->bank && i == s->patch) return;
    play_patch(s, s->bb, i);
}

// Every bank: the shipped ones, yours in my-banks, and the loose programs in my-banks/presets as "My Presets"
std::string my_banks_dir(Inst *s) {
    size_t k = s->data_dir.rfind('/');
    return k == std::string::npos ? std::string() : s->data_dir.substr(0, k) + "/my-banks";
}

void scan_all(Inst *s) {
    s->banks = obxdbank::scan_dir(s->data_dir.c_str());               // <plugin folder>/banks: shipped with the plugin, replaced on every install
    std::string mb = my_banks_dir(s);                                  // <plugin folder>/my-banks: yours, kept across upgrades
    if (!mb.empty()) {
        std::vector<obxdbank::BankFile> mine = obxdbank::scan_dir(mb.c_str());
        s->banks.insert(s->banks.end(), mine.begin(), mine.end());
        obxdbank::BankFile pb;
        if (obxdbank::presets_bank(mb, pb)) s->banks.push_back(pb);
    }
    s->names.clear();
    for (size_t b = 0; b < s->banks.size(); b++) {                    // every bank's patch names, for the BROWSE page
        std::vector<obxdbank::Patch> all;
        std::vector<std::string> nm, all_nm;
        if (obxdbank::load_bank(s->banks[b].path, PARAM_COUNT, all)) {
            for (size_t i = 0; i < all.size(); i++) {
                std::string t = tidy_name(all[i].name);
                all_nm.push_back(t);
                if (!unnamed(t)) nm.push_back(t);
            }
        }
        s->names.push_back(nm.empty() ? all_nm : nm);          // the same list select_bank() makes
    }
    s->cum.assign(1, 0);
    for (size_t b = 0; b < s->names.size(); b++) s->cum.push_back(s->cum.back() + (int)s->names[b].size());
}

// ---- the loader ----
std::string parent_of(const std::string &p) {
    if (p.size() <= 1) return "/";
    size_t k = p.find_last_of('/');
    if (k == std::string::npos || k == 0) return "/";
    return p.substr(0, k);
}

void fb_roots(Inst *s) {                                                 // places to start from: those that exist on this device
    s->roots.clear();
    const char *cand[][2] = { {"INTERNAL", "/sdcard"}, {"USB / SD", "/media"}, {"MOUNTS", "/mnt"}, {"HOME", "/root"}, {"ALL FILES", "/"} };
    for (int i = 0; i < 5; i++) if (obxdbank::is_dir(cand[i][1])) s->roots.push_back(std::make_pair(std::string(cand[i][0]), std::string(cand[i][1])));
    std::string pf = parent_of(s->data_dir);                             // the plugin's own folder is a good place to look too
    if (!s->data_dir.empty() && obxdbank::is_dir(pf)) s->roots.insert(s->roots.begin(), std::make_pair(std::string("PLUGIN"), pf));
    if ((int)s->roots.size() > BK_TILES) s->roots.resize(BK_TILES);
}

static std::string lower_s(std::string x) { for (size_t i = 0; i < x.size(); i++) x[i] = (char)tolower((unsigned char)x[i]); return x; }

void fb_list(Inst *s) {                                                  // the folders and matching files of cwd
    s->ents.clear();
    s->fpage = 0;
    if (s->cwd != "/" && !s->cwd.empty()) s->ents.push_back(Inst::FEnt{"..", true});
    std::vector<std::string> dirs, files;
    DIR *d = opendir(s->cwd.c_str());
    if (d) {
        while (struct dirent *e = readdir(d)) {
            std::string n = e->d_name;
            if (n.empty() || n[0] == '.') continue;
            if (obxdbank::is_dir(s->cwd + (s->cwd == "/" ? "" : "/") + n)) dirs.push_back(n);
            else if (obxdbank::ends_with_nocase(n, s->fmode == 1 ? ".fxb" : ".fxp")) files.push_back(n);
        }
        closedir(d);
    }
    struct Ci { static bool lt(const std::string &a, const std::string &b) { return lower_s(a) < lower_s(b); } };
    std::sort(dirs.begin(), dirs.end(), Ci::lt);
    std::sort(files.begin(), files.end(), Ci::lt);
    for (size_t i = 0; i < dirs.size(); i++) s->ents.push_back(Inst::FEnt{dirs[i], true});
    for (size_t i = 0; i < files.size(); i++) s->ents.push_back(Inst::FEnt{files[i], false});
}

void fb_open(Inst *s, int mode) {
    s->fmode = mode < 0 ? 0 : (mode > 2 ? 2 : mode);
    s->note.clear();
    if (s->fmode) {
        if (s->cwd.empty() || !obxdbank::is_dir(s->cwd)) s->cwd = s->roots.empty() ? "/" : s->roots[0].second;
        fb_list(s);
    }
    s->rev++;
}

static bool copy_bytes(const std::string &data, const std::string &dst) {
    FILE *f = fopen(dst.c_str(), "wb");
    if (!f) return false;
    bool ok = fwrite(data.data(), 1, data.size(), f) == data.size();
    ok = (fclose(f) == 0) && ok;
    return ok;
}

// Copy the picked file into my-banks (banks) or my-banks/presets (programs), so it is there for good, then look at it.
void fb_import(Inst *s, const std::string &path, const std::string &base) {
    bool preset = s->fmode == 2;
    std::string mb = my_banks_dir(s);
    if (mb.empty()) { s->note = "NO MY-BANKS FOLDER"; return; }
    std::string data;
    if (!obxdbank::read_file(path, data)) { s->note = "CANNOT READ FILE"; return; }
    if (preset) { obxdbank::Patch t; if (!obxdbank::load_fxp(path, PARAM_COUNT, t)) { s->note = "NOT AN OB-XD PRESET"; return; } }
    else { std::vector<obxdbank::Patch> t; if (!obxdbank::load_bank(path, PARAM_COUNT, t)) { s->note = "NOT AN OB-XD BANK"; return; } }
    std::string dir = preset ? mb + "/presets" : mb;
    mkdir(mb.c_str(), 0755);
    if (preset) mkdir(dir.c_str(), 0755);
    std::string stem = base.substr(0, base.size() - 4), ext = base.substr(base.size() - 4), dst = dir + "/" + base;
    for (int n = 2; ; n++) {
        std::string old;
        if (!obxdbank::read_file(dst, old)) break;                       // free name
        if (old == data) { s->note = "ALREADY ADDED"; return; }
        if (n > 99) { s->note = "TOO MANY COPIES"; return; }
        char sfx[16];
        snprintf(sfx, sizeof sfx, "-%d", n);
        dst = dir + "/" + stem + sfx + ext;
    }
    if (!copy_bytes(data, dst)) { s->note = "CANNOT WRITE (READ-ONLY?)"; return; }
    std::string keep = (s->banks.empty() ? std::string() : s->banks[s->bank].path);
    scan_all(s);                                                          // the bank list now has it
    s->bank = 0;
    for (size_t b = 0; b < s->banks.size(); b++) if (s->banks[b].path == keep) s->bank = (int)b;
    if (!s->banks.empty() && s->banks[s->bank].path == mb + "/presets") {   // the playing bank grew: refresh its list, same patch
        int p = s->patch;
        select_bank(s, s->bank);
        s->patch = p >= (int)s->patches.size() ? 0 : p;
    }
    std::string label = stem.size() > 16 ? stem.substr(0, 14) + ".." : stem;
    s->note = "ADDED: " + label;
    for (size_t b = 0; b < s->banks.size(); b++) {
        if (preset && s->banks[b].path == mb + "/presets") {              // a new program: play it
            std::vector<std::string> fl = obxdbank::list_ext(mb + "/presets", ".fxp");
            int idx = 0;
            for (size_t i = 0; i < fl.size(); i++) if (fl[i] == dst.substr(dst.rfind('/') + 1)) idx = (int)i;
            if (idx >= (int)s->names[b].size()) idx = 0;
            play_patch(s, (int)b, idx);
            s->bb = (int)b;
            s->ppage = idx / PT_TILES;
        } else if (!preset && s->banks[b].path == dst) {
            s->bb = (int)b;
            s->ppage = 0;
        }
    }
    s->rev++;
}

void fb_tap(Inst *s, int k) {                                            // tile k (0-based) of the file list
    int idx = s->fpage * PT_TILES + k;
    if (idx < 0 || idx >= (int)s->ents.size()) return;
    const Inst::FEnt &e = s->ents[idx];
    s->note.clear();
    if (e.dir) {
        s->cwd = e.name == ".." ? parent_of(s->cwd) : s->cwd + (s->cwd == "/" ? "" : "/") + e.name;
        fb_list(s);
        s->rev++;
        return;
    }
    fb_import(s, s->cwd + (s->cwd == "/" ? "" : "/") + e.name, e.name);
}


void *create(const char *data_dir) {
    Inst *s = new Inst();
    memset(s->vals, 0, sizeof s->vals);
    s->synth.setSampleRate(44100.0f);
    for (int i = 0; i < kObxdParamCount; i++) {
        apply(s, kObxdParams[i].id, kObxdParams[i].def);
    }
    s->data_dir = data_dir ? data_dir : "";
    scan_all(s);
    fb_roots(s);
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
    if (!strcmp(key, "load_mode")) { fb_open(s, atoi(val)); return; }                                 // the LOAD drop-down: PATCHES / LOAD BANK / LOAD PRESET
    if (s->fmode && (!strcmp(key, "bk_scroll") || !strcmp(key, "pt_scroll"))) return;               // the knobs rest while a file list is up
    if (!strcmp(key, "bk_scroll")) { browse_bank(s, (int)(atof(val) + 0.5) - 1); return; }        // BROWSE bank knob: look only
    if (!strcmp(key, "pt_scroll")) { scroll_patch(s, (int)(atof(val) + 0.5) - 1); return; }      // BROWSE patch knob: plays
    if (!strncmp(key, "bk_", 3) || !strncmp(key, "pt_", 3)) {                                      // BROWSE tiles and page arrows
        if (atof(val) < 0.5) return;                                                               // a tap, not its release
        int k = atoi(key + 3);
        if (s->fmode) {                                                                            // file list: places on the left, files on the right
            if (!strncmp(key, "bk_", 3) && k >= 1 && k <= (int)s->roots.size()) { s->cwd = s->roots[k - 1].second; s->note.clear(); fb_list(s); s->rev++; }
            else if (!strncmp(key, "pt_", 3) && k >= 1 && k <= PT_TILES) fb_tap(s, k - 1);
            else if (!strcmp(key, "pt_pg_prev")) { if (s->fpage > 0) { s->fpage--; s->rev++; } }
            else if (!strcmp(key, "pt_pg_next")) { if ((s->fpage + 1) * PT_TILES < (int)s->ents.size()) { s->fpage++; s->rev++; } }
            return;
        }
        if (!strncmp(key, "bk_", 3) && k >= 1 && k <= BK_TILES) browse_bank(s, (s->bb / BK_TILES) * BK_TILES + k - 1);
        else if (!strncmp(key, "pt_", 3) && k >= 1 && k <= PT_TILES) {
            int idx = s->ppage * PT_TILES + k - 1;
            if (idx < bank_patches(s, s->bb)) play_patch(s, s->bb, idx);
        } else if (!strcmp(key, "pt_pg_prev")) { if (s->ppage > 0) { s->ppage--; s->rev++; } }
        else if (!strcmp(key, "pt_pg_next")) { if ((s->ppage + 1) * PT_TILES < bank_patches(s, s->bb)) { s->ppage++; s->rev++; } }
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
    if (!strcmp(key, "bk_scroll")) return snprintf(buf, n, "%d", s->bb + 1);
    if (!strcmp(key, "pt_scroll")) return snprintf(buf, n, "%d", s->bb == s->bank ? s->patch + 1 : 1);
    if (!strcmp(key, "load_mode")) return snprintf(buf, n, "%d", s->fmode);
    if (!strcmp(key, "ui_cap_theme")) return snprintf(buf, n, "THEME");                              // static captions, drawn as live text so they can be sized
    if (!strcmp(key, "ui_cap_page")) return snprintf(buf, n, "PAGE");
    if (!strncmp(key, "br_", 3)) {                                                                 // the BROWSE page's own titles and displays
        if (!strcmp(key, "br_bank_title")) return snprintf(buf, n, "%s", s->fmode ? "PLACES" : "BANKS");
        if (!strcmp(key, "br_patch_title")) return snprintf(buf, n, "%s", s->fmode == 1 ? "BANK FILES (.FXB)" : s->fmode == 2 ? "PRESET FILES (.FXP)" : "PATCHES");
        if (!strcmp(key, "br_bank_cap")) return snprintf(buf, n, "%s", s->fmode ? "TAP A FILE TO ADD IT" : "PLAYING BANK");
        if (!strcmp(key, "br_patch_cap")) return snprintf(buf, n, "%s", s->fmode ? (s->note.empty() ? "FOLDER" : "RESULT") : "PLAYING PATCH");
        if (!strcmp(key, "br_bank")) {
            if (s->fmode) return snprintf(buf, n, "%s", s->fmode == 1 ? "LOAD BANK" : "LOAD PRESET");
            return get_param(p, "bank_name", buf, n);
        }
        if (!strcmp(key, "br_patch")) {
            if (!s->fmode) return get_param(p, "patch_name", buf, n);
            if (!s->note.empty()) return snprintf(buf, n, "%s", s->note.c_str());
            if (s->cwd.size() <= 30) return snprintf(buf, n, "%s", s->cwd.c_str());
            return snprintf(buf, n, "..%s", s->cwd.c_str() + s->cwd.size() - 28);
        }
        return -1;
    }
    if (!strcmp(key, "pt_page")) {
        if (s->fmode) {
            int tot = (int)s->ents.size(), pages = tot > 0 ? (tot + PT_TILES - 1) / PT_TILES : 1;
            return snprintf(buf, n, "%d / %d", s->fpage + 1, pages);
        }
        int tot = bank_patches(s, s->bb), pages = tot > 0 ? (tot + PT_TILES - 1) / PT_TILES : 1;
        return snprintf(buf, n, "%d / %d", s->ppage + 1, pages);
    }
    if (!strncmp(key, "bk_", 3) || !strncmp(key, "pt_", 3)) {                                      // BROWSE tiles: text, and "_on" = lit
        int k = atoi(key + 3);
        bool on = strlen(key) > 3 && !strcmp(key + strlen(key) - 3, "_on");
        if (s->fmode && !strncmp(key, "bk_", 3) && k >= 1 && k <= BK_TILES) {
            if (k > (int)s->roots.size()) return on ? snprintf(buf, n, "0") : snprintf(buf, n, " ");
            if (!on) return fit_tile(buf, n, s->roots[k - 1].first);
            int best = -1; size_t bl = 0;                                                          // lit: the place cwd is under (the deepest match)
            for (size_t r = 0; r < s->roots.size(); r++) {
                const std::string &rp = s->roots[r].second;
                bool under = s->cwd == rp || (s->cwd.compare(0, rp.size() + (rp == "/" ? 0 : 1), rp + (rp == "/" ? "" : "/")) == 0);
                if (under && rp.size() >= bl) { best = (int)r; bl = rp.size(); }
            }
            return snprintf(buf, n, "%d", best == k - 1 ? 1 : 0);
        }
        if (s->fmode && !strncmp(key, "pt_", 3) && k >= 1 && k <= PT_TILES) {
            int idx = s->fpage * PT_TILES + k - 1;
            if (on) return snprintf(buf, n, "0");
            if (idx >= (int)s->ents.size()) return snprintf(buf, n, " ");
            const Inst::FEnt &e = s->ents[idx];
            if (e.dir && e.name == "..") return snprintf(buf, n, "^ UP");
            return fit_tile(buf, n, e.dir ? "> " + e.name : e.name);
        }
        if (!strncmp(key, "bk_", 3) && k >= 1 && k <= BK_TILES) {
            int b = (s->bb / BK_TILES) * BK_TILES + k - 1;
            if (on) return snprintf(buf, n, "%d", b == s->bb ? 1 : 0);
            if (b < (int)s->banks.size()) return fit_tile(buf, n, s->banks[b].label);
            return snprintf(buf, n, " ");
        }
        if (!strncmp(key, "pt_", 3) && k >= 1 && k <= PT_TILES) {
            int idx = s->ppage * PT_TILES + k - 1;
            if (on) return snprintf(buf, n, "%d", (s->bb == s->bank && idx == s->patch) ? 1 : 0);
            if (idx < bank_patches(s, s->bb)) return fit_tile(buf, n, s->names[s->bb][idx]);
            return snprintf(buf, n, " ");
        }
        return on ? -1 : snprintf(buf, n, "0");                                                    // the page arrows
    }
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
