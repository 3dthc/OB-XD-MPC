// Offline audit of every patch in a banks folder: loads each patch, plays a six-note chord for 2 s and prints
//   bank|number|name|volume|rms|peak|cpu       (peak 1.0 = clipping; cpu = seconds of computing per second of sound, x86)
// build and run: tools/level_audit.sh <folder that has banks/ in it> [number of banks]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <time.h>
extern "C" {
#include "engine.h"
}
static void chord(const mpc_engine_t *e, void *p, int on) {
    static const int notes[6] = {48, 52, 55, 60, 64, 67};
    for (int i = 0; i < 6; i++) { uint8_t m[3] = {(uint8_t)(on ? 0x90 : 0x80), (uint8_t)notes[i], (uint8_t)(on ? 100 : 0)}; e->midi(p, m, 3); }
}
int main(int argc, char **argv) {
    const mpc_engine_t *e = mpc_engine();
    void *p = e->create(argv[1]);
    char b[256], v[16];
    int nbanks = argc > 2 ? atoi(argv[2]) : 3;
    for (int bk = 1; bk <= nbanks; bk++) {
        snprintf(v, 16, "%d", bk);
        e->set_param(p, "bank", v);
        e->get_param(p, "bank_name", b, 256);
        char bn[256]; strcpy(bn, b), b[0] = 0;
        char firstn[256] = "";
        for (int pt = 0; pt < 200; pt++) {
            if (pt > 0) e->set_param(p, "patch_next", "1");
            e->get_param(p, "patch_name", b, 256);
            if (pt == 0) strcpy(firstn, b); else if (!strcmp(firstn, b) && pt > 1) break;   // wrapped round
            char vol[32] = "0"; e->get_param(p, "volume", vol, 32);
            double s = 0, pk = 0; long n = 0; int16_t o[256];
            chord(e, p, 1);
            clock_t t0 = clock();
            for (int k = 0; k < 344 * 2; k++) {
                e->render(p, o, 128);
                for (int i = 0; i < 256; i++) { double x = o[i] / 32768.0; s += x * x; n++; if (fabs(x) > pk) pk = fabs(x); }
            }
            double cpu = (double)(clock() - t0) / CLOCKS_PER_SEC / 2.0;
            chord(e, p, 0);
            for (int k = 0; k < 344 * 3; k++) e->render(p, o, 128);
            printf("%s|%d|%s|%s|%.5f|%.3f|%.4f\n", bn, pt + 1, b, vol, sqrt(s / n), pk, cpu);
        }
    }
    return 0;
}
