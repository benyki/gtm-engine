# Setup — going further

Read this after a month of real runs, not on day one. Each section starts with the symptom that tells you it's time.

---

## Put your customised workflows in their own repo

**Symptom: your workflows only exist on one laptop, and you've started editing them in two places.**

Once you've tuned these templates to your product, they're the accumulated record of what works for you. Losing them to a wiped machine loses months.

Fork this repo, make it yours, and every machine you own pulls the same set.
Re-run `install_skills.sh` after `git pull` — it copies the selected skills into
`~/.agents/skills/` and refreshes the agent / workspace symlinks.

Keep your **workspace** in a separate private repo. It holds your CRM and your numbers, and it should never be public.

---

## Move run data to a database

**Symptom: two machines writing the same CSV, or a run history too long to scan.**

CSV is right until it isn't. The breaking points are specific: concurrent writes, wanting to query across projects, or a history long enough that reading it stops being practical.

Supabase (hosted Postgres) is the low-friction option — move `runs/index.csv`, `state/crm.csv` and the metrics into tables and give your agent access via the Supabase CLI or its MCP server. MCP is less setup; the CLI is more capable.

**One trap worth knowing about in advance.** If you have more than one Supabase account, a missing environment variable will silently target the wrong one — no error, just changes landing in the wrong project. The fix is a small wrapper script that injects the right token on every invocation, and never calling the bare CLI for automated work. Use one access token per machine so you can revoke a laptop without touching anything else.

---

## Object storage for media

**Symptom: your project folder is 40 GB and your laptop is the only copy.**

The pattern that works, and it's simpler than it looks:

- One bucket per project
- Credentials referenced by an environment variable pointing at a service-account file — never a key pasted into a config
- **Upload → get a URL → use it → delete once the post is confirmed live.** The bucket is a transfer buffer, not a library, so storage and egress stay near zero
- For anything private or large, use signed URLs with a 24–48 hour expiry plus a lifecycle rule that auto-deletes. Never leave a bucket publicly listable

This also fixes a specific annoyance: schedulers like Buffer require media to already be at a public URL, so a bucket is the difference between "scheduling works" and "scheduling doesn't".

GCS, S3 and Cloudflare R2 all work. R2 has no egress fees, which matters if you're serving video.

---

## Run the crons in the cloud

**Symptom: last week's job didn't run because the lid was shut.**

Once the loop is load-bearing, a local cron is the weak link — a closed laptop, a dropped VPN, an OS update at the wrong moment. Move the recurring jobs to a small always-on box or a scheduled cloud job.

Move the **crons** first and keep generation local while you're still iterating on taste. Push generation to the cloud only once you've stopped changing it weekly.

---

## Tailscale across machines

**Symptom: the machine that can render is never the machine you're sitting at.**

Desktop renders video, laptop travels, a VPS runs the crons. Tailscale puts them on one private network so your agent can reach files and services on any of them without port forwarding or a public IP.

The real unlock is triggering a render on the machine with the GPU from wherever you happen to be.
