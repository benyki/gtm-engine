# <Workflow name>

<Who this writes to, what the email asks for, and why them now. Two sentences.>

**The number:** <replies a week, or calls booked>

Cold outreach that ends in mail drafts. Nothing here sends: a person reads and
sends every email.

## Run it

Ask your agent to run this workflow with the `gtm-outreach` skill.

## Schedule

Manual.

<!-- Or, once it runs on its own:
When: working days, 09:00
Where: <the scheduler this project uses>
Prompt: "<the exact prompt>"
-->

## Files

| Path | What | In git |
|---|---|---|
| `crm.csv` | everyone on the list: status, research, dates | no, personal data |
| `inputs/audience/` | the lists as they arrived | no, personal data |
| `templates/` | the first-touch email and the follow-up blocks | yes |
| `drafts/` | drafts as files, only when no mail connector is set up | no |
| `log.csv` | one row per batch sent, with its result | yes |
| `brand.md` | voice notes, only if the project has none elsewhere | yes |

## Keys

None when the list already has addresses: drafts go through the mail
connector. `HUNTER_API_KEY`, in the project's own env, only to find missing
addresses.

## Sources

- **Leads**: `inputs/audience/`, plus <where new leads come from>
- **Research**: the browser. One real, recent, specific observation per person;
  nothing to find means the wrong target

## What we learned

<!-- One line each, newest first: what clearly won or lost, and why. -->
