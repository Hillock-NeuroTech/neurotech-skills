"""Tune an SVM (kernel, C, gamma) and estimate the accuracy of the tuned model.

With only 40 trials, the best inner-CV score of a wide grid search is optimistically
biased (selection on noise). The reported accuracy therefore comes from NESTED
cross-validation: hyperparameters are tuned inside each outer training fold only
(scaling also fit inside the pipeline), and the outer test folds are never seen
during tuning. A label-permutation test on the full nested procedure gives a p-value.
"""
import json
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

import numpy as np
from sklearn.model_selection import (GridSearchCV, StratifiedKFold, RepeatedStratifiedKFold,
                                     cross_val_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

HERE = Path(__file__).resolve().parent
X = np.load(HERE / "X.npy")
y = np.load(HERE / "y.npy")

pipe = Pipeline([("scale", StandardScaler()), ("svc", SVC(max_iter=200000))])
Cs = np.logspace(-3, 3, 7)
gammas = np.logspace(-4, 1, 6)
param_grid = [
    {"svc__kernel": ["linear"], "svc__C": Cs},
    {"svc__kernel": ["rbf"], "svc__C": Cs, "svc__gamma": gammas},
    {"svc__kernel": ["poly"], "svc__C": Cs, "svc__gamma": gammas, "svc__degree": [2, 3]},
    {"svc__kernel": ["sigmoid"], "svc__C": Cs, "svc__gamma": gammas},
]


def make_search(seed):
    inner = StratifiedKFold(5, shuffle=True, random_state=seed)
    return GridSearchCV(pipe, param_grid, cv=inner, scoring="accuracy", n_jobs=1)


# Non-nested (optimistic) score, for reference only
full = make_search(0).fit(X, y)
print(f"Best params (full data): {full.best_params_}")
print(f"Best inner-CV accuracy (optimistically biased): {full.best_score_:.3f}")

# Nested CV: repeated outer stratified 5-fold
outer = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=42)
nested_scores = cross_val_score(make_search(1), X, y, cv=outer, scoring="accuracy")
nested_acc = float(nested_scores.mean())
print(f"Nested CV accuracy: {nested_acc:.3f} +/- {nested_scores.std():.3f} "
      f"(over {len(nested_scores)} outer folds)")

with open(HERE / "answer.json", "w") as f:
    json.dump({"accuracy": round(nested_acc, 4)}, f, indent=2)
print(json.dumps({"accuracy": round(nested_acc, 4)}), flush=True)

# Permutation test of the whole nested procedure (single outer 5-fold to keep it fast)
rng = np.random.default_rng(0)
outer1 = StratifiedKFold(5, shuffle=True, random_state=42)
obs = cross_val_score(make_search(1), X, y, cv=outer1).mean()
n_perm = 100
null = np.array([cross_val_score(make_search(1), X, rng.permutation(y), cv=outer1).mean()
                 for _ in range(n_perm)])
p = (np.sum(null >= obs) + 1) / (n_perm + 1)
print(f"Permutation test (single 5-fold nested): observed {obs:.3f}, "
      f"null mean {null.mean():.3f}, p = {p:.3f}")

with open(HERE / "answer.json", "w") as f:
    json.dump({"accuracy": round(nested_acc, 4)}, f, indent=2)
print(json.dumps({"accuracy": round(nested_acc, 4)}))
