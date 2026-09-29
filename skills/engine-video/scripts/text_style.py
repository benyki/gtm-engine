#!/usr/bin/env python3
"""Resolve the overlay font, emit the ASS style, and prove libass used it.

libass never fails loudly on a missing font: it substitutes something, the
render looks plausible, and the channel is off-brand for weeks before anyone
notices. So nothing here is hardcoded and nothing is assumed — the font
directory is resolved, the family name is read out of the file itself, and
`probe` checks what libass actually picked.

Usage:
    text_style.py fonts                          # resolved dir + families in it
    text_style.py style --width 1080 --height 1920 [--family "..."] [--weight 700]
    text_style.py probe --video in.mp4 --ass overlay.ass

Font directory resolution, first hit wins:
    --fonts <dir>
    $GTM_FONTS_DIR
    <home>/shared/assets/fonts/     — the user's brand font, if any
    <this skill>/assets/fonts/           — the faces this repo ships

Style numbers come from references/ffmpeg-text-style.md and scale from a
1080-wide reference. Change them there and here together, or not at all.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR.parent / "engine-loop" / "scripts"))

REFERENCE_WIDTH = 1080
BASE_FONT_SIZE = 74
BASE_SPACING = -2.2
LINE_HEIGHT_RATIO = 1.05
PARAGRAPH_GAP_RATIO = 0.5
OUTLINE_RATIO = 0.0675
MIN_OUTLINE = 3
ANCHOR_PCT = 33.0
FONT_EXTS = (".ttf", ".otf", ".ttc")


# --- font directory ---------------------------------------------------------

def has_fonts(d: Path) -> bool:
    return d.is_dir() and any(p.suffix.lower() in FONT_EXTS for p in d.iterdir())


def home_fonts() -> Path | None:
    try:
        from gtmfind import find_home  # noqa: PLC0415
    except ImportError:
        return None
    try:
        ws = find_home(None)
    except SystemExit:
        return None
    d = ws / "shared" / "assets" / "fonts"
    return d if has_fonts(d) else None


def resolve_fonts_dir(explicit: str | None) -> Path:
    if explicit:
        d = Path(explicit).expanduser().resolve()
        if not has_fonts(d):
            sys.exit(f"error: no font files in {d}")
        return d
    env = (os.environ.get("GTM_FONTS_DIR") or "").strip()
    if env:
        d = Path(env).expanduser().resolve()
        if has_fonts(d):
            return d
    ws = home_fonts()
    if ws:
        return ws.resolve()
    shipped = SKILL_DIR / "assets" / "fonts"
    if has_fonts(shipped):
        return shipped
    sys.exit("error: no fonts found — pass --fonts, set GTM_FONTS_DIR, or put "
             "font files in <home>/shared/assets/fonts/")


# --- family names, read out of the font file itself -------------------------

def _name_records(data: bytes, offset: int = 0) -> list[tuple[int, str]]:
    """(nameID, value) from an sfnt `name` table. Empty on anything unexpected."""
    try:
        num_tables = struct.unpack(">H", data[offset + 4:offset + 6])[0]
        for i in range(num_tables):
            rec = offset + 12 + i * 16
            tag = data[rec:rec + 4]
            if tag != b"name":
                continue
            tbl = struct.unpack(">I", data[rec + 8:rec + 12])[0]
            count, str_off = struct.unpack(">HH", data[tbl + 2:tbl + 6])
            out = []
            for j in range(count):
                r = tbl + 6 + j * 12
                pid, eid, lid, nid, length, off = struct.unpack(">6H", data[r:r + 12])
                if nid not in (1, 16):
                    continue
                start = tbl + str_off + off
                raw = data[start:start + length]
                enc = "utf-16-be" if pid == 3 or (pid == 0) else "latin-1"
                try:
                    out.append((nid, raw.decode(enc).strip()))
                except UnicodeDecodeError:
                    continue
            return out
    except (struct.error, IndexError):
        pass
    return []


def families(path: Path) -> list[str]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    offsets = [0]
    if data[:4] == b"ttcf":                       # font collection
        n = struct.unpack(">I", data[8:12])[0]
        offsets = list(struct.unpack(f">{n}I", data[12:12 + 4 * n]))
    names: list[str] = []
    for off in offsets:
        for nid, value in _name_records(data, off):
            if value and value not in names:
                names.append(value)
    return names


def dir_families(d: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in sorted(d.iterdir()):
        if p.suffix.lower() in FONT_EXTS:
            for fam in families(p):
                out.setdefault(fam, []).append(p.name)
    return out


def default_family(d: Path) -> str | None:
    """The most specific family every face in the dir agrees on."""
    fams = dir_families(d)
    if not fams:
        return None
    total = len([p for p in d.iterdir() if p.suffix.lower() in FONT_EXTS])
    shared = [f for f, files in fams.items() if len(files) == total]
    return max(shared or list(fams), key=len)


# --- the style ---------------------------------------------------------------

def style_values(width: int, height: int) -> dict:
    scale = width / REFERENCE_WIDTH
    size = max(1, round(BASE_FONT_SIZE * scale))
    return {
        "font_size": size,
        "spacing": round(BASE_SPACING * scale, 2),
        "line_height": max(size, round(size * LINE_HEIGHT_RATIO)),
        "paragraph_gap": max(1, round(size * PARAGRAPH_GAP_RATIO)),
        "outline": max(MIN_OUTLINE, round(size * OUTLINE_RATIO)),
        "anchor_x": round(width / 2),
        "anchor_y": round(height * (ANCHOR_PCT / 100)),
    }


def style_block(family: str, width: int, height: int, weight: int) -> str:
    v = style_values(width, height)
    return "\n".join([
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
        "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
        f"Style: Overlay,{family},{v['font_size']},&H00FFFFFF,&H00FFFFFF,"
        f"&H00000000,&H00000000,0,0,0,0,100,100,{v['spacing']:.2f},0,1,"
        f"{v['outline']},0,5,0,0,0,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text",
        f"; one line, centred on {ANCHOR_PCT:g}% of the height:",
        f"; Dialogue: 0,0:00:00.00,0:00:03.00,Overlay,,0,0,0,,"
        f"{{\\an5\\q2\\pos({v['anchor_x']},{v['anchor_y']})\\b{weight}}}Your hook",
    ])


# --- probe -------------------------------------------------------------------

# fontselect: (requested_family, weight, italic) -> matched_name, index, tail
#
# `tail` is a real filesystem path on the backends that have one to give
# (fontconfig on Linux, CoreText on macOS) — there, comparing its resolved
# parent against the fonts dir is authoritative. On Windows (GDI/DirectWrite)
# libass has no path to report at all: `matched_name` and `tail` are just the
# same font name repeated, e.g. `-> ArialMT, 0, ArialMT`. On that backend we
# instead match the reported name against the family names and filenames our
# own fonts dir actually declares (from `dir_families`), which is the only
# signal available.
SELECT_RE = re.compile(r"fontselect: \((.+?), (\d+), \d+\) -> (.+?), (-?\d+), (.+)$")
_WIN_ABS_RE = re.compile(r"^[A-Za-z]:[\\/]|^\\\\")


def _is_real_path(s: str) -> bool:
    return s.startswith("/") or bool(_WIN_ABS_RE.match(s))


def _normalize(s: str) -> str:
    """Fold away spacing/casing differences between how a name-only backend
    reports a font and how the file itself declares its family or is named
    (`TikTok Sans 12pt` vs `TikTokSans12pt-Bold` vs a filename stem)."""
    return re.sub(r"[\s_-]+", "", s).casefold()


def _known_identifiers(fonts: Path) -> set[str]:
    ids: set[str] = set()
    for fam, files in dir_families(fonts).items():
        ids.add(_normalize(fam))
        for fn in files:
            ids.add(_normalize(Path(fn).stem))
    return ids


def filtergraph_path(p: Path) -> str:
    """Render a path for embedding in an ffmpeg -vf filtergraph value.

    A bare Windows absolute path (`C:\\Users\\...`) breaks ffmpeg's
    filtergraph parser even inside single quotes — the drive-letter colon
    still splits filter options, so libass silently gets no fontsdir/filename
    and substitutes a system font with no error. Prefer a path relative to
    the cwd, which has no drive letter to collide with. When that's not
    reachable (cwd and the path are on different drives), fall back to an
    absolute path with forward slashes and the colon escaped as `\\:`, per
    ffmpeg's own filtergraph escaping rules.
    """
    p = p.resolve()
    try:
        rel = os.path.relpath(p, Path.cwd())
    except ValueError:
        rel = None
    if rel is not None:
        return rel.replace("\\", "/")
    return str(p).replace("\\", "/").replace(":", "\\:")


def probe(video: Path, ass: Path, fonts: Path) -> int:
    ffmpeg = os.environ.get("FFMPEG_BIN", "ffmpeg")
    ass_arg = filtergraph_path(ass)
    fonts_arg = filtergraph_path(fonts)
    cmd = [ffmpeg, "-y", "-loglevel", "debug", "-i", str(video),
           "-vf", f"subtitles=filename='{ass_arg}':fontsdir='{fonts_arg}'",
           "-frames:v", "1", "-f", "null", "-"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit(f"error: {ffmpeg} not found — install ffmpeg or set FFMPEG_BIN")
    known = _known_identifiers(fonts)
    picks, bad = [], False
    for line in res.stderr.splitlines():
        m = SELECT_RE.search(line)
        if not m:
            continue
        requested, weight, matched, _idx, tail = m.groups()
        if _is_real_path(tail):
            ours = Path(tail).resolve().parent == fonts.resolve()
        else:
            ours = _normalize(matched) in known or _normalize(tail) in known
        picks.append({"requested": requested, "weight": int(weight),
                      "got": tail, "from": matched, "ours": ours})
        bad = bad or not ours
    if not picks:
        print("no font selection logged — is the .ass path right, and does this "
              "ffmpeg have libass?", file=sys.stderr)
        return 2
    for p in picks:
        mark = "ok  " if p["ours"] else "SUB "
        print(f"{mark} {p['requested']} @{p['weight']} -> {p['got']}  ({p['from']})")
    if bad:
        print("\nlibass substituted a system font. The family name in the ASS "
              "does not match anything in the fonts dir — run `fonts` to see "
              "the families it actually offers.", file=sys.stderr)
        return 1
    print("\nall faces came from the fonts dir.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("fonts", "style", "probe"))
    ap.add_argument("--fonts")
    ap.add_argument("--family")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--weight", type=int, default=700,
                    help="ASS \\b value; only weights with a matching face render")
    ap.add_argument("--video")
    ap.add_argument("--ass")
    a = ap.parse_args()

    d = resolve_fonts_dir(a.fonts)

    if a.command == "fonts":
        print(json.dumps({
            "fonts_dir": str(d),
            "use_this_family": default_family(d),
            "families": {k: v for k, v in dir_families(d).items()},
        }, indent=2))
        return 0

    if a.command == "style":
        family = a.family or default_family(d)
        if not family:
            sys.exit(f"error: no family name readable in {d} — pass --family")
        # The hint goes to stderr, never into the .ass. A comment line above
        # [Script Info] makes libass reject the whole script: no styles, no
        # font selection, no text — and it fails silently.
        print(f"fontsdir: {d}", file=sys.stderr)
        print(style_block(family, a.width, a.height, a.weight))
        return 0

    if not (a.video and a.ass):
        sys.exit("error: probe needs --video and --ass")
    return probe(Path(a.video), Path(a.ass), d)


if __name__ == "__main__":
    sys.exit(main())
