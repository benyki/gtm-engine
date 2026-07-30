---
name: engine-loop
description: The compounding loop for gtm-engine. Pulls metrics in (platform API, browser, or Apify), scores A/B arms, promotes winners and retires losers to a losers/ folder, writes a new challenger template with a stated hypothesis, generates next week's content inputs from what performed, and renders the weekly report. Use when the user says "run the loop", "score my experiments", "fetch my numbers", "weekly report", "which version is winning", or asks what to make next.
---

# engine-loop

Turns runs into decisions. Four jobs; run them in this order, because each depends on the one before.

| Job | Cadence | Command |
|---|---|---|
| fetch metrics | daily | `due_metrics.py` → read → `runlog.py metric` |
| score + challenge | weekly | `score_arms.py`, then act on the verdict |
| generate inputs | weekly | see *What to make next* |
| report | weekly | `render_report.py` |

All scripts live in `scripts/` and find the workspace automatically from the current directory. `weekly.sh` chains the deterministic ones.

**Starting fresh in a workspace you don't know? Read `reports/latest.json` first.** It gives you the last period's runs, what shipped, the metric totals and their sources, every live experiment with its verdict, and how many runs are still owed a number — as data. Don't reconstruct that by reading CSVs.

---

## What every workflow owes the loop

Workflows differ — a LinkedIn post has a public URL and an analytics screen, an outreach email has neither — and the loop doesn't care, as long as every workflow leaves the same three traces in the workspace:

1. **A run at creation.** `runlog.py new`, with the experiment, arm and template actually used. A piece of work that isn't in `runs/index.csv` doesn't exist to the loop
2. **A live moment.** `runlog.py publish` when it goes out, whatever "out" means for that workflow — posted, deployed, or sent. Pass `--url` when one exists; an email has none and publishes without it. Either way, this is what starts the 72-hour clock
3. **One number, 72h+ later.** `runlog.py metric` with `--source`. A written `metric_value` — zero counts — is what marks a run as analysed. `due_metrics.py` lists exactly the live runs that don't have one yet, so nothing is measured twice and nothing is forgotten

*How* the number is fetched is the part that adapts: an analytics page in the browser for social, the Gmail thread for outreach replies, Search Console for articles. The traces are the contract; the fetching is judgement. When a new or unusual workflow shows up, map it onto these three traces rather than forcing it through another workflow's mechanics.

---

## Getting the numbers

Start here, always:

```bash
python3 scripts/due_metrics.py
```

It lists published runs that are **72+ hours old and have no number yet**, and separately the ones still too young. Only read numbers for the first list.

**The 72-hour rule is not a guideline.** LinkedIn, TikTok, Instagram and X all keep distributing a post for days, and the curve differs per post. A number read at 24 or 48 hours mostly records what time of day you posted. Once it's in `index.csv` nothing marks it as early, and it skews every verdict from then on. Under 72 hours: leave the cell empty. It'll come round.

Three ways to get the number, in this order. **Always record which one you used** — `runlog.py metric` requires `--source` for exactly this reason. A report that can't distinguish a measured number from a typed-in one isn't worth reading.

**1. Platform API** — where it's free and already connected. Gmail for replies, Search Console for clicks and impressions, YouTube Data API. Exact and cheap. Use it when it's there.

**2. Browser** — the normal case, and it works well. TikTok, Instagram, LinkedIn and X all show analytics behind the user's own login, and reading them off the page is reliable. No API keys, no developer accounts, no cost.

Open the post's analytics view, read the numbers, then:

```bash
python3 scripts/runlog.py metric --run 2026-08-01-003-video --value 4200 --source browser
```

This is a first-class option, not a fallback. For someone with forty posts, browser reading is correct and an API integration is over-engineering.

**3. Apify** — paid, structured, precise. Worth it once hand-reading is the bottleneck, or when they want competitor and audience data rather than just their own. Browser until it hurts, then Apify.

If a number genuinely can't be fetched, `--source manual` and move on. Recording it honestly is better than leaving the row empty.

---

## Scoring and challenging

```bash
python3 scripts/score_arms.py
```

It reports and nothing else — it never promotes an arm or edits config. Read the verdict, then act.

