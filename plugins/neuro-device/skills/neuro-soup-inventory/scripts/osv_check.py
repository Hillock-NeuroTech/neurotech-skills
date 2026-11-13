#!/usr/bin/env python3
"""Check every SOUP item against the OSV vulnerability database (osv.dev).

    python3 osv_check.py --soup soup.csv --out soup_anomalies.csv
    python3 osv_check.py --pkg numpy==2.1.3 --pkg pillow==9.0.0

Reads the CSV written by soup_inventory.py (uses installed_version, or a
pinned declared_spec when nothing is installed) or name==version pairs.
Writes one row per known vulnerability with its ids, aliases (CVE),
summary and severity, plus items that could not be checked because no
exact version is known. This is input to the IEC 62304 anomaly review,
not the review itself: decide for each finding whether your use of the
item is affected and record why.
"""
import argparse
import csv
import json
import re
import sys
import urllib.request

OSV = "https://api.osv.dev/v1/"
ECOSYSTEM = {"pypi": "PyPI", "npm": "npm", "conda": None}


def _post(path, body):
    req = urllib.request.Request(OSV + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def _get(path):
    with urllib.request.urlopen(OSV + path, timeout=60) as r:
        return json.load(r)


def items_from_soup(path):
    out = []
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            v = (r.get("installed_version") or "").strip()
            if not v:
                m = re.fullmatch(r"\s*==\s*([\w.\-+!]+)\s*", r.get("declared_spec") or "")
                v = m.group(1) if m else ""
            out.append((r["name"], (r.get("ecosystem") or "pypi").lower(), v))
    return out


def check(items, details=True):
    """items: list of (name, ecosystem, version). Returns (findings, unchecked)."""
    query, idx, unchecked = [], [], []
    for name, eco, ver in items:
        osv_eco = ECOSYSTEM.get(eco, eco)
        if not ver or not osv_eco:
            unchecked.append({"name": name, "ecosystem": eco, "reason": "no exact version" if not ver else "ecosystem not in OSV"})
            continue
        query.append({"package": {"name": name, "ecosystem": osv_eco}, "version": ver})
        idx.append((name, eco, ver))
    findings = []
    for start in range(0, len(query), 500):
        res = _post("querybatch", {"queries": query[start:start + 500]})["results"]
        for (name, eco, ver), r in zip(idx[start:start + 500], res):
            for v in r.get("vulns", []):
                row = {"name": name, "ecosystem": eco, "version": ver, "id": v["id"],
                       "aliases": "", "summary": "", "severity": "", "assessment": ""}
                if details:
                    d = _get("vulns/" + v["id"])
                    row["aliases"] = ";".join(d.get("aliases", []))
                    row["summary"] = (d.get("summary") or d.get("details", "")[:200]).replace("\n", " ")
                    row["severity"] = ";".join(f'{s.get("type")}:{s.get("score")}' for s in d.get("severity", []))
                findings.append(row)
    return findings, unchecked


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--soup", help="CSV from soup_inventory.py")
    ap.add_argument("--pkg", action="append", default=[], help="name==version (PyPI); repeatable")
    ap.add_argument("--out", help="write findings to this CSV")
    ap.add_argument("--no-details", action="store_true", help="ids only (faster)")
    a = ap.parse_args()
    items = items_from_soup(a.soup) if a.soup else []
    for p in a.pkg:
        name, _, ver = p.partition("==")
        items.append((name, "pypi", ver))
    if not items:
        sys.exit("give --soup or --pkg")
    findings, unchecked = check(items, details=not a.no_details)
    per_item = {}
    for f in findings:
        per_item.setdefault(f"{f['name']}=={f['version']}", []).append(f["id"])
    print(json.dumps({"checked": len(items) - len(unchecked), "items_with_known_vulnerabilities": len(per_item),
                      "vulnerabilities": len(findings), "by_item": {k: len(v) for k, v in per_item.items()},
                      "not_checked": unchecked}, indent=1))
    if a.out:
        cols = ["name", "ecosystem", "version", "id", "aliases", "summary", "severity", "assessment"]
        with open(a.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(findings)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
