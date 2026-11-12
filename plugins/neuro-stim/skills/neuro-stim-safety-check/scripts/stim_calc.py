"""Charge, charge density, Shannon k and electrode-limit check for pulsed stimulation.

python stim_calc.py --current-ua 60 --pw-us 200 --freq-hz 100 --area-um2 2000 --material platinum
python stim_calc.py --voltage-v 3.5 --impedance-ohm 1000 --pw-us 90 --cylinder-diam-mm 1.27 --cylinder-len-mm 1.5
python stim_calc.py --current-ua 100 --pw-us 200 --anodic-ua 50 --anodic-pw-us 300 --freq-hz 130 --area-mm2 6

Research engineering support only; not clinical or regulatory sign-off.
Material ranges are approximate geometric-area values (Cogan 2008) and depend
on waveform, bias and electrode condition.
"""
import argparse
import json
import math

# approximate reversible charge-injection ranges, uC/cm^2 (geometric area), Cogan 2008
MATERIALS = {
    "platinum": (50, 150), "platinum-iridium": (50, 150),
    "iridium-oxide-activated": (1000, 5000), "titanium-nitride": (870, 870),
}
MICRO_CM2 = 1e-4      # below about 10,000 um^2: microelectrode, Shannon not validated
CHECK_CM2 = 1e-3      # 1e-4..1e-3 cm^2: small, check applicability


def area_cm2(a):
    if a.area_cm2:
        return a.area_cm2, "given"
    if a.area_mm2:
        return a.area_mm2 / 100, "given (mm^2)"
    if a.area_um2:
        return a.area_um2 * 1e-8, "given (um^2)"
    if a.disk_diam_mm:
        r = a.disk_diam_mm / 20
        return math.pi * r * r, "disk"
    if a.cylinder_diam_mm and a.cylinder_len_mm:
        return math.pi * (a.cylinder_diam_mm / 10) * (a.cylinder_len_mm / 10), "cylinder lateral surface"
    raise SystemExit("give an electrode area or geometry")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_argument_group("waveform")
    g.add_argument("--current-ua", type=float)
    g.add_argument("--voltage-v", type=float)
    g.add_argument("--impedance-ohm", type=float)
    g.add_argument("--pw-us", type=float, required=True, help="first (usually cathodic) phase width")
    g.add_argument("--anodic-ua", type=float, help="second phase amplitude if asymmetric")
    g.add_argument("--anodic-pw-us", type=float)
    g.add_argument("--freq-hz", type=float)
    e = ap.add_argument_group("electrode")
    for k in ("area-cm2", "area-mm2", "area-um2", "disk-diam-mm", "cylinder-diam-mm", "cylinder-len-mm"):
        e.add_argument(f"--{k}", type=float)
    e.add_argument("--material", choices=sorted(MATERIALS))
    ap.add_argument("--shannon-k-limit", type=float, default=1.85)
    ap.add_argument("--density-cap", type=float, help="device labeling cap, uC/cm^2/phase")
    a = ap.parse_args()

    if a.current_ua is not None:
        i_ua, mode = a.current_ua, "current-controlled"
    elif a.voltage_v is not None and a.impedance_ohm:
        i_ua, mode = a.voltage_v / a.impedance_ohm * 1e6, "voltage-controlled (I = V/Z, approximate)"
    else:
        raise SystemExit("give --current-ua, or --voltage-v with --impedance-ohm")
    A, how = area_cm2(a)
    q_uc = i_ua * a.pw_us * 1e-6                     # uA * us = pC; *1e-6 -> uC
    d = q_uc / A
    k = math.log10(d) + math.log10(q_uc)
    out = {
        "scope": "Research engineering support only; not clinical or regulatory sign-off.",
        "mode": mode, "current_ua": round(i_ua, 3), "pulse_width_us": a.pw_us,
        "area_cm2": float(f"{A:.6g}"), "area_um2": float(f"{A * 1e8:.6g}"), "area_method": how,
        "charge_per_phase_uC": float(f"{q_uc:.6g}"), "charge_per_phase_nC": float(f"{q_uc * 1e3:.6g}"),
        "charge_density_uC_per_cm2": float(f"{d:.6g}"),
        "shannon_k": round(k, 3), "shannon_k_limit": a.shannon_k_limit,
        "shannon_below_limit": k < a.shannon_k_limit,
    }
    if A < MICRO_CM2:
        out["shannon_applicability"] = "not validated: microelectrode (Shannon derived from macroelectrodes; Cogan et al. 2016)"
    elif A < CHECK_CM2:
        out["shannon_applicability"] = "uncertain: small electrode, check against size-specific data"
    else:
        out["shannon_applicability"] = "macroelectrode range"
    if a.material:
        lo, hi = MATERIALS[a.material]
        out["material"] = a.material
        out["material_reversible_range_uC_per_cm2"] = [lo, hi]
        out["exceeds_material_range"] = d > hi
        out["fraction_of_material_upper_bound"] = round(d / hi, 2)
    if a.anodic_ua is not None:
        q2 = a.anodic_ua * (a.anodic_pw_us or a.pw_us) * 1e-6
        net = q_uc - q2
        out["second_phase_charge_uC"] = float(f"{q2:.6g}")
        out["net_charge_per_pulse_uC"] = float(f"{net:.6g}")
        if a.freq_hz:
            out["net_dc_current_uA"] = float(f"{net * a.freq_hz:.6g}")
        out["charge_balanced"] = abs(net) <= 0.01 * q_uc
    if a.freq_hz:
        out["frequency_hz"] = a.freq_hz
        out["duty_cycle_percent"] = round(a.pw_us * 1e-6 * a.freq_hz * 100 * (2 if a.anodic_ua is None else 1), 3)
    if a.density_cap:
        out["density_cap_uC_per_cm2"] = a.density_cap
        out["exceeds_density_cap"] = d > a.density_cap
        out["max_pw_us_within_cap"] = round(a.density_cap * A / (i_ua * 1e-6), 1)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
