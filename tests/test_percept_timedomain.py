"""Known-answer tests for neuro-dbs-sensing-data/scripts/percept_timedomain.py
on synthetic Percept-style exports (no patient data).
    python -m pytest tests/test_percept_timedomain.py
"""
import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).parents[1] / "plugins/neuro-stim/skills/neuro-dbs-sensing-data/scripts/percept_timedomain.py"
spec = importlib.util.spec_from_file_location("percept_timedomain", SCRIPT)
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)


def _entry(n_packets=40, missing=(), fs=250, seed=0):
    """Packets every 250 ms with 62/63 samples alternating; `missing` packet indices are dropped."""
    rng = np.random.default_rng(seed)
    sizes, ticks, data, kept = [], [], [], []
    t = 1000
    full = []
    for k in range(n_packets):
        n = 63 if k % 2 else 62
        x = rng.normal(0, 1, n)
        full.append(x)
        if k not in missing:
            sizes.append(n); ticks.append(t); data.extend(x.tolist()); kept.append(k)
        t += 250
    return {"Channel": "ZERO_THREE_LEFT", "FirstPacketDateTime": "2026-01-01T10:00:00.000Z",
            "SampleRateInHz": fs, "TimeDomainData": data,
            "TicksInMses": ",".join(str(v) for v in ticks) + ",",
            "GlobalPacketSizes": ",".join(str(v) for v in sizes) + ","}, full, kept


def test_complete_stream_has_no_gaps():
    e, full, _ = _entry()
    sig, fs, rep = pt.rebuild(e)
    assert rep["missing_packets"] == 0 and rep["gaps"] == []
    assert not np.isnan(sig).any()
    assert abs(rep["duration_s"] - 10.0) < 0.05


def test_missing_packets_become_nan_gaps():
    e, full, kept = _entry(missing=(10, 11, 25))
    sig, fs, rep = pt.rebuild(e)
    assert rep["missing_packets"] == 3
    assert [g["missing_packets"] for g in rep["gaps"]] == [2, 1]
    assert abs(rep["gaps"][0]["after_s"] - 2.5) < 0.01   # packets 10-11 start at 2.5 s
    gap = sig[int(2.5 * 250) + 2:int(3.0 * 250) - 2]
    assert np.isnan(gap).all()
    # data after the gap sit at the right time: packet 12 starts at 3.0 s
    start = int(round(3.0 * 250))
    assert np.allclose(sig[start:start + 5], full[12][:5])


def test_size_mismatch_is_refused():
    e, _, _ = _entry()
    e["TimeDomainData"] = e["TimeDomainData"][:-5]
    try:
        pt.rebuild(e)
    except ValueError as err:
        assert "packet sizes sum" in str(err)
    else:
        raise AssertionError("mismatch not detected")
