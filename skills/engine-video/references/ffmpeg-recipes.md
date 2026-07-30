# ffmpeg recipes — engine-video defaults

Resolve binaries in order: `$FFMPEG_BIN` / `$FFPROBE_BIN`, then
`/opt/homebrew/bin/ffmpeg`, then `PATH`. Prefer a Homebrew build with **libass**
for captions.

All finals: H.264 + AAC + `yuv420p` + `-movflags +faststart`.
Target canvas from this workflow's `workflow.json` → `video.resolution` (default `1080x1920`).

## Probe

```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 input.mp4

ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt \
  -of default=noprint_wrappers=1 input.mp4
```

## Crop / zoom-fill to 9:16 (1080×1920)

Fills the frame (no letterbox):

```bash
ffmpeg -y -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p" \
  -c:v libx264 -preset veryfast -crf 20 \
  -c:a aac -b:a 128k -movflags +faststart \
  out-9x16.mp4
```

Pad (letterbox) instead when you must keep the full frame:

```bash
ffmpeg -y -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -c:v libx264 -preset veryfast -crf 20 \
  -c:a aac -b:a 128k -movflags +faststart \
  out-padded.mp4
```

## Trim

```bash
ffmpeg -y -i input.mp4 -ss 00:00:01 -t 15 \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart \
  clip.mp4
```

## Concat demuxer (same codec)

```bash
# list.txt:
# file 'a.mp4'
# file 'b.mp4'
ffmpeg -y -f concat -safe 0 -i list.txt -c copy concat.mp4
```

Re-encode if codecs/resolutions differ.

## Mix voiceover + bed

```bash
ffmpeg -y -i video.mp4 -i voice.wav -i bed.mp3 \
  -filter_complex "
    [1:a]loudnorm=I=-14:TP=-1.5:LRA=11[v0];
    [2:a]volume=0.15[b];
    [v0][b]amix=inputs=2:duration=first:dropout_transition=2[a]
  " \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 128k -shortest \
  -movflags +faststart mixed.mp4
```

## Burn captions (SRT)

```bash
ffmpeg -y -i input.mp4 -vf "subtitles=captions.srt:force_style='Fontsize=22,Outline=2'" \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart captioned.mp4
```

Prefer ASS / libass for precise styling. Avoid relying on platform auto-captions.

## Loudnorm to −14 LUFS (final audio pass)

```bash
ffmpeg -y -i input.mp4 \
  -af loudnorm=I=-14:TP=-1.5:LRA=11 \
  -c:v copy -c:a aac -b:a 128k -movflags +faststart \
  final.mp4
```

## Still frame (poster / thumbnail)

```bash
ffmpeg -y -ss 1.2 -i final.mp4 -frames:v 1 -q:v 2 poster.jpg
```

For richer filters and UGC looks, see `references/looks.md`.
For the full ffmpeg skill, install `benyki/skills/ffmpeg`.