### If undecided

Say so and stop. `undecided — not enough measured runs: partner 9/15` is a real answer. Do not talk yourself into an early winner; that's how people convince themselves of things that aren't true.

### If decided

Four things, in order:

1. **Promote.** The winning template becomes the base for that workflow.
2. **Retire.** Move the losing template into `templates/<workflow>/losers/`. Runs never read that folder, so it can't come back by accident — but it's kept, because something that lost against one audience often wins against the next.
3. **Write a challenger.** This is the part that matters. Read the winner, the arms that lost, and the numbers that decided it. Then write a *new* template that attacks the winner — usually by pushing the trait that won a little further, or going after the weakness the winner still has.

   **Most challengers should be small.** Once you have winners to protect, you're refining, not reinventing — a different opening line, a tighter ask, a different proof point. Every fifth or sixth experiment, or whenever results have gone flat, put up a genuinely different proposition instead; most of those lose, but they're the only way to find a ceiling you didn't know about. Raise `min_runs_per_arm` as the differences get subtler, or you'll start calling winners out of noise.

   Put the hypothesis in a header comment at the top of the file:

   ```
   # hypothesis: default won on reply rate because it asks for nothing.
   # This one keeps the low ask but leads with a specific observation about
   # their product, testing whether relevance beats brevity.
   ```

   In six weeks that comment is the only reason anyone will remember why the file exists.

4. **Register it** in `config/experiments.json` as a new arm, update `started` to today, and set the old experiment's `decision`.

**Guardrails**
- Two live arms per workflow, maximum. Three arms means three times the data before anything is decided
- You write the challenger automatically; **promoting it to default still needs the user's yes**
- A template you wrote to fill a gap starts as an ordinary arm. It earns default status by winning, not by being new

Full rules, and why each exists: `references/ab-testing.md`.

---

## What to make next

The second loop, and the one people skip. Analytics should decide *what* gets made, not only grade what already was.

Read `runs/index.csv`, the recent metrics, and the last report. Then write the next batch of content configs into `inputs/queue/`, each with a one-line reason pointing at the run that justifies it:

- Which topics, hooks and formats actually earned the metric — and which quietly didn't
- What's saturated: six of these, returns flat, stop
- What the winning arm implies for the next ten pieces
- Adjacent angles not yet tried

The user reviews the queue and approves. They never start from a blank page, and they don't have to remember what worked in March.

---

## The report

```bash
python3 scripts/render_report.py
```

Writes three files:

| File | For |
|---|---|
| `reports/weekly-YYYY-Www.md` | the human |
| `reports/latest.json` | **the next agent** — same content as data |
| `reports/index.csv` | one row per report ever, so the trend is queryable |

Six sections, same order every week. Sections 1–4 are filled in for you (what ran, what shipped, the numbers with their sources, every experiment with its verdict). **Sections 5 and 6 are left blank on purpose** — proposed config changes and next actions need judgement, and they're listed in the JSON under `needs_human` so nobody has to guess whether a blank section means "nothing to say" or "not done yet".

Fill them in after generating. Section 5 is a concrete diff to `config/` or the word "none"; section 6 is three actions or fewer.

**Don't redesign the format.** Comparability week to week is the entire value — a report that changes shape every week is just a pile of unrelated documents.

Reporting stays in the terminal by default. Telegram and WhatsApp are in `references/advanced.md`.

## Scheduling

The loop only compounds if it runs without you remembering. `weekly.sh` is the unattended half — it scores and reports from existing numbers, and never posts, sends or promotes anything.

The half that reads TikTok and LinkedIn analytics needs a browser, so it needs an agent session. `references/scheduling.md` has both: a launchd plist for the deterministic job, and the headless `claude -p` invocation that does the fetching too.

---

## Rules

- **Never invent a number.** No metric is better than a guessed one — it poisons every future verdict
- **Never promote an arm the user hasn't approved**
- **Never delete a template.** Losers move to `losers/`
- **Never mix cohort and all-time.** Rows predating an experiment sit in the default arm and make it look settled when it isn't. Cohort decides; all-time is context
- If `metric_value` is empty for most runs, say that plainly before reporting anything. A verdict on three measured rows is not a verdict
