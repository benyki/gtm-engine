# Input Formats

Everything vidwatch reads, and how to make it read something else. The design rule
throughout: **inputs are untrusted and optional.** Every reader returns `undefined`
on any failure; a post with zero resolvable inputs still renders as a card.

## 1. Video files

Any file matching `videoExtensions` inside a source folder. The **stem** (filename
minus extension) is the join key for everything else.

### Stems and timestamp stripping

Render pipelines commonly stamp outputs: `airport-20260627T004435Z.mp4` rendered from
`configs/airport.json`. The scanner therefore derives a second candidate stem by
stripping a trailing `-YYYYMMDD` or `-YYYYMMDDThhmmssZ`:

```
/^(.+)-\d{8}(?:T\d{6}Z)?$/  →  captured group
```

Metadata resolution tries the exact stem across **all** locations first, then the
stripped stem across all locations — an exact match must always beat a base match.
If the target pipeline stamps differently (e.g. `_v2`, `-final`, unix epochs), extend
this regex — it is the single point of truth for stem aliasing.

## 2. Per-clip metadata (sidecars)

Resolution order comes from config `metadataLocations` — path templates relative to
the mp4's directory with `{stem}` substituted. Defaults cover common layouts:

| template | which layout it serves |
|---|---|
| `{stem}.json` | sidecar right next to the published mp4 |
| `../{stem}.json` | render-dir sidecar (mp4 archived one level down into published/) |
| `../configs/{stem}.json` | configs folder beside the outputs dir |
| `../../configs/{stem}.json` | configs at the series root |
| `../../inputs/{stem}.json` | authored inputs dir |

First file that exists **and parses** wins. Adapting to a new project is usually just
editing this list — e.g. a pipeline that writes `meta/<stem>.yaml` adds
`../meta/{stem}.yaml` plus a YAML parse branch in `readJson`.

### Normalized shape

Whatever the sidecar looks like, it normalizes to:

```ts
interface PostInputs {
  language?: string;      // "French" | "Spanish" | ...
  hook?: string[];        // hook/title lines
  outro?: string;
  bgQuery?: string;       // background search query used at render time
  words: WordPair[];      // [{prompt, answer}] — the clip's content pairs
  durationSec?: number;
  sourcePath?: string;    // where the metadata was found (for the detail view)
  raw?: unknown;          // full original JSON, always kept
}
```

`raw` is the escape hatch: the detail view renders it as JSON, so even a completely
unrecognized dialect is inspectable in-app.

### Word-pair dialects the default extractor accepts

The list is found under the first present of: `words`, `items`, `pairs`, `entries`
(checked on the sidecar, then on a nested `config` object). Each element maps by the
first matching key pattern:

| element shape | prompt ← | answer ← |
|---|---|---|
| `{word, translation}` | word | translation |
| `{school, slang}` | school | slang |
| `{prompt, answer}` | prompt | answer |
| `{en, <other key>}` | en | the other key's value |
| `{english, target}` | english | target |
| two-string array `["hi","salut"]` | [0] | [1] |

### Adding a dialect

New pipelines mean new shapes. Add one `else if` branch to `extractWords` in
`scanner.ts` (match on the keys present, push `{prompt, answer}`), and if the
list itself lives under a new key, add that key to the list-lookup chain. Keep
branches ordered most-specific-first. Never throw on a weird element — skip it.

Language, if absent from metadata, falls back to the source's config `language`, then
to filename heuristics if you add any (otherwise flags can render a neutral mark when
unknown).

## 3. The posting ledger

Append-only log written by whatever posts the clips. One record per post attempt.
Example JSONL at `<workspace>/state/posts.jsonl` (or any path you set in config):

```jsonl
{"posted_at":"2026-07-28T17:38:12Z","pipeline":"upload-post","account":"your-account","status":"sent","post_url":"https://www.tiktok.com/@your-handle/video/7123456789012345678","post_id":"v_...","tag":"daily-posting","file_archived":"/path/to/videos/series-a/published/clip-001.mp4"}
```

The config `ledger.fields` block maps arbitrary field names onto the canonical set,
so a differently-shaped ledger needs zero code — only config. Three formats are worth
supporting in the reader: `jsonl` (line-delimited), `json-array`, `csv` (header row).
For anything else (SQLite, an API), write a small exporter to JSONL rather than
teaching vidwatch to query it — keeps the app read-only and dependency-free.

Join semantics (implement exactly):

- Index by normalized absolute path of the `file` field AND by that file's stem.
- `find(file, stem)`: path match first, stem match second.
- Later records override earlier ones (reposts/corrections).
- A record's `account`/`pipeline` overrides the source-level config guess.
- `postedAt` parse failure → keep the hit but fall back to mtime for the date.

Status vocabulary that the UI colors care about: `sent`/`feed` (live), `inbox` or
delivery `inbox` or post_id prefix `v_inbox_file` (delivered to the app's inbox, needs
manual posting — orange dot), anything else → neutral.

## 4. Platform status files

Optional per-source-folder record of multi-platform fanout, default name
`platform-status.json`, living next to the published folder:

```json
{
  "my-clip-stem": {
    "tiktok":  { "status": "posted", "url": "https://...", "postedAt": "...", "account": "...", "confirmed": true },
    "youtube": { "status": "scheduled" }
  }
}
```

Keys are stems; unknown platforms are ignored (config `platformStatus.platforms` is
the allowlist); unknown status strings pass through and simply don't light the icon.

## 5. App-owned state (not inputs, don't confuse them)

Written by vidwatch itself into `userData`, never into the video tree:

| file | contents |
|---|---|
| `vidwatch.config.json` | the config (if the user keeps it here) |
| `availability.json` | liveness + stats cache, keyed by post URL |
| `thumbs/*.jpg` | poster-frame cache, keyed by sha1(path:mtime[:seek]) |
| `projects.json` | user-defined tab groupings of formats |

Safe to delete any of these at any time; they rebuild. Tell users that — it is the
fix for 90% of "stale data" reports (and the other 90% is a stale packaged app,
see packaging.md).
