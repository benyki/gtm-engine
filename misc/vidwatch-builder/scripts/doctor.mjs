#!/usr/bin/env node
/**
 * doctor.mjs — validate a vidwatch.config.json against the real filesystem.
 *
 * Read-only. Answers "why does the app look emptier than I expected?" without
 * launching Electron: checks every configured path, simulates discovery and the
 * metadata/ledger joins, and flags the known failure modes.
 *
 * Usage:  node doctor.mjs <path/to/vidwatch.config.json>
 * Exit:   0 = healthy (warnings allowed) · 1 = fatal problem
 */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";

const cfgPath = process.argv[2];
if (!cfgPath) { console.error("usage: node doctor.mjs <vidwatch.config.json>"); process.exit(1); }

const expand = (p) => String(p).replace(/^~(?=$|\/)/, homedir());
let fatal = 0, warns = 0;
const ok = (m) => console.log(`  ✓ ${m}`);
const warn = (m) => { warns++; console.log(`  ⚠ ${m}`); };
const fail = (m) => { fatal++; console.log(`  ✗ ${m}`); };

let cfg;
try { cfg = JSON.parse(readFileSync(resolve(expand(cfgPath)), "utf8")); }
catch (e) { console.error(`✗ cannot read/parse config: ${e.message}`); process.exit(1); }

const list = (d) => { try { return readdirSync(d); } catch { return []; } };
const stat = (p) => { try { return statSync(p); } catch { return null; } };

console.log(`\nvidwatch doctor — ${cfgPath}`);
console.log("─".repeat(60));

// ── 1. Root & discovery ────────────────────────────────────────────────────
console.log("\n[1] videos root & discovery");
const ROOT = cfg.videosRoot ? resolve(expand(cfg.videosRoot)) : null;
if (!ROOT) fail("videosRoot missing — the one required field");
else if (!existsSync(ROOT)) fail(`videosRoot does not exist: ${ROOT}`);
else ok(`videosRoot exists: ${ROOT}`);

const MARKER = cfg.publishedMarker === undefined ? "published" : cfg.publishedMarker;
const DEPTH = cfg.walkDepth ?? 4;
const EXTS = (cfg.videoExtensions ?? [".mp4"]).map((e) => e.toLowerCase());
const isVideo = (f) => EXTS.some((e) => f.toLowerCase().endsWith(e));

const discovered = [];
if (ROOT && existsSync(ROOT)) {
  const walk = (dir, depth) => {
    if (depth > DEPTH) return;
    for (const name of list(dir)) {
      const full = join(dir, name);
      if (!stat(full)?.isDirectory()) continue;
      if (MARKER === null || name === MARKER) {
        const vids = list(full).filter(isVideo);
        if (vids.length) discovered.push({ dir: full, stems: vids.map((f) => f.replace(/\.[^.]+$/, "")) });
        if (MARKER !== null) continue;
      }
      walk(full, depth + 1);
    }
  };
  if (MARKER === null) {
    const vids = list(ROOT).filter(isVideo);
    if (vids.length) discovered.push({ dir: ROOT, stems: vids.map((f) => f.replace(/\.[^.]+$/, "")) });
  }
  walk(ROOT, 0);
  const clips = discovered.reduce((n, s) => n + s.stems.length, 0);
  if (discovered.length === 0) fail(`discovery finds NOTHING (marker "${MARKER}", depth ${DEPTH}, ext ${EXTS.join(",")}) — wrong marker? depth too small?`);
  else ok(`discovery: ${discovered.length} source folders, ${clips} clips`);
}

// configured sources actually on disk?
for (const s of cfg.sources ?? []) {
  const p = ROOT ? join(ROOT, s.publishedRel ?? "") : null;
  if (!p || !existsSync(p)) warn(`configured source "${s.id ?? s.publishedRel}" not on disk: ${p} (will simply not appear)`);
}
const relSet = new Set((cfg.sources ?? []).map((s) => s.publishedRel));
const unlinked = ROOT ? discovered.filter((d) => !relSet.has(d.dir.slice(ROOT.length + 1))) : [];
if (unlinked.length) console.log(`  · ${unlinked.length} discovered folder(s) not in config sources — will show as "unlinked" (fine)`);

