# <workflow name>

<One or two lines: what this workflow makes, for which product, on which
channel. Example: 16-second app demos for TikTok, three a week.>

**The number:** <installs or signups a week from these videos, or average views>

## Run it

Ask your agent: "Run the `<workflow name>` workflow with the gtm-video skill."

## Defaults

- **Format:** <viral product | viral vibe | informative | your own>
- **Canvas:** 1080x1920 (9:16). Use 1920x1080 for a landscape YouTube plan
- **Length:** about <16> seconds
- **Voice:** <ElevenLabs voice id, or "none">
- **Footage:** own clips and screen recordings first (`assets/`), Pexels as
  the fallback so a video always finishes
- **Posting:** <manual | Upload Post | Buffer>, never without an explicit yes

## Schedule

Manual.

<!-- Or, when it runs on a schedule:
- When: <every Monday at 09:00>
- Where: <the project's scheduler, e.g. a Claude Code routine, cron, CI>
- Prompt: "<the exact prompt the task runs>"
-->

## Files

| Path | What | In git |
|---|---|---|
| `README.md` | this page | yes |
| `log.csv` | one row per posted video | yes |
| `brand.md` | voice notes, only if the project has none elsewhere | yes |
| `templates/` | starter script, floating-text layout, `captions.md` | yes |
| `runs/<run_id>/inputs.json` | each video's config; the duplicate check reads it | yes |
| `runs/<run_id>/output/` | renders, voiceover, clips | no |
| `assets/` | footage, music and fonts this workflow reuses | media no, fonts yes |

## Keys

Set in the project's own env, by name: `PEXELS_API_KEY` (footage),
`ELEVENLABS_API_KEY` (voiceover), `UPLOADPOST_API_KEY` (posting, optional),
`FAL_KEY` (generated clips, optional). Delete the ones this workflow doesn't use.

## What we learned

<!-- One line each time something clearly won or lost, with the date of its
log.csv row. Example: 2026-11-10: question hooks doubled views over claims. -->
