"""Unbiased test accuracy for the small MLP decoder.

The original train_nn.py chose the "best checkpoint" by evaluating on the test
set every epoch, then reported that maximum -> test-set leakage (optimistic).
Here the number of epochs is chosen with an inner validation split carved out
of the training data only; the held-out fold is scored exactly once.
Performance is estimated with repeated stratified 5-fold CV (nested selection).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS","1"); os.environ.setdefault("OPENBLAS_NUM_THREADS","1"); os.environ.setdefault("MKL_NUM_THREADS","1")
import json
import warnings
import numpy as np
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)

X = np.load("X.npy")
y = np.load("y.npy").astype(int)
MAX_EPOCHS = 150


def make_net(seed):
    return MLPClassifier(hidden_layer_sizes=(32,), learning_rate_init=0.01, random_state=seed)


def pick_epochs(Xtr, ytr, seed):
    """Inner CV on training data only to choose the number of epochs."""
    inner = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    curves = np.zeros(MAX_EPOCHS)
    for itr, iva in inner.split(Xtr, ytr):
        sc = StandardScaler().fit(Xtr[itr])
        a, b = sc.transform(Xtr[itr]), sc.transform(Xtr[iva])
        net = make_net(seed)
        for e in range(MAX_EPOCHS):
            net.partial_fit(a, ytr[itr], classes=[0, 1])
            curves[e] += net.score(b, ytr[iva])
    return int(np.argmax(curves)) + 1


def fit_eval(Xtr, ytr, Xte, yte, seed):
    n_ep = pick_epochs(Xtr, ytr, seed)
    sc = StandardScaler().fit(Xtr)
    net = make_net(seed)
    for _ in range(n_ep):
        net.partial_fit(sc.transform(Xtr), ytr, classes=[0, 1])
    return net.score(sc.transform(Xte), yte), n_ep


# 1) Original 70/30 split, but with epoch selection done without the test set
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
single_acc, single_ep = fit_eval(Xtr, ytr, Xte, yte, 0)
print("original split, honest epoch selection: acc=%.3f (epochs=%d)" % (single_acc, single_ep))

# 2) Repeated stratified 5-fold nested CV (main estimate)
outer = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=0)
accs = []
for k, (tr, te) in enumerate(outer.split(X, y)):
    acc, _ = fit_eval(X[tr], y[tr], X[te], y[te], k)
    accs.append(acc); print("fold", k, acc, flush=True)
accs = np.array(accs)
print("nested CV accuracy: mean=%.3f sd=%.3f (n=%d folds)" % (accs.mean(), accs.std(), len(accs)))

# 3) Chance-level check: binomial test of first-repeat pooled correct count vs 0.5
from scipy.stats import binomtest
n_correct = int(round(sum(a * 16 for a in accs[:5])))
print("binomial test vs chance (repeat 1, %d/80 correct): p=%.3f"
      % (n_correct, binomtest(n_correct, 80, 0.5, alternative="greater").pvalue))

with open("answer.json", "w") as f:
    json.dump({"test_accuracy": round(float(accs.mean()), 4)}, f, indent=2)
print(open("answer.json").read())
