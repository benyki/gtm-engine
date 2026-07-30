# Remotion — when the render is React

Default path for this workflow is ffmpeg + floating text
(`references/floating-text.md`). Use Remotion when you need real composition:
animated type, sequenced scenes, React-driven layout, or a house design system
in code.

Scaffold (empty folder):

```bash
npx create-video@latest --yes --blank --no-tailwind my-video
```

## Hard rules

- Animate with `useCurrentFrame()` + `interpolate()` (+ `Easing`) — **never** CSS
  transitions/animations or Tailwind `animate-*` (they won't render)
- Put media in `public/`; reference with `staticFile()`
- Images: `<Img src={staticFile("…")} />`
- Video/audio: `@remotion/media` `<Video>` / `<Audio>`
- Prefer `<Sequence>` for timing; keep compositions explicit

## Minimal fade-in

```tsx
import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";

export const FadeIn = ({ children }: { children: React.ReactNode }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [0, 2 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return <div style={{ opacity }}>{children}</div>;
};
```

## Fit with engine-video

1. Still write `runs/<run_id>/plan.json` first (`references/structure-plan.md`)
2. Remotion composition implements the segments
3. Render to `runs/<run_id>/output/final.mp4` (same contract as ffmpeg path)
4. Same voice file / loudnorm / posting rules

## Optional deeper pack

Install `benyki/skills/remotion-best-practices` for captions, transitions,
voiceover sync, 3D, etc. Keep that knowledge out of the critical path until you
need it.
