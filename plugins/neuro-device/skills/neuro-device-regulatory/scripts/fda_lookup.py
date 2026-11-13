#!/usr/bin/env python3
"""Look up FDA device classification, clearances, approvals, adverse events
and recalls through the public openFDA API (api.fda.gov).

    python3 fda_lookup.py codes electroencephalograph
    python3 fda_lookup.py codes "deep brain"
    python3 fda_lookup.py profile MHY
    python3 fda_lookup.py profile GWQ --json gwq.json

`codes` searches device names in the classification database and lists
product codes. `profile` summarises one product code: class and
regulation, number of 510(k), De Novo and PMA records with the latest
decisions, MAUDE adverse-event reports by type and by year, and recalls
with root causes.

No key needed (openFDA allows about 240 requests per minute without one);
set OPENFDA_API_KEY to raise the limit. openFDA data lag the FDA's own
databases and MAUDE reports are unverified and incomplete: use them for
orientation, never as incidence rates. Engineering support, not
regulatory advice.
"""
import argparse
import collections
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.fda.gov/device/"


def fetch(endpoint, search=None, limit=None, count=None, sort=None):
    """Query one openFDA device endpoint; returns the parsed JSON or {} when nothing matches."""
    params = {}
    if search:
        params["search"] = search
    if limit:
        params["limit"] = str(limit)
    if count:
        params["count"] = count
    if sort:
        params["sort"] = sort
    key = os.environ.get("OPENFDA_API_KEY")
    if key:
        params["api_key"] = key
    url = BASE + endpoint + ".json?" + urllib.parse.urlencode(params, safe=":+\"")
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        raise


def total(js):
    return js.get("meta", {}).get("results", {}).get("total", 0) if js else 0


def search_codes(text, limit=25):
    terms = "+AND+".join(f"device_name:{urllib.parse.quote(w)}" for w in text.split())
    js = fetch("classification", terms, limit=limit)
    return [{"product_code": r.get("product_code"), "device_name": r.get("device_name"),
             "class": r.get("device_class"), "regulation": r.get("regulation_number") or None}
            for r in js.get("results", [])]


def profile(code):
    code = code.upper()
    cls = fetch("classification", f"product_code:{code}", limit=1).get("results", [{}])
    c = cls[0] if cls else {}
    k510 = fetch("510k", f"product_code:{code}", limit=5, sort="decision_date:desc")
    denovo = fetch("510k", f"product_code:{code}+AND+k_number:DEN*", limit=5, sort="decision_date:desc")
    pma = fetch("pma", f"product_code:{code}", limit=5, sort="decision_date:desc")
    ev_type = fetch("event", f"device.device_report_product_code:{code}", count="event_type.exact")
    ev_date = fetch("event", f"device.device_report_product_code:{code}", count="date_received")
    rec = fetch("recall", f"product_code:{code}", limit=100)
    by_year = collections.Counter()
    for r in ev_date.get("results", []):
        by_year[r["time"][:4]] += r["count"]
    causes = collections.Counter(r.get("root_cause_description") or "unspecified" for r in rec.get("results", []))
    return {
        "product_code": code,
        "device_name": c.get("device_name"),
        "device_class": c.get("device_class"),
        "regulation_number": c.get("regulation_number") or None,
        "medical_specialty": c.get("medical_specialty_description"),
        "implant_flag": c.get("implant_flag"),
        "life_sustain_support_flag": c.get("life_sustain_support_flag"),
        "counts": {"510k_records": total(k510), "de_novo_records": total(denovo),
                   "pma_records": total(pma), "recalls": total(rec)},
        "latest_510k": [{"k_number": r.get("k_number"), "applicant": r.get("applicant"),
                         "device_name": r.get("device_name"), "decision_date": r.get("decision_date")}
                        for r in k510.get("results", [])],
        "latest_pma": [{"pma_number": r.get("pma_number"), "supplement": r.get("supplement_number"),
                        "applicant": r.get("applicant"), "trade_name": r.get("trade_name"),
                        "decision_date": r.get("decision_date"), "decision_code": r.get("decision_code")}
                       for r in pma.get("results", [])],
        "maude_reports_by_type": {r["term"]: r["count"] for r in ev_type.get("results", [])},
        "maude_reports_by_year": dict(sorted(by_year.items())),
        "recall_root_causes": dict(causes.most_common(10)),
        "note": "MAUDE reports are unverified and lack denominators: not incidence rates.",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("codes", help="find product codes by device-name words")
    s1.add_argument("text")
    s2 = sub.add_parser("profile", help="summarise one product code")
    s2.add_argument("code")
    for s in (s1, s2):
        s.add_argument("--json", help="write the result to this file")
    a = ap.parse_args()
    out = search_codes(a.text) if a.cmd == "codes" else profile(a.code)
    print(json.dumps(out, indent=1))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=1)
    if not out:
        sys.exit("nothing found")


if __name__ == "__main__":
    main()
