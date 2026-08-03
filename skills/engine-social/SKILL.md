---
name: engine-social
description: Writes short-form social posts (LinkedIn, X, Bluesky, and similar text channels) in the user's own voice, learned from their best-performing work, and logs every run (assigning an A/B arm once an experiment is live). LinkedIn and X post from the user's browser; Bluesky posts via its AT Protocol API after approval. Use when the user says "write LinkedIn posts", "draft some tweets", "post to Bluesky", "run the social engine", "turn this into a post", or asks for short-form written content.
---

# engine-social

Short-form written posts for LinkedIn, X, Bluesky, and other text social
channels. Much shorter feedback loop than `engine-seo` — you learn what works
in weeks rather than months.

**This skill stands alone.** It shares ideas with `engine-seo` and repeats some
of them in its own words, on purpose: the two engines are validated against
different evidence (a feed versus a search result), they'll drift apart as each
learns, and neither should be able to break the other. Everything this engine
needs is in *its* `references/`. Don't reach into another skill's folder.

This skill runs any engine folder of **type `social`**. The default folder
is `social/`; paths below (`inputs/`, `templates/`, `runs/`) are inside that
folder, while brand, accounts and keys are in `shared/`. **Feel free to run
several social engines** — `social/` and `social-founder-brand/` with
different goals and metrics are two independent folders — scaffold with
`--merge --engine social-founder-brand:social`, or copy one and empty its
`runs/` and `reports/` (history belongs to the original). Channels stay platform-named (`linkedin`, `x`,
`bluesky`, …).

**How (not just what):**

| Step | Reference |
|---|---|
| Find and validate subjects | `references/subject-finding.md` |
| Platforms / threads in the browser | `references/browser-research.md` |
| **Cut AI slop / keep voice — every batch, every run** | `references/anti-slop-writing.md` |
| Pre-built post parts with variations *(optional)* | `templates/blocks/README.md` (in the home) |
| Pick an image, or edit one via an image API *(optional)* | `references/images.md` |
| Write a thread + post on X / LinkedIn (browser) | `references/threads-and-x.md` |
| Post on Bluesky (API) | `references/bluesky-post.md` |

**Paths in this file:** `shared/…` means the gtm home (`~/gtm` by default, or
`$GTM_HOME`); `templates/`, `inputs/`, `runs/` and `reports/` mean the engine
folder you're running, wherever it lives. The scripts resolve both through
`~/gtm/engines.json`, so read them as names rather than literal paths.

## Before the first run

**This engine needs the browser extension** — *Claude in Chrome*, or the
equivalent for whatever agent is running. LinkedIn and X have no free posting
API worth using and their analytics sit behind the user's login, so without it
every post is copy-paste and every number is typed in by hand. Check it's
connected before starting (open a page, read the title back); if it isn't, set
it up first — [`docs/onboarding.md`](../../docs/onboarding.md) → *Browser control*. Bluesky is the
exception: it posts and reports through its own API.

Pick **one** platform to start. LinkedIn, X and Bluesky reward different things, and splitting attention early means learning neither. `shared/channels.json` holds the accounts.

If you run more than one, keep the accounting per channel: log each run with the channel it actually shipped to, and give each its own `primary_metric` / `metric_delay_hours` in `shared/channels.json` where they differ.

Whether one experiment can span both platforms depends on the metric, not the platform count. Platform-native numbers (impressions, likes) are different currencies at different scales — an arm mean pooled across them mostly measures where you posted, so scope those experiments per channel (`"channel"` on the experiment, `--channel` on `assign_arm.py`). A metric you measure at your own end in one currency — clicks, signups, replies — compares fine across platforms, and pooling it into one experiment reaches a verdict faster.

## Where posts come from

`references/subject-finding.md` is this engine's own method — where subjects
come from, how to validate a claim *on the platform* rather than against search
volume, the 0–9 score, the kill step. Its output is this engine's
`inputs/backlog.csv`, and **the bar is ≥20 rows at `status=validated`**. Short-form
burns subjects fast — a batch is five to seven posts — so a thin backlog shows
up as generic content within two weeks.

