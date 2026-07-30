#!/usr/bin/env python3
"""Pick which template version to use for the next piece of work.

This is the only place an A/B arm is chosen. The rules it enforces:

  R2  Least-used arm wins. Nobody cherry-picks a favourite. Usage is
      counted from the workflow's own runs/index.csv — its spine — within
      the experiment's cohort. crm.csv is for stickiness, not counting.
  R3  Sticky — an entity that already has an arm keeps it, forever,
      including follow-ups.
  R4  A missing template file NEVER blocks the run. It reports
      action="write_template" with the hypothesis, and the agent writes it.
  R5  "default" and "none" normalise to the base template.

Everything is read from the workflow's own folder — its experiments.json,
its templates/, its runs and CRM. `--workflow` names that folder
(outreach, outreach-investors, newsletter, ...).

With no live experiment it doesn't guess a filename: it reports what's in
the workflow's active template folder — one file to use, a list to choose
from, or write_template when the folder is empty. The agent decides and
records the file it actually rendered.

Usage:
    assign_arm.py --workflow outreach [--entity someone@example.com]
    assign_arm.py --workflow video --json

Output is JSON so an agent can act on it directly.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wsfind import find_workspace, find_workflow_dir  # noqa: E402

NORMALISE_TO_BASE = {"", "default", "none", "null"}


def load_experiment(wd: Path, channel: str = "") -> tuple[dict | None, list[str]]:
    """The live experiment for this workflow (and channel, when either side
    names one), plus the ids of any other live candidates that were skipped —
    silence there would hide a config mistake.

    An experiment may carry an optional "channel" field. That makes concurrent
    experiments in one workflow legitimate as long as their channels differ —
    video hooks on tiktok and thumbnails on youtube, say. Pass --channel and
    the right one is selected; an experiment with no channel matches any."""
    path = wd / "experiments.json"
    if not path.is_file():
        return None, []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"error: {path} is not valid JSON — {e}")
    live = [exp for exp in data.get("experiments", [])
            if exp.get("status") == "live"]
    if channel:
        live = [e for e in live
                if not (e.get("channel") or "").strip()
                or e["channel"].strip() == channel]
    if not live:
        return None, []
    return live[0], [e.get("id", "?") for e in live[1:]]


def rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def sticky_arm(wd: Path, entity: str) -> str | None:
    """R3 — if we've spoken to them before, they stay in their arm."""
    for r in rows(wd / "crm.csv"):
        if r.get("id", "").strip().lower() == entity.strip().lower():
            arm = (r.get("arm") or "").strip()
            return arm or None
    return None


def arm_counts(wd: Path, exp: dict) -> Counter:
    """Count usage within this experiment's cohort only (R6).

    Reads the workflow's own runs/index.csv and nothing else. The CRM is
    not a usage ledger — every draft is logged as a run, so counting CRM
    rows on top would count the same work twice.
    """
    started = exp.get("started", "")
    counts: Counter = Counter()
    for r in rows(wd / "runs" / "index.csv"):
        if r.get("experiment_id") != exp["id"]:
            continue
        if started and r.get("created_at", "") < started:
            continue
        arm = (r.get("arm") or "").strip()
        if arm:
            counts[arm] += 1
    return counts


def active_templates(wd: Path) -> list[Path]:
    """Template files in the workflow's templates/. losers/ never counts."""
    d = wd / "templates"
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir()
                  if p.is_file() and not p.name.startswith("."))


def template_ext(wd: Path, base: str) -> str:
    """Extension for an implied template name: whatever the base template
    already uses, else the folder's most common, else .txt. Keeps seo's .md
    templates from being guessed as .txt."""
    files = active_templates(wd)
    for p in files:
        if p.stem == base and p.suffix:
            return p.suffix
    exts = Counter(p.suffix for p in files if p.suffix)
    return exts.most_common(1)[0][0] if exts else ".txt"


