"""Data-rate, power and heat-flux budget for an implanted neural interface.

python power_budget.py --channels 1024 --fs 20000 --bits 10 --afe-uw-per-ch 5 \
       --radio-nj-per-bit 1 [--reduction 0.05] [--digital-mw 2] [--adc-uw-per-ch 0] \
       [--other-mw 0] [--pm-efficiency 0.85] [--area-cm2 4] [--flux-screen-mw-cm2 40]

Prints JSON. The heat-flux comparison is a screening check only.
"""
import argparse
import json

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--channels", type=int, required=True)
    ap.add_argument("--fs", type=float, required=True)
    ap.add_argument("--bits", type=int, required=True)
    ap.add_argument("--afe-uw-per-ch", type=float, required=True)
    ap.add_argument("--adc-uw-per-ch", type=float, default=0.0)
    ap.add_argument("--radio-nj-per-bit", type=float, required=True)
    ap.add_argument("--reduction", type=float, default=1.0, help="fraction of raw data transmitted")
    ap.add_argument("--digital-mw", type=float, default=0.0)
    ap.add_argument("--other-mw", type=float, default=0.0)
    ap.add_argument("--pm-efficiency", type=float, default=0.85)
    ap.add_argument("--area-cm2", type=float)
    ap.add_argument("--flux-screen-mw-cm2", type=float, default=40.0)
    a = ap.parse_args()
    raw_bps = a.channels * a.fs * a.bits
    tx_bps = raw_bps * a.reduction
    blocks = {
        "front_end_mW": a.channels * a.afe_uw_per_ch / 1000,
        "adc_mW": a.channels * a.adc_uw_per_ch / 1000,
        "digital_mW": a.digital_mw,
        "radio_mW": tx_bps * a.radio_nj_per_bit * 1e-9 * 1000,
        "other_mW": a.other_mw,
    }
    load = sum(blocks.values())
    total = load / a.pm_efficiency
    out = {
        "raw_data_rate_Mbps": round(raw_bps / 1e6, 3),
        "transmitted_data_rate_Mbps": round(tx_bps / 1e6, 3),
        "power_by_block_mW": {k: round(v, 3) for k, v in blocks.items()},
        "load_power_mW": round(load, 3),
        "total_with_power_management_mW": round(total, 3),
        "largest_block": max(blocks, key=blocks.get),
    }
    if a.area_cm2:
        flux = total / a.area_cm2
        out["surface_heat_flux_mW_per_cm2"] = round(flux, 2)
        out["screening_flux_mW_per_cm2"] = a.flux_screen_mw_cm2
        out["below_screening_flux"] = flux < a.flux_screen_mw_cm2
        out["note"] = "Screening only: confirm temperature rise with thermal simulation and phantom measurement."
    print(json.dumps(out, indent=2))
