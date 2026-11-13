# Thermal modelling, wireless links and bench tests

Not executed while writing this file; methods summarised from standard
practice. Check limits against the current edition of the standards your
regulator recognises.

## Bio-heat model

Pennes bioheat equation for tissue around the implant:

ρc ∂T/∂t = ∇·(k∇T) + ρ_b c_b ω_b (T_a − T) + Q_m + Q_device

where ρ, c, k are tissue density, heat capacity and conductivity;
ρ_b c_b ω_b the blood perfusion term pulling tissue back to arterial
temperature T_a; Q_m metabolic heat; Q_device the implant's dissipated
power (as a surface or volume source) plus RF absorption.

| Tool | Notes |
|---|---|
| COMSOL Multiphysics (Heat Transfer, Bioheat) | standard for implant thermal FEM; couples to EM for SAR |
| Sim4Life | anatomical models with perfusion, EM and thermal together |
| Ansys (Icepak, HFSS + thermal) | electronics thermal and RF |
| Python (FEniCSx, or a finite-difference script) | transparent first estimates for simple geometry |

Model the actual implant geometry and placement (under skull, in
cortex, subcutaneous), use tissue properties from a cited database (for
example the IT'IS tissue properties database), include perfusion, and run
the worst-case duty cycle long enough to reach steady state. Report the
peak temperature rise at the tissue surface touching the device.

## Wireless power and data

- **Inductive links** (typically low MHz to tens of MHz): efficiency
  falls quickly with distance and misalignment; the losses heat both coils
  and tissue. Model coupling (k) across expected misalignments.
- **Radio (e.g. BLE at 2.4 GHz, MICS 402-405 MHz, UWB)**: energy per bit
  sets power; tissue absorption rises with frequency. Check specific
  absorption rate with an EM simulation against the applicable limits.
- **Ultrasonic and optical links** exist in research devices; each has
  its own tissue heating and safety framework.

## Bench verification

1. Tissue-mimicking phantom (agar or gel with matched thermal properties)
   at 37 °C, or saline with controlled convection.
2. Thermocouples or fibre-optic probes (fibre-optic for RF environments,
   since metal probes heat and perturb fields) at the device surface.
3. Run the worst-case operating mode until steady state; compare with
   the model, then correct the model before using it for other designs.
4. In vivo measurement in the animal model when the device is close to
   the limit.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| No perfusion in the model | temperature overestimated (conservative) but misleading for design trade-offs | include perfusion; also report the no-perfusion bound |
| Average power used instead of the worst-case mode | peak heating underestimated | simulate the highest-power state for its real duration |
| Heat-flux rule of thumb used as final evidence | not accepted as verification | model plus bench measurement |
| Metal thermocouples in an RF field | false readings and local heating | fibre-optic probes |
| Ignoring the external transmitter coil heating the skin | skin burns | include the external parts in the thermal analysis |
