"""Known-answer tests for neuro-tus-dose-planning/scripts/tus_indices.py.
    python -m pytest tests/test_tus_indices.py
"""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

SCRIPT = Path(__file__).parents[1] / "plugins/neuro-stim/skills/neuro-tus-dose-planning/scripts/tus_indices.py"
spec = importlib.util.spec_from_file_location("tus_indices", SCRIPT)
ti = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ti)


def test_mechanical_index():
    assert ti.mechanical_index(1.0, 0.5) == pytest.approx(1.41421, rel=1e-4)
    assert ti.mechanical_index(1.0, 0.25) == pytest.approx(2.0)


def test_intensity_of_1_mpa_in_water():
    # (1e6 Pa)^2 / (2 * 1000 * 1500) = 333,333 W/m^2 = 33.33 W/cm^2
    assert ti.pulse_intensity_w_cm2(1.0) == pytest.approx(33.333, rel=1e-3)


def test_duty_cycles_scale_ispta():
    r = ti.indices(1.0, 0.5, pulse_ms=0.1, prf_hz=1000, train_s=1.0, train_interval_s=10.0)
    assert r["pulse_duty_cycle"] == pytest.approx(0.1)
    assert r["Ispta_mW_cm2"] == pytest.approx(33.333 * 0.1 * 0.1 * 1000, rel=1e-3)


def test_impossible_duty_cycle_is_refused():
    with pytest.raises(ValueError):
        ti.indices(1.0, 0.5, pulse_ms=2.0, prf_hz=1000)


def test_cem43_reference_values():
    assert ti.cem43(np.full(600, 43.0), dt_s=0.1) == pytest.approx(1.0)            # 1 min at 43 C
    assert ti.cem43(np.full(3600, 39.0), dt_s=1.0) == pytest.approx(60 * 0.25 ** 4)  # 1 h at 39 C
    assert ti.cem43(np.full(60, 44.0), dt_s=1.0) == pytest.approx(2.0)              # 1 min at 44 C
