"""Run the lab pipeline as-is, then the leakage-free version.

analysis.py fits SelectKBest on ALL samples (labels included) before CV, so the
held-out folds influence which features are kept -> optimistic accuracy,
especially with n=50, p=5000. The fix: put selection inside a Pipeline so it is
refit on each training fold. A permutation test gives chance-level reference.
"""
import json
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import (StratifiedKFold, cross_val_score,
                                     RepeatedStratifiedKFold, permutation_test_score)
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC

X = np.load("X.npy")
y = np.load("y.npy")

# 1) Original (leaky) pipeline, exactly as in analysis.py
Xs = SelectKBest(f_classif, k=50).fit(X, y).transform(X)
cv = StratifiedKFold(5, shuffle=True, random_state=0)
leaky = cross_val_score(SVC(kernel="linear"), Xs, y, cv=cv).mean()
print("original analysis.py (selection before CV): %.3f" % leaky)

# 2) Correct: selection inside each training fold
pipe = make_pipeline(SelectKBest(f_classif, k=50), SVC(kernel="linear"))
honest = cross_val_score(pipe, X, y, cv=cv).mean()
print("selection inside CV, same split:            %.3f" % honest)

rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=0)
rep = cross_val_score(pipe, X, y, cv=rcv)
print("selection inside CV, 10x5 repeated:         %.3f +/- %.3f" % (rep.mean(), rep.std()))

score, perm, p = permutation_test_score(pipe, X, y, cv=cv, n_permutations=200,
                                        random_state=0, n_jobs=-1)
print("permutation test: score=%.3f, null mean=%.3f, p=%.3f" % (score, perm.mean(), p))

json.dump({"accuracy_for_report": round(float(rep.mean()), 3)},
          open("answer.json", "w"), indent=2)
print(open("answer.json").read())
