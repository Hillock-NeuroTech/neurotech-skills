---
name: neuro-stimulus-timing-audit
description: Measure and correct stimulus presentation timing for EEG/MEG/BCI experiments using a photodiode, microphone or trigger loopback (PsychoPy, Psychtoolbox, Presentation, Unity, web experiments, SSVEP/P300 spellers). Use whenever the user asks how accurate their stimulus timing is, sees jittery or late ERPs, checks frame drops or display latency, or needs to correct event times before epoching.
---

# Stimulus timing audit

The time a script logs a stimulus is not the time light leaves the screen
or sound leaves the speaker. Displays add a fixed lag plus frame-quantised
jitter, and dropped frames add whole frame periods. Measure with a sensor
on the output, recorded on the same amplifier as the brain data.

## 1. Set up the measurement

- Photodiode taped over a small patch in a screen corner that flips white
  with each stimulus; record it on an aux channel of the EEG amplifier.
- Audio: split the audio output into an aux channel or use a microphone.
- Keep the software marker (or TTL) too; the audit compares the two.

## 2. Measure with the bundled script

```bash
python scripts/photodiode_lag.py --sensor aux.npy --fs 1000 --markers marker_samples.npy \
       [--refresh 60] [--window-ms 200] [--polarity rise]
```

It finds the sensor onset after each marker (half-amplitude crossing),
reports lag statistics in ms, missed onsets, and whether lags cluster at
multiples of the frame period (frame drops). `--out corrected.npy` writes
corrected event samples.

## 3. Interpret

| Result | Meaning | Action |
|---|---|---|
| constant lag, small spread (under 1 ms) | display/audio latency only | shift events by the median lag |
| spread about one frame period | marker not synced to the display flip | send marker on flip (PsychoPy `win.callOnFlip`, Psychtoolbox `Screen('Flip')` timestamp) or use sensor onsets as events |
| lags at extra whole frames | dropped frames | reduce load, disable compositor effects, check refresh rate setting |
| missed onsets | stimulus not shown or sensor misplaced | check the log for those trials |

For SSVEP or flicker stimuli also check the actual flicker frequency from
the sensor spectrum, since frame drops shift it.

## 4. Report

Display/audio device, refresh rate, number of events, median lag, spread
(SD and range), frame drops, missed events, and the correction applied.
