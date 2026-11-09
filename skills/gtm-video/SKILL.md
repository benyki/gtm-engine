---
name: gtm-video
description: Makes short-form vertical video as a recurring workflow in the project's workflows/ folder. Plan, hook, voiceover, footage, 9:16 render (ffmpeg floating text by default, Remotion optional), optional look and music, then post on an explicit yes and log it. Use when the user says "make a video", "set up a video workflow", "run the video workflow", "turn this into a Reel/TikTok/Short", or asks for short-form video content.
---

# gtm-video

Script to rendered 9:16 mp4. The heaviest kind of gtm workflow: it needs disk,
keys and patience, so don't start here unless video really is the channel.

Every path below is relative to the workflow folder, `<repo>/workflows/<name>/`
(how that folder works: [`../gtm/SKILL.md`](../gtm/SKILL.md)). Each video gets
`runs/<run_id>/`, with `run_id` as `<YYYY-MM-DD>-<slug>`.

## Start

1. **Copy the template** (skip if `gtm` already made the folder): `cp -R`
   this skill's `template/` to `<repo>/workflows/<name>/`, named after what it
   makes (`tiktok-app-demos`). Fill in the README's first lines, the number
   and its Defaults.
2. **Voice.** The project's own voice notes. None? The five questions in
   [`../gtm/SKILL.md`](../gtm/SKILL.md) (Voice), answers written to `brand.md` in the folder.
3. **Tools.** `ffmpeg` with libass (`brew install ffmpeg`), the overlay font
   installed once (`cp ~/.agents/skills/gtm-video/assets/fonts/*.ttf ~/Library/Fonts/`),
   and the keys you need (below). A first video needs only `PEXELS_API_KEY`, or
   nothing if the user has their own clips.
4. **Plan and render one.** Pick a format, copy its example to
   `runs/<run_id>/inputs.json`, fill the placeholders, render it on the
   floating-text path (`references/floating-text.md`).
5. **Show it, post on a yes.** Hand over the mp4, its caption and the rights
   line for each clip. Once it's live, add a row to `log.csv`.

## Formats

Pick one **before** anything else: it sets the length, the footage, the voice
and the music level. Full rules: `references/formats.md`.

| | Length | Voice | Music | Copy from |
|---|---|---|---|---|
| **Viral product**: 4s hook + ~12s of the product working | ~16s | usually none | **50%** | `examples/viral-app-demo.json` |
| **Viral vibe**: one meditative clip, two lines of text, product named only in the caption | 8–15s | never | **50%** | `examples/viral-vibe.json` |
| **Informative**: text content (an article, a dataset, a series) made watchable | 30–60s | **ElevenLabs** | 3% *(optional)* | `examples/informative-vocab.json`, `examples/informative-recap.json` |

**50% is a no-voice level.** Once a voiceover exists the bed drops to ~3%, or
it fights the voice and loudness normalisation makes it worse.

The examples are real production configs with every project-specific value
replaced by a placeholder. They're proven starts, not the ceiling: tweak them,
and invent a format that isn't here (talking head, before/after, POV) when your
read on the audience says so. Change one thing at a time so you can tell what
moved the number. A second format is a second workflow folder.

## Keys

| Variable | For | Cost |
|---|---|---|
| `PEXELS_API_KEY` | stock footage, the fallback | free |
| `ELEVENLABS_API_KEY` | voiceover | free tier |
| `UPLOADPOST_API_KEY` | posting, optional | free to 10 posts a month |
| `FAL_KEY` | generated clips, optional | credits |

From the project's own env setup: read `.env.example` for the names, add a
missing name to it with no value, and let the user paste values themselves. Never
read `.env`; load it for a command (`set -a; . <repo>/.env; set +a`). Each is a
default: any TTS that yields a clean WAV, any footage with a named rights
position, and manual posting all do the job.

## The run

**1. Plan.** Copy the matching example to `runs/<run_id>/inputs.json` and fill
it in, segments and durations per `references/structure-plan.md`. It is the
shot list, the config and the only record of what the video was made of. Then
check it isn't a remake (from the workflow folder, or add `--dir workflows/<name>`):

```bash
python3 ~/.agents/skills/gtm-video/scripts/combo_check.py check --inputs runs/<run_id>/inputs.json
```

Same inputs or same scene durations alone is a real edit; both at once is a
duplicate the platform buries. Exit 1 names the collision: change one side and
re-check. `references/duplicate-safety.md`.

**2. Script and on-screen text.** Vertical video is decided in the first second
and a half. Open on the payoff or the tension, never a greeting. One idea. Write
for the ear: short sentences, contractions. 30–45 seconds is roughly 75–110
words. Read it aloud; if you stumble, so will the voiceover. Voice comes from
the project's notes or `brand.md`; the text goes on `voiceOverlay.fullScript`.
On-screen text is a separate craft, written for the eye, muted, at speed:
`references/hook-guide.md`, copy on `segments[].textOverlay.lines`. The hook is
the first thing worth varying: question versus claim, face versus text.

