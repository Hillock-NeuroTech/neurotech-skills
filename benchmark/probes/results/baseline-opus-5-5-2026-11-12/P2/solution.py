"""DBS charge-per-phase and charge-density check.

Assumptions:
- Voltage-controlled stimulator: current I = V / Z, using the measured
  impedance (1000 ohm) for both settings (assumes Z is unchanged at the
  new setting; real electrode impedance is not purely resistive).
- Rectangular cathodic phase: Q = I * pulse width.
- Active area = lateral surface of the cylindrical contact, pi * d * L
  (standard convention for DBS ring contacts, e.g. ~0.06 cm^2 for a
  1.27 mm x 1.5 mm contact; end caps are not exposed on ring contacts).
- Frequency (130 Hz) does not affect charge per phase.
"""
import json
import math

d_cm = 0.127   # 1.27 mm
L_cm = 0.15    # 1.5 mm
area_cm2 = math.pi * d_cm * L_cm
Z = 1000.0
CAP = 30.0     # uC/cm^2 per phase

def charge(V, pw_us):
    I_A = V / Z
    q_uC = I_A * pw_us          # A * us = uC
    return q_uC, q_uC / area_cm2

cq, cd = charge(3.5, 90.0)
pq, pd = charge(6.0, 450.0)

ans = {
    "current_q_uC": round(cq, 6),
    "current_density_uC_per_cm2": round(cd, 4),
    "proposed_q_uC": round(pq, 6),
    "proposed_density_uC_per_cm2": round(pd, 4),
    "proposed_exceeds_cap": bool(pd > CAP),
}
print(f"area = {area_cm2:.5f} cm^2")
# Max pulse width at 6.0 V within cap, for context
print(f"max PW at 6 V within cap: {CAP*area_cm2/(6.0/Z):.1f} us")
print(json.dumps(ans, indent=2))
with open("answer.json", "w") as f:
    json.dump(ans, f, indent=2)