def template_path(wd: Path, arm: dict, base: str) -> Path:
    name = arm.get("template")
    if not name:
        ext = template_ext(wd, base)
        name = f"{base}{ext}" if arm["id"] in NORMALISE_TO_BASE else f"{base}-{arm['id']}{ext}"
    return wd / "templates" / name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True,
                    help="the workflow FOLDER name — outreach, seo, social, "
                         "video, outreach-investors, or one of your own")
    ap.add_argument("--channel", default="",
                    help="channel this piece is for — selects between "
                         "channel-scoped experiments in the same workflow")
    ap.add_argument("--entity", default="",
                    help="stable id (email, handle) — keeps them in their arm")
    ap.add_argument("--workspace")
    ap.add_argument("--json", action="store_true", help="machine-readable only")
    a = ap.parse_args()

    ws = find_workspace(a.workspace)
    wd = find_workflow_dir(ws, a.workflow)
    exp, skipped_live = load_experiment(wd, a.channel)
    if skipped_live:
        scope = f"'{a.workflow}'" + (f" / channel '{a.channel}'" if a.channel else "")
        print(f"warning: {len(skipped_live) + 1} live experiments match "
              f"{scope} — using {exp['id']}, ignoring {', '.join(skipped_live)}. "
              f"Concurrent experiments are fine when scoped to different "
              f"channels (set \"channel\" on each and pass --channel); "
              f"otherwise pause the ones you aren't running.",
              file=sys.stderr)

    if exp is None:
        # No experiment: report what exists and let the agent decide.
        found = active_templates(wd)
        out = {"experiment_id": "", "arm": ""}
        if len(found) == 1:
            out.update({
                "template": str(found[0]),
                "action": "use_template",
                "why": "no live experiment — one active template, use it",
            })
        elif found:
            out.update({
                "template": "",
                "templates": [str(p) for p in found],
                "action": "choose_template",
                "why": "no live experiment — several active templates",
                "instruction": (
                    "Nothing is being tested, so any of these is fine. Pick "
                    "the one that fits the piece, and record template_used "
                    "as the file you actually rendered."
                ),
            })
        else:
            out.update({
                "template": str(wd / "templates"),
                "action": "write_template",
                "why": "no live experiment and no template yet",
                "instruction": (
                    f"Write the first template into {a.workflow}/templates/, "
                    "guided by shared/brand.md and the workflow's skill. Then "
                    "use it and record template_used on the run."
                ),
            })
        print(json.dumps(out, indent=2))
        return 0

    arms = exp.get("arms") or []
    if not arms:
        sys.exit(f"error: experiment {exp['id']} has no arms")

    base = exp.get("template_base", "first-touch")

    # R3 — sticky beats everything.
    chosen = None
    if a.entity:
        prev = sticky_arm(wd, a.entity)
        if prev:
            chosen = next((x for x in arms if x["id"] == prev), None)
            if chosen is None:   # arm was retired; honour history anyway
                chosen = {"id": prev, "label": prev, "hypothesis": ""}

    reason = "sticky — this entity is already in that arm"
    if chosen is None:
        # R2 — least used wins; ties break on declaration order.
        counts = arm_counts(wd, exp)
        chosen = min(arms, key=lambda x: (counts[x["id"]], arms.index(x)))
        reason = (f"least used ({counts[chosen['id']]} runs; "
                  + ", ".join(f"{x['id']}={counts[x['id']]}" for x in arms) + ")")

    path = template_path(wd, chosen, base)
    exists = path.is_file()

    out = {
        "experiment_id": exp["id"],
        "channel": (exp.get("channel") or "").strip(),
        "arm": chosen["id"],
        "label": chosen.get("label", ""),
        "template": str(path),
        "template_exists": exists,
        "action": "use_template" if exists else "write_template",
        "why": reason,
    }
    if skipped_live:
        out["ignored_live_experiments"] = skipped_live
    if not exists:
        # R4 — never block. Tell the agent exactly what to write.
        out["hypothesis"] = chosen.get("hypothesis", "")
        out["instruction"] = (
            f"This arm has no template yet. Write {path.name} in "
            f"{a.workflow}/templates/, guided by the hypothesis above and by the "
            f"other templates in that folder. Do not copy an existing arm — a "
            f"variant is a different proposition, not a reworded one. Then use it "
            f"and record template_used={path.name} on the run."
        )

    print(json.dumps(out, indent=2))
    if not a.json and not exists:
        print(f"\n→ write {a.workflow}/templates/{path.name} first, then use it.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
