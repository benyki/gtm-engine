# Images — pick one, and optionally edit it

Both steps are **optional**. A post with no image ships. A post with a bad
image ships worse than one with none, and a post with a *generated* image that
implies something the user hasn't built is the one that costs them.

Two separate things, and they fail differently:

| Step | Input | Who decides |
|---|---|---|
| **Pick** | what's already in `inputs/images/` | the agent proposes, the user keeps the veto |
| **Edit** | one of those images + an image API | the user says yes before a paid call, and again before it ships |

---

## Where images live

```
<engine>/inputs/images/            what the user dropped in — never modified
<engine>/inputs/images/README.md   what belongs here
<engine>/runs/<run_id>/output/     every edit lands here, next to the post
```

`inputs/images/` is the human's folder. Screenshots, product shots, photos from
a talk, charts they exported, the logo. **Read it, never write to it** — an
edited file that lands back in `inputs/` becomes the source for the next edit,
and three posts later nobody can tell what the original looked like.

Reusable across engines (a logo, a house background, a proof screenshot the
whole brand uses) → `shared/assets/`. This engine's own material stays here.

If the folder is empty, say so once and move on. Don't invent an image to fill
a gap; short-form text posts do fine without one, and on LinkedIn a
text-only post is not obviously worse.

---

## Step A — picking

Do this after the drafts exist, not before. The post decides the image; an
image looking for a post is how a batch ends up generic.

1. **List what's there.** Read the filenames first, then look at the
   candidates — you can read image files directly. A filename is a claim, not
   a fact: `dashboard-final-2.png` is regularly not the dashboard
2. **Match it to one post.** One image, one post. If the same image fits three
   drafts, it's decorative — that's a signal the picture isn't earning its slot
3. **Check what's in the frame** before proposing it. Real customer names,
   real revenue, an inbox, a browser tab bar, a Slack sidebar, a face that
   isn't the user's. Any of those and it needs a crop or a different image —
   flag it, don't quietly ship it
4. **Say why** when you show the batch: which post, which file, one line on
   what it adds. The user vetoes fast when the reason is visible

Formats that actually work, in order: something they made (a screenshot of the
thing, a chart from their own numbers, a photo of the real place), then a
plain-text-on-background card, then stock. Stock is close to no image.

**Copy the picked file into the run** so the post is reproducible later:

```bash
cp inputs/images/dashboard.png runs/<run_id>/output/
```

Note the filename in the run's `notes.md`, or pass it at log time:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --engine social \
  --channel linkedin --notes "image: dashboard.png (picked, unedited)"
```

---

## Step B — editing an image with an AI API

For **crops, background swaps, aspect-ratio variants, cleanups, and image A/B
arms** on an asset the user already owns. It starts from *their* image; it is
not a way to conjure an image they don't have.

Ask before the first call in a run. It costs money per image, and the answer is
often "just use it as it is."

### Getting a key

Either provider works. Pick one; there's no reason to hold both.

| | Console | Key page | Notes |
|---|---|---|---|
| **Google — Gemini image models** ("nano banana") | [aistudio.google.com](https://aistudio.google.com) | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Sign in with a Google account → **Create API key** → pick or create a project. Has a free tier; docs: [ai.google.dev/gemini-api/docs/image-generation](https://ai.google.dev/gemini-api/docs/image-generation) |
| **OpenAI — GPT Image** | [platform.openai.com](https://platform.openai.com) | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | **Create new secret key** — shown once, copy it then. Prepaid credits, no free tier, and image edits may need org verification. Docs: [developers.openai.com](https://developers.openai.com/api/docs/guides/image-generation) |

Then, in the home:

```bash
cp shared/.env.example shared/.env      # if it isn't there yet
```

and paste the key in as `GEMINI_API_KEY=` or `OPENAI_API_KEY=`. The user pastes
it themselves — never into a chat window, never dictated to the agent. `.env`
is gitignored; the agent reads `.env.example` for the *names* and the scripts
read the values without printing them.

### The command

```bash
python3 ~/.agents/skills/engine-social/scripts/edit_image.py \
  --image inputs/images/dashboard.png \
  --prompt "Place this screenshot on a flat warm-grey background with even margins. Change nothing inside the screenshot." \
  --out runs/<run_id>/output/post-1.png
```

Two variants for an image A/B arm, square for LinkedIn:

```bash
python3 ~/.agents/skills/engine-social/scripts/edit_image.py \
  --image inputs/images/dashboard.png --aspect 1:1 --n 2 \
  --prompt "..." --out runs/<run_id>/output/arm-a.png
#   → arm-a.png, arm-a-2.png
```

OpenAI instead:

```bash
python3 ~/.agents/skills/engine-social/scripts/edit_image.py --provider openai \
  --image inputs/images/dashboard.png --size 1024x1024 --quality high \
  --prompt "..." --out runs/<run_id>/output/post-1.png
