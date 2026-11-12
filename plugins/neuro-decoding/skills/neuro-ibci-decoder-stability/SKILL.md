---
name: neuro-ibci-decoder-stability
description: Evaluate intracortical BCI decoders across days and sessions (Utah arrays, Neuropixels, ECoG grids, spike or threshold-crossing features). Use when the user asks how a decoder holds up over time, about recalibration, nonstationarity, signal drift, few-shot adaptation, unit turnover, or FALCON-style benchmarking, or compares stabilization methods such as alignment, NDT/latent-space adaptation or daily recalibration.
---

# Intracortical decoder stability across days

Signals from chronic implants drift: units appear and disappear,
thresholds shift, and neural tuning changes. A decoder scored within one
session says nothing about tomorrow. Evaluate in time order and report how
much recalibration data each method needs.

## 1. Organise data by day

Index every trial by session date. Never shuffle across days. Keep the
features fixed in definition (same channels, bin width, threshold rule)
so later days are comparable; log any channel that is dead or re-referenced.

## 2. Use three evaluation regimes

| Regime | Train | Test | Answers |
|---|---|---|---|
| Within-day | early part of day d | later part of day d | ceiling |
| Zero-shot | days 1..d | day d+k, no new data | how fast does it decay |
| Few-shot | days 1..d + first m trials of day d+k | rest of day d+k | recalibration cost |

This matches the FALCON benchmark design (calibration, few-shot and held-out
evaluation days; Karpowicz et al. 2024). Report performance against days
since training, and against m (minutes or trials of recalibration).

## 3. Metrics

- Continuous decoding (cursor, kinematics): R^2 or correlation per
  dimension on held-out time, not on shuffled bins.
- Discrete (keys, phonemes, words): accuracy plus error rate per unit time.
- Closed-loop matters more than offline: if online data exist, report
  bit rate or task success, because offline R^2 can rank methods wrongly.

## 4. Baselines every comparison needs

1. Fixed decoder trained on day 1 only (lower bound).
2. Daily full recalibration (upper bound for cost).
3. Simple mean/variance re-normalisation per day (cheap, often strong).
4. Your method. Show it beats 3, not only 1.

## 5. Diagnose why performance drops

Plot per-channel firing-rate change, and decoder weights on channels that
changed. Separate recording change (lost units, impedance) from neural
change (tuning shift). Recording change argues for channel-robust features;
neural change argues for adaptive decoders.

## Report

Days spanned, sessions, channels kept, regimes above with performance vs
days and vs recalibration data, the three baselines, and online results if
any. Note the participant count: results from one participant are a case
study.
