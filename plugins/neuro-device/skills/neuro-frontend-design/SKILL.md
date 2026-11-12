---
name: neuro-frontend-design
description: Design or review analog front ends for neural recording (EEG, ECoG, EMG, LFP and spike headstages; ADS1299, Intan RHD/RHS, custom ASICs) - input-referred noise budgets, electrode impedance and DC offset, CMRR, input impedance, filtering, gain and ADC resolution. Use whenever the user chooses a biopotential amplifier or ADC, computes noise, sizes gain and bandwidth, or debugs a noisy front end at the circuit level.
---

# Neural recording front-end design

Start from the signal (amplitude and band) and the electrode (impedance
and offset), budget noise at the input, then choose gain, filters and ADC
so the amplifier, not the ADC or the electrode, sets the floor.

## 1. Requirements

| Signal | Typical amplitude | Band |
|---|---|---|
| EEG | about 10-100 uV | about 0.1-100 Hz |
| ECoG / LFP | about 50 uV-1 mV | about 0.1-300 Hz |
| Spikes | about 50-500 uV | about 300 Hz-6 kHz |
| EMG (surface) | about 0.1-5 mV | about 20-500 Hz |

Set an input-referred noise target well below the smallest signal (often
a few uV rms or less across the band) and a DC input range that covers
electrode offsets (hundreds of mV are possible with wet electrodes).

## 2. Noise budget with the bundled script

```bash
python scripts/noise_budget.py --en-nv 30 --fc-hz 10 --in-fa 10 --z-mag-kohm 10 --z-real-kohm 5 \
       --band 0.5 100 --gain 24 --adc-bits 24 --vref 4.5
```

Inputs: amplifier voltage noise density (nV/sqrtHz) and its 1/f corner,
current noise (fA/sqrtHz), electrode impedance magnitude and real part in
the band, bandwidth, gain, ADC bits and reference. It integrates each
source over the band and prints input-referred uV rms per source, the
total, approximate peak-to-peak (x 6.6), and which source dominates.

## 3. Design rules

- Input impedance far above electrode impedance (100x or more) to limit
  attenuation and common-mode-to-differential conversion from impedance
  mismatch.
- CMRR depends on electrode impedance mismatch as much as on the chip; use
  a driven right-leg or bias electrode.
- AC-coupled or wide-input-range DC-coupled inputs to survive offsets;
  check settling time after saturation.
- Anti-alias filtering matched to the ADC (delta-sigma converters relax
  the analog filter but check their digital filter latency for real-time
  use).
- Choose gain so the largest expected input plus offset uses most of the
  ADC range without clipping; then check ADC noise referred to input is
  below the amplifier's.
- Reference chips: ADS1299 (EEG class, 24-bit) and Intan RHD2000 (spike
  class, about 2.4 uV rms input-referred) are common baselines; quote
  datasheet values for your configuration.

## Output

Requirement table, noise budget per source with total, gain and ADC
choice, input range and impedance check, and the dominant noise source
with how to reduce it.
