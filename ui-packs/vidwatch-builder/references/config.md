# The Config Contract

Do not hardcode machine paths in `app/main/services/registry.ts`. Put everything
machine-specific in one config file and make `registry.ts` read it so the code
stays portable.

## Location

Resolution order (first hit wins):

1. `VIDWATCH_CONFIG` env var (absolute path)
2. `<userData>/vidwatch.config.json` (Electron's per-app data dir — survives repo moves)
3. `<repo>/vidwatch.config.json` (checked in or gitignored, user's choice)

`userData` is `~/Library/Application Support/<name>` on macOS, `%APPDATA%/<name>` on
Windows, `~/.config/<name>` on Linux. Electron gives it to you: `app.getPath("userData")`.

## Schema

Every field except `videosRoot` has a default. A minimal config is one line.

```jsonc
{
  // ── Layer 1: where videos live ──────────────────────────────────────────
  "videosRoot": "/path/to/your/videos",      // REQUIRED. ~ expands. The walk root.
  "publishedMarker": "published",            // folder name that flags "finished clips
                                             // live here". null = every .mp4 under
                                             // videosRoot (then set walkDepth sanely).
  "walkDepth": 4,                            // max directory depth when discovering
  "videoExtensions": [".mp4"],               // what counts as a clip (.mov, .webm …)

  // ── Layer 2: metadata resolution (see inputs.md) ────────────────────────
  "metadataLocations": [                     // relative to the mp4's dir; {stem} =
    "{stem}.json",                           // filename without extension. Tried in
    "../{stem}.json",                        // order; first parse win. Also each is
    "../configs/{stem}.json",                // retried with the timestamp-stripped
    "../../configs/{stem}.json",             // stem (see inputs.md § stems).
    "../../inputs/{stem}.json"
  ],
  "wordShapes": "default",                   // named extractor set, or add your own
                                             // dialect in scanner.ts (inputs.md § 4)

  // ── Layer 3: ledger (optional) ──────────────────────────────────────────
  "ledger": {
    "path": "/path/to/your/posts.jsonl",     // null → layer 3 off, mtime fallback
    "format": "jsonl",                       // jsonl | json-array | csv
    "fields": {                              // map YOUR ledger's field names onto
      "file": "file_archived",               // vidwatch's canonical ones. Only "file"
      "postedAt": "posted_at",               // (or a stem-bearing field) is required
      "account": "account",                  // for the join to work at all.
      "url": "post_url",
      "status": "status",
      "pipeline": "pipeline",
      "tag": "tag"
    }
  },

  // ── Layer 4: per-platform status files (optional) ───────────────────────
  "platformStatus": {
    "file": "platform-status.json",          // looked up next to the mp4's folder;
    "platforms": ["tiktok", "youtube",       // null file → layer 4 off
                  "instagram", "x", "bluesky", "facebook", "threads"]
  },

  // ── Layer 5: metrics (optional; see platforms.md) ───────────────────────
  "metrics": {
    "providers": ["tiktok-oembed"],          // which liveness/metrics providers run
    "statsTtlHours": 12,                     // live posts re-checked after this
    "unknownTtlDays": 7,                     // "unknown" retried after this
    "concurrency": 6
  },

  // ── Layer 6: thumbnails (optional) ──────────────────────────────────────
  "thumbnails": {
    "ffmpeg": null,                          // null → auto-detect (see below)
    "defaultSeekSeconds": 1.2,               // past any intro fade
    "width": 360
  },

  // ── Named sources (optional, overrides discovery) ───────────────────────
  // Discovery finds folders; this decorates or replaces them. Anything found on
  // disk but not listed here still appears, labeled "unlinked".
  "sources": [
    {
      "id": "series-a",
      "publishedRel": "series-a/published",  // relative to videosRoot
      "label": "Series A",
      "format": "default",
      "language": "English",
      "account": "your-account",             // fallback when ledger has no account
      "pipeline": "upload-post"
    }
  ]
}
```

## Rules for the implementation

- **Expand `~`** in every path field: `p.replace(/^~(?=$|\/)/, os.homedir())`.
- **Validate on startup, warn, never crash.** A bad config field falls back to its
  default and logs once. The app must always reach the window.
- **`sources[]` overrides discovery by `publishedRel` match**; discovery still runs
  and appends anything unlisted as `unlinked:<relpath>` (pipeline `"unknown"`). This
  is what makes the app useful on day one of a new format — no config edit needed to
  *see* new clips, only to *label* them.
- **ffmpeg auto-detect**: try config value, then `/opt/homebrew/bin/ffmpeg`,
  `/usr/local/bin/ffmpeg`, `/usr/bin/ffmpeg`, `ffmpeg` on PATH (Windows: also
  `ffmpeg.exe`, `C:\ffmpeg\bin\ffmpeg.exe`). Missing ffmpeg = no thumbs, app still runs.
- Cache the parsed config for the process lifetime; a restart picks up edits.

## Worked examples

### A. Ledger + published marker

```json
{
  "videosRoot": "/path/to/your/videos",
  "ledger": { "path": "/path/to/your/posts.jsonl", "format": "jsonl" }
}
```
Everything else can stay at defaults until you need named sources or extra platforms.

### B. Flat folder, no pipeline, no ledger

A user with `~/Videos/exports/*.mp4` and nothing else:

```json
{
  "videosRoot": "~/Videos/exports",
  "publishedMarker": null,
  "walkDepth": 1,
  "ledger": { "path": null },
  "platformStatus": { "file": null },
  "metrics": { "providers": [] }
}
```
Layers 3–5 off. Cards show file, mtime date, thumbnail. Still useful.

### C. CSV ledger, YouTube-first, Windows

```json
{
  "videosRoot": "C:/render/output",
  "publishedMarker": "done",
  "videoExtensions": [".mp4", ".mov"],
  "ledger": {
    "path": "C:/render/posted.csv",
    "format": "csv",
    "fields": { "file": "filename", "postedAt": "date", "url": "link", "account": "channel" }
  },
  "platformStatus": { "platforms": ["youtube"] },
  "metrics": { "providers": ["youtube-oembed"] },
  "thumbnails": { "ffmpeg": "C:/ffmpeg/bin/ffmpeg.exe" }
}
```

### D. Multiple roots

The schema has one root by design (one walk, one relative-path namespace). For
genuinely disjoint roots, prefer symlinking them under one umbrella folder and
pointing `videosRoot` at that. Only add a `videosRoots[]` array to the code if
symlinks are impossible (e.g. Windows without developer mode) — then every
`slice(VIDEOS_ROOT.length)` in scanner.ts must become root-aware, which is the only
invasive part.

## What must NOT go in the config

- Anything derived (counts, caches, scan results) — those live in `userData` as
  separate cache files (`availability.json`, `thumbs/`, `projects.json`).
- Secrets. vidwatch's built-in providers use public endpoints; if a user adds an
  authenticated provider, its key goes in the environment, never this file.
