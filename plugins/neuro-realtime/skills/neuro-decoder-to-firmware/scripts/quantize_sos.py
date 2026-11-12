"""Quantize an IIR filter (second-order sections) for fixed-point firmware.

Design and quantize:
  python quantize_sos.py --design butter --order 4 --band 8 30 --btype bandpass --fs 250
         [--coef-bits 30] [--input-bits 16] [--c-header sos_coefs.h] [--name BP]
Or start from saved sections:
  python quantize_sos.py --sos sos.npy --fs 250 ...

Reports per section: coefficient scaling, pole radius before/after quantization,
worst-case gain from the input to that section's output (L1 norm of the impulse
response), headroom bits, and the accumulator width a direct-form-I biquad needs.
"""
import argparse
import json

import numpy as np
from scipy import signal


def design(a):
    if a.sos:
        return np.load(a.sos)
    wn = a.band if len(a.band) > 1 else a.band[0]
    f = {"butter": signal.butter, "cheby1": lambda *x, **k: signal.cheby1(x[0], a.ripple, *x[1:], **k),
         "bessel": signal.bessel}[a.design]
    return f(a.order, wn, btype=a.btype, fs=a.fs, output="sos")


def analyse(sos, coef_bits, input_bits, n_imp=1 << 16):
    scale = 1 << coef_bits
    q = np.round(sos * scale).astype(np.int64)
    rows, cum = [], np.zeros(n_imp)
    cum[0] = 1.0
    for k, (s, sq) in enumerate(zip(sos, q)):
        cum = signal.sosfilt(s[None, :], cum)
        l1 = float(np.sum(np.abs(cum)))
        r = np.abs(np.roots(s[3:]))
        rq = np.abs(np.roots(sq[3:] / scale))
        coef_max = float(np.max(np.abs(sq)))
        state_bits = input_bits + int(np.ceil(np.log2(max(l1, 1.0))))
        acc_bits = int(np.ceil(np.log2(coef_max + 1))) + state_bits + 3  # 5 products
        rows.append({
            "section": k, "pole_radius": round(float(r.max()), 8), "pole_radius_quantized": round(float(rq.max()), 8),
            "stable_after_quantization": bool(rq.max() < 1),
            "max_coef_int": int(coef_max), "coef_bits_needed_signed": int(np.ceil(np.log2(coef_max + 1))) + 1,
            "worst_case_gain_input_to_here": round(l1, 3), "headroom_bits": int(np.ceil(np.log2(max(l1, 1.0)))),
            "state_bits_needed": state_bits, "accumulator_bits_needed": acc_bits,
        })
    return q, rows


def c_header(q, coef_bits, name):
    lines = [f"/* {name}: {len(q)} second-order sections, coefficients scaled by 2^{coef_bits}.",
             "   Row: b0, b1, b2, a1, a2 (a0 = 1 implied). y = (b.x - a.y) >> COEF_BITS. */",
             "#include <stdint.h>", f"#define {name}_COEF_BITS {coef_bits}", f"#define {name}_N_SECTIONS {len(q)}",
             f"static const int64_t {name}_SOS[{len(q)}][5] = {{"]
    for row in q:
        lines.append("    {" + ", ".join(str(int(v)) for v in (row[0], row[1], row[2], row[4], row[5])) + "},")
    lines.append("};")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--design", default="butter", choices=["butter", "cheby1", "bessel"])
    ap.add_argument("--order", type=int, default=2)
    ap.add_argument("--band", type=float, nargs="+")
    ap.add_argument("--btype", default="bandpass")
    ap.add_argument("--fs", type=float, required=True)
    ap.add_argument("--ripple", type=float, default=0.5)
    ap.add_argument("--sos")
    ap.add_argument("--coef-bits", type=int, default=30)
    ap.add_argument("--input-bits", type=int, default=16)
    ap.add_argument("--c-header")
    ap.add_argument("--name", default="FILT")
    a = ap.parse_args()
    sos = design(a)
    q, rows = analyse(sos, a.coef_bits, a.input_bits)
    if a.c_header:
        open(a.c_header, "w").write(c_header(q, a.coef_bits, a.name))
    worst = max(r["accumulator_bits_needed"] for r in rows)
    print(json.dumps({"sections": rows, "accumulator_bits_needed_max": worst,
                      "recommendation": "64-bit accumulator" if worst > 31 else "32-bit accumulator is enough",
                      "c_header": a.c_header}, indent=2))
