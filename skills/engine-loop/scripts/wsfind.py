#!/usr/bin/env python3
"""Find the workspace. One implementation, imported by every loop script.

A workspace is recognised by its marker files, not by its folder name:
config/pathways.json (written by the scaffold) or config/channels.json.
`workflows/` is only the default name — a workspace called growth/ or
marketing/ works the same.

Resolution order:
  1. --workspace flag (explicit always wins)
  2. GTM_WORKSPACE environment variable
  3. walking up from the cwd: the dir itself, then its workflows/ child
  4. immediate children of the cwd (so running from the project root works
     whatever the workspace is called)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

MARKERS = ("config/pathways.json", "config/channels.json")


def is_workspace(p: Path) -> bool:
    return any((p / m).is_file() for m in MARKERS)


def find_workspace(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if (p / "config").is_dir():
            return p
        sys.exit(f"error: no config/ in {p}")

    env = (os.environ.get("GTM_WORKSPACE") or "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "config").is_dir():
            return p
        sys.exit(f"error: GTM_WORKSPACE={env} has no config/")

    for base in (Path.cwd(), *Path.cwd().parents):
        if is_workspace(base):
            return base
        cand = base / "workflows"
        if is_workspace(cand) or (cand / "config").is_dir():
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
