# Scheduling the loop

The loop only compounds if it runs without you remembering to run it.

---

## What can and can't be automated

Be clear about this before wiring anything up, because it decides which kind of job you need.

| Step | Unattended script? | Why |
|---|---|---|
| Score experiments | **yes** | reads each engine's `runs/index.csv`, pure arithmetic |
| Render the report | **yes** | same |
| List what's owed a number | **yes** | `due_metrics.py` checks each channel's window (72h default) |
| **Read numbers off TikTok / LinkedIn / Instagram / X** | **no** | needs a logged-in browser, which needs an agent |
| Write a challenger template | **no** | needs judgement |
| Generate next week's inputs | **no** | same |

Most of the list is judgement or browser work, which means **most gtm-engine
jobs are agent jobs**. That decides the mechanism.

---

## Create them as local scheduled tasks

Claude Code and Codex both schedule themselves. **Ask the agent to create the
job** — it knows its own scheduler; you only need to tell it what to run:

```
Set up a daily scheduled task called engine-metrics-social that runs the
engine-loop metric pass for the social engine in
~/code/your-project/engines at 08:05.
```

Four things are specific to this system. The rest is your agent's business:

1. **Local, never cloud.** A cloud-run task gets a fresh clone and no browser;
   these jobs read your home off disk and your analytics from behind your
   own login. Not the in-session kind either (`/loop`, automations that live in
   one conversation) — those die with the session
2. **No isolated worktree.** That default is right for code and wrong here: the
   home is *data*, and a run whose `runs/index.csv` lands in a throwaway
   copy has measured nothing. Point the task at the folder containing
   `engines/` and let it write in place
3. **Pre-approve the tools.** Run the task once by hand and grant what it asks
   for permanently, or it stalls mid-run on an approval nobody is there to give
   — which looks exactly like a job that's working. Permissions are capability,
   not intent: the never-post, never-send, never-promote rules go in the prompt
4. **The prompt stands alone.** Each run is a fresh session with no memory of
   the conversation that created it, so name the home path, the commands in
   order, and the boundaries. `<engine>/reports/latest.json` and
   `shared/insights.md` are the handover between runs

### Late runs are fine here

A missed run catches up whenever the machine wakes, so a "9am" job may fire at
11pm. Harmless: `due_metrics.py` selects by how long ago a run published against
its channel's window, not by the clock, and re-rendering a report regenerates
that week in place. **So write prompts in terms of what's due, never "today".**

On a server with no agent app, `claude -p` and `codex exec` run the same prompt
non-interactively.

---

## The weekly task's prompt

Paste this as the task's instructions. It names the home, the order, and
the boundaries, because none of that survives from the conversation that
created it:

```
Run the engine-loop weekly cycle for the home at
~/code/your-project/engines.

1. python3 ~/.agents/skills/engine-loop/scripts/due_metrics.py
2. For each run it lists as READY: fetch its number the way its channel
   allows — analytics in the browser for social posts, the mailbox for
   outreach, Search Console for articles — and record it with
   runlog.py metric and the right --source. Skip anything due_metrics
   lists as too early; it will come round.
3. python3 ~/.agents/skills/engine-loop/scripts/score_arms.py
4. For any DECIDED experiment: move the losing template to that engine's
   templates/losers/, write a challenger with its hypothesis as a header
   comment, register it in the engine's experiments.json. Do NOT promote
   the challenger to default — leave that for me.
5. python3 ~/.agents/skills/engine-loop/scripts/render_report.py
6. Fill in sections 5 and 6 of each report.
7. Write next week's content ideas into each engine's inputs/queue/, each
   with the run that justifies it. If a finding generalises across
   engines, add one line to shared/insights.md.

Never post, never send, never promote an arm. If anything looks wrong, stop
and write it into the report rather than guessing.
```

Note what it doesn't say: nothing about "today" or "this morning". The task may
fire late after the machine was asleep, and every step above is defined by what
is *due*, not by the clock.

**Read the report before trusting it** for the first month. An unattended agent
that drifts is worse than no automation, and you only notice by reading the
output.

---

## Cadence

Which jobs to create, at what cadence, and what each may and may not do:
[`docs/scheduling.md`](../../../docs/scheduling.md) — one
`engine-metrics-<engine>` per engine on that channel's clock, plus one
`engine-weekly` for the home. Two rules that don't change: **fetch before
score, score before report**, and metric jobs run on their own cadence rather
than weekly — runs clear their channel's window on a rolling basis, so a
weekly-only job always reads a few of them late.

---

## How the next agent picks it up

This is the point of writing reports to a fixed place in a fixed shape.

Each engine's `reports/latest.json` is its handover file. Any agent starting fresh in this home should read them **first** (plus `shared/insights.md`) — it gets the period, what ran, what shipped, the metric totals with their sources, every live experiment with its verdict, and how many runs are still owed a number. As data, not prose.

```
<engine>/reports/
├── latest.json          ← always the most recent. Read this first
├── index.csv            ← one row per report ever: the trend line
└── weekly-2026-W31.md   ← the human-readable one
```

`needs_human` in the JSON lists the sections nobody has filled in yet, so an agent knows what's left rather than guessing whether a blank section means "nothing to say" or "not done".

Keep the shape stable. The comparability across weeks is the whole value — a report that changes format every week is a set of unrelated documents.
