---
name: neuro-data-sources
description: Find, choose and download public neural datasets and the archives that host them - OpenNeuro, NEMAR, DANDI, PhysioNet, TUH EEG, BNCI Horizon, MOABB, IEEG.org, NSRR, EBRAINS, CRCNS, Allen Institute, International Brain Laboratory, Neural Latents and FALCON benchmarks, Ninapro, Human Connectome Project, Cam-CAN, LEMON and MNE's built-in datasets. Use whenever the user needs data for a paradigm or question (motor imagery, P300, SSVEP, c-VEP, ERPs, seizures, sleep, clinical EEG, resting state, MEG, iEEG/ECoG, intracortical decoding, spikes, fNIRS, EMG), wants a benchmark to compare against published numbers, asks where a dataset lives or how to download it, or needs test data before their own recordings exist.
---

# Finding neural data

Pick data that answers the question, that others have used (so results
can be compared), and that you are allowed to use. Then audit it before
modelling.

## 1. Define what the data must have

Before searching, write down: modality and channel count; paradigm or
labels needed; number of people (cross-subject claims need many);
sessions per person (cross-day claims need at least two); sampling rate
and band of interest; healthy or patient population; licence (can results
and derived data be published?).

## 2. Search in this order

1. **A benchmark the field already uses** for that question
   (`references/datasets.md`, "By question"). Results then compare with
   the literature.
2. **A programmatic loader** that fixes events and splits for you:
   MOABB for BCI paradigms (about 170 datasets, `moabb.datasets`),
   `mne.datasets` for teaching and testing, the Allen SDK and IBL's ONE
   API for animal electrophysiology, `dandi download` for NWB sets.
3. **An archive search**: OpenNeuro (filter by modality: EEG, MEG, iEEG,
   fNIRS), NEMAR for OpenNeuro EEG/MEG with compute, DANDI (search by
   species, technique, brain region), PhysioNet (clinical and physiology),
   EBRAINS, CRCNS, Zenodo, OSF, G-Node GIN.
4. **The paper**: the data availability statement of the study you want to
   replicate, then the authors.

## 3. Check access and licence

| Access | Examples | What it means |
|---|---|---|
| Open download | OpenNeuro (CC0 by default), most of DANDI, many PhysioNet sets, BNCI Horizon, MOABB sources | Download now; cite as the dataset asks |
| Free registration or signed form | TUH EEG corpora, IEEG.org, Ninapro, Cam-CAN | Allow days to weeks; read the terms |
| Data use agreement or application | NSRR, UK Biobank, ABCD, Human Connectome Project restricted data | Institutional sign-off often needed; plan months ahead |
| Credentialed PhysioNet | some clinical sets | Requires a PhysioNet account plus human-subjects training |

Never redistribute restricted data (including in a GitHub repo or a
benchmark), and never try to re-identify participants. Derived features
may also be covered by the agreement: check before publishing them.

## 4. Download sensibly

- Large archives: download one subject first, load it, then fetch the
  rest. OpenNeuro: `openneuro-py` or DataLad; DANDI: `dandi download` or
  stream with `remfile`/`fsspec` instead of downloading; PhysioNet:
  `wget -r` per the dataset page or the `wfdb` package.
- Record dataset version or DOI and the download date with the results.
- Set an explicit data directory (`MNE_DATA`, `MNE_DATASETS_*_PATH`,
  MOABB's config) so tools do not fill the home folder.

## 5. Before any modelling

Run the `neuro-dataset-gotchas` audit (rates, channels, duplicate people,
label mapping, defined train and evaluation splits) and load files with
`neuro-file-formats`.

## Output

A short data plan: dataset name and version or DOI, why it fits, access
route and licence, subjects and sessions used, known issues, and the
published results to compare with.
