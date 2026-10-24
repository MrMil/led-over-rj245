#pragma once
// Defines the real wled.h's include guard: a quoted #include "wled.h" inside the firmware's own files resolves to the real
// header first, which then compiles to nothing. build.py force-includes this file (-include) ahead of every source.
#define WLED_H
// Stand-in for wled00/wled.h: what WLED's effect sources need from the rest of the firmware, and nothing else.
// FX.cpp, the Segment part of FX_fcn.cpp, FX_2Dfcn.cpp, FXparticleSystem.cpp, colors.cpp, palettes.cpp,
// wled_math.cpp and the noise/sound blocks of util.cpp compile unchanged against this header (build.py).
// The real FX.h, const.h and colors.h are used as they are.
#include "Arduino.h"
#include <vector>
#include <utility>
#include <time.h>
// The controller is a classic ESP32 (docs/controller/): its LEDC channel counts, which const.h otherwise reads from ESP-IDF
#define LEDC_CHANNEL_MAX 8
#define LEDC_SPEED_MODE_MAX 2
#define CONFIG_IDF_TARGET_ESP32 1
#include "const.h"                                      // the firmware's own constants
#include "src/dependencies/fastled_slim/fastled_slim.h" // the firmware's own FastLED subset
#include "fcn_declare.h"                                // our subset of the firmware's declarations

// Debug output: off, as in a release build
#define DEBUG_PRINT(x)
#define DEBUG_PRINTLN(x)
#define DEBUG_PRINTF(x...)
#define DEBUG_PRINTF_P(x...)
#define DEBUG_PRINT_P(x)
#define DEBUG_PRINTLN_P(x)
#define DEBUGFX_PRINT(x)
#define DEBUGFX_PRINTLN(x)
#define DEBUGFX_PRINTF(x...)
#define DEBUGFX_PRINTF_P(x...)

// The WLED_GLOBAL variables the effect sources read (defined in sim_main.cpp)
extern byte bri, briOld, briT, errorFlag, interfaceUpdateCallMode, lastRandomIndex, test, realtimeMode, realtimeOverride;
extern bool gammaCorrectBri, gammaCorrectCol, arlsDisableGammaCorrection, stateChanged, useMainSegmentOnly;
extern bool realtimeRespectLedMaps, useAMPM, useHarmonicRandomPalette;
extern uint8_t paletteBlend, blendingStyle, randomPaletteChangeTime, currentLedmap;
extern time_t localTime, sunrise, sunset;
extern unsigned loops;

// Busses: the simulator has none; FX.h asks only whether they can show.
struct BusConfig { uint8_t type = 0; uint16_t count = 0; uint16_t start = 0; };
extern std::vector<BusConfig> busConfigs;
class BusManager {
 public:
  static bool canAllShow() { return true; }
  static unsigned getNumBusses() { return 0; }
  static uint16_t getTotalLength(bool = false);
  static void setBrightness(uint8_t) {}
  static void setSegmentCCT(int, bool = false) {}
};
class JsonDocument;
extern JsonDocument *pDoc;

// Files: none. The font manager asks for fonts on the file system and gets nothing, so only the built-in fonts exist.
class File {
 public:
  operator bool() const { return false; }
  bool available() const { return false; }
  size_t read(uint8_t *, size_t) { return 0; }
  int read() { return -1; }
  bool seek(size_t, int = 0) { return false; }
  size_t size() const { return 0; }
  size_t position() const { return 0; }
  const char *name() const { return ""; }
  bool isDirectory() const { return false; }
  File openNextFile() { return File(); }
  void close() {}
};
#define SeekSet 0
struct WledFS { File open(const char *, const char * = "r") { return File(); } bool exists(const char *) { return false; } };
extern WledFS WLED_FS;

#include "colors.h"   // the firmware's colour types and palette declarations
#ifdef SIM_MAIN
  #define protected public   // sim_main.cpp reads the segment's pixel buffer, which the firmware keeps for its own show()
#endif
#include "FX.h"       // the firmware's Segment and WS2812FX, unchanged
#ifdef SIM_MAIN
  #undef protected
#endif
extern WS2812FX strip;
