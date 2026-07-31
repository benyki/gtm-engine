#!/usr/bin/env python3
"""Find the workspace and its workflow folders. One implementation,
imported by every loop script.

Layout: the workspace root holds one `shared/` folder (brand, channels,
.env, assets, docs, insights — everything cross-workflow) and one folder
per workflow. Each workflow folder is self-contained: its own
workflow.json, experiments.json, sources.json, templates/, inputs/,
runs/, reports/. Folder names are free — `outreach-investors/`
with `"type": "outreach"` in workflow.json is a second outreach workflow.

The root is recognised by its `shared/` folder, not by its name:
a workspace called growth/ or marketing/ works the same.

Resolution order for the root:
  1. --workspace flag (explicit always wins)
  2. GTM_WORKSPACE environment variable
  3. walking up from the cwd: the dir itself, then its workflows/ child
  4. immediate children of the cwd (so running from the project root works
     whatever the workspace is called)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SHARED = "shared"
WF_MARKER = "workflow.json"

# Files that identify shared/ as ours (any one is enough).
_SHARED_FILES = ("channels.json", "brand.md", ".env.example")

# The engine repo's own workspace/ folder is the scaffold SOURCE, not a
# workspace. This marker at its root keeps it from ever being picked up.
TEMPLATE_MARKER = ".gtm-template"


def is_workspace(p: Path) -> bool:
    if (p / TEMPLATE_MARKER).is_file():
        return False
    shared = p / SHARED
    return shared.is_dir() and any((shared / f).is_file() for f in _SHARED_FILES)


def _check(p: Path) -> Path:
    if is_workspace(p):
        return p
    sys.exit(f"error: no shared/ found in {p} — not a workspace")


def find_workspace(explicit: str | None) -> Path:
    if explicit:
        return _check(Path(explicit).expanduser().resolve())

    env = (os.environ.get("GTM_WORKSPACE") or "").strip()
    if env:
        return _check(Path(env).expanduser().resolve())

    for base in (Path.cwd(), *Path.cwd().parents):
        if is_workspace(base):
            return base
        cand = base / "workflows"
        if is_workspace(cand):
            return cand
        if base == Path.home():
            break

    try:
        for child in sorted(Path.cwd().iterdir()):
            if child.is_dir() and is_workspace(child):
                return child
    except OSError:
        pass

    sys.exit("error: no workspace found — pass --workspace or set GTM_WORKSPACE")


def list_workflow_dirs(ws: Path) -> list[Path]:
    """Every workflow folder in the workspace: a dir with a workflow.json."""
    out = []
    try:
        for p in sorted(ws.iterdir()):
            if p.is_dir() and (p / WF_MARKER).is_file():
                out.append(p)
    except OSError:
        pass
    return out


def workflow_meta(wd: Path) -> dict:
    """Parsed workflow.json; {} when missing or broken."""
    marker = wd / WF_MARKER
    if not marker.is_file():
        return {}
    try:
        data = json.loads(marker.read_text())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def find_workflow_dir(ws: Path, name: str) -> Path:
    """The workflow folder called `name`, with a helpful error otherwise."""
    wd = ws / name
    if wd.is_dir() and (wd / WF_MARKER).is_file():
        return wd
    have = [p.name for p in list_workflow_dirs(ws)]
    hint = f" — workflows here: {', '.join(have)}" if have else \
        " — no workflow folders yet; scaffold one or copy an existing folder"
    sys.exit(f"error: no workflow folder {name!r} in {ws}{hint}")
