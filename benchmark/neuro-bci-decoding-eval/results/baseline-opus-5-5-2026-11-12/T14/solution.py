"""Subject-level permutation test for EEG diagnosis decoding.

cv.py uses segment-level StratifiedKFold: segments of the same subject land in
both train and test folds, so the classifier can identify subjects rather than
diagnosis (leakage). Diagnosis is a subject-level label, so:
  * CV must be grouped by subject (no subject in both train and test), and
  * the permutation null must shuffle diagnosis labels across subjects
    (keeping all segments of a subject together), not across segments.
"""
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_score

X = np.load("X.npy")
y = np.load("y.npy")
subject = np.load("subject.npy")

subjects = np.unique(subject)
subj_label = np.array([y[subject == s][0] for s in subjects])
assert all(len(np.unique(y[subject == s])) == 1 for s in subjects)

clf = LogisticRegression(max_iter=1000)
cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=0)


def score(labels):
    return cross_val_score(clf, X, labels, groups=subject, cv=cv).mean()


# Original (leaky) result for reference
leaky = cross_val_score(clf, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0)).mean()
observed = score(y)

n_perm = 1000
rng = np.random.default_rng(0)
null = np.empty(n_perm)
for i in range(n_perm):
    perm_lab = rng.permutation(subj_label)
    mapping = dict(zip(subjects, perm_lab))
    y_perm = np.array([mapping[s] for s in subject])
    null[i] = score(y_perm)

p = (np.sum(null >= observed) + 1) / (n_perm + 1)

print("leaky segment-level CV accuracy: %.3f" % leaky)
print("subject-grouped CV accuracy:     %.3f" % observed)
print("null mean %.3f, 95th pct %.3f" % (null.mean(), np.percentile(null, 95)))
print("p = %.4f (n_perm=%d)" % (p, n_perm))

with open("answer.json", "w") as f:
    json.dump({"p_value": float(p), "n_permutations": int(n_perm)}, f, indent=2)
