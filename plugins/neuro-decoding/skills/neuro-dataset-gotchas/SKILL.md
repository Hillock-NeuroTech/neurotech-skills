---
name: neuro-dataset-gotchas
description: Audit a public or inherited neural dataset before training or analysis (BCI Competition, PhysioNet EEG Motor Movement/Imagery, OpenBMI/Lee2019, Sleep-EDF, CHB-MIT, TUH EEG, MOABB datasets, OpenNeuro BIDS sets, DANDI/NWB). Use whenever the user downloads, loads, merges or benchmarks on a dataset, sees odd results on one, or asks which subjects, channels or sessions to use.
---

# Dataset audit before you train

Most surprising results on public datasets come from the data, not the
model: mixed sampling rates, duplicated people, channel sets that change
between files, evaluation labels that differ from training labels. Spend
ten minutes on this audit before any modelling.

## 1. Run the audit

For each file or run, tabulate:

- sampling rate, number and names of channels, units, reference;
- duration, number of events per class, event code mapping;
- subject id, session id, site, date.

Then check:

1. **Rates and channels identical across files?** If not, resample and
   select a common channel set explicitly, and say so.
2. **One person, one id?** Merged or multi-site sets can list the same
   person twice. Compare demographics and feature similarity.
3. **Classes balanced per subject?** Pooled balance can hide subjects with
   one class only, which breaks per-subject CV.
4. **Labels match the documentation?** Recount events against the paper or
   README; check for off-by-one event codes and swapped class names.
5. **Train/evaluation split defined by the dataset?** Use it for comparison
   with published numbers; competitions often released evaluation labels
   separately.
6. **Data quality**: flat or saturated channels, long artifact periods,
   discontinuities, and recordings with long wake or idle periods.

Record exclusions with reasons in a table you keep with the results.

## 2. Known issues to check first

These are well-known pitfalls. Confirm each against the dataset's own
documentation before acting, since versions change.

| Dataset | Check |
|---|---|
| BCI Competition IV 2a | 22 EEG + 3 EOG channels; separate training (T) and evaluation (E) sessions; evaluation labels shipped separately |
| PhysioNet EEG Motor Movement/Imagery | several subjects are commonly excluded for sampling or annotation irregularities (often S088, S092, S100, S104); runs mix executed and imagined tasks, so select runs by task |
| Sleep-EDF | long wake periods before and after sleep inflate accuracy; trim to sleep period plus margin; older stage 3 and 4 labels map to N3 |
| CHB-MIT | channel montage changes between files of the same patient; pediatric patients; seizure annotations per file |
| TUH EEG corpora | mixed montages and sampling rates across sessions; use the corpus's train/dev/eval split and patient ids |
| MOABB datasets | use MOABB's paradigms and evaluation classes so results compare with the literature |

## 3. When merging datasets

Harmonise rate, channels, reference, filtering and units first. Keep a
dataset id column and test leave-one-dataset-out, because site effects
are large and a model can learn the site.

## Output

An audit table (file, rate, channels, duration, events per class, issues,
action) plus the final list of subjects and runs used.
