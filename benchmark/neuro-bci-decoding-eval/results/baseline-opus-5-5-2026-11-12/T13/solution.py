"""5-fold CV accuracy of a linear classifier with a 95% CI.

Choices:
- Classifier: standardization + L2 logistic regression inside a Pipeline, so
  scaling is fit only on training folds (no leakage).
- CV: StratifiedKFold(5, shuffle, fixed seed). Accuracy = pooled out-of-fold
  correct / N (each trial predicted exactly once).
- CI: Wilson score interval on the pooled count of correct out-of-fold
  predictions (k of N=100). A t-interval over the 5 fold accuracies is not used
  because fold scores are not independent (overlapping training sets) and n=5
  gives an unstable, often too-narrow interval.
- Sanity: chance level 0.5 (balanced classes); a label-permutation test is
  reported to check above-chance decoding. Repeated-CV spread is reported to
  show sensitivity to the fold split.
"""
import json
import numpy as np
from scipy.stats import norm
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score, RepeatedStratifiedKFold

X = np.load("X.npy")
y = np.load("y.npy")
N = len(y)

clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

pred = cross_val_predict(clf, X, y, cv=cv)
k = int((pred == y).sum())
acc = k / N

def wilson(k, n, alpha=0.05):
    z = norm.ppf(1 - alpha / 2)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half

lo, hi = wilson(k, N)

fold_acc = cross_val_score(clf, X, y, cv=cv)
rep = cross_val_score(clf, X, y, cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=0))
rng = np.random.default_rng(0)
n_perm = 500
perm_scores = np.array([(cross_val_predict(clf, X, yp, cv=cv) == yp).mean()
                        for yp in (rng.permutation(y) for _ in range(n_perm))])
pval = (1 + np.sum(perm_scores >= acc)) / (n_perm + 1)

print(f"Out-of-fold accuracy: {acc:.3f} ({k}/{N})")
print(f"Wilson 95% CI: [{lo:.3f}, {hi:.3f}]")
print("Per-fold accuracies:", np.round(fold_acc, 3))
print(f"Repeated 5-fold (20x) mean acc: {rep.reshape(20,5).mean(1).mean():.3f}, "
      f"range of repeat means: [{rep.reshape(20,5).mean(1).min():.3f}, {rep.reshape(20,5).mean(1).max():.3f}]")
print(f"Permutation test (500 perms): p = {pval:.4f}, null mean = {perm_scores.mean():.3f}")

answer = {
    "accuracy": round(float(acc), 4),
    "ci_low": round(float(lo), 4),
    "ci_high": round(float(hi), 4),
    "ci_method": (f"Wilson score 95% binomial interval on the pooled out-of-fold correct count "
                  f"({k}/{N}) from stratified 5-fold CV of standardized L2 logistic regression; "
                  "it reflects test-set sampling only, not training-set variability."),
}
with open("answer.json", "w") as f:
    json.dump(answer, f, indent=2)
print(json.dumps(answer, indent=2))
