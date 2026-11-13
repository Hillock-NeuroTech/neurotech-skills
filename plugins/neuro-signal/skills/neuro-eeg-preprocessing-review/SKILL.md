---
name: neuro-eeg-preprocessing-review
description: Design or audit an EEG/MEG preprocessing pipeline (MNE-Python, EEGLAB, FieldTrip, Brainstorm). Use whenever the user filters, re-references, runs ICA, rejects artifacts, interpolates channels, epochs or baseline-corrects EEG/MEG data, asks which settings to use, or wants a pipeline checked before analysis, ERP, time-frequency or decoding.
---

# EEG/MEG preprocessing: settings and order

Preprocessing choices can create or remove effects. Use this order and
these defaults unless there is a reason not to, and record every choice.

## 0. Load the toolbox reference

Read the file for the toolbox in use before writing or reviewing code:

| Toolbox | Reference |
|---|---|
| MNE-Python (and MNE-BIDS-Pipeline, MEG Maxwell filtering) | `references/mne.md` |
| EEGLAB (clean_rawdata, ICLabel, ERPLAB) | `references/eeglab.md` |
| FieldTrip | `references/fieldtrip.md` |
| Brainstorm | `references/brainstorm.md` |
| Moving between toolboxes, or reviewing a methods section | `references/equivalents.md` |

Each has a working recipe, the toolbox's own traps, and what to report.
Loading files of any format: `neuro-file-formats`.

## 1. Recommended order

1. Inspect raw data: units, sampling rate, channel types, montage, events.
2. Mark bad channels (flat, saturated, noisy; PREP-style criteria) before
   anything that mixes channels.
3. High-pass filter (see 2). Optionally low-pass and resample (resampling
   needs an anti-alias low-pass; MNE applies one).
4. Line-noise removal: notch at line frequency and harmonics, or spectral
   methods (ZapLine, CleanLine) when you want to keep the band intact.
5. Re-reference (average reference only with good head coverage and bad
   channels excluded or interpolated first).
6. ICA: fit on a copy high-passed at 1 Hz (more stable), apply the
   unmixing to the data you analyse (Winkler et al. 2015). Classify
   components with ICLabel or EOG/ECG correlation; remove only clear
   ocular, cardiac, muscle or line components.
7. Interpolate bad channels.
8. Epoch, then reject or repair epochs (thresholds or Autoreject).
9. Baseline-correct (ERPs) or not (decoding: baseline correction can move
   effects; see `neuro-bci-decoding-eval`).

## 2. Filter defaults and why

| Analysis | High-pass | Low-pass | Notes |
|---|---|---|---|
| ERP, slow components (P300, N400, CNV) | 0.01-0.1 Hz | 30-40 Hz | above 0.1 Hz distorts and can invert slow ERPs (Acunzo et al. 2012; Tanner et al. 2015) |
| Time-frequency, oscillations | 0.5-1 Hz | above band of interest | |
| Decoding | as low as practical; check time shifts | task dependent | zero-phase filters move effects in time |
| Real-time | causal filters only | | see `neuro-realtime-bci-pipeline` |

Prefer linear-phase FIR (MNE default `firwin`) with automatic transition
bands. Report filter type, order or length, cutoffs, transition bandwidth,
and causal vs zero-phase (Widmann et al. 2015). Check the impulse response
for ringing if effects sit close to sharp events.

## 3. Audit checklist for an existing pipeline

- Units and scaling correct (V vs uV)? Montage matches the cap?
- High-pass cutoff appropriate for the components analysed?
- Was a filter applied to epochs instead of continuous data (edge effects)?
- Reference applied before bad-channel handling? Average reference with
  few channels?
- ICA fitted on data with slow drifts, or on too little data (rule of
  thumb: many times more samples than channels squared)?
- Components removed on unclear grounds?
- Rejection thresholds identical across conditions, and trial counts
  balanced or reported per condition?
- Baseline window free of stimulus-related activity?

## Output

A table: step, setting, reason, reference. Flag each deviation with its
likely effect on the user's analysis.

## References

Widmann, Schroger & Maess 2015; Acunzo et al. 2012; Tanner et al. 2015;
Winkler et al. 2015; Bigdely-Shamlo et al. 2015 (PREP); Pion-Tonachini et
al. 2019 (ICLabel); Jas et al. 2017 (Autoreject).
