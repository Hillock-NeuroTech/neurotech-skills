---
name: neuro-sync-forensics
description: Align recordings and event logs that come from different clocks (EEG/ECoG amplifiers, stimulus PCs, eye trackers, cameras, implants, LSL streams, ephys systems with sync pulses). Use whenever the user needs event times in samples, merges data from two devices, sees events drifting out of place, has missing or extra sync pulses, or suspects a wrong sampling rate in a file header.
---

# Sync forensics

Two devices never share a clock. Crystals differ by tens to hundreds of
ppm (100 ppm is 0.36 s per hour), pulses get dropped, headers state a
nominal rate, and software timestamps jitter. Align with shared events,
not with nominal rates.

## 1. Find the shared events

Usually TTL sync pulses recorded on both sides (trigger channel on the
amplifier, log on the stimulus PC), a photodiode, or a sync LED seen by a
camera. Irregular intervals (for example 8-12 s random) make matching
unambiguous; regular 1 s pulses show the true sampling rate.

## 2. Fit the clock map with the bundled script

```bash
python scripts/align_clocks.py --a pc_sync_times.txt --b eeg_trigger_samples.npy \
       --b-rate 500 [--map keypress_times.txt] [--out mapped.npy]
```

`--a`: event times on clock A (seconds). `--b`: the same events on clock B
(samples or seconds, with `--b-rate` the nominal rate). The script matches
events robustly (handles dropped and spurious pulses), fits
`b = slope * a + offset` by least squares, iterates matching with the
fitted map, and reports drift in ppm, residuals, unmatched events on each
side, and the effective sampling rate. `--map` converts other clock-A times
(keypresses, stimuli) to clock B.

Check the residuals: under 1 sample means a linear map is enough. Steps in
the residuals mean a clock reset or a dropped data block; fit piecewise
between the steps.

## 3. Wrong header rate

If evenly spaced pulses of known period (for example 1 per second) give a
spacing that disagrees with the header, trust the pulses and fit the rate
from them. A constant spacing that is off by a few percent is a header or
export error, not drift.

## 4. Report

Shared events used, matched/unmatched counts, slope as ppm drift, offset,
residual RMS and max in samples, effective sampling rate, and any segments
fitted separately. Keep the fitted map with the data so others can apply it.
