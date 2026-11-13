#!/usr/bin/env python3
"""Load any MNE-readable recording and report what a person should check
before analysing it: rate, channels, units, events, gaps, montage, line noise.

    python3 inspect_recording.py recording.vhdr
    python3 inspect_recording.py recording.edf --json report.json

Needs mne (and whatever extra package the specific reader needs).
Exit code 0 when no warning was raised, 1 when at least one was.
"""
import argparse
import json
import sys

import numpy as np

EXG_TYPES = ("eeg", "eog", "ecg", "emg", "seeg", "ecog", "dbs")


def _amplitude_flag(median_abs_volts, ch_type):
    """Plausibility of a channel type's typical amplitude, in volts."""
    if ch_type in ("eeg", "eog", "seeg", "ecog", "dbs"):
        lo, hi = 1e-7, 1e-3
    elif ch_type in ("ecg", "emg"):
        lo, hi = 1e-7, 1e-1
    else:
        return None
    if median_abs_volts > 0.5:
        return "values look like microvolts stored as volts (multiply by 1e-6)"
    if median_abs_volts < 1e-9:
        return "values look far too small (volts read as microvolts, or a flat recording)"
    if not lo <= median_abs_volts <= hi:
        return f"median |x| = {median_abs_volts:.2e} V is unusual for {ch_type}"
    return None


def inspect(path, max_seconds=300.0):
    import mne

    mne.set_log_level("ERROR")
    raw = mne.io.read_raw(path, preload=False)
    sf = raw.info["sfreq"]
    stop = int(min(raw.n_times, max_seconds * sf))
    data = raw.get_data(start=0, stop=stop)
    types = raw.get_channel_types()
    warnings = []

    rep = {
        "file": str(path),
        "reader": type(raw).__name__,
        "mne_version": mne.__version__,
        "sfreq": sf,
        "n_samples": int(raw.n_times),
        "duration_s": round(raw.n_times / sf, 3),
        "meas_date": str(raw.info["meas_date"]),
        "highpass_lowpass_in_header": [raw.info["highpass"], raw.info["lowpass"]],
        "channels_by_type": {t: types.count(t) for t in sorted(set(types))},
        "bads_in_file": list(raw.info["bads"]),
    }

    # amplitude per channel type
    amp = {}
    for t in sorted(set(types)):
        if t not in EXG_TYPES:
            continue
        idx = [i for i, ct in enumerate(types) if ct == t]
        med = float(np.median(np.abs(data[idx] - np.median(data[idx], axis=1, keepdims=True))))
        amp[t] = med
        flag = _amplitude_flag(med, t)
        if flag:
            warnings.append(f"{t}: {flag}")
    rep["median_abs_amplitude_V"] = amp

    # flat and saturated channels
    flat, clipped = [], []
    for i, name in enumerate(raw.ch_names):
        if types[i] not in EXG_TYPES:
            continue
        x = data[i]
        if np.ptp(x) == 0 or np.std(x) < 1e-12:
            flat.append(name)
            continue
        top = np.isclose(x, x.max()).mean()
        bottom = np.isclose(x, x.min()).mean()
        if max(top, bottom) > 0.001:
            clipped.append(name)
    if flat:
        warnings.append(f"flat channels: {flat}")
    if clipped:
        warnings.append(f"channels sitting at their min or max for >0.1% of samples (clipping?): {clipped}")
    rep["flat_channels"], rep["possibly_clipped_channels"] = flat, clipped

    # events: stim channels and annotations
    stim = [n for n, t in zip(raw.ch_names, types) if t == "stim"]
    ev = {}
    if stim:
        try:
            events = mne.find_events(raw, stim_channel=stim, shortest_event=1)
            codes, counts = np.unique(events[:, 2], return_counts=True)
            ev["stim_channel_events"] = {int(c): int(n) for c, n in zip(codes, counts)}
        except Exception as e:  # noqa: BLE001
            ev["stim_channel_error"] = str(e)
    if len(raw.annotations):
        d, n = np.unique(raw.annotations.description, return_counts=True)
        ev["annotations"] = {str(a): int(b) for a, b in zip(d, n)}
        gaps = [a for a in raw.annotations.description if a.upper().startswith(("BAD_ACQ_SKIP", "EDGE"))]
        if gaps:
            warnings.append(f"{len(gaps)} acquisition gaps or edges annotated: data are discontinuous")
    if not ev:
        warnings.append("no events found on stim channels or in annotations: check for a separate event file")
    rep["events"] = ev

    # montage
    mont = raw.get_montage()
    eeg_names = [n for n, t in zip(raw.ch_names, types) if t == "eeg"]
    if eeg_names:
        if mont is None:
            rep["montage"] = None
            warnings.append("EEG channels have no positions: set a montage that matches the cap")
        else:
            pos = mont.get_positions()["ch_pos"]
            missing = [n for n in eeg_names if n not in pos or not np.isfinite(pos[n]).all()]
            rep["montage"] = {"with_positions": len(eeg_names) - len(missing), "without": missing[:20]}
            if missing:
                warnings.append(f"{len(missing)} EEG channels without positions")

    # line noise
    picks = [i for i, t in enumerate(types) if t in EXG_TYPES]
    if picks and sf > 130:
        from scipy.signal import welch

        f, p = welch(data[picks], fs=sf, nperseg=int(min(stop, 4 * sf)))
        p = np.median(p, axis=0)

        def peak(f0):
            band = (f > f0 - 1) & (f < f0 + 1)
            ref = ((f > f0 - 6) & (f < f0 - 2)) | ((f > f0 + 2) & (f < f0 + 6))
            return float(10 * np.log10(p[band].max() / np.median(p[ref])))

        p50, p60 = peak(50.0), peak(60.0)
        rep["line_noise_peak_dB"] = {"50Hz": round(p50, 1), "60Hz": round(p60, 1)}
        if max(p50, p60) > 6:
            rep["line_frequency_guess"] = 50 if p50 > p60 else 60
    rep["warnings"] = warnings
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path")
    ap.add_argument("--json", help="also write the report to this file")
    ap.add_argument("--max-seconds", type=float, default=300.0, help="seconds of data to scan (default 300)")
    a = ap.parse_args()
    rep = inspect(a.path, a.max_seconds)
    for k, v in rep.items():
        if k != "warnings":
            print(f"{k:28s} {v}")
    print("\nWARNINGS:" if rep["warnings"] else "\nNo warnings.")
    for w in rep["warnings"]:
        print("  -", w)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rep, fh, indent=1, default=str)
    sys.exit(1 if rep["warnings"] else 0)


if __name__ == "__main__":
    main()
