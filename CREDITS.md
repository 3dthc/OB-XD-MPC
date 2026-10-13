# Credits and licences

This project is an **unofficial** port. It is not made, endorsed or supported by discoDSP, 2Dat, Akai Professional or the OB-Xd community project.
"OB-Xd" is the name of the original synthesizer; "Akai", "MPC" and "Force" belong to their owners.

| What | Who | Licence |
|---|---|---|
| Original **Obxd** synthesizer and DSP engine (2013-2014) | Filatov Vadim ([2DaT](https://github.com/2DaT/Obxd)) | GPL (file headers) |
| **OB-Xd 2** source (discoDSP, last published source 2.10, commit `f1fcdd51eabcb7855cdd90818611cd7e357c359c`), the origin of the engine | [discoDSP / reales](https://github.com/reales/OB-Xd) | GPL v3 (upstream README) |
| Engine headers in `src/obxd/`, taken from **OB-Xd Community GPL** (commit `b678ce04f8c65e8d981661e4bdc0e774ca1934ab`) | [Nick Culbertson](https://github.com/NickCulbertson/OB-Xd-GPL), building on [joeloftusdev/OB-Xd](https://github.com/joeloftusdev/OB-Xd) and [pauloesteban/OB-Xx](https://github.com/pauloesteban/OB-Xx) | GPL v3 |
| `Decimator17` (`src/obxd/Decimator.h`) | T. Rochebois, via musicdsp.org | as published on musicdsp.org |
| `Tuning.h` (MTS-ESP hook) | Natalia Escalera / discoDSP, 2021 | part of the GPL v3 repositories above |
| **Skin artwork** (`skin-source/Default Skin/`, derived `vst/images/`): the default OB-Xd community theme (its knobs, buttons, displays and logo; the panel background, section frames and labels are redrawn for the MPC screen by `tools/panel_draw.py`, in the same style, and stay under the same licence) | gitterdude, inspired by Ilkka Rosma's theme; title image by Nick Culbertson | CC BY-SA 3.0 (see `skin-source/NOTICE.md`) |
| **Preset bank** (`banks/000 - Moby Pixel.fxb`, file contents unmodified, only the file name shortened; read by the plugin at run time) | from the OB-Xd Community GPL repository (patch author not named there) | GPL v3 (that repository) |
| **Preset banks** (`banks/010 - CC0 Keys.fxb`, `011 - CC0 Bass+Lead.fxb`, `012 - CC0 Pads+FX.fxb`; 79 patches) | factory patches of [OB-Xf](https://github.com/surge-synthesizer/OB-Xf) by its contributors (names in `banks/CREDITS-CC0.md`), converted to OB-Xd's bank format by `tools/convert_obxf_patches.py` | CC0 / Public Domain (stated in each patch file) |
| MPC VST2 wrapper, `mpc_engine_t` interface, build/test/skin tools (**not included**; cloned separately) | [sd88me/mpc-vst-plugins](https://github.com/sd88me/mpc-vst-plugins) | MIT |
| `src/obxd_mpc.cpp`, `src/obxd_dispatch.h`, `src/PluginProcessor.h`, `src/juce_audio_basics/`, `src/MTS/libMTSClient.h`, `tools/`, `vst/` (code) | this repository | GPL v3 |

Upstream thanks (from the OB-Xd README): 2Dat for the original OB-Xd, Soshi Studio, and the KVR community skin artists.

## What is deliberately NOT in this repository

discoDSP states that its own images and other resources (for example the "discoDSP Classic" theme and the banks in its installer) are all
rights reserved, apart from `Source/Images` (CC BY-SA 2.0). None of that is included. `tools/make_skin.py` can
read them from **your own** OB-Xd installation for private use; do not upload what they generate from those files.

## Version note

The engine is OB-Xd **2.10** because that is the last source published. Later releases (2.11 to 2.20 and newer) are binary-only, so this
plugin does not include their DSP changes.

## Themes

The four colour themes (panel plates, display wells, recoloured logo) are drawn by `tools/panel_draw.py` and are part of this repo (GPL-3.0 code, CC BY-SA 3.0 skin files, based on gitterdude's Default Skin).
