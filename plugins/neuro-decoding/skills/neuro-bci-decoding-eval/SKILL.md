---
name: neuro-bci-decoding-eval
description: Leak-free evaluation of neural decoders (EEG, MEG, ECoG, iEEG, spikes, BCI). Use whenever the user trains or cross-validates a classifier or regressor on neural data, reports a decoding accuracy, compares against chance or a published number, tunes hyperparameters, selects features or channels, or asks whether a BCI result is real. Covers subject/session/trial grouping, overlapping windows, fitted preprocessing inside folds, nested tuning, small-sample chance levels, permutation tests and confound checks.
---

# Neural decoder evaluation

Goal: report a number that will hold on new data. Neural data has strong
temporal autocorrelation and subject fingerprints, so ordinary shuffled
k-fold almost always overstates performance. Decide the split first, then
everything else follows from it.

## 1. Define the claim, then the unit of independence

Write down what the result must generalise to, and split on that unit:

| Claim | Split by | sklearn |
|---|---|---|
| works on new people | subject (or person: check for duplicate IDs across sites) | `StratifiedGroupKFold`, `LeaveOneGroupOut` |
| works tomorrow / next session | session; train on earlier, test on later | custom forward split |
| works on new trials, same session | trial (never window or segment) | `GroupKFold` on trial id |
| online, causal use | contiguous blocks with a gap | blocked splits + causal features |

Windows cut from one trial, segments from one recording, and copies made by
augmentation all share a group. If the design is blocked (all of one class
in one block), class is confounded with time: say so and do not report a
decoding accuracy from it.

## 2. Put every fitted step inside the folds

Anything that sees labels or learns statistics is part of the model:
scaling, PCA/ICA fitted for the decoder, CSP/xDAWN, feature or channel
selection, oversampling/augmentation, early stopping, threshold choice.
Use one `Pipeline` and pass `groups=`. Watch for steps hidden in loaders,
cached feature files and config keys the code ignores; read the data path
end to end before trusting a number.

Hyperparameter or pipeline search needs nested CV (inner search, outer
estimate). Reporting the best of many configurations on the same folds is
selection bias, not performance.

## 3. Report against the right baseline

- Chance is not 1/k for small n. Use the binomial threshold for the test
  count, or a permutation test that reruns the whole pipeline with labels
  permuted at the group level (Combrisson & Jerbi 2015).
- Imbalanced classes: report balanced accuracy and the majority baseline.
- Fold-to-fold standard error understates uncertainty (Varoquaux 2018);
  give an interval from the pooled out-of-fold predictions or repeats.
- Time-resolved decoding needs correction across time points (max-statistic
  or cluster permutation).

`scripts/leakage_safe_eval.py` does steps 1-3 in one call:

```bash
python scripts/leakage_safe_eval.py --X X.npy --y y.npy --groups subject.npy --model lda --n-perm 500
```

It prints grouped CV accuracy and balanced accuracy, the majority baseline,
the binomial chance threshold for the sample size, and a group-respecting
permutation p-value. Import `evaluate()` to use your own pipeline.

## 4. Rule out confounds before interpreting

Quick checks that catch most false positives:

- Train on time alone (trial index or timestamp). If it decodes as well,
  slow drift explains the result.
- Train on EOG/EMG channels alone, and on non-neural columns (epoch length,
  trial counters, impedance). Anything that decodes is a confound.
- Decoding before stimulus onset usually means a zero-phase filter or
  baseline correction smeared the response backwards (van Driel et al.
  2021). Re-run with a causal or milder filter.
- Offline whole-trial features with `filtfilt` do not transfer online;
  re-evaluate with causal filters and sliding windows.

## 5. Write the result

State: split unit and scheme, n per class, metric with interval, chance
level used, permutation p, and the checks from step 4. Scope the claim to
the datasets tested; one dataset is not "state of the art" (Jayaram &
Barachant 2018 show most methods do not transfer).

## References

Kriegeskorte et al. 2009 (double dipping); Combrisson & Jerbi 2015 (chance);
Varoquaux 2018 (CV error bars); Li et al. 2020 (block design); Brookshire
et al. 2024 (subject leakage in DNN-EEG); van Driel et al. 2021 (filter
artifacts); Jayaram & Barachant 2018 (MOABB).
