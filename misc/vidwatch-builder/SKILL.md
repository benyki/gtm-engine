---
name: vidwatch-builder
description: Build a "vidwatch"-style local desktop dashboard that watches a video-posting pipeline's output folders and shows every clip with its post status, live platform metrics, and links. Use when the user wants to build vidwatch on a new machine, port it to a different filesystem layout or OS, adapt it to different metadata/input formats, add a new platform beyond TikTok, or make its hardcoded paths config-driven.
---

# vidwatch Builder

vidwatch is a local Electron app that answers one question: **"what did my automated
posting pipeline actually put out, and how is it doing?"** It walks folders of rendered
videos, joins them against a posting ledger, and renders a grid of cards with poster
frames, per-platform status, and live view/like counts.

This skill builds it on **any** machine, against **any** folder layout and **any**
metadata format. Nothing here assumes the original author's paths.

## When to Use This Skill

- "Build vidwatch on this computer" / "set up vidwatch for my project"
- "Port vidwatch to Linux/Windows" or "my videos live somewhere else"
- "My metadata looks different — make vidwatch read it"
- "Add YouTube/Instagram/Bluesky metrics to vidwatch"
- "Make vidwatch's paths configurable instead of hardcoded"
- Building any local dashboard over a render-and-post pipeline's output

## The One Idea You Must Get Right

Everything in vidwatch derives from **one join**:

```
a video file on disk   ⋈   a record of it being posted   ⋈   live platform metrics
   (the artifact)           (the ledger / status file)        (fetched on demand)
```

The app is a viewer over that join. Every feature — status dots, the leaderboard,
engagement rates, filters — is a projection of it. Get the join right and the UI is
straightforward. Get it wrong and no amount of UI work helps.

The join key is the **stem**: the mp4's filename without extension. Everything else
(metadata sidecars, ledger records, platform status) is keyed off that stem or the
mp4's absolute path.

## Build Order

Work in layers. **Each layer is independently useful and independently skippable** —
stop whenever the app is good enough for the user's needs. Do not build layer N+1
before layer N renders something real on screen.

| Layer | Gives you | Skippable? |
|---|---|---|
| 0 · Shell | Empty window, build pipeline, hot rebuild | No |
| 1 · Sources | Which folders hold finished videos | No |
| 2 · Posts | A card per video + its metadata | No |
| 3 · Ledger | Real post times, accounts, permalinks | Yes → falls back to file mtime |
| 4 · Platform status | Per-platform posted/pending badges | Yes |
| 5 · Live metrics | Views/likes, removal detection, leaderboard | Yes |
| 6 · Thumbnails | Poster frames from the video | Yes → shows a placeholder |
| 7 · Packaging | A real .app/.exe in the dock/taskbar | Yes → `npm start` works fine |

Read `references/architecture.md` for the module map and how the layers talk to each
other. **Read `references/config.md` before writing any path** — it defines the config
contract that keeps every layer machine-independent.

## Instructions

### Step 1 — Interview the user (do not skip)

You cannot configure this from assumptions. Ask, and record answers into the config
file from `references/config.md`:

1. **Where do finished videos live?** One root, or several? Absolute path.
2. **How are they organised?** Is there a marker folder (the original uses
   `published/`), or is every mp4 under the root fair game?
3. **Is there a posting ledger?** A JSONL/JSON/CSV/SQLite record of what was posted,
   when, to which account, with what URL. Path? Or none?
4. **Where does per-clip metadata live** relative to the mp4, and what shape is it?
   Get one real example file — do not guess the schema.
5. **Which platforms** matter (TikTok, YouTube, Instagram, …)?
6. **Which OS**, and do they want a packaged app or just `npm start`?

If the user has an existing vidwatch to copy from, read its `registry.ts` /
`vidwatch.config.json` and diff against the new machine instead of interviewing.

### Step 2 — Probe the filesystem before writing code

Never trust the interview alone. Run the scaffolder, which walks the real filesystem
and proposes a config from what it finds:

