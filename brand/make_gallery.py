#!/usr/bin/env python3
"""Render the README gallery by running four of the suite's scripts on
synthetic data. Every number in the figure comes from the script output.

    python3 brand/make_gallery.py      # needs numpy, scipy, scikit-learn, matplotlib

Writes assets/gallery.png and prints the values it plotted.
"""
import importlib.util
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK, SUB, ACCENT, BLUE, GRID = "#101418", "#5b6470", "#ff6a3d", "#2f6fdf", "#e6e8eb"
plt.rcParams.update({"font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"], "font.size": 11,
                     "axes.edgecolor": "#c9ced4", "axes.labelcolor": SUB, "xtick.color": SUB, "ytick.color": SUB,
                     "axes.spines.top": False, "axes.spines.right": False})


def load(rel):
    path = os.path.join(ROOT, "plugins", rel)
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def title(ax, skill, text):
    ax.set_title(text, loc="left", fontsize=13.5, color=INK, fontweight="bold", pad=22)
    ax.text(0, 1.035, skill, transform=ax.transAxes, fontsize=10, color=SUB, family="monospace")


def panel_leakage(ax):
    """Labels constant within recording sessions, plus a session fingerprint in the features:
    a trial-level split learns the session, not the brain state."""
    ev = load("neuro-decoding/skills/neuro-bci-decoding-eval/scripts/leakage_safe_eval.py")
    rng = np.random.default_rng(0)
    n_sess, per = 12, 30
    groups = np.repeat(np.arange(n_sess), per)
    y = np.repeat(np.arange(n_sess) % 2, per)
    X = rng.normal(0, 1, (n_sess * per, 16)) + rng.normal(0, 1.5, (n_sess, 16))[groups]
    pipe = ev.MODELS["lda"]()
    naive = ev.evaluate(pipe, X, y, groups=None, n_perm=0)
    safe = ev.evaluate(pipe, X, y, groups=groups, n_perm=100)
    vals = [naive["balanced_accuracy"], safe["balanced_accuracy"]]
    bars = ax.bar([0, 1], vals, width=0.55, color=[ACCENT, BLUE])
    ax.axhline(safe["binomial_chance_threshold_p05"], color=SUB, ls="--", lw=1)
    ax.text(1.48, safe["binomial_chance_threshold_p05"] + 0.02, "chance level, p = 0.05", color=SUB, fontsize=9, ha="right")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", color=INK, fontsize=12, fontweight="bold")
    ax.set_xticks([0, 1], ["split by trial", "split by session"])
    ax.set_ylim(0, 1.08); ax.set_ylabel("balanced accuracy"); ax.set_xlim(-0.6, 1.5)
    ax.text(1, -0.24, f"permutation p = {safe['permutation_p']}", transform=ax.get_xaxis_transform(), ha="center",
            color=SUB, fontsize=9.5)
    title(ax, "neuro-bci-decoding-eval", "The same decoder, two answers")
    return {"naive": naive, "grouped": safe}


def panel_percept(ax):
    pt = load("neuro-stim/skills/neuro-dbs-sensing-data/scripts/percept_timedomain.py")
    rng = np.random.default_rng(3)
    sizes, ticks, data, t, missing = [], [], [], 1000, {10, 11, 25}
    tt = np.arange(40 * 62.5) / 250
    clean = 2.0 * np.sin(2 * np.pi * 20 * tt) * (1 + 0.5 * np.sin(2 * np.pi * 0.3 * tt)) + rng.normal(0, 0.8, tt.size)
    pos = 0
    for k in range(40):
        n = 63 if k % 2 else 62
        if k not in missing:
            sizes.append(n); ticks.append(t); data.extend(clean[pos:pos + n].tolist())
        pos += n; t += 250
    entry = {"Channel": "ZERO_THREE_LEFT", "FirstPacketDateTime": "2026-01-01T10:00:00.000Z", "SampleRateInHz": 250,
             "TimeDomainData": data, "TicksInMses": ",".join(map(str, ticks)) + ",",
             "GlobalPacketSizes": ",".join(map(str, sizes)) + ","}
    sig, fs, rep = pt.rebuild(entry)
    ts = np.arange(sig.size) / fs
    ax.plot(np.arange(len(data)) / fs, np.asarray(data) + 9, color="#9aa3ad", lw=0.6)
    ax.plot(ts, sig, color=BLUE, lw=0.6)
    for g in rep["gaps"]:
        ax.axvspan(g["after_s"], g["after_s"] + g["missing_packets"] * 0.25, ymin=0.07, ymax=0.56, color=ACCENT, alpha=0.25, lw=0)
    ax.text(0, 13.6, "concatenated (gaps hidden)", color=SUB, fontsize=9.5)
    ax.text(0, 4.6, "rebuilt from packet ticks", color=BLUE, fontsize=9.5)
    ax.text(rep["gaps"][0]["after_s"] + 0.6, -6.5, f"{rep['missing_packets']} lost packets → NaN", color=ACCENT, fontsize=9.5)
    ax.set_yticks([]); ax.set_xlabel("time (s)"); ax.set_xlim(0, 10); ax.set_ylim(-7.5, 15)
    ax.spines["left"].set_visible(False)
    title(ax, "neuro-dbs-sensing-data", "Lost packets kept as gaps")
    return rep


