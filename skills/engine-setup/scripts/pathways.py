#!/usr/bin/env python3
"""Shared workflow → workspace / skill maps for scaffold + install + doctor.

(The filename and the config/pathways.json marker keep the historical
"pathways" name for compatibility; everywhere else these are workflows.)

The four built-in workflows ship with a dedicated skill and templates. The set
is NOT closed: any other name (newsletter, podcast, ads, community, …) gets a
generic scaffold — a templates/<name>/ folder plus the shared loop files —
and engine-loop runs it through the same three traces as everything else.
There is just no dedicated skill for it; the agent supplies the judgement.

Usage (CLI helper for install_skills.sh):
    pathways.py skills seo,outreach
    pathways.py list
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Built-in workflows with a dedicated skill. Other names are welcome too —
# they get GENERIC treatment below.
WORKFLOWS = ("seo", "linkedin", "video", "outreach")

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

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

# Per-workflow extras (dirs are copied recursively; files as-is).
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
        "env": ("bluesky", "posting", "analytics"),
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
# Only the keys for your installed workflows are listed below.
"""

ENV_BLOCKS = {
    "bluesky": """\
# --- bluesky (optional; only if you post there) -----------------------------
# App password, NOT your account password:
# bsky.app → Settings → Privacy and Security → App Passwords
BSKY_HANDLE=
BSKY_APP_PASSWORD=
""",
    "video": """\
# --- video ------------------------------------------------------------------
# https://www.pexels.com/api/
PEXELS_API_KEY=

# https://elevenlabs.io  (Profile → API key)
ELEVENLABS_API_KEY=
""",
    "posting": """\
# --- posting (only needed for Upload Post or Buffer; manual needs nothing) --
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


def pathway_for(name: str) -> dict:
    """Config for a workflow. Built-ins get their full entry; anything else
    gets a generic one: a templates/<name>/ folder and nothing pre-decided."""
    if name in PATHWAY:
        return PATHWAY[name]
    return {
        "skill": None,
        "paths": (f"templates/{name}/.gitkeep",),
        "env": (),
        "sources_keys": (name,),
        "channels": (),
    }


def is_custom(name: str) -> bool:
    return name not in PATHWAY


def parse_workflows(raw: str | None) -> list[str]:
    """Parse 'seo,outreach' or 'all'. Names outside the built-in set are
    accepted (custom workflows); 'all' means all built-ins."""
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
        if not NAME_RE.match(name):
            raise ValueError(
                f"invalid workflow name {name!r} — lowercase letters, digits, "
                f"- and _ only (built-ins: {', '.join(WORKFLOWS)})"
            )
        if name not in out:
            out.append(name)
    if not out:
        raise ValueError("no workflows given")
    return out


def skills_for(workflows: list[str]) -> list[str]:
    names = list(ALWAYS_SKILLS)
    for wf in workflows:
        skill = pathway_for(wf)["skill"]
        if skill and skill not in names:
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
        for rel in pathway_for(wf)["paths"]:
            if rel not in seen:
                seen.add(rel)
                out.append(rel)
    return out


def env_sections_for(workflows: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for wf in workflows:
        for sec in pathway_for(wf)["env"]:
            if sec not in seen:
                seen.add(sec)
                out.append(sec)
    return out


def render_env_example(workflows: list[str]) -> str:
    sections = env_sections_for(workflows)
    parts = [ENV_HEADER]
    if not sections:
        parts.append(
            "\n# No API keys required for your workflows "
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
        keep.update(pathway_for(wf)["sources_keys"])
    return {k: v for k, v in data.items() if k in keep}


def patch_channels(data: dict, workflows: list[str]) -> dict:
    out = dict(data)
    out["active_workflow"] = workflows[0]
    channels = dict(out.get("channels") or {})
    wanted = set()
    for wf in workflows:
        wanted.update(pathway_for(wf)["channels"])
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
            # Custom workflow names are kept — the marker is the record of
            # what this workspace runs, not a filter to the built-ins.
            got = [w for w in data.get("workflows", [])
                   if isinstance(w, str) and NAME_RE.match(w)]
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
                if isinstance(w, str) and NAME_RE.match(w)
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
