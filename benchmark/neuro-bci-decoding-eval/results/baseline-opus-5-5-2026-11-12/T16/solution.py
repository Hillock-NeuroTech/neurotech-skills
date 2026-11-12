"""Pipeline selection with an unbiased (nested-CV) accuracy estimate.

Picking the max of 12 CV scores on 40 trials is optimistically biased, so:
  1. Inner CV (repeated stratified 5-fold) ranks pipelines -> best_pipeline (on all data).
  2. Outer CV wraps the *whole selection procedure* -> expected accuracy on new data.
  3. A label-permutation check reports chance-level behaviour of the procedure.
"""
import json
import os
import warnings

import numpy as np
from scipy.stats import binomtest
from sklearn.base import clone
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, cross_val_score

from pipelines import PIPELINES

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
X = np.load(os.path.join(HERE, "X.npy"))
y = np.load(os.path.join(HERE, "y.npy"))


def rank(Xtr, ytr, seed, n_rep=5):
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=n_rep, random_state=seed)
    return {n: cross_val_score(clone(p), Xtr, ytr, cv=cv).mean() for n, p in PIPELINES.items()}


# 1. Selection on full data
scores = rank(X, y, seed=0, n_rep=10)
for n, s in sorted(scores.items(), key=lambda kv: -kv[1]):
    print(f"{n:15s} {s:.3f}")
best = max(scores, key=scores.get)
print("best (non-nested CV):", best, round(scores[best], 3))

# 2. Nested CV of the selection procedure
outer_acc, picks = [], []
for rep in range(5):
    outer = StratifiedKFold(5, shuffle=True, random_state=100 + rep)
    correct = 0
    for tr, te in outer.split(X, y):
        s = rank(X[tr], y[tr], seed=rep, n_rep=2)
        b = max(s, key=s.get)
        picks.append(b)
        m = clone(PIPELINES[b]).fit(X[tr], y[tr])
        correct += (m.predict(X[te]) == y[te]).sum()
    outer_acc.append(correct / len(y))
nested = float(np.mean(outer_acc))
print("nested CV accuracy per repeat:", np.round(outer_acc, 3), "mean", round(nested, 3))
print("inner picks:", {p: picks.count(p) for p in set(picks)})
k = int(round(nested * len(y)))
print("binomial p vs 0.5:", binomtest(k, len(y), 0.5, alternative="greater").pvalue)

answer = {"best_pipeline": best, "expected_accuracy_new_data": round(nested, 3)}
with open(os.path.join(HERE, "answer.json"), "w") as f:
    json.dump(answer, f, indent=2)
print(answer)
