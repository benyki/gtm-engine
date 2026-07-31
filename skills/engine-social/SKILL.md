---
name: engine-social
description: Writes short-form social posts (LinkedIn, X, Bluesky, and similar text channels) in the user's own voice, learned from their best-performing work, and logs every run (assigning an A/B arm once an experiment is live). LinkedIn and X post from the user's browser; Bluesky posts via its AT Protocol API after approval. Use when the user says "write LinkedIn posts", "draft some tweets", "post to Bluesky", "run the social workflow", "turn this into a post", or asks for short-form written content.
---

# engine-social

Short-form written posts for LinkedIn, X, Bluesky, and other text social
channels. Much shorter feedback loop than `engine-seo` — you learn what works
in weeks rather than months.

**This skill stands alone.** It shares ideas with `engine-seo` and repeats some
of them in its own words, on purpose: the two workflows are validated against
different evidence (a feed versus a search result), they'll drift apart as each
learns, and neither should be able to break the other. Everything this workflow
needs is in *its* `references/`. Don't reach into another skill's folder.

This skill runs any workflow folder of **type `social`**. The default folder
is `social/`; paths below (`inputs/`, `templates/`, `runs/`) are inside that
folder, while brand, accounts and keys are in `shared/`. **Feel free to run
several social workflows** — `social/` and `social-founder-brand/` with
different goals and metrics are two independent folders — scaffold with
`--merge --workflow social-founder-brand:social`, or copy one and empty its
`runs/` and `reports/` (history belongs to the original). Channels stay platform-named (`linkedin`, `x`,
`bluesky`, …).

**How (not just what):**

| Step | Reference |
|---|---|
| Find and validate subjects | `references/subject-finding.md` |
| Platforms / threads in the browser | `references/browser-research.md` |
| Cut AI slop / keep voice | `references/anti-slop-writing.md` |
| Write a thread + post on X / LinkedIn (browser) | `references/threads-and-x.md` |
| Post on Bluesky (API) | `references/bluesky-post.md` |

## Before the first run

Pick **one** platform to start. LinkedIn, X and Bluesky reward different things, and splitting attention early means learning neither. `shared/channels.json` holds the accounts.

If you run more than one, keep the accounting per channel: log each run with the channel it actually shipped to, and give each its own `primary_metric` / `metric_delay_hours` in `shared/channels.json` where they differ.

Whether one experiment can span both platforms depends on the metric, not the platform count. Platform-native numbers (impressions, likes) are different currencies at different scales — an arm mean pooled across them mostly measures where you posted, so scope those experiments per channel (`"channel"` on the experiment, `--channel` on `assign_arm.py`). A metric you measure at your own end in one currency — clicks, signups, replies — compares fine across platforms, and pooling it into one experiment reaches a verdict faster.

## Where posts come from

`references/subject-finding.md` is this workflow's own method — where subjects
come from, how to validate a claim *on the platform* rather than against search
volume, the 0–9 score, the kill step. Its output is this workflow's
`inputs/backlog.csv`, and **the bar is ≥20 rows at `status=validated`**. Short-form
burns subjects fast — a batch is five to seven posts — so a thin backlog shows
up as generic content within two weeks.

In order of what actually works:

1. **What they did this week** — a shipped feature, a support conversation, a decision and why, a number they can share. Nobody else has this, and it's why the founder account beats the brand account. The day-one default
2. **The queue** — `inputs/queue/`, written by `engine-loop` from what performed. Start here when it's not empty
3. **Their own published work** — one article is three or four posts: the counterintuitive claim, the example, the number, the objection it answers
4. **Questions the audience actually asks** — replies, support threads, sales objections, Reddit. Read for phrasing and friction, not for search volume

`shared/insights.md` sits across all of it — read it before picking, and add to
it when a verdict here teaches something bigger than this workflow. Reading a
sibling workflow's `reports/latest.json` is worth doing; reaching into another
skill's `references/` is not.

`shared/insights.md` sits across all of it — read it before picking, add to it
when a verdict here teaches something bigger than this workflow.

## The run

### 1. Read their voice first

`inputs/best/` — their top-performing posts. Read them before writing anything, every single time. Voice is copied from examples, never from a description of a voice. If `inputs/best/` is empty, say so and ask for five links; the output will be generic otherwise and no amount of prompting fixes it.

### 2. Get the arm

```bash
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --workflow social
```

Good variables here: how the post opens, whether it tells a story or states a claim, one-liner versus paragraphs, ends on a question versus ends flat. If it returns `write_template`, write that template from the hypothesis and use it.

