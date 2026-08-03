---
name: engine-video
description: Makes short-form vertical video — plan (VideoArchitecture), voiceover, footage, render 9:16 (ffmpeg floating-text by default, Remotion optional), optional looks/music, then post and log. Use when the user says "make a video", "run the video engine", "turn this into a Reel/TikTok/Short", or asks for short-form video content.
---

# engine-video

Script to rendered 9:16 mp4. The heaviest engine in the repo — it needs disk, keys and patience — so don't pick it as a first engine unless video is genuinely the channel.

This skill runs any engine folder of **type `video`**. The default folder is
`video/`; paths below (`templates/`, `runs/`, `inputs/`) are inside it, while
brand, accounts, keys and **reusable footage/fonts/logos live in `shared/`**
(`shared/assets/` — any engine can use them).

**Several video engines are the normal shape, one per format**, each with its
own templates, experiments and metric. Name them after the format they run:

| Folder | Format |
|---|---|
| `video-app/` | viral product |
| `video-vibe/` | viral vibe |
| `video-info/` | informative |

All of them are type `video` — scaffold one with
`--merge --engine video-vibe:video`, or copy a folder and empty its `runs/`
and `reports/` (history belongs to the original). Running a single format? Keep
the shipped `video/` folder and ignore the rest. Render knobs (`resolution`,
`target_seconds`, voice id) live in each folder's `engine.json` under `video`,
so two video engines can render differently.

**Paths in this file:** `shared/…` means the gtm home (`~/gtm` by default, or
`$GTM_HOME`); `templates/`, `inputs/`, `runs/` and `reports/` mean the engine
folder you're running, wherever it lives. The scripts resolve both through
`~/gtm/engines.json`, so read them as names rather than literal paths.

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
own engine folder. `references/formats.md` covers how.

Running two formats means **two engine folders** (`video-app/` and
`video-vibe/`), not one folder with two kinds of run: different metrics,
different experiments, different queues.

**How (not just what):** the run below is the spine. The recipes live in `references/` — read the one for the step you're on instead of improvising ffmpeg or shot lists.

| Step | Reference |
|---|---|
| Which format, and its rules | `references/formats.md` |
| Shot list / segments | `references/structure-plan.md` |
| Hook and overlay copy — what the text says | `references/hook-guide.md` |
| Voiceover | `references/voiceover.md` |
| Where clips come from (and the rights call) | `references/clip-sourcing.md` |
| Footage / Pexels | `references/footage-pexels.md` |
| Default render (text over B-roll) | `references/floating-text.md` |
| Locked text style (font, size, position) | `references/ffmpeg-text-style.md` |
| Never shipping the same video twice | `references/duplicate-safety.md` |
| ffmpeg commands | `references/ffmpeg-recipes.md` |
| Optional looks | `references/looks.md` |
| Music beds — **offer one every run**, levels, rights, downloading | `references/music.md` |
| Remotion path | `references/remotion.md` |
| Posting how-to | `references/posting-api.md` |
| Manual vs Upload Post vs Buffer | `references/posting-options.md` |

## What it needs

