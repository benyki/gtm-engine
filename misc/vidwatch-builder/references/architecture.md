# Architecture & Layered Build Guide

If an existing vidwatch repo is reachable on the current machine (look for a
`vidwatch/` folder under the user's code directory), copy files from it and adapt;
when it isn't, this document is enough to rebuild from scratch.

## Stack

Electron + esbuild + React 18 + TanStack Query + Tailwind 3 + TypeScript. All
devDependencies; no runtime deps beyond Electron itself. esbuild compiles in ~130ms,
which is what makes the `npm start` loop pleasant. Avoid heavier bundlers.

## Module map

```
app/
  shared/types.ts            ← the contract between worlds. NO runtime logic.
  main/                      ← Node/Electron main process
    index.ts                 ← window, custom protocols, menu, self-check harness
    handlers/                ← IPC endpoints, one file per domain
      index.ts               ←   registers them all: ipcMain.handle(channel, fn)
      posts.ts               ←   posts:overview / posts:refresh / availability:refresh
      projects.ts            ←   user-defined tabs (CRUD → userData/projects.json)
      shell.ts               ←   reveal / open / openExternal / clipboard
    services/                ← pure logic, no Electron imports except app.getPath
      config.ts              ←   [NEW in ports] load + validate vidwatch.config.json
      registry.ts            ←   named sources (reads config; original hardcodes)
      scanner.ts             ←   THE CORE: discovery + metadata + the join → Overview
      ledger.ts              ←   posting-ledger reader (path/stem indexed)
      availability.ts        ←   liveness + metrics cache (see platforms.md)
      thumbs.ts              ←   ffmpeg poster frames, cached by path+mtime
      projects.ts            ←   tabs persistence
  renderer/
    preload.ts               ← ONLY file allowed to touch ipcRenderer; exposes window.api
    styles.css               ← Tailwind + design tokens + keyframe animations
    main/
      index.tsx  api.ts      ← bootstrap; typed wrappers over window.api + react-query
      app.tsx                ← layout: header / sidebar filters / card grid; state
      format.ts              ← display helpers (dates, counts, engagement %)
      components/            ← PostCard, PostDetail, TopPosts, ProjectsNav, ui, icons
esbuild.mjs                  ← 3 builds: main(node) / preload(cjs) / renderer(browser)
main-window.html             ← static entry, copied into build/
```

### Data flow (one direction)

```
scan(): walk videosRoot → sources → per-source mp4s → per-mp4:
        stem → findMetadata() → normalizeInputs()
             → ledger.find(path, stem) → postedAt/account/url
             → availabilityFor(url) + statsFor(url)   (cache reads, NO network)
             → platform-status.json record
        ⇒ Overview { posts[], sources[], scannedAt, emptyDirs[] }

renderer: useQuery("overview") → invoke("posts:overview") → grid
network:  ONLY inside availability:refresh (explicit or once-per-launch), which
          updates the cache and re-scans. scan() itself must never touch the network.
```

That separation — scan is filesystem-only, refresh is network-only — keeps the app
instant on launch and makes every network failure non-fatal by construction.

## Security posture (non-negotiable, all layers)

```ts
webPreferences: { preload, contextIsolation: true, nodeIntegration: false, sandbox: true }
```

Media is served over two privileged custom schemes registered **before** app ready:

```ts
protocol.registerSchemesAsPrivileged([
  { scheme: "vwthumb", privileges: { standard: true, secure: true, supportFetchAPI: true } },
  { scheme: "vwvideo", privileges: { standard: true, secure: true, supportFetchAPI: true, stream: true } },
]);
// handler: decode base64url path from URL → verify existsSync → net.fetch(pathToFileURL(...))
```

Preload encodes: `vwthumb://local/<base64url(absolute path)>?t=<seek>`. The handler
existence-checks the decoded path before serving — that check is the safety boundary;
keep it.

---

## Layer 0 — Shell

`package.json` scripts (the contract the rest of this doc assumes):

```json
{
  "build:main": "node esbuild.mjs",
  "build:css": "tailwindcss -i app/renderer/styles.css -o build/renderer/styles.css --minify",
  "build": "npm run build:main && npm run build:css",
  "start": "npm run build && electron ."
}
```

`esbuild.mjs` — three builds, exactly:

| entry | platform | format | external | note |
|---|---|---|---|---|
| `app/main/index.ts` | node | cjs | electron | everything bundled to one file |
| `app/renderer/preload.ts` | node | **cjs** | electron | sandbox requires cjs preload |
| `app/renderer/main/index.tsx` | browser | esm | — | `jsx: "automatic"` |

Window: `titleBarStyle: "hiddenInset"` is macOS-only sugar — gate it on
`process.platform === "darwin"`, default frame elsewhere. Set `backgroundColor` to the
app bg to avoid a white flash. `show: false` + show on `ready-to-show`.

Forward renderer console errors to main-process stdout (`console-message` event).
Without this, headless debugging is guesswork.

**Done when:** `npm start` opens a styled empty window with zero devtools errors.

## Layer 1 — Sources

`config.ts` (see config.md) + `registry.ts` + the discovery half of `scanner.ts`:

- Walk `videosRoot` to `walkDepth`. Every directory named `publishedMarker` becomes a
  source (or, marker null: every dir containing a matching video file).
- Merge with config `sources[]` by `publishedRel`; unmatched discoveries get
  `id: "unlinked:<relpath>"`, `pipeline: "unknown"`.
- Every fs call in try/catch. Unreadable dir → skip silently. Root missing → empty
  overview plus a visible warning in the UI, not a crash.

**Done when:** a debug print of `scan().sources` matches what `doctor.mjs` reports.

## Layer 2 — Posts + metadata

The join core in `scanner.ts`:

- Per source, list files matching `videoExtensions` → stem = basename minus ext.
- `findMetadata(dir, stem)`: try `metadataLocations` templates in order; then retry
  all of them with the timestamp-stripped stem (inputs.md § stems). First parse wins.
- `normalizeInputs(raw)`: tolerant extraction into `PostInputs` (inputs.md § shapes).
  Unknown shape → keep `raw` for the detail view, leave the rest undefined.
- `postedAt`: file mtime for now (ledger refines it in layer 3).
- Sort **newest first** and return.

Renderer: `api.ts` (invoke wrappers + `useOverview()`), `app.tsx` (header stats,
sidebar filter groups computed by `uniqCount`, card grid
`grid-cols-[repeat(auto-fill,minmax(112px,1fr))]`), `PostCard` (9:16 poster box —
placeholder until layer 6 — title from metadata, date line), `PostDetail` modal.

Filters are client-side derivations of the loaded overview — never separate IPC
round-trips. Account/language/format/pipeline each filter by exact match; groups
compose with AND.

**Done when:** real clips appear as cards, count matches disk, filters narrow the grid.

## Layer 3 — Ledger

`ledger.ts`: read the configured ledger into two maps — by absolute file path (from
the configured `file` field) and by stem. `find(file, stem)` tries path, then stem.
Later records win (append-only logs correct themselves). Tolerate: missing file,
blank lines, malformed rows, unparseable dates — row-level failures skip the row,
never abort the read.

A hit upgrades the post: exact `postedAt`, `account`, `url`, `status`, `exact: true`.
Also overlay onto the source: a ledger `account`/`pipeline` beats a config guess.

**Done when:** most cards show ledger times (`exact` count in a debug print), the
rest show mtime, and no ledger file at all still renders the full grid.

## Layer 4 — Platform status

Optional sidecar per source folder (config `platformStatus.file`), shape:
`{ "<stem>": { "<platform>": { status, url?, postedAt?, account? } } }` — accept
`status` values loosely (`posted|sent|scheduled|pending|inbox|failed`). Attach as
`post.platforms`. UI: row of small platform icons on the card for `posted` entries,
clickable when a `url` exists; full table in the detail view.

## Layer 5 — Liveness + metrics

Implement exactly the provider split in **platforms.md** (liveness verdict and
metrics scrape are separate concerns with separate failure modes). `availability.ts`
owns one cache file in userData:

```
{ [url]: { status: "available"|"removed"|"unknown", checkedAt, stats?: {plays, likes, comments, shares, fetchedAt} } }
```

TTLs from config: `removed` permanent, `available` re-checked after `statsTtlHours`,
`unknown` after `unknownTtlDays`. Worker-pool the refresh at `metrics.concurrency`,
persist incrementally (every ~10 results) so a crash keeps progress.

Trigger points: once per launch silently; on a header button explicitly. The explicit
path also opens the Top-5 leaderboard (`TopPosts`: rank by plays over a 31-day
window, engagement % = (likes+comments+shares)/plays) and fires the milestone
celebration on visible cards (thresholds ladder 250/500/1K/5K/10K/50K/100K — show the
highest rung cleared; keep the unmount timeout longer than the CSS animation).

**Done when:** dots reflect reality (grey no-url / green recent / blue live / red
removed / orange inbox), a forced refresh fills stats for most live posts, and
`doctor.mjs` style spot-checks of 2–3 URLs against the platform agree with the cache.

## Layer 6 — Thumbnails

`thumbs.ts`: `thumbFor(videoPath, atSeconds)` → cached jpg in `userData/thumbs/`,
key `sha1(path:mtime[:at])`. ffmpeg:
`-y -ss <at> -i <path> -frames:v 1 -vf scale=<width>:-2 -q:v 4 <out>` with a 20s
timeout. **Seeking past a short clip's end produces no file — return null, protocol
handler 404s, and the card's `onError` falls back** (this exact behavior implements
"peek at 6s" for free: pill click toggles `?t=6` on the thumb URL; error path drops
back to the default poster, not the placeholder).

## Layer 7 — Packaging

See packaging.md. Not needed for daily use — `npm start` is the loop.

---

## Verifying without a human

Build the self-check harness into `main/index.ts` from layer 0 — it is how an agent
sees the app. Gated on env vars, it runs after `did-finish-load`:

```
TT_SELFTEST=1  print JSON: title, card count, header stats, filter count, dot counts
TT_CLICK="label"  find button by text prefix, click it, wait
TT_SHOT=/path.png  capturePage() → png
TT_WAIT=ms  settle time before the checks (network refresh needs 60–90s)
```

then `app.quit()`. Usage pattern per layer:

```bash
TT_SELFTEST=1 TT_WAIT=6000 TT_SHOT=/tmp/check.png npx electron .
# → [SelfTest] {"title":"vidwatch","cards":300,...}  + screenshot to eyeball
```

Extend it ad hoc for a specific verification (click a card pill, sample an
animation's computed opacity over time, compare leaderboard rows against an
independent sort of the overview) — then **remove the ad-hoc block after the check
passes**. The four env hooks above are the only permanent residents.

Also verify one level below the UI: `doctor.mjs` for the filesystem join, and direct
curl/fetch probes for providers (platforms.md § probing) before wiring them in.
