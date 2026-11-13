"""Known-answer tests for neuro-file-formats/scripts/inspect_recording.py.

    python -m pytest tests/test_inspect_recording.py   (needs mne, scipy, edfio)
"""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

mne = pytest.importorskip("mne")
SCRIPT = Path(__file__).parents[1] / "plugins/neuro-router/skills/neuro-file-formats/scripts/inspect_recording.py"
spec = importlib.util.spec_from_file_location("inspect_recording", SCRIPT)
ir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ir)

SF, N = 500, 500 * 60
NAMES = ["Fp1", "Fp2", "C3", "C4", "O1", "O2", "EOG", "STI"]


def _raw(scale=1e-6, flat=False, clip=False, line=50, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(N) / SF
    eeg = rng.normal(0, 20, (6, N)) + 5 * np.sin(2 * np.pi * line * t)
    if flat:
        eeg[4] = 0
    if clip:
        eeg[5] = np.clip(eeg[5], -15, 15)
    stim = np.zeros(N)
    stim[SF * 2 :: SF * 4] = 1
    info = mne.create_info(NAMES, SF, ["eeg"] * 6 + ["eog", "stim"])
    raw = mne.io.RawArray(np.vstack([eeg * scale, rng.normal(0, 50, N) * scale, stim]), info, verbose="error")
    raw.set_montage("standard_1020", on_missing="ignore")
    return raw


def test_clean_file_has_no_warnings(tmp_path):
    f = tmp_path / "good_raw.fif"
    _raw().save(f, verbose="error")
    rep = ir.inspect(f)
    assert rep["warnings"] == []
    assert rep["line_frequency_guess"] == 50
    assert rep["events"]["stim_channel_events"] == {1: 15}


def test_planted_faults_are_found(tmp_path):
    f = tmp_path / "bad_raw.fif"
    _raw(scale=1.0, flat=True, clip=True, line=60).save(f, verbose="error")
    rep = ir.inspect(f)
    text = " ".join(rep["warnings"])
    assert "microvolts stored as volts" in text
    assert rep["flat_channels"] == ["O1"]
    assert rep["possibly_clipped_channels"] == ["O2"]
    assert rep["line_frequency_guess"] == 60


def test_edf_round_trip_loses_positions(tmp_path):
    pytest.importorskip("edfio")
    raw = _raw().pick(NAMES[:7])
    f = tmp_path / "x.edf"
    mne.export.export_raw(f, raw, verbose="error")
    rep = ir.inspect(f)
    assert rep["montage"] is None
    assert rep["channels_by_type"] == {"eeg": 7}  # EOG came back as EEG
