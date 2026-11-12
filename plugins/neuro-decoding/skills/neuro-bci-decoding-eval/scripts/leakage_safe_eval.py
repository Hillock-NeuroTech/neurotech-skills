"""Group-aware decoder evaluation with chance level and permutation test.

CLI:
  python leakage_safe_eval.py --X X.npy --y y.npy [--groups g.npy]
         [--model lda|logreg|svm] [--n-splits 5] [--n-perm 200] [--seed 0]

Import:
  from leakage_safe_eval import evaluate
  evaluate(pipeline, X, y, groups=None, n_perm=200)

Every fitted step must live inside `pipeline`; this script only guarantees
that whole groups stay on one side of each split and that permutations
respect the group structure.
"""
import argparse
import json

import numpy as np
from scipy import stats
from sklearn.base import clone
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

MODELS = {
    "lda": lambda: make_pipeline(StandardScaler(), LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
    "logreg": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
    "svm": lambda: make_pipeline(StandardScaler(), SVC(kernel="linear")),
}


def _splitter(groups, n_splits, seed):
    if groups is None:
        return StratifiedKFold(n_splits, shuffle=True, random_state=seed)
    return StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed)


def _oof_predict(pipe, X, y, groups, n_splits, seed):
    pred = np.empty_like(y)
    for tr, te in _splitter(groups, n_splits, seed).split(X, y, groups):
        pred[te] = clone(pipe).fit(X[tr], y[tr]).predict(X[te])
    return pred


def _permute(y, groups, rng):
    """Permute labels at the group level when labels are constant within groups,
    otherwise permute within each group."""
    if groups is None:
        return rng.permutation(y)
    ug = np.unique(groups)
    const = all(len(np.unique(y[groups == g])) == 1 for g in ug)
    out = y.copy()
    if const:
        lab = np.array([y[groups == g][0] for g in ug])
        for g, l in zip(ug, rng.permutation(lab)):
            out[groups == g] = l
    else:
        for g in ug:
            idx = np.where(groups == g)[0]
            out[idx] = rng.permutation(y[idx])
    return out


def evaluate(pipe, X, y, groups=None, n_splits=5, n_perm=200, seed=0):
    y = np.asarray(y)
    groups = None if groups is None else np.asarray(groups)
    n_groups = None if groups is None else len(np.unique(groups))
    n_splits = min(n_splits, n_groups) if n_groups else n_splits
    pred = _oof_predict(pipe, X, y, groups, n_splits, seed)
    acc = accuracy_score(y, pred)
    bacc = balanced_accuracy_score(y, pred)
    k = len(np.unique(y))
    n = len(y)
    majority = np.max(np.bincount(np.unique(y, return_inverse=True)[1])) / n
    # binomial threshold assumes independent test items: use the number of groups if grouped
    n_ind = n_groups if n_groups else n
    thr = stats.binom.ppf(0.95, n_ind, 1 / k) / n_ind
    rng = np.random.default_rng(seed)
    null = [balanced_accuracy_score(yp, _oof_predict(pipe, X, yp, groups, n_splits, seed))
            for yp in (_permute(y, groups, rng) for _ in range(n_perm))]
    p = (1 + np.sum(np.array(null) >= bacc)) / (n_perm + 1) if n_perm else None
    return {
        "split": f"{'StratifiedGroupKFold' if groups is not None else 'StratifiedKFold'}({n_splits})",
        "n_samples": n, "n_groups": n_groups, "n_classes": k,
        "accuracy": round(acc, 4), "balanced_accuracy": round(bacc, 4),
        "majority_baseline": round(majority, 4),
        "binomial_chance_threshold_p05": round(thr, 4),
        "binomial_n_used": n_ind,
        "permutation_p": None if p is None else round(p, 4),
        "permutation_null_mean": round(float(np.mean(null)), 4) if n_perm else None,
        "n_permutations": n_perm,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--X", required=True)
    ap.add_argument("--y", required=True)
    ap.add_argument("--groups")
    ap.add_argument("--model", default="lda", choices=MODELS)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    X = np.load(a.X)
    X = X.reshape(len(X), -1)
    y = np.load(a.y)
    g = np.load(a.groups) if a.groups else None
    print(json.dumps(evaluate(MODELS[a.model](), X, y, g, a.n_splits, a.n_perm, a.seed), indent=2))


if __name__ == "__main__":
    main()
