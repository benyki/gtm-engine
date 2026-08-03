---
name: engine-seo
description: Writes search-led articles and landing pages by mining the questions real people ask (Reddit by default, competitor pages when supplied), drafting in the user's voice, and logging the run. Generates locally — publishing stays manual. Use when the user says "write an article", "run the SEO engine", "what should I write about", "make a landing page", or asks for written content.
---

# engine-seo

Finds a question people actually asked, answers it better than what currently ranks, and writes the piece in the user's voice.

This skill runs any engine folder of **type `seo`**. The default folder is
`seo/`; paths below (`sources.json`, `inputs/`, `templates/`, `runs/`, `site/`)
are inside that folder, while brand, accounts and keys live in `shared/`.
**Two seo engines are fine** — e.g. `seo/` for the product blog and
`seo-docs/` for a docs/comparison site, each with its own sources, site and
metric — scaffold with `--merge --engine seo-docs:seo`, or copy a folder
and empty its `runs/` and `reports/` (history belongs to the original).

Output is markdown, generated locally. Where it goes depends on whether they already have a site — see **Publishing** below. Either way nothing goes live without them saying so.

**How (not just what):**

| Step | Reference |
|---|---|
| Reddit / SERPs in the browser | `references/browser-research.md` |
| Find and validate subjects | `references/subject-finding.md` |
| **Cut AI slop / keep voice — every draft, every run** | `references/anti-slop-writing.md` |
| Publishing: the gate, metadata, deploy | `references/publishing-site.md` |
| After publish (Clarity → rewrites) | `references/clarity-rewrite.md` |
| Static site / CMS tradeoffs | `references/advanced.md` |

## Where topics come from

Read this engine's `sources.json`. The default is Reddit, and it needs no account.

Topics don't get found one at a time at the start of a writing run — that's how
you end up writing whatever you thought of that morning.
`references/subject-finding.md` is the weekly pass that mines the query grid,
validates against live SERPs, scores each candidate and kills the weak ones.
Its output is `inputs/backlog.csv`, and **the bar is ≥20 rows at
`status=validated` at all times**. Below that, top it up before writing
anything — the sources below are the raw material it draws on.

**Reddit (default).** Find the subreddits where the audience in `shared/brand.md` actually posts, then look for questions asked repeatedly, questions with long comment threads, and questions where the top answer is bad. That last one is the opportunity — a real question with no good answer is the whole game. How to read threads without an API: `references/browser-research.md`.

**Competitor URLs.** If they're listed in `sources.json`, read them and find what they left out, what they got wrong, and what's aged badly. Beat the page that exists; don't write a worse copy of it.

**Ahrefs / Semrush.** Use them if they already pay. The free path is enough to start.

No API for something? Read it in the browser. That's the normal path here, not a workaround.

## The run

### 1. Pick the question

**Take the top rows of `inputs/backlog.csv`** — `status=validated`, highest
`potential` first — and show the user a shortlist of three with the score
breakdown and the angle from `notes`. They choose; you set that row to
`status=writing`.

One question, phrased the way a human would ask it. The queue in
`inputs/queue/` may already have one waiting from the loop — that counts as a
backlog row too, and belongs in the file.

If the backlog is empty or under twenty validated rows, stop and run
`references/subject-finding.md` first. Writing from a thin backlog is how a
engine starts producing articles nobody searched for.

### 2. Get the arm

```bash
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --engine seo
```

For articles the variants are usually structural — how it opens, whether it leads with the answer or the context, how long it runs. If it returns `write_template`, write that template from the hypothesis and use it.

**On a fresh engine this returns `use_template` and that's correct** — the
starter experiments ship paused on purpose. Ship one article until the user is
happy with the format, then start testing. `engine-loop/references/ab-testing.md`
→ R0 has the three conditions for flipping an experiment live.

### 3. Outline, then check

Show the outline before writing the draft. It costs a minute and saves an hour, and it's the last cheap moment to catch a wrong angle.

### 4. Write

Voice comes from `inputs/best/` — their own best-performing pieces — not from adjectives in a brief. Read those first, every time.

- Answer the question in the first hundred words. Nobody scrolls for it
- Specifics over hedging. Real numbers, real examples, real product names
- No throat-clearing intros, no "in today's fast-paced world", no summary of what the article will cover
- Length is whatever the question needs
- Respect the banned words and claims in `shared/brand.md`

### 4b. Cut the slop — every draft, before the user reads it

**`references/anti-slop-writing.md`, over every article, every run.** Not a
polish step to do if there's time: a long piece is where slop hides best, and
the user reading it is the wrong place to find it. Run it in **edit** mode by
default (minimum changes, return the draft); **detect** mode when the user wants
to see the patterns named rather than fixed.

