"""Logistic regression decoder with leakage-free CV.

dataio.load_data() augments (jitters) every trial BEFORE cross-validation, so
noisy copies of each test trial land in the training folds -> inflated accuracy.
Here CV splits the 60 original trials; augmentation is applied to training folds only.
"""
import json
import numpy as np
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from dataio import _augment

X = np.load("data/X.npy")
y = np.load("data/y.npy")
print("X", X.shape, "y", np.bincount(y.astype(int)))

clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
cv = StratifiedKFold(5, shuffle=True, random_state=0)

# Plain CV on original trials
acc_plain = cross_val_score(clf, X, y, cv=cv).mean()

# Augmentation inside training folds only
accs = []
for tr, te in cv.split(X, y):
    Xtr, ytr = _augment(X[tr], y[tr])
    m = clone(clf).fit(Xtr, ytr)
    accs.append(m.score(X[te], y[te]))
acc_aug = float(np.mean(accs))

# For reference: the leaky protocol of the original train.py
from dataio import load_data
Xa, ya = load_data()
acc_leaky = cross_val_score(clf, Xa, ya, cv=cv).mean()

# Repeated CV for a stable estimate (plain, original trials)
rep = [cross_val_score(clf, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=s)).mean() for s in range(20)]

print("plain CV: %.3f | train-fold-aug CV: %.3f | leaky (original) CV: %.3f | repeated plain: %.3f +- %.3f"
      % (acc_plain, acc_aug, acc_leaky, np.mean(rep), np.std(rep)))
json.dump({"accuracy": round(float(acc_aug), 4)}, open("answer.json", "w"))
