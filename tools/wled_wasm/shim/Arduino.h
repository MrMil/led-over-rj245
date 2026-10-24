#pragma once
// Just enough Arduino for WLED's effect sources to compile on a host: the integer types, the maths macros, a clock
// that the simulator advances, and a String class that only ever reaches debug output.
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <algorithm>
#include <string>
#include "pgmspace.h"

typedef uint8_t byte;
typedef bool boolean;

#ifndef PI
  #define PI 3.1415926535897932384626433832795
#endif
#define HALF_PI    (PI / 2.0)
#define TWO_PI     (PI * 2.0)
#define DEG_TO_RAD 0.017453292519943295769236907684886
#define RAD_TO_DEG 57.295779513082320876798154814105
#ifndef M_TWOPI
  #define M_TWOPI (2.0 * PI)
#endif

#define IRAM_ATTR
#define IRAM_ATTR_YN
#ifndef WLED_O2_ATTR
  #define WLED_O2_ATTR
#endif
#ifndef WLED_O3_ATTR
  #define WLED_O3_ATTR
#endif

using std::min;
using std::max;
#define constrain(amt, low, high) ((amt) < (low) ? (low) : ((amt) > (high) ? (high) : (amt)))
static inline long map(long x, long in_min, long in_max, long out_min, long out_max) {
  const long run = in_max - in_min;
  if (run == 0) return out_min;
  return (x - in_min) * (out_max - out_min) / run + out_min;
}
#define bitRead(value, bit)            (((value) >> (bit)) & 0x01)
#define bitSet(value, bit)             ((value) |= (1UL << (bit)))
#define bitClear(value, bit)           ((value) &= ~(1UL << (bit)))
#define bitWrite(value, bit, bitvalue) ((bitvalue) ? bitSet(value, bit) : bitClear(value, bit))
#define lowByte(w)  ((uint8_t)((w) & 0xff))
#define highByte(w) ((uint8_t)((w) >> 8))
#define sq(x) ((x) * (x))
#define radians(deg) ((deg) * DEG_TO_RAD)
#define degrees(rad) ((rad) * RAD_TO_DEG)
typedef unsigned int uint;

// TimeLib's accessors, on the simulated local time (Scrolling Text shows the clock)
#include <time.h>
static inline struct tm _simTm(time_t t) { struct tm out; gmtime_r(&t, &out); return out; }
static inline int hour(time_t t)    { return _simTm(t).tm_hour; }
static inline int minute(time_t t)  { return _simTm(t).tm_min; }
static inline int second(time_t t)  { return _simTm(t).tm_sec; }
static inline int day(time_t t)     { return _simTm(t).tm_mday; }
static inline int month(time_t t)   { return _simTm(t).tm_mon + 1; }
static inline int year(time_t t)    { return _simTm(t).tm_year + 1900; }
static inline int weekday(time_t t) { return _simTm(t).tm_wday + 1; }
static inline const char *monthStr(int m)      { static const char *n[] = {"", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"}; return n[m >= 1 && m <= 12 ? m : 0]; }
static inline const char *monthShortStr(int m) { static const char *n[] = {"", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}; return n[m >= 1 && m <= 12 ? m : 0]; }
static inline const char *dayStr(int d)        { static const char *n[] = {"", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}; return n[d >= 1 && d <= 7 ? d : 0]; }
static inline const char *dayShortStr(int d)   { static const char *n[] = {"", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"}; return n[d >= 1 && d <= 7 ? d : 0]; }

// The simulated clock: sim_main.cpp sets it from the page each frame, so millis() and strip.now agree.
uint32_t millis();
uint32_t micros();
void yield();
void delay(uint32_t ms);
void delayMicroseconds(uint32_t us);

// A String that is only ever concatenated for debug prints (WLED_DEBUG_PS is off, so even that is compiled out).
class String {
 public:
  String() {}
  String(const char *s) : _s(s ? s : "") {}
  String(const std::string &s) : _s(s) {}
  String(int v) : _s(std::to_string(v)) {}
  String(unsigned v) : _s(std::to_string(v)) {}
  String(long v) : _s(std::to_string(v)) {}
  String(unsigned long v) : _s(std::to_string(v)) {}
  String(float v) : _s(std::to_string(v)) {}
  String(double v) : _s(std::to_string(v)) {}
  const char *c_str() const { return _s.c_str(); }
  size_t length() const { return _s.size(); }
  long toInt() const { return atol(_s.c_str()); }
  float toFloat() const { return (float)atof(_s.c_str()); }
  String operator+(const String &o) const { return String(_s + o._s); }
  String &operator+=(const String &o) { _s += o._s; return *this; }
  bool operator==(const String &o) const { return _s == o._s; }
  char operator[](size_t i) const { return _s[i]; }
  char charAt(size_t i) const { return i < _s.size() ? _s[i] : 0; }
  bool endsWith(const String &o) const { return _s.size() >= o._s.size() && _s.compare(_s.size() - o._s.size(), o._s.size(), o._s) == 0; }
  bool startsWith(const String &o) const { return _s.compare(0, o._s.size(), o._s) == 0; }
  int indexOf(char c, size_t from = 0) const { size_t p = _s.find(c, from); return p == std::string::npos ? -1 : (int)p; }
  int indexOf(const String &o, size_t from = 0) const { size_t p = _s.find(o._s, from); return p == std::string::npos ? -1 : (int)p; }
  String substring(size_t a) const { return String(a < _s.size() ? _s.substr(a) : std::string()); }
  String substring(size_t a, size_t b) const { return String(a < _s.size() ? _s.substr(a, b > a ? b - a : 0) : std::string()); }
 private:
  std::string _s;
};
static inline String operator+(const char *a, const String &b) { return String(a) + b; }

class Print {
 public:
  template <class T> size_t print(const T &) { return 0; }
  template <class T> size_t println(const T &) { return 0; }
  size_t println() { return 0; }
  size_t printf(const char *, ...) { return 0; }
  size_t printf_P(const char *, ...) { return 0; }
};
class HardwareSerial : public Print {};
extern HardwareSerial Serial;
