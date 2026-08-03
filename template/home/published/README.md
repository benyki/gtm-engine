# published/

**Everything that actually went out, in one place.** One subfolder per engine,
created the first time that engine ships something:

```
published/
├── video/       the mp4s that were posted
├── social/      images or cards that went with a post
└── seo/         (usually empty : articles live on the site)
```

This folder is the **default**, not a requirement : see *Where it lives* below.

## Why it exists

Three reasons, in order of how often they matter:

1. **You can find your own work.** Without this, a shipped video is buried at
   `video/runs/2026-08-04-002-video/output/final.mp4` and nobody ever looks at it
   again
2. **You can delete it safely.** Video fills a disk faster than anyone expects.
   This folder is the part that's safe to empty : see below
3. **It's the "already shipped" record.** Before posting, a glance here answers
   *did this already go out?* : which is the question a filename in a queue can't
   answer once you've re-rendered something under a new timestamp

## What goes in, and what never does

**In:** the finished artifact, after it's posted, renamed so it's readable a year
later : `<run_id>-<slug>.<ext>`, e.g. `2026-08-04-002-video-coffee-ritual.mp4`.
The run_id prefix is what ties it back to `runs/index.csv`.

**Never:** `runs/<run_id>/inputs.json`. That file stays with its run forever : it
is two kilobytes and it's the only memory of what has already been made
(`engine-video/references/duplicate-safety.md`). Deleting artifacts is routine;
deleting configs means re-making combinations you can no longer see.

This folder holds *artifacts*, not state. The spine : `runs/index.csv`,
experiments, metrics : stays inside each engine folder, so nothing here is
pooled and nothing here can be lost by a cleanup.

## Where it lives is your call

The **contract** is what matters, and it's three things: a shipped artifact ends
up somewhere you can find it, its filename carries the `run_id` so it traces
back to `runs/index.csv`, and wherever it lands holds artifacts only : never
state. Any layout that satisfies that is correct.

Set `published_dir` in an engine's `engine.json`. It's per engine, so
different answers can coexist : video on an external drive, social in the
home:

| `published_dir` | Where artifacts go | Good when |
|---|---|---|
| *(empty : the default)* | `<home>/published/<engine>/` | you want one place to see everything you've shipped |
| `"video/published"` | inside that engine's own folder | you back up or move engines individually, and want each one self-contained |
| `"/Volumes/Media/clips"` · `"~/Dropbox/Team/social"` | anywhere on disk | the files are large, or an editor, client or teammate needs them without access to your home |
| `"none"` | nowhere : artifacts stay in `runs/<run_id>/output/` | low volume, or the platform is already your archive. You keep the runs and lose the "find your own work" folder |

Relative paths resolve from the home root; `~` and absolute paths work.

Two things to know before pointing it outside the home:

- **The `.gitignore` only covers `published/`.** A folder you create elsewhere
  inside the home needs its own ignore rule, or the first `git add` commits
  a video
- **Cleanup follows the artifacts.** The `find` command below and the
  `engine-cleanup` scheduled task both operate on whatever path you chose

## Cleaning it up

Emptying this folder costs you nothing but the files themselves. The runs, the
metrics, the verdicts and the configs all live elsewhere.

Substitute your own path if you moved it.

```bash
# what's actually taking the space
du -sh published/*

# delete published media older than 30 days (dry run first : drop -print, add -delete)
find published -type f \( -name '*.mp4' -o -name '*.mov' -o -name '*.png' \) -mtime +30 -print
```

Worth a scheduled task once the video engine is running weekly :
[`docs/scheduling.md`](../docs/engine/scheduling.md) → *Housekeeping*.
