# Goals — what has to exist by the end of the day

Not a plan, and not a list of intentions. A list of **achievements**: specific,
factual things that exist on your machine and run without you when you close the
laptop. Every line is checkable — a file that opens, a scheduler that fires, a
run row with a number in it.

Do the sections for the workflows you're actually setting up. Skip the rest —
an empty workflow folder is clutter, not an obligation.

## How to read the brackets

Each line ends with what you have to create for it:

| Tag | Meaning |
|---|---|
| `[daily scheduler <id> to create]` | a scheduled task that fires every day |
| `[weekly scheduler <id> to create]` | same, weekly |
| `[file <path> to create]` | a config / input / db file at that exact path |
| `[folder <path> to create]` | a directory with real content in it, not a `.gitkeep` |
| `[skill <name> to install]` | already exists — download it from `benyki/skills` |
| `[skill <name> to create]` | does not exist yet — write it |
| `[check]` | nothing to create; verify the statement is true |

- Paths are relative to your workspace (`<your-project>/workflows/`).
- Schedulers are **your agent's own scheduled tasks** — ask it to create one by
  name and it does. Catalogue: [`scheduling.md`](scheduling.md); mechanics and
  the OS-level fallback:
  [`skills/engine-loop/references/scheduling.md`](../skills/engine-loop/references/scheduling.md).
- Installing a skill: [`additional-skills.md`](additional-skills.md).

---

## 0. Baseline — true before anything else counts

- [ ] Workspace scaffolded: one folder per workflow you'll run, plus `shared/` [check: `doctor.py` is green]
- [ ] Brand filled in for real — audience type (B2B/B2C), named ICP, promise, tone, banned claims [file `shared/brand.md` to create]
- [ ] Every channel you ship to today is `enabled: true` with its handle and `metric_delay_hours` [file `shared/channels.json` to create]
- [ ] Keys pasted in by you, for the workflows below only [file `shared/.env` to create]
- [ ] Each workflow has a one-sentence `goal` and a real `primary_metric` (not "engagement") [file `<workflow>/workflow.json` to create]
- [ ] Cross-workflow learnings file exists, even empty [file `shared/insights.md` to create]

---

## 1. Viral app video workflow — `video-app/`

Short, hook-led clips of the product. Volume format: the hook is the variable,
everything else is production.

- [ ] Workflow folder exists, `type: video`, metric `watch_through_rate` [file `video-app/workflow.json` to create]
- [ ] ≥5 hook clips, each ≤5s, 9:16, each with its source and rights noted — own footage, generated, or downloaded; the options are in `engine-video/references/clip-sourcing.md` [folder `shared/assets/hooks-5s/` to create] [skill `yt-dlp` to install]
- [ ] ≥10 screen recordings of the app, 9:16, trimmed, named by what they show [folder `shared/assets/screen-recordings/` to create]
- [ ] Hook library: ≥30 text hooks that work for this product, event- and bump-style hooks removed [file `video-app/inputs/hooks.md` to create]
- [ ] Text overlay style locked once — font, size, weight, position, outline — and the `fontselect` probe run so libass isn't silently substituting [file `video-app/templates/floating-text-app.json` to create] [folder `shared/assets/fonts/` to create] [skill `ffmpeg-text-overlay` to install]
- [ ] Format doc: what this video is, every input a config must supply (hook, footage 1, footage 2, music), the exact shape of each, and the duration of each slot [file `video-app/inputs/format.md` to create]
- [ ] 10 configs queued for the next 10 videos, each naming its hook, footage and per-scene durations [folder `video-app/inputs/queue/` to create — 10 files]
- [ ] No two configs share **both** the same inputs and the same scene durations — same inputs with different durations is fine, and so is the reverse [check: `combo_check.py check` passes on all 10]
- [ ] Every rendered video keeps its config, so the next check still means something [file `video-app/runs/<run_id>/inputs.json` per video]
- [ ] A re-shipped winner changes ≥75% of its frames, so TikTok's duplicate detection doesn't collapse it [skill `video-duplicate-transformer` to install]
- [ ] One video rendered, logged, published, URL recorded [check: a row in `video-app/runs/index.csv` with a `url`]
- [ ] **One** hook template you'd ship unedited — not two. The A/B stays paused until the format is settled [file `video-app/experiments.json` to create — leave `status: paused`]
- [ ] Weekly job that reads the numbers and rewrites `hooks.md` from what earned watch-through [weekly scheduler `engine-video-app-hooks` to create]

