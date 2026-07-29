# Posting: manual, Upload Post, or Buffer

Start manual. Add a scheduler once you know the workflow is worth automating —
which you won't know for a few weeks.

| | **Manual** *(default)* | **Upload Post** | **Buffer** |
|---|---|---|---|
| Cost | free | free to 10 posts/month, then **$24/mo** | free tier available |
| Setup | none | account + API key | account + connect each channel |
| Media | you upload it | handles video upload directly | **needs media already at a public URL** |
| Platforms | all of them | TikTok, YouTube, Instagram, X, Threads, Facebook, LinkedIn | broad, strongest for text |
| Analytics back to the loop | none — read them in the browser | via API | via API |
| Best for | week one, everyone | the video workflow | you already use Buffer |
| The catch | you click post | the 10/month cap arrives fast | media hosting is real friction |

---

## Why manual is the default

You ship something real on day one with no accounts and no keys. That matters
more than it sounds: most people who never launch a growth system stall during
setup, not during the work.

Manual also costs you nothing in the loop. The metric still gets recorded —
you read it off the platform's own analytics screen and run:

```bash
python3 skills/engine-loop/scripts/runlog.py metric --run <id> --value 3400 --source browser
```

The only thing you lose is the scheduling.

## Upload Post

The better fit for video, because it handles the upload itself rather than
demanding a public URL first.

The free tier is 10 posts a month. If you're posting three times a week you'll
hit it in the second week, so decide up front whether you're paying or staying
manual — discovering the cap mid-run is annoying.

Key goes in `config/.env` as `UPLOADPOST_API_KEY`. Set the channel's `publish`
to `uploadpost` in `config/channels.json`.

## Buffer

Reasonable if you already use it. The friction is media: Buffer needs images
and video to already exist at a public URL, so you need somewhere to host them
first. That's a bucket and a small upload step — see
`skills/engine-setup/references/advanced.md` for the pattern that keeps storage
costs at roughly zero.

For text-only LinkedIn and X posts this doesn't apply and Buffer is fine.

Token goes in `config/.env` as `BUFFER_ACCESS_TOKEN`. Set `publish` to
`buffer`.

---

## Whichever you pick

**Record the URL after publishing.** The loop can't fetch numbers for a post it
can't find:

```bash
python3 skills/engine-loop/scripts/runlog.py publish --run <id> --url https://...
```

**Nothing posts without you.** All three modes end with a human approving. The
workflows draft; you publish.
