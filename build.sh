#!/usr/bin/env bash
# Build the OB-Xd port for MPC OS (needs Docker, and a checkout of sd88me/mpc-vst-plugins next to this folder
# or MPC_VST pointing at it).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MV="${MPC_VST:-$HERE/../mpc-vst-plugins}"
"$MV/tools/build_port.sh" "$HERE/vst/vst.json"
echo "Built: $HERE/vst/build/ (obxd.so, skin/, pluginlist-entry.xml)"
