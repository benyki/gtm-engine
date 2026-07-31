# Useful links

Everything you might need to download or sign up for, in one place.

Deep links into settings pages move around. Where that's likely, the root
domain is given plus the path in words — slower to follow, but it still works
in a year.

---

## Start here — everyone needs these

| What | Where | Notes |
|---|---|---|
| **Claude Desktop** (for Claude Code) | <https://claude.ai/download> | Sign in, then toggle to the **Code** tab, top left |
| **Claude Pro or higher** | <https://claude.ai/upgrade> | Required for Claude Code |
| **ChatGPT Desktop** (for Codex) | <https://openai.com/chatgpt/download/> | Alternative to Claude Code. Toggle to **Codex**, top left |
| **ChatGPT Plus or higher** | <https://chatgpt.com/#pricing> | Required for Codex |
| **Browser extension** — *Claude in Chrome*, or the ChatGPT one for Codex | install from your agent's app, then connect it | Lets the agent act in your logged-in browser. **Mandatory for `engine-social`**, recommended for `engine-video`, nice to have elsewhere — [preflight §2b](preflight.md) |
| **Xcode Command Line Tools** | run `xcode-select --install` | Gives you `git`. 5–10 min download, no URL needed |
| **Homebrew** | <https://brew.sh> | Only if you need `ffmpeg` |

Python is already on macOS. This repo needs no Python packages.

---

## Per workflow

### engine-outreach

**Gmail** connected to your agent with permission to create drafts — no Google
Cloud project, no API key.

- Gmail — <https://mail.google.com>

### engine-seo

Reddit needs no account to read.

Useful if you have them:

| What | Where | Notes |
|---|---|---|
| Google Search Console | <https://search.google.com/search-console> | Verify your site once; turns metric fetching into a free API call |
| Ahrefs API | <https://ahrefs.com/api> | Only if you already pay |
| Semrush API | <https://www.semrush.com/api-documentation/> | Only if you already pay |

**If you don't have a website yet**, the workflow builds one — Astro plus your
markdown, deployed on push. All free at this size:

| What | Where | Notes |
|---|---|---|
| Astro | <https://astro.build> · docs: <https://docs.astro.build> | Check the current docs — the content APIs changed in v5 |
| `@astrojs/sitemap` | <https://docs.astro.build/en/guides/integrations-guide/sitemap/> | sitemap.xml |
| `@astrojs/rss` | <https://docs.astro.build/en/guides/rss/> | RSS feed |
| astro-seo | <https://github.com/jonasmerlin/astro-seo> | Open Graph and Twitter tags |
| **Cloudflare Pages** | <https://pages.cloudflare.com> | free tier, deploys on push |
| **Railway** | <https://railway.app> | free trial then usage-based; simplest if you already run other services there |

### engine-social

Nothing required for LinkedIn and X — draft in the agent, post from your own
logged-in browser. Bluesky uses its API (app password), not a scheduler.

| What | Where | Notes |
|---|---|---|
| **Bluesky app password** *(only if you post there)* | <https://bsky.app> → Settings → Privacy and Security → App Passwords | Never your account password. Goes in `shared/.env` as `BSKY_HANDLE` / `BSKY_APP_PASSWORD` |

Images are optional. Picking one out of `social/inputs/images/` needs nothing.
*Editing* one — crop, background swap, aspect-ratio variants — needs one key,
either provider, in `shared/.env`:

| What | Where | Getting the key | Cost |
|---|---|---|---|
| **Google AI Studio** — Gemini image models, "nano banana" | <https://aistudio.google.com> · docs: <https://ai.google.dev/gemini-api/docs/image-generation> | <https://aistudio.google.com/apikey> → **Create API key**, pick a project | free tier, then per image |
| **OpenAI** — GPT Image | <https://platform.openai.com> · docs: <https://developers.openai.com/api/docs/guides/image-generation> | <https://platform.openai.com/api-keys> → **Create new secret key** (shown once). Image edits may need org verification | prepaid credits, no free tier |

How it's used: [engine-social/references/images.md](../skills/engine-social/references/images.md).

### engine-video

| What | Where | Getting the key | Cost |
|---|---|---|---|
| **ffmpeg** | `brew install ffmpeg` — <https://ffmpeg.org> | n/a | free |
| **Pexels** | <https://www.pexels.com/api/> | Request a key on that page — issued instantly, no card | free |
| **ElevenLabs** | <https://elevenlabs.io> | Sign in → profile menu → **API Keys** | free tier |
| **CapCut** *(optional)* | <https://www.capcut.com> | n/a | free |

Video posting options (manual / Upload Post / Buffer):
[engine-video/references/posting-options.md](../skills/engine-video/references/posting-options.md).

### Posting for video (optional — manual needs nothing)

| What | Where | Getting the key | Cost |
|---|---|---|---|
| **Upload Post** | <https://www.upload-post.com/> | Sign in → dashboard → API key | free to 10 posts/month, then paid |
| **Buffer** | <https://buffer.com> · developers: <https://developers.buffer.com> | Create an app, then generate an access token | free tier; needs media at a public URL |

### engine-loop

Not a content workflow — the learning framework under the ones above. Nothing
required; browser reading is free and works.

