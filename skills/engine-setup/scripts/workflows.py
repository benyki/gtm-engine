#!/usr/bin/env python3
"""Tiny shared helpers for scaffold / install / doctor.

Convention, not a registry:
  - core skills always install: engine-setup, engine-loop
  - a workflow folder's TYPE (workflow.json) maps to skill engine-<type>,
    but only if that skill folder exists
  - the folder NAME is free — outreach-investors/ with type "outreach" is
    a second outreach workflow; anything without a shipped type is custom
    (generic scaffold; the agent supplies the judgement)

Usage:
    workflows.py skills seo,outreach-investors:outreach
    workflows.py list          # types that ship a skill or starter
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
REPO_ROOT = _HERE.parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
STARTERS_DIR = REPO_ROOT / "workspace" / "workflows"

CORE_SKILLS = ("engine-setup", "engine-loop")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# A skill that reads another skill's references must not be installed alone.
# engine-social is a format layer on engine-seo: subject finding and browser
# research live there and are used as-is.
SKILL_DEPS = {
    "engine-social": ("engine-seo",),
}


def list_known() -> list[str]:
    """Workflow TYPES that ship a skill or a starter — discovery only."""
    names: list[str] = []
    if SKILLS_DIR.is_dir():
        for p in sorted(SKILLS_DIR.iterdir()):
            if not p.name.startswith("engine-") or p.name in CORE_SKILLS:
                continue
            if (p / "SKILL.md").is_file():
                names.append(p.name.removeprefix("engine-"))
    if STARTERS_DIR.is_dir():
        for p in sorted(STARTERS_DIR.iterdir()):
            # `_`-prefixed folders are shared scaffold parts, not workflow
            # types — `_every-workflow/` is merged into every folder created.
            if p.name.startswith("_"):
                continue
            if p.is_dir() and p.name not in names and NAME_RE.match(p.name):
                names.append(p.name)
    return names


def parse_workflows(raw: str | None) -> list[tuple[str, str]]:
    """Parse '--workflow' input into (name, type) pairs.

    Forms: 'outreach' (name = type), 'outreach-investors:outreach'
    (second instance of a type), 'newsletter' (custom — type = name),
    'all' (every known type, name = type). Empty/None → all: the default
    scaffold is one folder per shipped workflow.
    """
    known = list_known()
    if raw is None or raw.strip() == "" or raw.strip().lower() == "all":
        return [(t, t) for t in known]
    out: list[tuple[str, str]] = []
    for part in raw.strip().lower().split(","):
        part = part.strip()
        if not part:
            continue
        name, _, typ = part.partition(":")
        typ = typ or name
        for label, v in (("name", name), ("type", typ)):
            if not NAME_RE.match(v):
                raise ValueError(
                    f"invalid workflow {label} {v!r} — lowercase letters, "
                    f"digits, - and _ only"
                )
        if name not in [n for n, _ in out]:
            out.append((name, typ))
    if not out:
        raise ValueError("no workflows given")
    return out


def skill_for(wf_type: str) -> str | None:
    name = f"engine-{wf_type}"
    if (SKILLS_DIR / name / "SKILL.md").is_file():
        return name
    return None


def skills_for(types: list[str]) -> list[str]:
    names = list(CORE_SKILLS)
    for t in types:
        skill = skill_for(t)
        if not skill:
            continue
        for name in (skill, *SKILL_DEPS.get(skill, ())):
            # A dependency still has to exist as a skill folder.
            if name not in names and (SKILLS_DIR / name / "SKILL.md").is_file():
                names.append(name)
    return names


def workspace_types(ws: Path) -> list[str]:
    """Types of every workflow folder in a workspace (from workflow.json)."""
    types: list[str] = []
    try:
        for p in sorted(ws.iterdir()):
            marker = p / "workflow.json"
            if not (p.is_dir() and marker.is_file()):
                continue
            try:
                t = (json.loads(marker.read_text()).get("type") or "").strip()
            except (json.JSONDecodeError, OSError):
                t = ""
            t = t or p.name
            if t not in types:
                types.append(t)
    except OSError:
        pass
    return types


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
            pairs = parse_workflows(raw)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(" ".join(skills_for([t for _, t in pairs])))
        return 0
    print(f"error: unknown command {cmd!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
