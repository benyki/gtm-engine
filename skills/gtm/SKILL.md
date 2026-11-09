---
name: gtm
description: Start a marketing workflow in any project and ship a first piece today. A workflow is one folder in the project's workflows/; gtm-outreach, gtm-seo, gtm-social and gtm-video are optional templates to start it from, or it can be built freely. Use when the user says "run gtm", "set up gtm", "start a growth workflow", "marketing workflow", "help me get users", or points you at the gtm-engine repo.
---

# gtm

Gets a project from nothing to one workflow that ships something today.

## The `workflows/` folder

**`<repo>/workflows/` is deliberately loose: a workflow lives there, one folder
each, and covers one use case, in any domain (distribution, biz dev, finance,
reporting, support), that the project needs done regularly.** Those are the
only two rules.

Defaults, which a workflow may break when it has a reason:

- Only the main files go in git; heavy and temp files are gitignored, and kept
  out of app builds.
- One workflow is one scheduled task.
- Agents or people outside the company run workflows, so think everything from
  their side: they must be able to do the task correctly.

## Start one

1. **Look first.** If `workflows/` exists, list it. A new workflow goes next to
   what is there: never move, rename or merge into an existing folder, and pick
   a name no folder holds. If it does not exist, create it at the repo root
   (not `.github/workflows/`, which belongs to GitHub Actions). Outside a git
   repo, use the folder where the user keeps this project's work.
2. **Keep it out of the app build, now.** If the repo has an `.easignore`, add
   `/workflows/` to it: EAS reads that file instead of every `.gitignore`, so
   without the line a personal file such as `crm.csv` ships with the next
   build. If the app's `tsconfig.json` or lint config covers the whole repo,
   exclude `workflows/` there too. These edit the user's files: say so first.
3. **Pick a template, or none.**

   | Template | What it ships |
   |---|---|
   | `gtm-outreach` | personalised cold emails, as drafts, never sent |
   | `gtm-seo` | articles that answer the questions real people ask |
   | `gtm-social` | LinkedIn, X and Bluesky posts in the user's voice |
   | `gtm-video` | short vertical videos: script, voice, footage, render |

   If the user has no preference, suggest outreach: drafts today and replies
   this week, with no keys when they already have a list. Anything none of
   them covers is a free workflow: make the folder with a `README.md` saying
   what it does, for whom, and the number that says it works.
4. **Copy the template folder whole**, naming the copy after what it does
   (`creator-outreach`, `weekly-linkedin`), not after the template:

   ```bash
   mkdir -p workflows && cp -R ~/.agents/skills/gtm-outreach/template workflows/creator-outreach
   ```

   Use the folder where the skill is installed if it is not `~/.agents/skills`.
   Copying the folder, not `template/*`, keeps its `.gitignore`; check that it
   arrived. Fill in the README's first lines, including **The number**.
5. **Follow the template's Start**, skipping its copy step. The first session
   ends at a piece the user approves. Its row goes into `log.csv` when it is
   live: sent, posted or published.

## Voice

The project's own brand or voice notes come first: its README, its docs, a
`brand.md` anywhere. None? Ask these five, and write the answers to `brand.md`
in the workflow folder:

1. Who is it for, specifically?
2. What does the product do, in one line?
3. Three words for how it should sound, and three it should never sound like
4. Words or claims never to use
5. One piece of writing, theirs or anyone's, that sounds right

## Hints

- **Keys** come from the project's own env setup. Read `.env.example` for the
  names, never `.env`. A key the workflow needs and the file lacks: add its
  name to `.env.example` (create the file if there is none), and the user
  pastes the value into their own env.
- **Schedule it** once a first piece has shipped and the user wants more, with
  whatever scheduler the project already uses (Claude Code scheduled tasks,
  cron, CI). Each run starts with no memory, so the prompt must stand alone.
  Write when it runs, where, and the exact prompt in the README.
- **Learn from it.** When a piece's result is due (each template says when:
  days for email and social, weeks for search), fill in `result` in
  `log.csv`. When something clearly wins or loses, add one line under "What
  we learned" in the README, and read that section before the next piece.
- **Never send, post or publish without an explicit yes.**

## More

- [Useful links](https://github.com/benyki/gtm-engine/blob/main/docs/useful-links.md):
  every signup and key, per template.
- [Additional skills](https://github.com/benyki/gtm-engine/blob/main/docs/additional-skills.md):
  optional toolbox skills the templates can reach for.
