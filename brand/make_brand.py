#!/usr/bin/env python3
"""Draw the Hillock brand assets with matplotlib.

    python3 brand/make_brand.py

The mark: a neuron's cell body narrowing at the axon hillock into an axon
that fires one action potential. Writes SVG and PNG files to assets/brand/.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "brand")
INK, PAPER, ACCENT = "#101418", "#fcfcfb", "#ff6a3d"
DARK_BG, DARK_INK = "#0d1117", "#f0f3f6"
FONT = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]


def spike_xy(x0, length, height):
    """Baseline, sharp rise, overshoot, undershoot below baseline, recovery."""
    t = np.linspace(0, 1, 400)
    y = np.zeros_like(t)
    rise = (t > 0.30) & (t <= 0.40)
    y[rise] = height * np.sin((t[rise] - 0.30) / 0.10 * np.pi / 2)
    fall = (t > 0.40) & (t <= 0.52)
    y[fall] = height * np.cos((t[fall] - 0.40) / 0.12 * np.pi / 2) ** 1.4
    under = (t > 0.52) & (t <= 0.78)
    y[under] = -0.22 * height * np.sin((t[under] - 0.52) / 0.26 * np.pi)
    return x0 + t * length, y


def draw_mark(ax, ink, accent, x=0.0, y=0.0, s=1.0):
    r = 0.42 * s
    ax.add_patch(Circle((x, y), r, color=ink, zorder=3))
    # the hillock: a smooth taper from the soma into the axon
    w0, w1, x_start, x_end = 0.30 * s, 0.035 * s, x + 0.30 * s, x + 0.92 * s
    verts = [(x_start, y + w0), (x + 0.62 * s, y + 0.07 * s), (x_end - 0.12 * s, y + w1), (x_end, y + w1),
             (x_end, y - w1), (x_end - 0.12 * s, y - w1), (x + 0.62 * s, y - 0.07 * s), (x_start, y - w0),
             (x_start, y + w0)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), color=ink, lw=0, zorder=2))
    sx, sy = spike_xy(x_end - 0.01 * s, 1.15 * s, 0.62 * s)
    ax.plot(sx, y + sy, color=accent, lw=7.5 * s, solid_capstyle="round", solid_joinstyle="round", zorder=4)
    return x + 2.1 * s


def canvas(w, h, bg):
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100, facecolor=bg)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(bg); ax.axis("off")
    return fig, ax


def save(fig, name, transparent=False):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), transparent=transparent and ext == "png",
                    facecolor=fig.get_facecolor())
    plt.close(fig)


def logo(ink, name):
    fig, ax = canvas(600, 300, "none")
    draw_mark(ax, ink, ACCENT, 0, 0, 1)
    ax.set_xlim(-0.55, 2.2); ax.set_ylim(-0.7, 0.75); ax.set_aspect("equal")
    save(fig, name, transparent=True)


def banner(bg, ink, sub, name, w=1600, h=400, tagline=True):
    fig, ax = canvas(w, h, bg)
    ax.set_xlim(0, w / 100); ax.set_ylim(0, h / 100); ax.set_aspect("equal")
    cy = h / 200
    end = draw_mark(ax, ink, ACCENT, x=1.1, y=cy + (0.15 if tagline else 0), s=1.25)
    ax.text(end + 0.25, cy + (0.35 if tagline else 0.05), "hillock", color=ink, fontsize=96, fontweight="bold",
            family=FONT, va="center", ha="left")
    if tagline:
        ax.text(end + 0.3, cy - 0.75, "Field-standard neurotech workflows for Claude", color=sub, fontsize=27,
                family=FONT, va="center", ha="left")
    save(fig, name)


def avatar():
    fig, ax = canvas(500, 500, INK)
    ax.set_xlim(-1.55, 1.55); ax.set_ylim(-1.55, 1.55); ax.set_aspect("equal")
    draw_mark(ax, PAPER, ACCENT, x=-1.0, y=0.0, s=0.95)
    save(fig, "avatar")


def social():
    w, h = 1280, 640
    fig, ax = canvas(w, h, DARK_BG)
    ax.set_xlim(0, w / 100); ax.set_ylim(0, h / 100); ax.set_aspect("equal")
    end = draw_mark(ax, DARK_INK, ACCENT, x=1.4, y=3.95, s=1.3)
    ax.text(end + 0.25, 4.15, "hillock", color=DARK_INK, fontsize=100, fontweight="bold", family=FONT, va="center")
    ax.text(1.0, 2.35, "Field-standard neurotech workflows for Claude", color="#c9d1d9", fontsize=30, family=FONT)
    ax.text(1.0, 1.55, "EEG/MEG  ·  BCI decoding  ·  spike sorting  ·  real-time rigs  ·  neuromodulation  ·  devices",
            color="#8b949e", fontsize=19, family=FONT)
    save(fig, "social-preview")


def main():
    logo(INK, "logo")
    logo(DARK_INK, "logo-dark")
    banner(PAPER, INK, "#52514e", "banner-light")
    banner(DARK_BG, DARK_INK, "#9da7b3", "banner-dark")
    avatar()
    social()
    print("written to", OUT)


if __name__ == "__main__":
    main()
