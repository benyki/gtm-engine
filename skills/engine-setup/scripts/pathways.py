#!/usr/bin/env python3
"""Shared pathway → workspace / skill maps for scaffold + install + doctor.

Usage (CLI helper for install_skills.sh):
    pathways.py skills seo,outreach
    pathways.py list
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WORKFLOWS = ("seo", "linkedin", "video", "outreach")

ALWAYS_SKILLS = ("engine-setup", "engine-loop")

# Relative paths under templates/workspace/ that every scaffold gets.
ALWAYS_PATHS = (
    "config/brand.md",
    "config/channels.json",
    "config/sources.json",
    "config/experiments.json",
    "config/.env.example",
    "runs/index.csv",
    "reports/.gitkeep",
    "inputs/queue/.gitkeep",
    "state/published.csv",
)

# Per-pathway extras (dirs are copied recursively; files as-is).
PATHWAY = {
    "seo": {
        "skill": "engine-seo",
        "paths": (
            "templates/seo",
            "inputs/best/.gitkeep",
            "inputs/swipe/.gitkeep",
        ),
        "env": ("seo", "posting", "analytics"),
        "sources_keys": ("seo",),
        "channels": ("blog",),
    },
    "linkedin": {
        "skill": "engine-linkedin",
        "paths": (
            "templates/linkedin",
            "inputs/best/.gitkeep",
            "inputs/swipe/.gitkeep",
        ),
        "env": ("posting", "analytics"),
        "sources_keys": ("linkedin",),
        "channels": ("linkedin", "x"),
    },
    "video": {
        "skill": "engine-video",
        "paths": (
            "templates/video",
            "inputs/assets/.gitkeep",
            "inputs/best/.gitkeep",
        ),
        "env": ("video", "posting", "analytics"),
        "sources_keys": ("video",),
        "channels": ("tiktok", "instagram", "youtube"),
    },
    "outreach": {
        "skill": "engine-outreach",
        "paths": (
            "templates/outreach",
            "inputs/audience/.gitkeep",
            "state/crm.csv",
        ),
        "env": (),
        "sources_keys": ("outreach",),
        "channels": ("email",),
    },
}

ENV_HEADER = """\
# Copy this file to .env in the same folder and fill in the values you need.
#
# .env is gitignored. Your agent reads THIS file for the key names and never
# reads .env itself — so paste keys in yourself, and never into a chat window.
#
# Only the keys for your installed pathways are listed below.
"""

ENV_BLOCKS = {
    "video": """\
# --- video ------------------------------------------------------------------
# https://www.pexels.com/api/
PEXELS_API_KEY=

# https://elevenlabs.io  (Profile → API key)
ELEVENLABS_API_KEY=
""",
    "posting": """\
# --- posting (optional; manual posting needs nothing) -----------------------
# https://www.upload-post.com/
UPLOADPOST_API_KEY=

# Only if you already use Buffer.
BUFFER_ACCESS_TOKEN=
""",
    "seo": """\
# --- seo (optional, advanced) ----------------------------------------------
# Only if you already pay for these.
AHREFS_API_KEY=
SEMRUSH_API_KEY=
""",
    "analytics": """\
# --- analytics at volume (optional) ----------------------------------------
# Browser reading works. Add this only when it stops scaling.
APIFY_API_TOKEN=
""",
}


def parse_workflows(raw: str | None) -> list[str]:
    """Parse 'seo,outreach' or 'all'. Empty / None → all (explicit opt-in via 'all')."""
    if raw is None or raw.strip() == "":
        raise ValueError("pass --workflow <name>[,name...] or --workflow all")
    text = raw.strip().lower()
    if text == "all":
        return list(WORKFLOWS)
    out: list[str] = []
    for part in text.split(","):
        name = part.strip()
        if not name:
            continue
        if name not in PATHWAY:
            raise ValueError(
                f"unknown workflow {name!r} — choose from: {', '.join(WORKFLOWS)}, all"
            )
        if name not in out:
            out.append(name)
    if not out:
        raise ValueError("no workflows given")
    return out


def skills_for(workflows: list[str]) -> list[str]:
    names = list(ALWAYS_SKILLS)
    for wf in workflows:
        skill = PATHWAY[wf]["skill"]
        if skill not in names:
            names.append(skill)
    return names


def paths_for(workflows: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for rel in ALWAYS_PATHS:
        if rel not in seen:
            seen.add(rel)
            out.append(rel)
    for wf in workflows:
        for rel in PATHWAY[wf]["paths"]:
            if rel not in seen:
                seen.add(rel)
                out.append(rel)
    return out


def env_sections_for(workflows: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for wf in workflows:
        for sec in PATHWAY[wf]["env"]:
            if sec not in seen:
                seen.add(sec)
                out.append(sec)
    return out


def render_env_example(workflows: list[str]) -> str:
    sections = env_sections_for(workflows)
    parts = [ENV_HEADER]
    if not sections:
        parts.append(
            "\n# No API keys required for your pathways "
            f"({', '.join(workflows)}).\n"
        )
        return "".join(parts)
    for sec in sections:
        parts.append("\n")
        parts.append(ENV_BLOCKS[sec])
    return "".join(parts)


def filter_experiments(data: dict, workflows: list[str]) -> dict:
    out = dict(data)
    out["experiments"] = [
        e for e in data.get("experiments", [])
        if e.get("workflow") in workflows
    ]
    return out


def filter_sources(data: dict, workflows: list[str]) -> dict:
    keep = {"_comment"}
    for wf in workflows:
        keep.update(PATHWAY[wf]["sources_keys"])
    return {k: v for k, v in data.items() if k in keep}


def patch_channels(data: dict, workflows: list[str]) -> dict:
    out = dict(data)
    out["active_workflow"] = workflows[0]
    channels = dict(out.get("channels") or {})
    wanted = set()
    for wf in workflows:
        wanted.update(PATHWAY[wf]["channels"])
    for name, cfg in channels.items():
        if not isinstance(cfg, dict):
            continue
        updated = dict(cfg)
        updated["enabled"] = name in wanted
        channels[name] = updated
    out["channels"] = channels
    # Drop video block if video wasn't selected — keeps config honest.
    if "video" not in workflows and "video" in out:
        out = {k: v for k, v in out.items() if k != "video"}
    return out


def read_installed(ws: Path) -> list[str]:
    marker = ws / "config" / "pathways.json"
    if marker.is_file():
        try:
            data = json.loads(marker.read_text())
            got = [w for w in data.get("workflows", []) if w in PATHWAY]
            if got:
                return got
        except (json.JSONDecodeError, OSError):
            pass
    # Infer from templates/ if marker missing (older workspaces).
    templates = ws / "templates"
    if templates.is_dir():
        found = [w for w in WORKFLOWS if (templates / w).is_dir()]
        if found:
            return found
    return []


def write_installed(ws: Path, workflows: list[str]) -> None:
    marker = ws / "config" / "pathways.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if marker.is_file():
        try:
            existing = [
                w for w in json.loads(marker.read_text()).get("workflows", [])
                if w in PATHWAY
            ]
        except (json.JSONDecodeError, OSError):
            existing = []
    merged: list[str] = []
    for w in existing + workflows:
        if w not in merged:
            merged.append(w)
    marker.write_text(json.dumps({"workflows": merged}, indent=2) + "\n")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    cmd = sys.argv[1]
    if cmd == "list":
        print(" ".join(WORKFLOWS))
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
