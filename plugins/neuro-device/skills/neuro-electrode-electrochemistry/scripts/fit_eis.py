"""Fit an electrode impedance spectrum with Rs + (Rct || CPE).

python fit_eis.py --data eis.csv        columns: freq_hz,z_mag_ohm,phase_deg

CPE impedance: 1 / (Q (j w)^alpha). Prints fitted parameters, |Z| and phase at
1 kHz (measured and fitted) and the relative RMS residual.
"""
import argparse
import csv
import json

import numpy as np
from scipy.optimize import least_squares


def model(p, w):
    rs, rct, q, alpha = p
    zc = 1 / (q * (1j * w) ** alpha)
    return rs + rct * zc / (rct + zc)


def fit(f, mag, ph):
    w = 2 * np.pi * f
    z = mag * np.exp(1j * np.deg2rad(ph))
    rs0 = max(float(np.min(mag)) * 0.9, 1.0)
    q0 = 1 / (float(mag[np.argmin(f)]) * w.min())

    def res(lp):
        zm = model(np.exp(lp[:3]).tolist() + [lp[3]], w)
        return np.r_[np.log(np.abs(zm)) - np.log(mag), (np.angle(zm) - np.angle(z))]

    best = None
    for rct0 in (1e3, 1e5, 1e7, 1e9):
        x0 = [np.log(rs0), np.log(rct0), np.log(q0), 0.85]
        r = least_squares(res, x0, bounds=([-np.inf] * 3 + [0.3], [np.inf] * 3 + [1.0]))
        if best is None or r.cost < best.cost:
            best = r
    rs, rct, q = np.exp(best.x[:3])
    alpha = best.x[3]
    zf = model([rs, rct, q, alpha], w)
    rel = np.sqrt(np.mean(np.abs(zf - z) ** 2 / np.abs(z) ** 2))
    z1k = model([rs, rct, q, alpha], np.array([2 * np.pi * 1000]))[0]
    meas1k = float(np.interp(np.log(1000), np.log(f), mag)) if f.min() <= 1000 <= f.max() else None
    return {
        "Rs_ohm": float(f"{rs:.4g}"), "Rct_ohm": float(f"{rct:.4g}"),
        "CPE_Q": float(f"{q:.4g}"), "CPE_alpha": round(float(alpha), 3),
        "z_1kHz_fit_ohm": float(f"{abs(z1k):.4g}"), "phase_1kHz_fit_deg": round(float(np.degrees(np.angle(z1k))), 1),
        "z_1kHz_measured_ohm": None if meas1k is None else float(f"{meas1k:.4g}"),
        "relative_rms_residual": round(float(rel), 4),
        "note": "Rct far above |Z| in the measured band means the interface is mostly capacitive there; "
                "alpha near 1 is ideal capacitance, lower alpha means a rougher or porous surface.",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(a.data))]
    f = np.array([float(r["freq_hz"]) for r in rows])
    o = np.argsort(f)
    mag = np.array([float(r["z_mag_ohm"]) for r in rows])[o]
    ph = np.array([float(r["phase_deg"]) for r in rows])[o]
    print(json.dumps(fit(f[o], mag, ph), indent=2))
