---
name: neuro-stim-artifact-recovery
description: Remove electrical-stimulation artifacts from concurrent recordings (TMS-EEG, tACS/tDCS-EEG, DBS with LFP or EEG, intracortical microstimulation with spikes or ECoG, FES with EMG) and quantify what neural signal was lost. Use whenever the user records during or right after stimulation, sees pulse artifacts, ringing or saturation, or asks whether a post-stimulation effect is real.
---

# Stimulation artifact removal and recovery check

Artifact removal always removes some brain signal too, and residual
artifact can look like a neural effect. Choose the method for the artifact
type, then prove what the pipeline does with a known injected signal.

## 1. Characterise the artifact

From raw data at a high sampling rate: pulse shape, duration, whether the
amplifier saturated (flat tops), decay tail length, and whether the
artifact is identical across pulses (enables templates) or varies
(position, current, impedance changes).

## 2. Choose a method

| Artifact | Method |
|---|---|
| short pulses (TMS, microstimulation, DBS pulses) | blank the saturated span and interpolate, then subtract averaged templates per channel; or SSP/PCA on pulse-locked segments |
| decay tails after TMS | ICA or exponential fitting after blanking (TESA, ARTIST pipelines) |
| continuous sinusoidal (tACS) | template subtraction with sliding averages or SSP; removal is fundamentally limited because residuals scale with the artifact and are modulated by physiology (Noury et al. 2016) |
| DBS at fixed frequency | notch at stimulation frequency and harmonics plus aliasing products; analyse bands away from them |
| recording channels saturated | data are lost for that span; do not interpret it |

Keep the same pipeline for sham and real stimulation conditions.

## 3. Ground-truth injection test

Add a known synthetic signal (for example a 10 Hz burst or an ERP-shaped
waveform at realistic amplitude) to the raw data at times overlapping the
artifacts, run the full removal pipeline, and compare output with the
injected signal: amplitude recovered, phase or latency error, and
correlation. Report the time span after each pulse where recovery is
poor; effects inside that span are not interpretable.

Also check residual artifact power at the stimulation frequency and its
harmonics in sham vs real.

## 4. Report

Artifact properties, method and parameters, blanked durations,
injection-test recovery numbers, residual artifact spectrum, and the
analysis window you consider clean.
