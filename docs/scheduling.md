# Schedulers — the full list

Nothing here compounds if you have to remember to run it. A workflow that runs
when you think of it produces a burst in week one, a gap in week three, and no
verdict ever, because the runs are too clumped to compare.

This page is the **catalogue**: which jobs should exist, which are mandatory,
what each one may and may not do. The **mechanics** are in
[`skills/engine-loop/references/scheduling.md`](../skills/engine-loop/references/scheduling.md).
Read this to decide what to create; read that to create it.

**Create these with your agent's own scheduler.** Claude Code calls them
*scheduled tasks*; other agents have an equivalent. Ask for one by name and the
agent creates it — it already has the tool, the workspace and the logged-in
browser these jobs need:

> Create a daily scheduled task `engine-metrics-social` that runs the engine-loop
> metric pass for the `social` workflow on `~/code/your-project/workflows`.

Pick the **local** kind, not a cloud routine: every job here reads your
workspace off disk, and the metric jobs read analytics from behind your own
login. A cloud run gets a fresh clone and no browser.

## Two kinds of job

| | **Deterministic** | **Agent** |
|---|---|---|
| What runs | a script — `weekly.sh`, `due_metrics.py`, `render_report.py` | another run of your agent, scheduled by itself |
| Can it read TikTok/LinkedIn analytics? | no — needs a logged-in browser | yes |
| Can it write, judge, decide? | no | yes |
| Safe to leave running? | yes, it only reads and reports | yes, **if** it never posts, sends or promotes |

Most schedulers below are agent jobs. That's fine. The safety property isn't
"a script did it" — it's that **nothing publishes, sends or promotes an arm
without a human**, and every job's prompt has to say so out loud.

---

## The rule: split what touches the outside, keep what reads the workspace

Before the list, the principle that decides how many jobs you need:

- **One job per workflow** when it touches the outside world — fetching numbers,
  drafting, publishing. Each workflow reads a *different system* (a browser
  session, a mailbox, Search Console), on a *different clock*, and fails in a
  *different way*. Pooling them means one dead browser session silently costs
  you the outreach numbers too
- **One job for the whole workspace** when it reads what's already on disk and
  reasons across it — scoring, reporting, insights, cross-feeding queues. That
  work is *supposed* to see every workflow at once; splitting it destroys the
  only place cross-workflow learning happens

Everything below follows from that.

---

## Mandatory — metrics per workflow, one weekly for the workspace

Create these as soon as one workflow has shipped anything. Without them the
spine fills with runs that never get a number, and every report says "no runs
measured".

### One metric job per workflow

| Label | When | What it does |
|---|---|---|
| `engine-metrics-<workflow>` | per that workflow's clock | `due_metrics.py --workflow <name>`, then fetch each READY run's number the way *that* channel allows and record it with `runlog.py metric --source`. Skips anything still inside its window |

So `engine-metrics-social`, `engine-metrics-outreach`, `engine-metrics-seo`, one
per workflow folder you actually run. All three loop scripts take `--workflow`,
so this needs no extra machinery.

**Set each one's cadence from its channel's `metric_delay_hours`**, not from a
shared default. Roughly:

| Workflow | Cadence | Because |
|---|---|---|
| `outreach` | daily, working days | replies settle in 24–48h; `metric_delay_hours` 24–48 |
| `social` | daily | 72h window, and runs clear it on a rolling basis |
| `video` | daily | 72h window; watch-through read in the browser |
| `seo` | **weekly, or fortnightly** | Search Console needs weeks — `metric_delay_hours` 336. A daily job here finds nothing 27 days a month |

**Three reasons this beats one job for everything:**

| | Why it matters |
|---|---|
| **Different sources** | Social needs a logged-in browser; outreach needs the mailbox; SEO needs Search Console. One prompt covering all three is long, branchy, and the branch that runs least is the one that quietly breaks |
| **Different clocks** | Outreach replies settle in 24–48h, so daily is right. Search Console needs weeks — a daily SEO metric job spends 27 days a month finding nothing. Set each job's cadence to the channel's `metric_delay_hours`, not to a shared default |
| **Different failures** | A dead browser session should cost you social numbers, not the outreach ones. Isolated jobs fail visibly and separately; one job fails once and hides the rest |

There's also a mechanical reason: `runs/index.csv` is rewritten whole on every
update, so two jobs writing the **same** workflow concurrently lose rows. Per
workflow, that can't happen — each job owns one file. Just don't schedule two
jobs against the same workflow.

### One weekly job for the workspace

| Label | When | Shape | What it does |
|---|---|---|---|
| `engine-weekly` | weekly, Mon morning | deterministic (`weekly.sh`) + agent | Scores whatever is live, renders each workflow's report, then — as the agent half — fills report sections 5 and 6, writes next week's `inputs/queue/`, and adds to `shared/insights.md` |

