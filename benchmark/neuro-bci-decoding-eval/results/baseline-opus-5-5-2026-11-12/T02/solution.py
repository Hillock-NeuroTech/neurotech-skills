"""Trial-grouped cross-validation of a motor-imagery classifier.

Windows overlap heavily (1 s windows, 0.1 s step) and windows from the same
trial share signal, so splitting at the window level would leak information.
We therefore cross-validate with folds defined by trial (GroupKFold), keep all
preprocessing inside the pipeline, and score at the window level.
"""
import json
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedGroupKFold, GroupKFold, KFold, cross_val_score

X = np.load("X.npy")
y = np.load("y.npy")
trial = np.load("trial.npy")
t0 = np.load("window_start_s.npy")

print("X", X.shape, "classes", np.unique(y, return_counts=True))
print("trials", len(np.unique(trial)), "windows/trial", np.bincount(trial.astype(int)).max())
# check labels constant within trial
assert all(len(np.unique(y[trial == t])) == 1 for t in np.unique(trial))

clf = make_pipeline(StandardScaler(), LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto"))

cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=0)
scores = cross_val_score(clf, X, y, groups=trial, cv=cv)
acc = float(scores.mean())
print("Grouped-by-trial CV accuracy: %.3f +/- %.3f" % (acc, scores.std()))

# For reference only: leaky window-level CV (not reported)
leaky = cross_val_score(clf, X, y, cv=KFold(5, shuffle=True, random_state=0)).mean()
print("Leaky window-level KFold accuracy (NOT valid): %.3f" % leaky)

with open("answer.json", "w") as f:
    json.dump({"cross_validated_accuracy": round(acc, 4)}, f, indent=2)
