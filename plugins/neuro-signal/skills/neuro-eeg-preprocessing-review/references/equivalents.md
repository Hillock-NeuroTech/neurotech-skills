# Same step, four toolboxes

Use this when moving a pipeline between toolboxes, reviewing someone
else's code, or reproducing a paper. Defaults differ, so the same words
in two methods sections can mean different filters.

## Conventions

| | MNE-Python | EEGLAB | FieldTrip | Brainstorm |
|---|---|---|---|---|
| Data units | volts | microvolts | as in file (check `chanunit`) | volts |
| Continuous data | `Raw`, `(n_channels, n_times)` | `EEG.data` channels x samples | one trial covering the recording | linked raw file |
| Epoched data | `Epochs`, `(n_epochs, n_channels, n_times)` | `EEG.data` channels x samples x trials | `data.trial{k}` channels x samples | imported trials in the database |
| Time units in function arguments | seconds | `pop_epoch` seconds, `pop_rmbase` milliseconds, event latencies in samples | seconds | seconds (GUI shows ms) |
| Electrode positions | `Montage` (head coordinates, metres) | `EEG.chanlocs` (polar and Cartesian) | `elec` structure | channel file |

## Steps

| Step | MNE-Python | EEGLAB | FieldTrip | Brainstorm |
|---|---|---|---|---|
| Load | `mne.io.read_raw` | `pop_loadset`, `pop_loadbv`, `pop_biosig` | `ft_preprocessing` with `cfg.dataset`; `ft_read_header/data/event` | Review raw file |
| Electrode positions | `raw.set_montage` | `pop_chanedit(..., 'lookup', ...)` | `ft_read_sens`, `cfg.elec` | Channel file > Add EEG positions |
| High-/low-pass | `raw.filter` (FIR firwin, zero phase, Hamming) | `pop_eegfiltnew` (FIR windowed sinc, zero phase, Hamming) | `cfg.hpfilter`/`lpfilter` with `*filttype` (`'firws'`, `'but'`, ...) | Band-pass filter process |
| Line noise | `raw.notch_filter` (FIR notch, or `method="spectrum_fit"` to fit and remove sinusoids) | CleanLine, Zapline-plus, or `pop_eegfiltnew` notch | `cfg.dftfilter` (DFT filter), `cfg.bsfilter` | Notch filter process |
| Bad channels | `raw.info["bads"]`; pyprep; `find_bad_channels_lof` | `pop_clean_rawdata` (ChannelCriterion), PREP | `ft_rejectvisual`, `ft_badchannel` | mark bad in viewer; PSD |
| Re-reference | `raw.set_eeg_reference("average")` | `pop_reref(EEG, [])` | `cfg.reref = 'yes'`, `cfg.refmethod = 'avg'` | Re-reference process |
| ICA | `mne.preprocessing.ICA` (FastICA default; Picard, Infomax) | `pop_runica` (extended Infomax), AMICA | `ft_componentanalysis` (`'runica'`, `'fastica'`) | Artifacts > ICA |
| Component labelling | `mne_icalabel.label_components` | `pop_iclabel` | by inspection; ICLabel via EEGLAB | by inspection |
| Artefact subspace / bursts | none built in (asrpy third-party) | `clean_rawdata` ASR | none built in | none built in |
| Interpolate | `raw.interpolate_bads` (spherical spline) | `pop_interp(..., 'spherical')` | `ft_channelrepair` (`'spline'`, `'weighted'`) | Interpolate bad channels |
| Epoch | `mne.Epochs` | `pop_epoch` | `ft_definetrial` + `ft_redefinetrial` | Import in database |
| Baseline | `baseline=` in `Epochs` or `apply_baseline` | `pop_rmbase` | `ft_timelockbaseline`, `cfg.demean` + `cfg.baselinewindow` | at import or Pre-process > Remove DC offset |
| Reject epochs | `reject=`, autoreject | `pop_eegthresh`, `pop_jointprob` | `ft_rejectvisual`, `ft_artifact_zvalue` + `ft_rejectartifact` | bad trials in viewer |
| Average | `epochs.average()` | `pop_comperp`, ERPLAB `pop_averager` | `ft_timelockanalysis` | Average process |
| Cluster test | `mne.stats.spatio_temporal_cluster_test` | LIMO, FieldTrip via EEGLAB | `ft_timelockstatistics` (`'montecarlo'`, `'cluster'`) | Process2 > Test > permutation |

## Defaults that differ

- **Filter cutoff meaning.** MNE and EEGLAB's `pop_eegfiltnew` describe
  FIR filters by passband edges; the -6 dB point lies half a transition
  band away. Methods sections that quote "0.1 Hz high-pass" can mean
  different filters: report filter type, length or order, transition
  band and -6 dB cutoff.
- **FieldTrip filter types** depend on the option set; set `*filttype`
  explicitly when matching another toolbox.
- **ICA algorithm**: MNE defaults to FastICA, EEGLAB to extended Infomax.
  ICLabel expects extended Infomax-like decompositions of average-referenced
  1-100 Hz data.
- **Units**: moving data from EEGLAB to MNE or back is a factor of 1e6.
- **Interpolation**: spherical spline parameters (order, terms) differ
  slightly; small numerical differences are expected.
