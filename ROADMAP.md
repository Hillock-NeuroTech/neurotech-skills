# Skills: 30 workflows in five bundles plus a router

Suite: **Hillock**. Repo: `Hillock-NeuroTech/neurotech-skills`. Marketplace name: `hillock`.

## Naming rule

Every skill name starts with `neuro-`. A skill is often seen alone (in a
skill list, on a registry, copied into another agent) where the repo and
bundle names are not visible, so the name itself has to say the field.
Bundle (plugin) names follow the same rule, so nothing depends on the
suite name.

## Why these skills exist

Each skill packages the field's established workflow for one task: the
order of steps, the defaults, the checks and the reporting standard. With
it loaded, Claude follows that path directly instead of researching the
approach, which gives consistent results with less time and fewer tokens.

Status values: `draft` (written from published practice, scripts tested)
-> `reviewed` (signed off by a named practitioner). All skills are
`draft` in v0.1.

## Skills

| # | Bundle | Skill | What it does | Origin | Status |
|---|---|---|---|---|---|
| 1 | neuro-router | neuro-router | Thin index; hands NWB and BIDS work to CatalystNeuro and K-Dense | brief | draft |
| 2 | neuro-decoding | neuro-bci-decoding-eval | Leak-free splits, real chance levels, permutation tests | brief | draft |
| 3 | neuro-decoding | neuro-ibci-decoder-stability | Cross-day evaluation in the FALCON style | brief | draft |
| 4 | neuro-decoding | neuro-dataset-gotchas | Known quirks of each public dataset, applied before training | proposed | draft |
| 5 | neuro-decoding | neuro-seizure-detection-eval | Event-based scoring and false alarms per hour | proposed | draft |
| 6 | neuro-decoding | neuro-sleep-staging-eval | Subject-wise splits and agreement metrics | proposed | draft |
| 7 | neuro-decoding | neuro-foundation-model-eval | Fair comparison of pretrained EEG models against simple baselines | proposed | draft |
| 8 | neuro-signal | neuro-eeg-preprocessing-review | Audits filter, reference, ICA and rejection choices | brief | draft |
| 9 | neuro-signal | neuro-spike-sorting-qc | Unit quality metrics and curation | brief | draft |
| 10 | neuro-signal | neuro-noise-detective | Names the noise source from a spectrum or raw trace | proposed | draft |
| 11 | neuro-signal | neuro-channel-map-verifier | Catches swapped headstages, wrong probe geometry, bridged electrodes | proposed | draft |
| 12 | neuro-signal | neuro-connectivity-claims-check | Flags connectivity explained by volume conduction or shared reference | proposed | draft |
| 13 | neuro-signal | neuro-cluster-stats-interpreter | Stops over-claiming from cluster permutation tests | proposed | draft |
| 14 | neuro-realtime | neuro-realtime-bci-pipeline | Acquisition, marker sync, measured latency and jitter | brief | draft |
| 15 | neuro-realtime | neuro-sync-forensics | Aligns recordings from several clocks and reports residual drift | proposed | draft |
| 16 | neuro-realtime | neuro-stimulus-timing-audit | Checks frame drops and stimulus timing against a photodiode trace | proposed | draft |
| 17 | neuro-realtime | neuro-phase-locked-stim-eval | Measures real-time phase-estimate error against true phase | proposed | draft |
| 18 | neuro-realtime | neuro-stim-artifact-recovery | Removes stimulation artifact and reports lost signal | proposed | draft |
| 19 | neuro-realtime | neuro-decoder-to-firmware | Ports a Python decoder to fixed-point embedded code with matching tests | proposed | draft |
| 20 | neuro-stim | neuro-stim-safety-check | Charge and charge-density limits, and where they stop applying | brief | draft |
| 21 | neuro-stim | neuro-nibs-field-modeling | SimNIBS setup plus dose-reporting checklist | brief | draft |
| 22 | neuro-stim | neuro-dbs-sensing-data | Parses and aligns implant logs, including heartbeat contamination | brief | draft |
| 23 | neuro-stim | neuro-tus-dose-planning | Acoustic simulation and safety reporting for focused ultrasound | proposed | draft |
| 24 | neuro-stim | neuro-nerve-stim-modeling | Cuff-electrode and fibre-recruitment models for peripheral nerve | proposed | draft |
| 25 | neuro-stim | neuro-sham-and-blinding-design | Designs sham conditions and checks whether blinding held | proposed | draft |
| 26 | neuro-device | neuro-frontend-design | Noise budgets, impedance, converter configuration | brief | draft |
| 27 | neuro-device | neuro-electrode-electrochemistry | Fits impedance spectra and voltage transients; charge-injection limits | proposed | draft |
| 28 | neuro-device | neuro-implant-power-thermal-budget | Trades channel count and data rate against power and tissue heating | proposed | draft |
| 29 | neuro-device | neuro-device-regulatory | Maps a design to regulator test areas and builds the risk trace | brief | draft |
| 30 | neuro-device | neuro-soup-inventory | Turns a dependency list into the third-party software file IEC 62304 expects | proposed | draft |

## Next

1. Named practitioner review for each bundle (moves skills to `reviewed`).
2. Token and time comparison with and without each skill on the benchmark
   tasks (`claude plugin eval`).
3. More bundled scripts where agents still write the same code each time.