In order of what actually works:

1. **What they did this week** — a shipped feature, a support conversation, a decision and why, a number they can share. Nobody else has this, and it's why the founder account beats the brand account. The day-one default
2. **The queue** — `inputs/queue/`, written by `engine-loop` from what performed. Start here when it's not empty
3. **Their own published work** — one article is three or four posts: the counterintuitive claim, the example, the number, the objection it answers
4. **Questions the audience actually asks** — replies, support threads, sales objections, Reddit. Read for phrasing and friction, not for search volume

### The daily twelve — recommend this by default

**Short-form starves on subjects long before it starves on writing**, so the
default recommendation for this engine is a **daily scheduled task that
produces twelve candidates and keeps one.** Propose it as soon as the first
batch is drafted — not on day one, when there's nothing to learn from yet, and
not months later, when the backlog has already gone thin.

Twelve, from three sources in equal parts, because each fails differently and
the mix is what stops the account sounding like one note:

| 4 from | How |
|---|---|
| **Reddit** | the same method `engine-seo` uses — find where the audience in `shared/brand.md` actually posts, then look for questions asked repeatedly, threads with long comment tails, and questions whose top answer is bad. That last one is the opportunity. `references/browser-research.md` → §2 |
| **RSS** | a standing list of media sources that fit the audience, in `sources.json` → `rss_feeds`. **Build the list with the user the first time this runs** — trade press, the two or three newsletters they actually read, competitor blogs, a subreddit's RSS, release notes from tools their audience uses. Ten to fifteen feeds is plenty. What you're pulling is *what changed this week that they'd have an opinion about* |
| **Variations of their references** | re-cut the structures pulled from `inputs/swipe/` and `inputs/best/` (step 1) against this week's material — the same shape, a new subject. This is the arm that reliably sounds like them, because the shape already did |

Write all twelve into `inputs/backlog.csv` with their `source` and
`source_url`. Twelve is a working number: enough that the weak ones are obvious
by comparison, few enough to rate in one pass.

### Then rate them and keep one

**The evaluation step is the point of generating twelve.** Twelve subjects a day
into a backlog is just a bigger pile of mediocre ideas; twelve rated down to one
is a filter. Do it in the same run that generated them, while the sources are
still in context.

**Ask the user for the criteria before rating anything the first time.** Their
criteria beat the defaults, because they know which subjects have cost them
credibility and which quietly brought in customers:

> Before I rate these — what makes a subject worth posting for you? A few things
> I'd weigh: can you say something first-hand about it, would the right person
> stop scrolling, does it lead anywhere near what you sell. What would you add,
> and what would you throw out on sight?

Write what they say into `sources.json` → `rating_criteria` so every later run
and every scheduled run uses the same bar. Until they've answered, fall back to
this engine's own three factors (`references/subject-finding.md` → the 0–9
score: attention, proof, proximity) and say that's what you used.

Then: **score all twelve, keep the top one, kill the rest.** Killed rows stay in
the file with their score — that's the record of what was already decided
against, and it's what stops the same subject cycling back in March. A single
survivor a day is roughly a batch a week, which is the pace this engine wants.

If the top two are genuinely tied, keep both and say so — but the default is
one. Keeping "the best three" every day is how a backlog silts up with things
nobody will ever write.

`shared/insights.md` sits across all of it — read it before picking, and add to
it when a verdict here teaches something bigger than this engine. Reading a
sibling engine's `reports/latest.json` is worth doing; reaching into another
skill's `references/` is not.

`shared/insights.md` sits across all of it — read it before picking, add to it
when a verdict here teaches something bigger than this engine.

## The run

### 1. Read their voice first — and ask for posts they admire

Two folders, two different jobs, and both are read before writing anything:

