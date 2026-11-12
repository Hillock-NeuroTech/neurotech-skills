---
name: neuro-nibs-field-modeling
description: Plan and report non-invasive brain stimulation dose with electric-field modeling (TMS, tDCS, tACS, TI/temporal interference) using SimNIBS, ROAST or similar, plus dose reporting. Use whenever the user sets up a head model from MRI, places a TMS coil or tES electrodes, targets a brain region, compares montages, individualises intensity, or writes the stimulation methods section. Research support only.
---

# NIBS field modeling and dose reporting

The dose that matters is the electric field in the target, which depends
on anatomy, montage or coil placement, and intensity. Model it per person
when you can, and report the full dose so others can reproduce it.

## 1. Build the head model

- SimNIBS: `charm subID T1.nii.gz T2.nii.gz` (T2 improves skull and CSF).
  Inspect the segmentation overlay; fix obvious errors before simulating.
- Without individual MRI, use the template head (`ernie` or MNI) and say
  so; group-level conclusions only.
- Conductivities: keep defaults unless you have a reason; report them.

## 2. Set up the stimulation

- **TMS**: coil model file matching the hardware, position (EEG 10-20
  label or neuronavigation target), orientation, and dI/dt from the
  stimulator output (SimNIBS needs dI/dt; derive from % machine output
  using the device's calibration).
- **tES**: electrode shape, size, thickness, gel/sponge, positions and
  current per electrode (sum zero). For HD-tES list every electrode.
- Optimisation (SimNIBS `TDCSoptimize`, TMS coil-position search) when
  targeting a region: state the target, the constraint (total current,
  number of electrodes) and the objective.

## 3. Read the field

Report in the target ROI: mean and peak magnitude (use the 99th or
99.9th percentile, not the maximum element, which is a meshing artefact),
the component normal to the cortex (direction matters for excitation),
and focality (volume above half of peak). Plot on the cortical surface.

## 4. Intensity and safety context

TMS: determine motor threshold with an accepted method (IFCN guidance;
Rossini et al. 2015) and follow the TMS safety guidelines (Rossi et al.
2009, updated 2021) for intensity, frequency and train limits. tES: report
current density at electrodes; conventional protocols use up to about
2 mA for up to about 30-40 minutes (Bikson et al. 2016 safety review).

## 5. Dose reporting checklist

Following Peterchev et al. 2012: device and waveform; coil or electrode
type, size and position (with method); intensity (and how individualised);
pulse or current timing (frequency, duration, ramps, inter-train
intervals); session count and spacing; modeled field in the target with
software, version and head-model source.
