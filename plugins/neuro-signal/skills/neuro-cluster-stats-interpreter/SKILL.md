---
name: neuro-cluster-stats-interpreter
description: Run and correctly interpret cluster-based permutation tests and TFCE on EEG/MEG/iEEG data over time, frequency and space (MNE permutation_cluster_test, spatio_temporal_cluster_test, FieldTrip ft_timelockstatistics/ft_freqstatistics). Use whenever the user tests ERP, time-frequency or sensor/source differences with cluster statistics, picks a cluster-forming threshold, or describes when or where an effect starts, peaks or is located.
---

# Cluster-based permutation tests: run and read them right

A cluster test controls the family-wise error for the hypothesis "the
conditions do not differ anywhere". A significant cluster rejects that
null. It does not say the effect starts at the cluster's first sample, is
confined to its channels, or is absent elsewhere (Maris & Oostenveld
2007; Sassenhagen & Draschkow 2019).

## 1. Set up

- Define the data dimensions (time, frequency, channels or vertices) and
  the adjacency (channel neighbours from the montage).
- Choose the test statistic for the design: independent or paired t,
  F for several conditions; within-subject designs permute condition
  labels within subject (sign-flip for paired differences).
- Cluster-forming threshold: commonly the t value for p < 0.05 two-sided.
  It is arbitrary and changes cluster shape; decide it before looking, or
  use TFCE (Smith & Nichols 2009; in MNE pass `threshold=dict(start=0,
  step=0.2)`), which removes the threshold choice.
- Permutations: at least 1000 for a reported p; more for small p.
- Restrict the analysis window a priori if you have a hypothesis; a
  smaller search space gains power honestly.

## 2. Report what the test supports

Say: "the conditions differed (cluster-based permutation test, p = X); the
difference was most pronounced over channels ... between about T1 and T2".
Do not say: "the effect started at T1", "the effect was located at
channels ...", or "no effect at other channels".

For onset or latency claims, use a method built for it: jackknife-based
onset estimation on averaged waveforms, fractional area latency, or
bootstrap confidence intervals of onset.

## 3. Common mistakes

- Running separate tests per channel or time window, then using clusters.
- Changing the threshold or window after seeing results.
- Reporting several clusters from one test as independent findings with
  their own exact extents.
- Using cluster p-values to compare effect sizes between conditions.

## Output

Design, statistic, adjacency, threshold or TFCE, permutations, window,
p-values per cluster, and wording that stays within what the test shows.
