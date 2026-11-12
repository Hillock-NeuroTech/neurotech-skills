#include "hp.h"
/* naive reference: Q14 coefficients, int32 accumulator, int16 state */
static const int32_t B0 = 16377, B1 = -32753, B2 = 16377, A1 = -32753, A2 = 16369;
static int16_t x1, x2, y1, y2;
void hp_reset(void) { x1 = x2 = y1 = y2 = 0; }
int16_t hp_step(int16_t x) {
    int32_t acc = B0*x + B1*x1 + B2*x2 - A1*y1 - A2*y2;
    int16_t y = (int16_t)(acc >> 14);
    x2 = x1; x1 = x; y2 = y1; y1 = y;
    return y;
}
