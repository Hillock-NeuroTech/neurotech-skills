/*
 * Integer-only port of decoder.py for Cortex-M0 (no FPU, no libm).
 *
 * Python reference, per channel c:
 *   y_c = sosfilt(SOS, x_c - mean(x_c));  f_c = log(var(y_c))
 *   decision = (f_0 - f_1 + 0.3 > 0)
 * which is equivalent to  var(y_0) * e^0.3 > var(y_1)  (log is monotonic;
 * the degenerate zero-variance cases give the same answer as the reference).
 *
 * Implementation:
 *  - Mean removal is exact: c[n] = 250*x[n] - sum(x)  (= 250*(x - mean)).
 *    The common factor 250 cancels in the variance ratio. |c| < 2^24.
 *  - The input is placed in Q32 (c << 32). The 4 biquads (DF2-transposed,
 *    same structure as scipy's sosfilt) use Q60 coefficients; each product
 *    is computed exactly in 128 bits and rounded back to Q32. The worst-case
 *    (L1) gain of every state/output is < 4.2, so all states stay < 2^59
 *    for any int16 input, i.e. no overflow anywhere in the int16 range.
 *  - 250*var*250 = 250*sum(y^2) - (sum y)^2 is computed exactly with a small
 *    256-bit two's-complement integer type, then compared against
 *    var1 * 2^62 using K = round(e^0.3 * 2^62).
 */
#include "decoder.h"

#define NS 250
#define NSEC 4
#define COEF_SHIFT 60
#define SIG_SHIFT 32

/* b0, b1, b2, a1, a2 in Q60 (a0 = 1) for butter(4, [8,30], 'bandpass', fs=250, 'sos') */
static const int64_t SOS_Q60[NSEC][5] = {
    {INT64_C(3587780585990784), INT64_C(7175561171981567), INT64_C(3587780585990784),
     INT64_C(-1461089573188538112), INT64_C(569300169141558144)},
    {INT64_C(1152921504606846976), INT64_C(2305843009213693952), INT64_C(1152921504606846976),
     INT64_C(-1887378184907153920), INT64_C(809308184651809280)},
    {INT64_C(1152921504606846976), INT64_C(-2305843009213693952), INT64_C(1152921504606846976),
     INT64_C(-1483091817605964288), INT64_C(843697897728712832)},
    {INT64_C(1152921504606846976), INT64_C(-2305843009213693952), INT64_C(1152921504606846976),
     INT64_C(-2154037150749629952), INT64_C(1048185972109341184)},
};

/* round(exp(0.3) * 2^62) */
#define EXP_B_Q62 UINT64_C(6225124989749319313)

/* ---- signed 64x64 -> 128 multiply, rounded right shift by 60 ---- */
static int64_t mul_q60(int64_t a, int64_t b)
{
    int neg = 0;
    uint64_t ua, ub, a0, a1, b0, b1, p00, p01, p10, p11, mid, lo, hi, carry;

    if (a < 0) { ua = (uint64_t)0 - (uint64_t)a; neg = !neg; } else ua = (uint64_t)a;
    if (b < 0) { ub = (uint64_t)0 - (uint64_t)b; neg = !neg; } else ub = (uint64_t)b;

    a0 = ua & 0xFFFFFFFFu; a1 = ua >> 32;
    b0 = ub & 0xFFFFFFFFu; b1 = ub >> 32;
    p00 = a0 * b0; p01 = a0 * b1; p10 = a1 * b0; p11 = a1 * b1;

    mid = (p00 >> 32) + (p01 & 0xFFFFFFFFu) + (p10 & 0xFFFFFFFFu);
    lo = (p00 & 0xFFFFFFFFu) | (mid << 32);
    hi = p11 + (p01 >> 32) + (p10 >> 32) + (mid >> 32);

    /* add 2^59 for round-half-away-from-zero on the magnitude */
    {
        uint64_t r = UINT64_C(1) << (COEF_SHIFT - 1);
        uint64_t nlo = lo + r;
        carry = (nlo < lo) ? 1u : 0u;
        lo = nlo;
        hi += carry;
    }
    {
        uint64_t m = (hi << (64 - COEF_SHIFT)) | (lo >> COEF_SHIFT);
        return neg ? -(int64_t)m : (int64_t)m;
    }
}

/* ---- tiny 256-bit two's-complement integers (8 x 32-bit limbs) ---- */
#define BNL 8
typedef struct { uint32_t w[BNL]; } bn_t;

