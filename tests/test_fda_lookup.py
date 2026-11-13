"""Offline tests for neuro-device-regulatory/scripts/fda_lookup.py (openFDA responses are faked).
    python -m pytest tests/test_fda_lookup.py
"""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "plugins/neuro-device/skills/neuro-device-regulatory/scripts/fda_lookup.py"
spec = importlib.util.spec_from_file_location("fda_lookup", SCRIPT)
fl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fl)

FAKE = {
    "classification": {"meta": {"results": {"total": 1}}, "results": [{"product_code": "XYZ", "device_name": "Test Stimulator", "device_class": "3", "implant_flag": "Y"}]},
    "510k": {"meta": {"results": {"total": 2}}, "results": [{"k_number": "K250001", "decision_date": "2025-01-01"}]},
    "pma": {"meta": {"results": {"total": 7}}, "results": [{"pma_number": "P000001", "decision_code": "APPR"}]},
    "recall": {"meta": {"results": {"total": 3}}, "results": [{"root_cause_description": "Software design"}, {"root_cause_description": "Software design"}, {}]},
}


def fake_fetch(endpoint, search=None, limit=None, count=None, sort=None):
    if endpoint == "event" and count == "event_type.exact":
        return {"results": [{"term": "Injury", "count": 5}, {"term": "Malfunction", "count": 9}]}
    if endpoint == "event" and count == "date_received":
        return {"results": [{"time": "20240101", "count": 2}, {"time": "20240601", "count": 3}, {"time": "20250101", "count": 4}]}
    if endpoint == "510k" and search and "DEN" in search:
        return {}
    return FAKE.get(endpoint, {})


def test_profile_aggregates(monkeypatch):
    monkeypatch.setattr(fl, "fetch", fake_fetch)
    p = fl.profile("xyz")
    assert p["product_code"] == "XYZ" and p["device_class"] == "3"
    assert p["counts"] == {"510k_records": 2, "de_novo_records": 0, "pma_records": 7, "recalls": 3}
    assert p["maude_reports_by_type"] == {"Injury": 5, "Malfunction": 9}
    assert p["maude_reports_by_year"] == {"2024": 5, "2025": 4}
    assert p["recall_root_causes"]["Software design"] == 2 and p["recall_root_causes"]["unspecified"] == 1


def test_no_match_returns_empty_counts(monkeypatch):
    monkeypatch.setattr(fl, "fetch", lambda *a, **k: {})
    p = fl.profile("NONE")
    assert p["counts"] == {"510k_records": 0, "de_novo_records": 0, "pma_records": 0, "recalls": 0}
    assert fl.search_codes("nothing here") == []