---

## 2. Informative video workflow — `video-info/`

Same machinery, different job: turn text you didn't write into a watchable
explainer.

- [ ] Workflow folder exists, `type: video`, its own goal and metric [file `video-info/workflow.json` to create]
- [ ] A named text source — your own blog, an RSS feed, a subreddit, Wikipedia, industry news [file `video-info/sources.json` to create]
- [ ] If the source is fetched rather than picked: a job that pulls new items daily [daily scheduler `engine-video-info-source` to create]
- [ ] ≥2 real text items on disk, ready to build from [folder `video-info/inputs/source-texts/` to create]
- [ ] A template the agent chose — scenes, text hierarchy, which words get highlighted — decided from the two worked examples and the two texts, not from taste [file `video-info/templates/<name>.json` to create] [skill `phraser-remotion-learn-words` to install] [skill `neura-video-study` to install]
- [ ] Footage source set — Pexels by default — and a keyword fetch that actually returned clips [check: `PEXELS_API_KEY` set, files in `shared/assets/pexels/`] [skill `pexel-video-downloader` to install]
- [ ] An assembler that renders template + config → `final.mp4` [file `video-info/scripts/assemble.mjs` to create]
- [ ] ≥2 iterations done, with the template file **and** the assembler updated together each time [check]
- [ ] One template, iterated until the user likes it. The second variation is next month's job, not today's [file `video-info/experiments.json` to create — leave `status: paused`]
- [ ] One video rendered, logged, published, URL recorded [check]

---

## 3. SEO — `seo/`

- [ ] Workflow folder, goal, metric (clicks from Search Console) [file `seo/workflow.json` to create]
- [ ] Weekly job that finds the Reddit posts your audience actually engages with [weekly scheduler `engine-seo-subjects` to create]
- [ ] The question-mining query grid written down — `how <product type>`, `why <product type>`, `where <product type>`, … — and where each gets validated (Google, YouTube, Reddit) [file `seo/inputs/query-patterns.md` to create]
- [ ] Ahrefs / Semrush wired only if already paid for; otherwise the free path is the path [file `seo/sources.json` to create]
- [ ] A subject-quality rule written down: ultra-localisation and ultra-segmentation of what already performs [file `seo/inputs/subject-rules.md` to create]
- [ ] ≥20 validated titles in the backlog, each with its source, a potential score, and the low-potential ones already removed [file `seo/inputs/backlog.csv` to create]
- [ ] Weekly job that keeps the backlog at ≥20, re-validates what's in it, and drops what died [weekly scheduler `engine-seo-backlog` to create]
- [ ] ≥3 markdown articles you like, in the workflow, as the voice reference [folder `seo/inputs/best/` to create]
- [ ] The question → article prompt flow written down, including whatever internal knowledge enriches it [file `seo/templates/article-default.md` to create]
- [ ] Anti-slop pass runs over every draft before you see it [check: `engine-seo/references/anti-slop-writing.md`] [skill `no-ai-slop-writting` to install]
- [ ] A site that builds from markdown and deploys on git push [folder `seo/site/` to create]
- [ ] OG metadata, dynamic sitemap, canonical URLs and RSS verified on one live URL [check]
- [ ] Weekly job that takes everything in the publishing folder, pushes it, and triggers the rebuild [weekly scheduler `engine-seo-publish` to create]
- [ ] Optional manual gate: the builder only reads an approved subfolder, and you move articles into it yourself [folder `seo/site/src/content/blog/` to create]
- [ ] One article live, with its `run_id` and URL recorded [check]

---

## 4. Social — `social/`

