# MNE-Python: preprocessing recipe and traps

Function names checked against MNE 1.12. MNE stores data in volts and time
in seconds. Most methods modify in place and also return the object:
work on `.copy()` when you need the original.

## Recipe (continuous EEG)

```python
import mne

raw = mne.io.read_raw("sub-01_task-x_eeg.vhdr", preload=True)
raw.set_channel_types({"VEOG": "eog", "HEOG": "eog", "ECG": "ecg"})
raw.set_montage("standard_1020", on_missing="warn")   # match the real cap
raw.compute_psd(fmax=100).plot()                       # look first

# 1. bad channels: mark, do not delete
raw.info["bads"] += ["T7"]                              # from inspection
# automated helpers: pyprep.NoisyChannels(raw).find_all_bads();
# mne.preprocessing.find_bad_channels_lof(raw) (local outlier factor)

# 2. filters on continuous data
raw.filter(l_freq=0.1, h_freq=40.0)                     # FIR, zero phase, firwin
raw.notch_filter([50, 100])                             # or 60/120; often unnecessary below 40 Hz

# 3. reference after bads are marked (bads are excluded from the average)
raw.set_eeg_reference("average", projection=True)      # applied when data are used

# 4. ICA on a 1 Hz high-passed copy, applied to the analysis data
raw_ica = raw.copy().filter(l_freq=1.0, h_freq=100.0)
ica = mne.preprocessing.ICA(n_components=0.99, method="picard",
                            fit_params=dict(ortho=False, extended=True), random_state=97)
ica.fit(raw_ica, reject_by_annotation=True)
eog_idx, _ = ica.find_bads_eog(raw_ica)                 # needs EOG channels or ch_name=
ecg_idx, _ = ica.find_bads_ecg(raw_ica, method="correlation")
ica.exclude = sorted(set(eog_idx + ecg_idx))
ica.plot_components(); ica.plot_sources(raw_ica)       # confirm by eye
ica.apply(raw)

# 5. interpolate bad channels
raw.interpolate_bads(reset_bads=True)

# 6. epochs
events, event_id = mne.events_from_annotations(raw)    # or mne.find_events(raw)
epochs = mne.Epochs(raw, events, event_id, tmin=-0.2, tmax=0.8,
                    baseline=(None, 0), reject=dict(eeg=150e-6),
                    reject_by_annotation=True, preload=True)
epochs.drop_log                                          # report per condition
```

## Classifying components with ICLabel

`mne_icalabel.label_components(raw, ica, method="iclabel")` returns labels
and probabilities. ICLabel was trained on EEGLAB-style data: fit ICA on
data filtered 1-100 Hz and referenced to the common average, using
extended Infomax (`method="infomax", fit_params=dict(extended=True)`) or
Picard with `ortho=False, extended=True`. Otherwise the probabilities are
unreliable.

## Automated rejection

- `autoreject.AutoReject()` on epochs: learns per-channel thresholds and
  interpolates or drops; fit inside a cross-validation fold if epochs feed
  a decoder.
- `mne.preprocessing.annotate_amplitude(raw, peak=..., flat=...)`,
  `annotate_muscle_zscore(raw, threshold=4)`, `annotate_break(raw)` add
  `BAD_` annotations that `reject_by_annotation=True` honours.
- `mne.preprocessing.compute_bridged_electrodes(raw)` finds gel bridges
  (high-density caps).

## MEG

- `raw.info["proc_history"]` shows whether MaxFilter already ran.
- `mne.preprocessing.find_bad_channels_maxwell(raw, ...)` then
  `mne.preprocessing.maxwell_filter(raw, calibration=..., cross_talk=...,
  st_duration=10)` (tSSS). After SSS the data rank is about 64-80: set
  ICA `n_components` below the rank.
- CTF: keep the same `raw.compensation_grade` for every run.

## Whole datasets

`mne-bids-pipeline` runs a configured, logged pipeline over a BIDS
dataset (`mne_bids_pipeline --config config.py`). Prefer it to
hand-written loops when there are many participants.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Filtering epochs instead of continuous data | edge artefacts, slow drifts not removed | filter `Raw`, then epoch |
| `filter()` on `Epochs` or short segments | filter longer than the data, warning ignored | read the warning; filter continuous data |
| Events from `find_events` used to index `raw.get_data()` | off by `raw.first_samp` samples after cropping | subtract `raw.first_samp` |
| Average reference with `projection=True` never applied | data still on the original reference when exported | `raw.apply_proj()` before export |
| ICA fitted on 0.1 Hz-filtered data | unstable components | fit on a 1 Hz copy, apply to the original |
| `n_components` above the data rank (after average reference, interpolation, SSS) | ICA fails or returns noise components | pass a variance fraction (`0.99`) or a number below the rank |
| `reject` thresholds in microvolts | everything or nothing rejected | thresholds are in volts (`150e-6`) |
| Baseline correction before decoding | shifts effects into the baseline window | see `neuro-bci-decoding-eval` |
| `resample` on raw data with events in a stim channel | events lost or shifted | resample epochs, or pass `events=` to `resample` and use the returned events |
| `preload=False` and in-place methods | error or silently loading | `preload=True` before filtering |

## Report

Version, reader, every filter (`raw.info` shows header and applied
filters; `mne.viz.plot_filter(mne.filter.create_filter(...))` documents
the response), bad channels and why, ICA method, number of components and
which were removed, rejection thresholds and trials kept per condition.
