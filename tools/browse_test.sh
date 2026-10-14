#!/usr/bin/env bash
# usage: tools/browse_test.sh <folder that has banks/ in it>   (offline x86 check of the BROWSE page's engine side)
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
MV="${MPC_VST_PLUGINS:-$HERE/../mpc-vst-plugins}"
[ -d "$MV" ] || MV=/home/claude/mpc-vst-plugins
[ -f "$HERE/vst/build/params.h" ] || python3 "$MV/tools/gen_vst.py" "$HERE/vst/vst.json" --params-h
T="$(mktemp -d)"
g++ -O1 -std=gnu++11 -I "$HERE/src" -I "$HERE/vst/build" -I "$MV/wrapper" -ffast-math "$HERE/src/obxd_mpc.cpp" "$HERE/tools/browse_test.cpp" -o "$T/t"
mkdir -p "$T/plug" "$T/src/sub"; cp -r "$1/banks" "$T/plug/banks"; cp "$1/banks/011 - CC0 Bass+Lead.fxb" "$T/src/sub/Friends Bank.fxb"; echo junk > "$T/src/sub/bad.fxb"; "$T/t" "$T/plug/banks" "$T/src"
rm -rf "$T"
