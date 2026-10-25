// The simulator around WLED's effect code: one strip, one segment, driven frame by frame from JavaScript.
// Everything the effects see (SEGMENT, strip.now, palettes, noise, the sound simulator) is the firmware's own code
// (build.py); this file supplies the globals wled.h would, the few WS2812FX bodies that live in the uncompiled half
// of FX_fcn.cpp, and the exported calls the page uses. Why: docs/firmware/effects_in_browser.md.
#include "wled.h"
#include "palette_names.h"
#include <emscripten/emscripten.h>

// ---- the WLED_GLOBAL variables the effect sources read, at the firmware's defaults ----
byte bri = 255, briOld = 255, briT = 255, errorFlag = 0, interfaceUpdateCallMode = 0, lastRandomIndex = 0, test = 0;
byte realtimeMode = REALTIME_MODE_INACTIVE, realtimeOverride = 0;
bool gammaCorrectBri = false, gammaCorrectCol = true, arlsDisableGammaCorrection = true, stateChanged = false;
bool useMainSegmentOnly = false, realtimeRespectLedMaps = false, useAMPM = false, useHarmonicRandomPalette = true;
uint8_t paletteBlend = 0, blendingStyle = 0, randomPaletteChangeTime = 5, currentLedmap = 0;
time_t localTime = 0, sunrise = 0, sunset = 0;
unsigned loops = 0;
std::vector<BusConfig> busConfigs;
std::vector<CRGBPalette16> customPalettes;
std::vector<UsermodPalette> usermodPalettes;
JsonDocument *pDoc = nullptr;
HardwareSerial Serial;
WledFS WLED_FS;
WS2812FX strip;
uint16_t BusManager::getTotalLength(bool) { return Segment::maxWidth * Segment::maxHeight; }

// ---- the simulated clock and a seeded random source, so a run repeats ----
static uint32_t g_now = 0;
uint32_t millis() { return g_now; }
uint32_t micros() { return g_now * 1000u; }
void yield() {}
void delay(uint32_t) {}
void delayMicroseconds(uint32_t) {}
static uint32_t g_rng = 0x2545F491u;
uint32_t sim_random32() { uint32_t x = g_rng; x ^= x << 13; x ^= x >> 17; x ^= x << 5; g_rng = x; return x; }

// ---- memory: the heap, every time ----
extern "C" {
  void *d_malloc(size_t n) { return malloc(n); }
  void *d_calloc(size_t c, size_t n) { return calloc(c, n); }
  void *d_realloc_malloc(void *p, size_t n) { return realloc(p, n); }
}
void *allocate_buffer(size_t size, uint32_t type) { return (type & BFRALLOC_CLEAR) ? calloc(size, 1) : malloc(size); }

// ---- WS2812FX bodies from the uncompiled half of FX_fcn.cpp (the firmware's, minus busses) ----
Segment& WS2812FX::getSegment(unsigned id) { return _segments[id >= _segments.size() ? 0 : id]; }
uint16_t WS2812FX::getLengthTotal() const {
  unsigned len = Segment::maxWidth * Segment::maxHeight;
  if (isMatrix && _length > len) len = _length;
  return len;
}
uint16_t WS2812FX::getLengthPhysical() const { return _length; }
uint8_t WS2812FX::getActiveSegmentsNum() const { unsigned c = 0; for (const Segment &seg : _segments) if (seg.isActive()) c++; return c; }
void WS2812FX::updatePixelBuffer() {
  uint32_t requiredMem = getLengthTotal() * sizeof(uint32_t);
  p_free(_pixels);
  _pixels = static_cast<uint32_t*>(allocate_buffer(requiredMem, BFRALLOC_CLEAR));
}
void WS2812FX::show() {}
void WS2812FX::setUpMatrix() {}
bool WS2812FX::deserializeMap(unsigned) { return false; }
void WS2812FX::restartRuntime() { for (Segment &seg : _segments) seg.markForReset(); }
void WS2812FX::setTransitionMode(bool) {}
void WS2812FX::waitForIt() {}
void WS2812FX::setTargetFps(unsigned fps) { _targetFps = fps; }
void WS2812FX::setBrightness(uint8_t b, bool) { _brightness = b; }
uint8_t WS2812FX::getFirstSelectedSegId() const { return 0; }
void WS2812FX::setMainSegmentId(unsigned n) { _mainSegment = n; }
uint8_t WS2812FX::getLastActiveSegmentId() const { return 0; }
bool WS2812FX::hasRGBWBus() const { return false; }
bool WS2812FX::hasCCTBus() const { return false; }
void WS2812FX::purgeSegments() {}
void WS2812FX::resetSegments() {}
void WS2812FX::makeAutoSegments(bool) {}
void WS2812FX::fixInvalidSegments() {}
bool WS2812FX::checkSegmentAlignment() const { return true; }
void WS2812FX::setRange(uint16_t, uint16_t, uint32_t) {}
void WS2812FX::setRealtimePixelColor(unsigned, uint32_t) {}
void WS2812FX::setCCT(uint16_t) {}
uint8_t WS2812FX::getActiveSegsLightCapabilities(bool) const { return SEG_CAPABILITY_RGB; }
const char JSON_mode_names[] PROGMEM = R"=====(["FX names moved"])=====";

