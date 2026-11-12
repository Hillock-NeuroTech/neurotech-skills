"""Decoding free left/right choice from pre-movement EEG, controlling for slow drift.

Both the EEG features and the choice base rate drift strongly over the session
(features correlate |r| up to 0.97 with time; P(right) rises from ~0.2 to ~0.9).
Shuffled K-fold CV lets a classifier read "time in session" from the features
and so predict the choice via the drift alone. We therefore:
  1. report naive shuffled K-fold (inflated) for reference,
  2. a time-only baseline (how much the drift alone buys),
  3. features detrended against time (polynomial fit inside each training fold),
     plus time-matched controls, evaluated with contiguous blocked CV, and
  4. a circular-shift permutation null that preserves autocorrelation.
"""
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, KFold, cross_val_score

rng = np.random.default_rng(0)
X = np.load("X.npy")
y = np.load("choice.npy").astype(int)
t = np.load("trial_time_min.npy")
n = len(y)
clf = lambda: make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))

# 1. naive shuffled CV
naive = cross_val_score(clf(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0)).mean()

# 2. time-only baseline (shuffled CV) -- drift alone
T = np.column_stack([t, t ** 2, t ** 3])
time_only = cross_val_score(clf(), T, y, cv=StratifiedKFold(5, shuffle=True, random_state=0)).mean()


def detrend_fit(Xtr, ttr, deg=3):
    V = np.vander(ttr, deg + 1)
    B, *_ = np.linalg.lstsq(V, Xtr, rcond=None)
    return B


def detrend_apply(Xs, ts, B, deg=3):
    return Xs - np.vander(ts, deg + 1) @ B


def eval_detrended(yy, shuffle_cv=True, deg=3, add_time=True, n_splits=5):
    """Accuracy of EEG features after removing slow time trends; optionally
    compare against a time-only model to get the EEG *increment*."""
    cv = (StratifiedKFold(n_splits, shuffle=True, random_state=0) if shuffle_cv
          else KFold(n_splits, shuffle=False))
    accs, accs_t = [], []
    for tr, te in cv.split(X, yy):
        B = detrend_fit(X[tr], t[tr], deg)
        Xtr, Xte = detrend_apply(X[tr], t[tr], B, deg), detrend_apply(X[te], t[te], B, deg)
        if add_time:
            Xtr = np.column_stack([Xtr, T[tr]]); Xte = np.column_stack([Xte, T[te]])
        m = clf().fit(Xtr, yy[tr]); accs.append(m.score(Xte, yy[te]))
        mt = clf().fit(T[tr], yy[tr]); accs_t.append(mt.score(T[te], yy[te]))
    return float(np.mean(accs)), float(np.mean(accs_t))


det_shuf, det_shuf_time = eval_detrended(y, shuffle_cv=True)
det_shuf_eeg_only, _ = eval_detrended(y, shuffle_cv=True, add_time=False)

# Within-session-segment decoding: balanced accuracy of detrended EEG inside 6
# 10-minute windows (removes base-rate drift), leave-one-out-ish via 5-fold.
from sklearn.metrics import balanced_accuracy_score
bal = []
for w in range(6):
    idx = np.where((t >= 10 * w) & (t < 10 * (w + 1) + (1e-9 if w == 5 else 0)))[0]
    yy, XX, tt = y[idx], X[idx], t[idx]
    if min(np.bincount(yy, minlength=2)) < 5:
        continue
    pred = np.zeros_like(yy)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(XX, yy):
        B = detrend_fit(XX[tr], tt[tr], 1)
        m = clf().fit(detrend_apply(XX[tr], tt[tr], B, 1), yy[tr])
        pred[te] = m.predict(detrend_apply(XX[te], tt[te], B, 1))
    bal.append(balanced_accuracy_score(yy, pred))
within_bal = float(np.mean(bal))

# Circular-shift null for naive and detrended accuracy (preserves label autocorrelation)
null_naive, null_det = [], []
for _ in range(100):
    s = rng.integers(30, n - 30)
    ys = np.roll(y, s)
    null_naive.append(cross_val_score(clf(), X, ys, cv=StratifiedKFold(5, shuffle=True, random_state=0)).mean())
    null_det.append(eval_detrended(ys, shuffle_cv=True)[0])
null_naive, null_det = np.array(null_naive), np.array(null_det)
p_naive = (1 + np.sum(null_naive >= naive)) / (1 + len(null_naive))
p_det = (1 + np.sum(null_det >= det_shuf)) / (1 + len(null_det))

res = dict(naive_shuffled_cv=naive, time_only=time_only,
           detrended_eeg_plus_time=det_shuf, time_only_same_folds=det_shuf_time,
           detrended_eeg_only=det_shuf_eeg_only,
           within_window_balanced_acc=within_bal, within_window_each=bal,
           null_naive_mean=float(null_naive.mean()), p_naive_circshift=float(p_naive),
           null_det_mean=float(null_det.mean()), p_det_circshift=float(p_det))
for k, v in res.items():
    print(k, v)
json.dump(res, open("results_detail.json", "w"), indent=1, default=float)
