# Working in this workspace

This folder is **data, not logic**. It holds one brand's growth work: the brand
config, the inputs, every run and every number. The logic lives in the
`engine-*` skills (`skills/` here is a symlink to `~/.agents/skills`) and in the
gtm-engine clone. Skills get rewritten by `git pull`; nothing in here does.

One folder per workflow, and each is self-contained — its own `workflow.json`,
`experiments.json`, `sources.json`, `templates/`, `inputs/`, `runs/`,
`reports/`. **Never reach into another workflow's folder to change something.**
Reading a sibling's `reports/latest.json` is fine and encouraged; writing to it
is not. `workflow.json` → `type` says which skill runs a folder (`social` →
`engine-social`).

## Always end with next steps

**Every message that finishes a piece of work ends with a short list of possible
next steps.** Say plainly which ones **you can do right now** and offer to start
them; the point is that the user should never have to work out what to ask for
next.

```
Next:
  · draft the four remaining posts from inputs/queue/ — I can do this now
  · read Tuesday's post numbers off LinkedIn and record them — 72h window clears tomorrow
  · you: paste the Bluesky app password into shared/.env if you want that channel live
```

Offer, don't act: anything that leaves this machine — a post, an email, a
purchase, a push — waits for an explicit yes, every time. If there is genuinely
nothing to do next, say that instead of inventing filler.

## Before you produce anything

1. `shared/brand.md` — voice, audience, banned claims. If it's thin, say so
   rather than guessing at a voice
2. `shared/insights.md` — what previous runs taught, across workflows
3. That workflow's `reports/latest.json` and its `inputs/best/` — what worked
   here, and what the user's own good work looks like

## Every piece made gets a run row

```bash
python3 skills/engine-loop/scripts/runlog.py new --workflow <name> --channel <channel>
```

One run per artifact, logged before it ships, with the template it used. A piece
that isn't in `runs/index.csv` never gets a number, never joins an A/B verdict,
and is invisible to the weekly report. Record the publish (`runlog.py publish`)
and the number when the window has passed (`runlog.py metric`).

## Schedulers are the agent's own scheduled tasks

Every recurring job in this workspace — the metric fetches, the weekly report,
the drafting runs — is a **native scheduled task in the agent itself**: Claude
Code's scheduled tasks, or the Codex equivalent. Never `cron`, never `launchd`,
never a shell script on a timer.

They need a model, a browser and judgement, which an OS-level job doesn't have.
Each run also starts with no memory of this conversation, so the prompt has to
stand alone: name the workflow, the workspace path, and what to do.

## Boundaries that don't move

- **Never send email.** Outreach ends at a draft in the user's own mailbox
- **Never post or publish without an explicit yes** — per post, not per session
- **Never read `shared/.env`.** Variable *names* come from `.env.example`; the
  user pastes values in themselves, never into a chat window
- **Never invent a fact about a person**, and never generate an image that
  functions as proof (a metrics screenshot, a revenue chart, a testimonial)
- **Never start an A/B test that isn't already live.** Experiments ship paused
  on purpose — one template the user is happy with comes first

Each skill states the rest of its own rules; those override nothing here.
