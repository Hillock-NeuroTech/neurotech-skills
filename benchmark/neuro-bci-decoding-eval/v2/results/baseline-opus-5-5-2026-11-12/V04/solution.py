import json
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (StratifiedKFold, StratifiedGroupKFold,
                                     LeaveOneGroupOut, cross_val_score, cross_val_predict)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X = np.load("X.npy")
y = np.load("y.npy")
subject = np.load("subject.npy")

# Feature selection goes INSIDE the pipeline so it is refit on each training fold only
# (the original code selected features on all data, including test subjects -> a second leak).
def make_clf():
    return make_pipeline(SelectKBest(f_classif, k=30), StandardScaler(),
                         LogisticRegression(max_iter=1000))

# Original (leaky) for reference
X_red = SelectKBest(f_classif, k=30).fit_transform(X, y)
orig = cross_val_score(make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
                       X_red, y, cv=StratifiedKFold(5, shuffle=True, random_state=0)).mean()
print("original leaky accuracy: %.3f" % orig)

# Primary corrected analysis: subject-grouped CV (no participant in both train and test),
# repeated over several shuffles; segment-level accuracy pooled over folds.
accs = []
for seed in range(10):
    cv = StratifiedGroupKFold(5, shuffle=True, random_state=seed)
    pred = cross_val_predict(make_clf(), X, y, groups=subject, cv=cv)
    accs.append(np.mean(pred == y))
accs = np.array(accs)
print("grouped 5-fold segment accuracy: %.3f +/- %.3f" % (accs.mean(), accs.std()))

# Sensitivity: leave-one-subject-out, segment-level and participant-level (majority vote)
pred = cross_val_predict(make_clf(), X, y, groups=subject, cv=LeaveOneGroupOut())
loso_seg = np.mean(pred == y)
subs = np.unique(subject)
subj_pred = np.array([np.round(pred[subject == s].mean()) for s in subs])
subj_true = np.array([y[subject == s][0] for s in subs])
loso_subj = np.mean(subj_pred == subj_true)
print("LOSO segment accuracy: %.3f; participant-level (majority vote): %.3f" % (loso_seg, loso_subj))

json.dump({"corrected_accuracy": round(float(accs.mean()), 4)}, open("answer.json", "w"), indent=2)
print(open("answer.json").read())
