# BCI frameworks: which one, and how to start

Not executed while writing this file; written from each project's
documentation. Check versions and install instructions on the project
site. Pick a framework only if it saves work: a short Python loop over
LSL or BrainFlow is often enough for a single-paradigm study.

## Comparison

| Framework | Language | Strength | Typical use |
|---|---|---|---|
| BCI2000 | C++, modules configured by parameter files | mature, clinical and ECoG research history, P300 speller and cursor tasks built in, `.dat` recording with states | clinical studies, ECoG, labs that need a validated stack |
| OpenViBE | C++ with a visual scenario designer | no-code pipelines of boxes, acquisition server for many amplifiers, LSL in and out | teaching, quick prototypes, neurofeedback |
| Timeflux | Python, YAML-defined graphs | modern, readable pipelines, LSL and web interfaces | Python labs building custom online systems |
| BciPy | Python | complete RSVP and matrix speller toolkit with signal models and simulation | spelling BCIs |
| MEDUSA | Python | apps for P300, c-VEP and neurofeedback with a GUI platform | c-VEP and ERP spellers |
| NeuroPype | Python (commercial, free academic tier) | visual pipeline editor, many signal-processing nodes | applied and industry projects |
| MNE-LSL | Python | real-time streams inside MNE, replay of recordings | MNE users moving online (see `lsl.md`) |
| BRAND | Python and C, Redis-based | low-latency intracortical BCI graphs used in clinical trials | intracortical research groups |
| FieldTrip buffer | MATLAB, C | real-time access from MATLAB | MATLAB labs |

## BCI2000 in practice

- Modules: **Source** (amplifier), **SignalProcessing** (filters,
  classifiers), **Application** (task), started together by the
  **Operator** with a batch file.
- Configuration lives in `.prm` parameter files: save one per experiment
  and keep it with the data.
- Recordings are `.dat` with "states" (StimulusCode, StimulusBegin,
  Feedback) stored per sample. Read them with MATLAB `load_bcidat`, the
  `BCI2000Tools` Python package, or `mne.io.read_raw_bci2k`.
- The P300 speller's classifier weights come from the offline P300
  Classifier tool; record calibration first.

## OpenViBE in practice

- **Acquisition Server** connects to the amplifier (or an LSL stream)
  and serves data to the **Designer**.
- Scenarios (`.xml`) chain boxes: acquisition, filters, epoching,
  feature extraction, classifier trainer and processor, visualisation,
  LSL export.
- Standard workflow per paradigm: acquisition scenario, training
  scenario (offline), online scenario using the trained classifier
  file. Keep the three scenarios and the classifier configuration with
  the data.
- Recordings are `.ov` or exported to GDF/CSV.

## Choosing

1. Clinical or ECoG study needing an established, validated system:
   BCI2000.
2. No-code prototype, teaching or neurofeedback: OpenViBE.
3. Python lab with custom paradigms: plain LSL or BrainFlow plus MNE-LSL,
   or Timeflux for a structured graph.
4. Speller BCI: BciPy (RSVP and matrix) or MEDUSA (c-VEP, P300).
5. Intracortical with sub-10 ms requirements: BRAND or a custom C/C++
   loop.

## Whatever the framework

- Measure end-to-end latency and jitter (`neuro-stimulus-timing-audit`).
- Use the same features, window and causal filters offline and online.
- Log every decoder output with its timestamp and the input window it
  used, so online sessions can be replayed offline.
- Record the raw stream alongside the framework's own recording.
