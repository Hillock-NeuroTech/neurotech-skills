# Neuropixels: acquisition, preprocessing and sync

SpikeInterface names checked against 0.105. Hardware facts from the
Neuropixels and SpikeGLX documentation: confirm against the probe and
software versions you use.

## Probe basics

| | Neuropixels 1.0 | Neuropixels 2.0 |
|---|---|---|
| Recording channels | 384, selected from 960 sites | 384, from 1280 sites per shank (single- and four-shank versions) |
| Bands | separate AP (30 kHz) and LFP (2.5 kHz) streams | one wideband stream at 30 kHz |
| Gain | selectable; AP 500 and LFP 250 are common | fixed |
| Site selection | IMRO table in the `.meta` file | IMRO table |

The channel map and gains come from the recording's `.meta` (SpikeGLX)
or settings file (Open Ephys). Never reuse a probe file from another
recording without checking the IMRO table.

## Acquisition software

| Software | Output | Notes |
|---|---|---|
| SpikeGLX | `*.imec0.ap.bin`, `*.imec0.lf.bin` with `.meta`; NI-DAQ `*.nidq.bin` | `run_g0_t0` naming: gate and trigger indices. Channel 385 of each imec stream is the sync (SY0) channel |
| Open Ephys GUI (Neuropix-PXI plugin) | binary format: `structure.oebin`, one `continuous.dat` per stream | several record nodes and experiments may sit in one folder; pick them explicitly |

SpikeGLX companion tools: **CatGT** (joins trigger files, applies global
demux CAR and filters, extracts sync and event edges) and **TPrime**
(maps event times from one stream's clock onto another's using the shared
sync pulses).

## Reading

```python
import spikeinterface.full as si

si.get_neo_streams("spikeglx", folder)                    # list streams first
rec = si.read_spikeglx(folder, stream_name="imec0.ap")    # probe and gains from .meta
rec_oe = si.read_openephys(folder, stream_name=...)       # Open Ephys binary
```

`probeinterface.read_spikeglx(meta_file)` returns the probe on its own.

## Preprocessing for sorting (IBL / SpikeInterface practice)

```python
rec = si.highpass_filter(rec, freq_min=300.)
bad_ids, labels = si.detect_bad_channels(rec)              # Neuropixels-tuned defaults
print(dict(zip(*np.unique(labels, return_counts=True))))   # check before removing anything
rec = rec.remove_channels(bad_ids)                         # or si.interpolate_bad_channels
rec = si.phase_shift(rec)                                  # NP1.0 ADCs sample channels at different times
rec = si.common_reference(rec, operator="median", reference="global")
# alternative to CAR on long probes: si.highpass_spatial_filter (IBL "destriping")
rec = rec.save(folder="preprocessed", n_jobs=8, chunk_duration="1s")
```

Order matters: phase shift before any common reference, otherwise the
reference mixes samples taken at different moments.

`detect_bad_channels` is tuned for Neuropixels (dead, noisy and
out-of-brain channels). On other probes or synthetic data it can flag
most channels: on a clean 32-channel simulated recording it flagged 31
of 32. Always print the label counts before removing anything.

## Drift

Kilosort 4 corrects drift internally (`nblocks`). Without Kilosort:
`si.correct_motion(rec, preset="dredge")` (presets: `dredge`,
`dredge_fast`, `medicine`, `nonrigid_accurate`,
`nonrigid_fast_and_accurate`, `rigid_fast`, `kilosort_like`). Inspect
with `si.plot_motion` or the drift raster before and after.

## Synchronising streams

1. Record a shared sync signal on every device (SpikeGLX: imec SY0 and
   an NI-DAQ channel; Open Ephys: sync line per stream; behaviour rigs:
   a TTL into each).
2. Extract the edge times in each stream's own clock (CatGT, or read the
   sync channel and threshold it).
3. Fit a linear map between clocks (TPrime, or a regression on matched
   edges; see `neuro-sync-forensics` and its `align_clocks.py`).
4. Check the residuals: they should be well below a millisecond across
   the whole session.

## Localising the probe

Histology track tracing (brainreg / BrainGlobe, HERBS, SHARP-Track) to an
atlas (Allen CCF), then alignment of electrophysiological features
(firing-rate depth profile, LFP power) to the track in the IBL ephys
alignment GUI. Report the atlas, version and alignment method with any
region-level claim.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| CAR before phase shift on NP1.0 | residual noise, worse sorting | `phase_shift` first |
| Removing every channel `detect_bad_channels` flags without looking | most of the probe discarded | print label counts; inspect |
| Sorting the LFP stream or a downsampled copy | spikes missed | sort the AP (or NP2.0 wideband) stream at 30 kHz |
| Probe file from a different IMRO selection | wrong geometry | read the probe from this recording's metadata |
| Assuming streams share a clock | event times drift by milliseconds over an hour | align with sync pulses |
| Saving preprocessed data in float32 at full length | disk fills (about 2x the int16 size) | save as int16 with gain and offset, or keep the lazy chain and let the sorter write its own file |
