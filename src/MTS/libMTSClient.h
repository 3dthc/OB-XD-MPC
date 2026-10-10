// No-op stand-in for ODDSound's libMTSClient (MTS-ESP). The real client dlopen()s a master library
// from the host machine, which does not exist on an MPC, so the engine always runs in 12-TET here.
#pragma once
struct MTSClient;
static inline MTSClient *MTS_RegisterClient() { return nullptr; }
static inline void MTS_DeregisterClient(MTSClient *) {}
static inline bool MTS_HasMaster(MTSClient *) { return false; }
static inline double MTS_RetuningInSemitones(MTSClient *, char, char) { return 0.0; }
static inline const char *MTS_GetScaleName(MTSClient *) { return ""; }