**3. Voiceover.** `references/voiceover.md`. ElevenLabs with the voice id from
the README, or whatever TTS the user already uses. Same voice on every video.

**4. Footage.** Own footage first: product screen recordings, the project's
media, `assets/` here. Pexels as the fallback (`references/footage-pexels.md`).
All-stock channels look like every other channel. Generated clips, yt-dlp and
short-form platforms each carry a different rights position
(`references/clip-sourcing.md`): pick **with the user**, and note per clip which
licence or permission covers it.

**5. Music: offer it, every time.** In the no-voice formats the bed is the
video's energy, and a user never offered one assumes they must find it. Ask with
real options: *"I'll add a bed under this one. Name a track or an artist, or
I'd go calm lo-fi / ambient piano for this clip. Driving electronic suits
demos, warm acoustic founder pieces, a cinematic build a reveal."* Fetch what
they name into `assets/music/` (`references/music.md`). Say the rights line once:
their own upload, a bought track or a royalty-free library is clear; a trending
platform sound shipped in a rendered file is not. Unclear? Ship voice-only or a
royalty-free bed. Level: 0.5 with no voiceover, 0.03 under one.

**6. Render.** 1080×1920 (or the README's canvas), H.264, −14 LUFS, text burned
in. Default path: floating text over B-roll, `references/floating-text.md` with
`templates/floating-text-default.json`, the locked type from
`references/ffmpeg-text-style.md`, commands from `references/ffmpeg-recipes.md`.
Optional looks after the base render: `references/looks.md`. Remotion for
sequenced React composition, the right call for an informative series:
`references/remotion.md`. Output: `runs/<run_id>/output/final.mp4`. When a
format carries facts (exact words, numbers, prices), a twenty-line checker that
reads `inputs.json` and exits non-zero beats a checklist: it blocks the post.

**7. Caption.** The only place attribution happens when the product never
appears on screen. Keep them in `templates/captions.md`, grouped by kind of
video. Short and written like a person: at most one first-person mention ("the
app I use for this is X"), never "link in bio". Not in the first line, which is
what shows before "more". Rotate three or four phrasings. Match what's on
screen. Start with two or three, then ask the user to paste their
best-performing captions and rewrite the file around them.

**8. Post and log.** Manual, Upload Post or Buffer:
`references/posting-options.md` (which) and `references/posting-api.md` (how).
Once it's live, one row in `log.csv`:

```csv
date,channel,link,what_it_tried,result
2026-11-03,tiktok,https://www.tiktok.com/@<handle>/video/<id>,question hook over a screen recording,
```

`what_it_tried` is the one thing this video did differently. Then delete the
intermediate files; video fills a disk fast. Never delete
`runs/<run_id>/inputs.json`: it's the only record of what was already made.

## Results and what we learned

Wait at least 72 hours: the platforms keep pushing a video for days and an
early number is noise. Then fill in `result`. Views come off the public URL:

```bash
yt-dlp -J --no-warnings "<link>" | python3 -c "import json,sys; print(json.load(sys.stdin)['view_count'])"
```

Watch-through, the number that says whether the hook worked, lives only in the
creator dashboard; log it when the user can read it, otherwise log views. When
something clearly won or lost, add one line to the README's "What we learned".

## Scheduling (optional)

Rendering stays manual by default; it's slow and the step where a human eye is
cheapest. One scheduled task per workflow is the usual shape, in whatever
scheduler the project uses: say, a daily run that fills in `result` for rows
older than 72 hours and drafts the next video for approval. It never posts. The
README records when it runs, where, and the exact prompt.

## Rules

- **Never post without an explicit yes.** The user approves every upload
- **Know which right covers every clip** (owned, licensed or permitted) and say
  which at hand-over. Anything else is reference: state the risk once, the user decides
- **Never clone a real person's voice** without their explicit permission
- **Never render a config that reuses both the same inputs and the same durations**
- **Four or five posts a day per account is the ceiling**, spaced hours apart;
  three good posts a week beats twenty in a day. A burst silently cuts reach
- Renders, footage, voiceover audio and music stay out of git (the template's
  `.gitignore`); `inputs.json`, `log.csv` and the README go in
- If a render fails, fix it. Never ship a broken or half-length file

## Going further

- `references/advanced.md`: posting from a real device, and the cheaper wins first
- A hook finding here usually holds for `gtm-social` first lines too
- Optional tool skills from `benyki/gtm-skills` (`ffmpeg`, `elevenlabs`,
  `video-floating-text`, `video-filter`, `upload-post`, `remotion-best-practices`,
  `music-downloader`, `pexel-video-downloader`):
  [`docs/additional-skills.md`](https://github.com/benyki/gtm-engine/blob/main/docs/additional-skills.md)
