---
name: neuro-channel-map-verifier
description: Verify that channel labels, electrode positions and probe geometry match the physical recording (EEG caps, ECoG grids, sEEG shafts, Neuropixels and silicon probes, Utah arrays, headstage and connector mappings). Use whenever the user sets up a montage or probe map, suspects swapped or mislabelled channels, sees topographies or depth profiles that look wrong, or wants to detect bridged electrodes.
---

# Channel-map verification

A wrong map produces plausible-looking but wrong topographies, source
estimates and spike locations. Check the map against the physics of the
signal: nearby electrodes look alike, and the pattern of similarity should
follow the geometry.

## 1. Similarity should follow distance

Compute the correlation matrix of a few minutes of broadband or alpha-band
data and compare with the distance matrix from the montage or probe file.
Neighbouring sites should correlate most. For each channel, list its five
most correlated channels and check they are physical neighbours. Channels
whose best partners are far away are mislabelled or swapped; blocks of
channels behaving this way point to a swapped connector or headstage (for
example a 32-channel block offset).

## 2. Bridged electrodes (EEG)

Gel bridges make two electrodes nearly identical. Compute the variance of
the difference between each pair (electrical distance; Tenke & Kayser
2001; Alschuler et al. 2014). Pairs with near-zero difference variance
compared with other neighbours are bridged. Re-prep or treat the pair as
one channel; do not interpolate one from the other.

## 3. Physiological landmarks

- EEG: alpha largest at occipital sites with eyes closed; blinks largest
  at Fp1/Fp2 with frontal-to-posterior decay; lateral eye movements
  reverse polarity between F7 and F8. Wrong patterns mean a wrong montage.
- ECoG/sEEG: line noise and artifacts shared within a shaft or grid; check
  contact order along a shaft from the depth gradient of signals.
- Laminar or Neuropixels probes: LFP current-source density should show a
  plausible laminar profile; a spike's waveform should spread over a few
  adjacent sites in the probe geometry. Spikes "jumping" between distant
  sites indicate a wrong geometry file.
- Utah arrays: compare the map from the manufacturer's connector file;
  correlations should form a grid, not random pairs.

## 4. Fix and record

Correct the mapping file, not the data; keep the old and new map with the
evidence (correlation-vs-distance plot). Re-run downstream analyses that
used positions.

## Output

Map checked, method, channels or blocks found swapped, bridged pairs,
evidence plot description, corrected mapping.
