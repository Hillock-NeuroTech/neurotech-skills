# EEGLAB: preprocessing recipe and traps

Written for EEGLAB 2024-2025 with its default plugins (firfilt,
clean_rawdata, ICLabel, dipfit). Not executed while writing this file:
check function options with `help pop_<name>` in your installed version.

EEGLAB stores data in microvolts as `EEG.data` (channels x samples, or
channels x samples x trials after epoching). Event latencies are in
samples; `pop_epoch` takes seconds; `pop_rmbase` takes milliseconds.

## Recipe (script)

```matlab
eeglab nogui;                                         % puts plugins on the path

EEG = pop_loadset('filename', 'sub-01.set', 'filepath', datadir);
% other formats: pop_loadbv (BrainVision, bva-io plugin), pop_biosig (EDF/BDF/GDF),
% pop_mffimport (EGI), pop_loadcnt (Neuroscan)

EEG = pop_chanedit(EEG, 'lookup', 'standard_1005.elc'); % file shipped with dipfit; or the cap's own file
EEG = pop_select(EEG, 'rmchannel', {'HEOG'});           % only channels you will not use

% 1. filters on continuous data (firfilt: windowed-sinc FIR, zero phase)
EEG = pop_eegfiltnew(EEG, 'locutoff', 0.1);            % passband edge, not -6 dB point
EEG = pop_eegfiltnew(EEG, 'hicutoff', 40);

% 2. bad channels and bursts (clean_rawdata); keep a copy of the full montage
origChanlocs = EEG.chanlocs;
EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion', 5, 'ChannelCriterion', 0.8, ...
      'LineNoiseCriterion', 4, 'Highpass', 'off', ...
      'BurstCriterion', 20, 'WindowCriterion', 0.25, ...
      'BurstRejection', 'on', 'Distance', 'Euclidian');

% 3. average reference
EEG = pop_reref(EEG, []);

% 4. ICA: fit on a 1 Hz high-passed copy, copy weights back
EEGica = pop_eegfiltnew(EEG, 'locutoff', 1);
rk = rank(double(EEGica.data(:, :)));                   % rank drops after average reference
EEGica = pop_runica(EEGica, 'icatype', 'runica', 'extended', 1, 'pca', rk);
EEG.icaweights = EEGica.icaweights;  EEG.icasphere = EEGica.icasphere;
EEG.icachansind = EEGica.icachansind; EEG.icawinv = [];
EEG = eeg_checkset(EEG, 'ica');

% 5. classify and remove components
EEG = pop_iclabel(EEG, 'default');
EEG = pop_icflag(EEG, [NaN NaN; 0.9 1; 0.9 1; NaN NaN; NaN NaN; NaN NaN; NaN NaN]);
%      rows: Brain, Muscle, Eye, Heart, Line Noise, Channel Noise, Other
EEG = pop_subcomp(EEG, find(EEG.reject.gcompreject), 0);

% 6. interpolate removed channels back
EEG = pop_interp(EEG, origChanlocs, 'spherical');

% 7. epochs and baseline
EEG = pop_epoch(EEG, {'S  1', 'S  2'}, [-0.2 0.8]);    % seconds
EEG = pop_rmbase(EEG, [-200 0]);                        % milliseconds
EEG = pop_saveset(EEG, 'filename', 'sub-01_clean.set', 'filepath', outdir);
```

The GUI writes every action to `EEG.history`; `eegh` prints the session's
commands, which is the quickest way to turn a GUI session into a script.

## Plugins worth knowing

| Plugin | Use |
|---|---|
| clean_rawdata (ASR) | bad channels, burst correction or rejection |
| ICLabel | component classification |
| AMICA | higher-quality ICA, slower |
| PREP | standardised early pipeline (robust reference, bad channels) |
| CleanLine / Zapline-plus | line-noise removal without a notch |
| ERPLAB | ERP bins, measurement, ERP-specific filters |
| LIMO | hierarchical linear models |
| SIFT | source information flow (connectivity) |
| bids-matlab-tools | import and export BIDS |
| dipfit | dipole fitting, electrode coordinates |

## Traps

| Trap | Effect | Fix |
|---|---|---|
| `pop_epoch` limits in milliseconds, or `pop_rmbase` in seconds | empty or wrong windows | `pop_epoch` seconds, `pop_rmbase` milliseconds |
| ICA without `'pca'` after average reference or interpolation | rank-deficient decomposition, ghost components | set `'pca'` to the data rank, or interpolate after ICA |
| ICA on 0.1 Hz-filtered data | poor decomposition | fit on a 1 Hz copy, transfer weights |
| `clean_rawdata` with `'Highpass'` on twice | data filtered again | set `'Highpass', 'off'` if already filtered |
| Burst rejection removes data unevenly across conditions | biased trial counts | report trials per condition after epoching |
| Channels removed by clean_rawdata never interpolated | different channel sets across subjects | `pop_interp` with the original chanlocs |
| `pop_eegfiltnew` cutoffs read as -6 dB points | filter cuts lower or higher than expected | arguments are passband edges; the -6 dB cutoff is half a transition band away, printed in the command window |
| Event types with spaces (`'S  1'`) | no epochs found | copy the exact strings from `{EEG.event.type}` |
| `EEG.data` assumed in volts when exporting to Python | factor 1e6 errors | EEGLAB is microvolts; MNE converts on read |

## Report

EEGLAB and plugin versions, filter settings (as printed: order,
transition band, -6 dB cutoff), clean_rawdata parameters, channels and
time removed, ICA algorithm and rank, ICLabel thresholds and components
removed, interpolation method, epoch window, baseline and trials per
condition.
