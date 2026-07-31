# Workflow starters

What `scaffold_workspace.py` copies to create a workflow folder. Two kinds live
here, and only one of them is a workflow type.

## `outreach/` `seo/` `social/` `video/` — the type starters

One per shipped workflow type. A folder name here is a **type**: it's what
`--workflow seo` copies, what `workflows.py list` reports, and what maps to the
`engine-<type>` skill. Adding a folder here adds a scaffoldable type.

Each holds only what makes that type different — its `workflow.json`,
`experiments.json`, `sources.json`, its starting `templates/` and its own
`inputs/` subfolders.

## `_every-workflow/` — not a type

The shell **every** workflow folder gets, whatever its type:

```
runs/index.csv          the spine — one row per thing that workflow made
inputs/queue/           what engine-loop writes next week's ideas into
reports/                weekly report + latest.json
templates/losers/       where a losing template goes; runs never read it
experiments.json        empty starter
sources.json            empty starter
```

The scaffold copies the type starter **first**, then merges this on top without
overwriting anything — so a starter's own `experiments.json` and `sources.json`
win and this only fills the gaps. For a custom workflow with no starter
(`--workflow newsletter`), it's the whole body plus a generated `workflow.json`.

The leading `_` is what keeps it out of discovery: `workflows.py` skips
`_`-prefixed folders, and `--workflow _every-workflow` is rejected by the name
rule. No workspace ever contains a folder called `_every-workflow/`.

**Which one to edit:** something every workflow should have goes in
`_every-workflow/`. Something only one type needs goes in that type's starter.
