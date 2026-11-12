---
name: neuro-nerve-stim-modeling
description: Model peripheral nerve stimulation (vagus, sciatic, cuff and intrafascicular electrodes, spinal roots) with finite-element fields coupled to axon models - fiber recruitment, thresholds, selectivity and waveform choice (ASCENT, NEURON, MRG model, COMSOL, Sim4Life). Use whenever the user designs a nerve cuff or electrode contact layout, predicts which fibers are activated, compares waveforms, or fits recruitment curves.
---

# Nerve stimulation modeling

Which fibers fire depends on geometry (nerve, fascicles, electrode), tissue
conductivities, fiber diameter and type, and the waveform. Model the field
and the axons together, then check the model against measured recruitment.

## 1. Geometry and field

- Nerve cross-section from histology (fascicle outlines, perineurium,
  epineurium) rather than idealised circles when available.
- Electrode: cuff inner diameter, contact size and spacing, insulation,
  fluid gap.
- Solve the extracellular potential with finite elements (COMSOL,
  Sim4Life, or the open ASCENT pipeline; Musselman et al. 2021). Report
  conductivities (anisotropic for endoneurium) and mesh convergence.

## 2. Axon models

- Myelinated fibers: MRG model (McIntyre, Richardson & Grill 2002) across
  the fiber diameter distribution of the target nerve.
- Unmyelinated C fibers: a dedicated model (for example Sundt et al. 2015).
- Place fibers within fascicles from the histology; run in NEURON with the
  extracellular potentials applied.

## 3. Outputs

- Threshold per fiber, then recruitment curves (fraction activated vs
  amplitude) per fiber type and fascicle.
- Selectivity: recruitment of target vs off-target fascicles at the same
  amplitude.
- Strength-duration (rheobase, chronaxie) to choose pulse width.
- Waveform effects: cathodic vs anodic first, asymmetric charge-balanced
  pulses, kilohertz block if relevant.

## 4. Validate

Compare predicted thresholds and recruitment order with measured
compound action potentials or EMG; adjust only physically justified
parameters and report which. Check charge and density of chosen settings
with `neuro-stim-safety-check`.

## Report

Geometry source, FEM settings and conductivities, fiber models and
distributions, recruitment and selectivity results, validation against
data, and safety check of the proposed parameters.