```bash
node ~/.agents/skills/vidwatch-builder/scripts/scaffold-config.mjs <videos-root> [--marker published] [--out vidwatch.config.json]
```

It reports candidate source folders, mp4 counts, which metadata locations actually
resolve, and detected word-pair shapes. **Its output is a proposal — review it with
the user before committing.**

### Step 3 — Build layers 0–2, then look at the screen

Scaffold the shell (`references/architecture.md` § Layer 0), wire sources and post
discovery, and run it. You must see real cards before continuing. A grid of correct
cards with no metrics is a working app; a beautiful UI over a broken join is not.

Verify with the self-check harness described in
`references/architecture.md` § Verifying without a human — it renders the app
headless and prints what actually appeared. Use it after every layer.

### Step 4 — Add layers 3–7 as the user needs them

Each has a section in `references/architecture.md`. Two rules that are easy to get
wrong and expensive to debug:

- **Never let an optional layer break a required one.** A missing ledger, an
  unparseable sidecar, a failed metrics fetch, absent ffmpeg — each must degrade to
  "unknown" and leave the grid intact. Every read in the original is wrapped in
  try/catch returning `undefined` for exactly this reason.
- **Keep the liveness verdict separate from the metrics scrape.** See
  `references/platforms.md` — conflating them is the single worst bug in this design,
  because a scraper's HTML shape changing will silently mark healthy posts as deleted.

### Step 5 — Validate against the real filesystem

```bash
node ~/.agents/skills/vidwatch-builder/scripts/doctor.mjs vidwatch.config.json
```

Checks every configured path exists, counts what will be discovered, reports how many
clips resolve metadata / ledger records, and flags the common failure modes. Run it
whenever the app looks emptier than expected — it is almost always a path, not a bug.

### Step 6 — Package only if asked

`npm start` is the fast loop (~2s). Packaging is a separate, slower step, and a
packaged app **embeds a frozen copy of the build** — it never reflects source changes
until repackaged. This surprises everyone at least once. See
`references/packaging.md` for the per-OS recipe and the one-command update script.

## Non-Negotiables

Carry these into any port. Each one exists because its absence caused a real bug.

1. **`contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`.** The
   renderer gets a narrow `window.api` surface over IPC and nothing else. Only the
   preload file may touch `ipcRenderer`.
2. **Serve local media over a custom protocol, never `file://`.** Register a
   privileged scheme and stream through it. `file://` under a sandboxed renderer with
   CSP will fight you forever.
3. **Cache derived artifacts by path + mtime.** Thumbnails and probes are expensive;
   key them so a re-render invalidates automatically.
4. **Treat "deleted" as permanent, everything else as TTL'd.** A post that is gone
   does not come back; re-checking it every launch wastes requests.
5. **Never write into the user's video folders.** vidwatch is read-only over the
   pipeline's output. All app state goes in the OS app-data directory.

## Scripts

- `scripts/scaffold-config.mjs` — walk a videos root, propose a `vidwatch.config.json`.
  Read-only. `--marker`, `--out`, `--depth`, `--json`.
- `scripts/doctor.mjs` — validate a config against the real filesystem and report what
  will actually be discovered. Read-only. Exit 1 on fatal problems.

Both are dependency-free Node ≥18 and safe to run repeatedly.

## References

- `references/architecture.md` — module map, per-layer build instructions, the
  self-check harness, and the data flow through the join.
- `references/config.md` — **the config contract.** Every tunable, its default, and
  worked examples for four different real-world layouts.
- `references/inputs.md` — every input file shape: mp4 naming, metadata sidecar
  resolution order, ledger records, platform-status files, and how to add a new
  metadata dialect.
- `references/platforms.md` — pluggable liveness + metrics providers, why the two must
  stay separate, and a worked TikTok provider.
- `references/packaging.md` — macOS/Windows/Linux packaging, install scripts, and the
  stale-packaged-app trap.
