#!/usr/bin/env python3
"""Draw the Hillock brand assets.

    python3 brand/make_brand.py        # needs numpy, scipy, matplotlib

Avatar: a sagittal brain drawn as fibres, fanning from the brainstem to the
cortex the way tractography shows them, with one fibre firing in orange.
Logo: fibres gathering through the hillock into one axon, which fires.
Writes PNG (and SVG for the logo) to assets/brand/. Seeds are fixed, so the
output is the same on every run.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import FontProperties
from scipy.interpolate import splev, splprep

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "brand")

NIGHT, PAPER = "#0b0810", "#f7f3ee"
ORANGE = "#ff7a45"
INK_DARK, INK_LIGHT = "#ece6df", "#1a1420"
MUTED_DARK, MUTED_LIGHT = "#8a8394", "#6b6470"
WARM = LinearSegmentedColormap.from_list("warm", ["#f6cfa8", "#ee9fb4", "#c79be8", "#9fb3f0"])
WARM_ON_PAPER = LinearSegmentedColormap.from_list("warm_p", ["#d9824f", "#cf5f86", "#8f5fc4", "#5f74c9"])
MONO_FONTS = ["/System/Library/Fonts/SFNSMono.ttf", "/System/Library/Fonts/Menlo.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
MONO = FontProperties(fname=next((f for f in MONO_FONTS if os.path.exists(f)), None)) \
    if any(os.path.exists(f) for f in MONO_FONTS) else FontProperties(family="monospace")

# sagittal outline, facing left: frontal pole, over the top, occipital pole, temporal lobe underneath
OUTLINE = np.array([(-1.25, 0.02), (-1.17, 0.42), (-0.86, 0.78), (-0.35, 0.98), (0.2, 0.99), (0.7, 0.83),
                    (1.07, 0.5), (1.26, 0.08), (1.2, -0.17), (0.98, -0.26), (0.62, -0.27), (0.38, -0.42),
                    (0.05, -0.56), (-0.32, -0.57), (-0.62, -0.42), (-0.74, -0.22), (-0.86, -0.17), (-1.12, -0.2)])
STEM = np.array([0.12, -0.36])
CEREBELLUM = np.array([0.8, -0.46])


# ---------------------------------------------------------------- geometry
def cortex(n=1600, seed=3):
    """Outline with gyri: rounded crowns separated by narrow sulci."""
    tck, _ = splprep([np.r_[OUTLINE[:, 0], OUTLINE[0, 0]], np.r_[OUTLINE[:, 1], OUTLINE[0, 1]]], s=0, per=True)
    s = np.linspace(0, 1, n, endpoint=False)
    x, y = splev(s, tck)
    dx, dy = splev(s, tck, der=1)
    nx, ny = dy / np.hypot(dx, dy), -dx / np.hypot(dx, dy)
    rng = np.random.default_rng(seed)
    depth = np.zeros(n)
    k = 0
    while k < n:
        w = int(rng.integers(34, 62))
        u = np.arange(min(w, n - k)) / w
        depth[k:k + len(u)] = 0.036 * (np.abs(np.sin(np.pi * u)) ** 0.7) - 0.026      # rounded crown, narrow sulcus
        k += w
    depth[y < -0.15] *= 0.35                     # quieter along the base
    depth = np.convolve(np.r_[depth[-4:], depth, depth[:4]], np.ones(9) / 9, "valid")
    return x + nx * depth, y + ny * depth, nx, ny


def bez(p0, p1, p2, p3, n=70):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def wobble(c, rng, amp):
    """Low-frequency hand tremor along a polyline."""
    if amp == 0 or len(c) < 3:
        return c
    d = np.gradient(c, axis=0)
    nrm = np.c_[-d[:, 1], d[:, 0]] / (np.hypot(d[:, 0], d[:, 1])[:, None] + 1e-12)
    t = np.linspace(0, 1, len(c))
    w = amp * (np.sin(2 * np.pi * (t * rng.uniform(1, 2.5) + rng.uniform(0, 1))) * np.sin(np.pi * t))
    return c + nrm * w[:, None]


def brain_lines(n=1100, seed=3, tremor=0.006):
    """Return (segments, colour values 0-1, firing fibre)."""
    rng = np.random.default_rng(seed)
    cx, cy, nx, ny = cortex(seed=seed)
    segs, vals = [], []
    val = lambda x: float(np.clip(0.5 - x / 2.6, 0, 1))

    # projection fibres: brainstem → cortex
    for _ in range(n):
        i = int(rng.integers(0, len(cx)))
        if cy[i] < -0.2 and cx[i] > 0.3:
            continue
        end = np.array([cx[i], cy[i]]) - np.array([nx[i], ny[i]]) * rng.uniform(0.0, 0.05)
        st = STEM + rng.normal(0, [0.06, 0.03])
        mid = st + (end - st) * 0.45
        perp = np.array([-(end - st)[1], (end - st)[0]]) * (0.16 * np.sign(end[0] - st[0]) + rng.normal(0, 0.05))
        segs.append(wobble(bez(st, st + [rng.normal(0, 0.05), 0.3], mid + perp, end), rng, tremor))
        vals.append(val(cx[i]) + rng.normal(0, 0.04))

    # cortical ribbon: a few lines following the gyri, slightly inside
    for depth in (0.004, 0.02):
        segs.append(np.c_[np.r_[cx, cx[0]] - np.r_[nx, nx[0]] * depth, np.r_[cy, cy[0]] - np.r_[ny, ny[0]] * depth])
        vals.append(None)                        # coloured along its length below

    # short association fibres just under the cortex
    for _ in range(n // 4):
        i = int(rng.integers(0, len(cx)))
        w = int(rng.integers(30, 70))
        idx = (i + np.arange(w)) % len(cx)
        sag = 0.05 + 0.05 * np.sin(np.linspace(0, np.pi, w))
        segs.append(np.c_[cx[idx] - nx[idx] * sag, cy[idx] - ny[idx] * sag])
        vals.append(val(cx[i]))

    # brainstem
    for _ in range(n // 5):
        st = STEM + rng.normal(0, [0.05, 0.02])
        e = np.array([0.34, -0.98]) + rng.normal(0, [0.05, 0.01])
        segs.append(wobble(bez(st, st + [0.0, -0.25], e + [-0.06, 0.2], e, 40), rng, tremor))
        vals.append(0.05 + rng.uniform(0, 0.08))

    # cerebellum: fibres from the peduncle fanning to a folded edge
    t = np.linspace(-np.pi, np.pi, 700)
    rx, ry = 0.32, 0.2
    folia = 1 + 0.035 * np.abs(np.sin(t * 13))
    ex, ey = CEREBELLUM[0] + rx * folia * np.cos(t), CEREBELLUM[1] + ry * folia * np.sin(t)
    root = CEREBELLUM + [-0.2, 0.02]
    for _ in range(n // 4):
        j = int(rng.integers(0, len(t)))
        if np.cos(t[j]) < -0.55:
            continue
        end = np.array([ex[j], ey[j]]) * 0.995 + CEREBELLUM * 0.005
        c1 = root + (end - root) * 0.35 + rng.normal(0, 0.02, 2)
        segs.append(wobble(bez(root, c1, end - (end - CEREBELLUM) * 0.25, end, 40), rng, tremor * 0.5))
        vals.append(0.82)
    for r in (1.0, 0.97):
        segs.append(np.c_[CEREBELLUM[0] + (ex - CEREBELLUM[0]) * r, CEREBELLUM[1] + (ey - CEREBELLUM[1]) * r])
        vals.append(0.82)

    k = int(np.argmin(np.hypot(cx + 0.15, cy - 1.0)))   # the firing fibre, to motor cortex
    top = np.array([cx[k], cy[k]])
    fire = bez(STEM, STEM + [0, 0.35], top * 0.5 + [0.08, 0], top * 0.985)
    return segs, vals, (cx, cy), fire


def draw_brain(ax, cmap=WARM, n=1100, lw=0.32, alpha=0.6, glow=0.04, fire_lw=1.0, seed=3, tremor=0.006):
    segs, vals, (cx, cy), fire = brain_lines(n, seed, tremor)
    lines, cols = [], []
    for s, v in zip(segs, vals):
        if v is None:                            # ribbon: split into chunks so colour follows position
            for a in range(0, len(s) - 1, 20):
                part = s[a:a + 21]
                lines.append(part); cols.append(cmap(float(np.clip(0.5 - part[:, 0].mean() / 2.6, 0, 1))))
        else:
            lines.append(s); cols.append(cmap(float(np.clip(v, 0, 1))))
    if glow:
        ax.add_collection(LineCollection(lines, colors=cols, linewidths=lw * 7, alpha=glow))
    ax.add_collection(LineCollection(lines, colors=cols, linewidths=lw, alpha=alpha))
    ax.plot(fire[:, 0], fire[:, 1], color=ORANGE, lw=fire_lw * 3, alpha=0.18, solid_capstyle="round")
    ax.plot(fire[:, 0], fire[:, 1], color=ORANGE, lw=fire_lw, solid_capstyle="round")


# ---------------------------------------------------------------- logo
def spike(x0, length, h):
    t = np.linspace(0, 1, 300)
    y = np.zeros_like(t)
    r = (t > .35) & (t <= .43); y[r] = h * np.sin((t[r] - .35) / .08 * np.pi / 2)
    f = (t > .43) & (t <= .53); y[f] = h * np.cos((t[f] - .43) / .10 * np.pi / 2) ** 1.5
    u = (t > .53) & (t <= .75); y[u] = -.18 * h * np.sin((t[u] - .53) / .22 * np.pi)
    return x0 + t * length, y


def draw_mark(ax, x, y, s, ink, lw=1.1, n=9):
    """Fibres gather through the hillock into one axon, which fires. Returns the right edge."""
    segs = []
    for k in np.linspace(-1, 1, n):
        p0 = np.array([x, y + 0.42 * s * k]); p3 = np.array([x + 0.95 * s, y])
        segs.append(bez(p0, p0 + [0.45 * s, 0], p3 - [0.35 * s, 0], p3, 80))
    ax.add_collection(LineCollection(segs, colors=ink, linewidths=lw, capstyle="round"))
    sx, sy = spike(x + 0.95 * s, 1.1 * s, 0.5 * s)
    ax.plot(sx, y + sy, color=ORANGE, lw=lw * 1.6, solid_capstyle="round", solid_joinstyle="round")
    return x + 2.05 * s


def wordmark(ax, x, y, size, ink):
    ax.text(x, y, "hillock", fontproperties=MONO, fontsize=size, color=ink, va="center", ha="left")


# ---------------------------------------------------------------- files
def canvas(w, h, bg, dpi=100):
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi, facecolor=bg)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(bg); ax.axis("off")
    return fig, ax


def save(fig, name, exts=("png",), transparent=False):
    os.makedirs(OUT, exist_ok=True)
    for ext in exts:
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), facecolor="none" if transparent else fig.get_facecolor(),
                    transparent=transparent)
    plt.close(fig)


def avatar(size=1000):
    fig, ax = canvas(size, size, NIGHT)
    k = size / 1000
    draw_brain(ax, n=700, lw=0.75 * k, alpha=0.62, glow=0.05, fire_lw=2.6 * k, tremor=0.004)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.46, 1.54); ax.set_aspect("equal")
    save(fig, "avatar")


def logo(ink, name):
    fig, ax = canvas(900, 300, "none")
    end = draw_mark(ax, 0.2, 0, 1.0, ink, lw=2.2)
    wordmark(ax, end + 0.22, 0.0, 58, ink)
    ax.set_xlim(0, 6.8); ax.set_ylim(-1.1, 1.1); ax.set_aspect("equal")
    save(fig, name, exts=("png", "svg"), transparent=True)


def mark_only(ink, name):
    fig, ax = canvas(400, 260, "none")
    draw_mark(ax, 0.1, 0, 1.0, ink, lw=2.6)
    ax.set_xlim(0, 2.25); ax.set_ylim(-0.73, 0.73); ax.set_aspect("equal")
    save(fig, name, exts=("png", "svg"), transparent=True)


def banner(dark, w=1800, h=480, tagline="field-standard neurotech workflows for claude", name=None):
    bg, ink, muted, cmap = (NIGHT, INK_DARK, MUTED_DARK, WARM) if dark else (PAPER, INK_LIGHT, MUTED_LIGHT, WARM_ON_PAPER)
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100, facecolor=bg)
    bx = fig.add_axes([1 - (h * 1.08) / w - 0.03, 0.02, (h * 1.08) / w, 0.96]); bx.axis("off"); bx.set_facecolor("none")
    draw_brain(bx, cmap=cmap, n=900, lw=0.38, alpha=0.5 if dark else 0.42, glow=0.035 if dark else 0.0, fire_lw=1.3)
    bx.set_xlim(-1.35, 1.35); bx.set_ylim(-1.05, 1.12); bx.set_aspect("equal")
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none"); ax.axis("off")
    W, H = w / 100, h / 100
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    end = draw_mark(ax, 1.0, H * 0.58, 0.9, ink, lw=1.5)
    wordmark(ax, end + 0.2, H * 0.58, 56, ink)
    ax.text(1.02, H * 0.3, tagline, fontproperties=MONO, fontsize=16, color=muted)
    save(fig, name or ("banner-dark" if dark else "banner-light"))


def social():
    w, h = 1280, 640
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100, facecolor=NIGHT)
    bx = fig.add_axes([0.52, 0.06, 0.46, 0.88]); bx.axis("off"); bx.set_facecolor("none")
    draw_brain(bx, n=900, lw=0.42, alpha=0.55, glow=0.04, fire_lw=1.4)
    bx.set_xlim(-1.35, 1.35); bx.set_ylim(-1.05, 1.12); bx.set_aspect("equal")
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none"); ax.axis("off"); ax.set_xlim(0, 12.8); ax.set_ylim(0, 6.4)
    end = draw_mark(ax, 0.8, 3.75, 0.75, INK_DARK, lw=1.5)
    wordmark(ax, end + 0.18, 3.75, 50, INK_DARK)
    ax.text(0.82, 2.75, "neurotech workflows for claude", fontproperties=MONO, fontsize=17, color=MUTED_DARK)
    ax.text(0.82, 2.2, "eeg · bci · spike sorting · real time\nneuromodulation · devices", fontproperties=MONO,
            fontsize=13, color="#5f5868", va="top", linespacing=1.7)
    save(fig, "social-preview")


def main():
    for old in ("logo.svg", "logo-dark.svg", "avatar.svg", "banner-light.svg", "banner-dark.svg", "social-preview.svg"):
        p = os.path.join(OUT, old)
        if os.path.exists(p):
            os.remove(p)
    avatar()
    logo(INK_LIGHT, "logo"); logo(INK_DARK, "logo-dark")
    mark_only(INK_LIGHT, "mark"); mark_only(INK_DARK, "mark-dark")
    banner(True); banner(False)
    social()
    print("written to", OUT)


if __name__ == "__main__":
    main()
