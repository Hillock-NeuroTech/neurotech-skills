---
name: neuro-router
description: Entry point for any neurotechnology, neural engineering, BCI, EEG/MEG/ECoG/LFP, spike, neuromodulation or neural-device task. Use first whenever a request involves brain or nerve signals, brain-computer interfaces, neurostimulation or neural hardware, to pick the right Hillock workflow skill and agent instead of researching the approach from scratch.
---

# Hillock router

Pick the workflow, load it, follow it. Start with `neuro-file-formats` whenever data has to be loaded first. Each skill already contains the
field's standard procedure, defaults and checks, so there is no need to
research the method first. If several apply, run them in the order given.

## Foundations (neuro-router; installed with the router)

| Request | Skill |
|---|---|
| open, load, convert or export any recording file; wrong units, rate or events after loading | neuro-file-formats |
| find a dataset or benchmark, where data lives, how to download it | neuro-data-sources |

## Decoding and evaluation (neuro-decoding)

| Request | Skill |
|---|---|
| train, cross-validate or report a decoder or classifier | neuro-bci-decoding-eval |
| implant decoder over days, recalibration | neuro-ibci-decoder-stability |
| load, audit or merge a dataset | neuro-dataset-gotchas |
| seizure detection or forecasting | neuro-seizure-detection-eval |
| sleep staging | neuro-sleep-staging-eval |
| pretrained EEG / foundation models | neuro-foundation-model-eval |

## Signal analysis (neuro-signal)

| Request | Skill |
|---|---|
| filtering, referencing, ICA, epoching, artifacts | neuro-eeg-preprocessing-review |
| spike sorting, unit curation | neuro-spike-sorting-qc |
| noisy recording, hum, spectrum peaks | neuro-noise-detective |
| montage, probe map, swapped or bridged channels | neuro-channel-map-verifier |
| coherence, PLV, wPLI, Granger, networks | neuro-connectivity-claims-check |
| cluster permutation tests, TFCE | neuro-cluster-stats-interpreter |

## Real time and hardware timing (neuro-realtime)

| Request | Skill |
|---|---|
| online BCI, LSL, BrainFlow, neurofeedback, latency | neuro-realtime-bci-pipeline |
| align clocks, sync pulses, wrong sampling rate | neuro-sync-forensics |
| stimulus timing, photodiode, frame drops | neuro-stimulus-timing-audit |
| phase-locked or burst-triggered stimulation | neuro-phase-locked-stim-eval |
| stimulation artifacts in recordings | neuro-stim-artifact-recovery |
| decoder or filter to embedded C / fixed point | neuro-decoder-to-firmware |

## Neuromodulation (neuro-stim; research support only)

| Request | Skill |
|---|---|
| charge, charge density, Shannon, safe limits | neuro-stim-safety-check |
| TMS / tES field modeling, SimNIBS, dose | neuro-nibs-field-modeling |
| DBS / implant sensing exports, aDBS | neuro-dbs-sensing-data |
| focused ultrasound planning | neuro-tus-dose-planning |
| peripheral nerve stimulation models | neuro-nerve-stim-modeling |
| sham conditions, blinding | neuro-sham-and-blinding-design |

## Devices (neuro-device; engineering support only)

| Request | Skill |
|---|---|
| amplifier, ADC, noise budget | neuro-frontend-design |
| electrode impedance, CSC, charge-injection limit | neuro-electrode-electrochemistry |
| implant power, data rate, heating | neuro-implant-power-thermal-budget |
| standards, verification, traceability | neuro-device-regulatory |
| SOUP list, SBOM | neuro-soup-inventory |

## Hand off instead of rebuilding

- NWB conversion and DANDI: use CatalystNeuro's skills (NeuroConv-based)
  if installed, otherwise NeuroConv documentation.
- BIDS conversion and validation, Neuropixels pipelines, NeuroKit2
  physiology: use the K-Dense scientific skills if installed, otherwise
  MNE-BIDS / SpikeInterface / NeuroKit2 documentation.

## Agents

For multi-step work, delegate to the bundle's agent:
`neuro-decoding-reviewer`, `neuro-signal-reviewer`, `neuro-rig-engineer`,
`neuro-stim-engineer`, `neuro-device-engineer`; `neuro-lead` coordinates
work that spans several bundles.
