"""Robustly align two clocks from shared events (sync pulses).

python align_clocks.py --a a_times.txt --b b_events.npy --b-rate 500 [--map other_a.txt] [--out mapped.npy]

--a      event times on clock A in seconds (.txt one per line, .csv first column, or .npy)
--b      the same events on clock B: sample indices (with --b-rate) or seconds (--b-rate 1)
--b-rate nominal rate of clock B in units per second (samples/s; 1 if B is in seconds)
--map    optional clock-A times to convert to clock B (rounded to integers if --b-rate > 1)

Handles dropped and spurious events on either side. Prints a JSON report.
"""
import argparse
import json

import numpy as np


def read(path):
    if path.endswith(".npy"):
        return np.load(path).astype(float).ravel()
    vals = []
    for line in open(path):
        cell = line.strip().split(",")[0]
        try:
            vals.append(float(cell))
        except ValueError:
            continue
    return np.array(vals)


def match(a, b, slope, offset, tol):
    pred = slope * a + offset
    j = np.clip(np.searchsorted(b, pred), 1, len(b) - 1)
    j = np.where(np.abs(b[j - 1] - pred) < np.abs(b[j] - pred), j - 1, j)
    ok = np.abs(b[j] - pred) < tol
    # one-to-one: keep the closest a for each b
    best = {}
    for i in np.where(ok)[0]:
        d = abs(b[j[i]] - pred[i])
        if j[i] not in best or d < best[j[i]][1]:
            best[j[i]] = (i, d)
    ia = np.array(sorted(v[0] for v in best.values()), int)
    ib = np.array([j[i] for i in ia], int)
    return ia, ib


def align(a, b, rate, n_seed=6, seed_window_s=600):
    a, b = np.sort(a), np.sort(b)
    best = (-1, 0.0)
    for i in range(min(n_seed, len(a))):
        for k in range(min(n_seed, len(b))):
            off = b[k] - rate * a[i]
            sel = a < a[i] + seed_window_s
            ia, _ = match(a[sel], b, rate, off, tol=0.02 * rate)
            if len(ia) > best[0]:
                best = (len(ia), off)
    slope, off = rate, best[1]
    for frac in (0.1, 0.25, 0.5, 1.0):
        horizon = a[0] + frac * (a[-1] - a[0]) + 1e-9
        sel = a <= horizon
        ia, ib = match(a[sel], b, slope, off, tol=max(0.05 * rate, 3))
        if len(ia) >= 2:
            slope, off = np.polyfit(a[sel][ia], b[ib], 1)
    ia, ib = match(a, b, slope, off, tol=max(0.01 * rate, 2))
    slope, off = np.polyfit(a[ia], b[ib], 1)
    resid = b[ib] - (slope * a[ia] + off)
    return {
        "slope": slope, "offset": off,
        "drift_ppm": (slope / rate - 1) * 1e6,
        "effective_rate": slope,
        "matched": int(len(ia)), "events_a": int(len(a)), "events_b": int(len(b)),
        "unmatched_a_times": [round(float(x), 4) for x in np.delete(a, ia)][:50],
        "unmatched_b_values": [round(float(x), 2) for x in np.delete(b, ib)][:50],
        "residual_rms": float(np.sqrt(np.mean(resid ** 2))),
        "residual_max_abs": float(np.max(np.abs(resid))),
        "residual_step_suspected": bool(np.max(np.abs(np.diff(resid))) > 5 * (np.std(np.diff(resid)) + 1e-12)
                                        and np.max(np.abs(resid)) > 2),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--b-rate", type=float, required=True)
    ap.add_argument("--map")
    ap.add_argument("--out")
    x = ap.parse_args()
    r = align(read(x.a), read(x.b), x.b_rate)
    if x.map:
        m = r["slope"] * read(x.map) + r["offset"]
        m = np.round(m).astype(int) if x.b_rate > 1 else m
        if x.out:
            np.save(x.out, m)
        r["mapped"] = m.tolist()
    for k in ("slope", "offset", "drift_ppm", "effective_rate", "residual_rms", "residual_max_abs"):
        r[k] = round(r[k], 6)
    print(json.dumps(r, indent=2))
