"""10-fold CV of CSP+LDA on motor-imagery epochs.

The cached features.npy were produced by fitting CSP (a supervised spatial
filter) on ALL epochs and labels before cross-validation, which leaks test-fold
label information into the features. Here CSP is refit inside each training
fold via a Pipeline. The leaky cached-feature number is also printed for
comparison.
"""
import json
import numpy as np
from mne.decoding import CSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline

X = np.load("raw/epochs.npy")
y = np.load("raw/y.npy")
cv = StratifiedKFold(10, shuffle=True, random_state=0)

# Leaky baseline: cached features (CSP fit on all data)
Xf = np.load("features.npy")
yf = np.load("labels.npy")
print("labels match raw:", np.array_equal(yf, y))
leaky = cross_val_score(LinearDiscriminantAnalysis(), Xf, yf, cv=cv).mean()
print("cached-feature (leaky) 10-fold accuracy: %.3f" % leaky)

# Correct: CSP fit within each training fold
pipe = make_pipeline(CSP(n_components=6, log=True), LinearDiscriminantAnalysis())
acc = cross_val_score(pipe, X, y, cv=cv)
print("per-fold:", np.round(acc, 3))
print("leak-free 10-fold accuracy: %.3f" % acc.mean())

json.dump({"accuracy_10fold": float(acc.mean())}, open("answer.json", "w"), indent=2)
