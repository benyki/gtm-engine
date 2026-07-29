#!/usr/bin/env python3
"""Create a gtm-engine workspace inside your project — scoped to the pathways
you actually run.

Usage:
    scaffold_workspace.py [project_dir] --workflow seo
    scaffold_workspace.py . --workflow seo,outreach
    scaffold_workspace.py . --workflow all
    scaffold_workspace.py . --workflow video --merge

    project_dir   where to create it (default: current directory)
    --workflow    required: seo | linkedin | video | outreach | all
                  (comma-separated for more than one)
    --merge       fill in missing files in an existing workspace
                  (never overwrites anything that already exists)
    --name        workspace folder name (default: workflows)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import pathways as pw  # noqa: E402

REPO_ROOT = _HERE.parents[2]
TEMPLATE = REPO_ROOT / "templates" / "workspace"


def copy_path(src: Path, dst: Path, merge: bool) -> tuple[int, int]:
    """Copy a file or directory tree. Never overwrite existing files."""
    created = skipped = 0
    if src.is_dir():
        for item in sorted(src.rglob("*")):
            rel = item.relative_to(src)
            target = dst / rel
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if target.exists():
                skipped += 1
                if not merge:
                    print(f"  = {rel} (kept yours)")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            created += 1
        return created, skipped

    if dst.exists():
        return 0, 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return 1, 0


def write_json(path: Path, data: dict, *, merge: bool) -> tuple[int, int]:
    if path.exists() and merge:
        return 0, 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    return 1, 0


def merge_sources(existing: dict, template: dict, workflows: list[str]) -> dict:
    out = dict(existing)
    filtered = pw.filter_sources(template, workflows)
    for k, v in filtered.items():
        if k not in out:
            out[k] = v
    return out


def merge_experiments(existing: dict, template: dict, workflows: list[str]) -> dict:
    out = dict(existing)
    have = {e.get("id") for e in out.get("experiments", [])}
    extras = [
        e for e in pw.filter_experiments(template, workflows).get("experiments", [])
        if e.get("id") not in have
    ]
    if extras:
        out["experiments"] = list(out.get("experiments", [])) + extras
    return out


def merge_channels(existing: dict, workflows: list[str]) -> dict:
    """Enable channels for newly added pathways; keep active_workflow if set."""
    out = dict(existing)
    channels = dict(out.get("channels") or {})
    wanted = set()
    for wf in workflows:
        wanted.update(pw.PATHWAY[wf]["channels"])
    for name in wanted:
        if name not in channels:
            continue
        cfg = dict(channels[name])
        cfg["enabled"] = True
        channels[name] = cfg
    out["channels"] = channels
    if not (out.get("active_workflow") or "").strip():
        out["active_workflow"] = workflows[0]
    # Add video block from template if video was just added and missing.
    if "video" in workflows and "video" not in out:
        tmpl = json.loads((TEMPLATE / "config/channels.json").read_text())
        if "video" in tmpl:
            out["video"] = tmpl["video"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("project_dir", nargs="?", default=".")
    ap.add_argument(
        "--workflow", "-w", required=True,
        help="seo, linkedin, video, outreach (comma-separated), or all",
    )
    ap.add_argument("--name", default="workflows",
                    help="workspace folder name (default: workflows)")
    ap.add_argument("--merge", action="store_true",
                    help="add missing files to an existing workspace")
    a = ap.parse_args()

    try:
        workflows = pw.parse_workflows(a.workflow)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if not TEMPLATE.is_dir():
        print(f"error: template not found at {TEMPLATE}", file=sys.stderr)
        return 1

    project = Path(a.project_dir).expanduser().resolve()
    if not project.is_dir():
        print(f"error: {project} is not a directory", file=sys.stderr)
        return 1

    dest = project / a.name

    if dest.exists() and not a.merge:
        print(f"\n{dest} already exists.\n")
        print("That folder holds your runs and your brand config, so this")
        print("script will not touch it. Your options:\n")
        print(f"  --merge --workflow {a.workflow}")
        print("      add only the files you're missing for these pathways")
        print(f"  --name workflows2  scaffold alongside it\n")
        return 1

    print(f"\nCreating workspace: {dest}")
    print(f"  pathways: {', '.join(workflows)}\n")

    created = skipped = 0
    special = {
        "config/channels.json",
        "config/sources.json",
        "config/experiments.json",
        "config/.env.example",
    }

    for rel in pw.paths_for(workflows):
        if rel in special:
            continue
        src = TEMPLATE / rel
        if not src.exists():
            if rel.endswith("/.gitkeep"):
                (dest / Path(rel).parent).mkdir(parents=True, exist_ok=True)
                continue
            print(f"  ! missing in template: {rel}", file=sys.stderr)
            continue
        dst = dest / rel
        c, s = copy_path(src, dst, a.merge)
        created += c
        skipped += s
        if c:
            print(f"  + {rel}{'/' if src.is_dir() else ''}")
        elif s and not a.merge:
            print(f"  = {rel} (kept yours)")

    # Record pathways first so filtered config covers the full installed set.
    before = (
        set(pw.read_installed(dest))
        if (dest / "config/pathways.json").exists()
        else set()
    )
    pw.write_installed(dest, workflows)
    installed = pw.read_installed(dest)
    if set(installed) != before:
        created += 1
        print(f"  + config/pathways.json  ({', '.join(installed)})")

    # Config — create fresh, or merge pathway pieces into an existing workspace.
    tmpl_channels = json.loads((TEMPLATE / "config/channels.json").read_text())
    tmpl_sources = json.loads((TEMPLATE / "config/sources.json").read_text())
    tmpl_experiments = json.loads((TEMPLATE / "config/experiments.json").read_text())

    ch_path = dest / "config/channels.json"
    if ch_path.exists() and a.merge:
        data = merge_channels(json.loads(ch_path.read_text()), workflows)
        ch_path.write_text(json.dumps(data, indent=2) + "\n")
        print("  ~ config/channels.json  (enabled new pathway channels)")
    else:
        c, s = write_json(
            ch_path, pw.patch_channels(tmpl_channels, workflows), merge=False,
        )
        created += c
        skipped += s
        if c:
            print(f"  + config/channels.json  (active_workflow={workflows[0]})")

    src_path = dest / "config/sources.json"
    if src_path.exists() and a.merge:
        data = merge_sources(json.loads(src_path.read_text()), tmpl_sources, workflows)
        src_path.write_text(json.dumps(data, indent=2) + "\n")
        print("  ~ config/sources.json")
    else:
        c, s = write_json(
            src_path, pw.filter_sources(tmpl_sources, workflows), merge=False,
        )
        created += c
        skipped += s
        if c:
            print("  + config/sources.json")

    exp_path = dest / "config/experiments.json"
    if exp_path.exists() and a.merge:
        data = merge_experiments(
            json.loads(exp_path.read_text()), tmpl_experiments, workflows,
        )
        exp_path.write_text(json.dumps(data, indent=2) + "\n")
        print("  ~ config/experiments.json")
    else:
        c, s = write_json(
            exp_path, pw.filter_experiments(tmpl_experiments, workflows), merge=False,
        )
        created += c
        skipped += s
        if c:
            print("  + config/experiments.json")

    # .env.example is always regenerated from the full installed set — names only.
    env_text = pw.render_env_example(installed)
    env_path = dest / "config/.env.example"
    prev = env_path.read_text() if env_path.exists() else None
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text(env_text)
    if prev is None:
        created += 1
        print("  + config/.env.example")
    elif prev != env_text:
        print("  ~ config/.env.example  (keys for installed pathways)")

    gitignore = dest / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "# secrets\n"
            "config/.env\n"
            ".env\n"
            "*.local\n"
            "\n# skill symlinks — recreated by install_skills.sh --workspace\n"
            "skills/\n"
            "\n# build junk — site/ appears if engine-seo scaffolds you a website\n"
            "site/node_modules/\n"
            "site/dist/\n"
            "site/.astro/\n"
            "site/.next/\n"
            "\n# python\n"
            "__pycache__/\n"
            "*.pyc\n"
            "\n# video renders are large; keep the finished file, not the scratch\n"
            "runs/**/output/*.tmp.*\n"
        )
        created += 1
        print("  + .gitignore")

    skills = pw.skills_for(installed)
    print(f"\n  {created} files created" + (f", {skipped} left alone" if skipped else ""))
    print(f"""
Next:
  1. Install only the skills for these pathways:
       {REPO_ROOT}/skills/engine-setup/scripts/install_skills.sh \\
         --workspace {dest} --workflow {','.join(installed)}
     (skills: {', '.join(skills)})
  2. Copy config/.env.example to config/.env and add any keys you need
  3. Tell your agent:  run engine-setup
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
