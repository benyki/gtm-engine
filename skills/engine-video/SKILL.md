---
name: engine-video
description: Makes short-form vertical video — script, voiceover via ElevenLabs, footage sourced or pulled from Pexels, rendered 9:16 with ffmpeg — with the A/B arm assigned and the run logged. Posting is manual or via Upload Post. Use when the user says "make a video", "run the video workflow", "turn this into a Reel/TikTok/Short", or asks for short-form video content.
---

# engine-video

Script to rendered 9:16 mp4. The heaviest workflow in the repo — it needs disk, keys and patience — so don't pick it as a first workflow unless video is genuinely the channel.

## What it needs

| Thing | Why | Free? |
|---|---|---|
| `ffmpeg` | rendering | yes — `brew install ffmpeg` |
| `PEXELS_API_KEY` | background footage | yes |
| `ELEVENLABS_API_KEY` | voiceover | free tier |
| `UPLOADPOST_API_KEY` | posting, optional | free to 10 posts/month |
| ~10 GB disk | video is large | — |

Check `config/.env.example` for the exact names. Never read `config/.env` itself.

## The run

### 1. Get the arm before you write

```bash
python3 ../engine-loop/scripts/assign_arm.py --workflow video
```

The hook is the variable worth testing — question versus claim, face versus text, first-second payoff versus slow build. Everything else is noise by comparison. If it returns `write_template`, write that template from the hypothesis.

### 2. Script

Vertical video is decided in the first second and a half.

- Open on the payoff or the tension, never on a greeting
- One idea. A 30-second video holds exactly one
- Write for the ear — short sentences, contractions, no clauses that need punctuation to parse
- 30–45 seconds is roughly 75–110 words
- Read it aloud before rendering. If you stumble, so will the voiceover

Voice and constraints from `config/brand.md`.

### 3. Voiceover

ElevenLabs, with the voice id in `config/channels.json`. Keep the same voice across runs — an inconsistent voice reads as inconsistent brand, and it also contaminates the A/B comparison.

### 4. Footage

**Sourced first.** Their own clips in `inputs/assets/`, or product screen recordings. Real footage of the actual product beats stock every time.

**Pexels as fallback.** When there's nothing to source, pull background footage from Pexels. It's a safety net so the workflow always completes — not the default look. If every video is stock footage, the channel looks like every other channel.

### 5. Render

9:16, 1080×1920, H.264, audio at -14 LUFS. Burn captions in — most people watch muted, and platform auto-captions are unreliable and ugly.

Write the mp4 to `runs/<run_id>/output/`.

### 6. Log and post

Use the arm and template `assign_arm.py` returned — for example, when it picks the tension opener:

```bash
python3 ../engine-loop/scripts/runlog.py new --workflow video --channel tiktok \
  --experiment exp-004 --arm tension --template script-tension.txt
```

Posting is manual by default — the free tier of Upload Post caps at 10 posts a month, which goes quickly. Either way, record the URL:

```bash
python3 ../engine-loop/scripts/runlog.py publish --run <run_id> --url https://...
```

## Getting the numbers back

Read them off the platform's own analytics screen in the browser:

```bash
python3 ../engine-loop/scripts/runlog.py metric --run <run_id> --value 12400 --source browser
```

Views alone are a weak signal. Watch-through rate is the one that tells you whether the hook worked, so record that when the platform shows it.

**Wait at least 72 hours before recording.** TikTok, Reels and Shorts all keep pushing a video for days, and some of them re-surface it after a week. An early number is mostly noise, and once it's recorded it distorts every verdict that follows. Less than 72 hours old? Leave it empty and catch it on the next pass.

## Rules

- **Never post automatically.** The user approves every upload
- **Never use footage you don't have the rights to.** Pexels is licensed; a clip scraped off someone's TikTok is not
- **Never clone a real person's voice** without their explicit permission
- Delete the intermediate files after a successful render. Video fills a disk faster than anyone expects
- If a render fails, fix it — don't ship a broken or half-length file

## Going further

`references/advanced.md` — posting from a dedicated phone with mobilerun and a consistent VPN, which gets past what the posting APIs won't let you do. Read the account-risk section before acting on it.
