# FieldTrip: preprocessing recipe and traps

Written for recent FieldTrip releases. Not executed while writing this
file: check options with `help ft_<name>`. FieldTrip functions take a
`cfg` structure plus data and return data; every output keeps its
`cfg` history in `data.cfg`.

Data layout after `ft_preprocessing`: `data.trial` is a cell array of
channels x samples matrices, `data.time` a matching cell of time vectors
in seconds, `data.label` the channel names. Units follow the file (often
microvolts; check `hdr.chanunit`).

## Setup

```matlab
addpath('/path/to/fieldtrip');
ft_defaults;             % adds what is needed; never addpath(genpath(...)) on FieldTrip
```

## Recipe

```matlab
% 1. read continuous data and filter it whole
cfg = [];
cfg.dataset    = 'sub-01.vhdr';
cfg.hpfilter   = 'yes'; cfg.hpfreq = 0.1; cfg.hpfilttype = 'firws';
cfg.lpfilter   = 'yes'; cfg.lpfreq = 40;  cfg.lpfilttype = 'firws';
cfg.dftfilter  = 'yes'; cfg.dftfreq = [50 100 150];      % line noise; 60/120/180 in the Americas
cfg.reref      = 'yes'; cfg.refchannel = 'all'; cfg.refmethod = 'avg';
data_cont = ft_preprocessing(cfg);

% 2. define trials from events, then cut the filtered data
cfg = [];
cfg.dataset             = 'sub-01.vhdr';
cfg.trialdef.eventtype  = 'Stimulus';
cfg.trialdef.eventvalue = {'S  1', 'S  2'};
cfg.trialdef.prestim    = 0.2;
cfg.trialdef.poststim   = 0.8;
cfg = ft_definetrial(cfg);
data = ft_redefinetrial(struct('trl', cfg.trl), data_cont);

% 3. ICA on a 1 Hz high-passed copy, then remove components from the data
cfg = []; cfg.hpfilter = 'yes'; cfg.hpfreq = 1; cfg.hpfilttype = 'firws';
data_hp = ft_preprocessing(cfg, data);
cfg = []; cfg.method = 'runica';
cfg.numcomponent = rank(cat(2, data_hp.trial{:}));         % data rank drops after average reference
comp = ft_componentanalysis(cfg, data_hp);
cfg = []; cfg.layout = 'easycapM1.mat'; cfg.viewmode = 'component';
ft_databrowser(cfg, comp);                                      % inspect
cfg = []; cfg.unmixing = comp.unmixing; cfg.topolabel = comp.topolabel;
compfull = ft_componentanalysis(cfg, data);                      % same unmixing on the original data
cfg = []; cfg.component = [1 4];                                % chosen by inspection
data_clean = ft_rejectcomponent(cfg, compfull, data);

% 4. artefact rejection and channel repair
cfg = []; cfg.method = 'summary';
data_clean = ft_rejectvisual(cfg, data_clean);
cfg = []; cfg.method = 'triangulation'; cfg.layout = 'easycapM1.mat';
neighbours = ft_prepare_neighbours(cfg);
cfg = []; cfg.badchannel = {'T7'}; cfg.method = 'spline'; cfg.neighbours = neighbours;
cfg.elec = ft_read_sens('standard_1020.elc');
data_clean = ft_channelrepair(cfg, data_clean);

% 5. averages and baseline
cfg = []; cfg.trials = find(data_clean.trialinfo == 1);
erp1 = ft_timelockanalysis(cfg, data_clean);
cfg = []; cfg.baseline = [-0.2 0];
erp1 = ft_timelockbaseline(cfg, erp1);
```

## Downstream functions

| Task | Function |
|---|---|
| Time-frequency | `ft_freqanalysis` (`cfg.method = 'mtmconvol'`, `'wavelet'`, `'mtmfft'`; set `cfg.toi`, `cfg.foi`, `cfg.t_ftimwin`) then `ft_freqbaseline` |
| Cluster statistics | `ft_timelockstatistics` / `ft_freqstatistics` with `cfg.method = 'montecarlo'`, `cfg.correctm = 'cluster'`, `cfg.statistic = 'ft_statfun_depsamplesT'` (or `indepsamplesT`), neighbours from `ft_prepare_neighbours` |
| Source analysis | `ft_prepare_headmodel`, `ft_prepare_sourcemodel`, `ft_prepare_leadfield`, `ft_sourceanalysis` (`'lcmv'`, `'dics'`, `'mne'`, `'eloreta'`) |
| Connectivity | `ft_connectivityanalysis` (`'coh'`, `'wpli_debiased'`, `'granger'`) |
| Viewing | `ft_databrowser`, `ft_multiplotER`, `ft_topoplotER`, `ft_singleplotTFR` |
| Real time | FieldTrip buffer and `ft_realtime_*` examples |

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Filtering in `ft_preprocessing` after trials are defined | each trial filtered separately: edge artefacts and poor high-pass | filter continuous data first, or set `cfg.padding` well beyond the trial length |
| Default filter types left unset | IIR filters in some functions, FIR in others | set `cfg.hpfilttype`/`lpfilttype` explicitly and report them |
| `addpath(genpath(fieldtrip))` | function shadowing, external toolboxes on the path | `ft_defaults` only |
| `cfg.numcomponent` above the data rank | ICA fails or returns noise | compute the rank after re-referencing |
| Unmixing estimated on the 1 Hz copy but components removed from that copy | analysis data stay high-passed at 1 Hz | apply `comp.unmixing` to the original data as above |
| Neighbours from a layout that does not match the cap | wrong cluster statistics and repairs | build neighbours from the real electrode positions and plot them (`ft_neighbourplot`) |
| Statistics on one subject's trials, reported as a group effect | first-level only | between-subject statistics on subject averages |

## Report

FieldTrip version (`ft_version`), filter types and settings, line-noise
method, reference, trial definition, ICA method and components removed,
rejected trials and channels, repair method, and the statistics
configuration including neighbour definition, alpha and number of
randomisations.
