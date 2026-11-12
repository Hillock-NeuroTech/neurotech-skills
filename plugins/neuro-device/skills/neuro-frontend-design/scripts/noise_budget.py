"""Input-referred noise budget for a biopotential front end.

python noise_budget.py --en-nv 30 --fc-hz 10 --in-fa 10 --z-mag-kohm 10 --z-real-kohm 5 \
       --band 0.5 100 [--gain 24 --adc-bits 24 --vref 4.5] [--temp-c 37] [--channels-ref 1]

Sources (integrated over the band, input-referred, uV rms):
  amplifier voltage noise   en^2 * [(f2 - f1) + fc * ln(f2/f1)]
  amplifier current noise   (in * |Z|)^2 * (f2 - f1)
  electrode thermal noise   4 k T Re(Z) * (f2 - f1)
  ADC quantisation          (LSB / sqrt(12)) / gain
Totals add in quadrature. Peak-to-peak is estimated as 6.6 x rms.
"""
import argparse
import json
import math

K = 1.380649e-23


def budget(en_nv, fc, in_fa, zmag_k, zreal_k, f1, f2, gain, bits, vref, temp_c):
    bw = f2 - f1
    T = temp_c + 273.15
    src = {}
    src["amplifier_voltage_noise"] = math.sqrt((en_nv * 1e-9) ** 2 * (bw + fc * math.log(f2 / f1)))
    src["amplifier_current_noise"] = in_fa * 1e-15 * zmag_k * 1e3 * math.sqrt(bw)
    src["electrode_thermal_noise"] = math.sqrt(4 * K * T * zreal_k * 1e3 * bw)
    if bits and vref and gain:
        lsb = 2 * vref / 2 ** bits
        src["adc_quantisation"] = lsb / math.sqrt(12) / gain
    total = math.sqrt(sum(v ** 2 for v in src.values()))
    uv = {k: round(v * 1e6, 4) for k, v in src.items()}
    return {
        "band_hz": [f1, f2],
        "sources_uV_rms": uv,
        "total_uV_rms": round(total * 1e6, 4),
        "total_uV_pp_approx": round(total * 6.6e6, 3),
        "dominant_source": max(uv, key=uv.get),
        "share_of_power_percent": {k: round(100 * (v / (total * 1e6)) ** 2, 1) for k, v in uv.items()},
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--en-nv", type=float, required=True, help="voltage noise density, nV/sqrtHz (white)")
    ap.add_argument("--fc-hz", type=float, default=0.0, help="1/f corner frequency")
    ap.add_argument("--in-fa", type=float, default=0.0, help="current noise density, fA/sqrtHz")
    ap.add_argument("--z-mag-kohm", type=float, default=0.0)
    ap.add_argument("--z-real-kohm", type=float, default=0.0)
    ap.add_argument("--band", type=float, nargs=2, required=True)
    ap.add_argument("--gain", type=float)
    ap.add_argument("--adc-bits", type=int)
    ap.add_argument("--vref", type=float, help="ADC reference; full scale is +/- vref")
    ap.add_argument("--temp-c", type=float, default=37.0)
    a = ap.parse_args()
    print(json.dumps(budget(a.en_nv, a.fc_hz, a.in_fa, a.z_mag_kohm, a.z_real_kohm, a.band[0], a.band[1],
                            a.gain, a.adc_bits, a.vref, a.temp_c), indent=2))
