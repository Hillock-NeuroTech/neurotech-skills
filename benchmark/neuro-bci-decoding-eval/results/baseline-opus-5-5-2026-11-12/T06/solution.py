"""CSP (6 components) + LDA, 5-fold stratified CV on motor-imagery epochs.

CSP is fit inside each training fold (sklearn Pipeline) so no test-fold
information leaks into the spatial filters.
"""
import json
import os

import numpy as np
from mne.decoding import CSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

HERE = os.path.dirname(os.path.abspath(__file__))
X = np.load(os.path.join(HERE, "epochs.npy"))  # (40, 48, 150)
y = np.load(os.path.join(HERE, "y.npy")).astype(int)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


def make_pipe(reg=None):
    return Pipeline([
        ("csp", CSP(n_components=6, reg=reg, log=True, norm_trace=False)),
        ("lda", LinearDiscriminantAnalysis()),
    ])


# Primary: plain CSP + LDA as requested
scores = cross_val_score(make_pipe(None), X, y, cv=cv, scoring="accuracy")
print("CSP+LDA fold accuracies:", np.round(scores, 3))
print(f"CSP+LDA mean accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")

# Sensitivity check: 48 channels vs 32 training trials -> shrinkage CSP
scores_lw = cross_val_score(make_pipe("ledoit_wolf"), X, y, cv=cv, scoring="accuracy")
print(f"(check) Ledoit-Wolf CSP+LDA mean accuracy: {scores_lw.mean():.4f}")

# Repeated-CV stability of the primary estimate
rep = [cross_val_score(make_pipe(None), X, y,
                       cv=StratifiedKFold(5, shuffle=True, random_state=s)).mean()
       for s in range(10)]
print(f"(check) 10x repeated 5-fold mean: {np.mean(rep):.4f} (sd {np.std(rep):.4f})")

with open(os.path.join(HERE, "answer.json"), "w") as f:
    json.dump({"accuracy": float(scores.mean())}, f, indent=2)
