# The loop — going further

**Symptom: the report is good, and you only read it when you remember to.**

---

## Push the decision to your phone

The loop's bottleneck is human attention, not compute. A weekly report you open in a terminal gets read some weeks. A short daily message gets read every day — and more importantly, you can answer it.

The upgrade: the report goes out as a message, and your reply is the input.

> **Mon 09:00** — 3 posts shipped. `question` 4.1% vs `default` 2.8% (11/15 runs). Nothing decided yet.
>
> *"kill default, try a stat opener"*
>
> **Applied.** `default` → losers/. New arm `stat` registered, hypothesis written.

Decisions that used to wait for a weekly sit-down happen in twenty seconds.

**Telegram** is the easy one: a bot token, a chat id, one HTTP call. **WhatsApp** needs the Business API and is meaningfully more setup for the same outcome — pick it only if that's genuinely where you live.

## What to send, and when

- **Daily:** what shipped, anything anomalous, anything blocked. Three lines. Longer than that and nobody reads it on a phone
- **Weekly:** the full six-section report with the proposed config diff
- **Never:** a notification per run. The fastest way to get a channel muted is to make it noisy, and a muted channel is worse than no channel

## Keep the approval boundary

Even here, the system proposes and you dispose. It can retire a loser and write a challenger on its own; promoting a challenger to default waits for your reply.

That boundary is what keeps the templates explainable. Once it starts promoting its own work unattended, you lose the thread of why the current template says what it says — and that thread is the only thing that makes the losers folder useful later.

---

## Other upgrades, roughly in order of payoff

**Segment before you conclude.** One arm often wins for enterprise and loses for solo founders. Once you have a few hundred rows, score by segment as well as overall — the aggregate can hide two opposite truths.

**Track time-to-outcome, not just outcome.** A reply in two hours and a reply in three weeks are different results. The timestamps are already recorded — `created_at` and `published_at` in `runs/index.csv`, `sent_at` and `replied_at` in `state/crm.csv`.

**Write a decision log.** Every promotion, every retirement, one line each, appended forever. After six months this is the most valuable file you own — it's the only record of what you tried and what happened, and it's what stops you re-running an experiment you already ran.

**Re-test old losers deliberately.** Audience changes, product changes, market changes. A template that lost in March is worth another run in September. This is why nothing is ever deleted.

**Cross-workflow learning.** The hook that wins on LinkedIn usually tells you something about the video hook. Nothing automates this — but reading the reports side by side once a month tends to be worth more than the reports themselves.
