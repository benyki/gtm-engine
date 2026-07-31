---
name: engine-video
description: Makes short-form vertical video — plan (VideoArchitecture), voiceover, footage, render 9:16 (ffmpeg floating-text by default, Remotion optional), optional looks/music, then post and log. Use when the user says "make a video", "run the video workflow", "turn this into a Reel/TikTok/Short", or asks for short-form video content.
---

# engine-video

Script to rendered 9:16 mp4. The heaviest workflow in the repo — it needs disk, keys and patience — so don't pick it as a first workflow unless video is genuinely the channel.

This skill runs any workflow folder of **type `video`**. The default folder is
`video/`; paths below (`templates/`, `runs/`, `inputs/`) are inside it, while
brand, accounts, keys and **reusable footage/fonts/logos live in `shared/`**
(`shared/assets/` — any workflow can use them). **Several video workflows are a
normal shape** — `video/` for product demos and `video-founder/` for talking-head
content, each with its own templates, experiments and metric — scaffold with
`--merge --workflow video-founder:video`, or copy a folder and empty its
`runs/` and `reports/` (history belongs to the original). Render knobs (`resolution`, `target_seconds`,
voice id) live in each folder's `workflow.json` under `video`, so two video
workflows can render differently.

## Three formats, by default

Decide which one you're making **before** anything else — it sets the length,
the footage, whether there's a voice, and how loud the music is. Full spec and
the editorial rules for each: `references/formats.md`.

| | Length | Voice | Music | Copy from |
|---|---|---|---|---|
| **Viral product** — 4s hook + ~12s of the product working | ~16s | usually none | **50%** | `examples/viral-app-demo.json` |
| **Viral vibe** — one meditative clip, two lines of text, product named only in the caption | 8–15s | never | **50%** | `examples/viral-vibe.json` |
| **Informative** — text content (an article, a dataset, a series) turned into something watchable | 30–60s | **ElevenLabs** | 3% *(optional)* | `examples/informative-vocab.json`, `examples/informative-recap.json` |

**50% is a no-voice level.** The moment a voiceover exists the bed drops to ~3%
in any format, or it fights the voice and loudness normalisation makes it worse.

The four `examples/` are real production configs with every project-specific
value replaced by a placeholder that says what belongs there. Read the one
matching your format before writing a config — they carry the editorial rules
that took real posts to learn.

**All three have worked for real products; none of them is guaranteed to work
for yours.** They're defaults because they save you the first ten failures, not
because they're the ceiling. Tweaking them — hook length, cut count, music,
where the product appears — is expected, and **inventing a format that isn't
here is encouraged**: talking head, before/after, POV, reaction, silent tutorial.
Your read on how your audience watches beats this table. Change one thing per
experiment so the verdict means something, and give a genuinely new format its
own workflow folder. `references/formats.md` covers how.

Running two formats means **two workflow folders** (`video/` and `video-vibe/`),
not one folder with two kinds of run: different metrics, different experiments,
different queues.

**How (not just what):** the run below is the spine. The recipes live in `references/` — read the one for the step you're on instead of improvising ffmpeg or shot lists.

| Step | Reference |
|---|---|
| Which format, and its rules | `references/formats.md` |
| Shot list / segments | `references/structure-plan.md` |
| Voiceover | `references/voiceover.md` |
| Where clips come from (and the rights call) | `references/clip-sourcing.md` |
| Footage / Pexels | `references/footage-pexels.md` |
| Default render (text over B-roll) | `references/floating-text.md` |
| Locked text style (font, size, position) | `references/ffmpeg-text-style.md` |
| Never shipping the same video twice | `references/duplicate-safety.md` |
| ffmpeg commands | `references/ffmpeg-recipes.md` |
| Optional looks | `references/looks.md` |
| Music beds | `references/music.md` |
| Remotion path | `references/remotion.md` |
| Posting how-to | `references/posting-api.md` |
| Manual vs Upload Post vs Buffer | `references/posting-options.md` |

## What it needs

| Thing | Why | Free? |
|---|---|---|
| `ffmpeg` | rendering | yes — `brew install ffmpeg` |
| `PEXELS_API_KEY` | background footage | yes |
| `ELEVENLABS_API_KEY` | voiceover | free tier |
| `UPLOADPOST_API_KEY` | posting, optional | free to 10 posts/month |
| ~10 GB disk | video is large | — |

Check `shared/.env.example` for the exact names. Never read `shared/.env` itself.

These are the **defaults**, not requirements — each row is one way to satisfy a contract:

- **Voiceover contract:** any TTS that yields a clean WAV works; what matters is the *same voice across every arm* of an experiment. If the user has a brand voice in another tool, use it and skip ElevenLabs.
- **Footage contract:** every clip has a named rights position — owned, licensed, or permitted. Pexels is the free default; their own asset library, paid stock, generated clips and downloads each satisfy it differently. `references/clip-sourcing.md` compares them.
- **Posting contract:** the run gets published and its URL recorded. Manual posting satisfies it with zero keys.

## The run

### 1. Get the arm before you write

```bash
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --workflow video
```

The hook is the variable worth testing — question versus claim, face versus text, first-second payoff versus slow build. Everything else is noise by comparison, and it converges fastest. If it returns `write_template`, write that template from the hypothesis.

**On a fresh workflow this returns `use_template` and that's correct** — the
starter experiments ship paused on purpose. Ship one video until the user is
happy with the format, then start testing. `engine-loop/references/ab-testing.md`
→ R0 has the three conditions for flipping an experiment live.

Testing a whole **format** against a working one is a different, slower test: worth doing once this workflow is solid and the hook loop has stopped teaching you anything, never as the way to find your first winner. `references/advanced.md` → *A/B testing whole formats*.

