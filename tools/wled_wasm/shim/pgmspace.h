#pragma once
// Arduino's flash-string machinery, reduced to the identity: a host build has one flat address space, but WLED's
// sources are written against these names, so they have to exist.
#include <stdint.h>
#include <string.h>
#include <stdio.h>

#define PROGMEM
#define PGM_P            const char *
#define PSTR(s)          (s)
#define FPSTR(p)         (p)
#define F(s)             (s)
#define __FlashStringHelper char

static inline uint8_t  pgm_read_byte(const void *p)      { return *(const uint8_t  *)p; }
static inline uint8_t  pgm_read_byte_near(const void *p) { return *(const uint8_t  *)p; }
static inline uint16_t pgm_read_word(const void *p)      { return *(const uint16_t *)p; }
static inline uint32_t pgm_read_dword(const void *p)     { return *(const uint32_t *)p; }
static inline float    pgm_read_float(const void *p)     { return *(const float    *)p; }
static inline void    *pgm_read_ptr(const void *p)       { return *(void * const  *)p; }

#define memcpy_P         memcpy
#define strlen_P         strlen
#define strcpy_P         strcpy
#define strncpy_P        strncpy
#define strcmp_P         strcmp
#define strncmp_P        strncmp
#define strstr_P         strstr
#define strchr_P         strchr
#define snprintf_P       snprintf
#define sprintf_P        sprintf
#define memcmp_P         memcmp
