# Structure plan — concept → VideoArchitecture

Write this JSON to `runs/<run_id>/inputs.json` **before** voiceover or render.

It is the shot list *and* the config — one small file per video, and the only
record of what that video was made of. Everything downstream reads it: the
render, the dedupe fingerprints (`references/duplicate-safety.md`), and the next
agent wondering whether this has been made before. Do not improvise segments
after writing it without updating it, and do not delete it when cleaning up a
run.

## Checklist

1. Infer concept (from a sentence, or from a reference URL's caption/topic)
2. Pick platform + duration (default: TikTok, 9:16, 30s)
3. Pick a **segment pattern** below
4. Fill `VideoArchitecture` JSON
5. Confirm with the user if the hook or CTA is ambiguous
6. Only then: voiceover → footage → render

## Segment patterns (pick one)

| Pattern | Best for | Shape |
|---|---|---|
| **HIC** | One insight, 15–30s | hook → insight → cta |
| **PASC** | Product / problem, 30–60s | hook → problem → agitate → solve → cta |
| **Reveal** | Before/after, story | tease → setup → journey → reveal → cta |
| **List** | N tips/facts | hook → item×N → cta |
| **Reaction** | Commentary | hook → context → reaction → verdict → cta |

Rules of thumb:
- Hook segment ≤ 5s and must carry the payoff or the tension
- One idea per video; lists still serve one promise ("3 mistakes…")
- Scale segment durations so they sum to `meta.targetDuration`

## Schema

```json
{
  "meta": {
    "title": "founder-burnout-30s",
    "concept": "Burned-out founders need one system, not another app.",
    "sourceUrl": null,
    "targetDuration": 30,
    "aspectRatio": "9:16",
    "platform": "tiktok"
  },
  "voiceOverlay": {
    "fullScript": "…",
    "voiceId": "",
    "autoCaption": true
  },
  "musicBackground": {
    "mood": "tense",
    "genre": "cinematic",
    "volume": 0.03,
    "file": null
  },
  "segments": [
    {
      "position": 0,
      "duration": 4,
      "role": "hook",
      "backgroundFootage": {
        "query": "tired founder laptop night",
        "source": "assets|pexels",
        "file": null
      },
      "textOverlay": {
        "role": "hook",
        "lines": ["You're not lazy.", "You're drowning in tools."]
      },
      "voiceScript": "You're not lazy. You're drowning in tools."
    }
  ]
}
```

### Field notes

- `voiceOverlay.voiceId` — copy from this workflow's `workflow.json` → `video.elevenlabs_voice_id`. Same id every arm.
- `musicBackground.volume` — **0.03 under a voiceover, 0.5 when there's no voice**
  (`references/formats.md`). The bed either carries the video or stays out of the
  voice's way; the middle ground just makes both harder to hear once the platform
  normalises loudness
- `backgroundFootage.source` — prefer `assets` (`shared/assets/`); `pexels` is fallback
- Speaking rate estimate: ~14 characters/second; `len(fullScript) / 14 ≤ targetDuration`
- Omit `voiceOverlay` for silent / music-only concepts

## After the plan

- Voiceover: `references/voiceover.md`
- Footage: `references/footage-pexels.md` + `shared/assets/`
- Default render path: floating text (`references/floating-text.md`) or Remotion (`references/remotion.md`)
- ffmpeg assembly: `references/ffmpeg-recipes.md`
