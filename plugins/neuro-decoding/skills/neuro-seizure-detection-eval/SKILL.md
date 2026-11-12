---
name: neuro-seizure-detection-eval
description: Evaluate EEG/iEEG seizure detection or prediction algorithms the way clinicians and challenges score them. Use whenever the user builds or reports a seizure detector or forecaster, computes sensitivity or false alarms, uses CHB-MIT, TUH Seizure, Siena or ward recordings, or compares against published seizure results.
---

# Seizure detection evaluation

Sample- or window-level accuracy is meaningless for seizures: they are
rare, so a detector that never fires scores above 99%. Clinical usefulness
is about catching each seizure quickly without too many false alarms.

## 1. Split by patient, and by time within patient

- Patient-independent claims: leave-one-patient-out.
- Patient-specific claims: train on earlier seizures, test on later ones
  (never random windows; windows around one seizure are near-duplicates).
- Prediction/forecasting: also hold out the interictal data in time order,
  and keep a gap around each seizure as the dataset protocol defines.

## 2. Score events, not windows

Convert detector output to events (threshold, smoothing, minimum duration,
merge gaps), then compare with reference seizures:

- **Sensitivity**: fraction of reference seizures overlapped by a detection.
- **False alarms per hour (FA/h, or per 24 h)**: detections that overlap no
  seizure, divided by recording hours.
- **Latency**: detection onset minus reference onset, for detected seizures.
- Precision and F1 on events as secondary numbers.

`scripts/event_scoring.py` computes all of these from two CSVs:

```bash
python scripts/event_scoring.py --ref ref.csv --det det.csv --hours 72.5 [--tolerance 0]
```

Each CSV has `onset_s,offset_s` (optionally `record` for multi-file data).

Use any-overlap scoring unless the user's benchmark defines otherwise
(TUH and challenge papers sometimes use time-aligned or epoch-based
variants; report which).

## 3. Choose the operating point honestly

Pick the threshold on training data, then report test sensitivity and
FA/h at that threshold. A full sensitivity vs FA/h curve is useful, but
the headline must be one fixed operating point.

## 4. Report

Patients, recording hours, seizures per patient, split scheme, threshold
choice, event sensitivity, FA/h, median latency, and per-patient results
(averages hide patients where it fails).