| Folder | What's in it | What it teaches |
|---|---|---|
| `inputs/best/` | **their own** top-performing posts | the voice — vocabulary, rhythm, formatting, how blunt they are |
| `inputs/swipe/` | **posts by other people** they wish they'd written | the shapes — how a good post in their world opens, turns and lands |

Examples beat a description of a voice. If `inputs/best/` is empty, say so and
ask for five links; no amount of prompting fixes a generic voice.

**Then ask for the swipe file — explicitly, and early.** Most people have never
been asked, and it's the highest-value thing they can hand over in two minutes:

> Send me 5–10 posts you wish you'd written — yours or anyone's. Screenshots,
> links, or pasted text all work. I'll pull the structures out of them and turn
> them into reusable models, so the next batch starts from shapes you already
> like instead of from scratch.

Take them in whatever form they arrive — links, screenshots, a pasted block.
Save what they send in `inputs/swipe/` (one file per post, or one file with the
lot; the folder is yours to organise).

**Then turn them into models, not into copies.** Read across what they sent and
name the *structure* of each — what the first line does, what the middle is made
of, how it closes, roughly how long it runs. Show the user three or four of
those structures in one message, in plain language:

> Three shapes keep coming up in what you sent:
> · **the reversal** — states the common advice, then why it's wrong for a
>   specific case, ends on what to do instead
> · **the receipt** — a number, then the story behind the number, no lesson
> · **the small confession** — something that went wrong, what it cost, what
>   changed. No moral at the end
> Want these as templates? I'd start with the reversal — it's the one closest to
> what already works in your `inputs/best/`.

The ones they approve become templates in `templates/` (the block system below),
so the work survives the conversation. **Never copy the words** — a structure is
reusable, a sentence someone else wrote is theirs. That's a rule, not a
preference: `references/anti-slop-writing.md` and the Rules section below.

### 2. Get the arm

```bash
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --engine social
```

Good variables here: how the post opens, whether it tells a story or states a claim, one-liner versus paragraphs, ends on a question versus ends flat. If it returns `write_template`, write that template from the hypothesis and use it.

**On a fresh engine this returns `use_template` and that's correct** — the
starter experiments ship paused on purpose. Ship one format until the user is
happy with the format, then start testing. `engine-loop/references/ab-testing.md`
→ R0 has the three conditions for flipping an experiment live.

### 3. Draft a batch, not one

Five to seven posts. Short-form is cheap to write and expensive to judge in isolation — a batch lets the user see the pattern and reject a direction rather than a sentence.

