#!/usr/bin/env python3
"""Render assets/demo.gif: a terminal replay of leakage_safe_eval.py run twice
on the same synthetic recording, once split by trial and once by session.

    python3 brand/make_demo.py      # needs numpy, scipy, scikit-learn, pillow

The commands really run (in a temporary folder) and the lines shown are
copied from their output; the JSON is trimmed to four fields per run.
"""
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugins/neuro-decoding/skills/neuro-bci-decoding-eval/scripts/leakage_safe_eval.py")
KEEP = ("split", "balanced_accuracy", "binomial_chance_threshold_p05", "permutation_p")
W, H, PAD, LINE = 980, 530, 28, 26
BG, BAR, FG, DIM, PROMPT, GOOD, BAD, NOTE = ("#0d1117", "#161b22", "#e6edf3", "#7d8590", "#ff6a3d",
                                             "#3fb950", "#f85149", "#d2a8ff")


def font(size):
    for f in ("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/SFNSMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def run_commands():
    tmp = tempfile.mkdtemp()
    try:
        shutil.copy(SCRIPT, tmp)
        rng = np.random.default_rng(0)
        n, per = 12, 30
        g = np.repeat(np.arange(n), per)
        y = np.repeat(np.arange(n) % 2, per)
        X = rng.normal(0, 1, (n * per, 16)) + rng.normal(0, 1.5, (n, 16))[g]
        for name, arr in (("X", X), ("y", y), ("sessions", g)):
            np.save(os.path.join(tmp, f"{name}.npy"), arr)
        cmds = ["python3 leakage_safe_eval.py --X X.npy --y y.npy --n-perm 100",
                "python3 leakage_safe_eval.py --X X.npy --y y.npy --groups sessions.npy --n-perm 100"]
        out = []
        for c in cmds:
            res = subprocess.run([sys.executable] + c.split()[1:], cwd=tmp, capture_output=True, text=True, check=True)
            lines = [ln.rstrip(",") for ln in res.stdout.splitlines() if any(f'"{k}"' in ln for k in KEEP)]
            out.append((c, lines))
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class Term:
    def __init__(self):
        self.f, self.fs = font(17), font(13)
        self.rows = []      # list of [(text, color), ...]
        self.frames, self.durations = [], []

    def render(self, cursor=False):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W, 38], fill=BAR)
        for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            d.ellipse([18 + i * 22, 13, 30 + i * 22, 25], fill=c)
        d.text((W / 2, 19), "hillock · neuro-bci-decoding-eval", font=self.fs, fill=DIM, anchor="mm")
        y = 38 + PAD - 6
        for row in self.rows[-20:]:
            x = PAD
            for text, col in row:
                d.text((x, y), text, font=self.f, fill=col)
                x += d.textlength(text, font=self.f)
            last_x = x
            y += LINE
        if cursor:
            d.rectangle([last_x + 2, y - LINE + 3, last_x + 11, y - 4], fill=FG)
        return im

    def snap(self, ms, cursor=False):
        self.frames.append(self.render(cursor)); self.durations.append(ms)

    def type(self, prefix, text, color=FG, step=3):
        self.rows.append(prefix + [("", color)])
        for i in range(0, len(text) + 1, step):
            self.rows[-1] = prefix + [(text[:i], color)]
            self.snap(45, cursor=True)
        self.rows[-1] = prefix + [(text, color)]
        self.snap(450, cursor=True)

    def show(self, row, ms=140):
        self.rows.append(row); self.snap(ms)


def colour_line(line, chance):
    key, _, val = line.strip().partition(": ")
    col = FG
    if key == '"balanced_accuracy"':
        col = GOOD if float(val) > chance else BAD
    return [("  " + key + ": ", DIM), (val, col)]


def main():
    runs = run_commands()
    t = Term()
    t.show([("# same recording, same decoder, two ways to split it", DIM)], 700)
    for (cmd, lines), note in zip(runs, ("# split by trial", "# split by session")):
        t.show([(note, NOTE)], 350)
        t.type([("$ ", PROMPT)], cmd)
        chance = next(float(ln.split(": ")[1]) for ln in lines if "chance" in ln)
        for ln in lines:
            t.show(colour_line(ln, chance))
        t.show([("", FG)], 900)
    acc = [next(ln.split(": ")[1] for ln in lines if "balanced" in ln) for _, lines in runs]
    pv = [next(ln.split(": ")[1] for ln in lines if "permutation_p" in ln) for _, lines in runs]
    t.show([(f"# trial split: {float(acc[0]):.2f}, p = {float(pv[0]):.2f}. Looks like a finding.", GOOD)], 900)
    t.show([(f"# session split: {float(acc[1]):.2f}, p = {float(pv[1]):.2f}. The decoder learned the session.", BAD)], 4000)
    path = os.path.join(ROOT, "assets", "demo.gif")
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=32) for f in t.frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=t.durations, loop=0, optimize=True)
    print(f"wrote {path}: {len(pal)} frames, {sum(t.durations) / 1000:.1f} s, {os.path.getsize(path) // 1024} KB")
    for c, lines in runs:
        print(c); print("\n".join(lines))


if __name__ == "__main__":
    main()
