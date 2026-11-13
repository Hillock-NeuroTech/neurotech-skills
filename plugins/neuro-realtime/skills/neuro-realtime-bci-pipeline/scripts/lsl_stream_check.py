#!/usr/bin/env python3
"""Check a live Lab Streaming Layer stream before trusting it: true sampling
rate, gaps, dropped samples, clock offset and how old samples are on arrival.

    python3 lsl_stream_check.py --list
    python3 lsl_stream_check.py --name "MyAmp" --seconds 60
    python3 lsl_stream_check.py --type EEG --seconds 60 --counter-channel 8
    python3 lsl_stream_check.py --simulate --rate 250 --true-rate 252.5 --drop 5000:20

Needs pylsl. "Age on arrival" measures LSL transport and buffering on the
receiving machine only; it does not include amplifier, OS driver or
display latency. Measure end-to-end latency with a photodiode or loopback
(see neuro-stimulus-timing-audit).
"""
import argparse
import json
import sys
import threading
import time

import numpy as np


def simulate_outlet(rate, true_rate, n_channels=8, drop=None, name="hillock-sim", stop=None):
    """Publish a stream that declares `rate` but produces samples at `true_rate`.
    The last channel is a sample counter. `drop=(start, n)` skips n samples."""
    import pylsl

    info = pylsl.StreamInfo(name, "EEG", n_channels + 1, rate, pylsl.cf_float32, "hillock-sim-1")
    outlet = pylsl.StreamOutlet(info, chunk_size=10)
    i, chunk, t0 = 0, 10, pylsl.local_clock()
    rng = np.random.default_rng(0)
    while stop is None or not stop.is_set():
        target = t0 + (i + chunk) / true_rate
        now = pylsl.local_clock()
        if target > now:
            time.sleep(target - now)
        rows = []
        for k in range(i, i + chunk):
            if drop and drop[0] <= k < drop[0] + drop[1]:
                continue
            rows.append(list(rng.normal(0, 10, n_channels)) + [float(k)])
        if rows:
            outlet.push_chunk(rows)
        i += chunk


def check(inlet, seconds, counter_channel=None):
    import pylsl

    info = inlet.info()
    nominal = info.nominal_srate()
    ts, counters, ages, offsets = [], [], [], []
    t_end = pylsl.local_clock() + seconds
    last_offset_check = 0.0
    while pylsl.local_clock() < t_end:
        data, stamps = inlet.pull_chunk(timeout=0.2, max_samples=4096)
        now = pylsl.local_clock()
        if now - last_offset_check > 1.0:
            offsets.append(inlet.time_correction(timeout=2.0))
            last_offset_check = now
        if stamps:
            ts.extend(stamps)
            if counter_channel is not None:
                counters.extend(row[counter_channel] for row in data)
            ages.append(now - (stamps[-1] + (offsets[-1] if offsets else 0.0)))
    ts = np.asarray(ts)
    rep = {
        "name": info.name(), "type": info.type(), "source_id": info.source_id(),
        "hostname": info.hostname(), "channels": info.channel_count(),
        "nominal_rate_hz": nominal, "seconds_requested": seconds, "samples_received": int(len(ts)),
    }
    warnings = []
    if len(ts) < 2:
        warnings.append("no or almost no samples received")
        rep["warnings"] = warnings
        return rep
    if nominal > 0:
        # index each sample by its counter when there is one, so lost samples do not bias the rate
        k = np.asarray(counters, dtype=float) if counters else np.arange(len(ts), dtype=float)
        slope = np.polyfit(k, ts, 1)[0]
        eff = 1.0 / slope
        rep["effective_rate_hz"] = round(float(eff), 4)
        rep["rate_error_ppm"] = round(float((eff - nominal) / nominal * 1e6), 1)
        if abs(eff - nominal) / nominal > 0.002:
            warnings.append(f"true rate {eff:.3f} Hz differs from nominal {nominal} Hz by "
                            f"{(eff - nominal) / nominal * 100:.2f}%: use timestamps, not sample counts, for timing")
        d = np.diff(ts)
        # chunked pushes give timestamps a few ms of jitter; only call it a gap above 5 periods and 50 ms
        gaps = d[d > max(5.0 / nominal, 0.05)]
        rep["timestamp_gaps"] = {"count": int(len(gaps)), "largest_s": round(float(gaps.max()), 4) if len(gaps) else 0.0}
        if len(gaps):
            warnings.append(f"{len(gaps)} gaps in timestamps (largest {gaps.max() * 1000:.1f} ms)")
        rep["timestamp_spacing_jitter_ms"] = round(float(np.std(d) * 1000), 3)
        if np.std(d) > 0.25 / nominal:
            rep["note"] = ("timestamps are chunk-stamped and jittery; dejitter before epoching "
                           "(pyxdf dejitter_timestamps=True, or StreamInlet(processing_flags=pylsl.proc_dejitter))")
    if counters:
        c = np.asarray(counters)
        jumps = np.diff(c)
        lost = int(np.sum(jumps[jumps > 1] - 1))
        rep["counter_lost_samples"] = lost
        rep["counter_repeats_or_resets"] = int(np.sum(jumps < 1))
        if lost:
            warnings.append(f"{lost} samples lost according to the counter channel")
    if offsets:
        o = np.asarray(offsets)
        rep["clock_offset_s"] = {"median": round(float(np.median(o)), 6), "range": round(float(np.ptp(o)), 6)}
    if ages:
        a = np.asarray(ages) * 1000
        rep["age_on_arrival_ms"] = {"median": round(float(np.median(a)), 2), "p95": round(float(np.percentile(a, 95)), 2)}
    rep["warnings"] = warnings
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="list visible streams")
    g.add_argument("--name"); g.add_argument("--type"); g.add_argument("--simulate", action="store_true")
    ap.add_argument("--seconds", type=float, default=30.0)
    ap.add_argument("--counter-channel", type=int, help="index of a channel that counts samples")
    ap.add_argument("--rate", type=float, default=250.0, help="simulate: declared rate")
    ap.add_argument("--true-rate", type=float, help="simulate: actual production rate")
    ap.add_argument("--drop", help="simulate: START:N samples to skip")
    ap.add_argument("--json")
    a = ap.parse_args()
    import pylsl

    if a.list:
        for s in pylsl.resolve_streams(wait_time=2.0):
            print(f"{s.name():30s} type={s.type():10s} ch={s.channel_count():4d} rate={s.nominal_srate():8.2f} host={s.hostname()} id={s.source_id()}")
        return
    stop = None
    if a.simulate:
        stop = threading.Event()
        drop = tuple(int(x) for x in a.drop.split(":")) if a.drop else None
        threading.Thread(target=simulate_outlet, daemon=True,
                         args=(a.rate, a.true_rate or a.rate, 8, drop, "hillock-sim", stop)).start()
        prop, value, a.counter_channel = "name", "hillock-sim", 8
    else:
        prop, value = ("name", a.name) if a.name else ("type", a.type)
    found = pylsl.resolve_byprop(prop, value, timeout=10.0)
    if not found:
        sys.exit(f"no stream with {prop}={value!r} found (try --list)")
    inlet = pylsl.StreamInlet(found[0], max_buflen=60)
    rep = check(inlet, a.seconds, a.counter_channel)
    if stop:
        stop.set()
    print(json.dumps(rep, indent=1))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rep, fh, indent=1)
    sys.exit(1 if rep.get("warnings") else 0)


if __name__ == "__main__":
    main()
