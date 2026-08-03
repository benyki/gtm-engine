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
which. **Never reach into another engine's folder to change something.**
Reading a sibling's `reports/latest.json` is fine and encouraged; writing to it
is not. `engine.json` gives the `type`, which says which skill runs the folder
(`social` runs `engine-social`).

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

The boundaries at the bottom of this file are the exception; those don't bend.
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

## Before you produce anything

1. `shared/brand.md`: voice, audience, banned claims. If it's thin, say so
   rather than guessing at a voice
2. `shared/insights.md`: what previous runs taught, across every engine
3. That engine's `reports/latest.json` and its `inputs/best/`: what worked
   there, and what the user's own good work looks like

## Everything runs locally

gtm-engine is designed to run on this machine. Every task and every scheduled
task runs here, because that is where the files, the keys and the logged-in
browser are. If something is running in the cloud (a remote agent session, a
hosted runner, a cloud scheduler), say so and suggest moving it local, unless
there is a good reason it has to be remote.

## Schedulers are the agent's own scheduled tasks

Every recurring job here, the metric fetches, the weekly report, the drafting
runs, is a **native scheduled task in the agent itself**: Claude Code's
scheduled tasks, or the Codex equivalent. Never `cron`, never `launchd`, never
a shell script on a timer.

They need a model, a browser and judgement, which an OS-level job doesn't have.
Each run also starts with no memory of this conversation, so the prompt has to
stand alone: name the engine, its full path, and what to do.

## Boundaries that don't move

- **Never invent a fact about a person**, and never generate an image that
  functions as proof (a metrics screenshot, a revenue chart, a testimonial)
- **Never start an A/B test that isn't already live.** Experiments ship paused
  on purpose: one template the user is happy with comes first

Each skill states the rest of its own rules; those override nothing here.
