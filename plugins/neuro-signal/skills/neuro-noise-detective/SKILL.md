---
name: neuro-noise-detective
description: Diagnose noise and artifacts in neural recordings (EEG, ECoG, LFP, EMG, extracellular) from spectra or raw traces and name the likely source and fix. Use whenever the user sees hum, peaks in the spectrum, drift, flat or noisy channels, saturation, ground loops, interference from equipment, or asks why a recording is noisy, even if they only paste a PSD plot or describe the symptom.
---

# Noise detective

Start from the data, not guesses: compute spectra per channel, then match
the pattern to a source. Run the bundled script first; it does the
measurements so you only interpret.

```bash
python scripts/spectrum_report.py --data raw.npy --fs 1000 [--names names.json] [--line 50]
```

Input: array of shape (channels, samples) in volts or microvolts (`.npy`,
or any file MNE can read via `--mne-file`). Output: line frequency and
harmonics with their size above the noise floor, odd/even harmonic
balance, other narrow peaks, broadband high-frequency and slow-drift power
per channel, flat and saturated channels, and whether each problem is
common to all channels or channel-specific.

## Pattern to source

| Pattern | Likely source | Fix |
|---|---|---|
| 50/60 Hz on all channels, similar size | mains pickup; poor ground or reference contact, unshielded cables | fix ground/reference impedance, twist and shorten leads, move mains cables; then notch or ZapLine |
| 50/60 Hz on a few channels | high impedance on those electrodes | re-prep those electrodes |
| strong odd harmonics (150/180, 250/300 Hz) | non-linear loads: switching supplies, dimmers, motors | unplug or move the equipment; battery-power the amplifier |
| narrow peaks not at line multiples | monitor refresh, LED or motor drivers, Wi-Fi/BT duty cycles, stimulator | switch devices off one at a time; check the stimulator clock |
| broadband rise above about 30 Hz, temporal/frontal | muscle (EMG) | relax jaw/neck, reject or ICA |
| very slow drift below 1 Hz, large | sweat, electrode gel drying, cable movement | cooler room, re-prep, secure cables; high-pass |
| same waveform on all channels | reference or ground electrode problem | fix reference/ground |
| step changes or spikes | electrode pops, movement, cable knocks | mark and reject segments |
| flat channel | disconnected, shorted or bridged electrode | check connection; see `neuro-channel-map-verifier` for bridging |
| clipped values | amplifier range exceeded, DC offset too large | lower gain, re-prep, check DC coupling |
| periodic about 1 Hz sharp peaks | ECG | ICA or regression with ECG channel |

## Workflow

1. Run the script on a few minutes of raw (unfiltered) data.
2. Read whether the issue is common (reference/ground/environment) or
   channel-specific (that electrode).
3. Match the pattern above; propose the hardware fix first, software fix
   second (software can remove noise but cannot recover saturated data).
4. If the user can change the setup, suggest one change at a time and
   re-measure.

## Output

A short diagnosis: symptom with numbers from the report, most likely
source, hardware fix, software fix, and how to confirm.
