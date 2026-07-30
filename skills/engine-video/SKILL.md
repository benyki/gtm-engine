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

**How (not just what):** the run below is the spine. The recipes live in `references/` — read the one for the step you're on instead of improvising ffmpeg or shot lists.

| Step | Reference |
|---|---|
| Shot list / segments | `references/structure-plan.md` |
| Voiceover | `references/voiceover.md` |
| Footage / Pexels | `references/footage-pexels.md` |
| Default render (text over B-roll) | `references/floating-text.md` |
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
- **Footage contract:** licensed clips you have the rights to. Pexels is the free source; their own asset library or another licensed stock service is equally valid.
- **Posting contract:** the run gets published and its URL recorded. Manual posting satisfies it with zero keys.

## The run

### 1. Get the arm before you write

```bash
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --workflow video
```

The hook is the variable worth testing — question versus claim, face versus text, first-second payoff versus slow build. Everything else is noise by comparison. If it returns `write_template`, write that template from the hypothesis.

### 2. Plan the structure

Before drafting prose, write `runs/<run_id>/plan.json` from
`references/structure-plan.md` (pattern → segments → durations). That file is the
shot list; don't invent new scenes mid-render without updating it.

### 3. Script

Vertical video is decided in the first second and a half.

- Open on the payoff or the tension, never on a greeting
- One idea. A 30-second video holds exactly one
- Write for the ear — short sentences, contractions, no clauses that need punctuation to parse
- 30–45 seconds is roughly 75–110 words
- Read it aloud before rendering. If you stumble, so will the voiceover

Voice and constraints from `shared/brand.md`. Put the full VO text on
`plan.json` → `voiceOverlay.fullScript`.

### 4. Voiceover

Follow `references/voiceover.md`. ElevenLabs by default, voice id in
this workflow's `workflow.json` — or whatever TTS the user already uses. Same voice across
arms. Timed multi-beat scripts = one clip per line, then assemble.

### 5. Footage

**Sourced first** from `shared/assets/` (or product screen recordings).
**Pexels as fallback** per `references/footage-pexels.md`. Real product footage
beats stock; all-stock channels look like every other channel.

Optional bed: `references/music.md` (rights first; files under `shared/assets/music/`).

### 6. Render

Defaults: 9:16 at 1080×1920 (this workflow's `workflow.json` → `video.resolution` /
`target_seconds`), H.264, audio at −14 LUFS, captions burned in.

**Default path:** floating text over B-roll — `references/floating-text.md` +
workspace starter `templates/floating-text-default.json` (in the workflow folder) +
`references/ffmpeg-recipes.md`.

**Optional looks** after the base render: `references/looks.md` (keep identical
across arms unless the look *is* the experiment).

**Remotion** when you need sequenced React composition: `references/remotion.md`.

Write the mp4 to `runs/<run_id>/output/final.mp4`.

### 7. Log and post

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --workflow video --channel tiktok \
  --experiment exp-004 --arm tension --template script-tension.txt
```

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
- **Never use footage you don't have the rights to.** Pexels is licensed; a clip scraped off someone's TikTok is not
- **Never clone a real person's voice** without their explicit permission
- Delete the intermediate files after a successful render. Video fills a disk faster than anyone expects
- If a render fails, fix it — don't ship a broken or half-length file

A hook verdict here usually says something about the social workflow's hooks
too — when a finding generalises, add a line to `shared/insights.md`, and put
reusable clips or end-cards in `shared/assets/` so siblings don't re-make them.

## Going further

- `references/advanced.md` — dedicated phone + mobilerun (read account-risk first)
- Deeper tool skills (optional install): `benyki/skills` — `ffmpeg`, `elevenlabs`,
  `video-floating-text`, `video-filter`, `upload-post`, `remotion-best-practices`,
  `music-downloader`, `pexel-video-downloader` — see `docs/additional-skills.md`