```

Full flags in the script's docstring (`--model`, `--fidelity`, `--timeout`,
`--home`). It never writes to `inputs/`, and it exits with the key page
URL if the key is missing.

### Writing the prompt

The single biggest lever: **name what must not change.** These models happily
redraw a chart's numbers, re-letter a UI, and invent a plausible logo.

- ✅ "Extend the background to 1:1. Keep the screenshot pixel-identical, centred."
- ✅ "Remove the browser chrome and the bookmarks bar. Leave the app UI untouched."
- ❌ "Make this look more professional" — every pixel is now negotiable
- ❌ "Add a dashboard showing 40% growth" — that's a fabricated screenshot

Describe the subject, not the style, when a style reference exists: pass the
reference with a second `--image` and ask it to match the references exactly.
Verbal style adjectives fight an attached reference and lose.

### Then look at it

Open the output and read it as an image before showing the user. Every time.
Check: text still legible and still *the same words*, no invented logo, no
sixth finger, numbers unchanged, nothing cropped off that mattered. Generation
is non-deterministic — the run that worked yesterday says nothing about this
one. If it's wrong twice, use the original.

### Raw API, if you'd rather not use the script

```bash
# Gemini — payload built by a heredoc; a base64 image is far too big for argv
python3 - "$IMG" "$PROMPT" > body.json <<'PY'
import base64, json, sys
img, prompt = sys.argv[1], sys.argv[2]
print(json.dumps({"model": "gemini-3.1-flash-image", "input": [
    {"type": "text", "text": prompt},
    {"type": "image", "mime_type": "image/png",
     "data": base64.b64encode(open(img, "rb").read()).decode()}]}))
PY
curl -s -X POST https://generativelanguage.googleapis.com/v1beta/interactions \
  -H "x-goog-api-key: $GEMINI_API_KEY" -H "Content-Type: application/json" \
  -d @body.json > res.json
python3 -c "import base64,json,sys;d=json.load(open('res.json'));..."   # decode the image part
```

```bash
# OpenAI — multipart, so the file goes straight in
curl -s -X POST https://api.openai.com/v1/images/edits \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "model=gpt-image-2" -F "image=@dashboard.png" -F "prompt=$PROMPT" \
  | python3 -c "import base64,json,sys;sys.stdout.buffer.write(base64.b64decode(json.load(sys.stdin)['data'][0]['b64_json']))" > out.png
```

Both return base64, not a URL. Source the key first
(`set -a; . shared/.env; set +a`) and never read `.env` into the conversation.

If `/v1beta/interactions` 404s, the classic
`v1beta/models/<model>:generateContent` still serves the same models —
`{"contents":[{"parts":[{"inlineData":{…}},{"text":…}]}],
"generationConfig":{"responseModalities":["TEXT","IMAGE"]}}`, image at
`candidates[0].content.parts[].inlineData.data`. The script falls back to it on
its own.

---

## What never gets generated or edited

- **Anything that functions as proof.** A metrics screenshot, a revenue chart, a
  testimonial, a "we just hit X" graphic. If the number is real, screenshot the
  real thing; if it isn't, the post shouldn't claim it. This is the same rule as
  *never claim something the user hasn't done* — an image makes the claim
  louder and is what people screenshot back at you
- **A real person's face** — the user's, a customer's, an employee's — put into
  a scene that didn't happen. Cropping and colour-correcting a real photo is
  fine
- **A logo or brand mark that isn't theirs**, and their own logo redrawn (it
  comes back subtly wrong). Composite the real file instead
- **Someone else's image**, edited to look like it isn't. Same rule as copy:
  take the structure, never the asset

When a post is only strong *with* a generated illustration, that's the tell
that the underlying material is thin. Go back to `inputs/backlog.csv`.

---

## Platform specs

| | Ratio that survives the crop | Notes |
|---|---|---|
| LinkedIn | 1:1 or 4:5 | Portrait takes more feed height. ~1200×1200 / 1080×1350 |
| X | 16:9 or 1:1 | 16:9 avoids the timeline crop; the preview is what's judged |
| Bluesky | any, ≤4 images, ~1 MB each | Compress before posting |

**Alt text on every image, everywhere.** Describe what's in it, not the post's
point — a screenshot of the run log with three failed rows highlighted, not
"proof that it works". Bluesky enforces it in the API call; LinkedIn and X
hide it a click deep in the composer and it's on you to fill it in.

## Logging

The image is part of the thing that shipped, so it goes with the run:

- edited output stays in `runs/<run_id>/output/`
- the shipped file is copied to the engine's `published_dir` alongside the post
- `--notes` (or `notes.md`) records where it came from: picked as-is, edited
  with which provider and prompt, or none

That's what makes an image arm readable later: two runs, same copy, different
image, and a note saying which was which.
