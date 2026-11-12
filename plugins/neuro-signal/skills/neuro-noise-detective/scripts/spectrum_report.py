"""Measure the spectral and amplitude signatures of common noise sources.

python spectrum_report.py --data raw.npy --fs 1000 [--names names.json] [--line 50|60]
python spectrum_report.py --mne-file rec.fif [--picks eeg] [--line 50]

Prints a JSON report; does not modify data.
"""
import argparse
import json

import numpy as np
from scipy.signal import welch


def load(a):
    if a.mne_file:
        import mne
        raw = mne.io.read_raw(a.mne_file, preload=True, verbose="error")
        if a.picks:
            raw.pick(a.picks)
        return raw.get_data(), raw.info["sfreq"], raw.ch_names
    X = np.load(a.data)
    names = json.load(open(a.names)) if a.names else [f"ch{i}" for i in range(len(X))]
    return X, a.fs, names


def band(f, P, lo, hi):
    m = (f >= lo) & (f < hi)
    return P[:, m].mean(axis=1) if m.any() else np.zeros(len(P))


def peak_db(f, P, f0, half=0.6):
    """Peak height above the local floor (dB), per channel."""
    on = (f >= f0 - half) & (f <= f0 + half)
    off = ((f >= f0 - 5) & (f < f0 - 2)) | ((f > f0 + 2) & (f <= f0 + 5))
    if not on.any() or not off.any():
        return np.full(len(P), np.nan)
    return 10 * np.log10(P[:, on].max(axis=1) / np.median(P[:, off], axis=1))


def report(X, fs, names, line=None):
    X = np.asarray(X, float)
    nper = int(min(X.shape[1], 4 * fs))
    f, P = welch(X, fs=fs, nperseg=nper)
    P = P + 1e-30
    nyq = fs / 2
    if line is None:
        line = 50 if np.nanmean(peak_db(f, P, 50)) >= np.nanmean(peak_db(f, P, 60)) else 60
    harm = {}
    for k in range(1, 8):
        fk = k * line
        if fk < nyq - 5:
            d = peak_db(f, P, fk)
            harm[f"{fk:g}Hz"] = {"median_db_above_floor": round(float(np.nanmedian(d)), 1),
                                 "max_db": round(float(np.nanmax(d)), 1),
                                 "channels_over_10db": int(np.sum(d > 10))}
    odd = [harm[k]["median_db_above_floor"] for i, k in enumerate(harm) if (i + 1) % 2 == 1 and i > 0]
    even = [harm[k]["median_db_above_floor"] for i, k in enumerate(harm) if (i + 1) % 2 == 0]
    sd = X.std(axis=1)
    flat_i = set(np.where(sd < 1e-3 * np.median(sd))[0])
    sat_i = set(i for i, x in enumerate(X)
                if np.mean(np.isclose(x, x.max())) + np.mean(np.isclose(x, x.min())) > 0.001)
    good = [i for i in range(len(X)) if i not in flat_i | sat_i] or list(range(len(X)))
    # narrow peaks per channel, away from line multiples; alpha band reported separately
    from scipy.signal import find_peaks
    from scipy.ndimage import median_filter
    peaks = {}
    for i in good:
        lp = np.log10(P[i])
        resid = lp - median_filter(lp, size=max(5, int(len(f) / 100)))
        for j in find_peaks(resid, height=0.5)[0]:
            fj = round(float(f[j]) * 2) / 2
            if fj <= 1 or min(abs(fj - k * line) for k in range(1, 40)) <= 1.5:
                continue
            peaks.setdefault(fj, []).append(names[i])
    alpha = {k: v for k, v in peaks.items() if 7 <= k <= 14}
    others = {f"{k:g}Hz": v if len(v) <= 6 else f"{len(v)} channels"
              for k, v in sorted(peaks.items()) if not 7 <= k <= 14}
    hf = band(f, P, 30, min(100, nyq - 1)) / band(f, P, 8, 13)
    slow = band(f, P, 0.1, 1) / band(f, P, 1, 30)
    hf_rel = hf / np.median(hf[good])
    slow_rel = slow / np.median(slow[good])
    flat = [names[i] for i in sorted(flat_i)]
    sat = [names[i] for i in sorted(sat_i)]
    line_db = peak_db(f, P, line)
    spread = np.nanmedian(np.abs(line_db[good] - np.nanmedian(line_db[good])))
    rep = {
        "fs": fs, "n_channels": len(X), "duration_s": round(X.shape[1] / fs, 1),
        "line_frequency_hz": line,
        "line_harmonics": harm,
        "line_noise_pattern": "common to most channels (reference/ground/environment)" if spread < 4
        else "uneven across channels (electrode-specific impedance)",
        "line_worst_channels": [names[i] for i in sorted(good, key=lambda i: -np.nan_to_num(line_db[i]))[:5]],
        "odd_vs_even_harmonics_db": [round(float(np.mean(odd)), 1) if odd else None,
                                     round(float(np.mean(even)), 1) if even else None],
        "non_line_narrow_peaks": others,
        "alpha_band_peaks_hz": sorted(alpha),
        "muscle_index_vs_median_channel": {names[i]: round(float(hf_rel[i]), 1) for i in sorted(good, key=lambda i: -hf_rel[i])[:5]},
        "slow_drift_index_vs_median_channel": {names[i]: round(float(slow_rel[i]), 1) for i in sorted(good, key=lambda i: -slow_rel[i])[:5]},
        "flat_channels": flat, "possibly_saturated_channels": sat,
        "channel_sd_median": float(np.median(sd)),
        "hint": "odd harmonics well above even ones suggest switching supplies or other non-linear loads; "
                "muscle_index several times the median channel suggests EMG on that channel; "
                "slow_drift_index several times the median suggests sweat, gel drying or cable motion; "
                "alpha_band_peaks are usually physiological, not interference.",
    }
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data")
    ap.add_argument("--fs", type=float)
    ap.add_argument("--names")
    ap.add_argument("--mne-file")
    ap.add_argument("--picks")
    ap.add_argument("--line", type=float)
    a = ap.parse_args()
    X, fs, names = load(a)
    print(json.dumps(report(X, fs, names, a.line), indent=2))
