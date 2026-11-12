"""Map ward-clock seizure onset (14:32:10) to an EEG sample index using the
1 Hz sync-pulse train as the clock, not the header.

Findings:
  * Header says sfreq = 500 Hz, but every inter-pulse interval is exactly 512
    samples -> the true sampling rate of the export is 512 Hz (header is wrong;
    a constant 512, not a slow drift).
  * The first pulse sits at sample 128, not 0, and only 3599 pulses exist for
    an hour-long (3600 s) recording. One sync pulse per second from 14:00:00
    gives 3600 pulses (14:00:00 ... 14:59:59). The single explanation for both
    facts is that the export dropped the first 384 samples (0.75 s): the
    14:00:00 pulse was lost, and pulse[0] is the 14:00:01 pulse.
    (Sample 0 of the export is therefore 14:00:00.75.)
  * Onset 14:32:10 is 1930 s after 14:00:00 -> pulse at index 1930 - 1 = 1929.
"""
import json
import numpy as np

hdr = json.load(open("header.json"))
p = np.load("sync_pulse_samples.npy").astype(np.int64)

d = np.diff(p)
assert np.all(d == d[0]), "non-uniform pulse spacing"
fs_true = float(d[0])                       # samples per 1 s pulse = 512
print(f"header sfreq={hdr['sfreq']}, pulse-derived sfreq={fs_true}")

def hms(s):
    h, m, sec = map(int, s.split(":"))
    return 3600 * h + 60 * m + sec

rec_len_s = 3600
expected_pulses = rec_len_s                 # pulses at t = 0..3599 s
n_missing_start = expected_pulses - len(p)  # = 1 -> first pulse dropped by export
assert n_missing_start == 1
# consistency: missing exactly one leading pulse <=> leading trim < 1 s
trim = n_missing_start * fs_true - p[0]     # 512 - 128 = 384 samples (0.75 s)
assert 0 < trim <= fs_true
print(f"export trimmed {trim:.0f} samples ({trim/fs_true:.2f} s) at start")

t_onset = hms("14:32:10") - hms(hdr["meas_start"])   # 1930 s
k = t_onset - n_missing_start                          # pulse index 1929
onset_sample = int(p[k])                               # sample at exact second

# fractional-second fallback (none here) handled by pulse-relative interpolation
print(f"onset second {t_onset} -> pulse index {k} -> sample {onset_sample}")
print(f"(naive header answer would be {int(t_onset*hdr['sfreq'])})")

json.dump({"seizure_onset_sample": onset_sample}, open("answer.json", "w"), indent=2)
