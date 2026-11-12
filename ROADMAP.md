# Roadmap: 30 skills in five bundles

Suite: **Hillock**. Repo: `hillock-neuro/neurotech-skills`. Marketplace name: `hillock`.

## Naming rule

Every skill name starts with `neuro-`. A skill is often seen alone (in a
skill list, on a registry, copied into another agent) where the repo and
bundle names are not visible, so the name itself has to say the field.
Bundle (plugin) names follow the same rule, so nothing depends on the
suite name.

## Build gate

A skill is built only after its pitfall tasks show the base model failing
without it. A skill folder appears under `plugins/<bundle>/skills/` only
once it passes that gate; until then it exists here and in `research/`.

Status values: `planned` → `probed` → `dossier` → `benchmarked` → `draft` → `reviewed`, or `parked` when the base model already passes.

Origin: `brief` = evidence in the research brief. `proposed` = added later
from known field pain points, evidence not yet sourced.

## Skills

| # | Bundle | Skill | What it does | Origin | Status |
|---|---|---|---|---|---|
| 1 | neuro-router | neuro-router | Thin index; hands NWB and BIDS work to CatalystNeuro and K-Dense | brief | planned |
| 2 | neuro-decoding | neuro-bci-decoding-eval | Leak-free splits, real chance levels, permutation tests | brief | parked (base model 30/30, v1+v2) |
| 3 | neuro-decoding | neuro-ibci-decoder-stability | Cross-day evaluation in the FALCON style | brief | planned |
| 4 | neuro-decoding | neuro-dataset-gotchas | Known quirks of each public dataset, applied before training | proposed | planned |
| 5 | neuro-decoding | neuro-seizure-detection-eval | Event-based scoring and false alarms per hour | proposed | planned |
| 6 | neuro-decoding | neuro-sleep-staging-eval | Subject-wise splits and agreement metrics | proposed | planned |
| 7 | neuro-decoding | neuro-foundation-model-eval | Fair comparison of pretrained EEG models against simple baselines | proposed | planned |
| 8 | neuro-signal | neuro-eeg-preprocessing-review | Audits filter, reference, ICA and rejection choices | brief | planned |
| 9 | neuro-signal | neuro-spike-sorting-qc | Unit quality metrics and curation | brief | planned |
| 10 | neuro-signal | neuro-noise-detective | Names the noise source from a spectrum or raw trace | proposed | planned |
| 11 | neuro-signal | neuro-channel-map-verifier | Catches swapped headstages, wrong probe geometry, bridged electrodes | proposed | planned |
| 12 | neuro-signal | neuro-connectivity-claims-check | Flags connectivity explained by volume conduction or shared reference | proposed | planned |
| 13 | neuro-signal | neuro-cluster-stats-interpreter | Stops over-claiming from cluster permutation tests | proposed | planned |
| 14 | neuro-realtime | neuro-realtime-bci-pipeline | Acquisition, marker sync, measured latency and jitter | brief | planned |
| 15 | neuro-realtime | neuro-sync-forensics | Aligns recordings from several clocks and reports residual drift | proposed | probed: base model 2/2 |
| 16 | neuro-realtime | neuro-stimulus-timing-audit | Checks frame drops and stimulus timing against a photodiode trace | proposed | planned |
| 17 | neuro-realtime | neuro-phase-locked-stim-eval | Measures real-time phase-estimate error against true phase | proposed | planned |
| 18 | neuro-realtime | neuro-stim-artifact-recovery | Removes stimulation artifact and reports lost signal | proposed | planned |
| 19 | neuro-realtime | neuro-decoder-to-firmware | Ports a Python decoder to fixed-point embedded code with matching tests | proposed | probed: base model 2/2 |
| 20 | neuro-stim | neuro-stim-safety-check | Charge and charge-density limits, and where they stop applying | brief | probed: base model 2/2 |
| 21 | neuro-stim | neuro-nibs-field-modeling | SimNIBS setup plus dose-reporting checklist | brief | planned |
| 22 | neuro-stim | neuro-dbs-sensing-data | Parses and aligns implant logs, including heartbeat contamination | brief | planned |
| 23 | neuro-stim | neuro-tus-dose-planning | Acoustic simulation and safety reporting for focused ultrasound | proposed | planned |
| 24 | neuro-stim | neuro-nerve-stim-modeling | Cuff-electrode and fibre-recruitment models for peripheral nerve | proposed | planned |
| 25 | neuro-stim | neuro-sham-and-blinding-design | Designs sham conditions and checks whether blinding held | proposed | planned |
| 26 | neuro-device | neuro-frontend-design | Noise budgets, impedance, converter configuration | brief | planned |
| 27 | neuro-device | neuro-electrode-electrochemistry | Fits impedance spectra and voltage transients; charge-injection limits | proposed | planned |
| 28 | neuro-device | neuro-implant-power-thermal-budget | Trades channel count and data rate against power and tissue heating | proposed | planned |
| 29 | neuro-device | neuro-device-regulatory | Maps a design to regulator test areas and builds the risk trace | brief | planned |
| 30 | neuro-device | neuro-soup-inventory | Turns a dependency list into the third-party software file IEC 62304 expects | proposed | planned |

## Order of work

1. `neuro-bci-decoding-eval` end to end: dossier → pitfall tasks → no-skill
   baseline → skill → reviewer. This sets the template.
2. Rest of the brief's wave 1: `neuro-realtime-bci-pipeline`,
   `neuro-eeg-preprocessing-review`.
3. The five lead proposals, each gated on its dossier: `neuro-sync-forensics`,
   `neuro-dataset-gotchas`, `neuro-decoder-to-firmware`, `neuro-noise-detective`,
   `neuro-soup-inventory`.
4. Everything else, in the order the dossiers show the largest baseline failure.

## Findings so far (2026-11-12, Claude Opus 5.5, no skill)

| Skill | Test | Result |
|---|---|---|
| neuro-bci-decoding-eval | 20 visible traps (v1) + 10 hidden traps (v2) | 30/30 passed, parked |
| neuro-sync-forensics | clock drift with dropped and spurious pulses; wrong header rate | 2/2 passed |
| neuro-stim-safety-check | microelectrode where Shannon is invalid; DBS charge density vs cap | 2/2 passed |
| neuro-decoder-to-firmware | integer-only C decoder and 0.1 Hz high-pass, run on hidden signals | 2/2 passed |

All tasks: `benchmark/`. One run per task, Opus 5.5 only. In every task the
model found the trap without being pointed at it, and often added checks or
warnings the task did not ask for.

What this changes: on these four areas the strongest model does not need a
knowledge skill to avoid the known failures. Remaining places a skill could
still add lift, each untested:
- smaller or cheaper models (Sonnet, Haiku), which many users run;
- reliability over repeats rather than single runs;
- long sessions where the trap shows up late, after unrelated work;
- knowledge the model cannot have: lab- or vendor-specific formats, SDKs and
  devices, rules newer than the model's training data, a lab's own SOPs.
