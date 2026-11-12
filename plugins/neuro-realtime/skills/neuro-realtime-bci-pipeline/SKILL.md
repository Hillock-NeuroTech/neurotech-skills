---
name: neuro-realtime-bci-pipeline
description: Build or debug a real-time / closed-loop BCI or neurofeedback pipeline (Lab Streaming Layer/pylsl, LabRecorder/XDF, BrainFlow, OpenBCI, g.tec, Brain Products, MNE-LSL, PsychoPy/Psychtoolbox feedback). Use whenever the user streams neural data live, sends event markers, filters or decodes online, gives feedback, measures latency or jitter, or moves an offline pipeline online.
---

# Real-time BCI pipeline

An online pipeline has to be causal, keep up with the data rate, and have
known timing. Build it in the order below and measure timing before
collecting real data.

## 1. Acquisition

- **LSL**: one stream per device; record everything with LabRecorder to
  XDF. Load with `pyxdf.load_xdf(..., synchronize_clocks=True,
  dejitter_timestamps=True)` so streams share one clock.
- **BrainFlow**: `BoardShim` with the board id; use the synthetic board to
  develop without hardware. Check the board's real sampling rate, not the
  nominal one.
- Pull in chunks (for example 20-50 ms) rather than per sample; keep a ring
  buffer sized to the longest window you need.

## 2. Markers and sync

Software markers from the stimulus PC carry OS and display jitter. For
anything time-locked (ERPs, phase-locked stimulation) send a hardware
trigger (TTL into the amplifier's trigger input, or a photodiode on the
screen) and use software markers only as labels. Verify alignment with
`neuro-stimulus-timing-audit`; align separate clocks with
`neuro-sync-forensics`.

## 3. Causal processing

- Filters: `scipy.signal.sosfilt` with state carried across chunks
  (`zi` from `sosfilt_zi`, then pass the returned state into the next
  call). Never `filtfilt` online.
- Features over a sliding window ending at "now"; the offline model must
  be trained on the same causal features and window length.
- Re-referencing and spatial filters (CAR, CSP) are fine online if fitted
  offline on calibration data.

## 4. Measure latency and jitter

End-to-end latency = acquisition buffering + transport + processing +
feedback rendering. Measure it, do not estimate it:

1. Loopback test: feed a known signal (function generator or the amplifier
   test signal) and detect it at the output, or
2. Photodiode on the feedback display, recorded on an amplifier channel.

Report median and 95th percentile latency, and processing time per chunk
(must stay well below the chunk duration).

## 5. Before the first session

Dry run 30 minutes with a synthetic or test signal: no buffer growth, no
dropped samples (check sample counters), CPU headroom, and logging of
every decoder output with its timestamp.

## Output

Pipeline diagram (devices, streams, rates, chunk sizes), filter and feature
settings, measured latency (median, p95) and jitter, and the test log.
