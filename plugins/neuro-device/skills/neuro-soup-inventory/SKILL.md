---
name: neuro-soup-inventory
description: Build the IEC 62304 SOUP (software of unknown provenance) / third-party software inventory and SBOM starting point for neurotech device or analysis software from a code repository (requirements.txt, pyproject.toml, environment.yml, package.json, installed Python packages). Use whenever the user prepares software documentation for a medical or regulated neurotech device, needs a dependency list with versions and licences, or is asked for SOUP or SBOM records.
---

# SOUP inventory

IEC 62304 asks, for each SOUP item, for its title, manufacturer and unique
version, the functional and performance requirements your software relies
on, the hardware and software it needs, and an evaluation of its
published known anomalies. Collecting the list by hand is slow and misses
transitive dependencies; generate it, then add the judgment parts.

## 0. Load the tool reference

Read `references/sbom-and-vulnerabilities.md`. After generating the
inventory, check every item against the OSV vulnerability database with
`scripts/osv_check.py`, which writes the table for the anomaly review.

## 1. Generate the list

```bash
python scripts/soup_inventory.py --repo . --out soup.csv [--markdown soup.md] [--installed]
```

The script reads dependency declarations it finds (requirements*.txt,
pyproject.toml, environment.yml, package.json) and, with `--installed`,
the exact installed Python package versions with licence and homepage
from package metadata, including transitive dependencies. Run it inside
the project's own virtual environment: `--installed` lists everything in
the active environment. Unpinned declarations are flagged, because SOUP
needs a unique version.

It writes one row per item with empty columns for the parts only you can
fill: purpose in the device, requirements relied on, risk relevance,
anomaly review result.

## 2. Fill the judgment columns

- **Purpose and requirements**: what your software uses it for, and what
  must be true of it (for example "scipy.signal.sosfilt: numerically
  stable IIR filtering of float64 data").
- **Risk relevance**: link to hazards where a SOUP failure could
  contribute (see `neuro-device-regulatory`).
- **Known anomalies**: review the project's issue tracker, release notes
  and vulnerability databases (for example osv.dev) for the pinned
  version; record what you checked and the conclusion.

## 3. Keep it current

Pin versions (lock file), regenerate on every dependency change, and keep
the CSV under version control next to the code it describes.

## Output

`soup.csv` (and optional Markdown) with generated and judgment columns,
plus a list of unpinned or unknown-licence items to resolve.
