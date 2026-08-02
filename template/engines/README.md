# Engine starters

What `scaffold.py` copies to create a engine folder. Two kinds live
here, and only one of them is a engine type.

## `outreach/` `seo/` `social/` `video/` : the type starters

One per shipped engine type. A folder name here is a **type**: it's what
`--engine seo` copies, what `engines.py list` reports, and what maps to the
`engine-<type>` skill. Adding a folder here adds a scaffoldable type.

Each holds only what makes that type different : its `engine.json`,
`experiments.json`, `sources.json`, its starting `templates/` and its own
`inputs/` subfolders.

## `_every-engine/` : not a type

The shell **every** engine folder gets, whatever its type:

```
runs/index.csv          the spine : one row per thing that engine made
inputs/queue/           what engine-loop writes next week's ideas into
reports/                weekly report + latest.json
templates/losers/       where a losing template goes; runs never read it
experiments.json        empty starter
sources.json            empty starter
```

The scaffold copies the type starter **first**, then merges this on top without
overwriting anything : so a starter's own `experiments.json` and `sources.json`
win and this only fills the gaps. For a custom engine with no starter
(`--engine newsletter`), it's the whole body plus a generated `engine.json`.

The leading `_` is what keeps it out of discovery: `engines.py` skips
`_`-prefixed folders, and `--engine _every-engine` is rejected by the name
rule. No home ever contains a folder called `_every-engine/`.

**Which one to edit:** something every engine should have goes in
`_every-engine/`. Something only one type needs goes in that type's starter.
