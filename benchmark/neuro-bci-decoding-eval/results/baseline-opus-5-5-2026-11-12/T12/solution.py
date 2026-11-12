"""Spindle detector evaluation: imbalanced binary labels (20% spindle).
Accuracy is misleading under imbalance (all-zero baseline = 0.80), so we report
balanced accuracy as the headline and check chance-level with a permutation test."""
import json
import numpy as np
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, f1_score,
                             cohen_kappa_score, matthews_corrcoef, confusion_matrix,
                             precision_score, recall_score)

y_true = np.load("y_true.npy").astype(int)
y_pred = np.load("y_pred.npy").astype(int)

tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
prev = y_true.mean()
m = dict(
    n=len(y_true), prevalence=prev, tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp),
    accuracy=accuracy_score(y_true, y_pred),
    majority_baseline_accuracy=max(prev, 1 - prev),
    balanced_accuracy=balanced_accuracy_score(y_true, y_pred),
    sensitivity=recall_score(y_true, y_pred, zero_division=0),
    specificity=tn / (tn + fp),
    precision=precision_score(y_true, y_pred, zero_division=0),
    f1=f1_score(y_true, y_pred, zero_division=0),
    kappa=cohen_kappa_score(y_true, y_pred),
    mcc=matthews_corrcoef(y_true, y_pred),
)

def bacc(t, p):
    t = t.astype(bool); p = p.astype(bool)
    return 0.5 * ((p & t).sum() / t.sum() + (~p & ~t).sum() / (~t).sum())

# Permutation test on balanced accuracy (chance = 0.5)
rng = np.random.default_rng(0)
null = np.array([bacc(y_true, rng.permutation(y_pred)) for _ in range(5000)])
m["perm_p_balanced_acc"] = (np.sum(null >= m["balanced_accuracy"]) + 1) / (len(null) + 1)

# Bootstrap 95% CI
boot = []
for _ in range(5000):
    i = rng.integers(0, len(y_true), len(y_true))
    if y_true[i].min() == y_true[i].max():
        continue
    boot.append(bacc(y_true[i], y_pred[i]))
m["balanced_acc_ci95"] = list(np.percentile(boot, [2.5, 97.5]))

for k, v in m.items():
    print(f"{k}: {v}")

useful = bool(m["balanced_accuracy"] > 0.5 and m["perm_p_balanced_acc"] < 0.05
              and m["balanced_acc_ci95"][0] > 0.5)
answer = {"headline_metric": "balanced_accuracy",
          "headline_value": round(float(m["balanced_accuracy"]), 4),
          "detector_is_useful": useful}
with open("answer.json", "w") as f:
    json.dump(answer, f, indent=2)
print(answer)