Its own pipeline end to end — same shape as SEO in places, its own references
and its own backlog. The publishing end is the platform, not GitHub.

- [ ] Workflow folder, one platform chosen for today [file `social/workflow.json` to create]
- [ ] Subject flow set up for this workflow — `engine-social/references/subject-finding.md`, validated on the platform rather than on search volume [file `social/sources.json` to create]
- [ ] ≥20 validated rows in this workflow's own backlog, each with a claim, its proof and a score [file `social/inputs/backlog.csv` to create]
- [ ] The top rows moved into the queue, each with the source that justifies it [folder `social/inputs/queue/` to create]
- [ ] ≥5 of your own best-performing posts on disk as the voice reference [folder `social/inputs/best/` to create]
- [ ] Anti-slop pass runs before you see the batch [check: `engine-social/references/anti-slop-writing.md`] [skill `no-ai-slop-writting` to install]
- [ ] Weekly job that drafts the batch and prepares the publish step (drafts for LinkedIn/X, API for Bluesky after your yes) [weekly scheduler `engine-social-weekly` to create]
- [ ] 5–7 posts drafted, ≥1 published, logged, URL recorded [check]
- [ ] One post format the user would publish unedited. No live A/B on day one [file `social/experiments.json` to create — leave `status: paused`]

---

## 5. Outreach — `outreach/`

- [ ] Workflow folder, goal, metric = replies [file `outreach/workflow.json` to create]
- [ ] A lead list on disk, or a workflow step that produces one — hand-build the first 20–50 [folder `outreach/inputs/audience/` to create] [skill `prospect-finder` to install]
- [ ] Ten sampled leads each yield one real, recent observation — if not, the source is wrong, not the copy [check]
- [ ] Leads normalised and deduped into the CRM, nobody in it twice [file `outreach/crm.csv` to create]
- [ ] **One** first-touch message, written with you and short enough that you'd send it unedited [file `outreach/templates/first-touch.txt` to create — the agent writes it, nothing ships] [file `outreach/experiments.json` to create — leave `status: paused`]
- [ ] Daily job that drafts `<n>` personalised emails — drafts only, never sends [daily scheduler `engine-outreach-daily` to create]
- [ ] Decided whether you're handling replies yourself or the agent drafts them — both are complete answers [check]
- [ ] *If the agent drafts them:* a starting block library, and a habit of adding a block every time a reply arrives that nothing covers [file `outreach/templates/followups/blocks.md` to create]
- [ ] Daily job that reads the replies and records them — a reply is a 1, a closed sequence with no reply is a 0. That *is* this workflow's metric job; don't add a second one [daily scheduler `engine-metrics-outreach` to create]
- [ ] ≥10 drafts sitting in your mailbox with CRM rows to match [check]

---

## 6. The loop — true for every workflow above

- [ ] **One metric job per workflow you ran today**, on that channel's clock — daily for outreach replies and social, weekly or slower for Search Console [daily scheduler `engine-metrics-<workflow>` to create — one each]
- [ ] Weekly job that renders the reports (and scores arms later, once anything is live) — **one for the whole workspace**, because reading the sibling reports together is the point [weekly scheduler `engine-weekly` to create]
- [ ] **No live experiments yet — that's correct.** Every workflow ships one template and `experiments.json` stays paused until its format is settled and 5–10 pieces have numbers. `engine-loop/references/ab-testing.md` → R0 [check]
- [ ] Every workflow has a `reports/latest.json` from a real run [check]
- [ ] Nothing posts, sends or promotes an arm without you [check]

---

## End-of-day proof

Four commands and one question. If they all answer, the day worked.

```bash
python3 <repo>/skills/engine-setup/scripts/doctor.py
python3 <repo>/skills/engine-loop/scripts/due_metrics.py
python3 <repo>/skills/engine-loop/scripts/score_arms.py
find . -name index.csv -path '*/runs/*' -exec wc -l {} +
```

Then ask your agent: **"list my scheduled tasks"** — every job you created today
should be there, active, with a next run time.

One published thing per workflow beats five folders of drafts. The schedulers
are what make tomorrow happen without you.
