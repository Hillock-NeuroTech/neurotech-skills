"""Offline tests for neuro-soup-inventory/scripts/osv_check.py (OSV responses faked).
    python -m pytest tests/test_osv_check.py
"""
import csv
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "plugins/neuro-device/skills/neuro-soup-inventory/scripts/osv_check.py"
spec = importlib.util.spec_from_file_location("osv_check", SCRIPT)
oc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oc)


def test_versions_from_soup_csv(tmp_path):
    f = tmp_path / "soup.csv"
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "ecosystem", "declared_spec", "installed_version"])
        w.writeheader()
        w.writerow({"name": "a", "ecosystem": "pypi", "declared_spec": "==1.0", "installed_version": ""})
        w.writerow({"name": "b", "ecosystem": "pypi", "declared_spec": ">=2", "installed_version": "2.5"})
        w.writerow({"name": "c", "ecosystem": "pypi", "declared_spec": ">=3", "installed_version": ""})
    assert oc.items_from_soup(f) == [("a", "pypi", "1.0"), ("b", "pypi", "2.5"), ("c", "pypi", "")]


def test_findings_and_unchecked(monkeypatch):
    monkeypatch.setattr(oc, "_post", lambda path, body: {"results": [{"vulns": [{"id": "GHSA-1"}, {"id": "GHSA-2"}]}, {}]})
    monkeypatch.setattr(oc, "_get", lambda path: {"aliases": ["CVE-1"], "summary": "bad", "severity": [{"type": "CVSS_V3", "score": "9.8"}]})
    findings, unchecked = oc.check([("x", "pypi", "1.0"), ("y", "pypi", "2.0"), ("z", "pypi", "")])
    assert [f["id"] for f in findings] == ["GHSA-1", "GHSA-2"]
    assert findings[0]["aliases"] == "CVE-1" and findings[0]["severity"] == "CVSS_V3:9.8"
    assert unchecked == [{"name": "z", "ecosystem": "pypi", "reason": "no exact version"}]
