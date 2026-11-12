---
name: neuro-foundation-model-eval
description: Fairly evaluate pretrained EEG/iEEG "foundation" models (LaBraM, BIOT, BENDR, EEGPT, CBraMod and similar) and self-supervised encoders against simple baselines. Use whenever the user fine-tunes or linear-probes a pretrained neural-signal model, compares it to classical pipelines, or claims gains from pretraining.
---

# Foundation-model evaluation for neural signals

Pretrained EEG models are often compared against weak baselines, on
splits that leak, or on data seen during pretraining. A fair comparison
holds everything fixed except the model.

## 1. Check for pretraining overlap

List the pretraining corpora of the model (from its paper or card). If the
downstream dataset, or recordings of the same people, are in the
pretraining set, results are contaminated. Prefer datasets clearly outside
pretraining, or say plainly that overlap exists.

## 2. Same data, same split, same budget

- Use subject-wise splits (see `neuro-bci-decoding-eval`) identical for every
  method, ideally published folds.
- Match preprocessing to each model's expected input (sampling rate,
  channel set, units, window length) and document resampling or channel
  mapping, since mismatches silently hurt the pretrained model.
- Give baselines the same tuning effort and the same labelled data amount.

## 3. Baselines that must appear

1. Classical pipeline suited to the task: band power + LDA/logistic, or
   Riemannian tangent space (pyRiemann) for motor imagery/ERP.
2. A compact supervised CNN trained from scratch (EEGNet or ShallowConvNet
   via braindecode).
3. The pretrained model, linear probe.
4. The pretrained model, full fine-tune.

## 4. Measure what pretraining should buy

- **Label efficiency**: performance vs number of labelled subjects or
  trials (for example 1, 5, 10, 25, 100%). Pretraining should help most
  at low labels.
- **Transfer**: new dataset or device not seen in pretraining.
- **Cost**: parameters, GPU time to fine-tune, inference latency.

Run 3 or more seeds and report mean and spread; differences smaller than
seed variation are not gains.

## Report

Pretraining corpora and overlap check, downstream data and split, input
harmonisation, all baselines with tuning budget, metric with spread across
seeds and subjects, label-efficiency curve, compute cost.
