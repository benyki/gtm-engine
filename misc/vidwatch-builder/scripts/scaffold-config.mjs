#!/usr/bin/env node
/**
 * scaffold-config.mjs — walk a real videos tree and PROPOSE a vidwatch.config.json.
 *
 * Read-only. Prints a human report to stderr and the proposed config to stdout
 * (or writes it with --out). The proposal is a starting point for review with the
 * user, not a final answer — it cannot know accounts, pipelines, or ledger field
 * meanings; it only knows what exists on disk.
 *
 * Usage:
 *   node scaffold-config.mjs <videos-root> [--marker published] [--depth 4]
 *                            [--ext .mp4,.mov] [--out vidwatch.config.json] [--json]
 */
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join, relative, resolve } from "node:path";

const args = process.argv.slice(2);
const flags = {};
const positional = [];
for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith("--")) {
    const key = args[i].slice(2);
    const next = args[i + 1];
    if (next !== undefined && !next.startsWith("--")) { flags[key] = next; i++; }
    else flags[key] = true;
  } else positional.push(args[i]);
}

const expand = (p) => p.replace(/^~(?=$|\/)/, homedir());
const rootArg = positional[0];
if (!rootArg) {
  console.error("usage: node scaffold-config.mjs <videos-root> [--marker published] [--depth 4] [--ext .mp4] [--out file] [--json]");
  process.exit(1);
}
const ROOT = resolve(expand(rootArg));
const MARKER = flags.marker === "none" ? null : (flags.marker ?? "published");
const DEPTH = Number(flags.depth ?? 4);
const EXTS = String(flags.ext ?? ".mp4").split(",").map((e) => e.trim().toLowerCase());

if (!existsSync(ROOT)) {
  console.error(`✗ videos root does not exist: ${ROOT}`);
  process.exit(1);
}

const log = (...a) => console.error(...a);

/** Safe fs helpers — a permission error is a skip, never a crash. */
const list = (d) => { try { return readdirSync(d); } catch { return []; } };
const stat = (p) => { try { return statSync(p); } catch { return null; } };
const isVideo = (f) => EXTS.some((e) => f.toLowerCase().endsWith(e));

// ── 1. Discover source folders ─────────────────────────────────────────────
const sources = []; // { dir, mp4s: [stems] }
function walk(dir, depth) {
  if (depth > DEPTH) return;
  for (const name of list(dir)) {
    const full = join(dir, name);
    const st = stat(full);
    if (!st?.isDirectory()) continue;
    if (MARKER === null || name === MARKER) {
      const vids = list(full).filter(isVideo);
      if (vids.length > 0) sources.push({ dir: full, mp4s: vids.map((f) => f.replace(/\.[^.]+$/, "")) });
      if (MARKER !== null) continue; // marker folders are leaves
    }
    walk(full, depth + 1);
  }
}
// marker=null also treats the root itself as a candidate
if (MARKER === null) {
  const vids = list(ROOT).filter(isVideo);
  if (vids.length > 0) sources.push({ dir: ROOT, mp4s: vids.map((f) => f.replace(/\.[^.]+$/, "")) });
}
walk(ROOT, 0);

if (sources.length === 0) {
  log(`✗ No folders with ${EXTS.join("/")} files found under ${ROOT}` + (MARKER ? ` (marker: "${MARKER}")` : ""));
  log(`  Try --marker none, a bigger --depth, or check the root path.`);
  process.exit(1);
}

// ── 2. Probe metadata locations against real stems ─────────────────────────
const CANDIDATE_LOCATIONS = [
  "{stem}.json", "../{stem}.json", "../configs/{stem}.json",
  "../../configs/{stem}.json", "../../../configs/{stem}.json",
  "../../inputs/{stem}.json", "../meta/{stem}.json", "../metadata/{stem}.json",
];
const stripStamp = (stem) => stem.match(/^(.+)-\d{8}(?:T\d{6}Z)?$/)?.[1];

const locationHits = new Map(); // template -> hit count
let stamped = 0, totalClips = 0, clipsWithMeta = 0;
const shapeCounts = new Map(); // detected word-shape -> count

function detectShape(raw) {
  const listVal = raw?.words ?? raw?.items ?? raw?.pairs ?? raw?.entries ?? raw?.config?.words;
  if (!Array.isArray(listVal) || listVal.length === 0) return null;
  const el = listVal[0];
  if (Array.isArray(el)) return "two-string-array";
  if (el && typeof el === "object") {
    for (const pair of [["word", "translation"], ["school", "slang"], ["prompt", "answer"], ["english", "target"]]) {
      if (pair.every((k) => k in el)) return pair.join("/");
    }
    if ("en" in el && Object.keys(el).length >= 2) return "en/<other>";
    return "UNKNOWN keys: " + Object.keys(el).slice(0, 5).join(",");
  }
  return "UNKNOWN element type";
}

