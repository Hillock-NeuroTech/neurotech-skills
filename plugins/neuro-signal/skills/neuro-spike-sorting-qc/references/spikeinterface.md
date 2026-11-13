# SpikeInterface: end-to-end recipe and traps

Checked against SpikeInterface 0.105.4 by running this recipe on a
simulated recording with known ground truth (results at the end).
SpikeInterface wraps readers, preprocessing, about 20 sorters, metrics,
curation, comparison and export behind one API. Import everything from
`spikeinterface.full` so code survives module moves between releases.

## Recipe

```python
import numpy as np
import spikeinterface.full as si

si.set_global_job_kwargs(n_jobs=8, chunk_duration="1s", progress_bar=True)

# 1. read (see neuropixels.md for SpikeGLX / Open Ephys specifics)
rec = si.read_spikeglx(folder, stream_name="imec0.ap")      # or read_openephys, read_intan, read_blackrock, ...
print(rec)                                                  # rate, channels, duration, dtype
assert rec.has_probe()                                      # attach one with rec.set_probe(...) if not

# 2. preprocess lazily, then save once
rp = si.bandpass_filter(rec, freq_min=300., freq_max=6000.)
rp = si.common_reference(rp, reference="global", operator="median")
rp = rp.save(folder="preprocessed")                          # sorters need a saved or serialisable recording

# 3. sort (several sorters for comparison if time allows)
sorting = si.run_sorter("kilosort4", rp, folder="ks4")       # GPU recommended
# docker/singularity images avoid local installs: run_sorter(..., docker_image=True)

# 4. analyse
an = si.create_sorting_analyzer(sorting, rp, format="binary_folder", folder="analyzer", sparse=True)
an.compute(["random_spikes", "waveforms", "templates", "noise_levels", "spike_amplitudes",
            "principal_components", "unit_locations", "correlograms",
            "template_similarity", "template_metrics", "quality_metrics"])
qm = an.get_extension("quality_metrics").get_data()

# 5. curate (see curation.md), then export
si.export_to_phy(an, output_folder="phy", copy_binary=False)
si.export_report(an, "report")
```

Reload later with `si.load_sorting_analyzer("analyzer")`; extensions are
stored with it.

## Sorters

`si.available_sorters()` lists about 20; `si.installed_sorters()` shows
what runs locally. Built in, no extra install: `spykingcircus2`,
`tridesclous2`, `simple`. External: `kilosort4` (pip), `kilosort2`,
`kilosort2_5`, `kilosort3` (MATLAB + CUDA), `mountainsort5` (pip),
`herdingspikes`, `ironclust`, `waveclus`, `combinato`, `dartsort` and
others. Defaults: `si.get_default_sorter_params(name)`; descriptions:
`si.get_sorter_params_description(name)`.

## Checking a pipeline against ground truth

```python
rec, gt = si.generate_ground_truth_recording(durations=[300.], num_channels=32, num_units=20, seed=0)
rec = rec.save(folder="gt_rec")          # in-memory generated recordings cannot be sorted directly
...
cmp = si.compare_sorter_to_ground_truth(gt, sorting, exhaustive_gt=True)
cmp.get_performance()                     # accuracy, precision, recall per unit
cmp.get_well_detected_units(well_detected_score=0.8)
```

Use this before trusting a new sorter, parameter set or preprocessing
change. `si.generate_drifting_recording` adds probe motion;
`si.generate_hybrid_recording` injects known units into real data, which
is the stronger test. `si.compare_two_sorters` and
`si.compare_multiple_sorters` measure agreement between sorters on real
data.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| `import spikeinterface.qualitymetrics` (pre-0.105 code) | ImportError in 0.105 | `import spikeinterface.full as si` |
| Sorting an in-memory or generated recording | `RuntimeError: ... not serializable` | `rec.save(folder=...)` first |
| `n_jobs > 1` from a notebook cell, `python -` or a script without a main guard on macOS or Windows | workers never start: 0% CPU, no error, runs forever | put the code in a `.py` file under `if __name__ == "__main__":`, or set `n_jobs=1` |
| `detect_bad_channels` defaults on non-Neuropixels data | can flag nearly every channel (31 of 32 on a clean simulated probe) | print label counts, inspect, or choose `method=` to suit the probe |
| No probe attached | sorters fail or ignore geometry | `rec.set_probe(probe)` from probeinterface; check with `si.plot_probe_map(rec)` |
| Analyzer computed on the raw instead of the preprocessed recording | wrong waveforms and SNR | pass the same preprocessed recording the sorter used |
| `sparse=False` on high-channel-count probes | huge memory and disk use | `sparse=True` (default) |
| Extensions computed in the wrong order | errors about missing parents | `random_spikes` then `waveforms`/`templates` first; `an.compute` with a list resolves order |
| Different preprocessing in each session | metrics not comparable | save the preprocessing chain (`rec.to_dict()`, `si.get_preprocessing_list_from_analyzer`) and reuse it |

## Checked result

This recipe was run on a simulated 32-channel, 2-minute recording with 12
known neurons (`generate_ground_truth_recording(seed=7)`), sorted with
SpykingCircus2 on a laptop CPU in about 85 s:

- 14 units found; 11 of 12 true neurons recovered with accuracy at or
  above 0.8 (median accuracy 1.0); 3 false units.
- The false units had 1, 2 and 78 spikes. The two tiny ones had excellent
  SNR (13 and 25) and a presence ratio of 0.5-1.0: SNR and presence ratio
  alone would have kept them. The third had an ISI-violation ratio of 13.
- The standard thresholds (ISI-violation ratio below 0.5, presence ratio
  above 0.9, firing rate above 0.1 Hz) kept exactly the 11 true units and
  removed all 3 false ones. Bombcell labelled the false units MUA or noise
  and 10 of the 11 true units good.
- `detect_bad_channels` with default settings flagged 31 of 32 channels
  of this clean probe as bad (dead, noisy or out of brain).

## Report

SpikeInterface, sorter and probeinterface versions; preprocessing chain;
sorter parameters (dump `si.get_default_sorter_params` diffs); analyzer
extensions; metrics and thresholds; curation rule; unit counts per label.
