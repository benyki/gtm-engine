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
- **Test hooks, not videos.** Same body, three different first seconds. That's the A/B experiment worth running, and it converges much faster than testing whole concepts
- **Watch-through rate over views.** Views measure distribution; watch-through measures whether the hook did its job. Optimising views optimises the algorithm's mood
