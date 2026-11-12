"""Seizure-window classification with class balancing done INSIDE each CV training fold.

Oversampling before splitting would put exact duplicates of seizure windows in both
train and test folds, inflating the score. Here the minority class is randomly
oversampled (with replacement) only within each training fold; test folds are untouched.
"""
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score

X = np.load("X.npy")
y = np.load("y.npy").astype(int).ravel()
print("X", X.shape, "class counts", np.bincount(y))

def oversample(Xtr, ytr, rng):
    classes, counts = np.unique(ytr, return_counts=True)
    n_max = counts.max()
    idx = []
    for c, n in zip(classes, counts):
        ci = np.flatnonzero(ytr == c)
        idx.append(ci)
        if n < n_max:
            idx.append(rng.choice(ci, n_max - n, replace=True))
    idx = np.concatenate(idx)
    return Xtr[idx], ytr[idx]

scores, leaky_scores = [], []
for rep in range(5):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=rep)
    rng = np.random.default_rng(rep)
    for tr, te in skf.split(X, y):
        Xb, yb = oversample(X[tr], y[tr], rng)
        clf = RandomForestClassifier(n_estimators=300, random_state=rep, n_jobs=-1)
        clf.fit(Xb, yb)
        scores.append(balanced_accuracy_score(y[te], clf.predict(X[te])))

# For reference only: the leaky approach (oversample whole dataset, then CV)
rng = np.random.default_rng(0)
Xl, yl = oversample(X, y, rng)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
for tr, te in skf.split(Xl, yl):
    clf = RandomForestClassifier(n_estimators=300, random_state=0, n_jobs=-1).fit(Xl[tr], yl[tr])
    leaky_scores.append(balanced_accuracy_score(yl[te], clf.predict(Xl[te])))

ba = float(np.mean(scores))
print(f"Correct (oversample within train folds), 5x5 CV: {ba:.4f} +/- {np.std(scores):.4f}")
print(f"Leaky (oversample before CV), reference only:     {np.mean(leaky_scores):.4f}")
with open("answer.json", "w") as f:
    json.dump({"balanced_accuracy": round(ba, 4)}, f, indent=2)
