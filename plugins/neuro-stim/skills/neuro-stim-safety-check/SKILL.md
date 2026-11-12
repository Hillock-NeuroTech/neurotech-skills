---
name: neuro-stim-safety-check
description: Research-engineering check of electrical stimulation parameters (DBS, cortical and intracortical microstimulation, spinal cord, peripheral nerve, cochlear/retinal, FES, tDCS) - charge per phase, charge density, Shannon k, electrode material limits, charge balance and net DC. Use whenever the user plans or reviews stimulation amplitudes, pulse widths, electrode sizes or waveforms, or asks whether a setting is within safe limits. Research support only; not clinical or regulatory sign-off.
---

# Stimulation safety check

Scope: research engineering support. Final settings for humans or animals
follow the approved protocol, device labeling and the responsible
clinician or ethics/IACUC committee.

Two different limits apply and both must hold:
1. **Tissue damage**, usually screened with the Shannon criterion for
   macroelectrodes.
2. **Electrode electrochemistry**: the charge the electrode material can
   inject reversibly without gas evolution or dissolution.

## 1. Compute with the bundled calculator

```bash
python scripts/stim_calc.py --current-ua 60 --pw-us 200 --freq-hz 100 \
       --area-um2 2000 --material platinum [--shannon-k-limit 1.85]
```

Geometry options: `--area-cm2`, `--area-mm2`, `--area-um2`, `--disk-diam-mm`,
or `--cylinder-diam-mm D --cylinder-len-mm L` (lateral area, as for DBS
ring contacts). Voltage-mode stimulators: `--voltage-v V --impedance-ohm Z`
(current estimated as V/Z; impedance changes with amplitude and over
time, so treat as approximate). Asymmetric waveforms:
`--anodic-ua` and `--anodic-pw-us` for the second phase.

It prints charge per phase, charge density, Shannon k, net charge per
pulse and DC current, microelectrode warning, and the comparison with the
material's approximate reversible charge-injection range.

## 2. Interpret

- **Shannon k** (log D = k - log Q; D in uC/cm^2/phase, Q in uC/phase,
  Shannon 1992): k = 1.85 is the boundary in the original data; many
  groups use k = 1.5 as a conservative limit. It was derived from
  macroelectrode data; microelectrodes do not follow it (Cogan et al.
  2016), so for small sites rely on electrode and microstimulation-specific
  data instead.
- **Material limit**: approximate reversible ranges (Cogan 2008):
  platinum and platinum-iridium about 50-150 uC/cm^2, activated iridium
  oxide about 1-5 mC/cm^2, titanium nitride about 0.9 mC/cm^2 (all
  geometric area, waveform dependent). Above the range, measure voltage
  transients (see `neuro-electrode-electrochemistry`) before use.
- **Charge balance**: net charge per pulse must be near zero; any residual
  is DC current into tissue. Check passive recharge and blocking capacitors.
- **Device labeling**: clinical devices carry their own limits (for
  example 30 uC/cm^2 per phase in some DBS labeling). Check the actual
  labeling of the device in use.

## 3. Report

Inputs with units, computed Q, D, k, net DC, material comparison, which
criteria apply and which do not, the verdict per criterion, and what to
measure next. Start the report with the research-only scope line.
