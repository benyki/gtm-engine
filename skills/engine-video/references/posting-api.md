# Posting APIs — Upload Post + Buffer (how-to)

Decision table: `references/posting-options.md`.
This file is the **how** after the user picks a mode and approves the upload.

Always finish with:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish \
  --run <run_id> --url https://...
```

Never post without an explicit yes.

## Upload Post (best default for video)

- Key: `UPLOADPOST_API_KEY` in workspace `shared/.env`
- Accepts a **local file** (multipart) — no public URL required
- Docs: https://docs.upload-post.com/

```bash
set -a; . /absolute/path/to/workflows/shared/.env; set +a

# List profiles (usernames are case-sensitive)
curl -sS https://api.upload-post.com/api/uploadposts/users \
  -H "Authorization: Apikey $UPLOADPOST_API_KEY"
```

Post flow (conceptually — prefer the `upload-post` skill script if installed):

1. `--file runs/<run_id>/output/final.mp4`
2. `--user <profile-username>`
3. platform(s), caption, optional `--aigc` if the content is AI-disclosed
4. Confirm the response is a **real public URL**, not inbox/draft fallback
5. `runlog.py publish --run … --url …`

**Inbox trap:** Upload-Post's shared TikTok app can hit a daily active-user cap and
silently deliver to inbox (`reached_active_user_cap`). Treat inbox as not-published;
retry later or finish in the TikTok app. Details in the Upload-Post docs.

Optional full skill: `benyki/skills/upload-post`.

## Buffer (when they already live there)

- Key: `BUFFER_ACCESS_TOKEN` (or as named in `.env.example`)
- **Needs the media at a public HTTPS URL** — Buffer does not take local files
- Stronger for text; workable for video if you host the mp4 first

Flow:

1. Host `final.mp4` (signed URL, short TTL preferred)
2. Create/schedule the post to the connected channel via Buffer API / skill
3. Record the public post URL in `runlog` when it goes live

Optional: `benyki/skills/buffer` + `benyki/skills/buffer-videos`.

## Manual

User uploads from `runs/<run_id>/output/final.mp4`, pastes the URL, you run
`runlog.py publish`. Still valid — often correct on week one.
