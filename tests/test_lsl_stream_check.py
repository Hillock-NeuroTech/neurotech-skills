"""Known-answer tests for neuro-realtime-bci-pipeline/scripts/lsl_stream_check.py.

Runs a simulated LSL stream in a thread on this machine (about 25 s).
    python -m pytest tests/test_lsl_stream_check.py   (needs pylsl)
"""
import importlib.util
import threading
from pathlib import Path

import pytest

try:
    import pylsl  # noqa: F401  (raises RuntimeError, not ImportError, when liblsl is missing)
except Exception as e:  # pragma: no cover
    pytest.skip(f"pylsl unavailable: {e}", allow_module_level=True)
SCRIPT = Path(__file__).parents[1] / "plugins/neuro-realtime/skills/neuro-realtime-bci-pipeline/scripts/lsl_stream_check.py"
spec = importlib.util.spec_from_file_location("lsl_stream_check", SCRIPT)
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)


def _run(name, rate, true_rate, drop=None, seconds=8.0):
    stop = threading.Event()
    threading.Thread(target=lc.simulate_outlet, args=(rate, true_rate, 4, drop, name, stop), daemon=True).start()
    info = pylsl.resolve_byprop("name", name, timeout=10.0)[0]
    rep = lc.check(pylsl.StreamInlet(info, max_buflen=60), seconds, counter_channel=4)
    stop.set()
    return rep


def test_clean_stream():
    rep = _run("t-clean", 250.0, 250.0)
    assert abs(rep["effective_rate_hz"] - 250.0) < 0.25
    assert rep["counter_lost_samples"] == 0 and rep["warnings"] == []


def test_rate_error_is_detected():
    rep = _run("t-fast", 250.0, 252.5)
    assert abs(rep["effective_rate_hz"] - 252.5) < 0.3
    assert any("differs from nominal" in w for w in rep["warnings"])


def test_dropped_samples_are_detected_without_biasing_rate():
    rep = _run("t-drop", 250.0, 250.0, drop=(1000, 25))
    assert rep["counter_lost_samples"] == 25
    assert rep["timestamp_gaps"]["count"] == 1
    assert abs(rep["effective_rate_hz"] - 250.0) < 0.25
