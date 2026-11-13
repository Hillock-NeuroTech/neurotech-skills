# Potentiostats, data export and fitting

Fitting results below come from running both fitters on the same
synthetic spectrum (Rs 1 kΩ, Rct 2 MΩ, CPE Q 2 nF·s^(α-1), α 0.85, 1%
noise, 1 Hz-100 kHz) with impedance.py 1.7.1 (November 2026).

## Instruments and their software

| Instrument | Software | Export for analysis |
|---|---|---|
| Gamry (Reference, Interface) | Framework (acquisition), Echem Analyst (analysis) | `.DTA` text files; `impedance.preprocessing.readGamry` reads EIS |
| BioLogic (SP-, VSP-, VMP-series) | EC-Lab | `.mpr` binary or `.mpt` text; `readBioLogic` in impedance.py; `galvani` package for `.mpr` |
| Metrohm Autolab | NOVA | ASCII export; `readAutolab` |
| PalmSens (PalmSens4, EmStat) | PSTrace | `.csv` / `.pssession` |
| Zahner, Ivium | Thales, IviumSoft | ASCII export |
| Intan RHD/RHS | built-in impedance test at 1 kHz (and other frequencies) | quick screening only, not full EIS |

Export frequency, real and imaginary impedance (or magnitude and phase)
and the measurement settings (amplitude, DC bias, cell setup).

## Fitting equivalent circuits

**Preferred: `scripts/fit_eis.py`** (Rs + Rct ∥ CPE). On the synthetic
spectrum it returned Rs 995 Ω, Rct 1.997 MΩ, Q 2.006 nF, α 0.850, with
0.8% residual: the true values.

**impedance.py** (`pip install impedance`) fits arbitrary circuits:

```python
import numpy as np
from impedance.models.circuits import CustomCircuit
c = CustomCircuit("R0-p(R1,CPE1)", initial_guess=[1e3, 1e6, 1e-9, 0.85])
c.fit(f, Z, weight_by_modulus=True, bounds=([0, 0, 0, 0.5], [np.inf, np.inf, np.inf, 1.0]))
```

On the same spectrum, impedance.py with its default unweighted fit
converged to Rs 153 kΩ and α 0.71 (true: 1 kΩ, 0.85). With
`weight_by_modulus=True` it got closer but the answer depended on the
starting guess (α 0.78 or 0.91 from two guesses). Electrode spectra span
several decades of |Z|, which defeats local optimisers. When using it:
weight by modulus, set bounds, start from several guesses, and check the
fitted curve reproduces both |Z| and phase across the band.

Common circuits: Randles with CPE (`R0-p(R1,CPE1)`), with Warburg
diffusion (`R0-p(R1-W1,CPE1)`), and coating plus interface
(`R0-p(R1,CPE1)-p(R2,CPE2)`) for encapsulated or porous electrodes. Use
the simplest circuit the residuals allow; extra elements fit noise.

## Cyclic voltammetry and charge storage capacity

- Export current and potential per cycle; use a cycle after the
  response has stabilised (often the third or later), and state which.
- Cathodic CSC = integral of cathodic current over time (or of current
  over potential divided by sweep rate) for the cycle, divided by
  geometric area. Report sweep rate and potential window vs reference.
- The water window depends on the material and electrolyte; do not reuse
  platinum limits for other materials.

## Voltage transients

Record the electrode voltage during the actual pulse. Take Emc at the
end of the cathodic phase after removing the access voltage (the
instantaneous jump at pulse onset, read about 10 µs after the edge). Use
a fast enough sampling rate and an isolated, high-bandwidth measurement:
a slow scope or a filtered amplifier hides the access voltage.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Two-electrode measurement reported as electrode impedance | counter-electrode impedance included | three-electrode cell, large counter |
| Excitation too large | non-linear response, wrong fit | about 10 mV rms; check linearity |
| Comparing impedance at different frequencies or areas | meaningless comparisons | report at 1 kHz and normalise by geometric area where relevant |
| Unweighted local fit across decades | wrong parameters with a good-looking plot | weighted, bounded, multi-start fit; check residuals |
| CSC from a fast or slow sweep quoted as injection limit | over- or under-estimate | use voltage transients for the limit |
