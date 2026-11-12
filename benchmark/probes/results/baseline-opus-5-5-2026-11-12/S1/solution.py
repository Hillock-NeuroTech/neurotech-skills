"""Map stimulus-PC keypress times to EEG sample indices.

The PC log and the EEG trigger channel do not have the same number of sync
events: some pulses were never detected on the amplifier (missing edges), and
there is at least one spurious edge. So the sync pulses cannot be paired by
index. Instead we:
  1. Seed a linear clock model (sample = a*t_pc + b) from the first few syncs.
     Their inter-pulse intervals match the first few EEG edges exactly.
  2. Iteratively pair each PC sync with the nearest EEG edge, keep only pairs
     whose residual is < 20 samples, and refit. A slope a != sfreq absorbs the
     drift between the two clocks.
  3. Apply the final model to keypress times.
"""
import json
import numpy as np
import pandas as pd

hdr = json.load(open("header.json"))
fs = hdr["sfreq"]
log = pd.read_csv("pc_log.csv")
sync_t = log.loc[log.event == "sync", "time_s"].to_numpy()
key_t = log.loc[log.event == "keypress", "time_s"].to_numpy()
edges = np.sort(np.load("eeg_trigger_samples.npy"))

# Sanity check of the seed: the first 5 PC intervals match the first 5 EEG intervals
assert np.allclose(np.diff(sync_t[:5]) * fs, np.diff(edges[:5]), atol=3)
a, b = np.polyfit(sync_t[:5], edges[:5], 1)

def nearest(pred):
    i = np.clip(np.searchsorted(edges, pred), 1, len(edges) - 1)
    return np.where(np.abs(edges[i - 1] - pred) < np.abs(edges[i] - pred), i - 1, i)

for _ in range(10):
    pred = a * sync_t + b
    j = nearest(pred)
    ok = np.abs(edges[j] - pred) < 20
    # one-to-one pairing
    assert len(np.unique(j[ok])) == ok.sum()
    a_new, b_new = np.polyfit(sync_t[ok], edges[j][ok], 1)
    if np.isclose(a_new, a) and np.isclose(b_new, b):
        break
    a, b = a_new, b_new

pred = a * sync_t + b
res = edges[j][ok] - pred[ok]
unmatched_edges = np.setdiff1d(np.arange(len(edges)), j[ok])
print(f"slope={a:.5f} samples/s (drift {(a/fs-1)*1e6:.1f} ppm), offset={b:.2f}")
print(f"matched {ok.sum()}/{len(sync_t)} PC syncs; missing on EEG: {(~ok).sum()}; "
      f"spurious EEG edges: {len(unmatched_edges)} at {edges[unmatched_edges].tolist()}")
print(f"residual: max |r|={np.abs(res).max():.2f} samples, sd={res.std():.3f}")

key_samples = np.rint(a * key_t + b).astype(int)
json.dump({"keypress_samples": key_samples.tolist()}, open("answer.json", "w"), indent=2)
print(key_samples.tolist())
