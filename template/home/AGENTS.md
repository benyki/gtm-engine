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

The boundaries at the bottom of this file are the exception; those don't bend.
Everything else is negotiable, and the user is who negotiates it.

## Write for agents, not machines

Everything in this repo and in the engine folders is read and used by capable
agents. Write policies, modular instructions and templates, not rigid systems,
and don't over-specify what an agent can infer from context. Prefer intent,
boundaries and defaults over step-by-step procedure: leave room for judgment,
suggest sensible defaults, and involve the user whenever a decision depends on
their goals, preferences or context. Explain why something is recommended
rather than promoting the recommendation to a rule.

| Instead of | Write |
|---|---|
| Never do X | Avoid X unless the situation calls for it |
| Do these in order | The order below is the default one |
| Confirm the paths in steps 2 and 3 | The paths in steps 2 and 3 are worth confirming, because… |
| You need X | X is useful when… |
| Use X | X is the default |
| You must X | X is expected when relevant |
| Do not X | Avoid X unless the situation calls for it |

**Safety rules stay hard.** None of the above applies to safety, damage control
or destructive actions. When a rule exists to prevent data loss, an
irreversible action or real damage, keep it explicit and absolute.

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

## Boundaries that don't move

- **Never invent a fact about a person**, and never generate an image that
  functions as proof (a metrics screenshot, a revenue chart, a testimonial)
- **Never delete a template.** Losers move to `losers/`: it is the only record
  of what didn't work, and deleting it can't be undone

Each skill states the rest of its own rules; those override nothing here.