| Thing | Why | Free? |
|---|---|---|
| `ffmpeg` | rendering | yes — `brew install ffmpeg` |
| the overlay font, **installed** | text resolves by name, no `fontsdir` — `cp assets/fonts/*.ttf ~/Library/Fonts/`, once per machine (`references/ffmpeg-text-style.md`) | yes — bundled, OFL |
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
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --engine video
```

The hook is the variable worth testing — question versus claim, face versus text, first-second payoff versus slow build. Everything else is noise by comparison, and it converges fastest. If it returns `write_template`, write that template from the hypothesis. How to actually write one: `references/hook-guide.md`.

**On a fresh engine this returns `use_template` and that's correct** — the
starter experiments ship paused on purpose. Ship one video until the user is
happy with the format, then start testing. `engine-loop/references/ab-testing.md`
→ R0 has the three conditions for flipping an experiment live.

Testing a whole **format** against a working one is the slow test; hooks get to a first winner faster. Worth doing once this engine is solid and the hook loop has stopped teaching you anything. `references/advanced.md` → *A/B testing whole formats*.

### 2. Plan the structure

Pick the format first (`references/formats.md`), then copy the matching
`examples/*.json` and fill in its placeholders. Write the result to
`runs/<run_id>/inputs.json` — segments and durations per
`references/structure-plan.md`. That file is the shot list **and the config** —
the dedupe fingerprints are derived from it — so don't invent new scenes
mid-render without updating it.

Then check you're not about to remake something this engine already made:

```bash
python3 ~/.agents/skills/engine-video/scripts/combo_check.py check \
  --engine video --inputs runs/<run_id>/inputs.json
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

**On-screen text is a separate craft from the VO** — written for the eye, muted,
at speed. Its rules (hook formats, word counts, lowercase, punctuation,
localization) are in `references/hook-guide.md`; the copy goes on
`inputs.json` → `segments[].textOverlay.lines`.

### 4. Voiceover

Follow `references/voiceover.md`. ElevenLabs by default, voice id in
this engine's `engine.json` — or whatever TTS the user already uses. Same voice across
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

### 5b. Music — offer it, every time, before the render

**Ask, don't wait to be asked.** In the two no-voice formats the bed *is* the
video's energy, and a user who has never been offered one assumes they have to
find the file themselves. Put it as one question with real options rather than
"do you want music?", which gets "I don't know":

> I'll add a bed under this one. Want to name a track or an artist, or shall I
> suggest something? For this clip I'd go **calm lo-fi / ambient piano** — it
> suits the slow footage. Other directions that work: **driving electronic** for
> product demos, **warm acoustic** for founder-voice pieces, **cinematic build**
> for a reveal at the end.

Suggest by **mood first, artist second** — a mood they can react to instantly,
and two or three named artists in that mood only if they want a specific sound.
Take whatever they name, in whatever form: a title, an artist, a YouTube link, a
vibe, or a file they already own.

**Fetching it** — when they name a track or paste a URL they have the rights to
reuse, download it with `yt-dlp` into `shared/assets/music/` so every engine
can use it:

```bash
mkdir -p shared/assets/music && yt-dlp -x --audio-format mp3 --audio-quality 0 --no-warnings -o "shared/assets/music/%(title)s.%(ext)s" "URL"
```

If `benyki/skills/youtube-song-download` is installed, use it instead — it takes
a song name and artist rather than a URL, picks a video inside a sane duration
window (so you get the track, not a two-hour mix or a 20-second teaser), and
writes a tagged MP3. Point its output at `shared/assets/music/`.
`benyki/skills/music-downloader` is the broader version;
[`docs/additional-skills.md`](../../docs/additional-skills.md) has the install.

**The rights line has to be said, once, plainly** — and it isn't a reason to
skip the step: a track being downloadable is not a licence for a commercial
channel. Their own upload, a bought track, or a royalty-free library (Pexels,
Pixabay, YouTube Audio Library) is clear. A trending platform sound is not —
using it *inside* the platform's own editor is a different thing from shipping
it in a rendered file. State which of the three covers the file, note it with
the run, and **if the answer is unclear, ship voice-only or a royalty-free bed**
rather than guessing on the user's behalf.

**Level is set by the format, not by taste:** 0.5 with no voiceover, 0.03 under
one. Nothing in between. Mechanics, the mix and the trim/fade:
`references/music.md`; reference the file from `inputs.json` →
`musicBackground.file`.

### 6. Render

Defaults: 9:16 at 1080×1920 (this engine's `engine.json` → `video.resolution` /
`target_seconds`), H.264, audio at −14 LUFS, captions burned in.

**Default path:** floating text over B-roll — `references/floating-text.md` +
home starter `templates/floating-text-default.json` (in the engine folder) +
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
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --engine video --channel tiktok \
  --experiment exp-004 --arm tension --template script-tension.txt
```

Two records, two jobs: the run row says a video was made and what it earned;
`runs/<run_id>/inputs.json` says what it was made of, which is what makes the
next `combo_check` mean anything. Keep the config with the run — it's the only
memory this engine has of what has already been built.

**When a video has to get specific things right, write a checker.** Some formats
carry a factual payload — exact words, numbers, prices, names, a claim that has
to match a source — and the mistakes are always the same handful. When that's
true, a twenty-line script that reads the run's `inputs.json` and exits non-zero
beats a checklist in a prompt: it runs the same way every time, it can't be
skipped when the batch is late, and **it blocks the post rather than reporting
after the fact**. Give it the failure path too — skip that clip, move it aside,
take the next one — or an unattended job stalls on the first bad file. Optional,
and only worth it for a format you're producing repeatedly.

### The caption

Separate craft from the on-screen text, and easy to forget because the video
feels finished without it. It matters most in the formats where the product
never appears on screen — then the caption is the *only* place attribution
happens.

Keep the engine's captions in one file, `<engine>/templates/captions.md`,
grouped by which kind of video each one fits. Four rules:

- **Short, and written like a person, not an ad.** If the product belongs in it,
  one first-person mention — "the app I use for this is X" — never "Download now,
  link in bio". A caption that reads as promo gets treated as promo
- **Not the first line.** The first line is what shows before *"…more"*. Lead with
  the hook or the context; the mention goes in the middle or at the end
- **Rotate.** Keep three or four phrasings and cycle them. The identical sentence
  on two hundred posts is a pattern, to the platform and to a returning viewer
- **Match the caption to what's actually on screen.** A caption written for a
  different kind of clip is worse than a generic one — it signals nobody watched
  the video before posting it

Start with two or three per video type and don't agonise over them. **Then tell
the user the thing that actually improves this file:**

> *"Paste me your best-performing captions — yours or ones you've saved from
> accounts you like — and I'll rewrite `captions.md` around what actually
> works for you."*

Written captions are guesses until real ones replace them. Same principle as
`inputs/best/` for post voice: copied from examples, never from a description.

Posting mode: manual, Upload Post, or Buffer —
`references/posting-options.md` (decision) and `references/posting-api.md` (how).
Device posting: `references/advanced.md` (account-risk first). Record the URL:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish --run <run_id> --url https://...
```

Then move the mp4 to the home archive so you can find it later and delete it
easily — `<published_dir>/<run_id>-<slug>.mp4`, which defaults to
`published/<engine>/` and is set per engine in `engine.json`. Leave
`runs/<run_id>/inputs.json` where it is; that one is never disposable.
`published/README.md`.

### How often to post

There's no script for this and there shouldn't be, but it's the rule that
protects the account:

- **Four or five posts a day per account is the ceiling**, and most accounts do
  better well under it. Space them out — several hours apart, not a batch at
  09:00 — and vary the theme and the hook between them
- A burst reads as automation to the platform and to the audience, and the
  penalty is silent: reach drops, and you read it as "the format stopped working"
- **Three good posts a week beats twenty in a day**, every time
- If a scheduler is queueing posts, set the spacing *in the queue* rather than
  trusting the render pace. One video every 12 hours is a safe floor for a new
  account

Same rule per *account*, not per engine — two engines feeding one TikTok
handle share that ceiling.

## Getting the numbers back

Two routes, and which one you have decides what this engine's metric can be.

**With the browser extension** — the creator dashboard, where watch-through
lives:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py metric --run <run_id> --value 12400 --source browser
```

**Without it** — `yt-dlp` reads the public counters off your own posted URL, no
login and no extension. Verified on YouTube and TikTok: views, likes, comments
(and reposts on TikTok):

```bash
yt-dlp -J --no-warnings "<the url you recorded on publish>" | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['view_count'])"
# then: runlog.py metric --run <run_id> --value <views> --source yt-dlp
```

**What yt-dlp cannot give you on any platform is watch-through** — average view
duration, retention, impressions and traffic source exist only behind the
account login. So if there's no extension, set this engine's `primary_metric`
to `views` rather than leaving a `watch_through_rate` column that never fills.
Say that out loud to the user; a weak measured signal beats an empty one, and
the loop works identically either way. (YouTube-only exception: its Analytics
API returns real average view duration for your own channel over OAuth.)

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
- **Never exceed four or five posts a day on one account**, and space them out
- Delete the intermediate files after a successful render. Video fills a disk faster than anyone expects — but **never delete `runs/<run_id>/inputs.json`**. It's two kilobytes and it's the only record of what this engine has already made. Shipped mp4s live in this engine's `published_dir` and *are* safe to delete
- If a render fails, fix it — don't ship a broken or half-length file

A hook verdict here usually says something about the social engine's hooks
too — when a finding generalises, add a line to `shared/insights.md`, and put
reusable clips or end-cards in `shared/assets/` so siblings don't re-make them.

## Make it run without you

Rendering stays manual — it's slow, disk-hungry, and the step where a human eye
is cheapest. What's worth scheduling is everything around it:

| Label | When | What |
|---|---|---|
| `engine-metrics-video` | daily | record what each published video earned. Daily because the 72h window clears on a rolling basis |
| `engine-video-app-hooks` | weekly | read what earned watch-through, rewrite the hook library from it |
| `engine-video-info-source` | daily | pull new items from the text source into `inputs/source-texts/` — only when the informative engine *fetches* its source rather than being handed one |
| `engine-cleanup` | monthly | delete artifacts older than 30 days from wherever this engine publishes and report what was reclaimed. Optional, and ask first — some people want the year of videos on disk |

Neither of the first two renders and neither uploads — rendering stays manual,
and so does posting. Without the metric job this engine accumulates videos and no
verdicts, which is the most common way a video channel goes quiet. Catalogue:
[`docs/scheduling.md`](../../docs/scheduling.md); how to create one:
`engine-loop/references/scheduling.md`.

## Going further

- `references/advanced.md` — dedicated phone + mobilerun (read account-risk first)
- Deeper tool skills (optional install): `benyki/skills` — `ffmpeg`, `elevenlabs`,
  `video-floating-text`, `video-filter`, `upload-post`, `remotion-best-practices`,
  `music-downloader`, `pexel-video-downloader` — see `docs/additional-skills.md`