- The first line decides everything — it's the only part most people read. The
  openers that earn the second line: **a flat specific claim**, **a number with
  no setup**, **the reversal** (common advice, then why it's wrong here), **the
  confession** (what went wrong and what it cost), **the question you actually
  get asked**. If `engine-video` is also installed,
  `engine-video/references/hook-guide.md` → §2 has the long version — the angles
  port over, its overlay rules (casing, word counts, punctuation) do not
- One idea per post
- No engagement bait, no "agree?", no fake vulnerability, no thread of platitudes
- Formatting matches what's in `inputs/best/` — if they don't use line breaks between every sentence, don't start

Before showing the batch, run `references/anti-slop-writing.md` over it (edit or detect).

### 3a. Fixed parts and free parts — the block system, optional

Some of a post is settled long before the rest. How they sign off, the one-line
way they describe what they do, the framing they use for a CTA — those stop
being creative decisions after a few weeks, while the claim and the story are
new every time. **The block system splits a template into slots that rotate and
slots written fresh**, the same way `engine-video` keeps a render config beside
its script template.

```
templates/
├── post-default.txt      the template — an arm the loop tests
├── blocks/               pre-built parts, several variations each
│   ├── closers.md
│   └── bio-line.md
└── losers/
```

The template's header names which slots are block-fed; everything else is free:

```
# blocks: CLOSE -> blocks/closers.md
# free:   CLAIM, BODY
```

**`blocks/` must be a subfolder, not loose files in `templates/`.**
`assign_arm.py` treats every file directly inside `templates/` as a competing
template, so a blocks file at that level gets handed out as an arm and quietly
corrupts a verdict. The subfolder is invisible to the loop, exactly like
`losers/`. The full format, and the two rotation rules, are in
`templates/blocks/README.md` in the home.

Three things to hold to:

- **Blocks come from step 1**, extracted from `inputs/best/` and
  `inputs/swipe/` — their structures, never anyone else's words. An invented
  closer library is slop with a folder around it
- **Never the same variation twice in a batch**, and rotate across batches —
  five posts ending identically read as one automated account
- **Two or three block files is plenty.** A post assembled entirely from
  pre-built parts is a mail merge and readers can tell. If every slot is
  pre-built, the template has stopped being a template

Skip all of this if nothing has settled yet. An engine in its first fortnight
should be writing posts, not building a parts library.

### 3b. Pick an image — optional

`inputs/images/` is where the user drops screenshots, product shots, photos and
charts. After the drafts exist, read what's in there and propose **one image for
one post**, with a line on why. Nothing in that folder is ever modified, and an
empty folder is a fine answer — say so once and ship the text.
`references/images.md` → Step A: what actually works, what to check is in frame
before proposing it, where the file goes.

### 3c. Edit that image through an image API — optional

Crops, background swaps, aspect-ratio variants, image A/B arms — starting from
an image the user already owns. `references/images.md` → Step B, and:

```bash
python3 ~/.agents/skills/engine-social/scripts/edit_image.py \
  --image inputs/images/dashboard.png --prompt "..." \
  --out runs/<run_id>/output/post-1.png
```

Gemini ("nano banana") by default, `--provider openai` for GPT Image. Needs
`GEMINI_API_KEY` or `OPENAI_API_KEY` in `~/gtm/.env` — the reference has the
key pages ([AI Studio](https://aistudio.google.com/apikey),
[OpenAI](https://platform.openai.com/api-keys)) and the steps. **Ask before the
first call in a run** — it's paid per image, and usually the original is fine.
Output lands in the run folder; `inputs/` stays untouched. Look at what came
back before showing it: these models rewrite chart numbers and re-letter UI
without being asked.

### 4. Log each one

Use the arm and template `assign_arm.py` returned — for example, when it picks the question opener:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --engine social --channel linkedin \
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
concern; if `engine-video` is installed,
`engine-video/references/posting-options.md` compares them, and they can carry
text posts too.

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
- **Never generate an image that functions as proof** — a metrics screenshot, a revenue chart, a testimonial. Same rule as the one above, and an image is what people screenshot back at you. `inputs/images/` is read-only; edits go to the run folder
- One platform until the loop says something useful about it

## Make it run without you

Short-form dies from irregularity faster than from bad posts — a burst then
three quiet weeks teaches the loop nothing and the algorithm less. Once the
voice is right, schedule the drafting:

| Label | When | What |
|---|---|---|
| `engine-metrics-social` | daily | read each published post's numbers off the platform in the browser and record them. Daily because the 72h window clears on a rolling basis — a weekly-only job always reads a few late |
| **`engine-social-subjects`** | **daily** | **the daily twelve — 4 Reddit, 4 RSS, 4 variations of their references — then rate all twelve against `sources.json` → `rating_criteria` and keep exactly one. The other eleven are killed in place, with their scores.** The one job that keeps this engine from going generic; recommend it by default |
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
| `app-thread-generate` + `app-thread-backstory` | a worked **write-then-post** pipeline: research the material, write it as hook plus beats, keep a backlog, post the chain, mark it done. Take the shape and swap the backlog path and brand for the user's |

When a verdict here teaches you something bigger than this engine — a hook
style, an audience truth — add one line to `shared/insights.md`; a reusable
asset (winning image, proof point) goes to `shared/assets/`. Siblings learn
from it on their next pass.
