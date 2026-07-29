# Preflight — is this machine ready?

Ten minutes. Run through it before you install anything, or paste the block at
the bottom into your agent and let it check for you.

Only set up the pathway you're actually running. Downloads and signup links:
[useful-links.md](useful-links.md).

---

## 1. Machine

| Check | How | If not |
|---|---|---|
| **Apple Silicon Mac** (M1 or newer) | → About This Mac → "Chip" says Apple M-something | Intel works for text workflows; video rendering will be slow. Linux mostly works. Windows needs adapting — ask us |
| **macOS 13+** | same screen | Update first — it's a long download |
| **You can install apps** | try installing anything | Managed work laptops often block this. You need admin access. Sort it before you start |
| **10 GB free disk** | Storage settings | Only needed for the video pathway |
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

## 3. Everyone brings

- **A Gmail account** for the agent to draft in. Drafts only; nothing sends
  without you. Managed Workspace accounts sometimes block the connector — a
  personal Gmail works
- **Who you'd reach** — prospects, creators, investors, journalists, partners.
  Bring a list or CRM export if you have one
- **Three examples** of content you'd like output to resemble
- **What you sell**, and the promise you make
- **The one number that matters** — replies, signups, demos

## 4. Your pathway

Only set up the one you're running. Links in [useful-links.md](useful-links.md).

### A. SEO and written content (`engine-seo`)

Reddit needs no account; where there's no API the agent reads the page in your
browser. Output is local markdown first.

Useful if you have them:

- **Competitor URLs** — put them in `config/sources.json`
- **Google Search Console** — metric fetching becomes an API call
- **Ahrefs or Semrush** — only if you already pay
- **GA4 login**

**No website yet?** The workflow builds an Astro site in `workflows/site/`.
You'll need a **Cloudflare Pages** or **Railway** account to deploy. Or bring
your CMS login / GitHub access for a code-based site.

### B. Social (`engine-linkedin`)

Be signed in to **LinkedIn and/or X in your browser**. Manual posting is the
default. No API keys.

Instagram? You'll want Upload Post (see video below). Schedulers:
[posting-options.md](posting-options.md).

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
Keys go in `config/.env` — copy `config/.env.example` and fill it in yourself.

### Outreach (`engine-outreach`)

Covered under §3 — Gmail drafts only. Later: a domain and sending API when
drafts stop scaling — `skills/engine-outreach/references/advanced.md`.

### The improvement loop (`engine-loop`)

Reads your run data and your browser. Reporting stays inside Claude Code or
Codex. Optional: Slack, Discord or Telegram alerts; Apify at volume for
structured analytics.

## 5. Keys

- Paste them into `config/.env` yourself — never into a chat window
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
and check my machine against sections 1 and 2.

Give me a PASS / FAIL list with the exact command to fix anything that fails.
Do not install anything without asking me first.
```

Once the starter folder is on your machine:

```bash
python3 ~/code/gtm-engine/skills/engine-setup/scripts/doctor.py
```

Run it again after setup — it also checks workspace, config, and keys.
