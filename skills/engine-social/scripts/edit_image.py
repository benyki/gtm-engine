#!/usr/bin/env python3
"""Edit an image the user supplied, through an image-generation API.

Optional step. A post ships fine with the picked image untouched — this is for
crops, background swaps, size variants of the *same* asset, and A/B image arms.

Two providers, same command:

    Gemini ("nano banana")   GEMINI_API_KEY   https://aistudio.google.com/apikey
    OpenAI ("gpt-image")     OPENAI_API_KEY   https://platform.openai.com/api-keys

The key is read from the environment, and if it isn't there, from the
home's `.env` — parsed, never printed, never echoed back. Nothing
here writes a key anywhere.

Usage:
    edit_image.py --image inputs/images/dashboard.png \\
                  --prompt "Put this on a plain warm-grey background, 1:1" \\
                  --out runs/2026-07-31-001-social/output/post-1.png

    # several source images (style refs, or a composite), 2 variants
    edit_image.py --image a.png --image b.png --prompt "..." --n 2 --out v.png
    #   → v.png, v-2.png

    edit_image.py --provider openai --size 1024x1024 --quality high ...

Flags:
    --image PATH      source image; repeat for more than one (required)
    --prompt TEXT     what to change — name what stays, not just what moves
    --out PATH        where to write; --n 2+ appends -2, -3, …
    --provider        gemini (default) | openai
    --model           override the default model for the provider
    --aspect          gemini only: 1:1, 4:5, 9:16, 16:9, … (default: unset)
    --size            openai only: auto | 1024x1024 | 1536x1024 | 1024x1536
    --quality         openai only: auto | low | medium | high
    --fidelity        openai only: low | high — how closely to hold the input
    --n               how many variants (default 1)
    --home       the gtm home, if .env isn't found from the cwd
    --timeout         seconds per request (default 180)
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_LEGACY_URL = "https://generativelanguage.googleapis.com/v1beta/models"
OPENAI_URL = "https://api.openai.com/v1/images/edits"

DEFAULT_MODEL = {
    # Nano Banana 2 — fast and cheap. `gemini-3-pro-image` is the pro tier;
    # `gemini-2.5-flash-image` is the older one, still served.
    "gemini": "gemini-3.1-flash-image",
    "openai": "gpt-image-2",
}
KEY_VAR = {"gemini": "GEMINI_API_KEY", "openai": "OPENAI_API_KEY"}
KEY_HELP = {
    "gemini": "https://aistudio.google.com/apikey  (sign in → Create API key)",
    "openai": "https://platform.openai.com/api-keys  (may need org verification)",
}


# --- key ---------------------------------------------------------------------

def read_env_file(path: Path, name: str) -> str:
    """Pull ONE variable out of a .env. The value is returned, never printed."""
    if not path.is_file():
        return ""
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip().removeprefix("export ").strip() == name:
            return v.strip().strip('"').strip("'")
    return ""


def api_key(provider: str, home: str | None) -> str:
    name = KEY_VAR[provider]
    key = (os.environ.get(name) or "").strip()
    if key:
        return key
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "engine-loop" / "scripts"))
        from gtmfind import find_home  # noqa: PLC0415
        ws = find_home(home)
    except (ImportError, SystemExit):
        ws = None
    if ws:
        # .env sits at the root of the home; v1 homes keep it in shared/.
        for cand in (ws / ".env", ws / "shared" / ".env"):
            key = read_env_file(cand, name)
            if key:
                break
    if not key:
        sys.exit(
            f"error: no {name}.\n"
            f"  Get one: {KEY_HELP[provider]}\n"
            f"  Then paste it into your home's .env as {name}=…\n"
            f"  (paste it yourself — never into a chat window)"
        )
    return key


# --- shared ------------------------------------------------------------------

def load_images(paths: list[str]) -> list[tuple[Path, str, bytes]]:
    out = []
    for p in paths:
        f = Path(p).expanduser()
        if not f.is_file():
            sys.exit(f"error: no such image: {f}")
        mime = mimetypes.guess_type(f.name)[0] or "image/png"
        if not mime.startswith("image/"):
            sys.exit(f"error: {f} is not an image ({mime})")
        out.append((f, mime, f.read_bytes()))
    return out


def find_images(node) -> list[bytes]:
    """Walk a response and collect every base64 image payload in it.

    Deliberately shape-agnostic: these APIs have moved their envelope more than
    once (`candidates[].content.parts[].inlineData` → `steps[].content[]`), and
    a picture that arrives is worth more than a parser that was right last year.
    """
    found: list[bytes] = []

    def walk(n):
        if isinstance(n, dict):
            for key in ("data", "b64_json", "bytesBase64Encoded"):
                v = n.get(key)
                if isinstance(v, str) and len(v) > 256:
                    mime = str(n.get("mime_type") or n.get("mimeType") or "image/")
                    if mime.startswith("image/") or key == "b64_json":
                        try:
                            found.append(base64.b64decode(v, validate=True))
                            return
                        except (ValueError, TypeError):
                            pass
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    walk(node)
    return found


def post_raw(url: str, data: bytes, headers: dict, timeout: int) -> tuple[int, str]:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")
    except urllib.error.URLError as e:
        sys.exit(f"error: could not reach {url}: {e.reason}")


def post(url: str, data: bytes, headers: dict, timeout: int) -> dict:
    status, body = post_raw(url, data, headers, timeout)
    if status >= 400:
        sys.exit(f"error: {url} returned {status}\n{body[:600]}")
    return json.loads(body)


# --- providers ---------------------------------------------------------------

def call_gemini(a, images, key) -> list[bytes]:
    """Current endpoint first, classic generateContent as the fallback.

    Google moved image generation onto /v1beta/interactions; the older
    models/<model>:generateContent still serves the same models. If the new
    one isn't there (404) or doesn't know this model, drop to the old one
    rather than failing a run over an envelope change.
    """
    headers = {"Content-Type": "application/json", "x-goog-api-key": key}
    b64 = [(mime, base64.b64encode(raw).decode()) for _, mime, raw in images]

    body = {
        "model": a.model,
        "input": [{"type": "text", "text": a.prompt}]
             + [{"type": "image", "mime_type": m, "data": d} for m, d in b64],
        "response_format": {"type": "image"},
    }
    if a.aspect:
        body["response_format"]["aspect_ratio"] = a.aspect
    status, raw = post_raw(GEMINI_URL, json.dumps(body).encode(), headers, a.timeout)

    if status in (404, 405) or (status >= 400 and "not found" in raw.lower()):
        legacy = {
            "contents": [{"parts":
                [{"inlineData": {"mimeType": m, "data": d}} for m, d in b64]
                + [{"text": a.prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }
        if a.aspect:
            legacy["generationConfig"]["imageConfig"] = {"aspectRatio": a.aspect}
        url = f"{GEMINI_LEGACY_URL}/{a.model}:generateContent"
        print(f"note: {GEMINI_URL} said {status}; retrying on {url}", file=sys.stderr)
        status, raw = post_raw(url, json.dumps(legacy).encode(), headers, a.timeout)

    if status >= 400:
        sys.exit(f"error: Gemini returned {status}\n{raw[:600]}")
    return find_images(json.loads(raw))


def multipart(fields: list[tuple[str, str]], files: list[tuple[str, Path, str, bytes]]) -> tuple[bytes, str]:
    boundary = f"----gtm{uuid.uuid4().hex}"
    buf = bytearray()
    for name, value in fields:
        buf += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
    for name, path, mime, raw in files:
        buf += (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; "
            f"filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n"
        ).encode()
        buf += raw + b"\r\n"
    buf += f"--{boundary}--\r\n".encode()
    return bytes(buf), f"multipart/form-data; boundary={boundary}"


def call_openai(a, images, key) -> list[bytes]:
    fields = [("model", a.model), ("prompt", a.prompt), ("n", str(a.n))]
    if a.size:
        fields.append(("size", a.size))
    if a.quality:
        fields.append(("quality", a.quality))
    if a.fidelity:
        fields.append(("input_fidelity", a.fidelity))
    # One image goes in `image`; several go in `image[]`.
    field = "image" if len(images) == 1 else "image[]"
    files = [(field, path, mime, raw) for path, mime, raw in images]
    data, content_type = multipart(fields, files)
    res = post(
        OPENAI_URL,
        data,
        {"Content-Type": content_type, "Authorization": f"Bearer {key}"},
        a.timeout,
    )
    return find_images(res)


# --- main --------------------------------------------------------------------

def out_paths(out: Path, count: int) -> list[Path]:
    if count <= 1:
        return [out]
    return [out] + [out.with_name(f"{out.stem}-{i}{out.suffix}") for i in range(2, count + 1)]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image", action="append", required=True,
                    help="source image; repeat for more than one")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--provider", choices=("gemini", "openai"), default="gemini")
    ap.add_argument("--model", default="")
    ap.add_argument("--aspect", default="", help="gemini only, e.g. 1:1 4:5 9:16")
    ap.add_argument("--size", default="", help="openai only")
    ap.add_argument("--quality", default="", help="openai only")
    ap.add_argument("--fidelity", choices=("low", "high"), default="")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--home", default=None)
    ap.add_argument("--timeout", type=int, default=180)
    a = ap.parse_args()

    if a.n < 1:
        sys.exit("error: --n must be at least 1")
    a.model = a.model or DEFAULT_MODEL[a.provider]
    images = load_images(a.image)
    key = api_key(a.provider, a.home)

    if a.provider == "openai":
        blobs = call_openai(a, images, key)
    else:
        # One interaction per variant — the endpoint returns a single image.
        blobs = []
        for _ in range(a.n):
            blobs += call_gemini(a, images, key)

    if not blobs:
        sys.exit("error: the API returned no image. Usually the prompt was "
                 "refused (people, brands, anything it reads as a real "
                 "photo of a real person) — reword it and try once more.")

    out = Path(a.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for path, blob in zip(out_paths(out, len(blobs)), blobs):
        path.write_bytes(blob)
        written.append(path)
        print(path)
    print(f"{len(written)} image(s) from {a.provider}/{a.model}. "
          f"The source files were not touched.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
