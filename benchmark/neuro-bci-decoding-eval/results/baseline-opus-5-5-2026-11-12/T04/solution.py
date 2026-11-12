import json
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold

Xm, ym = np.load("X_mon.npy"), np.load("y_mon.npy")
Xt, yt = np.load("X_tue.npy"), np.load("y_tue.npy")
print(Xm.shape, Xt.shape, np.bincount(ym.astype(int)), np.bincount(yt.astype(int)))
print("mean shift between days (per feature):", np.round(Xt.mean(0) - Xm.mean(0), 2))

models = {
    "lda": lambda: make_pipeline(StandardScaler(), LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
    "logreg": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)),
}
cv = StratifiedKFold(5, shuffle=True, random_state=0)
res = {}
for name, mk in models.items():
    within_m = cross_val_score(mk(), Xm, ym, cv=cv).mean()
    within_t = cross_val_score(mk(), Xt, yt, cv=cv).mean()
    m2t = mk().fit(Xm, ym).score(Xt, yt)
    t2m = mk().fit(Xt, yt).score(Xm, ym)
    res[name] = dict(within_mon=within_m, within_tue=within_t, mon_to_tue=m2t, tue_to_mon=t2m,
                     cross=(m2t + t2m) / 2)
    print(name, {k: round(v, 3) for k, v in res[name].items()})

# The deployment scenario is "calibrate on one day, apply to a later day with a refitted cap",
# so the honest estimate is cross-session accuracy (no recalibration, no use of test-day labels
# or statistics). Within-session CV would be optimistic. Primary model: shrinkage LDA.
expected = float(res["lda"]["cross"])
print("expected accuracy on new day:", round(expected, 4))
json.dump({"expected_accuracy_new_day": round(expected, 4)}, open("answer.json", "w"), indent=2)
