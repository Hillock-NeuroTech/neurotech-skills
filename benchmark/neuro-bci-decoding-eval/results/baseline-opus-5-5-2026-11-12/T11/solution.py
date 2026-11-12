"""Test whether held-out decoding accuracy exceeds chance (50%, two balanced classes).

The decoder was trained on separate data and evaluated once on 40 independent
held-out trials, so the number of correct trials under H0 follows
Binomial(n=40, p=0.5). We use an exact one-sided binomial test
(H1: accuracy > chance).
"""
import json
import numpy as np
from scipy.stats import binomtest

y_true = np.load("y_true.npy", allow_pickle=False)
y_pred = np.load("y_pred.npy", allow_pickle=False)
assert y_true.shape == y_pred.shape

n = len(y_true)
k = int((y_true == y_pred).sum())
chance = 1.0 / len(np.unique(y_true))  # 0.5, balanced two-class
acc = k / n

res = binomtest(k, n, p=chance, alternative="greater")
p = float(res.pvalue)
ci = res.proportion_ci(confidence_level=0.95, method="exact")

print(f"n={n}, correct={k}, accuracy={acc:.3f}, chance={chance}")
print(f"class counts true={np.bincount(y_true)}, pred={np.bincount(y_pred)}")
print(f"one-sided exact binomial p={p:.4f}; 95% CI [{ci.low:.3f}, {ci.high:.3f}]")
# minimum correct needed for p<0.05
from scipy.stats import binom
kmin = next(j for j in range(n + 1) if binom.sf(j - 1, n, chance) < 0.05)
print(f"need >= {kmin}/{n} correct ({kmin/n:.3f}) for p<0.05")

with open("answer.json", "w") as f:
    json.dump({"accuracy": acc, "p_value": p,
               "above_chance_significant": bool(p < 0.05)}, f, indent=2)
