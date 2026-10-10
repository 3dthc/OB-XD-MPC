// Minimal stand-in for the JUCE bits the OB-Xd engine headers use (juce:: namespace). Included by
// obxd/SynthEngine.h as "../PluginProcessor.h", so the vendored engine files stay unmodified.
#pragma once
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>
#include <algorithm>
#include <map>
#include <vector>

namespace juce {
static const float float_Pi = 3.14159265358979323846f;
template <typename T> struct MathConstants { static constexpr T pi = (T)3.14159265358979323846L; };
template <typename T> static inline T jmin(T a, T b) { return a < b ? a : b; }
template <typename T> static inline T jmax(T a, T b) { return a > b ? a : b; }
template <typename T> static inline T jmin(T a, T b, T c) { return jmin(jmin(a, b), c); }
template <typename T> static inline T jmax(T a, T b, T c) { return jmax(jmax(a, b), c); }
template <typename T> static inline T jlimit(T lo, T hi, T v) { return v < lo ? lo : (v > hi ? hi : v); }
template <typename T> static inline int roundToInt(T v) { return (int)std::floor((double)v + 0.5); }
static inline void zeromem(void *p, size_t n) { memset(p, 0, n); }
typedef std::string String;


// juce::Random: only what the engine calls (seeded construction, nextFloat, nextInt64, getSystemRandom).
class Random {
    uint64_t seed;
public:
    Random() : seed(0x9E3779B97F4A7C15ull) {}
    explicit Random(int64_t s) : seed((uint64_t)s * 0x9E3779B97F4A7C15ull + 1) {}
    int64_t nextInt64() { seed = seed * 6364136223846793005ull + 1442695040888963407ull;
                          return (int64_t)(seed ^ (seed >> 29)); }
    int nextInt() { return (int)(nextInt64() >> 16); }
    float nextFloat() { return (float)((uint32_t)(nextInt64() >> 8) & 0xFFFFFF) / 16777216.0f; }
    static Random &getSystemRandom() { static Random r(12345); return r; }
};
} // namespace juce
using namespace juce;