**This one stays whole-workspace on purpose.** Its scoring and reporting are
pure arithmetic over files that are already written — nothing to conflict. And
its agent half is the *only* place the workflows meet: reading the sibling
reports side by side, noticing that the hook winning on social explains the
video numbers, writing one workflow's finding into another's queue. Split it per
workflow and you get four jobs that each know a quarter of the story.

If you're running four or more workflows and the weekly agent pass is getting
long, split the **queue-writing** half per workflow and keep one cross-reading
pass — not the other way round.

**Order matters.** Fetch before score, score before report. Reporting on stale
numbers produces confident, wrong verdicts — so schedule the metric jobs earlier
in the day than `engine-weekly`, or the Monday report scores last week's data.

---

## Per-workflow — optional, and worth it once the workflow is settled

None of these are needed on day one. Add one when its workflow is producing
something you'd ship, and when doing that step by hand has become the thing you
skip. A scheduler wrapped around a workflow you're still figuring out just
automates the wrong version.

**Each of these is *in addition to* that workflow's `engine-metrics-<workflow>`
job above** — the metric job records numbers and nothing else; these do the
workflow's own work.

### SEO

| Label | When | What it does | Never |
|---|---|---|---|
| `engine-seo-subjects` | weekly | Mines the communities where the audience posts for questions worth answering; writes candidates to `seo/inputs/queue/` | pick topics nobody asked |
| `engine-seo-backlog` | weekly | Keeps ≥20 validated titles in `seo/inputs/backlog.csv` — re-validates what's there, drops what died, adds from last week's research | inflate the count with filler |
| `engine-seo-publish` | weekly | Takes what's in the approved publishing folder, commits, pushes, triggers the rebuild | publish anything the user hasn't approved into that folder |

The publish job is the one with teeth: a git push is easy to do by accident and
hard to undo from someone's index. Scope it to a folder the user moves files
into deliberately.

### Social

| Label | When | What it does | Never |
|---|---|---|---|
| `engine-social-subjects` | daily | The daily twelve: 4 subjects from Reddit, 4 from the `rss_feeds` in `social/sources.json`, 4 variations of the structures in `inputs/swipe/` and `inputs/best/`. Then rates all twelve against `sources.json` → `rating_criteria` and keeps **one**, killing the rest in place with their scores | keep "the best three". One survivor a day is the point — the filter is the job |
| `engine-social-weekly` | weekly | Drafts the batch from `social/inputs/queue/`, runs the anti-slop pass, leaves them for review | post. LinkedIn and X drafts go to the user; Bluesky posts only after per-post approval |

### Video

| Label | When | What it does | Never |
|---|---|---|---|
| `engine-video-app-hooks` | weekly | Reads what earned watch-through and rewrites the hook library from it, against the rules in `engine-video/references/hook-guide.md` | promote a template to default |
| `engine-video-info-source` | daily | Pulls new items from the text source (RSS, subreddit, your own blog) into `inputs/source-texts/` — only if the informative workflow *fetches* its source rather than being handed one | render or upload anything |

Rendering is deliberately not on a scheduler: it's slow, disk-hungry, and it's
the step where a human eye is cheapest.

### Outreach

| Label | When | What it does | Never |
|---|---|---|---|
| `engine-outreach-daily` | daily, working days | Drafts `<n>` personalised emails into the user's mail system, updates the CRM | send. Not with permission, not "just this once" |
| `engine-outreach-leads` | weekly | Keeps the list alive: **finds** new leads from this workflow's `sources.json` and dedupes them against the CRM, **enriches** thin rows (missing email or role, empty or stale `research` / `research_source` / `researched_at`), and **retires** the ones that no longer fit — `status=closed` with the reason in `notes` | delete a row, contact anyone, or re-add someone with a `sent_at` or `status=closed` |

Pick `<n>` deliberately — a daily job drafting 50 emails produces a mailbox
nobody reviews, which is the same as not doing outreach.

The leads job is what stops the drafting job running dry, and it's list hygiene
only — it writes `crm.csv` and nothing else. Give it a different hour from
`engine-outreach-daily` so two jobs never write that file at once, and tell it
what "no longer fits" means for this business; left undefined, an agent prunes
either nobody or the wrong people. Retiring is a status change, never a
deletion — a deleted row is a person who gets contacted again next quarter.

**Outreach has no second *reply* job.** Reading the replies *is* the metric fetch,
so it belongs to `engine-metrics-outreach` above: a reply is `--value 1` plus
`replied_at`, a closed sequence with no reply is the zero. Running a separate
weekly job to "check replies" means two jobs writing the same `runs/index.csv`
and the same CRM — which is exactly the collision the per-workflow split exists
to prevent.

---

## Rules every scheduled job follows

1. **Never post, send, deploy or promote.** A job may draft, stage, score,
   report and queue. The last click is a human's, and the prompt says so
2. **The prompt stands alone.** Every scheduled run starts with no memory of
   the conversation that created it — name the workspace path, the commands in
   order, and the never-rules inside the prompt itself
