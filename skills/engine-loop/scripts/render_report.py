#!/usr/bin/env python3
"""Write the weekly report — same six sections, every week, per workflow.

Each workflow folder gets its own report in its own reports/ (workflows are
self-contained). Run with no --workflow and every folder is rendered.

Per workflow, produces three things:

  <wf>/reports/weekly-YYYY-Www.md   for you to read
  <wf>/reports/latest.json          for the NEXT agent to read
  <wf>/reports/index.csv            one row per report, ever

The JSON is the important one. An agent picking a workflow up next week
should read its `reports/latest.json` before deciding anything — it gets the
numbers, the verdicts and what's still undecided as data, instead of parsing
prose and guessing.

Sections 5 and 6 (proposed changes, next actions) are left for a human or an
agent to fill in. The script does arithmetic; it does not have opinions.

Re-running in the same ISO week regenerates (overwrites) that week's report —
that's how the weekly job stays idempotent. To keep more than one report in a
week — a mid-week check, a per-campaign cut — pass --tag and it gets its own
slug: weekly-2026-W31-launch.md.

Usage:
    render_report.py [--days 7] [--workspace PATH] [--workflow NAME] [--tag NAME]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_arms import find_workspace, rows, tally, judge, outlier_note, as_float  # noqa: E402
from wsfind import find_workflow_dir, list_workflow_dirs, workflow_meta  # noqa: E402

NEEDS_HUMAN = "_TODO — an agent or a human fills this in._"


def parse_ts(v: str) -> datetime | None:
    v = (v or "").strip()
    if not v:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(v, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def window(runs: list[dict], field: str, start: datetime, end: datetime) -> list[dict]:
    out = []
    for r in runs:
        ts = parse_ts(r.get(field, ""))
        if ts and start <= ts < end:
            out.append(r)
    return out


def summarise(runs: list[dict]) -> dict:
    measured = [as_float(r.get("metric_value")) for r in runs]
    measured = [m for m in measured if m is not None]
    by_source: dict[str, int] = {}
    by_metric: dict[str, dict] = {}
    for r in runs:
        if (r.get("metric_value") or "").strip():
            s = (r.get("metric_source") or "?").strip() or "?"
            by_source[s] = by_source.get(s, 0) + 1
            val = as_float(r.get("metric_value"))
            if val is not None:
                name = (r.get("primary_metric") or "?").strip() or "?"
                slot = by_metric.setdefault(name, {"total": 0.0, "measured": 0})
                slot["total"] = round(slot["total"] + val, 2)
                slot["measured"] += 1
    return {
        "runs": len(runs),
        "measured": len(measured),
        "total": round(sum(measured), 2),
        "mean": round(sum(measured) / len(measured), 2) if measured else 0.0,
        "by_source": by_source,
        "by_metric": by_metric,
    }


def counts(runs: list[dict], key: str) -> dict:
    out: dict[str, int] = {}
    for r in runs:
        k = (r.get(key) or "").strip() or "—"
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def render_workflow(wd, days: int, tag: str) -> None:
    runs = rows(wd / "runs" / "index.csv")

    now = datetime.now(timezone.utc)
    end, start = now, now - timedelta(days=days)
    prev_start = start - timedelta(days=days)

    this_runs = window(runs, "created_at", start, end)
    prev_runs = window(runs, "created_at", prev_start, start)
    shipped = window(runs, "published_at", start, end)

    metric_name = (workflow_meta(wd).get("primary_metric") or "").strip()

    this_sum, prev_sum = summarise(this_runs), summarise(prev_runs)

    # experiments — same rules as score_arms: cohort decides, all-time is context
    experiments = []
    cfg = wd / "experiments.json"
    if cfg.is_file():
        for exp in json.loads(cfg.read_text()).get("experiments", []):
            if exp.get("status") != "live":
                continue
            min_runs = int(exp.get("min_runs_per_arm", 15))
            ratio = float(exp.get("win_ratio", 1.2))
            direction = exp.get("direction", "up")
            aggregate = exp.get("aggregate", "mean")
            cohort = tally(runs, exp["id"], True, exp.get("started", ""))
            verdict, why = judge(cohort, min_runs, ratio, direction, aggregate)
            experiments.append({
                "id": exp["id"], "workflow": wd.name,
                "channel": (exp.get("channel") or "").strip(),
                "variable": exp.get("variable", ""), "verdict": verdict, "why": why,
                "min_runs_per_arm": min_runs, "win_ratio": ratio,
                "direction": direction, "aggregate": aggregate,
                "caution": outlier_note(cohort, aggregate),
                "arms": {k: {"runs": v["n"], "measured": v["measured"],
                             "mean": round(v["mean"], 2),
                             "median": round(v["median"], 2)}
                         for k, v in cohort.items()},
            })

    awaiting = sum(1 for r in runs
                   if (r.get("status") or "") == "published"
                   and not (r.get("metric_value") or "").strip())

    iso = now.isocalendar()
    slug = f"weekly-{iso[0]}-W{iso[1]:02d}"
    if tag.strip():
        slug += "-" + re.sub(r"[^A-Za-z0-9_-]+", "-", tag.strip()).strip("-")

    data = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report": slug,
        "workflow": wd.name,
        "period": {"from": start.strftime("%Y-%m-%d"),
                   "to": end.strftime("%Y-%m-%d"), "days": days},
        "primary_metric": metric_name,
        "ran": {"total": len(this_runs),
                "by_channel": counts(this_runs, "channel")},
        "shipped": [{"run_id": r.get("run_id", ""), "channel": r.get("channel", ""),
                     "url": r.get("url", "")} for r in shipped],
        "metrics": {"this_period": this_sum, "previous_period": prev_sum},
        "experiments": experiments,
        "awaiting_metrics": awaiting,
        "needs_human": ["proposed_changes", "next_actions"],
    }

    # --- markdown -----------------------------------------------------------
    L = [f"# {wd.name} — {slug}", "",
         f"_{data['period']['from']} → {data['period']['to']}_  ·  "
         f"generated {data['generated_at']}", "",
         "## 1. What ran", ""]

    if this_runs:
        L.append(f"**{len(this_runs)}** runs.")
        L += [""] + [f"- {k}: {v}" for k, v in data["ran"]["by_channel"].items()]
    else:
        L.append("Nothing. That's the finding.")

    L += ["", "## 2. What shipped", ""]
    if shipped:
        for s in data["shipped"]:
            L.append(f"- `{s['run_id']}` — {s['channel']} — {s['url'] or '_no URL recorded_'}")
    else:
        L.append("Nothing published this period.")

    L += ["", "## 3. Numbers", ""]
    if metric_name:
        delta = this_sum["total"] - prev_sum["total"]
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "—")
        L += [f"Primary metric: **{metric_name}**", "",
              "| | this period | previous |",
              "|---|---|---|",
              f"| total | {this_sum['total']} | {prev_sum['total']} |",
              f"| mean per run | {this_sum['mean']} | {prev_sum['mean']} |",
              f"| measured runs | {this_sum['measured']}/{this_sum['runs']} | "
              f"{prev_sum['measured']}/{prev_sum['runs']} |", "",
              f"{arrow} {abs(round(delta, 2))} vs previous period."]
        if len(this_sum["by_metric"]) > 1:
            L += ["", "> Runs this period recorded **different metrics** — the "
                      "totals above mix them and should not be read as one number:"]
            L += [f"> - {name}: {s['total']} across {s['measured']} runs"
                  for name, s in this_sum["by_metric"].items()]
        if this_sum["by_source"]:
            src = ", ".join(f"{k}: {v}" for k, v in this_sum["by_source"].items())
            L += ["", f"Sources: {src}."]
        if this_sum["measured"] < this_sum["runs"]:
            L += ["", f"> {this_sum['runs'] - this_sum['measured']} runs this period have no "
                      f"number yet. Treat everything above as partial."]
    else:
        L.append("_No primary metric set in this workflow's `workflow.json`._")

    if awaiting:
        L += ["", f"`{awaiting}` published runs are still waiting on a number "
                  f"— run `due_metrics.py` to see which are past their window."]

    L += ["", "## 4. Experiments", ""]
    if experiments:
        for e in experiments:
            scope = f" · {e['channel']}" if e["channel"] else ""
            L += [f"### {e['id']} — {e['workflow']}{scope} · {e['variable']}", ""]
            if e["arms"]:
                L += ["| arm | runs | measured | mean | median |", "|---|---|---|---|---|"]
                better = 1 if e["direction"] == "down" else -1
                key = "median" if e["aggregate"] == "median" else "mean"
                for arm, s in sorted(e["arms"].items(), key=lambda kv: better * kv[1][key]):
                    L.append(f"| {arm} | {s['runs']} | {s['measured']} | "
                             f"{s['mean']} | {s['median']} |")
                L.append("")
            L += [f"**{e['verdict']}** — {e['why']}", ""]
            if e["caution"]:
                L += [f"> {e['caution']}", ""]
    else:
        L.append("_No live experiments._")

    L += ["## 5. Proposed changes", "", NEEDS_HUMAN, "",
          "> A concrete diff to this workflow's config, or 'none'. If an "
          "experiment above is decided: promote the winner, move the loser to "
          "`templates/losers/`, write a challenger with its hypothesis. If a "
          "finding generalises beyond this workflow, add a line to "
          "`shared/insights.md`.", "",
          "## 6. Next actions", "", NEEDS_HUMAN, "", "> Three or fewer.", ""]

    reports = wd / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    md_path = reports / f"{slug}.md"
    md_path.write_text("\n".join(L))
    (reports / "latest.json").write_text(json.dumps(data, indent=2) + "\n")

    index = reports / "index.csv"
    new = not index.is_file()
    with index.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["report", "generated_at", "period_from", "period_to", "runs",
                        "shipped", "metric", "metric_total", "measured", "awaiting",
                        "decided_experiments"])
        w.writerow([slug, data["generated_at"], data["period"]["from"],
                    data["period"]["to"], len(this_runs), len(shipped), metric_name,
                    this_sum["total"], this_sum["measured"], awaiting,
                    sum(1 for e in experiments if e["verdict"] == "decided")])

    print(md_path)
    print(reports / "latest.json", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--workflow", default="",
                    help="render one workflow folder (default: all)")
    ap.add_argument("--tag", default="",
                    help="suffix for the report slug — a second report in the "
                         "same week overwrites the first unless it has one")
    a = ap.parse_args()

    ws = find_workspace(a.workspace)
    if a.workflow:
        dirs = [find_workflow_dir(ws, a.workflow)]
    else:
        dirs = list_workflow_dirs(ws)
        if not dirs:
            sys.exit("error: no workflow folders in this workspace")

    for wd in dirs:
        render_workflow(wd, a.days, a.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
