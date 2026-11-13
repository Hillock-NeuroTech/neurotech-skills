# Formats by system

Readers checked against MNE-Python 1.12 and Neo 0.14 (November 2026).
Check the reader's documentation for your installed version; support
changes between releases.

Columns: companion files that must stay next to the main file; the
Python reader; MATLAB route; traps.

## Scalp EEG, research systems

| System | Files | Python | MATLAB | Traps |
|---|---|---|---|---|
| Brain Products (Recorder, LiveAmp, actiCHamp) | `.vhdr` header, `.vmrk` markers, `.eeg` data | `mne.io.read_raw_brainvision(vhdr)`; Neo `BrainVisionIO` | EEGLAB bva-io `pop_loadbv`; FieldTrip `ft_read_data` | The `.vhdr` names the other two files inside it: renaming one file breaks loading, rename by editing the header too. Markers arrive as annotations such as `Stimulus/S  1` (note the spaces). Per-channel resolution in the header sets the scaling |
| BioSemi ActiveTwo | `.bdf` (24-bit) | `mne.io.read_raw_bdf` | EEGLAB BIOSIG `pop_biosig`; FieldTrip | No hardware reference: data are referenced to CMS/DRL, re-reference before use. Triggers on the `Status` channel carry extra bits in the upper byte; mask with `mne.find_events(raw, mask=0xFF)` or similar |
| EDF / EDF+ (many vendors) | `.edf` | `mne.io.read_raw_edf`; Neo `EDFIO` | EEGLAB BIOSIG; FieldTrip | 16-bit. Channels at different rates are upsampled to the highest rate. EDF+D files are discontinuous. Missing unit fields: pass `units=` |
| GDF (BCI Competition, g.tec, BioSig) | `.gdf` | `mne.io.read_raw_gdf` | BIOSIG `sload` | Event codes are numeric (for example 768 trial start, 769-772 cues in BCI IV 2a); map them from the dataset paper |
| EGI / Magstim | `.mff` folder | `mne.io.read_raw_egi` (handles `.mff`) | EEGLAB MFFMatlabIO plugin | Events on `DIN` channels; the `events_as_annotations` default is changing, set it explicitly |
| ANT Neuro eego | `.cnt`, `.evt` | `mne.io.read_raw_ant` (needs `antio`, MNE 1.9+) | FieldTrip | Same `.cnt` extension as Neuroscan: choose the reader by vendor, not extension |
| Compumedics Neuroscan | `.cnt` (also `.cdt` Curry) | `mne.io.read_raw_cnt`; Curry: `read_raw_curry` (needs `curryreader`) | EEGLAB `pop_loadcnt`; FieldTrip | 16- vs 32-bit `.cnt` cannot always be detected: if amplitudes look wrong, pass `data_format` |
| Neuroelectrics Enobio / Starstim | `.easy`, `.nedf` | `mne.io.read_raw_nedf` for `.nedf`; `.easy` is plain text | NIC export | `.easy` is plain text with a final marker column; confirm its unit in the NIC documentation (commonly nanovolts) before scaling |
| BCI2000 | `.dat` | `mne.io.read_raw_bci2k` (requires `preload=True`) | BCI2000 `load_bcidat` | States (StimulusCode, Feedback) become channels or annotations; check which |
| EEGLAB | `.set` (+ `.fdt` if data stored separately) | `mne.io.read_raw_eeglab`, `mne.read_epochs_eeglab`; ICA: `mne.preprocessing.read_ica_eeglab` | `pop_loadset` | EEGLAB stores microvolts; MNE converts. Epoched `.set` files need `read_epochs_eeglab` |
| OpenBCI | GUI `.txt`/`.csv`, SD-card `.TXT`, BrainFlow CSV | `numpy.loadtxt` / pandas then `mne.io.RawArray(data * 1e-6, info)` | import as ASCII | Values in microvolts. GUI files have a header block and an accelerometer column; Cyton+Daisy alternates samples between boards |
| Consumer (Muse, Emotiv, Neurosity) | vendor CSV, Mind Monitor CSV, EDF exports | pandas then `RawArray` | ASCII import | Timestamps can be irregular or duplicated: check the real rate from the timestamps, interpolate to a uniform grid if needed |