def panel_tus(ax):
    tus = load("neuro-stim/skills/neuro-tus-dose-planning/scripts/tus_indices.py")
    protocols = {"10% duty": dict(pnp_mpa=0.8, freq_mhz=0.5, pulse_ms=0.1, prf_hz=1000),
                 "100% duty": dict(pnp_mpa=0.8, freq_mhz=0.5, pulse_ms=1.0, prf_hz=1000)}
    out = {k: tus.indices(**v) for k, v in protocols.items()}
    names = list(out)
    ispta = [out[k]["Ispta_mW_cm2"] for k in names]
    mi = [out[k]["MI"] for k in names]
    bars = ax.barh([1, 0], ispta, color=[BLUE, ACCENT], height=0.5)
    ax.axvline(tus.FDA_DIAGNOSTIC_ISPTA_MW_CM2, color=SUB, ls="--", lw=1)
    ax.text(tus.FDA_DIAGNOSTIC_ISPTA_MW_CM2 * 1.15, 1.42, "720 mW/cm²\ndiagnostic reference", color=SUB, fontsize=9)
    for b, v, m in zip(bars, ispta, mi):
        ax.text(v * 1.12, b.get_y() + b.get_height() / 2, f"{v:,.0f} mW/cm²   MI {m:.2f}", va="center", color=INK,
                fontsize=10.5)
    ax.set_xscale("log"); ax.set_xlim(100, 1e5)
    ax.set_yticks([1, 0], names); ax.set_ylim(-0.6, 1.9); ax.set_xlabel("in situ Ispta, log scale  (both 0.8 MPa at 500 kHz)")
    title(ax, "neuro-tus-dose-planning", "Same MI, very different dose")
    return out


def panel_noise(ax):
    sr = load("neuro-signal/skills/neuro-noise-detective/scripts/spectrum_report.py")
    from scipy.signal import welch
    rng = np.random.default_rng(1)
    fs, n = 500, 500 * 60
    t = np.arange(n) / fs
    pink = np.cumsum(rng.normal(0, 1, (8, n)), axis=1)
    pink -= np.apply_along_axis(lambda x: np.convolve(x, np.ones(250) / 250, "same"), 1, pink)
    X = 4 * pink + 6 * np.sin(2 * np.pi * 10 * t)
    mains = 3 * np.sin(2 * np.pi * 50 * t) + 1.2 * np.sin(2 * np.pi * 150 * t) + 0.8 * np.sin(2 * np.pi * 250 * t)
    X = X + mains + rng.normal(0, 1, (8, n))
    X[5] += 25 * rng.normal(0, 1, n) * (np.abs(np.sin(2 * np.pi * 0.2 * t)) > 0.7)   # EMG bursts on one channel
    names = ["Fp1", "Fp2", "C3", "C4", "P3", "T8", "O1", "O2"]
    rep = sr.report(X, fs, names)
    f, P = welch(X, fs=fs, nperseg=4 * fs)
    for i in range(8):
        if names[i] != "T8":
            ax.semilogy(f, P[i], color="#aab3bd", lw=0.7)
    ax.semilogy(f, P[5], color=ACCENT, lw=1.1, label="T8 (EMG bursts)")
    for k, h in rep["line_harmonics"].items():
        fk = float(k[:-2])
        if h["median_db_above_floor"] > 10:
            ax.annotate(f"{k}\n+{h['median_db_above_floor']:.0f} dB", (fk, P[:, int(fk * 4)].max()), xytext=(0, 10),
                        textcoords="offset points", ha="center", fontsize=8.5, color=BLUE)
    ax.set_xlim(0, 260); ax.set_ylim(top=P.max() * 30); ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("power")
    ax.set_yticks([]); ax.minorticks_off()
    ax.legend(frameon=False, loc="upper right", fontsize=9.5, labelcolor=ACCENT, handlelength=1.2)
    title(ax, "neuro-noise-detective", "Mains harmonics and a muscle channel")
    return {k: rep[k] for k in ("line_frequency_hz", "line_harmonics", "line_noise_pattern",
                                "muscle_index_vs_median_channel", "odd_vs_even_harmonics_db")}


def main():
    fig, axes = plt.subplots(2, 2, figsize=(14, 8.6), dpi=110, facecolor="white")
    fig.subplots_adjust(left=0.085, right=0.97, top=0.9, bottom=0.115, hspace=0.62, wspace=0.22)
    out = {"leakage": panel_leakage(axes[0, 0]), "percept": panel_percept(axes[0, 1]),
           "tus": panel_tus(axes[1, 0]), "noise": panel_noise(axes[1, 1])}
    fig.text(0.085, 0.012, "Synthetic data. Each panel runs one of the suite's scripts; "
             "regenerate with python3 brand/make_gallery.py", color=SUB, fontsize=9.5)
    path = os.path.join(ROOT, "assets", "gallery.png")
    fig.savefig(path, facecolor="white")
    out["percept"] = {k: out["percept"][k] for k in ("missing_packets", "gaps")}
    print(json.dumps(out, indent=1, default=str))
    print("wrote", path)


if __name__ == "__main__":
    main()