3. **Log to a file** and read it for the first month. An unattended agent that
   drifts is worse than no automation, and you only notice by reading output
4. **Idempotent.** Re-running in the same period regenerates rather than
   duplicating — `render_report.py` overwrites that ISO week's report on purpose
5. **One writer at a time.** `runs/index.csv` is rewritten whole on every
   update, so two jobs writing the same workflow concurrently will silently lose
   rows. Stagger the schedules
6. **Fail loudly, do nothing quietly.** A job that can't reach a platform should
   leave the cell empty and say so, never guess a number

## When a job generates a batch: propose, validate, re-propose

The rules above keep a job from doing damage. This one keeps it from producing
**junk**, and it's the pattern that makes unattended generation trustworthy —
whether the batch is ten video themes, seven post subjects, twenty article
titles or a list of leads.

Attended, you catch the bad item yourself. Unattended, nobody does — and the
specific thing that goes wrong is never creativity, it's **memory**: the model
proposes something used three weeks ago, or twice inside the same batch, or four
characters too long for the layout. Asking it to "check what we've already done"
across four hundred previous items works until it doesn't, silently.

So split the job by what each side is actually good at:

| The agent | A small script |
|---|---|
| Proposes the items — **it is the generator.** Never hardcode a list of themes or subjects into a prompt: a static list runs out, a model doesn't | Decides which proposals are acceptable, against the rules you can state mechanically |
| Owns the rules that need taste: is this interesting, does it fit the brand, would anyone care | Owns already-used (check the registry), duplicated inside this batch, too long, missing a field, banned term, wrong shape |

The loop:

1. The agent writes its proposal to a file — `<workflow>/inputs/queue/` or a
   scratch file for this run
2. The script reads it and emits a **verdict per item, with a reason** —
   `dup-registry`, `dup-in-batch`, `too-long(47)`, `missing-proof`, `already-published`
3. Everything that passed proceeds immediately. For the failures, the agent
   **re-proposes only those**, with the reasons in hand — not the whole batch
4. **Cap it at two or three rounds.** If an item still won't validate, drop it,
   log that it was dropped, and carry on with a smaller batch. An uncapped
   reconcile loop is how a nightly job burns until morning

Two things that make it work in practice: the script writes **why**, not just
pass/fail, or round two repeats round one's mistake; and the registry it checks
against is a file that survives runs — the workflow's `runs/index.csv`, its
`crm.csv`, its `backlog.csv`, or a plain list of what's been used. That file is
the memory the model doesn't have.

Where this already exists in the repo, use it instead of writing another:
`combo_check.py` is exactly this validator for video configs, and the CRM check
before every outreach draft is the same idea by hand.

**Say what got dropped.** A batch that quietly came back with six items instead
of ten reads as success. One line in the report — *"3 dropped: 2 duplicates, 1
over length"* — is what turns that into a signal about the queue.

---

## Housekeeping

One optional job, worth adding once video is running weekly:

| Label | When | What it does | Never |
|---|---|---|---|
| `engine-cleanup` | weekly or monthly | Delete artifacts older than N days (30 is a reasonable default) from each workflow's publish folder, report how much was reclaimed | touch `runs/`, `inputs.json`, any CSV, or anything outside those folders |

A publish folder holds shipped artifacts and nothing else — no state, no
configs, no metrics — which is exactly why it's the only thing safe to put on a
timer. **Resolve the paths before you write the prompt**: each workflow's
`published_dir` in its `workflow.json`, defaulting to `published/<workflow>/`,
and skip any set to `"none"`. Then hardcode the resolved list into the prompt
and say what's out of bounds — "clean up old files" is a dangerous instruction
to give an agent with a shell, and a wildcard it resolves itself is worse.

Ask before creating it. Some people want their year of videos on disk, and disk
is cheap; the job is for the ones who'd rather not think about it.

## A sane starting set

Don't create ten jobs on setup day. In order:

1. `engine-metrics-<workflow>` for the **one** workflow you're running — as soon
   as it has published anything
2. `engine-weekly` — same week
3. One content job for that same workflow (subjects, backlog, drafting)
4. A second `engine-metrics-<workflow>` only when you start a second workflow —
   on *its* clock, not a copy of the first one's

Running one workflow means two jobs, not ten. The per-workflow split is what
keeps that true as you add the third and fourth: you add one metric job at a
time instead of growing one prompt until nobody can read it.

## Checking they're alive

Ask the agent to list its scheduled tasks — it reports each one's schedule, when
it last ran, and when it runs next. Both products also keep a per-task run
history, including **skipped** runs with the reason (machine asleep, previous
run still going).

Check that history after the first firing, then monthly. A task that fires and
stalls on a permission prompt looks identical to one that's working until you
look.

A job that's loaded but silently failing looks identical to a job that's working
until you read the log. Check it after the first firing, then monthly.
