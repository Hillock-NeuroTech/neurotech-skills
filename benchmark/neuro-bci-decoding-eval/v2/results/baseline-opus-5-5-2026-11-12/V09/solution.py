"""LOSO accuracy with cross-site duplicate participants merged.

README: some volunteers took part at both sites with unlinked IDs. Site-A and
site-B IDs are matched on (age, sex, handedness) from participants.csv; every
site-A ID has exactly one site-B match, confirmed by subject-mean feature
correlation (~0.9+ vs <0.62 for any other candidate). Folds are therefore
leave-one-PERSON-out (12 folds) so no person is in both train and test.
"""
import json
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneGroupOut, cross_val_predict

X = np.load("X.npy"); y = np.load("y.npy"); sid = np.load("subject_id.npy")
p = pd.read_csv("participants.csv")
ids = p.subject_id.tolist()  # index i <-> S{i+1:02d}
key = p.age.astype(str) + p.sex + p.handedness
person = {}
for k, grp in p.groupby(key):
    for s in grp.subject_id: person[s] = grp.subject_id.iloc[0]

# verify with feature fingerprints
M = np.array([X[sid == i].mean(0) for i in range(24)])
C = np.corrcoef(M)
for i in range(12):
    j = 12 + int(np.argmax(C[i, 12:]))
    assert person[ids[i]] == person[ids[j]], (ids[i], ids[j])

pid_names = sorted(set(person.values()))
groups = np.array([pid_names.index(person[ids[i]]) for i in sid])
for g in np.unique(groups):
    assert len(np.unique(y[groups == g])) == 1
print("unique persons:", len(np.unique(groups)))

clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))
pred = cross_val_predict(clf, X, y, groups=groups, cv=LeaveOneGroupOut())
acc = float((pred == y).mean())
print("leave-one-person-out segment accuracy:", acc)

# subject-level (majority vote) for reference
subj_acc = np.mean([np.round(pred[groups == g].mean()) == y[groups == g][0]
                    for g in np.unique(groups)])
print("person-level majority-vote accuracy:", subj_acc)

# naive 24-ID LOSO (leaky) for comparison only
naive = cross_val_predict(clf, X, y, groups=sid, cv=LeaveOneGroupOut())
print("naive 24-ID LOSO (leaky, not reported):", float((naive == y).mean()))

json.dump({"loso_accuracy": round(acc, 4)}, open("answer.json", "w"), indent=2)
