# Working in gtm-engine

`skills/` holds the `engine-*` skills agents load, `template/` holds what gets
scaffolded into a user's home (`template/home` becomes `~/gtm`) and into each
engine folder (`template/engines`), `docs/` is the reading material for both,
`interfaces/` holds builders for things that sit on top (a local dashboard, for
instance), and `install.sh` wires it together.

Nothing a user owns lives here: their brand, keys, runs and numbers are in
`~/gtm` and in their engine folders, and `git pull` overwrites this clone.
Changing something here changes it for everybody on the next pull.

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
irreversible action or real damage, keep it explicit and absolute. The current
set: nothing sends or publishes without the user's yes, no invented facts about
a person and no invented metrics, no images that function as proof, no
contacting someone twice or after a no, `.env` values are never read, and a
losing template is retired to `losers/` rather than deleted.

## What ships to users

`template/home/AGENTS.md` is the file every agent reads inside a user's `~/gtm`.
It is the one place house rules reach people who never open this repo, so
changes there carry further than changes anywhere else.

Scripts in `skills/*/scripts/` are plain stdlib Python and bash: they run on the
user's machine, often unattended, and a traceback there lands in someone's
scheduled task. Worth running them against a scratch home (`GTM_HOME=/tmp/x`)
before pushing.
