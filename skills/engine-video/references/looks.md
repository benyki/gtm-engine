# Looks — optional post-process filters

Apply **after** the base 9:16 render, before loudnorm if the filter touches audio.
Stack 2–3 max; one alone often looks like a gimmick.

Paths below are recipes — run with your `ffmpeg` binary. Inputs/outputs under
`runs/<run_id>/output/`.

## When

- Stock or AI footage looks too clean / "template-y"
- You want a consistent house look across arms (then keep the **same** look on both arms)

## Named looks

### 1. `phone-filmed`

Slight rotate, crop, contrast, vignette, light grain + phone-ish EQ.

```bash
ffmpeg -y -i in.mp4 -vf "
scale=1080:1920,
rotate=0.015:c=black:ow=rotw(0.015):oh=roth(0.015),
crop=iw-20:ih-40,scale=1080:1920,
eq=contrast=1.1:brightness=-0.02:saturation=0.9,
noise=alls=10:allf=t,
vignette=PI/4.5
" -af "highpass=f=200,lowpass=f=3500,acompressor=threshold=-20dB:ratio=4" \
  -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 96k -movflags +faststart out-phone.mp4
```

### 2. `grain`

```bash
ffmpeg -y -i in.mp4 -vf "noise=alls=18:allf=t+u" \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart out-grain.mp4
```

### 3. `soft-downup` (hide fine AI artifacts)

Down to ~540p then back up:

```bash
ffmpeg -y -i in.mp4 \
  -vf "scale=-2:540,scale=1080:1920:flags=lanczos,format=yuv420p" \
  -c:v libx264 -preset veryfast -crf 20 \
  -c:a copy -movflags +faststart out-soft.mp4
```

### 4. `solid-box-caption`

Burn a hook in a solid box (~25% from top). Strong when B-roll is busy.

```bash
# White box, dark text — adjust text= and fontsize to taste
ffmpeg -y -i in.mp4 -vf "
drawbox=x=(iw-text_w)/2-24:y=ih*0.22:w=text_w+48:h=text_h+28:color=white@0.92:t=fill,
drawtext=text='YOUR HOOK HERE':fontcolor=black:fontsize=48:\
x=(w-text_w)/2:y=h*0.22+14:font='Helvetica'
" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart out-caption.mp4
```

Prefer ASS for wrapping/long hooks (`references/ffmpeg-recipes.md`).

### 5. `punch-zoom`

Subtle zoom-in over a window (e.g. 2s–5s), then ease back — energy on B-roll.

```bash
# Approximate: continuous slow zoom 1.0 → 1.25 over full clip (tune for beats)
ffmpeg -y -i in.mp4 \
  -vf "scale=1080*1.25:1920*1.25,zoompan=z='min(zoom+0.0015,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30" \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
  -an -movflags +faststart out-zoom.mp4
```

Re-attach audio from `in.mp4` after if needed.

## A/B rule

Looks are production polish. If an experiment is about **hook copy**, keep the look
identical across arms. If the experiment *is* the look, name the arm after it
(`phone-filmed` vs `clean`) and hold script constant.

Full filter skill: `benyki/skills/video-filter`.