### 2. Plan the structure

Pick the format first (`references/formats.md`), then copy the matching
`examples/*.json` and fill in its placeholders. Write the result to
`runs/<run_id>/inputs.json` — segments and durations per
`references/structure-plan.md`. That file is the shot list **and the config** —
the dedupe fingerprints are derived from it — so don't invent new scenes
mid-render without updating it.

Then check you're not about to remake something this workflow already made:

```bash
python3 ~/.agents/skills/engine-video/scripts/combo_check.py check \
  --workflow video --inputs runs/<run_id>/inputs.json
```

**Never reuse the same inputs *and* the same scene durations.** Same inputs
re-timed is a real edit; the same rhythm carrying new material is too; both at
once is a duplicate and the platform buries it. Exit 1 names the collision —
change one side and re-check. `references/duplicate-safety.md`.

### 3. Script

Vertical video is decided in the first second and a half.

- Open on the payoff or the tension, never on a greeting
- One idea. A 30-second video holds exactly one
- Write for the ear — short sentences, contractions, no clauses that need punctuation to parse
- 30–45 seconds is roughly 75–110 words
- Read it aloud before rendering. If you stumble, so will the voiceover

Voice and constraints from `shared/brand.md`. Put the full VO text on
`inputs.json` → `voiceOverlay.fullScript`.

### 4. Voiceover

Follow `references/voiceover.md`. ElevenLabs by default, voice id in
this workflow's `workflow.json` — or whatever TTS the user already uses. Same voice across
arms. Timed multi-beat scripts = one clip per line, then assemble.

### 5. Footage

**Sourced first** from `shared/assets/` (or product screen recordings).
**Pexels as fallback** per `references/footage-pexels.md`. Real product footage
beats stock; all-stock channels look like every other channel.

Other sources — generated clips (fal.ai), yt-dlp from YouTube or Pinterest,
short-form platforms — are all viable and each carries a different rights
position. `references/clip-sourcing.md` lays out the options; pick one **with
the user** rather than defaulting silently, and note per clip which license or
permission it's covered by.

Optional bed: `references/music.md` (rights first; files under `shared/assets/music/`).

### 6. Render

Defaults: 9:16 at 1080×1920 (this workflow's `workflow.json` → `video.resolution` /
`target_seconds`), H.264, audio at −14 LUFS, captions burned in.

**Default path:** floating text over B-roll — `references/floating-text.md` +
workspace starter `templates/floating-text-default.json` (in the workflow folder) +
`references/ffmpeg-recipes.md`.

**Optional looks** after the base render: `references/looks.md` (keep identical
across arms unless the look *is* the experiment).

**Remotion** when you need sequenced React composition: `references/remotion.md`
— the right call for the informative formats, where the composition is built once
and fed configs forever.

**Music level is set by the format, not by taste:** 50% when there's no voice,
3% under one. `references/music.md` for the mechanics.

Write the mp4 to `runs/<run_id>/output/final.mp4`.

### 7. Log and post

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --workflow video --channel tiktok \
  --experiment exp-004 --arm tension --template script-tension.txt
```

Two records, two jobs: the run row says a video was made and what it earned;
`runs/<run_id>/inputs.json` says what it was made of, which is what makes the
next `combo_check` mean anything. Keep the config with the run — it's the only
memory this workflow has of what has already been built.

Posting mode: manual, Upload Post, or Buffer —
`references/posting-options.md` (decision) and `references/posting-api.md` (how).
Device posting: `references/advanced.md` (account-risk first). Record the URL:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish --run <run_id> --url https://...
```

## Getting the numbers back

Read them off the platform's own analytics screen in the browser:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py metric --run <run_id> --value 12400 --source browser
```

Views alone are a weak signal. Watch-through rate is the one that tells you whether the hook worked. `index.csv` holds only the primary metric — put the second number in the run's `metrics.json` under `secondary` (e.g. `"secondary": {"watch_through_rate": 0.41}`), which is open for exactly this; every re-read of the primary is appended to its `history` automatically, so a 3-week read never erases the 72-hour one.

**Wait at least 72 hours before recording.** TikTok, Reels and Shorts all keep pushing a video for days, and some of them re-surface it after a week. An early number is mostly noise, and once it's recorded it distorts every verdict that follows. Less than 72 hours old? Leave it empty and catch it on the next pass.

## Rules

- **Never post automatically.** The user approves every upload
- **Know which right covers every clip you ship** — owned, licensed, or
  permitted — and say which when you hand the render over. Where a clip is none
  of those, it's reference material: state the risk once and let the user
  decide. `references/clip-sourcing.md`
- **Never clone a real person's voice** without their explicit permission
- **Never render a config that reuses both the same inputs and the same durations.** `references/duplicate-safety.md`
- Delete the intermediate files after a successful render. Video fills a disk faster than anyone expects — but **never delete `runs/<run_id>/inputs.json`**. It's two kilobytes and it's the only record of what this workflow has already made
- If a render fails, fix it — don't ship a broken or half-length file

A hook verdict here usually says something about the social workflow's hooks
too — when a finding generalises, add a line to `shared/insights.md`, and put
reusable clips or end-cards in `shared/assets/` so siblings don't re-make them.

## Going further

- `references/advanced.md` — dedicated phone + mobilerun (read account-risk first)
- Deeper tool skills (optional install): `benyki/skills` — `ffmpeg`, `elevenlabs`,
  `video-floating-text`, `video-filter`, `upload-post`, `remotion-best-practices`,
  `music-downloader`, `pexel-video-downloader` — see `docs/additional-skills.md`
