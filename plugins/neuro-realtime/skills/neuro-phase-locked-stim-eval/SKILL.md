---
name: neuro-phase-locked-stim-eval
description: Design and evaluate brain-state- or phase-dependent closed-loop stimulation (phase-locked TMS, tACS, auditory stimulation during sleep slow waves, DBS triggered on beta bursts, real-time Hilbert, AR forward prediction, ecHT). Use whenever the user estimates oscillation phase in real time, triggers stimulation at a target phase or on bursts, or needs to know how accurate the timing really was.
---

# Phase-locked stimulation: estimate, trigger, verify

Real-time phase estimates are noisy because the filter and Hilbert
transform need future samples. Every system must be evaluated against the
phase computed offline with full data, at the moments it actually fired.

## 1. Choose an estimator

| Method | Idea | Notes |
|---|---|---|
| AR forward prediction | band-pass a past window, fit an autoregressive model, predict ahead, take phase at "now" | used for phase-triggered TMS (Zrenner et al. 2018) |
| Educated temporal prediction | learn the typical cycle length per person, extrapolate from the last peak | simple, fast (Shirinpour et al. 2020) |
| Endpoint-corrected Hilbert (ecHT) | causal Hilbert with end-point correction | low latency (Schreglmann et al. 2021) |
| Threshold / peak detection | trigger on slow-wave down-states or burst amplitude | sleep and beta-burst paradigms |

Fix the target band per participant from a resting baseline (individual
peak frequency) and include a minimum amplitude gate: phase is undefined
when the oscillation is weak.

## 2. Evaluate against offline ground truth

1. Record the raw signal and every trigger time.
2. Offline, compute the "true" phase with a zero-phase band-pass and
   Hilbert on the full recording.
3. Stimulation artifacts corrupt the data right after a pulse, so take
   ground truth from sham or catch triggers (estimator fires, no pulse), or
   from data before the artifact with care.
4. Report the circular mean phase error, the resultant vector length
   (consistency), the fraction of triggers within +/-30 or +/-45 degrees of
   target, and how accuracy depends on amplitude (SNR).

## 3. Timing chain

Add the hardware delay from decision to pulse (stimulator trigger latency)
and compensate it in the prediction horizon; measure it with a loopback.
A 10 Hz rhythm moves 3.6 degrees per millisecond.

## 4. Report

Target band and phase, estimator and parameters, amplitude gate, number of
real and sham triggers, phase error mean and spread, consistency, accuracy
vs amplitude, and the measured hardware delay.
