---
name: neuro-sleep-staging-eval
description: Build and evaluate automatic sleep staging from EEG/EOG/EMG (polysomnography, wearables, Sleep-EDF, SHHS, MASS, DREEM). Use whenever the user scores sleep stages, trains a hypnogram model, reports staging accuracy or kappa, compares to human scorers, or computes sleep metrics such as total sleep time, efficiency or N3/REM percentage.
---

# Sleep staging evaluation

Staging is scored in 30 s epochs under AASM rules (W, N1, N2, N3, REM).
Epochs from one night are strongly dependent and stage proportions are
very unequal, so evaluation choices change the headline number a lot.

## 1. Prepare labels and data

- Map legacy R&K labels to AASM (S3 and S4 to N3; movement and unscored
  epochs excluded, and say how many).
- Trim long wake before lights-off and after lights-on (or use the lights
  markers). Untrimmed wake inflates accuracy because wake is easy.
- Keep channel choice consistent with the claim (single-channel EEG,
  EEG+EOG, full PSG, wearable).

## 2. Split by subject

Subject-wise (or night-wise with all nights of a person on one side). For
public datasets use the published folds when comparing to papers.

## 3. Report the right metrics

- Overall accuracy and **Cohen's kappa** (the field's standard), plus
  macro-F1.
- **Per-stage F1 and the confusion matrix**: N1 is always worst; say so.
- Per-subject distribution, not only pooled: show median and range.
- Human context: inter-scorer agreement on PSG is typically around kappa
  0.75 to 0.8, and lower for N1; a model at that level is near the ceiling
  the labels allow.

## 4. Check clinically used summary metrics

Compare predicted vs scored per night: total sleep time, sleep efficiency,
sleep onset latency, WASO, % N3, % REM, REM latency. Report bias and
limits of agreement (Bland-Altman). A model can have good kappa and still
bias REM latency.

## 5. Generalisation

Test on another dataset or device before claiming robustness; cohort age
and disorders change stage distributions (older adults have less N3).

## Report

Dataset and cohort, channels, label mapping, trimming rule, split, kappa,
accuracy, macro-F1, per-stage F1, confusion matrix, per-subject spread,
summary-metric agreement, and external validation if any.
