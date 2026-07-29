---
name: engine-linkedin
description: Writes LinkedIn and X posts in the user's own voice, learned from their best-performing work, with the A/B arm assigned and the run logged. Posting is manual by default; Upload Post or Buffer optional. Use when the user says "write LinkedIn posts", "draft some tweets", "run the social workflow", "turn this into a post", or asks for short-form written content.
---

# engine-linkedin

Short-form written posts for LinkedIn and X. Same machinery as `engine-seo`, different format and a much shorter feedback loop — which makes it the best workflow to run the A/B loop on, because you get verdicts in weeks rather than months.

Workflow id in config and scripts: **`linkedin`**. Skill folder and `runlog` skill column: **`engine-linkedin`**.

## Before the first run

Pick **one** platform. LinkedIn and X reward different things and splitting attention early means learning neither. `config/channels.json` holds the choice.

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
python3 ../engine-loop/scripts/assign_arm.py --workflow linkedin
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
python3 ../engine-loop/scripts/runlog.py new --workflow linkedin --channel linkedin \
  --experiment exp-003 --arm question --template post-question.txt
```

One run per post. That's what makes the arm comparison work.

### 5. Publish

Manual by default — the user posts it themselves, then:

```bash
python3 ../engine-loop/scripts/runlog.py publish --run <run_id> --url https://...
```

The URL is needed to read the numbers back later. If they use Upload Post or Buffer, see `docs/posting-options.md`.

## Getting the numbers back

Impressions and engagement live behind their own login on both platforms, so the browser is the normal route:

```bash
python3 ../engine-loop/scripts/runlog.py metric --run <run_id> --value 3400 --source browser
```

**Wait at least 72 hours before recording.** LinkedIn and X keep distributing for days. A number read earlier tells you what time you posted, not whether the post was good — and once it's in `index.csv` it's in every verdict from then on. If it's been less than 72 hours, leave the cell empty and pick it up on the next run.

## Rules

- **Never post automatically.** Drafts go to the user
- **Never claim something the user hasn't done.** Invented anecdotes are the fastest way to burn a personal brand, and they're unrecoverable once someone notices
- **Never copy a competitor's post.** Take the structure if it works, never the words
- One platform until the loop says something useful about it
