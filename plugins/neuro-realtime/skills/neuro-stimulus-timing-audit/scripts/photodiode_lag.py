"""Marker-to-sensor lag from a photodiode (or audio) channel.

python photodiode_lag.py --sensor aux.npy --fs 1000 --markers marker_samples.npy
       [--refresh 60] [--window-ms 200] [--polarity rise|fall] [--out corrected.npy]

For each marker, finds the first half-amplitude crossing of the sensor within
the window after it. Prints lag statistics (ms) as JSON.
"""
import argparse
import json

import numpy as np


def onsets(sensor, fs, markers, window_ms=200, polarity="rise"):
    x = np.asarray(sensor, float).ravel()
    if polarity == "fall":
        x = -x
    lo, hi = np.percentile(x, 5), np.percentile(x, 95)
    thr = lo + 0.5 * (hi - lo)
    w = int(window_ms * fs / 1000)
    out = []
    for m in np.asarray(markers, int):
        seg = x[m:m + w]
        if len(seg) < 2:
            out.append(None)
            continue
        above = seg >= thr
        # require the segment to start below threshold, then cross
        start = np.argmax(~above) if above[0] else 0
        cross = np.where(above[start:])[0]
        out.append(int(m + start + cross[0]) if len(cross) else None)
    return out


def summary(markers, ons, fs, refresh=None):
    lag = np.array([(o - m) * 1000 / fs for m, o in zip(markers, ons) if o is not None])
    r = {"events": len(markers), "detected": int(len(lag)), "missed": int(len(markers) - len(lag))}
    if len(lag):
        r.update({"median_lag_ms": round(float(np.median(lag)), 2), "mean_lag_ms": round(float(lag.mean()), 2),
                  "sd_ms": round(float(lag.std()), 2), "min_ms": round(float(lag.min()), 2),
                  "max_ms": round(float(lag.max()), 2)})
        if refresh:
            frame = 1000 / refresh
            extra = np.round((lag - np.min(lag)) / frame)
            r["frame_period_ms"] = round(frame, 3)
            r["events_late_by_frames"] = {int(k): int(v) for k, v in zip(*np.unique(extra, return_counts=True))}
            r["likely_frame_drops"] = int(np.sum(extra >= 1))
            base = lag[extra == 0]
            if len(base) > 1 and base.std() > 0.25 * frame:
                r["warning"] = "on-time lags already spread over a quarter frame: marker is probably not sent on the display flip, so frame counts are approximate"
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sensor", required=True)
    ap.add_argument("--fs", type=float, required=True)
    ap.add_argument("--markers", required=True)
    ap.add_argument("--refresh", type=float)
    ap.add_argument("--window-ms", type=float, default=200)
    ap.add_argument("--polarity", default="rise", choices=["rise", "fall"])
    ap.add_argument("--out")
    a = ap.parse_args()
    mk = np.load(a.markers).astype(int).ravel()
    on = onsets(np.load(a.sensor), a.fs, mk, a.window_ms, a.polarity)
    if a.out:
        np.save(a.out, np.array([o if o is not None else -1 for o in on]))
    print(json.dumps(summary(mk, on, a.fs, a.refresh), indent=2))
