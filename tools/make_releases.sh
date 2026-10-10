#!/usr/bin/env bash
# One build, up to two zips (run from the repo folder, in Ubuntu/WSL2 with Docker):
#   dist-public/  OB-Xd-<ver>-mpc-armv7.zip               ships the Moby Pixel bank only: safe to publish
#   dist-private/ OB-Xd-PRIVATE-all-banks-<ver>.zip       also holds the .fxb banks of YOUR OB-Xd install: your device only, never upload
#
#   bash tools/make_releases.sh [path/to/OB-Xd/Banks]     (no path: only the public zip)
#
# The banks are plain files in the plugin's "banks" folder, so the two zips hold the same plugin. You can also skip the private zip
# and just copy .fxb files into <plugin folder>/banks/ on the MPC.
# Environment: MPC_VST (default ~/mpc-vst-plugins), OWNER (default 3dthc), VERSION (default 0.3.0)
set -euo pipefail
cd "$(dirname "$0")/.."
export MPC_VST="${MPC_VST:-$HOME/mpc-vst-plugins}"
OWNER="${OWNER:-3dthc}"
VERSION="${VERSION:-0.3.0}"
BANKS="${1:-}"
ABOUT="OB-Xd virtual analog polysynth (unofficial port)."
SKIN="vst/build/skin/sd88me - VST - OB-Xd"

package() {   # $1 = output folder, $2 = folder holding the banks to ship
  "$MPC_VST/tools/release.py" --so vst/build/obxd.so --skin "$SKIN" --entry vst/build/pluginlist-entry.xml \
    --version "$VERSION" --id obxd --repo "$OWNER/OB-XD-MPC" --license GPL-3.0-only --about "$ABOUT" \
    --extra "$2:banks" --user-data banks -o "$1"
}

echo "== build =="
rm -rf vst/build dist-public dist-private
./build.sh | tail -2

echo "== public zip (Moby Pixel bank only) =="
package dist-public banks
Z="dist-public/OB-Xd-$VERSION-mpc-armv7.zip"
[ "$(unzip -Z1 "$Z" | grep -i '\.fxb$' | sed 's#.*/##')" = "000 - Moby Pixel Bank.fxb" ] || { echo "public zip must hold only the Moby Pixel bank: stopping"; exit 1; }
echo "OK: $Z"

if [ -n "$BANKS" ]; then
  echo "== private zip (your banks from $BANKS) =="
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  cp banks/*.fxb "$TMP/"
  find "$BANKS" -maxdepth 1 -iname '*.fxb' -exec cp {} "$TMP/" \;
  package dist-private "$TMP"
  mv "dist-private/OB-Xd-$VERSION-mpc-armv7.zip" "dist-private/OB-Xd-PRIVATE-all-banks-$VERSION.zip"
  echo "OK: dist-private/OB-Xd-PRIVATE-all-banks-$VERSION.zip (your device only, do not upload)"
fi
