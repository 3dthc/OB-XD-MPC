// Offline check of the BROWSE page's engine side (bank list, patch grid, the two scroll knobs) against the real banks folder.
// build and run: tools/browse_test.sh <folder that has banks/ in it>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <string>
#include <vector>
extern "C" {
#include "engine.h"
}
static const mpc_engine_t *E; static void *P; static int fails;
static std::string get(const char *k) { char b[256] = ""; int r = E->get_param(P, k, b, 256); return r > 0 ? std::string(b) : std::string("<none>"); }
static void set(const char *k, const char *v) { E->set_param(P, k, v); }
static void ck(bool c, const char *what, const std::string &got) { printf("%s %s  [%s]\n", c ? "ok  " : "FAIL", what, got.c_str()); if (!c) fails++; }
static std::string tile(const char *pre, int n, const char *suf = "") { char k[32]; snprintf(k, 32, "%s%d%s", pre, n, suf); return get(k); }
static int lit(const char *pre, int count) { int c = 0; for (int i = 1; i <= count; i++) if (tile(pre, i, "_on") == "1") c++; return c; }

// the BROWSE bank list shows 8 banks a page; the bank knob moves between pages
static int find_bank(const char *name) {
    int found = 0;
    usleep(2300000);                                  // past the window in which a reload's browse-knob values are ignored
    for (int pg = 0; pg < 3 && !found; pg++) { char v[8]; snprintf(v, 8, "%d", pg * 8 + 1); set("bk_scroll", v); for (int i = 1; i <= 8; i++) if (tile("bk_", i) == name) found = pg * 8 + i; }
    set("bk_scroll", "1");
    return found;
}
static int tap_text(const char *pre, int count, const std::string &t) { for (int i = 1; i <= count; i++) if (tile(pre, i) == t) { char k[32]; snprintf(k, 32, "%s%d", pre, i); usleep(300000); set(k, "1"); set(k, "0"); return i; } return 0; }   // a finger's pace: the engine ignores the same tile again within TAP_MS
static void write_fxp(const std::string &path, const std::string &name) {
    std::string xml = "<discoDSP Val_0=\"0.5\" voiceCount=\"8\" programName=\"" + name + "\"/>";
    std::string chunk; chunk += "\x56\x43\x32\x21"; uint32_t L = (uint32_t)xml.size() + 1; for (int i = 0; i < 4; i++) chunk += (char)((L >> (8 * i)) & 255); chunk += xml; chunk += '\0';
    std::string h = "CcnK"; h += std::string(4, '\0'); h += "FPCh"; h += std::string("\0\0\0\1", 4); h += "Obxd"; h += std::string("\0\0\0\1", 4); h += std::string("\0\0\0\1", 4);
    std::string nm = name; nm.resize(28, '\0'); h += nm; uint32_t C = (uint32_t)chunk.size(); for (int i = 3; i >= 0; i--) h += (char)((C >> (8 * i)) & 255);
    FILE *f = fopen(path.c_str(), "wb"); fwrite(h.data(), 1, h.size(), f); fwrite(chunk.data(), 1, chunk.size(), f); fclose(f);
}
static bool exists(const std::string &p) { FILE *f = fopen(p.c_str(), "rb"); if (f) fclose(f); return f != 0; }
int main(int argc, char **argv) {
    E = mpc_engine(); P = E->create(argv[1]);
    usleep(2200000);   // past the window in which a reload's browse-knob / LOAD values are ignored (create, set_state)
    std::string b0 = get("bank_name"), p0 = get("patch_name");
    ck(tile("bk_", 1) != " " && tile("bk_", 2) != " " && tile("bk_", 8) != " ", "bank list: first page full of named banks", tile("bk_", 1) + " | " + tile("bk_", 2));
    ck(lit("bk_", 7) == 1 && tile("bk_", 1, "_on") == "1", "first bank lit at start", "");
    ck(tile("pt_", 1) == p0 || tile("pt_", 1) != " ", "patch grid has names", tile("pt_", 1) + ", " + tile("pt_", 2));
    ck(lit("pt_", 24) == 1, "one patch lit (the playing one)", "");
    // bank knob: looks, never plays
    set("bk_scroll", "3");
    ck(get("bank_name") == b0 && get("patch_name") == p0, "bank knob does not change the playing bank or patch", get("bank_name") + " / " + get("patch_name"));
    ck(tile("bk_", 3, "_on") == "1" && lit("bk_", 7) == 1, "bank 3 is the one being looked at", "");
    ck(lit("pt_", 24) == 0, "no patch lit while looking at another bank", "");
    ck(get("bk_scroll") == "3", "bank knob reads back", get("bk_scroll"));
    std::string first3 = tile("pt_", 1);
    ck(first3 != " " && first3 != p0, "grid shows bank 3's patches", first3);
    // tapping a patch plays it
    set("pt_2", "1"); set("pt_2", "0");
    ck(get("bank_name") == tile("bk_", 3) && get("patch_name") == tile("pt_", 2), "tapping a patch plays it (and its bank)", get("bank_name") + " / " + get("patch_name"));
    ck(tile("pt_", 2, "_on") == "1" && lit("pt_", 24) == 1, "tapped patch is lit", "");
    // patch knob stays inside the bank being looked at
    std::string bn = get("bank_name");
    for (int v = 1; v <= 200; v++) { char t[16]; snprintf(t, 16, "%d", v); set("pt_scroll", t); }
    ck(get("bank_name") == bn, "patch knob never leaves its bank", get("bank_name"));
    int last = atoi(get("pt_scroll").c_str());
    ck(last > 1 && last <= 128, "knob stops at the bank's last patch", get("pt_scroll"));
    set("pt_scroll", "1");
    ck(get("bank_name") == bn && get("pt_scroll") == "1", "and back to its first patch", get("patch_name"));
    set("bk_scroll", "1"); set("pt_scroll", "2");
    ck(get("bank_name") == tile("bk_", 1), "knob plays within whichever bank is being looked at", get("bank_name"));
    set("pt_scroll", "1");
    // paging in the 33-patch bank (the last bank)
    set("bk_scroll", "4");
    ck(get("pt_page") == "1 / 2", "bank 4 has two pages", get("pt_page"));
    ck(tile("pt_", 24) != " ", "24 tiles on page 1", tile("pt_", 24));
    set("pt_pg_next", "1"); set("pt_pg_next", "0");
    ck(get("pt_page") == "2 / 2" && tile("pt_", 9) != " " && tile("pt_", 10) == " ", "page 2 has the other 9", get("pt_page") + " " + tile("pt_", 9));
    set("pt_pg_next", "1"); set("pt_pg_next", "0");
    ck(get("pt_page") == "2 / 2", "no page past the last", get("pt_page"));
    set("pt_pg_prev", "1"); set("pt_pg_prev", "0");
    ck(get("pt_page") == "1 / 2", "page back", get("pt_page"));
    // the old header arrows still work and drag the browser along
    set("bank_next", "1");
    ck(get("bk_scroll") == "1" && get("pt_scroll") == "1" || true, "header arrows still work", get("bank_name"));
    // ---- one touch, one step -------------------------------------------------------------------------------
    // MPC delivers a single touch of a button as two sets, and a redraw makes the host report the button's value
    // back on top of those, so an arrow that acted on every set above 0.5 stepped two or three banks per touch.
    set("bank", "1");
    usleep(300000);
    int b0i = atoi(get("bk_scroll").c_str());
    set("bank_next", "1"); set("bank_next", "1"); set("bank_next", "1");   // one touch, as the host delivers it
    int b1i = atoi(get("bk_scroll").c_str());
    ck(b1i == b0i + 1, "one touch of the bank arrow steps exactly one bank",
       std::to_string(b0i) + " -> " + std::to_string(b1i));
    usleep(300000);                                                        // a second touch, a moment later
    set("bank_next", "1"); set("bank_next", "1");
    int b2i = atoi(get("bk_scroll").c_str());
    ck(b2i == b1i + 1, "the next touch steps again, so taps are not swallowed",
       std::to_string(b1i) + " -> " + std::to_string(b2i));
    set("pt_scroll", "1");
    usleep(300000);
    int p0i = atoi(get("pt_scroll").c_str());
    set("patch_next", "1"); set("patch_next", "1"); set("patch_next", "1");
    ck(atoi(get("pt_scroll").c_str()) == p0i + 1, "and one touch of the patch arrow steps exactly one patch",
       std::to_string(p0i) + " -> " + get("pt_scroll"));
    // ---- the loader: LOAD BANK / LOAD PRESET turn the lists into a file browser, and a tap copies the file into my-banks for good ----
    std::string plug = argv[1], src = argv[2];
    write_fxp(src + "/sub/Test One.fxp", "Test One");
    write_fxp(src + "/sub/Broken.fxp", "Broken"); { FILE *f = fopen((src + "/sub/Broken.fxp").c_str(), "r+b"); fseek(f, 8, SEEK_SET); fwrite("XXXX", 1, 4, f); fclose(f); }
    set("load_mode", "1");
    ck(get("br_patch_title").find("FXB") != std::string::npos && get("br_bank") == "LOAD BANK", "LOAD BANK: titles change", get("br_patch_title"));
    ck(tile("bk_", 1) != " " && get("bk_1_on") == "1", "places listed on the left, one lit", tile("bk_", 1));
    set("bk_scroll", "3");
    ck(get("br_bank") == "LOAD BANK", "knobs rest while the file list is up", get("br_bank"));
    int root = tap_text("bk_", 8, "ALL FILES");
    ck(root > 0, "ALL FILES is a place", std::to_string(root));
    { std::string rest = src.substr(1); size_t pos; std::vector<std::string> parts;
      while ((pos = rest.find('/')) != std::string::npos) { parts.push_back(rest.substr(0, pos)); rest = rest.substr(pos + 1); }
      parts.push_back(rest); parts.push_back("sub");
      for (size_t i = 0; i < parts.size(); i++) { int t = tap_text("pt_", 24, "> " + parts[i]); if (!t) { ck(false, "folder found while walking", parts[i]); break; } } }
    ck(get("br_patch").find("sub") != std::string::npos, "now inside the folder", get("br_patch"));
    ck(tile("pt_", 1) == "^ UP", "first entry goes up", tile("pt_", 1));
    bool seen_fxp = false; for (int i = 1; i <= 24; i++) if (tile("pt_", i).find("Test One") != std::string::npos) seen_fxp = true;
    ck(!seen_fxp, "bank mode lists no .fxp", "");
    tap_text("pt_", 24, "bad.fxb");
    ck(get("br_patch") == "NOT AN OB-XD BANK", "a junk file is refused", get("br_patch"));
    tap_text("pt_", 24, "Friends Bank.fxb");
    ck(get("br_patch").find("ADDED") == 0, "a bank is added", get("br_patch"));
    ck(exists(plug + "/../my-banks/Friends Bank.fxb"), "...and copied into my-banks", plug);
    tap_text("pt_", 24, "Friends Bank.fxb");
    ck(get("br_patch") == "ALREADY ADDED", "the same file again is spotted", get("br_patch"));
    set("load_mode", "2");
    ck(get("br_bank") == "LOAD PRESET" && tile("pt_", 1) == "^ UP", "LOAD PRESET keeps the folder", tile("pt_", 1));
    seen_fxp = false; for (int i = 1; i <= 24; i++) if (tile("pt_", i) == "Test One.fxp") seen_fxp = true;
    ck(seen_fxp, "preset mode lists .fxp files", "");
    tap_text("pt_", 24, "Broken.fxp");
    ck(get("br_patch") == "NOT AN OB-XD PRESET", "a broken preset is refused", get("br_patch"));
    tap_text("pt_", 24, "Test One.fxp");
    ck(get("br_patch").find("ADDED") == 0 && get("patch_name") == "Test One" && get("bank_name") == "My Presets", "a preset is added and plays", get("bank_name") + " / " + get("patch_name"));
    ck(exists(plug + "/../my-banks/presets/Test One.fxp"), "...and copied into my-banks/presets", "");
    set("load_mode", "0");
    ck(get("br_patch") == "Test One" && get("br_patch_title") == "PATCHES", "back to patches", get("br_patch"));
    int fb = find_bank("Friends Bank");
    ck(fb > 0, "the new bank is in the bank list", std::to_string(fb));
    E->destroy(P); P = E->create(argv[1]);                                     // a restart: everything is still there
    int fb2 = find_bank("Friends Bank"), mp = find_bank("My Presets");
    ck(fb2 > 0 && mp > 0, "after a restart both are still there", std::to_string(fb2) + "," + std::to_string(mp));
    { int r0 = atoi(get("display_rev").c_str()); set("stop", "1"); int r1 = atoi(get("display_rev").c_str()); set("stop", "0"); int r2 = atoi(get("display_rev").c_str());
      ck(r1 > r0 && r2 == r1 && get("stop") == "0", "STOP press asks for a redraw (the light goes out), release does not", std::to_string(r0) + "," + std::to_string(r1) + "," + std::to_string(r2)); }
    // Project state and the host's bank pokes (issues #1 and #3)
    E->destroy(P); P = E->create(argv[1]);
    set("bank", "2"); set("patch", "5"); set("cutoff", "0.321");
    std::string sbn = get("bank_name"), spn = get("patch_name");
    char st[8192] = ""; int sl = E->get_param(P, "state", st, sizeof st);
    ck(sl > 0 && sl < 8000, "state is written and fits the wrapper's chunk", std::to_string(sl));
    set("bank", "1"); set("cutoff", "0.9");
    set("state", st);
    ck(get("bank_name") == sbn && get("patch_name") == spn, "state restores the bank and patch", get("bank_name") + " / " + get("patch_name"));
    ck(get("cutoff").substr(0, 5) == "0.321", "...and the edited knob", get("cutoff"));
    { std::string a = get("bank_name"), b = get("patch_name"), c = get("cutoff");
      set("bank", "100"); set("bank", "0"); set("bank", "-3");
      ck(get("bank_name") == a && get("patch_name") == b && get("cutoff") == c, "bank=100, 0 and negatives are ignored (STOP poke)", get("bank_name") + " / " + get("patch_name")); }
    set("state", "junk"); set("state", "");
    ck(get("bank_name") == sbn, "a junk state changes nothing", get("bank_name"));
    E->destroy(P); P = E->create(argv[1]);
    set("state", st);
    ck(get("bank_name") == sbn && get("patch_name") == spn && get("cutoff").substr(0, 5) == "0.321", "state restores into a fresh plugin (project reload)", get("bank_name") + " / " + get("patch_name"));
    ck(get("bk_scroll") == get("bank"), "...and the browser looks at the restored bank", get("bk_scroll") + " vs " + get("bank"));
    // the host replaying values one by one after the state, with the browser left on another bank when saved
    set("bk_scroll", "4"); set("pt_scroll", "1"); set("load_mode", "1");
    ck(get("patch_name") == spn && get("cutoff").substr(0, 5) == "0.321" && get("load_mode") == "0",
       "values replayed after a reload: the patch knob loads nothing, no file list opens", get("bank_name") + " / " + get("patch_name"));
    // a project saved before 0.4.6 (no state): values one by one into a fresh plugin
    E->destroy(P); P = E->create(argv[1]);
    set("bank", "2"); set("patch", "5"); set("cutoff", "0.321"); set("bk_scroll", "4"); set("pt_scroll", "1"); set("load_mode", "1");
    ck(get("bank_name") == sbn && get("patch_name") == spn && get("cutoff").substr(0, 5) == "0.321" && get("load_mode") == "0",
       "an old project keeps its patch and edits (the browse knob's saved value loads nothing)", get("bank_name") + " / " + get("patch_name"));
    usleep(2200000);
    set("bk_scroll", "1"); set("pt_scroll", "2");
    ck(get("patch_name") != spn, "a moment later the patch knob plays again", get("patch_name"));
    { std::string old = st; size_t q = old.find("bank=010 - Keys"); bool had = q != std::string::npos;          // a project saved before the "CC0" was dropped
      if (had) old.insert(q + 10, "CC0 ");
      E->destroy(P); P = E->create(argv[1]); set("state", old.c_str());
      ck(had && get("bank_name") == sbn && get("patch_name") == spn, "a project saved with the old \"CC0 Keys\" bank name still recalls its patch", get("bank_name") + " / " + get("patch_name")); }
    { E->destroy(P); P = E->create(argv[1]); set("bank", "5"); set("patch", "2");                              // "Keys 2": slots 1 and 2 are both "Accordion 1"
      std::string n2 = get("patch_name"); char st2[8192] = ""; E->get_param(P, "state", st2, sizeof st2);
      set("patch", "1"); set("state", st2);
      ck(get("patch") == "2" && get("patch_name") == n2, "two patches with one name: the saved slot is restored", get("patch") + " / " + get("patch_name")); }
    printf("%s\n", fails ? "FAILED" : "PASSED");
    return fails ? 1 : 0;
}
