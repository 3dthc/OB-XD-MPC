#!/usr/bin/env bash
# One build, up to two zips (run from the repo folder, in Ubuntu/WSL2 with Docker):
#   dist-public/  OB-Xd-<ver>-mpc-armv7.zip               ships the Moby Pixel bank only: safe to publish
#   dist-private/ OB-Xd-PRIVATE-all-banks-<ver>.zip       also holds the .fxb banks of YOUR OB-Xd install: your device only, never upload
#
#   bash tools/make_releases.sh [path/to/OB-Xd/Banks]     (no path: only the public zip)
#
# The banks are plain files in the plugin's "banks" folder, so the two zips hold the same plugin. You can also skip the private zip
# and just copy .fxb files into <plugin folder>/my-banks/ on the MPC (kept on upgrade; banks/ is replaced by every install).
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
    --extra "$2:banks" --user-data my-banks -o "$1"
}

echo "== build =="
rm -rf vst/build dist-public dist-private
bash ./build.sh | tail -2

echo "== public zip (cleared banks only) =="
# The public zip is built from a staging folder holding ONLY the cleared banks and their notices, copied by exact name.
# Nothing else in banks/ (or anywhere else) can get in, and every bank is checked against the SHA-256 listed here.
#   Moby Pixel Bank: GPL community repository (see banks/NOTICE.md)
#   CC0 Keys / Bass+Lead / Pads+FX: converted from OB-Xf's CC0 / public-domain patches (see banks/CREDITS-CC0.md)
CLEARED="29cf57db9de19f257297c80bd3ccb7a4c1b142a0764a75a7844bd6d2338c68e8  000 - Moby Pixel.fxb
b0c956b8564cf3e012708256eeb91b34900eee92bd07ed8bbb9518db37f9f9d5  010 - CC0 Keys.fxb
84e14981e3dec0547388b2869f24ebb32785b60fe626df6a4702a95431975ce6  011 - CC0 Bass+Lead.fxb
cda26d070a245192247d041e5b1932945481e392b8d4ea2bfe5a83da41aedb5a  012 - CC0 Pads+FX.fxb"
PUB="$(mktemp -d)"
NAMES=""
while IFS= read -r line; do
  sha="${line%%  *}"; name="${line#*  }"
  [ -f "banks/$name" ] || { echo "banks/$name is missing: stopping"; exit 1; }
  [ "$(sha256sum "banks/$name" | cut -d' ' -f1)" = "$sha" ] || { echo "banks/$name is not the cleared file: stopping"; exit 1; }
  cp "banks/$name" "$PUB/"
  NAMES="$NAMES$name
"
done <<EOF
$CLEARED
EOF
cp banks/NOTICE.md banks/CREDITS-CC0.md "$PUB/"
EXTRA=$(find banks -maxdepth 1 -type f ! -name '*.md' | wc -l)
[ "$EXTRA" = "4" ] || echo "note: $((EXTRA - 4)) other file(s) in banks/ are ignored for the public zip"
package dist-public "$PUB"
rm -rf "$PUB"
Z="dist-public/OB-Xd-$VERSION-mpc-armv7.zip"
GOT="$(unzip -Z1 "$Z" | grep -i -E '\.(fxb|fxp)$' | sed 's#.*/##' | sort)"
WANT="$(printf '%s' "$NAMES" | sed '/^$/d' | sort)"
[ "$GOT" = "$WANT" ] || { echo "public zip must hold exactly the cleared banks: stopping"; exit 1; }
while IFS= read -r line; do
  sha="${line%%  *}"; name="${line#*  }"
  [ "$(unzip -p "$Z" "*/banks/$name" | sha256sum | cut -d' ' -f1)" = "$sha" ] || { echo "$name in the zip differs from the cleared one: stopping"; exit 1; }
done <<EOF
$CLEARED
EOF
echo "OK: $Z (only the cleared banks)"

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
