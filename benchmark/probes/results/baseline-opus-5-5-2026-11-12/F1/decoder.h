#ifndef DECODER_H
#define DECODER_H

#include <stdint.h>

/* Motor-imagery decoder, integer-only port of decoder.py.
 * x: 2 channels x 250 samples of int16 ADC counts (250 Hz).
 * Returns 0 or 1. */
int decode_trial(const int16_t x[2][250]);

#endif /* DECODER_H */
