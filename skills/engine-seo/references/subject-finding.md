# Subject finding — from nothing to twenty validated titles

`SKILL.md` says *pick a question people actually asked*. This is how you find
twenty of them, prove they're worth writing, and throw away the ones that
aren't.

Run it weekly. The backlog is the product of this file
(`inputs/backlog.csv`) and the writing run just takes the top row.

Scoped to this workflow. `engine-social` has its own version in its own
references — same shape, different signals, its own backlog. Two files that
say similar things is the cost of workflows that can't break each other.

The whole loop:

```
grid → collect → validate → score → kill the weak → multiply the winners
```

---

## 1. The query grid

Start from what the user sells. Write the **product type** the way a stranger
would say it ("time tracking app", "sourdough starter", "freelance invoicing"),
not the way marketing says it. Then run the grid — every row is a real search
shape, and each one finds a different kind of buyer:

| Pattern | Finds | Example |
|---|---|---|
| `how to <job the product does>` | people already trying to do it manually | how to track billable hours |
| `why does <thing> <problem>` | people diagnosing, pre-purchase | why does my invoice get paid late |
| `where to <action>` | people ready to act | where to send invoices for free |
| `<product type> vs <alternative>` | people comparing, high intent | time tracking app vs spreadsheet |
| `best <product type> for <segment>` | people shortlisting | best invoicing app for freelancers |
| `<product type> without <constraint>` | people blocked by a dealbreaker | invoicing without a subscription |
| `is <product type> worth it` | people at the objection stage | is time tracking worth it |
| `how much does <product type> cost` | people budgeting | how much does bookkeeping cost |
| `<competitor> alternative` | people already leaving someone | Toggl alternative |
| `<thing> not working` / `<thing> error` | people in pain right now | invoice reminder not sending |

Store the resolved grid in `inputs/query-patterns.md` — the product type and
segments filled in, so the next pass and the weekly job start from the same
list instead of re-inventing it.

Two multipliers to apply to any row: **segment** (for freelancers, for agencies,
for two-person teams) and **place** (in the UK, in Germany, in euros). Hold
those back until §6 — they're for multiplying winners, not for generating
noise.

## 2. Collect

For each grid row, gather the *actual phrasing* people use. Three sources, in
this order:

**Google autocomplete and People Also Ask.** Type the pattern, don't press
enter. Autocomplete is a frequency-ranked list of how the query is really
finished. PAA boxes are the follow-up questions; each is a candidate on its own.

**Reddit** — `references/browser-research.md`. The phrasing here is unedited,
and a long thread with a thin top answer is the strongest signal in this whole
document.

**YouTube.** Search the pattern and read the view counts. A topic with several
100k-view videos and no decent article is a gap you can fill in an afternoon —
demand is proven, and text competition is weak precisely because everyone
answered it on video.

Write down the phrasing you found, not your tidy rewrite of it. The title comes
later; the question is the record.

## 3. Validate

A candidate is not a subject until you've looked at what already ranks. Open
the SERP and answer three things:

| Question | What you're looking for |
|---|---|
| Who ranks? | Forums, Quora, Reddit and 2019 blog posts in the top 5 = **weak field**. Wikipedia, a government site, or four well-funded competitors = **skip it** |
| Does the top result actually answer it? | Read it. A page that ranks but dodges the question is the opening |
| Is the intent buying or browsing? | "How much does X cost" is closer to a purchase than "history of X". Both can be worth writing; only one pays this quarter |

If nothing ranks at all, be suspicious rather than delighted — usually it means
nobody searches it.

## 4. Score

Three factors, `0–3` each, summed into `potential` (0–9). Score honestly; the
whole point is that the number lets you throw things away later without
re-litigating them.

**Demand (0–3)** — evidence people ask this
`0` you assumed it · `1` one thread or autocomplete hit · `2` repeated across
sources · `3` repeated, plus high-view video coverage

**Gap (0–3)** — how weak the current answer is
`0` a strong page fully answers it · `1` decent answer, some holes · `2` thin,
outdated or forum-only · `3` genuinely nobody has answered it well

**Proximity (0–3)** — how close the searcher is to being a customer
`0` idle curiosity · `1` researching the problem · `2` comparing solutions ·
`3` ready to buy, blocked on one question

