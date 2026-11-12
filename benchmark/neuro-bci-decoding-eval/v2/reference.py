"""Check every v2 trap: the naive path must be inflated, the careful path at chance.

Usage: python reference.py [tasks_dir]
"""
import csv
import sys
import warnings
from pathlib import Path

import numpy as np
from mne.decoding import CSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (GroupKFold, LeaveOneGroupOut, StratifiedGroupKFold,
                                     StratifiedKFold, cross_val_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")
T = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "tasks")
L = lambda *p: np.load(T.joinpath(*p))
skf = lambda k=5, s=0: StratifiedKFold(k, shuffle=True, random_state=s)
sgkf = lambda s=0: StratifiedGroupKFold(5, shuffle=True, random_state=s)
svm = lambda: make_pipeline(StandardScaler(), SVC())
lr = lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
rows = {}

# V01
X, y, g = L("V01", "data", "X.npy"), L("V01", "data", "y.npy"), L("V01", "data", "subject.npy")
rows["V01"] = (cross_val_score(svm(), X, y, cv=skf()).mean(),
               np.mean([cross_val_score(svm(), X, y, groups=g, cv=sgkf(s)).mean() for s in range(3)]))
# V02
X, y = L("V02", "raw", "epochs.npy"), L("V02", "raw", "y.npy")
F = CSP(6, log=True).fit_transform(X, y)
rows["V02"] = (cross_val_score(LDA(), F, y, cv=skf(10)).mean(),
               cross_val_score(make_pipeline(CSP(6, log=True), LDA()), X, y, cv=skf(10)).mean())
# V03
X, y = L("V03", "X.npy"), L("V03", "y.npy")
Xs = SelectKBest(f_classif, k=50).fit_transform(X, y)
rows["V03"] = (cross_val_score(SVC(kernel="linear"), Xs, y, cv=skf()).mean(),
               np.mean([cross_val_score(make_pipeline(SelectKBest(f_classif, k=50), SVC(kernel="linear")),
                                        X, y, cv=skf(5, s)).mean() for s in range(3)]))
# V04: fix only the subject split vs fix both
X, y, g = L("V04", "X.npy"), L("V04", "y.npy"), L("V04", "subject.npy")
Xr = SelectKBest(f_classif, k=30).fit_transform(X, y)
half = np.mean([cross_val_score(lr(), Xr, y, groups=g, cv=sgkf(s)).mean() for s in range(3)])
full = np.mean([cross_val_score(make_pipeline(SelectKBest(f_classif, k=30), StandardScaler(),
                                              LogisticRegression(max_iter=1000)),
                                X, y, groups=g, cv=sgkf(s)).mean() for s in range(3)])
rows["V04"] = (half, full)
# V05
X, y, tr = L("V05", "X.npy"), L("V05", "y.npy"), L("V05", "trial.npy")
rf = lambda: RandomForestClassifier(100, random_state=0, n_jobs=1)
rows["V05"] = (cross_val_score(rf(), X, y, groups=np.arange(len(X)) // 10, cv=GroupKFold(5)).mean(),
               cross_val_score(rf(), X, y, groups=tr, cv=GroupKFold(5)).mean())
# V06: shuffled CV vs time-residualised features in blocked CV
X, y, tm = L("V06", "X.npy"), L("V06", "choice.npy"), L("V06", "trial_time_min.npy")
naive = cross_val_score(lr(), X, y, cv=skf()).mean()
B = np.c_[np.ones_like(tm), tm, tm ** 2, np.sin(np.pi * tm / 60)]
Xres = X - B @ np.linalg.lstsq(B, X, rcond=None)[0]
from sklearn.metrics import balanced_accuracy_score  # noqa: E402
from sklearn.model_selection import cross_val_predict  # noqa: E402
careful = balanced_accuracy_score(y, cross_val_predict(lr(), Xres, y, cv=skf()))
rows["V06"] = (naive, careful)
# V07
X, y = L("V07", "data", "X.npy"), L("V07", "data", "y.npy")
rng = np.random.default_rng(0)
Xa = np.concatenate([X] + [X + rng.normal(0, 0.05, X.shape) for _ in range(4)])
ya = np.tile(y, 5)
rows["V07"] = (cross_val_score(lr(), Xa, ya, cv=skf()).mean(),
               np.mean([cross_val_score(lr(), X, y, cv=skf(5, s)).mean() for s in range(5)]))
# V08: best logged config vs nested selection
sys.path.insert(0, str(T / "V08"))
from configs import CONFIGS, cols  # noqa: E402
X, y = L("V08", "X.npy"), L("V08", "y.npy")
log = list(csv.DictReader(open(T / "V08" / "experiments.csv")))
best = max(float(r["cv_accuracy"]) for r in log)
outer = []
for s in range(3):
    for trn, te in skf(5, s + 10).split(X, y):
        inner = {i: cross_val_score(m(), X[trn][:, cols(d)], y[trn], cv=skf(5, s)).mean()
                 for i, (d, m) in enumerate(CONFIGS)}
        b = max(inner, key=inner.get)
        d, m = CONFIGS[b]
        outer.append(m().fit(X[trn][:, cols(d)], y[trn]).score(X[te][:, cols(d)], y[te]))
rows["V08"] = (best, np.mean(outer))
# V09: LOSO by ID vs leave-one-person-out
X, y, sid = L("V09", "X.npy"), L("V09", "y.npy"), L("V09", "subject_id.npy")
p = list(csv.DictReader(open(T / "V09" / "participants.csv")))
key = {int(r["subject_id"][1:]) - 1: (r["age"], r["sex"], r["handedness"]) for r in p}
keys = sorted(set(key.values()))
person = np.array([keys.index(key[i]) for i in sid])
print("V09 people found from demographics:", len(keys))
rows["V09"] = (cross_val_score(lr(), X, y, groups=sid, cv=LeaveOneGroupOut()).mean(),
               cross_val_score(lr(), X, y, groups=person, cv=LeaveOneGroupOut()).mean())
# V10
r = list(csv.reader(open(T / "V10" / "features.csv")))
head, body = r[0], np.array(r[1:], float)
y = body[:, -1].astype(int)
Xall = body[:, 1:-1]
names = head[1:-1]
eeg = [i for i, n in enumerate(names) if n != "epoch_len_ms"]
gb = lambda: GradientBoostingClassifier(random_state=0)
rows["V10"] = (cross_val_score(gb(), Xall, y, cv=skf()).mean(),
               cross_val_score(gb(), Xall[:, eeg], y, cv=skf()).mean())

print(f"{'task':5} {'naive':>7} {'careful':>8}")
for k, (a, b) in rows.items():
    print(f"{k:5} {a:7.3f} {b:8.3f}")
