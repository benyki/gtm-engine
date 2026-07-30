#!/usr/bin/env python3
"""Create runs and record what they earned.

runs/index.csv is the spine of the whole system: one row per thing you ever
made, the arm it used, and the number it got. Everything the loop knows, it
knows from this file — so every workflow writes here, always.

Usage:
    runlog.py new --workflow seo --channel blog \
                  [--experiment exp-001 --arm default --template first-touch.txt]
    runlog.py metric --run 2026-08-01-001-seo --value 340 --source browser
    runlog.py publish --run 2026-08-01-001-seo [--url https://...] [--title "..."]
    runlog.py verdict --run 2026-08-01-001-seo --verdict good

`--source` is required when recording a metric, and it is not decoration:
a report that can't tell a measured number from a typed-in one is worse
than no report. Name the actual system that produced the number —
`browser`, `api`, `search_console`, `ga4`, `apify`, `manual`, whatever it
was. Any value is accepted; the point is provenance, not a fixed list.

`--url` is optional on publish: an outreach email has no URL. `publish`
still records the moment it went out, which is what starts the metric
clock in due_metrics.py.

Extra columns are a supported extension point: add `segment`, `language`,
`campaign` or anything else to runs/index.csv and this script preserves
them on every rewrite. Only the columns listed below are ever written by
the script itself.

One writer at a time: every update rewrites the whole CSV, so two agents
or machines logging concurrently will silently lose rows. If you need
concurrent writers, move the spine to a database first (see
engine-loop/references/advanced.md).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wsfind import find_workspace  # noqa: E402

COLUMNS = ["run_id", "created_at", "skill", "channel", "experiment_id", "arm",
           "template_used", "status", "published_at", "url", "primary_metric",
           "metric_value", "metric_source", "metrics_fetched_at", "human_verdict"]

# Suggested values, not a closed set — name the system the number came from.
SUGGESTED_SOURCES = ("api", "browser", "apify", "manual")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_rows(idx: Path) -> tuple[list[dict], list[str]]:
    """Rows plus the header as found — user-added columns included."""
    if not idx.is_file():
        return [], list(COLUMNS)
    with idx.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        header = list(reader.fieldnames or [])
    fields = list(COLUMNS) + [c for c in header if c and c not in COLUMNS]
    return rows, fields


def write_rows(idx: Path, rows: list[dict], fields: list[str]) -> None:
    idx.parent.mkdir(parents=True, exist_ok=True)
    with idx.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in fields})


def primary_metric(ws: Path, channel: str = "") -> str:
    """The metric for this run: the channel's own if set, else the global one."""
    ch = ws / "config" / "channels.json"
    if not ch.is_file():
        return ""
    try:
        data = json.loads(ch.read_text())
    except json.JSONDecodeError:
        return ""
    if channel:
        cfg = (data.get("channels") or {}).get(channel)
        if isinstance(cfg, dict):
            per = (cfg.get("primary_metric") or "").strip()
            if per:
                return per
    return (data.get("primary_metric") or "").strip()


def cmd_new(ws: Path, a) -> int:
    idx = ws / "runs" / "index.csv"
    rows, fields = read_rows(idx)
    today = datetime.now().strftime("%Y-%m-%d")
    seq = sum(1 for r in rows if r.get("run_id", "").startswith(today)) + 1
    run_id = f"{today}-{seq:03d}-{a.workflow}"

    folder = ws / "runs" / run_id
    (folder / "output").mkdir(parents=True, exist_ok=True)
    (folder / "input.json").write_text(json.dumps({
        "run_id": run_id, "created_at": now(), "workflow": a.workflow,
        "channel": a.channel, "experiment_id": a.experiment, "arm": a.arm,
        "template_used": a.template, "notes": a.notes,
    }, indent=2) + "\n")
    # metrics.json is the open half of the record: index.csv keeps ONE primary
    # number; secondary metrics (watch-through rate, comments, positions) and
    # every re-read go here. Add keys freely — the script only manages
    # value/source/fetched_at/history.
    (folder / "metrics.json").write_text(json.dumps({
        "run_id": run_id, "metric": primary_metric(ws, a.channel),
        "value": None, "source": None, "fetched_at": None,
        "history": [], "secondary": {},
    }, indent=2) + "\n")
    (folder / "notes.md").write_text(
        f"# {run_id}\n\n## What I was going for\n\n\n## Verdict\n\n"
        f"<!-- one word in index.csv — e.g. good | meh | bad; any scale "
        f"works if you keep it consistent -->\n")

    rows.append({
        # The column is named "skill" for historical compatibility; it records
        # the workflow name itself, whether or not a dedicated skill exists.
        "run_id": run_id, "created_at": now(), "skill": a.workflow,
        "channel": a.channel, "experiment_id": a.experiment, "arm": a.arm,
        "template_used": a.template, "status": "draft",
        "primary_metric": primary_metric(ws, a.channel),
    })
    write_rows(idx, rows, fields)

    print(run_id)
    print(f"{folder}", file=sys.stderr)
    return 0


