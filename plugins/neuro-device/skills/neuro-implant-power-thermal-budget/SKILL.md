---
name: neuro-implant-power-thermal-budget
description: Budget power, data rate and tissue heating for implanted or head-mounted neural interfaces - channel count vs sampling rate and bits, on-chip spike detection or compression, radio energy per bit, wireless power, and temperature-rise limits. Use whenever the user sizes a high-channel-count implant or wireless headstage, trades channels against battery or link budget, or asks whether a device will heat tissue too much.
---

# Implant power and thermal budget

Channel count drives data rate, data rate drives radio power, and power
becomes heat in tissue. Budget all three together early, because the
thermal limit usually decides what is feasible.

## 1. Data rate

raw rate = channels x sampling rate x bits per sample. Options that cut
it: on-chip spike detection (send events or threshold crossings), spike-
band power, decimated LFP, lossless compression. State what the
downstream decoder needs: many BCIs decode well from threshold crossings
or spike-band power alone.

## 2. Power budget

Sum per-channel front-end power x channels, ADC, digital processing,
radio (energy per bit x data rate), power management losses, and
stimulation if present. Use datasheet or measured numbers and a margin.
The bundled script does the arithmetic and the heat-flux check:

```bash
python scripts/power_budget.py --channels 1024 --fs 20000 --bits 10 --afe-uw-per-ch 5 \
       --radio-nj-per-bit 1 --digital-mw 2 --other-mw 1 --reduction 0.05 --area-cm2 4
```

`--reduction` is the fraction of raw data sent after compression or
detection. It prints data rates, power per block, total, and surface heat
flux (mW/cm^2) of the implant.

## 3. Thermal limit

- Active implant standards cap the outer-surface temperature rise
  (ISO 14708-1 is commonly cited at 2 deg C above body temperature);
  many designs target 1 deg C for margin.
- Heat-flux screening values (for example about 40 mW/cm^2 of implant
  surface, Seese et al. 1998) give a first check only. Confirm with a
  bio-heat thermal simulation (Pennes equation, perfusion, implant
  geometry) and bench measurement in a tissue phantom.
- Wireless power and data links also deposit RF energy; check specific
  absorption rate against the applicable limits (for example FCC 1.6 W/kg
  averaged over 1 g for partial-body exposure) with an EM simulation.

## Output

Data-rate table (raw and reduced), power table by block with total and
margin, heat flux, thermal simulation or measurement plan, and the
channel/feature trade-off you recommend.
