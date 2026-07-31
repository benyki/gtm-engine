# Video — going further

**Symptom: the posting APIs limit what you can publish, and reach is unpredictable.**

---

## Posting from a real device

Platform APIs are the sanctioned route and also the constrained one: limited formats, missing features, no access to some surfaces at all, and posts the platform can identify as API-originated.

Posting from an actual phone removes those constraints.

**mobilerun** drives a real Android device programmatically, so an agent can post the way a person does:

- <https://github.com/droidrun/mobilerun>
- <https://docs.mobilerun.ai/quickstart>

## The setup that works

- **A dedicated phone**, not your daily driver. A cheap Android is fine. One account per device wherever you can manage it
- **A consistent VPN or residential proxy per account.** Account identity on these platforms is tied to network fingerprint as much as to login, and a device that appears in three countries in a week looks exactly like what it looks like
- **Human-ish timing.** Consistent hours, not bursts at 3am
- **Keep API posting** for platforms where it isn't restricted. Use the device where it is

## Read this before you act on any of it

Automating a real device sits in a grey area of most platforms' terms of service, and the account risk is entirely yours.

It's a reasonable tool for running *your own* accounts at a scale you couldn't sustain by hand. It is not a tool for running fifty fake ones, and that second use is how people lose every account they have, usually all at once and without warning.

If the account matters to your business, weigh that properly before automating it.

---

## Other things worth doing before you get there

Most people reach for device automation before they've exhausted the cheaper wins:

- **Batch renders.** One session producing ten videos beats ten sessions producing one — the setup cost dominates
- **Repurpose across platforms.** The same 9:16 render goes to TikTok, Reels and Shorts. Post natively to each; cross-posted files with another platform's watermark get suppressed
- **Cache your b-roll.** Re-downloading the same stock clips wastes time and quota. Keep a local library, or move it to object storage (see `engine-setup/references/advanced.md`)
- **Test hooks, not videos.** Same body, three different first seconds. That's the A/B experiment worth running, and it converges much faster than testing whole concepts. (Once a format is genuinely working, testing *formats* becomes worthwhile too — see below)
- **Watch-through rate over views.** Views measure distribution; watch-through measures whether the hook did its job. Optimising views optimises the algorithm's mood

---

## A/B testing whole formats, not just hooks

**Symptom: the hook loop has stopped teaching you anything. Every challenger
lands within noise of the champion, and you suspect the ceiling is the format
itself, not the first line.**

That suspicion is often right, and testing a whole format against a working one
is the way to find out. It is also the most expensive test in this workflow, so
the entry conditions matter.

### Do this only when all three are true

1. **One format is genuinely working**, with a measured baseline — enough runs
   carrying numbers that you know its *median*, not its best day. Roughly
   fifteen measured runs is where a median stops moving around
2. **Your volume can feed two things.** Splitting a thin run stream produces two
   undecided experiments instead of one decided one
3. **The hook loop inside that format has already been round several times.**
   Formats are the second-order question; if you haven't answered the
   first-order one, you're skipping the cheap learning to buy the expensive kind

If any of those is false, `references/formats.md` and the hook experiment are
where the returns are. This section will still be here in two months.

### The rule that makes it safe

**Freeze the champion.** While the test runs, the working format changes in no
way at all — not the durations, not the look, not the music, not a "small
improvement" to the CTA. Every idea you have for it goes into the challenger
instead, and gets its turn later.

This is the part people skip, and skipping it wastes the whole test: a champion
you kept tuning is a moving baseline, so whatever the challenger's numbers say,
you can't attribute the difference to the format. You end up with two months of
runs and no answer.

### How to run it

| | |
|---|---|
| **Where** | The challenger gets its **own workflow folder** — `--merge --workflow video-<format>:video`. Same `primary_metric`, same channel as the champion, so the numbers are comparable |
| **Why a folder** | Formats have their own templates, queues, experiments and shot logic. They don't fit as two arms of one experiment, and a folder keeps the champion's spine untouched |
| **Split** | Roughly one run in three or four goes to the challenger. The working format keeps earning while the new one is unproven |
| **Minimum** | Five or six runs before you judge it. A format's first attempt is also your worst attempt at it |
| **Compare** | Both workflows' `reports/latest.json`, side by side, on the **median** of the shared metric. Not `score_arms.py` — nothing is pooled across folders, and that's deliberate |
| **Why median** | Short-form is heavy-tailed. One viral run under a mean hands the verdict to whichever folder got lucky |

### Deciding

- **Challenger clearly better** → it becomes the champion. The old format keeps
  running as the new challenger rather than being deleted — audiences move, and
  it's the cheapest challenger you'll ever have
- **Clearly worse** → stop it, keep the folder, and write *why* in
  `shared/insights.md`. "Talking head underperformed screen-recording demos 3:1
  on watch-through" is worth more next quarter than the runs cost you
- **Neither** → the format wasn't the lever. Fold the best bits into the
  champion one at a time as ordinary hook-level experiments, and go back to the
  hook loop

A format test that ends undecided is still information: it says your audience
cares more about what you're saying than how it's packaged, which is a useful
thing to know before you rebuild a pipeline.

Full rules and the loop-side view: `engine-loop/references/ab-testing.md`.
