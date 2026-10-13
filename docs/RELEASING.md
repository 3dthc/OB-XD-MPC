# Releasing (and listing in the mpc-vst-plugins catalog)

Follows `docs/RELEASING.md` and `docs/CATALOG_SPEC.md` in sd88me/mpc-vst-plugins. Keep the catalog id (`obxd`), the uid
(`ObXd`) and the `.so` name (`obxd.so`) fixed across releases.

1. `./build.sh` (Ubuntu/WSL2, Docker) then `../mpc-vst-plugins/tools/test_port.sh vst/vst.json` must print PASSED.
2. Package (never include third-party artwork or banks you may not redistribute, see CREDITS.md). `tools/make_releases.sh` does the
   build and the zip; by hand:

       ../mpc-vst-plugins/tools/release.py --so vst/build/obxd.so --skin "vst/build/skin/sd88me - VST - OB-Xd" \
         --entry vst/build/pluginlist-entry.xml --version 0.3.0 --id obxd --repo OWNER/REPO --license GPL-3.0-only \
         --about "OB-Xd virtual analog polysynth (unofficial port)." --extra banks:banks --user-data my-banks -o dist
       ../mpc-vst-plugins/tools/catalog_check.py dist/OB-Xd-0.3.0-mpc-armv7.zip --catalog

   The zip must hold exactly the four cleared banks listed in `tools/make_releases.sh` (checked by SHA-256). `--user-data my-banks` makes the installer keep banks users add there; `banks/` is replaced on every install, so leftovers can never survive an upgrade.

3. Tag `vX.Y.Z` in this repo and attach the zip to a GitHub release. GPL: the release must point at this source repo.
4. Open a PR to sd88me/mpc-vst-plugins adding `catalog/plugins/obxd.json` (draft: `docs/catalog-obxd.json`; fill in
   `repo`, and a screenshot of the MPC screen committed at `docs/screenshots/obxd.png`, linked by tag or commit, not branch).
5. Optional: add a `tested.json` listing the devices tried (MPC Live II Gen 1, MPC OS 3.x).