The test that matters most in long-form: **if a paragraph could appear on a
competitor's blog after swapping the product name, rewrite it from
`inputs/best/` or cut it.** Voice survives the pass — vocabulary, bluntness,
digressions and edge come from `inputs/best/`, and sanding those off is the
failure mode, not the goal.

If `benyki/skills/no-ai-slop-writting` is installed, use it instead — same pass,
full pattern list and an eval set. The reference has the one-line install.

### 5. Log it

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --engine seo --channel blog \
  --experiment exp-002 --arm default --template article-default.md
```

Write the draft to `runs/<run_id>/output/`.

## Publishing

Two routes. Ask which one applies before the first run — it changes where the markdown ends up.

### They already have a site

Generate locally, they paste it into their CMS. Don't try to automate WordPress, Webflow or Ghost — every setup is different and it's a bad problem to solve on day one.

### They don't have a site, or want to start fresh

Then building one is part of this engine, because thirty good articles in a folder are worth nothing.

The **contract** is: content stays in plain markdown files an agent can read and fix, publishing is a git push, and each page carries its `run_id` back to the spine. Any stack that satisfies it works — if they already have a Next.js site or a company-standard host, publish into that rather than building a parallel one. The **default**, when starting from nothing, is Astro + local markdown, deployed to Cloudflare Pages or Railway (both free at this size, both deploy on git push).

Scaffold it into this engine's own `site/` folder — self-contained like
everything else here. Then `references/publishing-site.md` has the whole build:
the **approved-folder gate** (the agent writes to `runs/<run_id>/output/`, a
human copies into the built folder — that copy *is* the approval), the
frontmatter contract and collection schema, the six metadata pieces (title +
description, canonical, OG/Twitter, JSON-LD, sitemap, RSS), and the curl checks
that prove they're live rather than merely configured.

Keeping the content as markdown files is deliberate: when something breaks, an agent opens the file and fixes it. That stops being true once the content lives in a database — see `references/advanced.md`, which covers when that trade is worth making.

### Either way

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish --run <run_id> --url https://...
```

The URL matters — `engine-loop` needs it to fetch Search Console numbers later.

One timing note: search is slow. The 72-hour default window in `due_metrics.py` is a social-media number; Search Console data on a new article takes weeks to mean anything. Set `metric_delay_hours` on the blog channel in `shared/channels.json` (336 = two weeks is a sane floor) so the loop doesn't ask for numbers that don't exist yet.

### After it has traffic

If Clarity is set up, turn behavior into the next rewrite with
`references/clarity-rewrite.md` — don’t guess from vanity metrics alone.

## Rules

- **Never publish without a yes.** Deploying is a git push, which is easy to do by accident and hard to undo from someone's index. The agent never writes into the built folder — `references/publishing-site.md`
- **Never invent a statistic, study or quote.** If a claim needs a source, find one or cut the claim. A fabricated number in a published article is the kind of mistake that outlives the article
- **Articles are worth tracing to a real question**: a backlog row with a `source_url`, a real thread, a real SERP, a real competitor gap. Flag the ones that aren't
- **Variants pay off best on articles that already earned numbers** — `references/subject-finding.md`
- Don't write ten pieces in a batch. One good piece, published, measured, beats ten in a folder
- An objection or question that keeps appearing in other engines' replies is your next article — check `shared/insights.md` and the siblings' `reports/latest.json` when picking topics, and add a line back when an article's numbers teach something general

## Make it run without you

Subject finding, backlog upkeep and publishing are the three steps people stop
doing by hand, and a backlog nobody tops up is an empty queue in a month. Once
this engine is producing articles the user is happy with, put them on a
schedule:

| Label | When | What |
|---|---|---|
| `engine-metrics-seo` | **weekly or fortnightly** | record what published articles earned. Search Console needs weeks to mean anything, so a daily job here finds nothing 27 days a month — this is the one engine whose metric job is *not* daily |
| `engine-seo-subjects` | weekly | mine communities for real questions → `inputs/queue/` |
| `engine-seo-backlog` | weekly | keep ≥20 validated titles, re-validate, drop what died |
| `engine-seo-publish` | weekly | push what's in the **approved** folder and trigger the rebuild |

The publish job never publishes something the user hasn't moved into the
approved folder themselves. Catalogue and rules:
[`docs/scheduling.md`](../../docs/scheduling.md); how to create one:
`engine-loop/references/scheduling.md`.

## Going further

- `references/advanced.md` — site that generates from `runs/`
- Optional: `benyki/skills/clarity-api-seo`, `benyki/skills/agent-browser` —
  `docs/additional-skills.md`
