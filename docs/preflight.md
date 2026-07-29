# Preflight — is this machine ready?

Ten minutes. Run through it before you install anything, or paste the block at
the bottom into your agent and let it check for you.

---

## 1. Machine

| Check | How | If not |
|---|---|---|
| **Apple Silicon Mac** (M1 or newer) |  → About This Mac → "Chip" says Apple M-something | Intel works for text workflows; video rendering will be slow. Linux mostly works. Windows needs adapting — ask us |
| **macOS 13+** | same screen | Update first — it's a long download |
| **You can install apps** | try installing anything | Managed work laptops often block this. You need admin access. Sort it before you start |
| **10 GB free disk** | Storage settings | Only strictly needed for the video pathway |
| **Developer tools** | `xcode-select --install` in Terminal | 5–10 minutes. This is what gives you `git` |
| **Python 3.9+** | `python3 --version` | Already on macOS. No packages needed — the scripts use the standard library only |

Bring your charger.

## 2. An AI coding agent

Pick one and check you can **sign in** before you start. This is the thing most
likely to cost you a morning.

- **Claude Code** — Claude Desktop, sign in, toggle to the **Code** tab (top left). Needs Claude Pro or higher
- **Codex** — ChatGPT desktop, sign in, toggle to **Codex** (top left). ChatGPT Plus or higher recommended

Prefer the terminal? Install commands are in [useful-links.md](useful-links.md).

**Then check it actually works.** Open any folder and ask it:

```
create a file called hello.txt with the word hello in it
```

If the file appears, you're ready. If it asks for permissions, approve them.

## 3. Everyone

Whatever pathway you pick, you need these:

- **A Gmail account** you're happy for an agent to draft in — everyone builds
  the outreach workflow. No Google Cloud project, no API key, no OAuth consent
  screen. Drafts only; nothing sends without you reviewing it
- **A rough idea of who you'd reach** — sales prospects if you're B2B, creators
  if you're B2C, or investors, journalists, partners. Bring a list or CRM export
  if you have one
- **Three examples** of content you'd like your agent's output to resemble,
  yours or anyone's. These become the templates, so they matter
- **What you sell**, and the promise you make
- **The one number that matters** — replies, signups, demos. The loop optimises
  whatever you name, so name it honestly

## 4. Your pathway

Only set up the one you're running. Full detail in
[prerequisites.md](prerequisites.md); links in [useful-links.md](useful-links.md).

**A. SEO and written content** — nothing technical. Sources are Reddit and
Google Trends via RSS, no accounts. Everything is generated locally as markdown
first. To publish live: your CMS login (plus API key if you have one), or
GitHub access for a code-based site, or nothing at all — we can build you an
Astro site on Cloudflare Pages. *Recommended:* be able to log in to GA4, Search
Console, Ahrefs or Semrush. That's what makes the improvement loop useful.

**B. Social** — same engine as SEO, publishing to social instead of a blog. Be
signed in to **LinkedIn and/or X in your browser**; the agent posts through the
browser. No API keys — neither platform offers a usable posting API. Instagram
in your plan? You'll want upload-post too, below.

**C. Short-form video** — the heaviest setup, so do it in advance. Four keys,
all free or free to start, roughly five minutes each:

| Key | Why | Notes |
|---|---|---|
| **upload-post** | publishing | ~10 uploads/month free. Create a Profile and note its name. Connect TikTok/Instagram/YouTube inside it |
| **Pexels** | B-roll fallback | free, instant |
| **ElevenLabs** | voiceover | ~10 min free, no commercial licence on the free tier |
| **fal.ai** | AI-generated clips | pay-per-use, no free tier. **Check your credit balance** — empty means failed requests |

Also: `brew install ffmpeg`, 3–5 reference videos, and a few rough content ideas.

**Everyone: the improvement loop** — nothing extra. Reporting stays inside
Claude Code or Codex. Optionally we can wire alerts to Slack, Discord or
Telegram; just have the app installed.

**Keys:** treat them like passwords. Don't paste them into a chat window,
Slack, or anything you'd commit to GitHub. A note on your own machine is fine
until we show you where they live.

## 5. A home for the work

Create a `workflows/` folder on this machine. That's where drafts, outputs and
state live — the place the engine actually runs.

Unsure where? Inside your company or project folder is great:
`~/code/acme/workflows/` or `~/Desktop/acme/workflows/`.

---

## Let your agent check it

Paste this into Claude Code or Codex:

```
Read https://github.com/benyki/gtm-engine/blob/main/docs/preflight.md
and check my machine against sections 1 and 2.

Give me a PASS / FAIL list with the exact command to fix anything that fails.
Do not install anything without asking me first.
```

Once the starter folder is on your machine, the same check is a script:

```bash
python3 ~/code/gtm-engine/skills/engine-setup/scripts/doctor.py
```

Run it again after setup — it also checks your workspace, your config and
whether your keys are set.