static void bn_from_i64(bn_t *r, int64_t v)
{
    uint64_t u = (uint64_t)v;
    uint32_t ext = (v < 0) ? 0xFFFFFFFFu : 0u;
    int i;
    r->w[0] = (uint32_t)u;
    r->w[1] = (uint32_t)(u >> 32);
    for (i = 2; i < BNL; i++) r->w[i] = ext;
}

static void bn_from_u64(bn_t *r, uint64_t u)
{
    int i;
    r->w[0] = (uint32_t)u;
    r->w[1] = (uint32_t)(u >> 32);
    for (i = 2; i < BNL; i++) r->w[i] = 0;
}

static void bn_add(bn_t *r, const bn_t *a, const bn_t *b)
{
    uint64_t c = 0;
    int i;
    for (i = 0; i < BNL; i++) {
        c += (uint64_t)a->w[i] + b->w[i];
        r->w[i] = (uint32_t)c;
        c >>= 32;
    }
}

static void bn_sub(bn_t *r, const bn_t *a, const bn_t *b)
{
    uint64_t br = 0;
    int i;
    for (i = 0; i < BNL; i++) {
        uint64_t d = (uint64_t)a->w[i] - b->w[i] - br;
        r->w[i] = (uint32_t)d;
        br = (d >> 32) & 1u;
    }
}

/* product modulo 2^256 (correct for signed values when the result fits) */
static void bn_mul(bn_t *r, const bn_t *a, const bn_t *b)
{
    uint32_t t[BNL];
    int i, j;
    for (i = 0; i < BNL; i++) t[i] = 0;
    for (i = 0; i < BNL; i++) {
        uint64_t c = 0;
        if (a->w[i] == 0) continue;
        for (j = 0; i + j < BNL; j++) {
            c += (uint64_t)a->w[i] * b->w[j] + t[i + j];
            t[i + j] = (uint32_t)c;
            c >>= 32;
        }
    }
    for (i = 0; i < BNL; i++) r->w[i] = t[i];
}

static int bn_is_neg(const bn_t *a) { return (a->w[BNL - 1] >> 31) & 1u; }

static int bn_is_zero(const bn_t *a)
{
    int i;
    for (i = 0; i < BNL; i++) if (a->w[i]) return 0;
    return 1;
}

/* 250^2 * var of one channel after mean removal and band-pass, exact
 * from the integer filter output (units: Q32^2). Always >= 0. */
static void channel_var(const int16_t *x, bn_t *v)
{
    int32_t sum = 0;
    int64_t z1[NSEC], z2[NSEC];
    bn_t s1, s2, t, n;
    int i, k;

    for (i = 0; i < NS; i++) sum += x[i];
    for (k = 0; k < NSEC; k++) { z1[k] = 0; z2[k] = 0; }
    bn_from_i64(&s1, 0);
    bn_from_i64(&s2, 0);

    for (i = 0; i < NS; i++) {
        int64_t c = (int64_t)NS * x[i] - sum;           /* |c| < 2^24 */
        int64_t s = (int64_t)((uint64_t)c << SIG_SHIFT); /* Q32 */
        for (k = 0; k < NSEC; k++) {
            const int64_t *q = SOS_Q60[k];
            int64_t y = mul_q60(q[0], s) + z1[k];
            z1[k] = mul_q60(q[1], s) - mul_q60(q[3], y) + z2[k];
            z2[k] = mul_q60(q[2], s) - mul_q60(q[4], y);
            s = y;
        }
        bn_from_i64(&t, s);
        bn_add(&s1, &s1, &t);
        bn_mul(&t, &t, &t);
        bn_add(&s2, &s2, &t);
    }

    /* n = 250 * sum(y^2) - (sum y)^2 */
    bn_from_i64(&t, NS);
    bn_mul(&n, &s2, &t);
    bn_mul(&t, &s1, &s1);
    bn_sub(v, &n, &t);
    if (bn_is_neg(v)) bn_from_i64(v, 0); /* cannot happen (Cauchy-Schwarz) */
}

int decode_trial(const int16_t x[2][250])
{
    bn_t v0, v1, lhs, rhs, k, d;

    channel_var(x[0], &v0);
    channel_var(x[1], &v1);

    /* log(v0) - log(v1) + 0.3 > 0  <=>  v0 * e^0.3 > v1 */
    bn_from_u64(&k, EXP_B_Q62);
    bn_mul(&lhs, &v0, &k);
    bn_from_u64(&k, UINT64_C(1) << 62);
    bn_mul(&rhs, &v1, &k);
    bn_sub(&d, &lhs, &rhs);
    return (!bn_is_neg(&d) && !bn_is_zero(&d)) ? 1 : 0;
}
