# Packaging & Distribution

Packaging is layer 7 — strictly optional. `npm start` is the development loop and a
perfectly fine daily driver. Package only when the user wants a Dock/taskbar app.

## The trap to explain up front

A packaged app **embeds a frozen copy of `build/`** inside its bundle. It never reads
the working tree. `npm start` after a code change updates nothing about the installed
app. Every user hits "the app I open from the Dock doesn't have my changes" exactly
once — pre-empt it by setting up the update command below at the same time as the
first package.

## electron-builder config (in package.json)

```json
"build": {
  "appId": "com.<user>.vidwatch",
  "productName": "vidwatch",
  "asar": false,
  "directories": { "buildResources": "build-resources", "output": "dist" },
  "files": ["build/**/*", "package.json"],
  "mac":   { "category": "public.app-category.productivity", "icon": "build-resources/icon.icns", "identity": null },
  "win":   { "target": "nsis", "icon": "build-resources/icon.ico" },
  "linux": { "target": "AppImage", "icon": "build-resources/icon.png" }
}
```

Notes:

- `identity: null` skips macOS code signing — right for a personal local app; a
  signed/notarized build is a distribution concern, out of scope here.
- `asar: false` keeps the bundled code as loose inspectable files. Consequence:
  **updating by copying over an old install leaves orphaned files** — always
  remove-then-copy (the install script does).
- Icons are optional at first; electron-builder warns and uses a default. macOS wants
  `.icns` (512/1024px), Windows `.ico`, Linux png.

## Scripts

```json
"package":  "npm run build && CSC_IDENTITY_AUTO_DISCOVERY=false electron-builder --dir",
"dist:dmg": "npm run build && CSC_IDENTITY_AUTO_DISCOVERY=false electron-builder",
"app":      "npm run package && bash scripts/install-app.sh"
```

`--dir` produces the bare app bundle (fast, no installer) — all a local user needs.
`npm run app` is the one-command "update what my Dock launches" loop (~40s).

## scripts/install-app.sh (macOS)

Behavior contract, in order:

1. **Refuse to run** unless the freshly packaged bundle exists in `dist/` — the
   script must never delete the installed app without a replacement in hand.
2. Quit any running instance: `osascript -e 'tell application "vidwatch" to quit'`,
   poll `pgrep -x vidwatch` up to ~5s, then `pkill -x` as fallback. (Swapping files
   under a live process is the failure being prevented.)
3. `rm -rf /Applications/vidwatch.app && ditto dist/mac-arm64/vidwatch.app /Applications/vidwatch.app`
   — remove-then-`ditto`, never `cp` over (asar:false orphans, and `ditto` preserves
   the bundle attributes `cp -r` can mangle).
4. `open /Applications/vidwatch.app` and print a timestamped confirmation.
5. Touch nothing but that one destination path.

Note the arch in the dist path (`mac-arm64` vs `mac`) — derive it or glob it.

### Windows / Linux equivalents

Same contract, different mechanics:

- **Windows** (powershell): check `dist/win-unpacked/` exists → `Stop-Process -Name vidwatch` →
  remove + `Copy-Item -Recurse` into `%LOCALAPPDATA%\Programs\vidwatch` → start it.
  (Or just ship the NSIS installer from `dist:dmg`'s equivalent and re-run it.)
- **Linux**: AppImage is single-file — `cp dist/*.AppImage ~/.local/bin/vidwatch.AppImage && chmod +x`.
  No quit dance needed if the user relaunches themselves.

## Verifying an install (agents: do this, don't assume)

```bash
# bundle actually contains the current code? grep for a string you just added:
grep -rqs "<newly-added-identifier>" /Applications/vidwatch.app/Contents/Resources/app/build/ && echo fresh || echo STALE
# timestamps tell the same story:
ls -lad /Applications/vidwatch.app        # install time
ls -la build/main/index.js                # last dev build
# and it launched:
pgrep -x vidwatch
```

The grep is the strong check — mtimes can lie after a `ditto`.

## Cache locations (for support questions)

Packaged and dev builds share the same `userData` (same app name), so thumbnails,
availability cache, config and projects carry over between `npm start` and the
installed app automatically. That is intended; mention it so users don't think the
packaged app "lost" or "kept" data mysteriously.
