# Onboarding a new user

This is the script `engine-setup` follows the first time someone installs
gtm-engine. It is written for the agent, not the user: read it top to bottom
before you touch their disk.

Target state, written against the architecture in
[`architecture-v2.md`](architecture-v2.md). Terminology here is **engine**, not
workflow: an engine is one self-contained growth channel folder (its own
config, templates, inputs, runs, reports).

Two rules over everything below:

- **Nothing is a required-choices screen.** Every question has a recommended
  default. Say which default you took and keep moving. A beginner should be
  able to answer "yes" three times and be done.
- **Say what you are about to write, before you write it.** Every path, once,
  in plain text.

---

## Step 0. Say what is about to happen

Before creating anything, tell them, in this order:

> I'm going to create a folder at `~/gtm`. That is the home for everything
> shared between your growth engines: your brand voice, your accounts, your
> API keys, your assets, and what previous runs taught. It is yours. The engine
> code lives somewhere else (`~/.gtm-engine`) and gets overwritten by updates,
> so nothing in `~/gtm` can ever be clobbered by a `git pull`.

Then confirm the two things that come with it:

- `~/.gtm-engine` is the clone: read-only for day to day work, updated with
  `git pull`.
- `~/.agents/skills/` is where the skills get copied so Claude Code, Codex and
  Cursor can all find them.

If `~/gtm` already exists with a `shared/` inside it, this is not a first
install. Skip to "Adding an engine later".

---

## Step 1. Offer the first engines

Ask one question, with the answer already suggested:

> Do you want me to set up the four default engines (seo, social, video,
> outreach)? Recommended if you are new to this, they cost nothing sitting
> there unused and you can run them one at a time.

- **New to AI agents, or unsure: scaffold all four.** No further questions.
  Having the folder already there means picking a channel later is a decision,
  not an install step.
- **Experienced, or they name one channel: scaffold what they named.** Adding
  more later is one command.

Do not ask which one they will run first as a blocking question. State the
recommendation instead: start with outreach unless they have a reason not to,
because the loop only has something to say once there are runs on the board.

---

## Step 2. Ask where the engines live

This is the one question worth asking properly, because moving engines later
means re-registering paths. Give them the picture first:

> Each engine can live in a different place. If you have several products or
> brands, I recommend one `engines/` folder inside each project, holding that
> project's engines. Everything shared still lives in `~/gtm`, so your brand
> voice and your keys are written once.
>
> By default I'll create `engines/` in the folder we are in right now
> (`<cwd>`).

Then offer the alternative, explicitly:

> If you would rather keep every engine for every project in one place, that
> works too: they all go in `~/gtm/engines/`. In that case I recommend naming
> each folder `engine-<type>-<project>`, for example
> `engine-outreach-acme/`, so it is obvious at a glance which project a folder
> belongs to.

Three answers, three behaviours:

| They say | Where engines go | How folders are named |
|---|---|---|
| nothing / "the default" | `<cwd>/engines/` | `<type>/`, for example `outreach/` |
| "keep them all together" | `~/gtm/engines/` | `engine-<type>-<project>/` |
| a path of their own | that path | ask for a project name, then `engine-<type>-<project>/` |

Override the cwd default without asking when the current directory is a bad
home for data: the home directory itself, `~/Downloads`, a temp directory, or
the `~/.gtm-engine` clone. In those cases use `~/gtm/engines/` and say why in
one line.

If the cwd is a git repo, say so and ask whether the engine folder should be
committed or gitignored. Recommend committing it when the repo is theirs and
private, gitignoring it when the repo is shared or public, because runs and
CRM rows are their data and often personal.

If `engines/` already exists in the cwd and is not ours (a Rails project keeps
mountable engines there), do not merge into it. Say what you found and use
`gtm-engines/` instead.

---

## Step 3. Scaffold, then say what exists

Create, in this order:

1. `~/gtm/` with `shared/` (brand, channels, `.env.example`, assets, docs,
   insights), the docs, `AGENTS.md`, `CLAUDE.md`, and `engines.json` (the
   registry of where every engine lives).
2. Each engine folder at the location from step 2, each one registered in
   `~/gtm/engines.json`.
3. The skills for the engine types they scaffolded, into `~/.agents/skills/`,
   symlinked into whichever agents are installed.

Then print the tree you actually created, with real paths. Not a diagram of
the general case: the folders that now exist on their machine.

---

## Step 4. Fill in the brand, once

`~/gtm/shared/brand.md` is the file every engine reads before it writes a word.
Interview them for it now, briefly: who they are, who they sell to, what they
will never claim. Thin answers are fine and better than invented ones. Say
plainly that this file is shared by every engine in every project, and that a
project needing a different voice gets an override in its own engine folder.

Then point at `~/gtm/shared/.env.example`: copy it to `.env` and fill in only
the keys for the channels they are actually running. Never read `.env` back.

---

## Step 5. Hand over

End with what they can do next, and which of it you can start right now:

```
Next:
  · run the outreach engine on a first list of 10 people, I can do this now
  · set up the daily metric job and the weekly report, I can do this now
  · you: paste your API keys into ~/gtm/shared/.env for the channels you want live
```

---

## Adding an engine later

Same two questions, much shorter: which type, and where it goes (default: an
`engines/` folder in the project they are in). Register it in
`~/gtm/engines.json`, install the skill for its type if it is missing, and stop.
Never rescaffold `~/gtm/shared/`: it already exists and it is theirs.

## What onboarding never does

- Never write outside `~/gtm`, `~/.gtm-engine`, `~/.agents/skills`, the agent
  skill folders, `~/Desktop` symlinks, and the engine folder they chose.
- Never overwrite a file that already exists. Merging means filling gaps.
- Never send, post or publish anything as part of setup.
- Never read the values in `.env`, only the key names.
