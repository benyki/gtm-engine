# Onboarding a new user

This is the script `engine-setup` follows the first time someone installs
gtm-engine. It is written for the agent, not the user: read it top to bottom
before you touch their disk.

An **engine** is one self-contained growth channel folder: its own config,
templates, inputs, runs and reports. The design behind the layout is
[`architecture-v2.md`](architecture-v2.md); what changed from the older shape,
and what to do when you meet one, is [`changelog.md`](changelog.md).

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

**Ask this one properly.** It is the only question in setup whose answer is
awkward to change later, because moving an engine means re-registering its
path. Ask it as a yes-or-something-else, with the default named:

> By default your engines go in `~/gtm/engines/`, right next to everything they
> share. Is that what you want, or would you rather pick a folder yourself?

Then, in the same message, say what picking a folder is for, so they can answer
without knowing the system yet:

> If you have several products or brands, I'd suggest an `engines/` folder
> inside each project, holding that project's engines. Everything shared still
> lives in `~/gtm`, so your brand voice and your keys are only written once.
> We're in `<cwd>` right now, so that would be `<cwd>/engines/`.

Three answers, three behaviours:

| They say | Where engines go | How folders are named |
|---|---|---|
| nothing / "the default" | `~/gtm/engines/` | `engine-<type>-<project>/` when you know the project, else `<type>/` |
| "keep them with the project" | `<cwd>/engines/` | `<type>/`, for example `outreach/` |
| a path of their own | that path | ask for a project name, then `engine-<type>-<project>/` |

Two things you settle without asking:

- **Never scaffold into a bad home for data.** If the cwd is the home directory
  itself, `~/Downloads`, a temp directory, or the `~/.gtm-engine` clone, use
  `~/gtm/engines/` and say why in one line.
- **Engine names are unique across every project**, because `engines.json` is
  keyed on them. Two engines cannot both be called `outreach`. The scaffolder
  refuses rather than overwrite, so pass `--project <name>` and let it name the
  folder `engine-<type>-<project>`.

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
   `~/gtm/engines.json`. An engine that lives away from the home also gets a
   short `AGENTS.md` pointing back at `~/gtm`, so an agent opening that project
   alone still finds the house rules.
3. The skills for the engine types they scaffolded, into `~/.agents/skills/`,
   symlinked into whichever agents are installed.

```bash
# the default
python3 ~/.gtm-engine/skills/engine-setup/scripts/scaffold.py --project acme

# engines kept with the project
python3 ~/.gtm-engine/skills/engine-setup/scripts/scaffold.py \
  --engine all --at ./engines --project acme

~/.gtm-engine/skills/engine-setup/scripts/install_skills.sh --home ~/gtm
```

Then print the tree you actually created, with real paths. Not a diagram of
the general case: the folders that now exist on their machine.

**If they are not on Claude Code or Codex** (openclaw, Cursor, Hermes,
Antigravity, or any other coding-agent framework), fetch that harness's current
documentation first, then read through the installed skills and the `~/gtm`
folder and adapt every Claude Code or Codex reference to their environment:
where skills live, how scheduled tasks are defined, which instruction file the
agent reads. Do it now, while the tree is fresh, rather than leaving them to
hit each mismatch on their own.

---

## Step 4. Fill in the brand, once

`~/gtm/shared/brand.md` is the file every engine reads before it writes a word.
Interview them for it now, briefly: who they are, who they sell to, what they
will never claim. Thin answers are fine and better than invented ones. Say
plainly that this file is shared by every engine in every project, and that a
project needing a different voice gets an override in its own engine folder.

Then point at `~/gtm/shared/.env.example`: copy it to `.env` and fill in only
the keys for the channels they are actually running. Never read `.env` back.

Say what this file becomes: it is read before anything is written, and it grows
with the business. Every engine, every session, reads three things before it
produces anything, in this order:

1. `shared/brand.md`: voice, audience, banned claims. If it's thin, say so
   rather than guessing at a voice
2. `shared/insights.md`: what previous runs taught, across every engine
3. That engine's `reports/latest.json` and its `inputs/best/`: what worked
   there, and what the user's own good work looks like

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

Same two questions, much shorter: which type, and where it goes (default:
`~/gtm/engines/`, or the project's own `engines/` if that is where their other
engines for this project are). `scaffold.py --engine <name> --at <path>
--project <name>` registers it and fills the gaps; install the skill for its
type if it is missing, and stop. Never rescaffold `~/gtm/shared/`: it already
exists and it is theirs. If this is the engine that puts them in a second
location, do the one thing below as well.

## Only if the engines end up spread out

Everything above assumes one location. **If, and only if, this user's engines
live in more than one place** (some in `~/gtm/engines/` and some in a project,
or engines in two different projects), add this section to `~/gtm/AGENTS.md`,
and to the `AGENTS.md` of each engine outside the home:

```markdown
## Moving an engine

Engines here live in more than one place, and `~/gtm/engines.json` is the only
map of where. If you create, move, rename or delete an engine folder, fix its
entry in the same breath (`registry.py add|mv|rm`, or `doctor.py --fix`), or it
becomes invisible: absent from the weekly report, unreadable by the other
engines, unknown to the next agent.
```

One location means nothing to keep in sync, so don't write it. Add it the day
they scaffold a second location, not before.

## What onboarding never does

- Never write outside `~/gtm`, `~/.gtm-engine`, `~/.agents/skills`, the agent
  skill folders, `~/Desktop` symlinks, and the engine folder they chose.
- Never overwrite a file that already exists. Merging means filling gaps.
- Never send, post or publish anything as part of setup.
- Never read the values in `.env`, only the key names.
