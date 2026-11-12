---
name: neuro-decoder-to-firmware
description: Port neural signal processing or a BCI decoder from Python/MATLAB to embedded C on microcontrollers or DSPs (Cortex-M0/M4/M7, ESP32, nRF, implant or headstage firmware), including fixed-point/integer-only versions. Use whenever the user moves filters, band power, CSP, LDA, spike detection or a small neural network onto a device, asks about Q formats, overflow, coefficient quantization, or needs firmware to match a reference implementation.
---

# Decoder to firmware

The firmware must give the same decisions as the reference on every input
the hardware can produce, including full-scale and near-silent signals.
Work from a bit-accurate plan, then test against the reference with
vectors that cover the extremes.

## 1. Inventory the reference

List every stage with its numeric range: input type and range (int16 ADC
counts, offsets), filters (order, type, band, fs), features (variance,
log, power), classifier (weights, bias, comparison). Note where the
reference relies on floating point (log, division, mean removal).

## 2. Filters

- Always implement IIR filters as cascaded second-order sections, never
  as one high-order direct form (coefficient sensitivity grows with order).
- Generate quantized coefficients and headroom with the bundled script:

```bash
python scripts/quantize_sos.py --design butter --order 4 --band 8 30 --btype bandpass --fs 250 \
       --coef-bits 30 --input-bits 16 --c-header sos_coefs.h
```

It reports, per section, the coefficient format, pole radius before and
after quantization (stability margin), the worst-case gain from the input
to each section output (L1 norm of the impulse response), the bits of
headroom needed, and the accumulator width required. It writes a C header.
- Poles near z = 1 (high-pass below about 1 Hz at kHz rates) need more
  coefficient and state precision; use 32-bit coefficients with 64-bit
  accumulation, or a state-variable / error-feedback structure.
- Saturate on output; never let values wrap.

## 3. Features and classifier without floats

- Mean removal: work with sums (`n*x - sum`) to avoid division.
- Variance: sum of squares in 64 bits (int16 squared times hundreds of
  samples overflows 32 bits).
- Log: avoid it where possible. For LDA on log-variance,
  `w*(log v0 - log v1) + b > 0` becomes `v0^w * e^b > v1^w`; for w = 1
  compare `v0 * K > v1` with K = round(e^b * 2^q). Otherwise use a
  fixed-point log2 (leading-zero count plus a lookup or polynomial).
- Keep weights in a Q format chosen from their range.

## 4. Verify

1. Write a bit-exact Python model of the C arithmetic, or compile the C
   on the host and call it from Python.
2. Test vectors: typical trials, full-scale (near +/-32767), near-silent,
   large DC offsets, constant input, single spikes, and trials close to
   the decision boundary.
3. Require identical decisions (or report the mismatch rate and where it
   occurs) and filter output error within one LSB.
4. Cross-compile for the target and estimate cycles per sample against the
   sample period.

## Output

C files with the requested API, the coefficient header, the headroom
report, the test-vector results, and the cycle estimate.