// The one segment: the whole strip, width × height (height 1 for the controller's one logical strip, the tallest tower
// for the rolled 2D map). finalizeInit() is the firmware's name for strip set-up, so it is the member that lays it out.
static int g_w = 1, g_h = 1;
void WS2812FX::finalizeInit() {
  isMatrix = g_h > 1;
  Segment::maxWidth = g_w; Segment::maxHeight = g_h;
  _length = g_w * g_h;
  d_free(customMappingTable); customMappingTable = nullptr; customMappingSize = 0;
  _segments.clear();
  _segments.push_back(Segment(0, g_w, 0, g_h));
  _segments[0].setColor(0, DEFAULT_COLOR);
  _segments[0].refreshLightCapabilities();       // marks the segment RGB; without it color_from_palette() ignores every palette
  _currentSegment = &_segments[0];
  updatePixelBuffer();
  _transitionDur = 0;                            // no transitions: a change shows on the next frame, as a preset does
  if (_mode.size() <= 1) setupEffectData();      // the firmware's own effect list, once
}

// One frame: the effect part of the firmware's service(), without the busses.
void WS2812FX::service() {
  now = millis() + timebase;
  Segment &seg = _segments[0];
  _segment_index = 0;
  seg.handleTransition();
  seg.resetIfRequired();
  if (seg.isActive() && !seg.freeze) {
    uint16_t prog = seg.progress();
    seg.beginDraw(prog);
    _currentSegment = &seg;
    _mode[seg.mode]();
    seg.call++;
  }
  _currentSegment = &_segments[0];
  Segment::handleRandomPalette();
}

// ---- exports ----
static Segment &seg0() { if (strip.getSegmentsNum() == 0) { g_w = g_h = 1; strip.finalizeInit(); } return strip.getSegment(0); }   // never an empty strip
extern "C" {
EMSCRIPTEN_KEEPALIVE void sim_init(int width, int height) {
  static bool once = false;
  if (!once) { NeoGammaWLEDMethod::calcGammaTable(2.8f); once = true; }
  g_w = width > 0 ? width : 1; g_h = height > 0 ? height : 1;
  strip.finalizeInit();
}
EMSCRIPTEN_KEEPALIVE const uint32_t *sim_frame(uint32_t now_ms) { g_now = now_ms; strip.service(); return seg0().getPixels(); }
EMSCRIPTEN_KEEPALIVE const uint32_t *sim_pixels() { return seg0().getPixels(); }
EMSCRIPTEN_KEEPALIVE int sim_width() { return seg0().virtualWidth(); }
EMSCRIPTEN_KEEPALIVE int sim_height() { return seg0().virtualHeight(); }
EMSCRIPTEN_KEEPALIVE int sim_mode_count() { return strip.getModeCount(); }
EMSCRIPTEN_KEEPALIVE const char *sim_mode_data(int id) { return strip.getModeData(id); }
EMSCRIPTEN_KEEPALIVE const char *sim_palette_names() { return JSON_palette_names; }
EMSCRIPTEN_KEEPALIVE void sim_set_mode(int fx, int loadDefaults) { seg0().setMode(fx, loadDefaults != 0); }
EMSCRIPTEN_KEEPALIVE void sim_set_color(int slot, int r, int g, int b, int w) { seg0().setColor(slot, RGBW32(r, g, b, w)); }
EMSCRIPTEN_KEEPALIVE uint32_t sim_get_color(int slot) { return seg0().colors[slot < NUM_COLORS ? slot : 0]; }
EMSCRIPTEN_KEEPALIVE void sim_reset() { seg0().markForReset(); }
EMSCRIPTEN_KEEPALIVE void sim_seed(uint32_t s) { g_rng = s ? s : 1; }
// Segment fields by key, the keys of /json/state: 0 sx, 1 ix, 2 c1, 3 c2, 4 c3, 5 o1, 6 o2, 7 o3, 8 pal, 9 si (sound simulation),
// 10 m12 (1D→2D mapping), 11 rev, 12 mi, 13 rY, 14 mY, 15 fx, 16 bri (strip), 17 opacity (segment bri)
EMSCRIPTEN_KEEPALIVE void sim_set(int key, int v) {
  Segment &s = seg0();
  switch (key) {
    case 0: s.speed = v; break;         case 1: s.intensity = v; break;
    case 2: s.custom1 = v; break;       case 3: s.custom2 = v; break;     case 4: s.custom3 = v & 31; break;
    case 5: s.check1 = v; break;        case 6: s.check2 = v; break;      case 7: s.check3 = v; break;
    case 8: s.setPalette(v); break;     case 9: s.soundSim = v & 3; break;
    case 10: s.setGeometry(s.start, s.stop, s.grouping, s.spacing, s.offset, s.startY, s.stopY, v & 7); break;
    case 11: s.setOption(SEG_OPTION_REVERSED, v); break;   case 12: s.setOption(SEG_OPTION_MIRROR, v); break;
    case 13: s.setOption(SEG_OPTION_REVERSED_Y, v); break; case 14: s.setOption(SEG_OPTION_MIRROR_Y, v); break;
    case 15: s.setMode(v, false); break; case 16: bri = v; strip.setBrightness(v); break;
    case 17: s.setOpacity(v); break;
  }
}
EMSCRIPTEN_KEEPALIVE int sim_get(int key) {
  Segment &s = seg0();
  switch (key) {
    case 0: return s.speed;    case 1: return s.intensity; case 2: return s.custom1; case 3: return s.custom2; case 4: return s.custom3;
    case 5: return s.check1;   case 6: return s.check2;    case 7: return s.check3;  case 8: return s.palette;  case 9: return s.soundSim;
    case 10: return s.map1D2D; case 11: return s.reverse;  case 12: return s.mirror; case 13: return s.reverse_y; case 14: return s.mirror_y;
    case 15: return s.mode;    case 16: return bri;        case 17: return s.opacity;
  }
  return 0;
}
}
