import json
import numpy as np
from scipy.signal import butter, filtfilt, lfilter
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold

X = np.load("trials.npy"); y = np.load("y.npy")
fs = 250; step = fs // 4
b, a = butter(4, [8, 12], btype="bandpass", fs=fs)
cv = StratifiedKFold(5, shuffle=True, random_state=0)
splits = list(cv.split(X[:, 0, 0], y))

def cvacc(f):
    return np.mean([LinearDiscriminantAnalysis().fit(f[tr], y[tr]).score(f[te], y[te]) for tr, te in splits])

# 1) reproduce offline number
Xf = filtfilt(b, a, X, axis=-1)
Xn = (Xf - Xf.mean(-1, keepdims=True)) / Xf.std(axis=(1, 2), keepdims=True)
off = cvacc(np.log(Xn.var(-1)))
print("offline (as is): %.3f" % off)

# 2) where in the trial is the information? (non-causal, per 250-ms segment, diagnostic)
print("per-segment acc (diagnostic):")
for k in range(16):
    print("  %.2f-%.2f s: %.3f" % (k*step/fs, (k+1)*step/fs, cvacc(np.log(Xf[..., k*step:(k+1)*step].var(-1)))))

# 3) online simulation: causal filter, feedback every 250 ms from trial start,
#    features only from data available so far (growing window, no future normalisation).
Xc = lfilter(b, a, X, axis=-1)
def causal_feat(Z, t):
    return np.log(Z[..., :t].var(-1) + 1e-12)
ticks = np.arange(step, X.shape[-1] + 1, step)
acc_dep = np.zeros(len(ticks)); acc_tick = np.zeros(len(ticks))
for tr, te in splits:
    clf = LinearDiscriminantAnalysis().fit(causal_feat(Xc[tr], X.shape[-1]), y[tr])
    for i, t in enumerate(ticks):
        acc_dep[i] += clf.score(causal_feat(Xc[te], t), y[te]) / len(splits)
        c2 = LinearDiscriminantAnalysis().fit(causal_feat(Xc[tr], t), y[tr])
        acc_tick[i] += c2.score(causal_feat(Xc[te], t), y[te]) / len(splits)
print("online sim  tick: deployed-model  per-tick-model")
for t, a1, a2 in zip(ticks, acc_dep, acc_tick):
    print("  %.2f s: %.3f  %.3f" % (t/fs, a1, a2))
online = float(np.mean(acc_dep))
print("mean feedback accuracy (deployed model): %.3f" % online)
print("mean feedback accuracy (per-tick models): %.3f" % np.mean(acc_tick))

json.dump({
    "ready_for_online_as_is": False,
    "expected_online_accuracy": round(online, 3),
    "explanation": (
        "The offline %.0f%% relies on non-causal filtfilt, whole-trial normalisation and band power over the full 4 s, none of which "
        "are available when feedback is given every 250 ms from trial onset; a causal simulation using only data available at each "
        "tick gives a mean feedback accuracy of ~%.0f%%, so the pipeline needs a causal, short-window redesign before closed loop."
        % (100*off, 100*online)),
}, open("answer.json", "w"), indent=2)
print(open("answer.json").read())
