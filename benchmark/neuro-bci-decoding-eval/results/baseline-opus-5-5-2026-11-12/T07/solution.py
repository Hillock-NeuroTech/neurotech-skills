"""Select 10 most discriminative features and estimate accuracy without selection leakage.

Feature selection (ANOVA F) is placed inside the cross-validation pipeline so each
fold selects features using only its training trials. The reported feature list is
from a final fit on all 60 trials (for deployment); the accuracy is the nested CV
estimate, which is what that deployed decoder can be expected to achieve.
"""
import json
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold, cross_val_score, permutation_test_score

X = np.load("X.npy"); y = np.load("y.npy")
print("X", X.shape, "y", y.shape, "classes", np.unique(y, return_counts=True))
assert np.isfinite(X).all()

K = 10
def make_pipe():
    return make_pipeline(StandardScaler(), SelectKBest(f_classif, k=K),
                         LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto"))

# Nested (selection inside folds) accuracy, repeated 5-fold CV
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=0)
scores = cross_val_score(make_pipe(), X, y, cv=cv, scoring="accuracy")
acc = float(scores.mean())
print(f"Nested CV accuracy: {acc:.3f} +/- {scores.std():.3f}")

# Permutation test (selection repeated per permutation)
score, perm, p = permutation_test_score(make_pipe(), X, y,
    cv=StratifiedKFold(5, shuffle=True, random_state=0), n_permutations=500, random_state=0)
print(f"Perm test: score={score:.3f}, null mean={perm.mean():.3f}, p={p:.4f}")

# Leaky estimate for comparison only (selection on all data, then CV) -- NOT reported
sel_all = SelectKBest(f_classif, k=K).fit(X, y)
idx = np.sort(np.argsort(sel_all.scores_)[::-1][:K])
leaky = cross_val_score(make_pipeline(StandardScaler(), LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
                        X[:, idx], y, cv=cv).mean()
print(f"Leaky (selection-before-CV) accuracy, for reference only: {leaky:.3f}")

# Selection stability across folds
from collections import Counter
cnt = Counter()
for tr, te in cv.split(X, y):
    s = SelectKBest(f_classif, k=K).fit(X[tr], y[tr])
    cnt.update(np.argsort(s.scores_)[::-1][:K].tolist())
print("Most frequently selected (feature: count/100):", cnt.most_common(15))
print("Final selected features (fit on all data):", idx.tolist(),
      "-> (channel, band):", [(int(i)//8, int(i)%8) for i in idx])
print("F-scores:", np.round(sel_all.scores_[idx], 2).tolist(), "p:", np.round(sel_all.pvalues_[idx], 5).tolist())

json.dump({"selected_features": [int(i) for i in idx], "accuracy": round(acc, 4)},
          open("answer.json", "w"), indent=2)
print(open("answer.json").read())