Record all three plus the sum. A `7` made of `3+3+1` and a `7` made of `1+3+3`
are different bets and you'll want to know which you took.

## 5. Kill the weak

The step everyone skips, which is why backlogs rot.

- **`potential < 5` → `status=killed`.** Not "maybe later". Killed, with the
  score still in the row so nobody re-adds it in March
- **Two rows asking the same question → keep the better-phrased one**, kill the
  other. Near-duplicate articles cannibalise each other in search
- **A row whose SERP has changed since it was validated** — a competitor
  published, a big site moved in — gets re-scored or killed on the weekly pass.
  `validated_at` is what tells you it's stale
- **Anything you can't source** → killed. If there's no thread, no autocomplete
  hit, no competitor page, it came from imagination

Killed rows stay in the file. That's the record of what you already decided
against, and it's what stops the backlog from cycling.

**The bar: ≥20 rows at `status=validated` at all times.** Below twenty, the
writing run starts reaching for whatever's left and quality follows the
inventory down. The weekly job's job is to top it back up.

## 6. Multiply the winners

Once an article has real numbers, it stops being a guess and becomes a
template. Two ways to spend that, both of them cheap:

**Ultra-segmentation** — the same question, one narrower audience.
"How to track billable hours" → *for freelance designers*, *for a two-person
agency*, *for someone billing in two currencies*. Works because the generic
version is a compromise; the segmented one names the reader's exact situation
in the title.

**Ultra-localisation** — the same question, one place.
*in the UK*, *in Germany*, *in euros*, *under Making Tax Digital*. Works when
something real actually differs: the tax rule, the currency, the platform
availability, the legal requirement.

Rules that keep this from turning into doorway spam:

- **Only multiply a proven winner.** Multiplying a guess gives you ten guesses
- **One axis at a time.** "For freelance designers in Germany" is a third-order
  page; the traffic isn't there
- **The variant must have a different answer**, not a find-and-replace on the
  original. If the German version says the same thing with a different flag
  emoji, don't publish it — merge it into the original as a section
- **Cap it.** Five to eight variants off one winner, then go find a new winner

Each variant enters the backlog as an ordinary row with `source=variant-of` and
the parent's `run_id`, and gets scored like anything else.

## The output

Everything above ends as rows in `inputs/backlog.csv`:

```csv
title,question,source,source_url,segment,demand,gap,proximity,potential,status,validated_at,parent_run_id,notes
```

| Column | |
|---|---|
| `title` | the working headline — rewritten at draft time, fine |
| `question` | the question **as a human asked it**. This is the durable part |
| `source` | `reddit` · `serp` · `youtube` · `autocomplete` · `competitor` · `variant-of` · `queue` |
| `source_url` | where you saw it. A row you can't trace is a row you can't re-validate |
| `segment` | empty for the generic version; the audience or place for a variant |
| `demand` `gap` `proximity` | 0–3 each, per §4 |
| `potential` | their sum, 0–9 |
| `status` | `candidate` → `validated` → `queued` → `writing` → `published` · or `killed` |
| `validated_at` | ISO date. Older than ~90 days means re-check the SERP |
| `parent_run_id` | for variants, the run that earned the right to spawn them |
| `notes` | the angle. One line: what this piece does that the ranking page doesn't |

Add columns if the workflow needs them — nothing parses this file but you and
the next agent.

## Weekly, in order

1. Re-check `status=validated` rows older than 90 days; re-score or kill
2. Run two or three grid rows you haven't mined yet
3. Score the new candidates, kill everything under 5
4. If any published article has numbers worth multiplying, add its variants
5. Confirm ≥20 validated rows. If not, mine more — don't lower the bar
6. Move the top rows into `inputs/queue/` for the writing runs

Automating this: `engine-loop/references/scheduling.md`. It needs a browser, so
it's an agent job, not a plain cron script.

## Rules

- **Never add a row you can't source.** `source_url` is not optional
- **Never write from a `candidate` row.** Validate it or drop it
- **Never multiply a guess** — variants come from winners only
- **Score before you fall in love with a title.** The order matters: a good
  headline makes a bad subject feel like a good one
- Check `shared/insights.md` and the sibling workflows' `reports/latest.json`
  before mining. An objection that keeps coming back in outreach replies is a
  validated subject that cost you nothing to find
