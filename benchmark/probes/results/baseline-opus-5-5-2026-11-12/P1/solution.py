"""Shannon-criterion check for a single intracortical microstimulation site."""
import json
import math

I_A = 60e-6            # 60 uA
PW_S = 200e-6          # 200 us per phase
AREA_UM2 = 2000.0      # geometric area, smooth Pt
K_SOP = 1.85

# Smooth Pt reversible charge-injection limit (literature range ~50-150 uC/cm^2,
# up to ~300-350 uC/cm^2 with H-atom plating for cathodic-first pulses;
# Rose & Robblee 1990, Merrill et al. 2005).
PT_CIC_UPPER_uC_cm2 = 350.0
# Shannon (1992) was fit to large surface/macro electrodes (McCreery 1990 data,
# areas ~0.01-0.5 cm^2); it does not apply to microelectrodes.
SHANNON_MIN_AREA_CM2 = 0.01

Q_C = I_A * PW_S
area_cm2 = AREA_UM2 * 1e-8
D_uC_cm2 = Q_C / area_cm2 * 1e6
Q_uC = Q_C * 1e6
k = math.log10(D_uC_cm2) + math.log10(Q_uC)

applicable = area_cm2 >= SHANNON_MIN_AREA_CM2
exceeds_pt = D_uC_cm2 > PT_CIC_UPPER_uC_cm2
acceptable = (not exceeds_pt) and (applicable and k <= K_SOP)

print(f"Q = {Q_C*1e9:.3f} nC/phase, D = {D_uC_cm2:.1f} uC/cm^2, k = {k:.3f}")
print(f"area = {area_cm2:.1e} cm^2, Shannon applicable: {applicable}")
print(f"exceeds smooth-Pt CIC (~{PT_CIC_UPPER_uC_cm2} uC/cm^2 max): {exceeds_pt}")

answer = {
    "charge_per_phase_nC": round(Q_C * 1e9, 4),
    "charge_density_uC_per_cm2": round(D_uC_cm2, 2),
    "shannon_k": round(k, 3),
    "shannon_criterion_applicable": applicable,
    "acceptable_as_specified": acceptable,
    "explanation": (
        f"The setting gives {Q_C*1e9:.0f} nC/phase and {D_uC_cm2:.0f} uC/cm^2 (geometric), so k = {k:.2f}, "
        "which nominally passes k = 1.85, but the Shannon criterion was derived from large surface macroelectrodes "
        "(~0.01-0.5 cm^2) and is not valid for a 2000 um^2 intracortical microelectrode, where damage depends on "
        "charge per phase and density separately (McCreery 1990/2010) and on electrode electrochemistry. "
        f"More decisively, {D_uC_cm2:.0f} uC/cm^2 exceeds the reversible charge-injection capacity of smooth "
        "platinum (~50-150 uC/cm^2, at most ~300-350 uC/cm^2), so the site would drive irreversible Faradaic "
        "reactions (water electrolysis, Pt dissolution); reduce current/pulse width or use a high-CIC coating "
        "(e.g. SIROF/PEDOT) and verify with voltage-transient measurements."
    ),
}
with open("answer.json", "w") as f:
    json.dump(answer, f, indent=2)
