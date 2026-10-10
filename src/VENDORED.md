# Vendored engine

- Upstream: https://github.com/NickCulbertson/OB-Xd-GPL ("OB-Xd Community GPL"), GPL v3, commit b678ce04f8c65e8d981661e4bdc0e774ca1934ab
  (2025-03-19). It is a fork of https://github.com/reales/OB-Xd (discoDSP OB-Xd 2, originally Filatov Vadim's / 2DaT's Obxd).
- The DSP is the same as discoDSP's last published source (2.10, commit f1fcdd51eabcb7855cdd90818611cd7e357c359c); the community
  fork only modernises JUCE calls (`juce::` names, `MathConstants`). We checked by diffing both. discoDSP's later releases
  (2.11 to 2.20) are binary-only, so their changes are not in this plugin.
- Copied unmodified into `src/obxd/`: `Source/Engine/*.h` except `midiMap.h` and `ObxdBank.h` (JUCE XML/file code the port doesn't use).
- Added locally (nothing in `src/obxd/` is edited):
  - `src/PluginProcessor.h` and `src/juce_audio_basics/juce_audio_basics.h`: a tiny stand-in for the JUCE symbols the engine uses
    (`juce::jmin/jmax/jlimit/roundToInt/MathConstants/Random/String`, `zeromem`).
  - `src/MTS/libMTSClient.h`: no-op MTS-ESP client (always 12-TET), so nothing is dlopen()ed on the device.
  - `src/obxd_dispatch.h`: generated from upstream `PluginProcessor.cpp` `setEngineParameterValue` (77 parameters, same order as
    `ParamsEnum.h`, defaults from `Params.h`). `UNDEFINED`, `MIDILEARN`, `UNLEARN` are not exposed.
  - `src/obxd_mpc.cpp`: the `mpc_engine_t` that drives `SynthEngine` (MIDI: notes, pitch bend, mod wheel, sustain, all notes/sound off),
    plus the `master_hz` (FREQUENCY) and `stop` parameters.
- Not ported: the JUCE GUI, MIDI learn, the menu.

Licence notes: 18 of the 20 headers carry Filatov Vadim's 2013-2014 Obxd GPL header; `Decimator.h` is T. Rochebois's musicdsp.org
code; `Tuning.h` is discoDSP's 2021 file ("Copyright 2021 discoDSP") shipped inside the GPL v3 upstream repositories.
