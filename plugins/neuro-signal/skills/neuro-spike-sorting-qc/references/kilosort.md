# Kilosort 4: settings, outputs and traps

Parameter names and defaults read from Kilosort 4.1.7's
`kilosort/parameters.py` (November 2026). Kilosort 4 is Python
(`pip install kilosort`), uses PyTorch, and runs far faster on an NVIDIA
GPU; CPU runs work but are slow. Kilosort 1-3 are MATLAB and need CUDA;
prefer 4 for new work.

## Running it

Three routes, same algorithm:

1. **GUI**: `python -m kilosort` (needs `pip install "kilosort[gui]"`).
   Load the binary, the probe file, check the data preview, run.
2. **Python**:
   ```python
   from kilosort import run_kilosort, io
   settings = {"n_chan_bin": 385, "fs": 30000}          # n_chan_bin counts ALL channels in the file
   probe = io.load_probe("NP1_probe.prb")                # .prb, .mat or .json probe file
   ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate, kept_spikes = run_kilosort(
       settings=settings, probe=probe, filename="rec.ap.bin", results_dir="ks4_out")
   ```
   The return values have changed between releases: check the docstring
   of your version.
3. **SpikeInterface**: `si.run_sorter("kilosort4", recording, folder=..., nblocks=1, Th_universal=9)`.
   The recording carries the probe; SpikeInterface writes the binary.
   Its extra options include `do_CAR`, `bad_channels`, `do_correction`
   and `skip_kilosort_preprocessing`.

## Settings that matter

| Setting | Default | When to change |
|---|---|---|
| `n_chan_bin` | required | total channels in the binary, including sync and unused channels (385 for a Neuropixels 1.0 AP file) |
| `fs` | 30000 | match the recording |
| `batch_size` | 60000 | 2 s at 30 kHz; smaller if GPU memory runs out |
| `nblocks` | 1 | drift correction: 0 turns it off, 1 is rigid, more blocks allow non-rigid correction along long probes. Too many blocks on short probes overfit |
| `Th_universal` | 9 | detection threshold for the universal templates; lower finds smaller units and more noise |
| `Th_learned` | 8 | threshold for the learned templates |
| `tmin`, `tmax` | 0, inf | sort a time window only, for tests or to skip a bad start |
| `artifact_threshold` | inf | batches with values above it are zeroed; set for recordings with large stimulation or movement artefacts |
| `highpass_cutoff` | 300 | Butterworth high-pass applied internally |
| `whitening_range` | 32 | channels used for local whitening |
| `dmin`, `dminx` | auto, 32 | vertical and horizontal spacing of template centres; set for unusual probe geometries |
| `nearest_chans` | 10 | fewer for low-density probes |
| `duplicate_spike_ms` | 0.25 | spikes from one cluster closer than this are removed as duplicates |
| `acg_threshold`, `ccg_threshold` | 0.2, 0.25 | refractory-violation fractions used to label units good and to merge |
| `shift`, `scale` | none | for data that are not int16 in microvolt-like units |

Function-level options: `do_CAR=True` (common average reference),
`invert_sign` (for positive-going spikes, some MEA and intracellular
setups), `bad_channels` (list of indices to ignore), `data_dtype`,
`save_preprocessed_copy`.

## Outputs (Phy format, in the results folder)

| File | Holds |
|---|---|
| `spike_times.npy` | spike times in samples |
| `spike_clusters.npy`, `spike_templates.npy` | cluster and template per spike |
| `templates.npy`, `amplitudes.npy` | waveform templates, per-spike amplitude |
| `channel_map.npy`, `channel_positions.npy` | channels used and their positions |
| `pc_features.npy`, `pc_feature_ind.npy` | features used by Phy |
| `cluster_KSLabel.tsv` | Kilosort's own good/mua label (from refractory violations) |
| `cluster_group.tsv` | manual labels after curation in Phy |
| `spike_positions.npy` | estimated spike depth, for drift plots |
| `ops.npy` | all settings and the drift estimate (`kilosort.io.load_ops`) |
| `params.py` | points Phy at the binary file |
| `kilosort4.log` | full run log |

Load into SpikeInterface with `si.read_kilosort(folder)` or
`si.read_kilosort_as_analyzer(folder)`.

## Checks after every run

1. **Drift map** (spike depth against time, `spike_positions.npy` or
   `si.plot_drift_raster_map`): bands should be horizontal after
   correction. Sudden jumps mean the probe moved; consider sorting the
   parts separately.
2. **Unit count and depth distribution** make sense for the region.
3. **`KSLabel` is not curation.** It only reflects refractory violations;
   apply quality metrics and look at borderline units (`references/curation.md`).
4. Waveforms on all channels at once, or locked to line frequency, are
   noise.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| `n_chan_bin` set to the number of recording channels when the file has a sync channel | every sample misaligned, garbage output | count all channels in the file (`.meta` `nSavedChans`) |
| Wrong probe file (channel order, geometry, or 1.0 file for a 2.0 probe) | units smeared across sites, drift correction fails | build the probe from the recording metadata (`probeinterface.read_spikeglx`) |
| Sorting LFP-band or already high-passed data with different units | thresholds wrong | sort the AP band raw int16; set `shift`/`scale` otherwise |
| `nblocks` large on a short or low-density probe | spurious non-rigid drift | 1 (rigid) or 0 |
| Concatenating sessions without checking drift between them | units split at the boundary | check the drift map across the join; match units across sessions with UnitMatch instead |
| Out of GPU memory | crash | smaller `batch_size`, close other GPU jobs, or `clear_cache=True` |
| Reporting Kilosort `good` units as single units | contaminated units in results | apply quality metrics and report thresholds |
