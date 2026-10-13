#!/usr/bin/env bash
# usage: tools/level_audit.sh <folder that has banks/ in it> [number of banks]   -> CSV on stdout
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
MV="${MPC_VST_PLUGINS:-$HERE/../mpc-vst-plugins}"
[ -d "$MV" ] || MV=/home/claude/mpc-vst-plugins
[ -f "$HERE/vst/build/params.h" ] || python3 "$MV/tools/gen_vst.py" "$HERE/vst/vst.json" --params-h
T="$(mktemp -d)"
g++ -O1 -std=gnu++11 -I "$HERE/src" -I "$HERE/vst/build" -I "$MV/wrapper" -ffast-math "$HERE/src/obxd_mpc.cpp" "$HERE/tools/level_audit.cpp" -o "$T/audit"
"$T/audit" "$1/banks" "${2:-3}"
rm -rf "$T"
