# A/B testing templates

The rules below come from a cold-outreach system that has been running these tests for months. Each one exists because breaking it produced a wrong answer that took weeks to notice.

They apply to **any workflow built from a template plus config** — outreach emails, video hooks, article openings, LinkedIn posts. If the output is rendered from a template, it can be tested this way.

---

## R1 — A variant is a whole template file

`<workflow>/templates/<base>-<variant>.txt`. The file is the unit, even when the change inside it is one line. That way what was actually sent is always recoverable, and a diff between two arms is a real diff rather than a config lookup.

**How big the difference should be is not fixed — it shrinks as you learn.**

**Early on, swing wide.** You know nothing, so test propositions that are genuinely different. In the system these rules come from, one arm offered free access in exchange for feedback and the other offered a 50/50 revenue split — two different deals. The reply rates weren't close, and that gap was the most useful thing the test ever produced.

**As winners accumulate, the changes get subtler.** You keep what works, so each new arm varies less: the same offer with a different opening line, the same structure with a different proof point, the same ask phrased shorter. This is normal and it's the sign the system is working. Most of your tests, most of the time, will look small.

**Then deliberately swing wide again, occasionally.** Refinement converges on a local maximum and sits there. Every so often — every fifth or sixth experiment, or whenever results have gone flat — put up a genuinely new proposition against the reigning winner. Most of these lose. The one that doesn't resets the ceiling, and it's the only way to find a ceiling you didn't already know about.

**The practical consequence:** subtle differences need more runs to separate than dramatic ones. Raise `min_runs_per_arm` as your variants converge. A 1.2× win ratio is easy to hit when the offers are different and very hard when only the first sentence changed — if you leave the thresholds where they were in week one, you'll start declaring winners out of noise.

## R2 — Rotation is a rule, not a preference

Arms are assigned least-used-first and written down immediately, so the split stays balanced without anyone managing it.

Whether a script or the agent does the rotation matters less than what's forbidden: **nobody picks a favourite.** An agent that keeps reaching for the template it likes isn't running a test, it's confirming a hunch — and it will produce a clean-looking table that means nothing.

`scripts/assign_arm.py` is the only thing that assigns an arm. Usage is counted from `runs/index.csv` — the spine — within the experiment's cohort. The CRM is never a usage ledger: its job is stickiness (R3), and every draft is already a run.

## R3 — Assignment is sticky

Once an entity is in an arm it stays there, including on every follow-up. Someone who got the partnership pitch gets partnership-flavoured follow-ups.

Switch someone mid-sequence and you no longer know which message produced the reply. Pass `--entity` on every call so the lookup happens.

## R4 — A missing template never blocks the run

The original implementation hard-errored when a variant's file was absent. That's too strict: a run that stops because a file is missing has cost you a day to protect a statistic.

Instead:

- Rotate across whatever exists in the workflow's active folder
- If the assigned arm has no template, **write it** from the hypothesis in `experiments.json`, then use it
- Record the template you **actually rendered**, never the one that was requested

That last line is the part that matters. The real failure was never the missing file — it was mislabelling. Rows tagged `partner` that actually received the default content leave the attribution quietly wrong for weeks, with nothing in any log to show for it. Write the missing template, record what shipped, and you never have to stop.

The same spirit applies when no experiment is live at all: `assign_arm.py` doesn't guess a filename, it reports what's actually in the workflow's active folder — one template to use, a list to choose from (`action: choose_template` — nothing is being tested, so pick what fits), or `write_template` when the folder is empty. Whatever you decide, record the file you actually rendered.

## R5 — `default` and `none` mean the base template

So a stored value can be passed straight through without special-casing every call site.

## R6 — The cohort decides; all-time is context

Every row that predates an experiment sits in the default arm. Include those and the default looks enormous and settled before the test has said anything.

`score_arms.py` reports the cohort as the decision input and all-time separately, labelled as context. Never quote the all-time number as a verdict.

