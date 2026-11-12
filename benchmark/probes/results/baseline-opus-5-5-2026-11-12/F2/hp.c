/*
 * 2nd-order Butterworth high-pass (0.1 Hz @ 1 kHz), integer arithmetic only.
 *
 * Structure: topology-preserving-transform (trapezoidal) state-variable
 * filter. With g = tan(pi*fc/fs) and k = 2R = sqrt(2), it is exactly the
 * bilinear-transformed (prewarped) Butterworth that scipy's butter() designs:
 *
 *   hp = (x - (k + g)*s1 - s2) * D,     D = 1 / (1 + k*g + g^2)
 *   v1 = g*hp;  bp = v1 + s1;  s1 = bp + v1
 *   v2 = g*bp;  lp = v2 + s2;  s2 = lp + v2
 *
 * Why this form instead of a direct-form biquad: the poles sit ~4e-4 from
 * z = 1, so direct-form coefficients (a1 ~ -1.99911, a2 ~ 0.99911) need
 * extreme precision, and a DF-II state grows like x / (1 + a1 + a2) ~ 2.5e6*x
 * for DC offsets. In the SVF the low-pass state s2 simply tracks the
 * electrode offset (bounded by the int16 input range) and s1 stays small,
 * so the filter is well conditioned for large offsets and unbounded run time.
 *
 * Numbers: states are int64 in Q32 (|value| < 2^18 => < 2^50, ample headroom).
 * Coefficients are int32 with per-coefficient Q formats; products use an
 * exact 64x32 -> shifted 64 multiply built from 32x32->64 pieces (portable C,
 * fine on Cortex-M0 via the compiler's 64-bit helpers). Integer-only.
 */
#include "hp.h"

/* g = tan(pi*0.1/1000) = 3.14159275694e-4, Q42 */
#define G_Q42      ((int32_t)1381687106)
/* k + g = sqrt(2) + g = 1.41452772164879, Q30 */
#define KG_Q30     ((int32_t)1518837576)
/* D = 1/(1 + sqrt(2)*g + g^2) = 0.99955581038761, Q31 */
#define D_Q31      ((int32_t)2146529758)

#define FRAC 32

static int64_t s1; /* band-pass integrator state, Q32 */
static int64_t s2; /* low-pass integrator state (tracks offset), Q32 */

/* (a * c) / 2^sh for int64 a, int32 c, 1 <= sh <= 62, without 128-bit
 * types (floor for sh <= 32, round-to-nearest for sh > 32).
 * a = ah*2^32 + al with al in [0, 2^32). Caller guarantees the result fits. */
static int64_t mul_shr(int64_t a, int32_t c, unsigned sh)
{
    int64_t  ah = a >> 32;                      /* arithmetic shift */
    uint32_t al = (uint32_t)(a & 0xFFFFFFFFu);
    int64_t  lo = (int64_t)al * (int64_t)c;     /* |lo| < 2^63 */
    int64_t  t;
    if (sh <= 32) {
        t = ah * (int64_t)c * ((int64_t)1 << (32 - sh)) + (lo >> sh);
    } else {
        t = ah * (int64_t)c + (lo >> 32);       /* floor(a*c / 2^32) */
        t += (int64_t)1 << (sh - 33);
        t >>= (sh - 32);
    }
    return t;
}

void hp_reset(void)
{
    s1 = 0;
    s2 = 0;
}

int16_t hp_step(int16_t x)
{
    int64_t xq = (int64_t)x << FRAC;
    int64_t u, hp, v1, bp, v2, lp, r;

    /* hp = (x - (k+g)*s1 - s2) * D */
    u  = xq - s2 - mul_shr(s1, KG_Q30, 30);
    hp = mul_shr(u, D_Q31, 31);

    v1 = mul_shr(hp, G_Q42, 42);
    bp = v1 + s1;
    s1 = bp + v1;

    v2 = mul_shr(bp, G_Q42, 42);
    lp = v2 + s2;
    s2 = lp + v2;

    /* round Q32 -> integer, saturate to int16 */
    r = (hp + ((int64_t)1 << (FRAC - 1))) >> FRAC;
    if (r > 32767)  r = 32767;
    if (r < -32768) r = -32768;
    return (int16_t)r;
}