**On a fresh workflow this returns `use_template` and that's correct** — the
starter experiments ship paused on purpose. Ship one format until the user is
happy with the format, then start testing. `engine-loop/references/ab-testing.md`
→ R0 has the three conditions for flipping an experiment live.

### 3. Draft a batch, not one

Five to seven posts. Short-form is cheap to write and expensive to judge in isolation — a batch lets the user see the pattern and reject a direction rather than a sentence.

- The first line decides everything. It's the only part most people read
- One idea per post
- No engagement bait, no "agree?", no fake vulnerability, no thread of platitudes
- Formatting matches what's in `inputs/best/` — if they don't use line breaks between every sentence, don't start

Before showing the batch, run `references/anti-slop-writing.md` over it (edit or detect).

### 4. Log each one

Use the arm and template `assign_arm.py` returned — for example, when it picks the question opener:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --workflow social --channel linkedin \
  --experiment exp-003 --arm question --template post-question.txt
```

One run per post. That's what makes the arm comparison work.

### 5. Publish

**LinkedIn and X** — logged-in browser. Hand them the draft, or drive the UI per
`references/threads-and-x.md` (X checklist; LinkedIn same contract). Threads are
staged in full and published together, so that file is also where the thread
gets written — a thread is not a long post cut into pieces. Then:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish --run <run_id> --url https://...
```

**Bluesky** — AT Protocol API after explicit per-post approval —
`references/bluesky-post.md`. Schedulers (Upload Post / Buffer) are a video
concern; see `engine-video/references/posting-options.md` if you later want them
for text too.

The URL is needed to read the numbers back later.

## Bluesky (summary)

Open API, sanctioned posting — **approval boundary unchanged.** App password only;
details and minimal `AtpAgent` example in `references/bluesky-post.md`. Prefer
`benyki/skills/bluesky-post-manage` when installed.

Format: **300 graphemes** max, ≤4 images with alt text, facets via
`RichText.detectFacets()`. Log with `--channel bluesky`; metrics `--source api`.

## Getting the numbers back

On LinkedIn and X, impressions and engagement live behind the user's own login, so the browser is the normal route (Bluesky's numbers come back through its API — see above):

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py metric --run <run_id> --value 3400 --source browser
```

**Wait at least 72 hours before recording** — for these channels the default window is the right one. LinkedIn and X keep distributing for days. A number read earlier tells you what time you posted, not whether the post was good — and once it's in `index.csv` it's in every verdict from then on. If `due_metrics.py` says it's too early, leave the cell empty and pick it up on the next run.

## Rules

- **Never publish without the user's yes.** On LinkedIn and X, drafts go to the user to post; on Bluesky the agent may post via the API — after an explicit approval per post, not instead of one
- **Never claim something the user hasn't done.** Invented anecdotes are the fastest way to burn a personal brand, and they're unrecoverable once someone notices
- **Never copy a competitor's post.** Take the structure if it works, never the words
- One platform until the loop says something useful about it

## Make it run without you

Short-form dies from irregularity faster than from bad posts — a burst then
three quiet weeks teaches the loop nothing and the algorithm less. Once the
voice is right, schedule the drafting:

| Label | When | What |
|---|---|---|
| `engine-metrics-social` | daily | read each published post's numbers off the platform in the browser and record them. Daily because the 72h window clears on a rolling basis — a weekly-only job always reads a few late |
| `engine-social-weekly` | weekly | draft the batch from `inputs/queue/`, run the anti-slop pass, leave them for review |

**It drafts; it never posts.** LinkedIn and X drafts go to the user, and Bluesky
publishes only after per-post approval — the scheduler doesn't relax that
boundary. Catalogue: [`docs/scheduling.md`](../../docs/scheduling.md); how to
create one: `engine-loop/references/scheduling.md`.

## Going further

Optional installs from `benyki/skills` — see `docs/additional-skills.md`:

Threads and X posting are covered in `references/threads-and-x.md` — enough to
write and ship one without installing anything. Install these when you want more:

| Skill | What it adds beyond the reference |
|---|---|
| `x-browser-post` | the frozen element map with fallback queries, the clipboard image script, the staged-thread loop as pseudocode, and a quirks file |
| `bluesky-post-manage` | Bluesky chains, images, multi-account, delete |
| `phraser-thread-generate` + `phraser-thread-backstory` | a worked **write-then-post** pipeline: research the material, write it as hook plus beats, keep a backlog, post the chain, mark it done. Project-specific as shipped — take the shape, swap the backlog path and brand |

When a verdict here teaches you something bigger than this workflow — a hook
style, an audience truth — add one line to `shared/insights.md`; a reusable
asset (winning image, proof point) goes to `shared/assets/`. Siblings learn
from it on their next pass.
