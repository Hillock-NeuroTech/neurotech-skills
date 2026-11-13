---
name: neuro-dbs-sensing-data
description: Load, time-align and analyse sensing data from DBS and other bidirectional implants (Medtronic Percept PC/RC BrainSense JSON exports, Summit RC+S, NeuroPace RNS), including beta-band and adaptive DBS analyses. Use whenever the user works with implant LFP exports, BrainSense streaming or timeline data, packet loss, implant timestamps, ECG contamination, stimulation artifacts in implant recordings, or aDBS biomarkers.
---

# Implant sensing data

Implant exports are not continuous recordings: data come in packets with
their own timestamps, packets go missing, several clocks are involved, and
ECG and stimulation leak into the LFP. Rebuild a clean, gap-aware time
series before any spectral analysis.

## 0. Load the tool reference

Read `references/percept-and-dbs-tools.md`: every Percept export section
and its timing fields, the perceive toolbox, Lead-DBS and OSS-DBS. Rebuild
Percept streams with `scripts/percept_timedomain.py`, which keeps lost
packets as NaN gaps.

## 1. Load with an established reader

- Medtronic Percept: the JSON session export has separate sections for
  survey, streaming and timeline (chronic) data. Community readers exist
  (for example the Perceive toolbox in MATLAB and Python ports); check
  their current version against your firmware.
- Summit RC+S: several JSON files per session; use the open processing
  pipeline from the investigators who released it (Sellers et al. 2021
  describe the data format and timing problems).
- Record device model, firmware, sensing configuration (contacts, sampling
  rate, filters) from the export, not from memory.

## 2. Reconstruct time

1. Use packet timestamps and packet sizes to place samples; detect gaps
   (missing packets) and mark them as NaN rather than concatenating.
2. Convert device time to wall-clock time using the export's reference
   timestamps; keep the offset and any drift (see `neuro-sync-forensics`
   for aligning to external recordings via shared events such as
   stimulation onset artifacts).
3. Report total duration, number and length of gaps, and the fraction of
   data lost.

## 3. Clean

- **ECG**: cardiac artifacts are common, especially with single-sided
  sensing configurations. Detect QRS complexes (from the LFP itself or an
  external ECG) and remove with template subtraction; check the spectrum
  before and after.
- **Stimulation**: identify stimulation frequency and its aliases at the
  sensing sampling rate; analyse bands away from them; mark ramp periods.
- **Movement and telemetry artifacts**: mark and exclude.

## 4. Analyse gap-aware

Compute spectra with Welch on clean contiguous segments only (never
across gaps), average by segment length, and report beta peak frequency
and power with the segment count. For chronic timeline data, analyse
power over time-of-day and against stimulation and medication logs. For
aDBS, report the biomarker definition, thresholds, and how often
stimulation changed.

## Output

Device and configuration, time reconstruction summary (gaps, loss),
cleaning steps with before/after spectra, analysis results per segment
count.
