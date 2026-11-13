---
name: neuro-electrode-electrochemistry
description: Characterise neural electrodes electrochemically - impedance spectroscopy (EIS) and equivalent-circuit fits, cyclic voltammetry and charge storage capacity (CSC), voltage transients and charge-injection limits, for Pt, PtIr, IrOx, TiN, PEDOT and other coatings, in vitro and in vivo. Use whenever the user measures or interprets electrode impedance, compares coatings, computes CSC or CIL, or asks how much charge an electrode can safely deliver.
---

# Electrode electrochemistry

Recording quality depends on impedance; stimulation capacity depends on
how much charge the interface injects reversibly. Measure both with
standard methods and report conditions, because values change with
electrolyte, sweep rate, pulse width and bias.

## 0. Load the tool reference

Read `references/instruments-and-fitting.md`: Gamry, BioLogic, Autolab
and PalmSens exports, how to fit spectra (`scripts/fit_eis.py` recovered
known values where impedance.py's default fit did not), CSC and voltage
transient analysis.

## 1. Impedance spectroscopy

- Three-electrode cell (working, large counter, Ag/AgCl reference) in
  phosphate-buffered saline at room or body temperature; state which.
- Sweep about 1 Hz to 100 kHz with a small sinusoid (about 10 mV rms).
- Report |Z| and phase at 1 kHz (the field's common comparison point) plus
  the full spectrum.
- Fit an equivalent circuit to separate solution resistance, charge-
  transfer resistance and double-layer behaviour:

```bash
python scripts/fit_eis.py --data eis.csv [--model randles-cpe]
```

`eis.csv` columns: `freq_hz,z_mag_ohm,phase_deg`. The script fits
Rs + (Rct || CPE) and reports Rs, Rct, CPE Q and alpha, the 1 kHz
impedance, and fit residuals.

## 2. Cyclic voltammetry and CSC

Sweep within the water window of the material (for platinum commonly
about -0.6 to +0.8 V vs Ag/AgCl) at a stated sweep rate. Cathodic CSC is
the time integral of cathodic current over the cycle divided by
geometric area. CSC at slow sweep greatly overestimates what a short
pulse can deliver; do not use it as the charge-injection limit.

## 3. Voltage transients and charge-injection limit

Apply the actual stimulation pulse (current, pulse width, interphase,
bias) and record electrode voltage. Subtract the access-voltage step (Va,
the instantaneous ohmic drop) to get the maximum cathodic polarisation
(Emc). The charge-injection limit is the charge density at which Emc
reaches the water-reduction limit for the material. Repeat in vivo when
possible; in vivo limits are usually lower than in saline (Cogan 2008).

## 4. Typical ranges (orientation only)

Approximate reversible charge-injection ranges (geometric area,
Cogan 2008): platinum about 50-150 uC/cm^2, activated iridium oxide about
1-5 mC/cm^2, titanium nitride about 0.9 mC/cm^2; conductive polymers
report higher values that depend strongly on deposition and stability.
Use them to sanity-check, not to replace measurement.

## Output

Setup and conditions, EIS at 1 kHz and fit parameters, CSC with sweep
rate, voltage-transient Emc and resulting charge-injection limit, and the
comparison with the intended stimulation (see `neuro-stim-safety-check`).
