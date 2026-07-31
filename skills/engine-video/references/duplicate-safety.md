# Duplicate safety — never ship the same video twice

A video workflow at volume is a factory: one look, one template, many configs.
The failure mode is producing two videos that are the same video, and the
punishment isn't a warning — TikTok, Reels and Shorts quietly bury the second
one. You see it as a run that mysteriously got no distribution, and you learn
nothing from it because the arm looks like it lost.

Two rules, in order. The first stops you *making* duplicates; the second lets
you deliberately re-ship something that already won.

---

## Rule 1 — never reuse the same inputs *and* the same durations

| Inputs | Durations | Verdict |
|---|---|---|
| same | same | **duplicate** — don't render it |
| same | different | fine — re-timing is a real edit |
| different | same | fine — same rhythm, new material |
| different | different | fine |

Same footage cut to a different rhythm is a different video. So is the same
rhythm carrying different footage. Both at once is a repost with extra steps.

**Inputs** = every media file the config references (background clips, hook
clip, music) **plus the on-screen text**. Copy counts as an input on purpose:
two A/B arms testing different hooks over identical footage are genuinely
different videos, and the rule must not block the experiment it exists to
protect.

**Durations** = the ordered list of segment durations, rounded to 0.1s.

### One config per video, and that's the record

`runs/<run_id>/inputs.json` is the config: the segments, the media refs, the
durations, the overlay lines. It's written before the render
(`references/structure-plan.md`), it's what actually got made, and it's a couple
of kilobytes.

That file is the whole memory. There is no ledger, no index, no second copy to
keep in sync — the fingerprints are **derived** from the configs every time they
are needed, so they can't disagree with what shipped. Writing `inputs.json` *is*
the logging step; if it exists, this workflow remembers the video.

Queued configs in `inputs/queue/` have the same shape and count the same way, so
two queued configs that collide with each other are caught before either one is
rendered.

**`inputs.json` is not an intermediate.** Delete the renders, the scratch files
and the source clips when disk gets tight — never the configs. A combination you
can no longer see is one you'll re-make.

### Checking it

Don't eyeball this across ten queued configs — the point is that it's
mechanical:

```bash
# before you render
python3 ~/.agents/skills/engine-video/scripts/combo_check.py check \
  --workflow video --inputs runs/<run_id>/inputs.json
```

Exit 1 with a named collision means change one side and re-check.

```bash
# what this workflow has already made, with both fingerprints
python3 …/combo_check.py list --workflow video

# fingerprints for one config, no workspace needed
python3 …/combo_check.py fp --inputs <config.json>
```

`combo_check.py` and `runlog.py` answer different questions and you want both:
`runlog.py` records *that* a video was made and what it earned, `inputs.json`
records *what it was made of*.

---

## Rule 2 — re-shipping a winner: change ≥75% of the frames

Sometimes you *want* to post the same thing again: it won, the audience turned
over, a different platform never saw it. That's legitimate, and it still gets
collapsed if you upload the same file.

Platform duplicate detection works on perceptual hashes, and single-axis
changes stopped being enough years ago — a flip, a crop, or one filter leaves
you well inside the ~80–85% similarity band that gets a re-upload buried. What
works is **stacking three to five small per-pixel changes** so the combined
hash drifts past the cutoff while each individual change stays invisible: a
slight zoom, a degree of rotation, a gamma nudge, light grain, a
downscale-upscale cycle, a speed wobble, fresh metadata.

Target **≥75% of the frame changed** by that combination — measure it, don't
estimate it.

`benyki/skills/video-duplicate-transformer` ships that stack with tuned presets
(1, 5 or 15 variations from one source) and is the shortest path here; install
it per [`docs/additional-skills.md`](../../../docs/additional-skills.md). The
manual version is `references/looks.md` — stack `soft-downup` + `grain` +
`punch-zoom` rather than reaching for one filter.

Two things this does **not** license:

- Re-shipping someone else's video. The rights question is unchanged and lives
  in `references/clip-sourcing.md`
- Padding a channel with fifteen versions of one idea. The transformer solves
  a distribution problem, not an ideas problem — if every week is variations of
  the same winner, the queue is the thing that's broken

---

## In the A/B loop

Log the variation as its own run with its own row. A re-shipped winner is a new
run, not an amendment to the old one — it has its own metric, and comparing the
two tells you whether the audience had actually turned over.

Where a duplicate slipped out anyway, say so in the run's note. An unexplained
zero in `index.csv` poisons an arm's mean for months, and "this one was buried
as a duplicate" is the difference between a bad hook and a bad upload.
