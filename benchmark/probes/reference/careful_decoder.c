#include "decoder.h"
/* careful reference: Q28 coefficients, int64 accumulators, Q8 signal, Q16 log2 */
static const int64_t C[4][5] = {
{835345, 1670691, 835345, -340186426, 132550525},
{268435456, 536870912, 268435456, -439439478, 188431746},
{268435456, -536870912, 268435456, -345309222, 196438725},
{268435456, -536870912, 268435456, -501525856, 244049815}
};
static int64_t log2_q16(uint64_t v) {
    if (v == 0) return -(64LL << 16);
    int p = 63; while (!(v >> p)) p--;
    uint64_t m = (p >= 31) ? (v >> (p - 31)) : (v << (31 - p));   /* m in [2^31, 2^32), Q31 */
    int64_t r = (int64_t)p << 16;
    for (int i = 15; i >= 0; i--) {
        m = (m * m) >> 31;
        if (m >= (1ULL << 32)) { m >>= 1; r += 1LL << i; }
    }
    return r;
}
static uint64_t band_var(const int16_t *x) {
    int32_t s = 0; for (int n = 0; n < 250; n++) s += x[n];
    int32_t mean = (s >= 0 ? s + 125 : s - 125) / 250;
    int64_t xs[3][3] = {{0}}, ys[4][2] = {{0}}, x1[4] = {0}, x2[4] = {0};
    (void)xs;
    int64_t sum = 0, sum2 = 0;
    for (int n = 0; n < 250; n++) {
        int64_t v = ((int64_t)x[n] - mean) * 256;
        for (int k = 0; k < 4; k++) {
            int64_t acc = C[k][0]*v + C[k][1]*x1[k] + C[k][2]*x2[k] - C[k][3]*ys[k][0] - C[k][4]*ys[k][1];
            int64_t y = (acc + (1LL << 27)) >> 28;
            x2[k] = x1[k]; x1[k] = v; ys[k][1] = ys[k][0]; ys[k][0] = y; v = y;
        }
        int64_t w = v >> 4; sum += w; sum2 += w * w;
    }
    int64_t mean_y = sum / 250;
    int64_t var = sum2 / 250 - mean_y * mean_y;
    return var > 0 ? (uint64_t)var : 1;
}
int decode_trial(const int16_t x[2][250]) {
    int64_t d = log2_q16(band_var(x[0])) - log2_q16(band_var(x[1]));
    return d > -28365;   /* (ln v0 - ln v1) + 0.3 > 0  <=>  log2 diff > -0.3/ln 2 */
}
