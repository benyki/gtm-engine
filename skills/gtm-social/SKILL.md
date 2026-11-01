---
name: gtm-social
description: Writes short-form social posts (LinkedIn, X, Bluesky and similar text channels) in the user's own voice, learned from their best posts, from a workflow folder in the project. LinkedIn and X post from the user's logged-in browser; Bluesky posts through its API after approval. Use when the user says "write LinkedIn posts", "draft some tweets", "post to Bluesky", "set up a social workflow", "turn this into a post", or asks for short-form written content.
---

# gtm-social

Short-form written posts for LinkedIn, X, Bluesky and other text channels: a
template folder to copy, and the craft to fill it. The work lives in
`<repo>/workflows/<name>/`, and every path below is relative to that folder.
How workflow folders work in general: [`../gtm/SKILL.md`](../gtm/SKILL.md).

## Start

1. **Copy the template** (skip if `gtm` already made the folder), named after
   what it does:
   `mkdir -p workflows && cp -R ~/.agents/skills/gtm-social/template workflows/linkedin-posts`.
   Fill in the README's first lines: the channel, the account, who it's for,
   the number
2. **Find the voice.** The project's own brand or voice notes. None? The five
   questions in [`../gtm/SKILL.md`](../gtm/SKILL.md) (Voice), answers written to `brand.md` here
3. **Ask for their best work**: five of their own posts that did well
   (`inputs/best/`), and 5 to 10 posts by anyone they wish they'd written
   (`inputs/swipe/`). Nothing to hand? Carry on and ask again next time
4. **Ask what they did this week**: a shipped feature, a decision, a number, a
   customer conversation. That's the first post
5. **Draft three to five, run the anti-slop pass, show them.** The one they pick
   ships after their yes and gets a row in `log.csv`

**One platform to start**: LinkedIn, X and Bluesky reward different things, and
a second platform is a second workflow folder. LinkedIn and X need the browser
extension (*Claude in Chrome* or equivalent), because posting and numbers sit
behind the user's login; check it's connected by opening a page and reading
the title back. Bluesky posts and reports through its own API.

## The craft

| Step | Reference |
|---|---|
| Find and validate subjects | `references/subject-finding.md` |
| Read platforms and threads in the browser | `references/browser-research.md` |
| **Cut AI slop, keep the voice: every batch** | `references/anti-slop-writing.md` |
| Pick an image, or edit one through an image API *(optional)* | `references/images.md` |
| Write a thread, post on X or LinkedIn (browser) | `references/threads-and-x.md` |
| Post on Bluesky (API) | `references/bluesky-post.md` |

**Voice comes from their best work.** `inputs/best/` (their own top posts)
teaches the voice: vocabulary, rhythm, formatting, how blunt they are.
`inputs/swipe/` (other people's posts they admire) teaches the shapes: how a
good post opens, turns and lands. Read both before writing. Turn the swipe
file into **structures, not copies**: name what each first line does, what the
middle is made of, how it closes ("the receipt: a number, then the story
behind it, no lesson"), show the user three or four, and make the ones they
approve into templates in `templates/`. **Never copy the words.**

**Subjects run out before writing does.** In order of what works: what they did
this week (the day-one default, and nobody else has it); what already worked
(`log.csv`, "What we learned"); their own published work (one article is three
or four posts); questions the audience actually asks, read for phrasing and
friction. Scored subjects go in `inputs/backlog.csv`, about 20 validated rows
ahead; `references/subject-finding.md` has the method, the 0 to 9 score and
the kill step.

**The daily twelve** keeps that backlog full once the first batch is out: four
candidates from Reddit (`references/browser-research.md` §2), four from the RSS
feeds in the README's Sources (build the list with the user the first time),
four variations of their references (a structure from `inputs/best/` or
`inputs/swipe/` with this week's material). Rate all twelve against the user's
criteria in Sources (ask the first time what makes a subject worth posting;
until then use the 0 to 9 score and say so), keep the top one, and mark the
rest `killed` with their scores so they don't cycle back.

**Drafting.** A batch of three to seven, so the user rejects a direction rather
than a sentence, saved as `posts/<date>.md` with one line per draft on what it
tries (that line goes in the log).

- The first line is the only part most people read. Openers that earn the
  second: a flat specific claim, a number with no setup, the reversal, the
  confession, the question you actually get asked. With `gtm-video` installed,
  `gtm-video/references/hook-guide.md` §2 has more angles
- One idea per post. No engagement bait, no "agree?", no fake vulnerability
- Formatting matches `inputs/best/`
- Run `references/anti-slop-writing.md` over the whole batch before showing it

**Blocks, optional.** Once a part has settled (the sign-off, the one-line "what
I do"), keep its variations in `templates/blocks/` and rotate them; never the
same one twice in a batch. Format in `templates/blocks/README.md`.

**Images, optional.** After the drafts exist, propose one image from
`inputs/images/` (read it, never write to it) for one post, with a line on why.
To crop, swap a background or resize an image the user owns:

```bash
python3 ~/.agents/skills/gtm-social/scripts/edit_image.py \
  --image inputs/images/dashboard.png --prompt "..." \
  --out posts/2026-11-03-post-1.png
```

Gemini by default, `--provider openai` for GPT Image, with `GEMINI_API_KEY` or
`OPENAI_API_KEY` from the project's env. **Ask before the first call in a
session**: it's paid per image. Look at the result before showing it; these
models rewrite chart numbers unasked. More in `references/images.md`.

## Publish

- **LinkedIn and X**: hand them the draft, or drive the composer in their
  browser per `references/threads-and-x.md`, after their yes for that post
- **Bluesky**: the AT Protocol API with an app password, per
  `references/bluesky-post.md`. 300 graphemes, up to 4 images with alt text

## Log and learn

One row per shipped post in `log.csv`:

```csv
date,channel,link,what_it_tried,result
2026-11-03,linkedin,https://www.linkedin.com/feed/update/...,number opener with no setup,
```

**Fill in `result` after at least 72 hours**: LinkedIn and X keep distributing
for days, and an earlier number only tells you what time you posted. Read it in
the browser (Bluesky: its API). When a post clearly won or lost, add one line
to the README's "What we learned"; the next batch reads it first.

## Schedule, optional

Short-form dies from irregularity faster than from bad posts. Once the voice is
right, one daily task covers it: fill in `result` for posts older than 72
hours, run the daily twelve, draft the survivor, leave it for review. Record
when, where and the exact prompt in the README. **It drafts; it never posts.**

## Rules

- **Never publish without the user's yes.** On LinkedIn and X, drafts go to the
  user to post; on Bluesky the agent may post via the API, after an explicit
  approval per post, not instead of one. A logged-in browser is not consent,
  and neither is a scheduled run
- **Never claim something the user hasn't done.** An invented anecdote is
  unrecoverable once someone notices
- **Never copy someone else's post.** The structure, never the words
- **Never generate an image that functions as proof**: a metrics screenshot, a
  revenue chart, a testimonial. Edits go to `posts/`, never `inputs/images/`

## Going further

Optional skills from `benyki/gtm-skills`, installed per
[`docs/additional-skills.md`](https://github.com/benyki/gtm-engine/blob/main/docs/additional-skills.md):

| Skill | What it adds |
|---|---|
| `x-browser-post` | the frozen X element map, the clipboard image script, the staged-thread loop, a quirks file |
| `bluesky-post-manage` | Bluesky chains, images, multi-account, delete |
| `app-thread-generate` + `app-thread-backstory` | a worked write-then-post pipeline with a backlog; take the shape, swap in the user's paths and brand |