## MEG

| System | Files | Python | Traps |
|---|---|---|---|
| MEGIN / Elekta Neuromag | `.fif` | `mne.io.read_raw_fif` | Split files `-1.fif`, `-2.fif` must stay together. Run Maxwell filtering (`mne.preprocessing.maxwell_filter`) or check whether MaxFilter was already applied (`raw.info["proc_history"]`) |
| CTF | `.ds` folder | `mne.io.read_raw_ctf` | Third-order gradient compensation state: check `raw.compensation_grade` and keep it consistent across runs |
| KIT / Ricoh, 4D/BTi, Artemis123 | `.con`/`.sqd`; 4D folder | `read_raw_kit`, `read_raw_bti`, `read_raw_artemis123` | Marker coils and head-shape files needed for coregistration |
| OPM (UCL FIL format) | `.bin` + JSON sidecars | `mne.io.read_raw_fil` | Sensor positions and orientations come from the sidecars; vendor formats differ (FieldLine, QuSpin), check vendor tools |

## Clinical and intracranial EEG

| System | Files | Python | Traps |
|---|---|---|---|
| Nihon Kohden | `.EEG` with `.21E`, `.PNT`, `.LOG` | `mne.io.read_raw_nihon` | Keep the sidecar files beside the `.EEG`; electrode names and annotations come from them. Annotation text encoding is settable (`encoding=`, MNE 1.11+) |
| Micromed | `.TRC` | Neo `MicromedRawIO` | No MNE reader: load with Neo and build a `RawArray` |
| Persyst | `.lay` + `.dat` | `mne.io.read_raw_persyst` | Pass the `.lay` file |
| Nicolet (older format) | `.data` + `.head` | `mne.io.read_raw_nicolet` (pass the `.data` file) | Newer Natus `.e` files are not read by MNE: export to EDF from NeuroWorks |
| MEF3 (Mayo, IEEG.org) | `.mefd` folder | `mne.io.read_raw_mef` (needs `pymef`) | Sessions may be password-protected (`password=`) |
| Natus, Compumedics clinical | proprietary | export EDF from the vendor software | Exports may drop or rename channels and anonymise dates: compare channel count before and after |

## Intracranial microelectrodes and animal electrophysiology

