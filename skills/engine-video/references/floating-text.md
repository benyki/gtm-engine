# Floating text — 9:16 text over B-roll

The default Remotion-free render path: centered typography over a background clip.
Use when the arm is text-led (hook on screen) or you need a reliable first ship.

Starter template in the workflow folder: `templates/floating-text-default.json`
(copied by scaffold). Write each video's resolved config to
`runs/<run_id>/inputs.json`.

## Recipe (one video)

1. Have an `inputs.json` (`references/structure-plan.md`) or a short hook + body lines
2. Pick one background clip — `shared/assets/` first, else Pexels
3. Crop/scale to 1080×1920 (`references/ffmpeg-recipes.md`)
4. Burn text with libass / `subtitles=` (not free-float drawtext unless you must) —
   the exact type is `references/ffmpeg-text-style.md`, and `scripts/text_style.py`
   emits the ASS block so no font path or family is ever hardcoded
5. Mix voiceover at full level; bed music at 0.03 under it, or 0.5 when there's
   no voice (`references/music.md`)
6. Loudnorm to −14 LUFS; write `runs/<run_id>/output/final.mp4`

## Template JSON (shape)

```jsonc
{
  "description": "Default floating-text look",
  "duration_s": 15,
  "output": {
    "dir": "runs/<run_id>/output",
    "filename_pattern": "final.mp4"
  },
  "background": {
    "paths": ["shared/assets"],
    "extensions": [".mp4", ".mov", ".m4v"],
    "random": true
  },
  "crop": { "w": 1080, "h": 1920, "mode": "center-zoom-fill" },
  "layout": "stacked-center",
  "elements": [
    {
      "name": "hook",
      "source": "literal",
      "value": "Your hook goes here",
      "font": "Helvetica Neue",
      "size": 72,
      "weight": "bold",
      "align": "center"
    },
    {
      "name": "detail",
      "source": "literal",
      "value": "One supporting line.",
      "font": "Helvetica Neue",
      "size": 48,
      "align": "center"
    }
  ]
}
```

## Layout rules

- Max 1–3 on-screen text blocks; if it needs four, the script is wrong
- Hook in the first 1.5s of *screen time*, not after a fade
- High-contrast text; outline or solid box if the B-roll is busy
  (`references/looks.md` → solid-box captions)
- Prefer landscape B-roll center-cropped to 9:16 over letterboxing

## Batch / factory mode

When the user wants many clips from one look (same geometry, new lines each time):

- Keep one template JSON; vary only the `elements[].value` (or a data file of hooks)
- Track used backgrounds in `runs/` or a small registry so the same clip isn't reused every time
- Still one `runlog` row per published video — batches are production, not one A/B unit

Full engines live in optional skills (`video-floating-text`, `video-factory-floating-text-short`
on `benyki/skills`). This reference is enough to render without installing them.
