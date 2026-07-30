# After publish — Clarity → rewrite checklist

Use Microsoft Clarity (export API or dashboard) as **behavioral evidence**, not a
ranking oracle. Turn what people do on a page into the next rewrite — don’t
guess from impressions alone.

If `benyki/skills/clarity-api-seo` is installed and `CLARITY_API_KEY` is set,
prefer its export script. Otherwise the dashboard is enough for this checklist.

## When to run

After the article has real traffic (weeks for organic, not the 72h social
window). Compare a recent window to a prior window of the same length when you can
(7 vs prior 7, or 28 vs prior 28).

## Signal → rewrite

| Signal | Likely cause | Rewrite / fix |
|---|---|---|
| High visits, high **quick backs** | Title/intent mismatch, weak first screen | Rewrite H1 + first 100 words to answer the query; tighten title/meta |
| High visits, **shallow scroll** | Wall of text, buried answer, slow start | Lead with the answer; cut throat-clearing; add subheads that match questions |
| **Rage / dead clicks** on a control | Looks clickable, isn’t — or broken UI | Fix the control, or stop styling non-links as buttons |
| Engaged pages, weak conversion | No next step, buried CTA | Add one clear CTA / internal link to the money page |
| Strong engagement on a topic cluster | Template works | Clone structure for adjacent questions; internal-link the cluster |
| Mobile worse than desktop | Tap targets, sticky overlays, layout | Fix mobile first; don’t “average” the two |
| Spike in JS errors on a URL | Broken experience | Fix tech before rewriting copy |
| Source X sends long sessions; source Y bounces | Landing mismatch by channel | Align opening to how that source frames the promise |

## Minimum pull (per page you’re judging)

- Sessions / pageviews (and landing share if available)
- Quick backs
- Scroll depth (or “excessive scroll” if that’s what you get)
- Rage clicks / dead clicks
- Device split (mobile vs desktop)
- Top referrers / sources for that URL

Label whether a number is from the **export API**, an **approximate dashboard
card**, or **unavailable** — they are not always 1:1.

## Output for the next SEO run

One short note the agent can act on:

1. **Page URL** + `run_id` if known
2. **Top 1–3 problems** (signal + interpretation)
3. **Concrete rewrite** (which sections, what to change)
4. **UX/tech** items that block the rewrite from mattering
5. Whether to log a **new** `runlog.py` run (major rewrite) or treat it as a
   fix on the existing published URL

Do **not** claim ranking changes from Clarity alone — use Search Console (or
equivalent) for that.
