#include "hp.h"
/* careful reference: Q30 coefficients, 128-bit accumulator, Q24 state */
typedef __int128 i128;
static const int64_t B0 = 1073264879, B1 = -2146529758, B2 = 1073264879, A1 = -2146529546, A2 = 1072788146;
static int64_t x1, x2, y1, y2;
void hp_reset(void) { x1 = x2 = y1 = y2 = 0; }
int16_t hp_step(int16_t x) {
    int64_t xs = (int64_t)x << 24;
    i128 acc = (i128)B0*xs + (i128)B1*x1 + (i128)B2*x2 - (i128)A1*y1 - (i128)A2*y2;
    int64_t y = (int64_t)((acc + ((i128)1 << 29)) >> 30);
    x2 = x1; x1 = xs; y2 = y1; y1 = y;
    int64_t out = (y + (1 << 23)) >> 24;
    if (out > 32767) out = 32767; if (out < -32768) out = -32768;
    return (int16_t)out;
}
