---
name: neuro-tus-dose-planning
description: Plan and report transcranial focused ultrasound stimulation (TUS/tFUS/LIFU) dose - acoustic and thermal simulation through the skull (k-Wave, k-Plan, BabelBrain, Kranion), pulsing parameters, mechanical index, intensity and temperature rise, and auditory confounds. Use whenever the user designs a TUS protocol, simulates a transducer and target, checks ultrasound safety indices, or writes TUS methods. Research support only.
---

# TUS dose planning

Ultrasound is attenuated, refracted and focused differently by each
skull, so free-water transducer specifications do not describe the dose
in the brain. Simulate per participant, check mechanical and thermal
indices, and report every parameter.

## 0. Load the tool reference

Read `references/simulation-and-safety.md`: k-Wave / k-wave-python,
k-Plan, BabelBrain and Kranion, and the ITRUSST levels. Compute MI,
Isppa, Ispta and thermal dose with `scripts/tus_indices.py`.

## 1. Parameters to define

Transducer (model, elements, focal distance, aperture), fundamental
frequency, pulse duration, pulse repetition frequency (PRF), duty cycle,
pulse train duration, sonication duration and repetition, total session
time, and target with coordinates.

## 2. Simulate through the skull

- Build skull properties from CT (best) or pseudo-CT from MRI
  (UTE/ZTE or T1-based methods), registered to the participant.
- Run acoustic simulation (k-Wave, k-Plan or BabelBrain) for the
  transducer placement, then a thermal simulation for the full pulsing
  sequence.
- Report in brain and skull: peak pressure, spatial-peak pulse-average
  intensity (Isppa), spatial-peak temporal-average intensity (Ispta),
  mechanical index (MI), focal position shift and size vs intended, and
  maximum temperature rise in brain, skull and skin.

## 3. Check against safety guidance

Compare with the ITRUSST consensus (Aubry et al. 2025, Brain Stimulation
18(6):1896-1905): non-significant risk if MI (or MItc) is at most 1.9, and
for heating if any one of these holds: peak rise at most 2 °C (or peak at
most 39 °C from 37 °C); thermal dose at most 2 CEM43 in brain, 16 in bone,
21 in skin; or thermal index within the tabulated values for the exposure
time. These are levels, not limits; your approved protocol governs. The
FDA diagnostic reference (Ispta.3 up to 720 mW/cm^2, MI up to 1.9) is
often quoted alongside but was set for imaging. If simulation
uncertainty is large, plan with margin.

## 4. Control for auditory and somatosensory confounds

Pulsed ultrasound at audible PRFs can produce an audible tone through
bone conduction, which by itself evokes brain responses. Use auditory
masking, ramped pulse envelopes, and an active sham with matched sound,
and ask participants afterwards what they perceived (see
`neuro-sham-and-blinding-design`).

## 5. Report

All parameters from step 1, free-field calibration (hydrophone), skull
model source, simulated in-brain values from step 2 with software and
version, safety comparison, confound controls.
