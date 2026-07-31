# Text style — the locked overlay look

`references/floating-text.md` says *put text over B-roll*. This file says
**exactly what that text looks like**, so two videos made a month apart are the
same channel and an A/B on the hook copy isn't secretly an A/B on the type.

One look, one set of numbers, scaled from the video width. Don't re-derive it
per render, and don't hand-copy it either — `scripts/text_style.py` emits it.

## The contract

| | Value |
|---|---|
| Font | the family in the resolved fonts dir — **read it, don't assume it** (below) |
| Weight | an ASS `\b` override, not a separate bold family |
| Fill / outline | white `&H00FFFFFF` on black `&H00000000` |
| Border style | `1` (outline + shadow), shadow `0` |
| Vertical anchor | **33%** from the top — the text block is *centred* on that line, not started at it |
| Alignment | `\an5` (centre), `MarginL/R/V` all `0`, horizontal anchor `PlayResX / 2` |
| Wrap | `WrapStyle 2` — line breaks come from the reflow below, never from libass |
| Positioning | every dialogue line carries its own `\pos(x,y)` |

Everything sizeable derives from a **1080-wide reference**:

```
scale     = video_width / 1080
font_size = round(74  × scale)          # 74 at 1080
spacing   = round(-2.2 × scale, 2)      # letter spacing, negative on purpose
line_height    = round(font_size × 1.05)
paragraph_gap  = round(font_size × 0.5)   # only for a blank line (\n\n)
outline        = max(3, round(font_size × 0.0675))
```

At 1080×1920: font 74, spacing −2.20, line height 78, paragraph gap 37, outline
5. **Outline and line height scale off the font size, not the width** — get that
backwards and the stroke goes fat on a 720p render.

A single `\n` wraps inside the same paragraph and adds no extra gap; only a
blank line does.

### Reflow limits

Text is re-wrapped per script before any positioning:

| Script | Chars per line |
|---|---|
| Latin / default | 30 |
| RTL (Arabic, Hebrew) | 21 |
| Abugida (Devanagari, Thai) | 23 |
| CJK | 13 |

### Vertical maths

```
anchor_y     = round(height × 0.33)
center_shift = anchor_y − (last_line_offset / 2)
line_y       = round(center_shift + line_offset)
```

One line at 1080×1920 sits at `\pos(540,634)`; two lines at 595 and 673. The
block grows symmetrically around 33% instead of pushing downward.

## The font

### Where it comes from

Resolution order, first hit wins — so a user with a brand face never has to
edit this file:

1. `--fonts <dir>`
2. `$GTM_FONTS_DIR`
3. **`<workspace>/shared/assets/fonts/`** — the user's own font, if they have one
4. **`<this skill>/assets/fonts/`** — TikTok Sans 12pt (Regular + Bold), shipped
   here under the OFL so a fresh clone renders on-brand with no downloads

```bash
python3 ~/.agents/skills/engine-video/scripts/text_style.py fonts
```

It prints the resolved directory, every family the files declare, and
`use_this_family` — the name to put in the ASS. **That name comes out of the
font file, not out of a doc**, which is the point: filenames lie, and a family
you assume is a family libass will silently replace.

### Verify, every machine, every font change

libass never fails loudly on a missing font. It substitutes, the render looks
plausible, and you find out weeks later that half the channel is Helvetica:

```bash
python3 ~/.agents/skills/engine-video/scripts/text_style.py probe \
  --video runs/<run_id>/output/base.mp4 --ass runs/<run_id>/overlay.ass
```

Exit 0 means every face came from the fonts dir. Exit 1 prints `SUB` lines
naming the system font that got used instead — the family name in the ASS
doesn't match what the directory offers, so run `fonts` and use what it says.

This is not TikTok-Sans trivia you can skip for another face. Two things that
bite whatever you burn:

- **Family ≠ filename ≠ PostScript name.** Only the declared family matches
- **A weight with no matching face falls back silently.** With Regular + Bold
  shipped here, `\b400` → Regular and `\b700` → Bold, but `\b600` also lands on
  Regular. Ask for a weight you have a face for, or add the face

## Rendering it

### Emit the style, don't type it

```bash
python3 ~/.agents/skills/engine-video/scripts/text_style.py style \
  --width 1080 --height 1920 --weight 700
```

Prints the `[Script Info]` / `[V4+ Styles]` block with every number already
resolved for that resolution, plus a worked `Dialogue:` line showing the `\pos`
maths. Redirect it to the `.ass` and append your cues with `printf` or a quoted
heredoc — **not** `echo`, which eats `\a` and `\b` in the override tags and
leaves you with `{n5\q2…700}` and a silently unstyled line. Then burn:

```bash
FONTS=$(python3 ~/.agents/skills/engine-video/scripts/text_style.py fonts | \
  python3 -c 'import json,sys; print(json.load(sys.stdin)["fonts_dir"])')

ffmpeg -y -i runs/<run_id>/output/base.mp4 \
  -vf "subtitles=filename='runs/<run_id>/overlay.ass':fontsdir='$FONTS'" \
  -c:v libx264 -preset slow -crf 18 -c:a copy -movflags +faststart \
  runs/<run_id>/output/final.mp4
```

`fontsdir` is not optional — and it is not sufficient either. Probe the result.

### One hook line

Cues are ordinary ASS dialogue. For a single hook, one `Dialogue:` line at the
resolved `\pos` is the whole file. Don't reach for `drawtext`: no reflow, no
outline parity, no positioning maths.

### The optional capability skill

`ffmpeg-text-overlay` ([`docs/additional-skills.md`](../../../docs/additional-skills.md))
wraps this into an SRT→ASS→burn helper with sidecar logs, and its
`text-overlay-style.json` is where these numbers came from. Useful at volume;
not required — everything above works with ffmpeg alone.

Three things to know if you install it:

- Its default family name does **not** resolve from a directory load on a
  machine where the family isn't installed system-wide. Point its style JSON at
  the family `text_style.py fonts` reports, then probe
- Its `SKILL.md` prose disagrees with its own JSON on line height and the
  char-per-line limits. The JSON wins; this page follows the JSON
- Its bundled font smoke test looks for a fixture path from the author's
  machine and fails everywhere else. Use `probe` instead

## In the workspace

- A brand font goes in **`shared/assets/fonts/`** — every video workflow picks
  it up automatically, no config
- Overlay copy comes from the config (`references/structure-plan.md` →
  `segments[].textOverlay.lines`); this file only decides how it looks
- Deviated from the default on a run (a different anchor, a different weight)?
  Note it with the run. A style you can't reconstruct is a run you can't repeat

## A/B rule

**The style is constant across arms.** If the experiment is the hook copy and
one arm is also a different size or position, the verdict is unreadable.

When the *look* is the experiment, name the arms after it (`anchor-33` vs
`anchor-50`, `outline` vs `solid-box`), hold the copy identical, and change one
value. `references/looks.md` covers the solid-box treatment, the usual
challenger when B-roll is busy.

## Rules

- Never inline a `force_style=` string. The style lives in one place; a copy in
  a shell command is a fork that drifts
- Never hardcode a font path or family in a render script — resolve both
- Never ship a render you haven't probed after changing font, family or machine
- Change the numbers here **before** any code that mirrors them
- Non-Latin scripts get the reflow limit automatically; the font does **not**
  auto-switch. Hebrew, Arabic, Devanagari, CJK and Thai need a Noto face in the
  fonts dir and the family name to match
