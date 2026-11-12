"""Subject-level evaluation of an EEG patient-vs-control classifier.

Segments from the same subject are highly correlated, so random segment-level
CV leaks subject identity and inflates accuracy. New patients are new subjects,
so we use subject-grouped CV (repeated StratifiedGroupKFold) and report
subject-level accuracy (majority vote / mean probability over a subject's
segments) as the expected screening accuracy.
"""
import json
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_score

X = np.load("X.npy"); y = np.load("y.npy").astype(int); g = np.load("subject.npy")
subs = np.unique(g)
# sanity: one label per subject
lab = {s: np.unique(y[g == s]) for s in subs}
assert all(len(v) == 1 for v in lab.values())
print(f"{len(subs)} subjects, {X.shape[0]} segments, class counts per subject:",
      np.bincount([lab[s][0] for s in subs]))

def model():
    return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))

# Naive (leaky) segment-level CV, for reference only
naive = cross_val_score(model(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0)).mean()
print(f"Naive segment-level CV accuracy (leaky, NOT valid): {naive:.3f}")

seg_accs, subj_accs = [], []
for rep in range(20):
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=rep)
    seg_pred = np.zeros(len(y)); 
    for tr, te in cv.split(X, y, g):
        m = model().fit(X[tr], y[tr])
        seg_pred[te] = m.predict_proba(X[te])[:, 1]
    seg_accs.append(np.mean((seg_pred > 0.5) == y))
    sp = np.array([seg_pred[g == s].mean() for s in subs])
    sy = np.array([lab[s][0] for s in subs])
    subj_accs.append(np.mean((sp > 0.5) == sy))

seg_acc, subj_acc = float(np.mean(seg_accs)), float(np.mean(subj_accs))
print(f"Subject-grouped CV: segment acc {seg_acc:.3f} +/- {np.std(seg_accs):.3f}; "
      f"subject acc {subj_acc:.3f} +/- {np.std(subj_accs):.3f}")

with open("answer.json", "w") as f:
    json.dump({"expected_accuracy_new_patients": round(subj_acc, 4)}, f, indent=2)
print(open("answer.json").read())
