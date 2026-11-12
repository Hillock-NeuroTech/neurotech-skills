"""Generate a SOUP / third-party software inventory from a repository.

python soup_inventory.py --repo . --out soup.csv [--markdown soup.md] [--installed]

Reads requirements*.txt, pyproject.toml, environment.yml/.yaml and package.json
found under --repo (skipping .git, node_modules, virtualenvs). With --installed,
adds every installed Python distribution with exact version, licence and
homepage from its metadata. Makes no network requests.
"""
import argparse
import csv
import json
import re
from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", "site-packages", "dist", "build"}
REQ_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*(\[.*?\])?\s*([<>=!~]=?\s*[^;#\s]+(?:\s*,\s*[<>=!~]=?\s*[^;#\s]+)*)?")
JUDGMENT = ["purpose_in_device", "requirements_relied_on", "risk_relevance", "anomaly_review"]


def files(repo):
    for p in Path(repo).rglob("*"):
        if p.is_file() and not (set(p.parts) & SKIP):
            yield p


def parse_requirements(p):
    for line in p.read_text(errors="ignore").splitlines():
        line = line.split("#")[0].strip()
        if not line or line.startswith(("-", "git+", "http")):
            continue
        m = REQ_RE.match(line)
        if m:
            yield m.group(1), (m.group(3) or "").replace(" ", "")


def parse_pyproject(p):
    try:
        import tomllib
    except ImportError:
        return
    d = tomllib.loads(p.read_text())
    for spec in d.get("project", {}).get("dependencies", []):
        m = REQ_RE.match(spec)
        if m:
            yield m.group(1), (m.group(3) or "").replace(" ", "")
    for group in d.get("project", {}).get("optional-dependencies", {}).values():
        for spec in group:
            m = REQ_RE.match(spec)
            if m:
                yield m.group(1), (m.group(3) or "").replace(" ", "")
    for name, v in d.get("tool", {}).get("poetry", {}).get("dependencies", {}).items():
        if name.lower() != "python":
            yield name, v if isinstance(v, str) else v.get("version", "")


def parse_environment(p):
    for line in p.read_text(errors="ignore").splitlines():
        m = re.match(r"^\s*-\s*([A-Za-z0-9_.\-]+)\s*([=<>!].*)?$", line)
        if m and m.group(1) not in ("pip",):
            yield m.group(1), (m.group(2) or "").strip()


def parse_package_json(p):
    d = json.loads(p.read_text())
    for sec in ("dependencies", "devDependencies"):
        for name, v in d.get(sec, {}).items():
            yield name, v


def declared(repo):
    rows = []
    for p in files(repo):
        n = p.name.lower()
        if n.startswith("requirements") and n.endswith(".txt"):
            parser, eco = parse_requirements, "pypi"
        elif n == "pyproject.toml":
            parser, eco = parse_pyproject, "pypi"
        elif n in ("environment.yml", "environment.yaml"):
            parser, eco = parse_environment, "conda"
        elif n == "package.json":
            parser, eco = parse_package_json, "npm"
        else:
            continue
        for name, spec in parser(p) or []:
            rows.append({"name": name, "ecosystem": eco, "declared_spec": spec,
                         "pinned": bool(re.fullmatch(r"==?[\w.\-+]+|\d[\w.\-+]*", spec or "")),
                         "declared_in": str(p.relative_to(repo))})
    return rows


def installed():
    from importlib import metadata
    out = {}
    for dist in metadata.distributions():
        md = dist.metadata
        name = md.get("Name")
        if not name:
            continue
        lic = md.get("License-Expression") or md.get("License") or ""
        if not lic or len(lic) > 80:
            cls = [c.split("::")[-1].strip() for c in md.get_all("Classifier") or [] if c.startswith("License")]
            lic = "; ".join(cls) or (lic[:80] + "..." if lic else "")
        home = md.get("Home-page") or ""
        if not home:
            for u in md.get_all("Project-URL") or []:
                home = u.split(",", 1)[-1].strip()
                break
        out[name.lower().replace("_", "-")] = {"installed_version": dist.version, "license": lic,
                                               "homepage": home, "manufacturer": md.get("Author") or md.get("Maintainer") or ""}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="soup.csv")
    ap.add_argument("--markdown")
    ap.add_argument("--installed", action="store_true")
    a = ap.parse_args()
    rows = {(r["ecosystem"], r["name"].lower()): r for r in declared(a.repo)}
    inst = installed() if a.installed else {}
    for key, info in inst.items():
        r = rows.setdefault(("pypi", key), {"name": key, "ecosystem": "pypi", "declared_spec": "",
                                            "pinned": False, "declared_in": "(installed, transitive)"})
        r.update(info)
    for (eco, key), r in rows.items():
        if eco == "pypi" and not a.installed:
            r.update({"installed_version": "", "license": "", "homepage": "", "manufacturer": ""})
        else:
            match = inst.get(key.replace("_", "-"), {})
            for k in ("installed_version", "license", "homepage", "manufacturer"):
                r.setdefault(k, match.get(k, ""))
        for k in JUDGMENT:
            r.setdefault(k, "")
    cols = ["name", "ecosystem", "declared_spec", "pinned", "installed_version", "license", "manufacturer",
            "homepage", "declared_in"] + JUDGMENT
    data = sorted(rows.values(), key=lambda r: (r["ecosystem"], r["name"].lower()))
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(data)
    if a.markdown:
        with open(a.markdown, "w") as fh:
            fh.write("| " + " | ".join(cols[:8]) + " |\n|" + "---|" * 8 + "\n")
            for r in data:
                fh.write("| " + " | ".join(str(r.get(c, "")).replace("|", "/") for c in cols[:8]) + " |\n")
    unpinned = [r["name"] for r in data if r["declared_in"] != "(installed, transitive)" and not r["pinned"]]
    nolic = [r["name"] for r in data if a.installed and r["ecosystem"] == "pypi" and not r.get("license")]
    print(json.dumps({"items": len(data), "written": a.out, "unpinned_declared": unpinned[:50],
                      "missing_license_metadata": nolic[:50]}, indent=2))


if __name__ == "__main__":
    main()
