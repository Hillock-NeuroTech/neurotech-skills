"""Checks the marketplace layout: manifests parse, every listed plugin exists,
and every skill and agent has frontmatter whose name matches its file.
    python -m pytest tests/test_structure.py
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
MARKET = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())


def frontmatter(path):
    m = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    assert m, f"{path} has no frontmatter"
    return dict(re.findall(r"^(\w[\w-]*):\s*(.+)$", m.group(1), re.M))


def test_marketplace_lists_existing_plugins():
    for p in MARKET["plugins"]:
        manifest = ROOT / p["source"] / ".claude-plugin/plugin.json"
        assert manifest.exists(), p["name"]
        assert json.loads(manifest.read_text())["name"] == p["name"]


SKILLS = sorted(ROOT.glob("plugins/*/skills/*/SKILL.md"))
AGENTS = sorted(ROOT.glob("plugins/*/agents/*.md"))


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_skill_frontmatter(path):
    fm = frontmatter(path)
    assert fm.get("name") == path.parent.name
    assert len(fm.get("description", "")) > 40


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_agent_frontmatter(path):
    fm = frontmatter(path)
    assert fm.get("name") == path.stem
    assert fm.get("description")


def test_skill_links_resolve():
    """Files named in a SKILL.md as references/... or scripts/... exist."""
    missing = []
    for s in SKILLS:
        for rel in set(re.findall(r"\b((?:references|scripts)/[\w./-]+\.(?:md|py))", s.read_text())):
            if not (s.parent / rel).exists():
                missing.append(f"{s.parent.name}: {rel}")
    assert not missing, missing
