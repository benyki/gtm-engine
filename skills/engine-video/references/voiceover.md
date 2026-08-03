# Voiceover — ElevenLabs (default)

Contract: **same voice id across every arm** of an experiment.
Id lives in this engine's `engine.json` → `video.elevenlabs_voice_id`.
Never invent a new voice mid-test.

Load secrets from the home (never read `.env` into chat):

```bash
set -a; . ~/gtm/shared/.env; set +a
[[ -n "$ELEVENLABS_API_KEY" ]] && echo set
```

## Single script → one file

```bash
VOICE_ID="$(jq -r '.video.elevenlabs_voice_id' engine.json)"
body="$(jq -n --arg t "$SCRIPT" --arg m "eleven_multilingual_v2" \
  '{text:$t, model_id:$m, voice_settings:{stability:0.45, similarity_boost:0.80, style:0.0, use_speaker_boost:true}}')"
curl -sS -X POST \
  "https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}?output_format=mp3_44100_128" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d "$body" -o runs/<run_id>/output/voice.mp3
```

Defaults: model `eleven_multilingual_v2`, output `mp3_44100_128`, settings as above.

## Timed multi-line (no intra-request timing)

ElevenLabs cannot place pauses inside one request. For fixed timestamps
(guess-gap, stingers, multi-beat hooks): **one clip per line**, then lay on a
timeline with ffmpeg `adelay` + `amix`.

Config shape (`runs/<run_id>/voice-timeline.json`):

```json
{
  "voice_id": "",
  "model": "eleven_multilingual_v2",
  "total_seconds": 35,
  "lines": [
    { "id": "hook", "start": 0.0, "text": "Stop scrolling." },
    { "id": "body", "start": 2.5, "text": "Here's the only metric that mattered this week." },
    { "id": "cta", "start": 28.0, "text": "Link in bio — try it once." }
  ]
}
```

Flow:

1. TTS each `lines[].text` → `runs/<run_id>/output/clips/<id>.mp3`
2. Build a silent bed of `total_seconds`
3. `adelay` each clip to `start * 1000` ms; `amix`
4. Optional SFX in gaps from `shared/assets/` (never hardcode personal sound libraries)

Optional full script: install `benyki/skills/elevenlabs` (`timed-multiline.sh`).

## Alignment / captions

Prefer `/v1/text-to-speech/.../with-timestamps` (or the skill's examples) when you
need word-level timing for burned captions. Otherwise write a tight SRT from the
script and burn with `references/ffmpeg-recipes.md`.

## Rules

- Read the script aloud before spending API credits
- Do not clone a real person's voice without explicit permission
- Other TTS is fine if it honors the same-voice contract
