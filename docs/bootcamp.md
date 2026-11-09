# Running gtm-engine as a bootcamp

For the **organiser's agent**: you're helping someone run a session where a room
of people install gtm-engine and ship something real before they leave. Most of
them will be new to coding agents. Your job is the logistics and the room, not
the install itself, which each participant's own agent handles with the `gtm`
skill.

The one measure of a good session: **every participant leaves with one piece
they'd actually send or publish**, and a machine that will still work on Monday.

---

## Before the session

Give the organiser something to send participants a day or two ahead. It should
be short, and everything in it is a thing that costs ten minutes at home and
half an hour in the room.

What they need to have working:

- **A coding agent they're signed into.** Claude Code (Claude Desktop → Code
  tab, Pro or higher) or Codex (ChatGPT desktop → Codex, Plus or higher).
  Worth having them test it once: ask it to create a file and see it appear.
- **Browser control** installed and connected, since it's the piece nobody has
  by default and the one that blocks the most. *Claude in Chrome* or the
  ChatGPT extension. `gtm-social` is effectively dead without it.
- **A Gmail their agent can reach**, if they're doing outreach. Personal
  accounts are safer here: managed Workspace accounts often block the
  connector, and finding that out at 10am costs the morning.
- **Admin rights on the laptop.** Managed work machines that block installs are
  the single most common dead end, and there's no fix in the room.
- **A charger**, and 10 GB free if anyone is doing video.

What to ask them to bring, in whatever shape they already have it:

- **who they'd reach**: a list, a CRM export, a spreadsheet, a pasted block of
  addresses, even a screenshot. Tell them explicitly not to reformat it
- **what they sell** and the promise they make
- **the one number that matters** to them: replies, signups, demos
- **three pieces of content** they wish they'd made, as raw material for voice

Collect the answers to the middle two before the session if you can. They're the
slowest part of `brand.md`, and they're much better answered at a desk than
under time pressure.

## The shape of a session

Roughly ninety minutes to a first shipped piece, if the prep landed:

1. **Install**, five minutes. The one-line installer from the README, then
   each participant opens their project and tells their agent `run gtm`.
2. **One workflow, set up properly**, twenty minutes. Outreach unless they
   have a reason otherwise: it needs no keys and no website, and a reply is a
   real signal inside a week. The voice questions are the substance here.
3. **Ship one thing**, the rest. A draft they'd actually send, ten researched
   people, one post. Whatever it is, it gets a row in the workflow's `log.csv`,
   so next week's result has somewhere to land.
4. **A schedule**, five minutes at the end, for anyone who wants more next
   week: one scheduled task for the workflow, its prompt written in the
   workflow's README. Without it the session was a demo rather than a start.

Resist a second workflow in the room. One that shipped teaches more than two
half set up, and the other templates are there whenever they want one.

## What eats the time

- **A managed laptop that won't install.** No fix. Pair them with someone else
  and let them watch, or have them work in a cloud environment for the day.
- **A Workspace Gmail that won't connect.** Personal account, or draft into a
  local file and move on.
- **The browser extension not connected**, or the participant logged into
  LinkedIn in a different browser profile from the one the agent drives.
- **Video keys.** ffmpeg not installed, fal.ai credit at zero, upload-post
  profile not created. Anyone doing video needs the prep done beforehand.
- **A blank `brand.md`.** Thin answers are fine, invented ones are not. If
  someone genuinely can't say who they sell to, that's the real session.

## Guiding beginners

- **Take the defaults out loud.** Say which one you took and keep going. Nobody
  in their first hour benefits from a folder-layout decision.
- **Don't teach the folder rules.** They don't need to know why `workflows/`
  is shaped the way it is to send an email. It's there when they ask.
- **Show them a draft they'd actually send** as early as possible. That's the
  moment the thing becomes real; everything before it is setup.
- **Let them reject things.** Telling the agent why a draft is wrong is most of
  the work, and it's the habit that makes month three better than week one.
- **Be honest about results.** A few pieces are not a verdict; it takes a few
  weeks of shipping before the numbers say much. A session produces the first
  piece, not the answer.

## Afterwards

Send a nudge a week later, when the first results are in: fill in `result`
in `log.csv`, and write one line under "What we learned" in the workflow's
README when something clearly worked or didn't.

If a participant's skills look broken, re-run the installer. The workflow
itself is only files in their project, so there is nothing else to repair.
