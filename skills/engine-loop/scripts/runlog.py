#!/usr/bin/env python3
"""Create runs and record what they earned.

runs/index.csv is the spine of the whole system: one row per thing you ever
made, the arm it used, and the number it got. Everything the loop knows, it
knows from this file — so every workflow writes here, always.

Usage:
    runlog.py new --workflow seo --channel blog \
                  [--experiment exp-001 --arm default --template first-touch.txt]
    runlog.py metric --run 2026-08-01-001-seo --value 340 --source browser
    runlog.py publish --run 2026-08-01-001-seo --url https://... [--title "..."]
    runlog.py verdict --run 2026-08-01-001-seo --verdict good

`--source` is required when recording a metric, and it is not decoration:
a report that can't tell a measured number from a typed-in one is worse
than no report.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ["run_id", "created_at", "skill", "channel", "experiment_id", "arm",
           "template_used", "status", "published_at", "url", "primary_metric",
           "metric_value", "metric_source", "metrics_fetched_at", "human_verdict"]

SOURCES = ("api", "browser", "apify", "manual")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_workspace(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if (p / "config").is_dir():
            return p
        sys.exit(f"error: no config/ in {p}")
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / "workflows" / "config").is_dir():
            return base / "workflows"
        if base == Path.home():
            break
    sys.exit("error: no workspace found — pass --workspace")


def read_rows(idx: Path) -> list[dict]:
    if not idx.is_file():
        return []
    with idx.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(idx: Path, rows: list[dict]) -> None:
    idx.parent.mkdir(parents=True, exist_ok=True)
    with idx.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})


def primary_metric(ws: Path) -> str:
    ch = ws / "config" / "channels.json"
    if ch.is_file():
        try:
            return (json.loads(ch.read_text()).get("primary_metric") or "").strip()
        except json.JSONDecodeError:
            pass
    return ""


def cmd_new(ws: Path, a) -> int:
    idx = ws / "runs" / "index.csv"
    rows = read_rows(idx)
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
    (folder / "metrics.json").write_text(json.dumps({
        "run_id": run_id, "metric": primary_metric(ws),
        "value": None, "source": None, "fetched_at": None,
    }, indent=2) + "\n")
    (folder / "notes.md").write_text(
        f"# {run_id}\n\n## What I was going for\n\n\n## Verdict\n\n"
        f"<!-- one word in index.csv: good | meh | bad -->\n")

    rows.append({
        "run_id": run_id, "created_at": now(), "skill": f"engine-{a.workflow}",
        "channel": a.channel, "experiment_id": a.experiment, "arm": a.arm,
        "template_used": a.template, "status": "draft",
        "primary_metric": primary_metric(ws),
    })
    write_rows(idx, rows)

    print(run_id)
    print(f"{folder}", file=sys.stderr)
    return 0


def update(ws: Path, run_id: str, changes: dict) -> dict:
    idx = ws / "runs" / "index.csv"
    rows = read_rows(idx)
    for r in rows:
        if r.get("run_id") == run_id:
            r.update(changes)
            write_rows(idx, rows)
            return r
    sys.exit(f"error: no run {run_id} in runs/index.csv")


def cmd_metric(ws: Path, a) -> int:
    if a.source not in SOURCES:
        sys.exit(f"error: --source must be one of {', '.join(SOURCES)}")
    row = update(ws, a.run, {"metric_value": a.value, "metric_source": a.source,
                             "metrics_fetched_at": now()})
    mfile = ws / "runs" / a.run / "metrics.json"
    if mfile.is_file():
        data = json.loads(mfile.read_text())
        data.update({"value": a.value, "source": a.source, "fetched_at": now()})
        mfile.write_text(json.dumps(data, indent=2) + "\n")
    print(f"{a.run}: {row.get('primary_metric') or 'metric'} = {a.value} ({a.source})")
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
    print(f"{a.run}: published → {a.url}")
    return 0


def cmd_verdict(ws: Path, a) -> int:
    if a.verdict not in ("good", "meh", "bad"):
        sys.exit("error: --verdict must be good, meh or bad")
    update(ws, a.run, {"human_verdict": a.verdict})
    print(f"{a.run}: {a.verdict}")
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
    m.add_argument("--source", required=True, help="|".join(SOURCES))

    p = sub.add_parser("publish", help="mark it live")
    p.add_argument("--run", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--channel", default="")
    p.add_argument("--title", default="")
    p.add_argument("--notes", default="")

    v = sub.add_parser("verdict", help="your one-word call")
    v.add_argument("--run", required=True)
    v.add_argument("--verdict", required=True, help="good | meh | bad")

    a = ap.parse_args()
    ws = find_workspace(a.workspace)
    return {"new": cmd_new, "metric": cmd_metric,
            "publish": cmd_publish, "verdict": cmd_verdict}[a.cmd](ws, a)


if __name__ == "__main__":
    sys.exit(main())
