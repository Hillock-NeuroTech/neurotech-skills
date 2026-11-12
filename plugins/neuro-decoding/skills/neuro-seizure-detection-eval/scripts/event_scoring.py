"""Event-based scoring for seizure (or any rare-event) detectors.

python event_scoring.py --ref ref.csv --det det.csv --hours 72.5 [--tolerance 0]

CSV columns: onset_s,offset_s[,record]. A reference event is detected if any
detection in the same record overlaps it (extended by --tolerance seconds on
both sides). A detection overlapping no reference event is a false alarm.
"""
import argparse
import csv
import json
from collections import defaultdict

import numpy as np


def load(path):
    ev = defaultdict(list)
    for r in csv.DictReader(open(path)):
        ev[r.get("record", "_")].append((float(r["onset_s"]), float(r["offset_s"])))
    return ev


def score(ref, det, hours, tol=0.0):
    tp, fn, fa, lat = 0, 0, 0, []
    for rec in set(ref) | set(det):
        R, D = ref.get(rec, []), det.get(rec, [])
        hit = [False] * len(D)
        for on, off in R:
            over = [i for i, (a, b) in enumerate(D) if a <= off + tol and b >= on - tol]
            if over:
                tp += 1
                lat.append(min(D[i][0] for i in over) - on)
                for i in over:
                    hit[i] = True
            else:
                fn += 1
        fa += hit.count(False)
    n_ref = tp + fn
    precision_den = tp + fa
    sens = tp / n_ref if n_ref else float("nan")
    prec = tp / precision_den if precision_den else float("nan")
    f1 = 2 * sens * prec / (sens + prec) if (sens + prec) else 0.0
    return {
        "reference_events": n_ref, "detected": tp, "missed": fn, "false_alarms": fa,
        "sensitivity": round(sens, 4), "false_alarms_per_hour": round(fa / hours, 4),
        "false_alarms_per_24h": round(24 * fa / hours, 3),
        "precision": round(prec, 4), "f1": round(f1, 4),
        "median_latency_s": round(float(np.median(lat)), 2) if lat else None,
        "tolerance_s": tol, "hours": hours,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--det", required=True)
    ap.add_argument("--hours", type=float, required=True, help="total recording hours scored")
    ap.add_argument("--tolerance", type=float, default=0.0)
    a = ap.parse_args()
    print(json.dumps(score(load(a.ref), load(a.det), a.hours, a.tolerance), indent=2))
