"""Learning curve + CV accuracy with trial-level grouping.

The original make_groups (blocks of 10 consecutive windows) does not align with
trial boundaries (31 windows per trial), so overlapping windows of one trial
land in different folds -> leakage. Here groups = trial id (trial.npy), and the
learning curve subsamples whole training trials (not windows) per fold.
"""
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold
from utils import make_groups

cfg = json.load(open("config.json"))
X = np.load("X.npy"); y = np.load("y.npy"); trial = np.load("trial.npy")
rng = np.random.default_rng(0)

def clf():
    return RandomForestClassifier(200, random_state=0, n_jobs=-1)

cv = StratifiedGroupKFold(cfg["n_splits"], shuffle=True, random_state=0)
splits = list(cv.split(X, y, groups=trial))

fracs = [0.2, 0.4, 0.6, 0.8, 1.0]
curve = {f: [] for f in fracs}
nwin = {f: [] for f in fracs}
for tr, te in splits:
    tr_trials = np.unique(trial[tr])
    # stratify trial subsampling by class
    lab = {t: y[trial == t][0] for t in tr_trials}
    perm = {c: rng.permutation([t for t in tr_trials if lab[t] == c]) for c in (0, 1)}
    for f in fracs:
        keep = np.concatenate([p[:max(1, int(round(f * len(p))))] for p in perm.values()])
        m = np.isin(trial, keep) & np.isin(np.arange(len(X)), tr)
        model = clf().fit(X[m], y[m])
        curve[f].append(model.score(X[te], y[te]))
        nwin[f].append(m.sum())

print("n_train_windows  accuracy (mean +- sd over folds)")
for f in fracs:
    print("%6d  %.3f +- %.3f" % (np.mean(nwin[f]), np.mean(curve[f]), np.std(curve[f])))

# for reference: original leaky grouping
from sklearn.model_selection import GroupKFold, cross_val_score
leaky = cross_val_score(clf(), X, y, groups=make_groups(len(X), cfg["group_size"]),
                        cv=GroupKFold(cfg["n_splits"])).mean()
print("original (leaky) group_size=10 accuracy: %.3f" % leaky)

full = float(np.mean(curve[1.0]))
print("trial-grouped CV accuracy at full size: %.3f" % full)
json.dump({"cv_accuracy_full": round(full, 4)}, open("answer.json", "w"), indent=2)
