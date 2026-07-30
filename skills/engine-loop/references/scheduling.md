# Scheduling the loop

The loop only compounds if it runs without you remembering to run it.

---

## What can and can't be automated

Be clear about this before wiring anything up, because it decides which kind of job you need.

| Step | Unattended script? | Why |
|---|---|---|
| Score experiments | **yes** | reads each workflow's `runs/index.csv`, pure arithmetic |
| Render the report | **yes** | same |
| List what's owed a number | **yes** | `due_metrics.py` checks each channel's window (72h default) |
| **Read numbers off TikTok / LinkedIn / Instagram / X** | **no** | needs a logged-in browser, which needs an agent |
| Write a challenger template | **no** | needs judgement |
| Generate next week's inputs | **no** | same |

So there are two shapes. Most people want both.

---

## Shape 1 — the deterministic job

`weekly.sh` scores and reports from whatever numbers are already recorded. It never posts, sends or promotes anything, so it's safe to leave running.

```bash
~/code/gtm-engine/skills/engine-loop/scripts/weekly.sh /path/to/your-project/workflows
```

### macOS: launchd

macOS is aggressive about killing cron jobs, so use launchd. Save as `~/Library/LaunchAgents/com.gtm-engine.weekly.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.gtm-engine.weekly</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/YOU/code/gtm-engine/skills/engine-loop/scripts/weekly.sh</string>
    <string>/Users/YOU/code/YOUR-PROJECT/workflows</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key><integer>1</integer>
    <key>Hour</key><integer>8</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key><string>/tmp/gtm-engine-weekly.log</string>
  <key>StandardErrorPath</key><string>/tmp/gtm-engine-weekly.err</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.gtm-engine.weekly.plist
launchctl start com.gtm-engine.weekly     # test it now
tail /tmp/gtm-engine-weekly.log
```

Absolute paths only — launchd has almost no environment, so `~` won't expand. Replace `/Users/YOU/...` with the output of `echo $HOME` plus your real paths before loading.

### Linux: cron

```cron
0 8 * * 1 /home/you/code/gtm-engine/skills/engine-loop/scripts/weekly.sh /home/you/project/workflows >> /tmp/gtm-weekly.log 2>&1
```

---

## Shape 2 — the agent job

This is the one that actually closes the loop, because it can open a browser and read the numbers.

The contract: **any coding agent that can run headlessly on a schedule, read the installed skills, and drive a logged-in browser.** Claude Code's headless mode (`claude -p`) is the worked example below; other agents have equivalents — swap the invocation, keep the prompt:

```bash
cd /path/to/your-project && claude -p "$(cat <<'EOF'
Run the engine-loop weekly cycle for this workspace.

1. python3 ~/code/gtm-engine/skills/engine-loop/scripts/due_metrics.py
2. For each run it lists as READY: fetch its number the way its channel
   allows — analytics in the browser for social posts, the Gmail thread for
   outreach — and record it with runlog.py metric and the right --source.
   Skip anything due_metrics lists as too early — leave those for next week.
3. python3 ~/code/gtm-engine/skills/engine-loop/scripts/score_arms.py
4. For any DECIDED experiment: move the losing template to that
   workflow's templates/losers/, write a challenger with its hypothesis as a
   header comment, register it in the workflow's experiments.json. Do NOT
   promote the challenger to default — leave that for me.
5. python3 ~/code/gtm-engine/skills/engine-loop/scripts/render_report.py
6. Fill in sections 5 and 6 of the report.
7. Write next week's content ideas into each workflow's inputs/queue/, each
   with the run that justifies it. If a finding generalises across workflows,
   add one line to shared/insights.md.

Never post, never send, never promote an arm. Stop and tell me if anything
looks wrong.
EOF
)"
```

Schedule that the same way as shape 1 — same plist, different `ProgramArguments`.

**Read the report before trusting it** for the first month. An unattended agent that drifts is worse than no automation, and you only notice by reading the output.

---

## Suggested cadence

| Job | When | Which shape |
|---|---|---|
| `due_metrics` + record numbers | daily or every other day | agent |
| `score_arms` + challenger | weekly, Monday morning | agent |
| `render_report` | weekly, after the above | either |
| generate next week's inputs | weekly | agent |

Order matters: fetch before score, score before report. Reporting on stale numbers produces confident, wrong verdicts.

Daily metric collection isn't about speed — it's that runs come due on a rolling basis as they clear their channel's window, and a weekly-only job will always have a few that aged past it and got read late.

---

## How the next agent picks it up

This is the point of writing reports to a fixed place in a fixed shape.

Each workflow's `reports/latest.json` is its handover file. Any agent starting fresh in this workspace should read them **first** (plus `shared/insights.md`) — it gets the period, what ran, what shipped, the metric totals with their sources, every live experiment with its verdict, and how many runs are still owed a number. As data, not prose.

```
<workflow>/reports/
├── latest.json          ← always the most recent. Read this first
├── index.csv            ← one row per report ever: the trend line
└── weekly-2026-W31.md   ← the human-readable one
```

`needs_human` in the JSON lists the sections nobody has filled in yet, so an agent knows what's left rather than guessing whether a blank section means "nothing to say" or "not done".

Keep the shape stable. The comparability across weeks is the whole value — a report that changes format every week is a set of unrelated documents.
