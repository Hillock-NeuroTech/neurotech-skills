---
name: neuro-file-formats
description: Open, inspect and convert neural recording files from any acquisition system - EEG (BrainVision .vhdr, BioSemi .bdf, EDF/EDF+, GDF, EGI .mff, ANT/Neuroscan .cnt, EEGLAB .set, OpenBCI, Muse/Emotiv CSV), MEG (.fif, CTF .ds, OPM), clinical and intracranial (Nihon Kohden, Micromed .trc, Persyst, Natus/Nicolet, MEF3, Blackrock .nev/.nsx, Neuralynx .ncs, Plexon .plx/.pl2, Intan .rhd/.rhs, Open Ephys, SpikeGLX/Neuropixels .bin+.meta, TDT, SpikeGadgets), fNIRS (SNIRF, NIRx), streams (XDF/LSL), BCI2000 .dat and MATLAB .mat. Use whenever the user loads, reads, opens, converts or exports a recording, gets a reader error, sees wrong units, wrong sampling rate, missing events or channels, or asks what format or library to use.
---

# Neural file formats: open, verify, convert

Most "the analysis is wrong" problems start at loading: values in the
wrong unit, a sidecar file missing, events read from the wrong channel,
mixed sampling rates silently resampled. Load with the right reader, then
verify before any analysis.

## 1. Pick the reader

Identify the system from the extension and the files next to it, then use
`references/formats.md` (system by system: reader, required companion
files, units, known traps). Defaults:

| Data | First choice | Fallback |
|---|---|---|
| Scalp EEG, MEG, clinical EEG, fNIRS | MNE-Python: `mne.io.read_raw(path)` picks the reader from the extension | the specific `mne.io.read_raw_*`, then Neo, then the vendor converter |
| Intracranial and animal electrophysiology (spikes, LFP) | SpikeInterface `read_*` extractors or Neo `neo.io.*IO` / `neo.rawio.*RawIO` | MNE (`read_raw_nsx`, `read_raw_neuralynx` read continuous data only) |
| XDF from LabRecorder / LSL | `pyxdf.load_xdf(path, synchronize_clocks=True, dejitter_timestamps=True)` | build `mne.io.RawArray` per stream after alignment |
| BIDS dataset | `mne_bids.read_raw_bids(BIDSPath(...))` | read the underlying file directly |
| NWB file | `pynwb.NWBHDF5IO(path, "r")`; for conversion use NeuroConv | `neo.io.NWBIO` |
| MATLAB `.mat` | `scipy.io.loadmat` (v7 and older) | v7.3 files are HDF5: `h5py` or `pymatreader` |
| MATLAB toolboxes | EEGLAB `pop_loadset`, plugins (bva-io, BIOSIG, MFF), FieldTrip `ft_read_header` / `ft_read_data` / `ft_read_event` | Brainstorm "Review raw file" with the right file type |

Install only what the reader needs. Readers that need extra packages:
`read_raw_ant` (antio), `read_raw_mef` (pymef), `read_raw_curry`
(curryreader, MNE 1.11+), `read_raw_neuralynx` (neo), XDF (pyxdf), BIDS
(mne-bids), exports (pybv, eeglabio, edfio).

## 2. Verify before analysing

Run `scripts/inspect_recording.py <file>` (MNE-readable formats), or check
by hand:

1. **Sampling rate** matches the acquisition settings and the
   documentation. EDF/BDF with channels at different rates are upsampled
   to the highest rate by MNE: check `raw.info["sfreq"]` against the file
   header.
2. **Channels**: count, names, types (EEG, EOG, ECG, EMG, stim, misc).
   Set types explicitly; readers guess EEG for unknown labels.
3. **Units**: MNE stores volts. Scalp EEG should sit at roughly tens of
   microvolts (median absolute value 1e-6 to 1e-4 V). Values near 1 to
   100 "volts" mean microvolts were read as volts; values near 1e-12
   mean the reverse. Fix with `raw.apply_function(lambda x: x * 1e-6)`
   on the affected picks, or the reader's `units` argument (EDF/BDF).
4. **Events**: number per code matches the protocol. Events may live on a
   stim channel (`mne.find_events`), in annotations
   (`mne.events_from_annotations`), or in a separate file. Event samples
   from `find_events` include `raw.first_samp`; subtract it before indexing
   `raw.get_data()` directly.
5. **Time**: duration, `meas_date`, discontinuities (EDF+D, clinical
   recordings paused and resumed, Neuralynx gaps). Check for
   `BAD_ACQ_SKIP` or `edge` annotations.
6. **Montage**: electrode positions attached (`raw.get_montage()`), or set
   one with `raw.set_montage(...)` matching the cap actually used.
7. **Visual check**: plot ten seconds and the PSD. A line-noise peak at 50
   or 60 Hz confirms the time axis; its frequency also tells you the
   country of recording.
8. **Cross-check one channel** against the vendor viewer (or EDFbrowser)
   at one time point when anything looks off.

## 3. Convert and export

- Analysis copy: save as FIF (`raw.save("x_raw.fif")`); files over 2 GB
  are split automatically into `x_raw-1.fif` and so on, keep them together.
- Exchange: `mne.export.export_raw(fname, raw, fmt="brainvision" | "edf" |
  "eeglab")`. EDF stores 16-bit integers with a per-channel physical
  range, so large offsets or wide ranges lose resolution or clip; check
  the exported range. Annotations require `meas_date` to match
  `annotations.orig_time`. An EDF round trip also loses channel types
  (EOG and ECG come back as EEG) and electrode positions, and a missing
  `meas_date` comes back as 1 January 1985: reset types and montage after
  reading, and do not trust that date.
- Sharing: convert to BIDS (`mne_bids.write_raw_bids`) or NWB
  (NeuroConv). Hand the conversion details to a BIDS or NWB skill if one
  is installed.
- Never overwrite the original. Record the reader, its version and every
  unit or channel-type change.

## Output

A short load report: file, reader and version, sampling rate, channels by
type, units check, events per code, duration and gaps, montage, and any
corrections applied.
