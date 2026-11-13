#!/usr/bin/env python3
"""Rebuild Medtronic Percept time-domain streams from a session JSON export,
with lost packets kept as NaN gaps instead of being silently concatenated.

    python3 percept_timedomain.py Report_Json_Session_Report_*.json
    python3 percept_timedomain.py report.json --section IndefiniteStreaming --out lfp.npz

Reads BrainSenseTimeDomain (default), IndefiniteStreaming or
LfpMontageTimeDomain. Timing follows the logic of the perceive toolbox
(neuromodulation/perceive): one packet every 250 ms by TicksInMses, packet
lengths from GlobalPacketSizes, gaps where consecutive ticks differ by more
than 250 ms. Research tool; not for clinical use. Check results against
perceive for your firmware version.
"""
import argparse
import json
import sys

import numpy as np

PACKET_MS = 250.0


def _nums(x):
    """Percept stores several fields as comma-separated strings."""
    if isinstance(x, str):
        return np.array([float(v) for v in x.split(",") if v.strip() != ""])
    return np.asarray(x, dtype=float)


def rebuild(entry):
    """One stream entry -> (signal with NaN gaps, sampling rate, report)."""
    fs = float(entry["SampleRateInHz"])
    data = np.asarray(entry["TimeDomainData"], dtype=float)
    ticks = _nums(entry["TicksInMses"])
    sizes = _nums(entry["GlobalPacketSizes"]).astype(int)
    if len(ticks) != len(sizes):
        raise ValueError(f"{len(ticks)} ticks but {len(sizes)} packet sizes")
    if sizes.sum() != len(data):
        raise ValueError(f"packet sizes sum to {sizes.sum()} but {len(data)} samples present")
    # packets are contiguous; ticks only tell us where packets are missing (perceive's approach)
    rel_ms = ticks - ticks[0]
    steps = np.diff(rel_ms)
    extra = [int(round(max(st - PACKET_MS, 0.0) / 1000.0 * fs)) if st > PACKET_MS * 1.5 else 0 for st in steps]
    out = np.full(len(data) + sum(extra), np.nan)
    gaps, i_data, i_out = [], 0, 0
    for k, n in enumerate(sizes):
        out[i_out:i_out + n] = data[i_data:i_data + n]
        i_data += n
        i_out += n
        if k < len(steps):
            st = steps[k]
            if st > PACKET_MS * 1.5:
                gaps.append({"after_s": round((rel_ms[k] + PACKET_MS) / 1000.0, 3),
                             "missing_packets": int(round(st / PACKET_MS)) - 1})
                i_out += extra[k]
            elif st < PACKET_MS * 0.5:
                gaps.append({"after_s": round(rel_ms[k] / 1000.0, 3), "missing_packets": 0,
                             "note": f"ticks step {st:.0f} ms (overlap or clock reset)"})
    n_missing = sum(g["missing_packets"] for g in gaps)
    rep = {
        "channel": entry.get("Channel"),
        "first_packet": entry.get("FirstPacketDateTime"),
        "fs_hz": fs,
        "packets": int(len(sizes)),
        "missing_packets": int(n_missing),
        "fraction_lost": round(n_missing / (len(sizes) + n_missing), 4) if len(sizes) else None,
        "duration_s": round(len(out) / fs, 3),
        "gaps": gaps,
    }
    return out, fs, rep


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("json_file")
    ap.add_argument("--section", default="BrainSenseTimeDomain",
                    choices=["BrainSenseTimeDomain", "IndefiniteStreaming", "LfpMontageTimeDomain"])
    ap.add_argument("--out", help="save signals to .npz (one array per stream)")
    a = ap.parse_args()
    with open(a.json_file) as fh:
        js = json.load(fh)
    entries = js.get(a.section) or []
    if not entries:
        sys.exit(f"no {a.section} section in this export; sections present: {sorted(js)}")
    arrays, reports = {}, []
    for i, e in enumerate(entries):
        sig, fs, rep = rebuild(e)
        reports.append(rep)
        arrays[f"stream{i}_{rep['channel']}"] = sig
    print(json.dumps(reports, indent=1))
    if a.out:
        np.savez_compressed(a.out, **arrays)
    sys.exit(1 if any(r["missing_packets"] or r["gaps"] for r in reports) else 0)


if __name__ == "__main__":
    main()