| System | Files | Python | Traps |
|---|---|---|---|
| Blackrock (Cerebus, NeuroPort) | `.nev` (spikes, events), `.ns1`-`.ns6` (continuous at increasing rates; `.ns5`/`.ns6` are 30 kHz) | Neo `BlackrockIO`; SpikeInterface `read_blackrock`; MNE `read_raw_nsx` | MNE does not read NSx version 2.1. Pick the `.nsX` that holds the band you need. Pauses create segments |
| Ripple (Grapevine) | `.nev`, `.nsX`, `.nf3` | Neo `BlackrockIO` reads the shared NEV/NSx layout for many files; Ripple's own tools otherwise | Confirm with a known channel |
| Neuralynx (Cheetah) | one `.ncs` per channel, `.nev` events, `.ntt` tetrode spikes, `.nvt` video | Neo `NeuralynxIO(dirname=...)`; MNE `read_raw_neuralynx` (continuous `.ncs` only) | Recording gaps split data into segments; timestamps in microseconds. Channels at different rates in one folder cannot form one Raw: exclude some with `exclude_fname_patterns=` |
| Plexon | `.plx`, `.pl2` | Neo `PlexonIO`, `Plexon2IO` | `.pl2` reading depends on Plexon's library; on macOS and Linux check the Neo documentation for its requirements |
| Intan (RHD/RHS) | `.rhd`/`.rhs` (traditional) or one-file-per-signal folders | Neo `IntanIO`; SpikeInterface `read_intan` | Several file layouts exist; RHS stimulation channels need separate handling |
| Open Ephys | legacy `.continuous`/`.events`; binary `structure.oebin` + `.dat` | Neo `OpenEphysIO` / `OpenEphysBinaryIO`; SpikeInterface `read_openephys`; `open-ephys-python-tools` | Binary format stores sample numbers that may not start at zero; multiple record nodes and experiments in one folder |
| Neuropixels via SpikeGLX | `.ap.bin`/`.lf.bin` + `.meta` | SpikeInterface `read_spikeglx`; Neo `SpikeGLXIO` | Raw int16: gains and channel map come from `.meta` (IMRO table). Use the reader rather than `numpy.memmap` alone. Sync channel is the last channel |
| SpikeGadgets (Trodes) | `.rec` | Neo `SpikeGadgetsIO`; SpikeInterface `read_spikegadgets` | Hardware configuration is embedded in the file header |
| TDT (Synapse) | tank folder (`.tev`, `.tsq`, `.sev`) | Neo `TdtIO`; `tdt` Python package | Stores (streams) named by four-character codes; pick the right one |
| Axon (pCLAMP), HEKA, CED Spike2, WinWCP | `.abf`, `.dat`, `.smr`/`.smrx`, `.wcp` | Neo `AxonIO`, `CedIO`/`Spike2IO`, `WinWcpIO`; `pyabf` for `.abf` | Intracellular units (mV, pA) and sweeps; HEKA needs a dedicated reader |
| MEAs (MCS, 3Brain, MaxWell) | `.raw`/`.h5`, `.brw`, `.h5` | Neo `RawMCSIO`, `BiocamIO`, `MaxwellIO`; SpikeInterface `read_maxwell`, `read_biocam` | MaxWell files may need the vendor decompression plugin (HDF5 compression filter) |
| Phy / Kilosort output | `.npy`, `.tsv` folder | SpikeInterface `read_phy`, `read_kilosort`; Neo `PhyIO` | Use `cluster_group.tsv` or `cluster_KSLabel.tsv` for curation labels |

## fNIRS and physiology

| System | Files | Python | Traps |
|---|---|---|---|
| SNIRF (standard) | `.snirf` | `mne.io.read_raw_snirf` | Check optode positions and source-detector distances after loading |
| NIRx | folder (`.hdr`, `.wl1`, `.wl2`, ...) | `mne.io.read_raw_nirx` | Pass the folder; short channels need identifying |
| Hitachi, BOXY | `.csv`, `.txt` | `read_raw_hitachi`, `read_raw_boxy` | |
| Eye tracking (EyeLink) | `.asc` (convert `.edf` with `edf2asc`) | `mne.io.read_raw_eyelink` | EyeLink `.edf` is not EDF; convert first |
| WFDB (PhysioNet) | `.dat` + `.hea` | `wfdb.rdrecord` | Gains and baselines in the `.hea` header |

## Streams and generic containers

| Format | Python | Traps |
|---|---|---|
| XDF (LabRecorder) | `pyxdf.load_xdf(..., synchronize_clocks=True, dejitter_timestamps=True)` | One recording holds several streams with their own clocks and rates; markers are a separate irregular stream. Align, then resample to a common grid if needed |
| HDF5 vendor files | `h5py` | Inspect the tree (`h5py.File(path).visit(print)`) before assuming layout |
| MATLAB v7.3 | `h5py`, `pymatreader.read_mat` | `scipy.io.loadmat` raises on v7.3; arrays come back transposed in h5py |
| NumPy / CSV | `numpy`, `pandas` | Units and sampling rate are not stored: get them from the source and write them into `mne.create_info` |
| BIDS | `mne_bids.read_raw_bids` | The sidecar JSON and `channels.tsv` override some header values; `events.tsv` holds the events |
| NWB | `pynwb`, `neo.io.NWBIO`, SpikeInterface `read_nwb` | Data may be lazily loaded from remote (DANDI) storage; units are in the `conversion` attribute |
