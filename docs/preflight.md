# Preflight — is this machine ready?

**This is the workshop checklist** — deliberately rigid and ordered so a room
full of different machines reaches the same working state. Do the steps in
sequence, and set up **one** workflow only — outreach unless you'd rather start
somewhere else. (Everywhere else in this repo, instructions are defaults you may
adapt — here they're steps to follow.)

Ten minutes. Run through it before you install anything, or paste the block at
the bottom into your agent and let it check for you.

Only set up the workflow you're actually running. Downloads and signup links:
[useful-links.md](useful-links.md).

---

## 1. Machine

| Check | How | If not |
|---|---|---|
| **Apple Silicon Mac** (M1 or newer) | → About This Mac → "Chip" says Apple M-something | Intel works for text workflows; video rendering will be slow. Linux mostly works. Windows needs adapting — ask us |
| **macOS 13+** | same screen | Update first — it's a long download |
| **You can install apps** | try installing anything | Managed work laptops often block this. You need admin access. Sort it before you start |
| **10 GB free disk** | Storage settings | Only needed for the video workflow |
| **Developer tools** | `xcode-select --install` in Terminal | 5–10 minutes. This is what gives you `git` |
| **Python 3.9+** | `python3 --version` | Already on macOS. Scripts use the standard library only |

Bring your charger.

## 2. An AI coding agent

Pick one and check you can **sign in** before you start.

- **Claude Code** — Claude Desktop, sign in, toggle to the **Code** tab (top left). Needs Claude Pro or higher
- **Codex** — ChatGPT desktop, sign in, toggle to **Codex** (top left). ChatGPT Plus or higher recommended

Prefer the terminal? Install commands are in [useful-links.md](useful-links.md).

**Then check it actually works.** Open any folder and ask it:

```
create a file called hello.txt with the word hello in it
```

If the file appears, you're ready. If it asks for permissions, approve them.

## 2b. The browser extension

The piece that lets the agent **act in your browser on your behalf** — open a
page, read what's on it, fill a composer, click through an analytics screen —
using the sessions you're already logged into. No API keys, no developer
accounts.

- **Claude Code** → *Claude in Chrome* extension, then connect it from the app
- **Codex** → the ChatGPT browser extension, connected the same way

Install it **before** the session and confirm the agent can see the browser —
ask it to open a page and tell you the title. If it can't, that's a ten-minute
fix now and a blocked workflow later.

| Workflow | Extension |
|---|---|
| **`engine-social`** | **Mandatory.** LinkedIn and X have no free posting API worth using, and their analytics live behind your login. Without it, every post is copy-paste and every number is typed in by hand |
| `engine-video` | Recommended, not required — **views, likes and comments come back without it** via `yt-dlp` on your own public URLs. What needs the login is **watch-through**, which is the number that tells you whether the hook worked |
| `engine-seo` | Nice to have — Reddit and SERP research without an API |
| `engine-outreach` | Nice to have — researching each person is browser work; the mail side goes through a connector instead |

Two things worth knowing before you install it:

- **It uses your real logged-in sessions.** That's the point, and it's also why
  the agent never logs in, never touches credentials, and asks before anything
  publishes
- **Only some workflows need it, and only for some steps.** If you'd rather not
  install it, `engine-seo` and `engine-outreach` run fine without it — and every
  workflow still records its numbers, they just get typed in rather than read

## 3. Everyone brings

- **A Gmail account** for the agent to draft in. Drafts only; nothing sends
  without you. Managed Workspace accounts sometimes block the connector — a
  personal Gmail works. Connecting it takes two minutes on the day and your
  agent walks you through it: on Claude Code it's claude.ai → Settings →
  Connectors → Gmail; on Codex it's a Gmail MCP server plus `codex mcp login`
- **Who you'd reach** — prospects, creators, investors, journalists, partners.
  Bring a list or CRM export if you have one, **in whatever format it's already
  in** — spreadsheet, CSV, a pasted block of addresses, a screenshot. Don't
  reformat it; the workflow converts it
- **Three examples** of content you'd like output to resemble — inspiration
  material for finding ideas on the day; the workflows don't ingest them
- **What you sell**, and the promise you make
- **The one number that matters** — replies, signups, demos

## 4. Your workflow

Only set up the one you're running. **Outreach is the default first one** — its
section is below, and it needs nothing but a Gmail your agent can reach. Start
somewhere else if you have a reason to; do that section instead of this one.
Links in [useful-links.md](useful-links.md).

### A. SEO and written content (`engine-seo`)

Reddit needs no account; where there's no API the agent reads the page in your
browser. Output is local markdown first.

Useful if you have them:

- **Competitor URLs** — put them in the seo workflow's `sources.json`
- **Google Search Console** — metric fetching becomes an API call
- **Ahrefs or Semrush** — only if you already pay
- **GA4 login**

**No website yet?** The workflow builds an Astro site inside its own folder (`workflows/seo/site/`).
You can use a **Cloudflare Pages** or **Railway** account to deploy. Or bring
your CMS login / GitHub access for a code-based site.

### B. Social (`engine-social`)

**The browser extension (§2b) is mandatory here** — it's how posts get drafted
into the composer and how the numbers come back. Set it up first, then be signed
in to **LinkedIn and/or X in that browser**. No API keys needed for either.
Schedulers are optional later.

**Bluesky?** Create an **app password** before the session — bsky.app →
Settings → Privacy and Security → App Passwords (format `xxxx-xxxx-xxxx-xxxx`).
Never use your account password. It goes in `shared/.env` as `BSKY_HANDLE`
and `BSKY_APP_PASSWORD`. The agent posts via the Bluesky API after you approve
each post.

**Images?** Optional both ways. Drop screenshots, charts and photos into
`social/inputs/images/` before the session and the agent can pick one per post
— no key needed for that. Only *editing* one (crop, background swap,
aspect-ratio variants) needs a key: [AI Studio](https://aistudio.google.com/apikey)
→ `GEMINI_API_KEY`, or [OpenAI](https://platform.openai.com/api-keys) →
`OPENAI_API_KEY`, in `shared/.env`. Either one, not both.

Video posting (manual / Upload Post / Buffer):
[engine-video/references/posting-options.md](../skills/engine-video/references/posting-options.md).

### C. Short-form video (`engine-video`)

Do this in advance:

| | Get it from |
|---|---|
| **ffmpeg** | `brew install ffmpeg` |
| **upload-post** | [upload-post.com](https://www.upload-post.com/) → dashboard → API key. Create a Profile, note its name, connect TikTok/Instagram/YouTube |
| **Pexels** | [pexels.com/api](https://www.pexels.com/api/) |
| **ElevenLabs** | [elevenlabs.io](https://elevenlabs.io) → Profile → API key |
| **fal.ai** *(optional)* | AI-generated clips — **check credit balance** before the session |

Also: **~10 GB free disk**, 3–5 reference videos, a few rough content ideas.
Keys go in `shared/.env` — copy `shared/.env.example` and fill it in yourself.

### Outreach (`engine-outreach`)

Covered under §3 — Gmail drafts only, connected on the day, and your list in
whatever format you already have it. Later: a domain and sending API when drafts
stop scaling — `skills/engine-outreach/references/advanced.md`.

### The improvement loop (`engine-loop`)

Not a workflow you "pick" — it rides along with whatever content workflow you
run. It reads your run data (and your browser when needed) so seo / social /
video / outreach learn and compound. Reporting stays inside Claude Code or
Codex. Optional: Slack, Discord or Telegram alerts; Apify at volume for
structured analytics.

## 5. Keys

- Paste them into `shared/.env` yourself — never into a chat window
- `.env` is gitignored. Keep it that way
- If a key leaks, rotate it
- Your agent reads `.env.example` for variable *names*, never `.env`. If a key
  is missing it should name the variable and where to get it

## 6. A home for the work

Create a `workflows/` folder on this machine:

`~/code/acme/workflows/` or `~/Desktop/acme/workflows/`

Full layout once scaffolded: [workspace.md](workspace.md).

---

## Let your agent check it

Paste this into Claude Code or Codex:

```
Read https://github.com/benyki/gtm-engine/blob/main/docs/preflight.md
and check my machine against sections 1, 2 and 2b.

Give me a PASS / FAIL list with the exact command to fix anything that fails.
For 2b, try to open a page in my browser and tell me the title — that's the
real test of whether the extension is connected.
Do not install anything without asking me first.
```

Once the starter folder is on your machine:

```bash
python3 <repo>/skills/engine-setup/scripts/doctor.py
```

Run it again after setup — it also checks workspace, config, and keys.