for (const src of sources) {
  for (const stem of src.mp4s) {
    totalClips++;
    const base = stripStamp(stem);
    if (base) stamped++;
    let found = false;
    for (const name of base ? [stem, base] : [stem]) {
      for (const tpl of CANDIDATE_LOCATIONS) {
        const p = resolve(src.dir, tpl.replace("{stem}", name));
        if (!existsSync(p)) continue;
        try {
          const raw = JSON.parse(readFileSync(p, "utf8"));
          locationHits.set(tpl, (locationHits.get(tpl) ?? 0) + 1);
          const shape = detectShape(raw);
          if (shape) shapeCounts.set(shape, (shapeCounts.get(shape) ?? 0) + 1);
          found = true;
        } catch { /* unparseable candidate — keep looking */ }
        if (found) break;
      }
      if (found) break;
    }
    if (found) clipsWithMeta++;
  }
}

// ── 3. Probe common ledger locations ───────────────────────────────────────
const LEDGER_CANDIDATES = [
  join(homedir(), ".agents", "runs", "posts.jsonl"),
  join(ROOT, "posts.jsonl"), join(ROOT, "ledger.jsonl"),
  join(dirname(ROOT), "posts.jsonl"),
];
const foundLedger = LEDGER_CANDIDATES.find((p) => existsSync(p)) ?? null;

// platform-status sidecars?
const psCount = sources.filter((s) =>
  existsSync(join(s.dir, "platform-status.json")) || existsSync(join(dirname(s.dir), "platform-status.json")),
).length;

// ── 4. Report ──────────────────────────────────────────────────────────────
log(`\nvidwatch scaffold — ${ROOT}`);
log(`─`.repeat(60));
log(`sources found:       ${sources.length}` + (MARKER ? ` (marker "${MARKER}")` : " (no marker: any video folder)"));
for (const s of sources.slice(0, 15)) log(`  ${relative(ROOT, s.dir) || "."}  (${s.mp4s.length} clips)`);
if (sources.length > 15) log(`  … and ${sources.length - 15} more`);
log(`total clips:         ${totalClips}`);
log(`timestamp-stamped:   ${stamped} (${Math.round((stamped / Math.max(totalClips, 1)) * 100)}%)`);
log(`metadata resolved:   ${clipsWithMeta}/${totalClips}`);
if (locationHits.size) {
  log(`metadata locations that actually hit:`);
  for (const [tpl, n] of [...locationHits].sort((a, b) => b[1] - a[1])) log(`  ${tpl}  ×${n}`);
}
if (shapeCounts.size) {
  log(`word-pair shapes detected:`);
  for (const [shape, n] of [...shapeCounts].sort((a, b) => b[1] - a[1])) {
    log(`  ${shape}  ×${n}` + (shape.startsWith("UNKNOWN") ? "   ← needs a new extractWords branch (inputs.md §4)" : ""));
  }
}
log(`ledger candidate:    ${foundLedger ?? "none found — layer 3 will use file mtime"}`);
log(`platform-status:     ${psCount}/${sources.length} sources have one`);

// ── 5. Proposed config ─────────────────────────────────────────────────────
const usedLocations = [...locationHits.keys()];
const config = {
  videosRoot: rootArg.startsWith("~") ? rootArg : ROOT,
  publishedMarker: MARKER,
  walkDepth: DEPTH,
  videoExtensions: EXTS,
  metadataLocations: usedLocations.length ? usedLocations : CANDIDATE_LOCATIONS.slice(0, 6),
  ledger: { path: foundLedger, format: "jsonl", fields: {
    file: "file_archived", postedAt: "posted_at", account: "account",
    url: "post_url", status: "status", pipeline: "pipeline", tag: "tag",
  } },
  platformStatus: psCount > 0 ? { file: "platform-status.json" } : { file: null },
  metrics: { providers: ["tiktok-oembed"], statsTtlHours: 12, unknownTtlDays: 7, concurrency: 6 },
  thumbnails: { ffmpeg: null, defaultSeekSeconds: 1.2, width: 360 },
  sources: sources.map((s) => {
    const rel = relative(ROOT, s.dir);
    return { id: `unlinked:${rel}`, publishedRel: rel, label: rel.replace(new RegExp(`/${MARKER}$`), "") || basename(ROOT), format: basename(dirname(s.dir)) || "other", pipeline: "unknown" };
  }),
};

const out = JSON.stringify(config, null, 2);
if (flags.out) {
  const dest = resolve(expand(String(flags.out)));
  if (existsSync(dest)) {
    log(`\n✗ ${dest} already exists — refusing to overwrite. Print without --out and merge by hand.`);
    process.exit(1);
  }
  writeFileSync(dest, out + "\n");
  log(`\n✓ wrote ${dest} — REVIEW IT: fill in accounts/pipelines/labels, verify the ledger fields match.`);
} else {
  log(`\nProposed config (redirect stdout or use --out to save):\n`);
  console.log(out);
}
