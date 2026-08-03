# Footage — sourced first, Pexels fallback

## Order

1. **`shared/assets/`** — product recordings, licensed B-roll, brand clips
2. **Pexels** — the default fallback when assets can't cover the segment
   (`inputs.json` → `backgroundFootage`)

Pexels is the default because it's free, licensed and needs one key. It is not
the only option: generated clips, YouTube, Pinterest and short-form platforms
are all on the table, each with its own trade-off. **`references/clip-sourcing.md`
lays the options out and helps you pick with the user** — read it before
deciding a source, and come back here for the Pexels mechanics.

## Pexels download (portrait)

Needs `PEXELS_API_KEY` in `shared/.env` (source the file; don't read it into chat).

```bash
set -a; . ~/gtm/shared/.env; set +a

QUERY="tired founder laptop night"
OUT="shared/assets/pexels"
mkdir -p "$OUT"

# Search (portrait). Keep the JSON for attribution if you care later.
curl -sS "https://api.pexels.com/videos/search?query=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$QUERY")&orientation=portrait&per_page=5" \
  -H "Authorization: $PEXELS_API_KEY" -o /tmp/pexels.json

# Pick a file URL (agent: choose a portrait file ~1080-ish height) then:
# curl -L -o "$OUT/${QUERY// /-}-1.mp4" "<video_file_link>"
```

Prefer **medium** quality for B-roll; re-encode to 1080×1920 with
`references/ffmpeg-recipes.md` (zoom-fill).

Save downloads under `shared/assets/` (or `shared/assets/pexels/`), **not**
home-directory media trees. For a run-specific pull, you may also write to
`runs/<run_id>/assets/` and reference those paths from `inputs.json`.

## Naming

```
shared/assets/pexels/<slug>-<n>.mp4
```

Embed the query in the slug so the next agent knows why the clip was pulled.

## Optional skill

Full helper script: `benyki/skills/pexel-video-downloader` — if installed, point
`--output` at `shared/assets/pexels` (never `~/runs/…`).
