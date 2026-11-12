#include "decoder.h"
/* naive reference: Q14 coefficients, int32 everything, integer msb as log */
static const int32_t C[4][5] = {
{51, 102, 51, -20763, 8090},
{16384, 32768, 16384, -26821, 11501},
{16384, -32768, 16384, -21076, 11990},
{16384, -32768, 16384, -30611, 14896}
};
static int32_t band_var(const int16_t *x) {
    int32_t s = 0; for (int n = 0; n < 250; n++) s += x[n];
    int16_t mean = (int16_t)(s / 250);
    int16_t x1[4] = {0}, x2[4] = {0}, y1[4] = {0}, y2[4] = {0};
    int32_t sum2 = 0;
    for (int n = 0; n < 250; n++) {
        int16_t v = (int16_t)(x[n] - mean);
        for (int k = 0; k < 4; k++) {
            int32_t acc = C[k][0]*v + C[k][1]*x1[k] + C[k][2]*x2[k] - C[k][3]*y1[k] - C[k][4]*y2[k];
            int16_t y = (int16_t)(acc >> 14);
            x2[k] = x1[k]; x1[k] = v; y2[k] = y1[k]; y1[k] = y; v = y;
        }
        sum2 += (int32_t)v * v;
    }
    return sum2 / 250;
}
static int ilog2(int32_t v) { int p = 0; while (v > 1) { v >>= 1; p++; } return p; }
int decode_trial(const int16_t x[2][250]) {
    return ilog2(band_var(x[0])) - ilog2(band_var(x[1])) >= 0;
}
