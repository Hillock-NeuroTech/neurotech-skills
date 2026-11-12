import json, itertools
import numpy as np
from scipy import stats

new = np.load("acc_new.npy"); base = np.load("acc_baseline.npy")
d = new - base
n = len(d)
t = stats.ttest_rel(new, base)
w = stats.wilcoxon(new, base)
# exact sign-flip permutation test on paired differences (2^9 = 512 flips)
obs = d.mean()
perm = np.array([np.mean(d * np.array(s)) for s in itertools.product([1, -1], repeat=n)])
p_perm = np.mean(np.abs(perm) >= abs(obs) - 1e-12)
# bootstrap 95% CI of mean difference
rng = np.random.default_rng(0)
boot = np.array([rng.choice(d, n, replace=True).mean() for _ in range(10000)])
ci = np.percentile(boot, [2.5, 97.5])
tci = stats.t.interval(0.95, n - 1, loc=obs, scale=stats.sem(d))
dz = obs / d.std(ddof=1)
wins = int((d > 0).sum())
print(f"new {new.mean():.3f}±{new.std(ddof=1):.3f}, base {base.mean():.3f}±{base.std(ddof=1):.3f}")
print(f"diff {obs:.3f}, t-CI {tci}, boot CI {ci}, dz {dz:.2f}, wins {wins}/{n}")
print(f"paired t p={t.pvalue:.3f}, wilcoxon p={w.pvalue:.3f}, perm p={p_perm:.3f}")

sentence = (f"On a public 9-subject motor-imagery dataset, the new decoder reached a mean accuracy of "
            f"{new.mean()*100:.1f}% versus {base.mean()*100:.1f}% for the standard baseline "
            f"(mean paired difference +{obs*100:.1f} percentage points, 95% CI {tci[0]*100:.1f} to {tci[1]*100:.1f}; "
            f"better in {wins} of {n} subjects), but this difference was not statistically significant "
            f"(paired t-test p = {t.pvalue:.2f}; Wilcoxon signed-rank p = {w.pvalue:.2f}), so the two decoders "
            f"performed comparably.")
json.dump({"sentence": sentence, "claims_significant_improvement": False},
          open("answer.json", "w"), indent=2)
print(sentence)
