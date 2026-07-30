#!/usr/bin/env python3
"""Tiny shared helpers for scaffold / install / doctor.

Convention, not a registry:
  - core skills always install: engine-setup, engine-loop
  - workflow name N → skill engine-N, but only if that folder exists
  - anything else is a custom workflow (templates only; agent supplies judgement)

Usage:
    workflows.py skills seo,outreach
    workflows.py list
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
REPO_ROOT = _HERE.parents[2]
SKILLS_DIR = REPO_ROOT / "skills"

CORE_SKILLS = ("engine-setup", "engine-loop")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# New name; still read the old marker so existing workspaces keep working.
MARKER_NEW = "workflows.json"
MARKER_OLD = "pathways.json"


def parse_workflows(raw: str | None) -> list[str]:
    if raw is None or raw.strip() == "":
        raise ValueError("pass --workflow <name>[,name...] or --workflow all")
    text = raw.strip().lower()
    if text == "all":
        return list_known()
    out: list[str] = []
    for part in text.split(","):
        name = part.strip()
        if not name:
            continue
        if not NAME_RE.match(name):
            raise ValueError(
                f"invalid workflow name {name!r} — lowercase letters, digits, "
                f"- and _ only"
            )
        if name not in out:
            out.append(name)
    if not out:
        raise ValueError("no workflows given")
    return out


def list_known() -> list[str]:
    """Workflows that already ship a skill or a starter template — discovery only."""
    names: list[str] = []
    if SKILLS_DIR.is_dir():
        for p in sorted(SKILLS_DIR.iterdir()):
            if not p.name.startswith("engine-"):
                continue
            if p.name in CORE_SKILLS:
                continue
            if (p / "SKILL.md").is_file():
                names.append(p.name.removeprefix("engine-"))
    tmpl = REPO_ROOT / "templates" / "workspace" / "templates"
    if tmpl.is_dir():
        for p in sorted(tmpl.iterdir()):
            if p.is_dir() and p.name not in names and NAME_RE.match(p.name):
                names.append(p.name)
    return names


def skill_for(workflow: str) -> str | None:
    name = f"engine-{workflow}"
    if (SKILLS_DIR / name / "SKILL.md").is_file():
        return name
    return None


def skills_for(workflows: list[str]) -> list[str]:
    names = list(CORE_SKILLS)
    for wf in workflows:
        skill = skill_for(wf)
        if skill and skill not in names:
            names.append(skill)
    return names


def _marker_path(ws: Path) -> Path:
    new = ws / "config" / MARKER_NEW
    old = ws / "config" / MARKER_OLD
    if new.is_file():
        return new
    if old.is_file():
        return old
    return new


def read_workflows(ws: Path) -> list[str]:
    marker = _marker_path(ws)
    if marker.is_file():
        try:
            data = json.loads(marker.read_text())
            got = [
                w for w in data.get("workflows", [])
                if isinstance(w, str) and NAME_RE.match(w)
            ]
            if got:
                return got
        except (json.JSONDecodeError, OSError):
            pass
    templates = ws / "templates"
    if templates.is_dir():
        found = [
            p.name for p in sorted(templates.iterdir())
            if p.is_dir() and NAME_RE.match(p.name)
        ]
        if found:
            return found
    return []


def write_workflows(ws: Path, workflows: list[str]) -> None:
    """Merge into config/workflows.json. Migrates away from pathways.json."""
    config = ws / "config"
    config.mkdir(parents=True, exist_ok=True)
    dest = config / MARKER_NEW
    existing = read_workflows(ws)
    merged: list[str] = []
    for w in existing + workflows:
        if w not in merged:
            merged.append(w)
    dest.write_text(json.dumps({"workflows": merged}, indent=2) + "\n")
    old = config / MARKER_OLD
    if old.is_file() and old != dest:
        try:
            old.unlink()
        except OSError:
            pass


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    cmd = sys.argv[1]
    if cmd == "list":
        print(" ".join(list_known()))
        return 0
    if cmd == "skills":
        raw = sys.argv[2] if len(sys.argv) > 2 else ""
        try:
            wfs = parse_workflows(raw)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(" ".join(skills_for(wfs)))
        return 0
    print(f"error: unknown command {cmd!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
