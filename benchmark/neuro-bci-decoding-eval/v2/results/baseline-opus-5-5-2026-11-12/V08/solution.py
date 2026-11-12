"""Selection-aware evaluation of the 'best of 40' P300 decoder.

The logged 0.781 (svm_lin|last10) is the max over 40 configs evaluated on the
same 32 trials / same folds -> optimistically biased (winner's curse).
We (1) reproduce the logged CV, (2) estimate the accuracy of the whole
"pick the best of 40" procedure with nested CV, and (3) build a permutation
null for the max-over-40 CV accuracy to get a selection-corrected p-value.
"""
import json, time, warnings
import numpy as np
from scipy.stats import binomtest
from sklearn.model_selection import StratifiedKFold
from sklearn.base import clone
from configs import CONFIGS, cols

warnings.filterwarnings("ignore")
X = np.load("X.npy"); y = np.load("y.npy")
n = len(y)
t0 = time.time()

def cv_scores_all(Xa, ya, cv):
    """Mean CV accuracy for each of the 40 configs on (Xa, ya)."""
    splits = list(cv.split(Xa, ya))
    out = np.zeros(len(CONFIGS))
    for i, (desc, make) in enumerate(CONFIGS):
        c = cols(desc); acc = []
        for tr, te in splits:
            m = make().fit(Xa[tr][:, c], ya[tr])
            acc.append((m.predict(Xa[te][:, c]) == ya[te]).mean())
        out[i] = np.mean(acc)
    return out

# 1) reproduce the log
cv0 = StratifiedKFold(5, shuffle=True, random_state=0)
naive = cv_scores_all(X, y, cv0)
best = int(np.argmax(naive))
print("best logged config:", CONFIGS[best][0], round(naive[best], 3))

# 2) nested CV of the selection procedure, repeated over outer splits
nested = []
for rep in range(5):
    outer = StratifiedKFold(5, shuffle=True, random_state=100 + rep)
    correct = 0
    for tr, te in outer.split(X, y):
        inner = StratifiedKFold(4, shuffle=True, random_state=rep)
        s = cv_scores_all(X[tr], y[tr], inner)
        k = int(np.argmax(s)); desc, make = CONFIGS[k]; c = cols(desc)
        m = make().fit(X[tr][:, c], y[tr])
        correct += (m.predict(X[te][:, c]) == y[te]).sum()
    nested.append(correct / n)
    print(f"nested rep {rep}: {nested[-1]:.3f}  ({time.time()-t0:.0f}s)")
nested_acc = float(np.mean(nested))

# 3) permutation null for max-over-40 CV accuracy (same folds as the log)
rng = np.random.default_rng(0)
n_perm = 200
null_max = []
for p in range(n_perm):
    yp = rng.permutation(y)
    null_max.append(cv_scores_all(X, yp, cv0).max())
    if time.time() - t0 > 240: break
null_max = np.array(null_max)
p_sel = (1 + np.sum(null_max >= naive[best])) / (1 + len(null_max))
p_naive_binom = binomtest(int(round(naive[best] * n)), n, 0.5, alternative="greater").pvalue
print(f"null max-of-40 mean={null_max.mean():.3f}, 95th pct={np.percentile(null_max,95):.3f}, "
      f"perms={len(null_max)}, selection-corrected p={p_sel:.3f}, naive binomial p={p_naive_binom:.4f}")
print("total time", round(time.time() - t0), "s")

res = dict(best=CONFIGS[best][0], best_cv=float(naive[best]), nested=nested,
           nested_mean=nested_acc, null_mean=float(null_max.mean()),
           null_95=float(np.percentile(null_max, 95)), n_perm=len(null_max),
           p_sel=float(p_sel), p_naive=float(p_naive_binom))
json.dump(res, open("results_detail.json", "w"), indent=2)
