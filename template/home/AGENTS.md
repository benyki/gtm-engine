# Working in this home

This folder is **data, not logic**. It holds everything shared between your
engines: the brand config, the accounts, the keys, the assets, and what every
run has taught. The logic lives in the `engine-*` skills (`skills/` here is a
symlink to `~/.agents/skills`) and in the gtm-engine clone at `~/.gtm-engine`.
Skills get rewritten by `git pull`; nothing in here does.

**An engine is one self-contained folder** with its own `engine.json`,
`experiments.json`, `sources.json`, `templates/`, `inputs/`, `runs/`,
`reports/`. Engines can live anywhere: in `engines/` here, or in an `engines/`
folder inside the project they grow, and `engines.json` here records which is
which. **Read other engines freely; write into the one you're running.** A
sibling's `reports/latest.json` is worth reading. `engine.json` gives the
`type`, which says which skill runs the folder (`social` runs
`engine-social`).

## Stay flexible

**The goal is engines that adapt to the user, not users who adapt to
engines.** Everything written down here and in the skills, the folder shapes,
the column headers, the step order, the fields an engine asks for, is a
default that worked for someone else. When it doesn't fit the person in front
of you, bend it and carry on. Read the instructions for their intent, not as a
checklist to enforce.

- **Take what they have, in the shape they have it.** Never send someone away to
  reformat a file, fill in a missing field, rename a column or re-export a
  spreadsheet before anything can happen: converting it is your job
- **A missing input is a note, not a stop.** Do the part you can do now, say in
  one line what was missing and what it cost, and offer the fix
- **A step that doesn't apply gets skipped**, out loud, so they can say
  otherwise. Skipping it silently is the failure, not skipping it
- **Their way beats the default.** If they already have a template, a tool or a
  process that works, fit around it rather than migrating them onto ours
- **Nothing here is a required-choices screen.** Take the sensible default, say
  which one you took, keep moving
- **A/B tests are worth more once there's one template the user is happy with.**
  Experiments ship paused for that reason

The guardrails at the bottom of this file are the exception; those don't bend.
Everything else is negotiable, and the user is who negotiates it.

## Always end with next steps

**Every message that finishes a piece of work ends with a short list of possible
next steps.** Say plainly which ones **you can do right now** and offer to start
them; the point is that the user should never have to work out what to ask for
next.

```
Next:
  · draft the four remaining posts from inputs/queue/, I can do this now
  · read Tuesday's post numbers off LinkedIn and record them, the 72h window clears tomorrow
  · you: paste the Bluesky app password into shared/.env if you want that channel live
```

## Keep brand.md and insights.md growing

`shared/brand.md` holds the guidelines every engine writes from: whenever the
user brings new material, or you find something current about the brand, the
product or the business, add it there and tell them what you added.
`shared/insights.md` holds the clues: when the user tells you something they
have learned about their market or their audience, write it down as a line.

## Everything runs locally

gtm-engine is designed to run on this machine. Every task and every scheduled
task runs here, because that is where the files, the keys and the logged-in
browser are. If something is running in the cloud (a remote agent session, a
hosted runner, a cloud scheduler), say so and suggest moving it local, unless
there is a good reason it has to be remote.

## Schedulers are the agent's own scheduled tasks

Every recurring job here is defined in the **native scheduled-task format of
the harness you are running in**: Claude Code's scheduled tasks, the Codex
equivalent, or your framework's own. Not `cron`, not `launchd`, not a shell
script on a timer, unless something genuinely needs a deterministic job or the
user asks for one.

## Guardrails

Everything else here is a default you can bend. These are not: each one exists
because getting it wrong is irreversible, damages the user's reputation, or
poisons data they can't reconstruct.

- **Nothing sends, posts or publishes without an explicit yes**, per piece, not
  per session
- **Never invent a fact about a person, or a metric.** Thin research is
  something to say out loud; a made-up detail in a cold email or a guessed
  number in the spine can't be taken back
- **Never generate an image that functions as proof**: a metrics screenshot, a
  revenue chart, a testimonial
- **Never contact someone twice, and honour a no permanently.** Check the CRM
  before every draft
- **Never delete a template.** Losers move to `losers/`: it is the only record
  of what didn't work, and the deletion can't be undone
- **Never read the values in `shared/.env`.** Key names come from
  `.env.example`
- **Never overwrite the user's own work.** Runs, CRM rows, templates and
  `brand.md` are theirs; add to them, and ask before replacing anything

Each skill states the rest of its own rules; those override nothing here.

## Write for agents, not machines

Anything you write in here is read by capable agents: this file, `brand.md`, an
engine's templates and config. So write policies and defaults, not rigid
systems, and don't over-specify what an agent can infer from context. Prefer
intent, boundaries and defaults over step-by-step procedure, involve the user
whenever a decision depends on their goals
or context, and explain why something is recommended rather than promoting it
to a rule.

| Instead of | Write |
|---|---|
| Never do X | Avoid X unless the situation calls for it |
| Do these in order | The order below is the default one |
| You need X | X is useful when… |
| Use X | X is the default |
| You must X | X is expected when relevant |
| Do not X | Avoid X unless the situation calls for it |

The guardrails above are the exception: those stay explicit and absolute.
