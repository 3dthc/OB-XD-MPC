# Skin artwork notice

The files in `Default Skin/` (`main@4x.png`, `knob@4x.png`, `button@4x.png`, `voices@4x.png`, `legato@4x.png`, `coords.xml`) are the
default OB-Xd community theme:

- Author: gitterdude (https://github.com/gitterdude). "The default skin is inspired by Ilkka Rosma's theme in the discoDSP release."
- Taken unmodified from https://github.com/NickCulbertson/OB-Xd-GPL (`Themes/Default Skin`, commit b678ce04f8c65e8d981661e4bdc0e774ca1934ab).
  That repository's title image reads "OB-Xd Community GPL" (the original title was changed there by Nick Culbertson).
- Licence: **Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)**, as stated in that repository's README
  (https://creativecommons.org/licenses/by-sa/3.0/). The same theme is also shipped by https://github.com/pauloesteban/OB-Xx under the same licence.

## Changes made here (ShareAlike: the results below are under CC BY-SA 3.0 too)

`tools/make_skin.py` scales these images to the MPC screen, cuts the knob/button/voices/legato filmstrips, removes the MENU, LEARN and CLEAR
buttons and labels, moves VAM to the middle, adds a STOP button (its letters are lifted from the theme's own labels), and draws a second
page ("MORE") on the same colours. The results are `vst/images/*` and `vst/layout.conf`.

## How this fits with the GPL code

The skin is separate artwork shipped next to the GPL v3 code, not part of the program's source. The code stays GPL v3 (see `LICENSE`);
the skin files above, and `vst/images/`, stay CC BY-SA 3.0. If you redistribute the plugin zip you are redistributing both, each under its own terms.

## What is NOT included

discoDSP's own themes (for example "discoDSP Classic") are all-rights-reserved and are not in this repository. `tools/make_skin.py` can
build a private skin from a theme on your own computer; do not publish the result.