def update(ws: Path, run_id: str, changes: dict) -> dict:
    idx = ws / "runs" / "index.csv"
    rows, fields = read_rows(idx)
    for r in rows:
        if r.get("run_id") == run_id:
            r.update(changes)
            write_rows(idx, rows, fields)
            return r
    sys.exit(f"error: no run {run_id} in runs/index.csv")


def cmd_metric(ws: Path, a) -> int:
    source = a.source.strip()
    if not source:
        sys.exit("error: --source can't be empty — name where the number came from")
    row = update(ws, a.run, {"metric_value": a.value, "metric_source": source,
                             "metrics_fetched_at": now()})
    mfile = ws / "runs" / a.run / "metrics.json"
    if mfile.is_file():
        data = json.loads(mfile.read_text())
        entry = {"value": a.value, "source": source, "fetched_at": now()}
        data.update(entry)
        # Every read is appended, so a later re-read never erases the curve.
        data.setdefault("history", []).append(entry)
        mfile.write_text(json.dumps(data, indent=2) + "\n")
    print(f"{a.run}: {row.get('primary_metric') or 'metric'} = {a.value} ({source})")
    return 0


def cmd_publish(ws: Path, a) -> int:
    stamp = now()
    update(ws, a.run, {"status": "published", "published_at": stamp, "url": a.url})
    pub = ws / "state" / "published.csv"
    exists = pub.is_file()
    pub.parent.mkdir(parents=True, exist_ok=True)
    with pub.open("a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["run_id", "channel", "url", "published_at", "title", "notes"])
        w.writerow([a.run, a.channel, a.url, stamp, a.title, a.notes])
    print(f"{a.run}: published" + (f" → {a.url}" if a.url else ""))
    return 0


def cmd_verdict(ws: Path, a) -> int:
    verdict = a.verdict.strip()
    if not verdict:
        sys.exit("error: --verdict can't be empty")
    # good | meh | bad is the suggested scale, not a rule — use whatever
    # taxonomy you'll actually keep consistent (keep/kill, 1-5, ...).
    update(ws, a.run, {"human_verdict": verdict})
    print(f"{a.run}: {verdict}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace")
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="start a run")
    n.add_argument("--workflow", required=True)
    n.add_argument("--channel", default="")
    n.add_argument("--experiment", default="")
    n.add_argument("--arm", default="")
    n.add_argument("--template", default="")
    n.add_argument("--notes", default="")

    m = sub.add_parser("metric", help="record what it earned")
    m.add_argument("--run", required=True)
    m.add_argument("--value", required=True)
    m.add_argument("--source", required=True,
                   help="where the number came from — e.g. "
                        + ", ".join(SUGGESTED_SOURCES)
                        + ", search_console, ga4 (free text)")

    p = sub.add_parser("publish", help="mark it live (posted, deployed, or sent)")
    p.add_argument("--run", required=True)
    p.add_argument("--url", default="",
                   help="public URL if one exists — an email has none")
    p.add_argument("--channel", default="")
    p.add_argument("--title", default="")
    p.add_argument("--notes", default="")

    v = sub.add_parser("verdict", help="your one-word call")
    v.add_argument("--run", required=True)
    v.add_argument("--verdict", required=True,
                   help="free text — good | meh | bad is the suggested scale")

    a = ap.parse_args()
    ws = find_workspace(a.workspace)
    return {"new": cmd_new, "metric": cmd_metric,
            "publish": cmd_publish, "verdict": cmd_verdict}[a.cmd](ws, a)


if __name__ == "__main__":
    sys.exit(main())
