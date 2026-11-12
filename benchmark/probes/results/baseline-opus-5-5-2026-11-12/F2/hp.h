#ifndef HP_H
#define HP_H

#include <stdint.h>

/* 2nd-order Butterworth high-pass, fc = 0.1 Hz, fs = 1000 Hz, causal.
 * Integer-only implementation (no FPU needed). Matches
 * scipy.signal.sosfilt(butter(2, 0.1, 'highpass', fs=1000, output='sos'), x)
 * with zero initial state, rounded and clipped to int16. */

void hp_reset(void);
int16_t hp_step(int16_t x);

#endif /* HP_H */
