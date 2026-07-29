# What each workflow needs

Nothing here costs money to start. Only set up the workflow you're actually
running — the others need nothing.

Every download and signup link, plus which key maps to which environment
variable: [useful-links.md](useful-links.md).

---

## Everyone

| | Why |
|---|---|
| **GitHub account** | clone the repo |
| **Claude Code or Codex** | runs the workflows |
| **git + Python 3.9+** | `xcode-select --install`; Python is already on macOS |

No Python packages. The scripts use the standard library only, deliberately —
a dependency you have to install is a dependency that breaks on someone's
machine at the worst moment.

---

## engine-outreach

**A Gmail account connected to your agent, with permission to create drafts.**
That's all of it. No Google Cloud project, no API key, no OAuth consent screen.

If your Gmail is a managed Workspace account, the connector is sometimes
blocked at the admin level. A personal Gmail works and takes two minutes.

*Optional, much later:* a domain and a sending API when drafts stop scaling.
See `skills/engine-outreach/references/advanced.md` — including why you
shouldn't jump straight to it.

## engine-seo

**Nothing.** Reddit needs no account, and where there's no API the agent reads
the page in your browser.

Useful if you have them:

- **Competitor URLs** — pages you'd like to outrank. Put them in `config/sources.json`
- **Google Search Console** — verify your site once and metric fetching becomes
  a free API call instead of a browser read
- **Ahrefs or Semrush** — only if you already pay. Don't buy one for this

**No website yet?** The workflow builds one — an Astro site in `workflows/site/`
that turns your markdown into pages. You'll need a free **Cloudflare Pages** or
**Railway** account to deploy it. Nothing to install up front; the agent
scaffolds it when you get there.

## engine-linkedin

**Nothing**, if you post manually — which is the default and is fine.

Optional: Upload Post or Buffer for scheduling. See [posting-options.md](posting-options.md).

## engine-video

The one workflow with real setup:

| | Get it from | Cost |
|---|---|---|
| **ffmpeg** | `brew install ffmpeg` | free |
| **Pexels API key** | [pexels.com/api](https://www.pexels.com/api/) — instant, no card | free |
| **ElevenLabs API key** | [elevenlabs.io](https://elevenlabs.io) → Profile → API key | free tier |
| **~10 GB free disk** | | — |
| **Upload Post** *(optional)* | [upload-post.com](https://www.upload-post.com/) → dashboard → API key | free to 10 posts/month, then paid |

Names go in `config/.env` — copy `config/.env.example` and fill it in yourself.
Your agent reads the example file for names and never reads `.env`.

## engine-loop

**Nothing** to start. It reads your run data and your browser.

Optional at volume: an Apify token for structured platform analytics. Browser
reading is free and works well — don't pay for this in week one.

---

## Keys: the rules

- **Paste them into `config/.env` yourself.** Never into a chat window
- **`.env` is gitignored** from the first commit. Keep it that way
- If a key leaks, rotate it — every service here lets you, and it takes a minute
- Your agent reads `.env.example` for the *names* of variables, never `.env`
  itself. If a key is missing it should tell you which variable and where to
  get it, not work around it
