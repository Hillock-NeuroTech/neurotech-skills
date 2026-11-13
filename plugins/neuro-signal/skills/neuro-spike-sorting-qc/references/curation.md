# Curation: metrics, automatic labels and manual review

Function names checked against SpikeInterface 0.105. Curation turns
sorter clusters into labelled units (single unit, multi-unit, noise) with
a rule others can apply again. Do it the same way for every session and
report the rule.

## 1. Compute everything on a SortingAnalyzer

```python
import spikeinterface.full as si

an = si.create_sorting_analyzer(sorting, recording_preprocessed, format="binary_folder",
                                folder="analyzer", sparse=True)
an.compute(["random_spikes", "waveforms", "templates", "noise_levels",
            "spike_amplitudes", "principal_components", "unit_locations",
            "correlograms", "template_similarity", "template_metrics"])
qm = an.compute("quality_metrics").get_data()        # pandas DataFrame, one row per unit
```

Quality metrics available (`si.get_quality_metric_list()`):
`num_spikes`, `firing_rate`, `presence_ratio`, `snr`, `isi_violation`,
`rp_violation`, `sliding_rp_violation`, `synchrony`, `firing_range`,
`amplitude_cv`, `amplitude_cutoff`, `noise_cutoff`, `amplitude_median`,
`drift`, `sd_ratio`, plus PCA-based `mahalanobis` (isolation distance and
L-ratio), `d_prime`, `nearest_neighbor`, `silhouette`, `nn_advanced`.

In SpikeInterface 0.105 metrics live in `spikeinterface.metrics`; code
that imports `spikeinterface.qualitymetrics` fails. Import from
`spikeinterface.full` to stay version-proof.

## 2. Automatic labels

| Tool | How | Labels |
|---|---|---|
| Threshold rules | `spikeinterface.curation.threshold_metrics_label_units(qm, thresholds)`, or a pandas query on `qm` | your own |
| Bombcell | `si.bombcell_label_units(analyzer)`; defaults from `si.bombcell_get_default_thresholds()`; standalone MATLAB and Python versions also exist | good, MUA, noise, non-somatic |
| UnitRefine (model-based) | `spikeinterface.curation.unitrefine_label_units(...)` with a pretrained model, or `model_based_label_units` / `train_model` for your own | noise vs neural, SUA vs MUA |
| Kilosort `KSLabel` | `cluster_KSLabel.tsv` | good/mua from refractory violations only |
| Merge suggestions | `si.compute_merge_unit_groups(analyzer)` then `si.auto_merge_units` or `si.apply_merges_to_sorting` | merged units |

Thresholds commonly used as a starting point (state the ones you use):

| Metric | Single-unit criterion |
|---|---|
| `isi_violations_ratio` | below 0.5 (or `rp_contamination` below about 0.1) |
| `amplitude_cutoff` | below 0.1 |
| `presence_ratio` | above 0.9 |
| `firing_rate` | above 0.1 Hz |
| `snr` | above a dataset-specific value, often 5 for Neuropixels |

Use several metrics together. Units with one or two spikes can show
excellent SNR and presence ratio; a firing-rate or spike-count floor
removes them (see the checked result in `spikeinterface.md`).

Every threshold is a choice. Report how many units pass, and check the
main result does not depend on one threshold by repeating it with a
stricter and a looser set.

## 3. Manual review in Phy

```bash
pip install phy                                        # check the Phy README for the current install line
phy template-gui path/to/params.py
```

From SpikeInterface: `si.export_to_phy(analyzer, output_folder="phy",
copy_binary=False)` writes a Phy folder pointing at the binary; read the
result back with `si.read_phy("phy", exclude_cluster_groups=["noise"])`.

For each borderline unit look at: waveform and spatial footprint across
channels; autocorrelogram (a refractory dip near zero); amplitude over
time (drift, drop-out, a cut-off lower edge means missed spikes);
feature view; cross-correlograms with neighbouring units (a refractory
dip in the cross-correlogram suggests one neuron split in two).

Phy's keyboard shortcuts (merge, split, label good/MUA/noise) are listed
under Help > Shortcuts; labels save to `cluster_group.tsv`.

Log every merge and split with the reason. Two people curating the same
session will disagree on borderline units: if results depend on manual
curation, have a second person curate a subset and report agreement.

## 4. Across sessions and days

- **UnitMatch** matches units across days using waveform and location
  (Python and MATLAB). Do not assume a unit with the same ID in two
  sessions is the same neuron.
- Concatenated sorting across sessions only works when drift between
  sessions is small: check the drift map at each join.

## 5. Browser review and sharing

`si.export_report(analyzer, "report")` writes figures and metric tables
per unit. SortingView (figurl) gives shareable curation links;
`si.apply_sortingview_curation` reads the result back.

## Report

Analyzer extensions and parameters, metric list, thresholds or model used
for labels, counts of good/MUA/noise units per session, manual merges and
splits, and agreement if two curators were involved.