| What | Where | Getting the token | Cost |
|---|---|---|---|
| **Microsoft Clarity** *(optional)* | <https://clarity.microsoft.com> | Add your site → project → Settings → **Data Export** → generate token | free at any volume |
| **Apify** *(optional)* | <https://apify.com> · console: <https://console.apify.com> | Console → Settings → Integrations → API token | paid |

Clarity is optional like everything else here, but it's the only free source
that shows what people did *on* the page — scroll depth, rage clicks,
quick-backs — which is what decides what to make next rather than grading what
you already made.

**What it needs is a website**, with the Clarity snippet on it — any site you
control: an existing product site, a landing page, a blog you already run, or
one `engine-seo` built for you. That's the only requirement. It's useful to any
workflow that sends traffic somewhere: a social post's click-through lands on a
page, and Clarity is what tells you whether that page worked.

If there's no site at all, Clarity has nothing to record — skip it until there
is one.

---

## Advanced track

Only relevant once you've been running this for a while. Each links back to
the reference that explains when it's worth it.

### Storage and data — `engine-setup/references/advanced.md`

| What | Where |
|---|---|
| Supabase | <https://supabase.com> |
| Supabase CLI | <https://supabase.com/docs/guides/cli> |
| Supabase MCP server | <https://supabase.com/docs/guides/getting-started/mcp> |
| Google Cloud Storage | <https://cloud.google.com/storage> |
| Cloudflare R2 *(no egress fees)* | <https://developers.cloudflare.com/r2/> |
| AWS S3 | <https://aws.amazon.com/s3/> |
| Tailscale | <https://tailscale.com> |

### Additional skills (optional toolbox)

Not part of the default gtm-engine install. Download from
[`benyki/skills`](https://github.com/benyki/skills) **into** `~/.agents/skills/<name>`,
then symlink to Claude / Codex / Cursor — full steps in
[additional-skills.md](additional-skills.md).

| What | Where |
|---|---|
| Skills repo | <https://github.com/benyki/skills> |
| Example skill | <https://github.com/benyki/skills/tree/main/ffmpeg> |
| Canonical install path | `~/.agents/skills/<skill-name>/` |

### Email at volume — `engine-outreach/references/advanced.md`

| What | Where |
|---|---|
| Cloudflare Email Routing | <https://developers.cloudflare.com/email-routing/> |
| Resend | <https://resend.com> · keys: <https://resend.com/api-keys> |
| Postmark | <https://postmarkapp.com> |
| AWS SES | <https://aws.amazon.com/ses/> |
| Check your SPF/DKIM/DMARC | <https://www.mail-tester.com> |

### Publishing — `engine-seo/references/advanced.md`

Content in a database, built into static pages at build time.

| What | Where |
|---|---|
| Astro Content Loader API *(custom loaders)* | <https://docs.astro.build/en/reference/content-loader-reference/> |
| Next.js | <https://nextjs.org> |
| Supabase JS client | <https://supabase.com/docs/reference/javascript> |
| Vercel | <https://vercel.com> |

Read the framework's current SEO guide when you build this — these integrations move.

### Device posting — `engine-video/references/advanced.md`

| What | Where |
|---|---|
| mobilerun | <https://github.com/droidrun/mobilerun> |
| mobilerun quickstart | <https://docs.mobilerun.ai/quickstart> |

Read the account-risk section in that reference before acting on it.

### Reporting to your phone — `engine-loop/references/advanced.md`

| What | Where |
|---|---|
| Telegram BotFather *(create a bot)* | <https://t.me/botfather> |
| Telegram Bot API | <https://core.telegram.org/bots/api> |
| WhatsApp Business Platform | <https://developers.facebook.com/docs/whatsapp> |

---

## Which key goes where

Every value below lives in `workflows/shared/.env`. Copy `.env.example`
first, then paste your own keys in — never into a chat window.

| Environment variable | Get it from | Needed for |
|---|---|---|
| `BSKY_HANDLE` / `BSKY_APP_PASSWORD` | <https://bsky.app> → Settings → App Passwords | engine-social (Bluesky only) |
| `PEXELS_API_KEY` | <https://www.pexels.com/api/> | engine-video |
| `ELEVENLABS_API_KEY` | <https://elevenlabs.io> → API Keys | engine-video |
| `UPLOADPOST_API_KEY` | <https://www.upload-post.com/> → dashboard | posting (optional) |
| `BUFFER_ACCESS_TOKEN` | <https://developers.buffer.com> | posting (optional) |
| `RESEND_API_KEY` | <https://resend.com> → API Keys | engine-outreach (optional, advanced) |
| `CLARITY_API_KEY` | <https://clarity.microsoft.com> → project → Settings → Data Export | engine-seo + engine-loop (optional, free) |
| `AHREFS_API_KEY` | <https://ahrefs.com/api> | engine-seo (optional) |
| `SEMRUSH_API_KEY` | <https://www.semrush.com/api-documentation/> | engine-seo (optional) |
| `APIFY_API_TOKEN` | <https://console.apify.com> → Integrations | engine-loop (optional) |

Your agent reads `.env.example` for the variable *names* and never reads
`.env` itself, so it can tell that a key is set but not what it is.

If a key ever leaks, rotate it — every service here lets you, and it takes
about a minute.

---

## Something moved?

If a link here 404s, open an issue or a PR. Signup flows change more often
than anything else in this repo.