// ── 2. Metadata join ───────────────────────────────────────────────────────
console.log("\n[2] metadata resolution");
const LOCS = cfg.metadataLocations ?? ["{stem}.json", "../{stem}.json", "../configs/{stem}.json", "../../configs/{stem}.json", "../../inputs/{stem}.json"];
const stripStamp = (stem) => stem.match(/^(.+)-\d{8}(?:T\d{6}Z)?$/)?.[1];
let withMeta = 0, total = 0, unparseable = 0;
for (const src of discovered) {
  for (const stem of src.stems) {
    total++;
    const base = stripStamp(stem);
    let hit = false;
    outer: for (const name of base ? [stem, base] : [stem]) {
      for (const tpl of LOCS) {
        const p = resolve(src.dir, tpl.replace("{stem}", name));
        if (!existsSync(p)) continue;
        try { JSON.parse(readFileSync(p, "utf8")); hit = true; break outer; }
        catch { unparseable++; }
      }
    }
    if (hit) withMeta++;
  }
}
if (total === 0) warn("no clips to test metadata against");
else {
  const pct = Math.round((withMeta / total) * 100);
  (pct >= 60 ? ok : warn)(`metadata resolves for ${withMeta}/${total} clips (${pct}%)${pct < 60 ? " — check metadataLocations against the real layout (inputs.md §2)" : ""}`);
  if (unparseable) warn(`${unparseable} sidecar candidate(s) exist but fail JSON.parse`);
}

// ── 3. Ledger ──────────────────────────────────────────────────────────────
console.log("\n[3] ledger");
const lpath = cfg.ledger?.path ? resolve(expand(cfg.ledger.path)) : null;
if (!lpath) console.log("  · no ledger configured — dates fall back to file mtime (layer 3 off)");
else if (!existsSync(lpath)) fail(`ledger configured but missing: ${lpath}`);
else {
  const fields = cfg.ledger.fields ?? {};
  const fileField = fields.file ?? "file_archived";
  const text = readFileSync(lpath, "utf8");
  let rows = 0, bad = 0, withFile = 0;
  const byStem = new Set();
  if ((cfg.ledger.format ?? "jsonl") === "jsonl") {
    for (const line of text.split("\n")) {
      if (!line.trim()) continue;
      rows++;
      try {
        const rec = JSON.parse(line);
        const f = rec[fileField];
        if (typeof f === "string" && f) { withFile++; byStem.add(f.split("/").pop().replace(/\.[^.]+$/, "")); }
      } catch { bad++; }
    }
  } else warn(`doctor only simulates jsonl joins; format "${cfg.ledger.format}" is checked for existence only`);
  ok(`ledger: ${rows} rows (${bad} malformed — tolerated)`);
  if (rows && withFile === 0) fail(`no row has a "${fileField}" field — ledger.fields.file is wrong; the join will match NOTHING`);
  else if (rows) {
    let matched = 0;
    for (const src of discovered) for (const stem of src.stems) if (byStem.has(stem)) matched++;
    const pct = total ? Math.round((matched / total) * 100) : 0;
    (pct >= 40 ? ok : warn)(`ledger joins ${matched}/${total} clips by stem (${pct}%)${pct < 40 ? " — different naming between renderer and poster?" : ""}`);
  }
}

// ── 4. Platform status ─────────────────────────────────────────────────────
console.log("\n[4] platform status");
const psFile = cfg.platformStatus?.file;
if (!psFile) console.log("  · disabled");
else {
  const n = discovered.filter((s) => existsSync(join(s.dir, psFile)) || existsSync(join(s.dir, "..", psFile))).length;
  (n > 0 ? ok : warn)(`${n}/${discovered.length} sources have ${psFile}${n === 0 ? " — layer 4 will show nothing (fine if unused)" : ""}`);
}

// ── 5. Tooling ─────────────────────────────────────────────────────────────
console.log("\n[5] tooling");
const ffCandidates = [cfg.thumbnails?.ffmpeg, "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/usr/bin/ffmpeg"].filter(Boolean).map(expand);
const ff = ffCandidates.find((c) => existsSync(c));
if (ff) ok(`ffmpeg: ${ff}`);
else warn("ffmpeg not found at config/common paths (PATH lookup may still work) — no ffmpeg = no thumbnails, app still runs");
const major = Number(process.versions.node.split(".")[0]);
(major >= 18 ? ok : fail)(`node ${process.versions.node}${major < 18 ? " — need ≥18" : ""}`);

// URL normalization heads-up (the www trap, platforms.md)
if ((cfg.metrics?.providers ?? []).includes("tiktok-oembed")) {
  console.log("  · reminder: normalize TikTok URLs to www.tiktok.com before liveness checks (platforms.md — the non-www 400 trap)");
}

console.log("\n" + "─".repeat(60));
console.log(fatal ? `✗ ${fatal} fatal problem(s), ${warns} warning(s)` : `✓ healthy — ${warns} warning(s)`);
process.exit(fatal ? 1 : 0);
