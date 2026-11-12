---
name: neuro-spike-sorting-qc
description: Quality control and curation of spike-sorted units from extracellular recordings (Neuropixels, tetrodes, Utah arrays; Kilosort, MountainSort, SpykingCircus, SpikeInterface, Phy, Bombcell). Use whenever the user sorts spikes, curates clusters, decides which units are single units, computes ISI violations or other unit metrics, or deals with drift.
---

# Spike-sorting quality control

Sorter output is a list of candidate clusters, not neurons. Decide which
are well isolated single units with explicit metrics, applied the same way
to every session, and report the thresholds.

## 1. Before sorting

- Check the probe geometry file matches the hardware (site positions,
  channel order; see `neuro-channel-map-verifier`).
- Common-average or common-median reference and high-pass (about 300 Hz)
  as the sorter expects.
- Estimate and correct drift (Kilosort and SpikeInterface motion
  correction); look at the drift map before trusting long recordings.

## 2. Compute standard metrics per unit

Use SpikeInterface `compute_quality_metrics` or Bombcell:

| Metric | Measures | Commonly used threshold |
|---|---|---|
| ISI violations (refractory, about 1.5 ms) | contamination by other spikes | violation ratio below 0.5, or contamination estimate below about 10% |
| Amplitude cutoff | spikes lost below detection threshold | below 0.1 |
| Presence ratio | unit present across the session | above 0.9 |
| Firing rate | very low rates make metrics unreliable | above about 0.1 Hz |
| SNR / amplitude | separation from noise | dataset dependent |
| Isolation distance, L-ratio, d' | cluster separation in feature space | relative, compare within dataset |
| Drift | position change over time | flag large drift |

The thresholds in the table follow commonly used defaults (Allen Institute
pipelines; Siegle et al. 2021) and are a starting point, not a rule. State
the ones you use.

## 3. Curate

1. Auto-label with metrics (good / MUA / noise).
2. Inspect borderline units in Phy or SpikeInterface GUI: waveform shape
   and spatial footprint, autocorrelogram (refractory dip), amplitude over
   time (drift or loss), cross-correlograms with neighbours (merge
   candidates show a refractory dip in the cross-correlogram).
3. Remove noise clusters (non-physiological waveforms, waveforms on all
   channels, line-frequency locked).
4. Log every manual merge or split.

## 4. Report

Sorter and version, parameters, drift correction, metric thresholds,
counts of good/MUA/noise units per session, and which analyses use only
single units vs multi-unit activity.

## References

Hill, Mehta & Kleinfeld 2011 (quality metrics); Siegle et al. 2021
(Allen Brain Observatory); Fabre et al. 2023 (Bombcell); Buccino et al.
2020 (SpikeInterface); Pachitariu et al. 2024 (Kilosort4).
