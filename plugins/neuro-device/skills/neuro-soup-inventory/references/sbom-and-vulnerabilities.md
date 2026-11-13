# SBOMs, lock files and vulnerability review

`scripts/osv_check.py` checked against the live OSV API on 13 November
2026: run on a test project's `soup.csv` it found 88 known
vulnerabilities for Pillow 9.0.0, none for NumPy 2.1.3 or MNE 1.12.0, and
reported that an unpinned SciPy could not be checked.

## From inventory to anomaly review

```bash
python3 scripts/soup_inventory.py --repo . --out soup.csv --installed
python3 scripts/osv_check.py --soup soup.csv --out soup_anomalies.csv
```

`soup_anomalies.csv` has one row per known vulnerability (OSV id, CVE
aliases, summary, CVSS severity) and an empty `assessment` column. For
each row record whether your use of the item is affected, why, and the
action (upgrade, mitigate, accept with rationale). That record is the IEC
62304 anomaly evaluation; the tool output alone is not.

## Pin exact versions

A SOUP item needs a unique version. Ways to pin Python environments:

| Tool | Lock file |
|---|---|
| pip-tools (`pip-compile`) | `requirements.txt` with hashes |
| uv (`uv lock`) | `uv.lock` |
| Poetry | `poetry.lock` |
| conda-lock | `conda-lock.yml` |

Regenerate the inventory and rerun the check whenever the lock file
changes, and on a schedule (new vulnerabilities appear for old versions).

## SBOM formats and generators

| Tool | Output |
|---|---|
| CycloneDX (`cyclonedx-py` for Python environments) | CycloneDX JSON/XML |
| Syft | CycloneDX or SPDX from directories, containers, images |
| SPDX tools | SPDX documents |
| pip-audit | vulnerability report for a Python environment (PyPI advisories and OSV) |
| GitHub dependency graph / Dependabot | continuous alerts for repositories |

FDA's premarket cybersecurity guidance expects an SBOM with support
status and known vulnerabilities assessed; CycloneDX or SPDX output plus
the assessed anomaly table covers it. Include non-Python parts too:
firmware libraries, RTOS, operating system, mobile and cloud components.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Unpinned dependencies | no unique version; checks impossible | lock files |
| Checking only direct dependencies | transitive vulnerabilities missed | `--installed` inventory of the real environment |
| Running the inventory outside the device's environment | wrong versions | run inside the project's own virtual environment or build image |
| Treating every CVE as a hazard, or none | wasted effort or missed risk | assess reachability and use in your device for each |
| One-off check before submission | stale by the time of release | rerun on each dependency change and periodically |
