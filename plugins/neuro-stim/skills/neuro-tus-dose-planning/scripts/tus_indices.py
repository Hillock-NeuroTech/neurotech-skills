#!/usr/bin/env python3
"""Ultrasound exposure indices for a transcranial ultrasound (TUS) protocol,
compared with the ITRUSST levels for non-significant risk.

    python3 tus_indices.py --pnp-mpa 0.8 --freq-mhz 0.5 --pulse-ms 0.3 --prf-hz 1000 \
        --train-s 0.3 --train-interval-s 3 --temps temps.csv

Inputs are IN SITU values at the target (from simulation or derated
measurement), not free-field values. Outputs: MI, Isppa, Ispta, duty cycles,
and thermal dose (CEM43) from a temperature time series if given.

ITRUSST consensus (Aubry et al. 2025, Brain Stimulation 18(6):1896-1905,
doi:10.1016/j.brs.2025.10.007): non-significant risk if MI (or MItc) <= 1.9,
and for heating if ANY of: peak rise <= 2 C (or peak <= 39 C from 37 C);
thermal dose <= 2 CEM43 brain, 16 bone, 21 skin; or TI within the values
tabulated for the exposure time. These are levels, not safety limits.
Research support only; not clinical or regulatory sign-off.
"""
import argparse
import json
import sys

import numpy as np

ITRUSST_MI = 1.9
ITRUSST_DT_C = 2.0
ITRUSST_CEM43 = {"brain": 2.0, "bone": 16.0, "skin": 21.0}
FDA_DIAGNOSTIC_ISPTA_MW_CM2 = 720.0   # diagnostic-imaging reference (Ispta.3), not a TUS limit


def mechanical_index(pnp_mpa, freq_mhz):
    """MI = peak negative pressure (MPa) / sqrt(centre frequency in MHz)."""
    return pnp_mpa / np.sqrt(freq_mhz)


def pulse_intensity_w_cm2(p_mpa, rho=1000.0, c=1500.0):
    """Spatial-peak pulse-average intensity for a sinusoidal burst: p^2 / (2 rho c), in W/cm^2."""
    p = p_mpa * 1e6
    return p * p / (2.0 * rho * c) / 1e4


def cem43(temps_c, dt_s):
    """Cumulative equivalent minutes at 43 C (Sapareto & Dewey): sum R^(43-T) dt/60."""
    t = np.asarray(temps_c, dtype=float)
    r = np.where(t >= 43.0, 0.5, 0.25)
    return float(np.sum(r ** (43.0 - t)) * dt_s / 60.0)


def indices(pnp_mpa, freq_mhz, pulse_ms, prf_hz, train_s=None, train_interval_s=None,
            p_peak_mpa=None, rho=1000.0, c=1500.0):
    pulse_duty = pulse_ms / 1000.0 * prf_hz
    if not 0 < pulse_duty <= 1:
        raise ValueError(f"pulse duty cycle {pulse_duty:.3f} is impossible: check pulse length and PRF")
    train_duty = (train_s / train_interval_s) if (train_s and train_interval_s) else 1.0
    isppa = pulse_intensity_w_cm2(p_peak_mpa if p_peak_mpa else pnp_mpa, rho, c)
    ispta_mw = isppa * pulse_duty * train_duty * 1000.0
    mi = mechanical_index(pnp_mpa, freq_mhz)
    return {
        "MI": round(float(mi), 3),
        "Isppa_W_cm2": round(float(isppa), 3),
        "pulse_duty_cycle": round(float(pulse_duty), 4),
        "train_duty_cycle": round(float(train_duty), 4),
        "Ispta_mW_cm2": round(float(ispta_mw), 1),
        "Ispta_within_pulse_train_mW_cm2": round(float(isppa * pulse_duty * 1000.0), 1),
        "MI_within_ITRUSST": bool(mi <= ITRUSST_MI),
        "Ispta_vs_FDA_diagnostic_720": "below" if ispta_mw <= FDA_DIAGNOSTIC_ISPTA_MW_CM2 else "above (diagnostic reference only, not a TUS limit)",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pnp-mpa", type=float, required=True, help="in situ peak negative pressure, MPa")
    ap.add_argument("--freq-mhz", type=float, required=True)
    ap.add_argument("--pulse-ms", type=float, required=True, help="pulse (burst) duration")
    ap.add_argument("--prf-hz", type=float, required=True)
    ap.add_argument("--train-s", type=float, help="pulse train duration")
    ap.add_argument("--train-interval-s", type=float, help="time from one train start to the next")
    ap.add_argument("--p-peak-mpa", type=float, help="peak pressure for intensity if different from PNP")
    ap.add_argument("--temps", help="CSV of temperature (C) over time, one column, for thermal dose")
    ap.add_argument("--temps-dt-s", type=float, default=0.1)
    ap.add_argument("--tissue", default="brain", choices=list(ITRUSST_CEM43))
    a = ap.parse_args()
    rep = indices(a.pnp_mpa, a.freq_mhz, a.pulse_ms, a.prf_hz, a.train_s, a.train_interval_s, a.p_peak_mpa)
    if a.temps:
        t = np.loadtxt(a.temps, delimiter=",", ndmin=1)
        dose = cem43(t, a.temps_dt_s)
        rep.update({"peak_temp_rise_C": round(float(t.max() - t[0]), 3), f"CEM43_{a.tissue}": round(dose, 4),
                    "thermal_within_ITRUSST": bool((t.max() - t[0]) <= ITRUSST_DT_C or dose <= ITRUSST_CEM43[a.tissue])})
    print(json.dumps(rep, indent=1))
    ok = rep["MI_within_ITRUSST"] and rep.get("thermal_within_ITRUSST", True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
