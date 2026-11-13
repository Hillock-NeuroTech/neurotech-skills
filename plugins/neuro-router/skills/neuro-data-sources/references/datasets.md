# Datasets and archives

MOABB names checked against MOABB 1.7.2 and `mne.datasets` against MNE
1.12 (November 2026); archive links checked to respond on 13 November
2026. Subject counts are MOABB's. Dataset versions change: confirm on the
dataset page.

## Archives

| Archive | Holds | Access route |
|---|---|---|
| [OpenNeuro](https://openneuro.org) | BIDS datasets: MRI, EEG, MEG, iEEG, fNIRS, PET | web, `openneuro-py`, DataLad; mostly CC0 |
| [NEMAR](https://nemar.org) | OpenNeuro EEG, MEG and iEEG with EEGLAB-processed views and HPC compute | web |
| [DANDI Archive](https://dandiarchive.org) | NWB datasets: Neuropixels, ECoG, calcium imaging, intracortical BCI benchmarks | `dandi` CLI, DANDI API, streaming |
| [PhysioNet](https://physionet.org) | clinical EEG, sleep, EMG, ECG and physiology | web, `wget`, `wfdb` |
| [TUH EEG Corpus](https://isip.piconepress.com/projects/nedc/html/tuh_eeg/) | largest public clinical EEG corpus and subsets (seizures TUSZ, abnormal TUAB, events TUEV, artifacts TUAR) | signed form, then download |
| [BNCI Horizon 2020](https://bnci-horizon-2020.eu/database/data-sets) | classic BCI datasets, including BCI Competition IV 2a and 2b | open download; most also in MOABB |
| [MOABB](https://moabb.neurotechx.com) | Python loaders and benchmarks for about 170 BCI datasets | `pip install moabb` |
| [IEEG.org](https://www.ieeg.org) | intracranial EEG, mostly epilepsy | free registration |
| [NSRR](https://sleepdata.org) | large polysomnography cohorts (SHHS, MESA and others) | data access request; site did not respond when checked |
| [EBRAINS](https://www.ebrains.eu) | European datasets, atlases, models | registration for some data |
| [CRCNS](https://crcns.org) | systems neuroscience recordings | free account |
| [Allen Brain Map](https://portal.brain-map.org) | Neuropixels and imaging (Brain Observatory), atlases including the Common Coordinate Framework | AllenSDK, AWS open data |
| [International Brain Laboratory](https://docs.internationalbrainlab.org) | standardised mouse decision-making recordings across labs | ONE API (`ONE-api`) |
| [Neural Latents Benchmark](https://neurallatents.github.io) | intracortical datasets and leaderboard for latent-dynamics models | data on DANDI |
| [FALCON](https://github.com/snel-repo/falcon-challenge) | cross-session intracortical decoder benchmark | data on DANDI |
| [Human Connectome Project](https://www.humanconnectome.org) | MRI, fMRI, MEG | registration, data use terms |
| [Cam-CAN](https://camcan-archive.mrc-cbu.cam.ac.uk) | lifespan MEG and MRI, about 650 adults | application |
| [MPI-Leipzig LEMON](https://fcon_1000.projects.nitrc.org/indi/retro/MPI_LEMON.html) | resting EEG plus MRI, young and older adults | open |
| Healthy Brain Network (Child Mind Institute) | developmental EEG, MRI, phenotype | registration and terms |
| [Ninapro](https://ninapro.hevs.ch) | surface EMG for hand movements and prosthetics | registration |
| [ERP CORE](https://erpinfo.org/erp-core) | seven standard ERP components from 40 people, with scripts | open; also MOABB `ErpCore2021_*` and `mne.datasets.erp_core` |
| [Kaggle](https://www.kaggle.com/competitions/hms-harmful-brain-activity-classification) | competition EEG (for example HMS harmful brain activity) | competition rules apply |
| General repositories | [Zenodo](https://zenodo.org), [OSF](https://osf.io), [G-Node GIN](https://gin.g-node.org), [brainlife.io](https://brainlife.io), [NeuroVault](https://neurovault.org), [NITRC](https://www.nitrc.org) | per deposit |

## By question

### Motor imagery and movement (EEG)

| Dataset | MOABB class | People | Notes |
|---|---|---|---|
| BCI Competition IV 2a | `BNCI2014_001` | 9 | 4 classes, 22 EEG + 3 EOG, two sessions on different days: the standard cross-session benchmark |
| BCI Competition IV 2b | `BNCI2014_004` | 9 | 2 classes, 3 bipolar channels, 5 sessions |
| PhysioNet EEG Motor Movement/Imagery | `PhysionetMI` | 109 | 64 channels at 160 Hz; executed and imagined runs mixed |
| OpenBMI (Lee 2019) | `Lee2019_MI` | 54 | 2 sessions; same people also did ERP and SSVEP (`Lee2019_ERP`, `Lee2019_SSVEP`) |
| Cho 2017 | `Cho2017` | 52 | 64 channels, left and right hand |
| High-Gamma Dataset | `Schirrmeister2017` | 14 | executed movements, 128 channels, common deep-learning benchmark |
| Stieger 2021 | `Stieger2021` | 62 | up to 11 sessions per person: learning across sessions |
| Dreyer 2023 | `Dreyer2023` | 87 | large single-session cohort |

### P300, ERPs and c-VEP

| Dataset | MOABB class | People | Notes |
|---|---|---|---|
| BNCI 2014-009 | `BNCI2014_009` | 10 | P300 speller, 3 sessions |
| Brain Invaders 2013a-2015b | `BI2013a` ... `BI2015b` | 24-64 | P300 game, several sessions |
| EPFL P300 | `EPFLP300` | 8 | includes patients |
| ERP CORE | `ErpCore2021_P3`, `_N170`, `_MMN`, `_N2pc`, `_N400`, `_ERN`, `_LRP` | 40 | clean reference ERPs with published analysis scripts |
| c-VEP | `Thielen2021`, `Thielen2015`, `CastillosCVEP100` | 12-30 | code-modulated VEP |

### SSVEP

| Dataset | MOABB class | People | Notes |
|---|---|---|---|
| Tsinghua benchmark | `Wang2016` | 34 | 40 targets: the standard SSVEP speller benchmark |
| BETA | `Liu2020BETA` | 70 | 40 targets, outside the lab |
| Nakanishi 2015 | `Nakanishi2015` | 9 | 12 targets |
| MAMEM 1-3 | `MAMEM1`-`MAMEM3` | 11 each | |
| Kalunga 2016 | `Kalunga2016` | 12 | |

### Seizures and clinical EEG

| Dataset | Where | Notes |
|---|---|---|
| CHB-MIT Scalp EEG | [PhysioNet](https://physionet.org/content/chbmit/) | 23 cases from 22 paediatric patients (one recorded twice), long recordings, montage changes between files |
| Siena Scalp EEG | [PhysioNet](https://physionet.org/content/siena-scalp-eeg/) | adult patients |
| TUH Seizure Corpus (TUSZ) | TUH | largest annotated seizure set; use its train/dev/eval split |
| TUH Abnormal (TUAB), Events (TUEV), Artifacts (TUAR) | TUH | normal/abnormal classification, event types, artefact labels |
| HMS harmful brain activity | Kaggle | expert-voted labels for seizure-like patterns |
| Epilepsy ECoG | `mne.datasets.epilepsy_ecog` | small iEEG example |

### Sleep

| Dataset | Where | Notes |
|---|---|---|
| Sleep-EDF Expanded | [PhysioNet](https://physionet.org/content/sleep-edfx/); `mne.datasets.sleep_physionet` | 2 EEG channels, R&K labels (map stages 3 and 4 to N3) |
| SHHS, MESA, MrOS and other cohorts | NSRR | thousands of polysomnograms, application required |

### Resting state, normative and cognition (EEG/MEG)

| Dataset | Where | Notes |
|---|---|---|
| LEMON | MPI Leipzig (link above) | resting EEG with MRI, two age groups |
| Healthy Brain Network | Child Mind Institute; EEG also on NEMAR | thousands of children |
| Cam-CAN | Cam-CAN archive | lifespan MEG |
| MNE teaching sets | `mne.datasets.sample`, `somato`, `spm_face`, `brainstorm`, `opm`, `visual_92_categories`, `kiloword`, `limo`, `ssvep`, `eegbci` | small, documented, ideal for testing pipelines |

### Intracranial (ECoG, sEEG) and intracortical

| Dataset | Where | Notes |
|---|---|---|
| BCI Competition IV dataset 4 | [BCI Competition IV](https://www.bbci.de/competition/iv/) | ECoG with finger flexion from a data glove |
| IEEG.org collections | IEEG.org | epilepsy iEEG, often MEF |
| OpenNeuro iEEG | OpenNeuro, filter modality iEEG | BIDS-formatted |
| Neural Latents Benchmark (MC_Maze, Area2_Bump, MC_RTT, DMFC_RSG) | DANDI | monkey intracortical, standard evaluation |
| FALCON | DANDI | human and monkey intracortical across sessions |

### Animal electrophysiology and imaging

| Dataset | Access | Notes |
|---|---|---|
| Allen Brain Observatory (Visual Coding Neuropixels, Visual Behavior) | AllenSDK | standardised, very large |
| IBL Brain-Wide Map | ONE API | one task, many labs and brain regions |
| DANDI collections | `dandi` | search by technique |
| CRCNS | crcns.org | hippocampus, cortex and many classics |

### fNIRS, EMG and multimodal

| Dataset | Where | Notes |
|---|---|---|
| fNIRS motor task | `mne.datasets.fnirs_motor` | finger tapping, small |
| OpenNeuro fNIRS | OpenNeuro, filter modality NIRS | BIDS NIRS |
| Shin 2017 EEG+fNIRS | MOABB `Shin2017A`, `Shin2017B` | simultaneous EEG and NIRS, 29 people |
| Ninapro | ninapro.hevs.ch | the standard hand-gesture sEMG benchmark |
| Hyser high-density sEMG | [PhysioNet](https://physionet.org/content/hd-semg/) | HD-EMG with toolbox |
| EyeLink example | `mne.datasets.eyelink` | eye tracking with EEG |

## Comparing with published numbers

- Use the dataset's own train and evaluation split where one exists
  (BCI Competition sessions, TUH splits, benchmark leaderboards).
- For BCI paradigms use MOABB's evaluations (within-session,
  cross-session, cross-subject) so the numbers match the MOABB
  benchmark papers.
- Report the dataset version or DOI, subjects used and excluded, and the
  evaluation scheme next to every number.
