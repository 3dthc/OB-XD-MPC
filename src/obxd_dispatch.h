// generated from OB-Xd 2.10 PluginProcessor.cpp setEngineParameterValue: do not edit
#pragma once
struct ObxdParamInfo { const char *key; int id; float def; };
static const ObxdParamInfo kObxdParams[] = {
  {"volume", VOLUME, 0.5f},
  {"voice_count", VOICE_COUNT, 0.2f},
  {"tune", TUNE, 0.5f},
  {"octave", OCTAVE, 0.5f},
  {"bendrange", BENDRANGE, 0.0f},
  {"bendosc2", BENDOSC2, 0.0f},
  {"legatomode", LEGATOMODE, 0.0f},
  {"bendlforate", BENDLFORATE, 0.6f},
  {"vfltenv", VFLTENV, 0.0f},
  {"vampenv", VAMPENV, 0.0f},
  {"asplayedallocation", ASPLAYEDALLOCATION, 0.0f},
  {"portamento", PORTAMENTO, 0.0f},
  {"unison", UNISON, 0.0f},
  {"udet", UDET, 0.2f},
  {"osc2_det", OSC2_DET, 0.4f},
  {"lfofreq", LFOFREQ, 0.0f},
  {"lfosinwave", LFOSINWAVE, 0.0f},
  {"lfosquarewave", LFOSQUAREWAVE, 0.0f},
  {"lfoshwave", LFOSHWAVE, 0.0f},
  {"lfo1amt", LFO1AMT, 0.0f},
  {"lfo2amt", LFO2AMT, 0.0f},
  {"lfoosc1", LFOOSC1, 0.0f},
  {"lfoosc2", LFOOSC2, 0.0f},
  {"lfofilter", LFOFILTER, 0.0f},
  {"lfopw1", LFOPW1, 0.0f},
  {"lfopw2", LFOPW2, 0.0f},
  {"osc2hs", OSC2HS, 0.0f},
  {"xmod", XMOD, 0.0f},
  {"osc1p", OSC1P, 0.0f},
  {"osc2p", OSC2P, 0.0f},
  {"oscquantize", OSCQuantize, 0.0f},
  {"osc1saw", OSC1Saw, 1.0f},
  {"osc1pul", OSC1Pul, 0.0f},
  {"osc2saw", OSC2Saw, 1.0f},
  {"osc2pul", OSC2Pul, 0.0f},
  {"pw", PW, 0.0f},
  {"brightness", BRIGHTNESS, 1.0f},
  {"envpitch", ENVPITCH, 0.0f},
  {"osc1mix", OSC1MIX, 1.0f},
  {"osc2mix", OSC2MIX, 1.0f},
  {"noisemix", NOISEMIX, 0.0f},
  {"flt_kf", FLT_KF, 0.0f},
  {"cutoff", CUTOFF, 1.0f},
  {"resonance", RESONANCE, 0.0f},
  {"multimode", MULTIMODE, 0.0f},
  {"filter_warm", FILTER_WARM, 0.0f},
  {"bandpass", BANDPASS, 0.0f},
  {"fourpole", FOURPOLE, 0.0f},
  {"envelope_amt", ENVELOPE_AMT, 0.0f},
  {"latk", LATK, 0.0f},
  {"ldec", LDEC, 0.0f},
  {"lsus", LSUS, 1.0f},
  {"lrel", LREL, 0.0f},
  {"fatk", FATK, 0.0f},
  {"fdec", FDEC, 0.0f},
  {"fsus", FSUS, 0.0f},
  {"frel", FREL, 0.0f},
  {"envder", ENVDER, 0.3f},
  {"filterder", FILTERDER, 0.3f},
  {"portader", PORTADER, 0.3f},
  {"pan1", PAN1, 0.5f},
  {"pan2", PAN2, 0.5f},
  {"pan3", PAN3, 0.5f},
  {"pan4", PAN4, 0.5f},
  {"pan5", PAN5, 0.5f},
  {"pan6", PAN6, 0.5f},
  {"pan7", PAN7, 0.5f},
  {"pan8", PAN8, 0.5f},
  {"economy_mode", ECONOMY_MODE, 1.0f},
  {"lfo_sync", LFO_SYNC, 0.0f},
  {"pw_env", PW_ENV, 0.0f},
  {"pw_env_both", PW_ENV_BOTH, 0.0f},
  {"env_pitch_both", ENV_PITCH_BOTH, 0.0f},
  {"fenv_invert", FENV_INVERT, 0.0f},
  {"pw_osc2_ofs", PW_OSC2_OFS, 0.0f},
  {"level_dif", LEVEL_DIF, 0.3f},
  {"self_osc_push", SELF_OSC_PUSH, 0.0f},
};
static const int kObxdParamCount = 77;
static inline void obxd_dispatch(SynthEngine &synth, int index, float newValue) {
  switch (index) {
  case VOLUME: synth.processVolume(newValue); break;
  case VOICE_COUNT: synth.setVoiceCount(newValue); break;
  case TUNE: synth.processTune(newValue); break;
  case OCTAVE: synth.processOctave(newValue); break;
  case BENDRANGE: synth.procPitchWheelAmount(newValue); break;
  case BENDOSC2: synth.procPitchWheelOsc2Only(newValue); break;
  case LEGATOMODE: synth.processLegatoMode(newValue); break;
  case BENDLFORATE: synth.procModWheelFrequency(newValue); break;
  case VFLTENV: synth.procFltVelocityAmount(newValue); break;
  case VAMPENV: synth.procAmpVelocityAmount(newValue); break;
  case ASPLAYEDALLOCATION: synth.procAsPlayedAlloc(newValue); break;
  case PORTAMENTO: synth.processPortamento(newValue); break;
  case UNISON: synth.processUnison(newValue); break;
  case UDET: synth.processDetune(newValue); break;
  case OSC2_DET: synth.processOsc2Det(newValue); break;
  case LFOFREQ: synth.processLfoFrequency(newValue); break;
  case LFOSINWAVE: synth.processLfoSine(newValue); break;
  case LFOSQUAREWAVE: synth.processLfoSquare(newValue); break;
  case LFOSHWAVE: synth.processLfoSH(newValue); break;
  case LFO1AMT: synth.processLfoAmt1(newValue); break;
  case LFO2AMT: synth.processLfoAmt2(newValue); break;
  case LFOOSC1: synth.processLfoOsc1(newValue); break;
  case LFOOSC2: synth.processLfoOsc2(newValue); break;
  case LFOFILTER: synth.processLfoFilter(newValue); break;
  case LFOPW1: synth.processLfoPw1(newValue); break;
  case LFOPW2: synth.processLfoPw2(newValue); break;
  case OSC2HS: synth.processOsc2HardSync(newValue); break;
  case XMOD: synth.processOsc2Xmod(newValue); break;
  case OSC1P: synth.processOsc1Pitch(newValue); break;
  case OSC2P: synth.processOsc2Pitch(newValue); break;
  case OSCQuantize: synth.processPitchQuantization(newValue); break;
  case OSC1Saw: synth.processOsc1Saw(newValue); break;
  case OSC1Pul: synth.processOsc1Pulse(newValue); break;
  case OSC2Saw: synth.processOsc2Saw(newValue); break;
  case OSC2Pul: synth.processOsc2Pulse(newValue); break;
  case PW: synth.processPulseWidth(newValue); break;
  case BRIGHTNESS: synth.processBrightness(newValue); break;
  case ENVPITCH: synth.processEnvelopeToPitch(newValue); break;
  case OSC1MIX: synth.processOsc1Mix(newValue); break;
  case OSC2MIX: synth.processOsc2Mix(newValue); break;
  case NOISEMIX: synth.processNoiseMix(newValue); break;
  case FLT_KF: synth.processFilterKeyFollow(newValue); break;
  case CUTOFF: synth.processCutoff(newValue); break;
  case RESONANCE: synth.processResonance(newValue); break;
  case MULTIMODE: synth.processMultimode(newValue); break;
  case FILTER_WARM: synth.processOversampling(newValue); break;
  case BANDPASS: synth.processBandpassSw(newValue); break;
  case FOURPOLE: synth.processFourPole(newValue); break;
  case ENVELOPE_AMT: synth.processFilterEnvelopeAmt(newValue); break;
  case LATK: synth.processLoudnessEnvelopeAttack(newValue); break;
  case LDEC: synth.processLoudnessEnvelopeDecay(newValue); break;
  case LSUS: synth.processLoudnessEnvelopeSustain(newValue); break;
  case LREL: synth.processLoudnessEnvelopeRelease(newValue); break;
  case FATK: synth.processFilterEnvelopeAttack(newValue); break;
  case FDEC: synth.processFilterEnvelopeDecay(newValue); break;
  case FSUS: synth.processFilterEnvelopeSustain(newValue); break;
  case FREL: synth.processFilterEnvelopeRelease(newValue); break;
  case ENVDER: synth.processEnvelopeDetune(newValue); break;
  case FILTERDER: synth.processFilterDetune(newValue); break;
  case PORTADER: synth.processPortamentoDetune(newValue); break;
  case PAN1: synth.processPan(newValue, 1); break;
  case PAN2: synth.processPan(newValue, 2); break;
  case PAN3: synth.processPan(newValue, 3); break;
  case PAN4: synth.processPan(newValue, 4); break;
  case PAN5: synth.processPan(newValue, 5); break;
  case PAN6: synth.processPan(newValue, 6); break;
  case PAN7: synth.processPan(newValue, 7); break;
  case PAN8: synth.processPan(newValue, 8); break;
  case ECONOMY_MODE: synth.procEconomyMode(newValue); break;
  case LFO_SYNC: synth.procLfoSync(newValue); break;
  case PW_ENV: synth.processPwEnv(newValue); break;
  case PW_ENV_BOTH: synth.processPwEnvBoth(newValue); break;
  case ENV_PITCH_BOTH: synth.processPitchModBoth(newValue); break;
  case FENV_INVERT: synth.processInvertFenv(newValue); break;
  case PW_OSC2_OFS: synth.processPwOfs(newValue); break;
  case LEVEL_DIF: synth.processLoudnessDetune(newValue); break;
  case SELF_OSC_PUSH: synth.processSelfOscPush(newValue); break;
  default: break;
  }
}
