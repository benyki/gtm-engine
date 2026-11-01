# Video — going further

Next steps once one video workflow ships reliably. None of them is needed for
the first month.

---

## Cheaper wins first

Most people reach for device automation before they've exhausted these:

- **Batch renders.** One session producing ten videos beats ten sessions producing one — the setup cost dominates
- **Repurpose across platforms.** The same 9:16 render goes to TikTok, Reels and Shorts. Post natively to each; cross-posted files with another platform's watermark get suppressed
- **Cache your b-roll.** Re-downloading the same stock clips wastes time and quota. Keep a local library in the workflow's `assets/`, or move it to object storage once it outgrows the disk
- **Vary hooks, not videos.** Same body, three different first seconds. It teaches you much faster than comparing whole concepts
- **Watch-through rate over views.** Views measure distribution; watch-through measures whether the hook did its job. Optimising views optimises the algorithm's mood

---

## Trying a second format against a working one

Worth it only once one format works, with enough logged videos (roughly
fifteen) that you know its median rather than its best day, and once varying
the hook has stopped teaching you anything.

- **Its own workflow folder**, same channel, so the numbers compare
- **Freeze the working format** while the new one runs. A baseline you keep
  tuning is a moving target, and the comparison means nothing
- **Five or six videos** before you judge it. A format's first attempt is also
  your worst attempt at it
- **Compare medians** of the two `log.csv` files, not means. Short-form is
  heavy-tailed; one viral video under a mean hands the verdict to luck
- Clearly better: it becomes the main format. Clearly worse: stop it and write
  why in "What we learned". Neither: the format wasn't the lever, go back to hooks

---

## Posting from a real device

**Symptom: the posting APIs limit what you can publish, and reach is unpredictable.**

Platform APIs are the sanctioned route and also the constrained one: limited formats, missing features, no access to some surfaces at all, and posts the platform can identify as API-originated.

Posting from an actual phone removes those constraints.

**mobilerun** drives a real Android device programmatically, so an agent can post the way a person does:

- <https://github.com/droidrun/mobilerun>
- <https://docs.mobilerun.ai/quickstart>

### The setup that works

- **A dedicated phone**, not your daily driver. A cheap Android is fine. One account per device wherever you can manage it
- **A consistent VPN or residential proxy per account.** Account identity on these platforms is tied to network fingerprint as much as to login, and a device that appears in three countries in a week looks exactly like what it looks like
- **Human-ish timing.** Consistent hours, not bursts at 3am
- **Keep API posting** for platforms where it isn't restricted. Use the device where it is

### Read this before you act on any of it

Automating a real device sits in a grey area of most platforms' terms of service, and the account risk is entirely yours.

It's a reasonable tool for running *your own* accounts at a scale you couldn't sustain by hand. It is not a tool for running fifty fake ones, and that second use is how people lose every account they have, usually all at once and without warning.

If the account matters to your business, weigh that properly before automating it.

Whatever posts the video, a human still says yes to each one first.