---

## When is it decided?

Both conditions, or it stays open:

- every arm has at least `min_runs_per_arm` **measured** runs — runs with a metric, not runs that merely exist
- the leader beats the runner-up by at least `win_ratio` (1.2× by default)

Otherwise: `undecided — partner 9/15`. That's a real answer and reporting it is not a failure. Declaring winners early is how you end up confident about something untrue.

With the volumes most people are working at, this is a judgement rule, not statistical significance. It's deliberately a low bar for *noticing* and a high bar for *acting*.

### Which number the arms are compared on

Two optional per-experiment fields shape the comparison:

- **`direction`** — `"up"` (default) or `"down"`. Most metrics are more-is-better; cost per lead, unsubscribe rate and churn are not. With `"down"`, the lower arm leads and the win ratio is computed the right way round.
- **`aggregate`** — `"mean"` (default) or `"median"`. Social metrics are heavy-tailed: one viral post can hand an arm the verdict single-handedly, which is precisely the "winner out of noise" these rules exist to prevent. `score_arms.py` prints a caution whenever a single run is half or more of an arm's total under a mean — when you see it, look at the run before acting, or switch the experiment to `"median"` and re-score. The median is the safer default once you expect virality; the mean is fine for metrics that arrive in similar-sized pieces (replies, demos).

Whatever you pick, the sanity check before acting on any `decided` verdict is the same: open the winning arm's runs and ask whether the win survives removing its single best run. If it doesn't, it isn't decided yet.

## After a verdict

1. **Promote** the winner to the base template
2. **Retire** the loser to the workflow's `templates/losers/` — never delete it. Runs only read the active folder, so it can't return by accident, but something that lost against one audience often wins against the next, and the folder is the cheapest record you'll keep of what doesn't work
3. **Write a challenger** that attacks the winner, with the hypothesis in a header comment
4. **Register** it in `experiments.json`, reset `started` to today, record the decision

Promoting and stopping means settling at a local maximum. The challenger is what keeps the thing moving.

## Guardrails

- Two live arms per **experiment** is the working default — every extra arm multiplies the runs needed before anything is decided. It's volume advice, not law: at real volume, three arms is a choice you can afford
- Concurrent experiments in one workflow are fine **when they're scoped to different channels** — set `"channel"` on each and pass `--channel` to `assign_arm.py`. What's not fine is two live experiments competing for the same runs: the first one in the file wins and the script warns
- Don't run more concurrent tests than your volume can decide. Every live experiment divides the same run stream; four half-starved tests decide nothing while one fed test decides something
- The challenger is written automatically; **promoting it needs a human yes**
- A template written to fill a gap starts as an ordinary arm — it earns default status by winning, not by being newest
- One variable at a time *per experiment*. Two variables in one test and the verdict tells you nothing about either

## `experiments.json`

```json
{
  "active_metric": "replies",
  "experiments": [
    {
      "id": "exp-001",
      "status": "live",
      "workflow": "outreach",
      "template_base": "first-touch",
      "variable": "offer",
      "min_runs_per_arm": 15,
      "win_ratio": 1.2,
      "started": "2026-08-01",
      "arms": [
        {
          "id": "default",
          "label": "free access for feedback",
          "template": "first-touch.txt",
          "hypothesis": "A small ask converts better cold."
        },
        {
          "id": "partner",
          "label": "50/50 revenue split",
          "template": "first-touch-partner.txt",
          "hypothesis": "A serious offer filters for serious people, so fewer replies but better ones."
        }
      ],
      "decision": null
    }
  ]
}
```

`status` is `live`, `paused` or `decided`. Only `live` experiments are assigned or scored.

Optional per-experiment fields: `channel` scopes the experiment to one channel so several can run concurrently in a workflow (see Guardrails); `direction` and `aggregate` shape the comparison (see *Which number the arms are compared on*).
