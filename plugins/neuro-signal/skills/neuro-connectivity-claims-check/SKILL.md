---
name: neuro-connectivity-claims-check
description: Choose and check functional connectivity analyses for EEG, MEG, ECoG and LFP (coherence, PLV, PLI/wPLI, imaginary coherency, amplitude-envelope correlation, Granger, PDC/DTF, graph metrics). Use whenever the user computes or reports connectivity, networks, synchrony or directed influence between channels or sources, or compares connectivity between groups or conditions.
---

# Connectivity: choose robust measures and rule out artifacts

Two sensors see the same sources (volume conduction and field spread),
share a reference, and differ in signal-to-noise. Each can create
"connectivity" with no interaction at all. Choose measures and controls
that remove these before interpreting.

## 1. Pick a measure that tolerates zero-lag mixing

| Question | Use | Avoid on raw sensor data |
|---|---|---|
| phase coupling | imaginary coherency (Nolte et al. 2004), wPLI (Vinck et al. 2011), PLI (Stam et al. 2007) | coherence, PLV (inflated by zero-lag mixing) |
| amplitude coupling | orthogonalised amplitude-envelope correlation (Hipp et al. 2012; Brookes et al. 2012) | plain envelope correlation |
| directed influence | Granger/PDC/DTF on source data, with stationarity checks (Barnett & Seth 2011) | Granger after aggressive filtering |

Source-space analysis reduces but does not remove leakage; apply
leakage correction there too.

## 2. Controls that every comparison needs

- **Reference**: common reference creates shared signal; use a
  reference-free approach (bipolar for ECoG/sEEG, source space, or
  surface Laplacian for EEG) or show results hold across references.
- **Trial count**: PLV, coherence and wPLI are biased by number of trials;
  equalise counts across conditions or use unbiased estimators (for
  example debiased wPLI).
- **Signal-to-noise and power**: a condition with more power shows more
  phase consistency. Report power alongside connectivity and test whether
  the effect survives when power is matched.
- **Surrogates**: compare with time-shifted or phase-randomised surrogates
  to get a null per edge.
- **Multiple comparisons**: all channel pairs x frequencies; use network-
  based statistics or permutation with max statistic.

## 3. Interpretation limits

Connectivity is statistical dependence, not anatomical connection; a
common driver produces coupling between areas that do not talk. Graph
metrics depend strongly on thresholding and network density; compare
networks at matched density.

## Output

Measure and why, reference and leakage handling, trial and power
matching, null model, correction method, and the claim scoped to what the
measure supports.
