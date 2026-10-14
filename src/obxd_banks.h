// Reads OB-Xd .fxb preset banks (the format discoDSP's OB-Xd and the GPL builds save) for the MPC port.
// Header only, no JUCE. Two kinds exist in the wild:
//   FBCh  a "chunk" bank: JUCE binary XML (magic 0x21324356, size, text) with <program programName=".." Val_N=".."/>
//   FxBk  a plain VST2 bank: big-endian floats per program
// The parameter numbers (N) are OB-Xd's own enum (src/obxd/ParamsEnum.h).
#pragma once
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <dirent.h>
#include <string>
#include <vector>
#include <algorithm>
#include <sys/stat.h>

namespace obxdbank {

struct Patch {
    std::string name;
    std::vector<float> v;     // indexed by OB-Xd parameter number; NaN = not in the file
    bool voice_count_new;     // the bank stores voice count as a 1..32 voice count (2.x), not 0..1 (1.x)
};

struct BankFile {
    std::string path;
    std::string label;        // file name without the leading "000 - " and the extension
};

static inline uint32_t be32(const unsigned char *p) { return ((uint32_t)p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]; }
static inline uint32_t le32(const unsigned char *p) { return ((uint32_t)p[3] << 24) | (p[2] << 16) | (p[1] << 8) | p[0]; }

static inline bool read_file(const std::string &path, std::string &out) {
    FILE *f = fopen(path.c_str(), "rb");
    if (!f) return false;
    char buf[65536];
    size_t n;
    out.clear();
    while ((n = fread(buf, 1, sizeof buf, f)) > 0) {
        out.append(buf, n);
        if (out.size() > 64u * 1024 * 1024) { fclose(f); return false; }   // not a bank
    }
    fclose(f);
    return true;
}

static inline std::string decode_entities(const std::string &s) {
    if (s.find('&') == std::string::npos) return s;
    std::string o;
    for (size_t i = 0; i < s.size(); i++) {
        if (s[i] != '&') { o += s[i]; continue; }
        size_t e = s.find(';', i);
        if (e == std::string::npos || e - i > 8) { o += '&'; continue; }     // a bare & in a name
        std::string t = s.substr(i + 1, e - i - 1);
        if (t == "amp") o += '&';
        else if (t == "lt") o += '<';
        else if (t == "gt") o += '>';
        else if (t == "quot") o += '"';
        else if (t == "apos") o += '\'';
        else if (t.size() > 1 && t[0] == '#') {
            long c = t[1] == 'x' ? strtol(t.c_str() + 2, 0, 16) : strtol(t.c_str() + 1, 0, 10);
            o += (c > 0 && c < 256) ? (char)c : '?';
        } else { o += '&'; continue; }
        i = e;
    }
    return o;
}

// <program a="b" c="d" ...> starting at '<' of "<program ": fill name and values
static inline void parse_program(const std::string &x, size_t pos, size_t end, int nparams, Patch &p) {
    p.v.assign(nparams, __builtin_nanf(""));
    p.voice_count_new = false;
    size_t i = pos + 9;                                        // after "<program "
    while (i < end) {
        while (i < end && isspace((unsigned char)x[i])) i++;
        size_t k0 = i;
        while (i < end && x[i] != '=' && !isspace((unsigned char)x[i]) && x[i] != '>' && x[i] != '/') i++;
        std::string key = x.substr(k0, i - k0);
        if (i >= end || x[i] != '=') { if (i < end && (x[i] == '>' || x[i] == '/')) break; i++; continue; }
        i++;
        if (i >= end || (x[i] != '"' && x[i] != '\'')) continue;
        char q = x[i++];
        size_t v0 = i;
        while (i < end && x[i] != q) i++;
        std::string val = x.substr(v0, i - v0);
        i++;
        if (key == "programName") p.name = decode_entities(val);
        else if (key == "voiceCount") p.voice_count_new = true;
        else {
            const char *kp = key.c_str();
            if (!strncmp(kp, "Val_", 4)) kp += 4;              // old banks number the values without the prefix
            char *e = 0;
            long n = strtol(kp, &e, 10);
            if (e && *e == 0 && e != kp && n >= 0 && n < nparams) p.v[n] = (float)atof(val.c_str());
        }
    }
}

static inline bool is_dir(const std::string &path) {
    struct stat st;
    return stat(path.c_str(), &st) == 0 && S_ISDIR(st.st_mode);
}

static inline bool ends_with_nocase(const std::string &s, const char *suf);

// One program file (.fxp): "FPCh" (a chunk holding the same <discoDSP .../> state as a bank's programs) or "FxCk" (plain parameters)
static inline bool load_fxp(const std::string &path, int nparams, Patch &pr) {
    std::string d;
    if (!read_file(path, d) || d.size() < 60) return false;
    const unsigned char *b = (const unsigned char *)d.data();
    if (memcmp(b, "CcnK", 4)) return false;
    if (!memcmp(b + 8, "FPCh", 4)) {
        uint32_t csize = be32(b + 56);
        if (60 + (size_t)csize > d.size() || csize < 8 || le32(b + 60) != 0x21324356u) return false;
        size_t xe = 68 + (size_t)le32(b + 64);
        if (xe > 60 + (size_t)csize) xe = 60 + csize;
        std::string x = d.substr(68, xe - 68);
        size_t z = x.find('\0');
        if (z != std::string::npos) x.resize(z);
        size_t lt = x.find('<'), sp = x.find(' ', lt == std::string::npos ? 0 : lt);
        if (lt == std::string::npos || sp == std::string::npos) return false;
        std::string y = "<program " + x.substr(sp + 1);                    // parse_program() reads from after "<program "
        size_t e = y.find('>');
        parse_program(y, 0, e == std::string::npos ? y.size() : e, nparams, pr);
        if (pr.name.empty()) pr.name.assign((const char *)b + 28, strnlen((const char *)b + 28, 28));
        return true;
    }
    if (!memcmp(b + 8, "FxCk", 4)) {
        uint32_t np = be32(b + 24);
        if (np > 4096 || 56 + (size_t)np * 4 > d.size()) return false;
        pr.name.assign((const char *)b + 28, strnlen((const char *)b + 28, 28));
        pr.voice_count_new = true;
        pr.v.assign(nparams, __builtin_nanf(""));
        for (uint32_t j = 0; j < np && (int)j < nparams; j++) {
            uint32_t u = be32(b + 56 + 4 * j);
            float f;
            memcpy(&f, &u, 4);
            pr.v[j] = f;
        }
        return true;
    }
    return false;
}

static inline std::vector<std::string> list_ext(const std::string &dir, const char *ext) {
    std::vector<std::string> names;
    DIR *d = opendir(dir.c_str());
    if (!d) return names;
    while (struct dirent *e = readdir(d)) {
        std::string n = e->d_name;
        if (n.size() > 4 && n[0] != '.' && ends_with_nocase(n, ext)) names.push_back(n);
    }
    closedir(d);
    std::sort(names.begin(), names.end());
    return names;
}

static inline bool load_bank(const std::string &path, int nparams, std::vector<Patch> &out) {
    std::string d;
    out.clear();
    if (is_dir(path)) {                                        // a folder of .fxp programs is one bank ("My Presets")
        std::vector<std::string> fl = list_ext(path, ".fxp");
        for (size_t i = 0; i < fl.size(); i++) {
            Patch pr;
            if (load_fxp(path + "/" + fl[i], nparams, pr)) out.push_back(pr);
        }
        return !out.empty();
    }
    if (!read_file(path, d) || d.size() < 160) return false;
    const unsigned char *b = (const unsigned char *)d.data();
    if (memcmp(b, "CcnK", 4)) return false;
    if (!memcmp(b + 8, "FBCh", 4)) {
        uint32_t csize = be32(b + 156);
        if (160 + (size_t)csize > d.size() || csize < 8 || le32(b + 160) != 0x21324356u) return false;
        size_t xs = 168, xe = 168 + (size_t)le32(b + 164);
        if (xe > 160 + csize) xe = 160 + csize;
        std::string x = d.substr(xs, xe - xs);
        size_t z = x.find('\0');
        if (z != std::string::npos) x.resize(z);
        size_t p = 0;
        while ((p = x.find("<program ", p)) != std::string::npos) {
            size_t e = x.find('>', p);
            if (e == std::string::npos) break;
            Patch pr;
            parse_program(x, p, e, nparams, pr);
            out.push_back(pr);
            p = e;
        }
        return !out.empty();
    }
    if (!memcmp(b + 8, "FxBk", 4)) {
        int n = (int)be32(b + 24);
        size_t off = 156;
        for (int i = 0; i < n; i++) {
            if (off + 56 > d.size() || memcmp(b + off, "CcnK", 4)) break;
            uint32_t bsz = be32(b + off + 4), np = be32(b + off + 24);
            if (np > 4096 || off + 56 + (size_t)np * 4 > d.size()) break;
            Patch pr;
            pr.name.assign((const char *)b + off + 28, strnlen((const char *)b + off + 28, 28));
            pr.voice_count_new = true;
            pr.v.assign(nparams, __builtin_nanf(""));
            for (uint32_t j = 0; j < np && (int)j < nparams; j++) {
                uint32_t u = be32(b + off + 56 + 4 * j);
                float f;
                memcpy(&f, &u, 4);
                pr.v[j] = f;
            }
            out.push_back(pr);
            off += 8 + bsz;
        }
        return !out.empty();
    }
    return false;
}

static inline bool ends_with_nocase(const std::string &s, const char *suf) {
    size_t n = strlen(suf);
    if (s.size() < n) return false;
    for (size_t i = 0; i < n; i++) if (tolower((unsigned char)s[s.size() - n + i]) != suf[i]) return false;
    return true;
}

// banks/*.fxb sorted by file name (so a Q-Link position always means the same bank)
static inline std::vector<BankFile> scan_dir(const char *dir) {
    std::vector<BankFile> out;
    if (!dir || !*dir) return out;
    DIR *d = opendir(dir);
    if (!d) return out;
    std::vector<std::string> names;
    while (struct dirent *e = readdir(d)) {
        std::string n = e->d_name;
        if (n.size() > 4 && n[0] != '.' && ends_with_nocase(n, ".fxb")) names.push_back(n);
    }
    closedir(d);
    std::sort(names.begin(), names.end());
    for (size_t i = 0; i < names.size(); i++) {
        BankFile bf;
        bf.path = std::string(dir) + "/" + names[i];
        std::string l = names[i].substr(0, names[i].size() - 4);
        size_t k = 0;
        while (k < l.size() && isdigit((unsigned char)l[k])) k++;                 // "000 - Name" -> "Name"
        if (k > 0 && k < l.size()) {
            size_t m = k;
            while (m < l.size() && (l[m] == ' ' || l[m] == '-' || l[m] == '_')) m++;
            if (m < l.size()) l = l.substr(m);
        }
        bf.label = l;
        out.push_back(bf);
    }
    return out;
}

// <my-banks>/presets/*.fxp as one bank, if there are any
static inline bool presets_bank(const std::string &my_banks_dir, BankFile &bf) {
    std::string pd = my_banks_dir + "/presets";
    if (list_ext(pd, ".fxp").empty()) return false;
    bf.path = pd;
    bf.label = "My Presets";
    return true;
}

} // namespace obxdbank
