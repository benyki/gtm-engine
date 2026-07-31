# A/B testing templates

The rules below come from a cold-outreach system that has been running these tests for months. Each one exists because breaking it produced a wrong answer that took weeks to notice.

They apply to **any workflow built from a template plus config** — outreach emails, video hooks, article openings, LinkedIn posts. If the output is rendered from a template, it can be tested this way.

---

## R0 — Don't test on day one

**A new workflow ships with one template and no live experiment.** Every
starter `experiments.json` in the workspace is `"status": "paused"` for this
reason, and flipping one to `live` before the workflow is settled is the most
common way to waste the first month.

Three reasons, in order of how much they hurt:

1. **You'd be testing the wrong thing.** The first version of anything is wrong
   in ways you can see without statistics — the format is off, the length is
   off, the ask is wrong. Fix that by looking at it, not by splitting traffic
   between two versions of a thing that isn't working yet
2. **The volume isn't there.** `min_runs_per_arm` is 8–15 in the starters. At
   two posts a week, one arm reaches that in two months, and until then every
   number you look at is noise wearing a table
3. **It slows the loop that actually matters.** Early on you learn most from
   shipping, watching, and changing one thing on purpose. An experiment freezes
   the template while it collects data — exactly the wrong constraint when the
   template still needs work

So the first phase is: **one template, ship it, look at the numbers, change
it.** `assign_arm.py` supports this directly — with no live experiment it
returns `action: use_template` (one template) or `choose_template` (several),
records nothing about arms, and every run still lands in `runs/index.csv` with
its `template_used`. You lose nothing. The spine is being written the whole
time.

### When to start testing

Flip an experiment to `live` when all three are true:

- **The user is happy with the format.** They'd send it, post it, ship it
  without editing. If they're still rewriting every draft, keep iterating
- **You've shipped enough to know the format works** — roughly 5–10 pieces with
  numbers on them. Not a rule, a smell test: you should be able to say what
  "normal" looks like for this workflow
- **You can name the one variable worth an answer.** "Does a question opener
  beat a claim opener" is a test. "Let's see what works" is not

Then: write the second arm, set `started` to today, set `status` to `live`, and
size `min_runs_per_arm` to a volume you'll actually reach this quarter.

Everything below applies from that moment on.

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

## Video: test the hook, then — much later — the format

Video has a variable so dominant that it's worth naming explicitly.

**Test the hook. Almost always, only the hook.** The first second and a half
decides whether anything else in the video is seen, which makes it the only
variable that pays back at low volume. Two shapes of the same test:

- **Hook text** — same footage, same durations, different opening line. Question
  versus claim, payoff-first versus tension-first, number versus promise.
  `engine-video/references/hook-guide.md` has the formats to draw the arms from
- **Hook clip** — same script and body, different first 4 seconds. A face versus
  a screen, motion versus stillness, product-visible versus product-hidden

Hold everything else identical: same body footage, same scene durations, same
voice, same look, same music level. If two things changed, the verdict tells you
nothing about either. Hook tests also converge fastest — the effect is large, so
you reach a verdict in weeks rather than months.

### Testing whole formats — advanced, and only once something works

Eventually you'll want to know whether a different *format* — not a different
hook, a different kind of video — would do better. That's a real question and
worth answering, but it is an **advanced practice for a workflow that's already
solid**, not a way to find your first winner. Do it only when:

- one format is genuinely working, with a **measured baseline** — enough runs
  with numbers that you know its median, not its best day
- your run volume can feed two things at once without starving both
- the hook loop inside the working format has already been round several times

Then the rule that makes it safe:

**Don't touch the working format while the test runs.** No tweaks, no small
improvements, no "while I'm in there". The champion is the measuring stick, and
a measuring stick you keep filing down measures nothing. Every change you're
itching to make goes into the challenger.

How to run it:

1. **Give the challenger its own workflow folder** (`--merge --workflow
   video-<format>:video`) with the **same `primary_metric` and channel** as the
   champion. Formats have different templates, queues and experiments — they
   don't fit as two arms of one experiment, and nothing is pooled across folders
2. **Send it a minority of the run stream** — roughly one in three or one in
   four. The working format keeps earning while the new one is unproven
3. **Compare at the report level**, not with `score_arms.py`: read both
   workflows' `reports/latest.json` side by side and compare the **medians** on
   the same metric. Means lie here — one viral video in either folder decides
   nothing
4. **Give it five or six runs minimum before judging.** A format's first attempt
   is also your worst attempt at it, and short-form is heavy-tailed enough that
   three runs is noise
5. **Decide, then act.** Clearly better → it becomes the champion and the old
   format keeps running as the new challenger. Clearly worse → stop it and write
   *why* in `shared/insights.md`. Neither → the format isn't the lever; go back
   to hooks

Formats are also worth trying **because the audience changed**, not only because
you're chasing a number. A format that lost a year ago can win now.

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
