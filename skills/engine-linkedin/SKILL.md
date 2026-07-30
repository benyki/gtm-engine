---
name: engine-linkedin
description: Writes LinkedIn, X and Bluesky posts in the user's own voice, learned from their best-performing work, with the A/B arm assigned and the run logged. LinkedIn and X post from the user's browser; Bluesky posts via its AT Protocol API after approval. Use when the user says "write LinkedIn posts", "draft some tweets", "post to Bluesky", "run the social workflow", "turn this into a post", or asks for short-form written content.
---

# engine-linkedin

Short-form written posts for LinkedIn and X. Same machinery as `engine-seo`, different format and a much shorter feedback loop — which makes it the best workflow to run the A/B loop on, because you get verdicts in weeks rather than months.

Workflow id in config, scripts and the run log: **`linkedin`**. Skill folder: **`engine-linkedin`**.

## Before the first run

Pick **one** platform to start. LinkedIn, X and Bluesky reward different things, and splitting attention early means learning neither. `config/channels.json` holds the choice.

If you run more than one, keep the accounting per channel: log each run with the channel it actually shipped to, and give each its own `primary_metric` / `metric_delay_hours` in `channels.json` where they differ.

Whether one experiment can span both platforms depends on the metric, not the platform count. Platform-native numbers (impressions, likes) are different currencies at different scales — an arm mean pooled across them mostly measures where you posted, so scope those experiments per channel (`"channel"` on the experiment, `--channel` on `assign_arm.py`). A metric you measure at your own end in one currency — clicks, signups, replies — compares fine across platforms, and pooling it into one experiment reaches a verdict faster.

## Where posts come from

In order of what actually works:

1. **The queue** — `inputs/queue/`, written by `engine-loop` from what performed. Start here when it's not empty
2. **Their own material** — a shipped feature, a support conversation, a decision they made and why, a number they can share. Specific beats clever. This is the day-one default when the queue is empty
3. **An article they've already written** — one `engine-seo` piece is three or four posts
4. **A real question from the audience** — same Reddit mining as `engine-seo`

## The run

### 1. Read their voice first

`inputs/best/` — their top-performing posts. Read them before writing anything, every single time. Voice is copied from examples, never from a description of a voice. If `inputs/best/` is empty, say so and ask for five links; the output will be generic otherwise and no amount of prompting fixes it.

### 2. Get the arm

```bash
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --workflow linkedin
```

Good variables here: how the post opens, whether it tells a story or states a claim, one-liner versus paragraphs, ends on a question versus ends flat. If it returns `write_template`, write that template from the hypothesis and use it.

### 3. Draft a batch, not one

Five to seven posts. Short-form is cheap to write and expensive to judge in isolation — a batch lets the user see the pattern and reject a direction rather than a sentence.

- The first line decides everything. It's the only part most people read
- One idea per post
- No engagement bait, no "agree?", no fake vulnerability, no thread of platitudes
- Formatting matches what's in `inputs/best/` — if they don't use line breaks between every sentence, don't start

### 4. Log each one

Use the arm and template `assign_arm.py` returned — for example, when it picks the question opener:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --workflow linkedin --channel linkedin \
  --experiment exp-003 --arm question --template post-question.txt
```

One run per post. That's what makes the arm comparison work.

### 5. Publish

**LinkedIn and X** — the user posts from their logged-in browser (you hand them
the draft). Then record the URL:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish --run <run_id> --url https://...
```

**Bluesky** — post via the AT Protocol API after explicit per-post approval
(see below). Schedulers (Upload Post / Buffer) are a video concern; see
`engine-video/references/posting-options.md` if you later want them for text too.

The URL is needed to read the numbers back later.

## Bluesky

Bluesky is the exception to manual-by-default: the AT Protocol API is open and posting through it is sanctioned, so the agent can publish directly — **the approval boundary doesn't move, though.** The user approves every post before it goes out; the API only changes who clicks.

Getting connected:

- **Never use the account password.** Bluesky issues **app passwords** for exactly this: Settings → Privacy and Security → App Passwords (format `xxxx-xxxx-xxxx-xxxx`). One per agent/machine, revocable independently
- Store them as `BSKY_HANDLE` / `BSKY_APP_PASSWORD` in the workspace `config/.env` (the scaffold's `.env.example` lists them), never in chat, never committed. A leaked app password gets revoked in the same settings screen
- The official SDK is `@atproto/api` (Node 18+): log in with `AtpAgent` (`BskyAgent` is deprecated), post with `agent.post(...)`. Writes go to `https://bsky.social`; public reads need no auth
- If a Bluesky posting skill is already installed on the machine (e.g. `bluesky-post-manage`), use it instead of re-implementing — check the agent's skill list before writing code

Format constraints worth knowing before drafting: **300 graphemes** max per post (threads for anything longer), up to 4 images of ~1 MB each — alt text on every one — and mentions/links/hashtags need facets (`RichText.detectFacets()` handles it; don't compute byte offsets by hand).

The loop treats it like any channel: add a `bluesky` entry to `channels.json`, log runs with `--channel bluesky`, record the post URL on publish, and read likes/reposts/replies back through the same API — `--source api`. Engagement settles fast there; a shorter `metric_delay_hours` than the social default is reasonable.

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
