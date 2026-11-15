# Lodavo Video Pipeline

Two-tier video production for Lodavo growth content.

## Structure

```
scripts/          # Generation scripts
  reelgen.py      # FFmpeg volume pipeline (100+ reels/hour)
  reel-content.json  # Reel content definitions (slides, text, timing)
work/             # HyperFrames compositions (high-quality tier)
  lottery-odds-dataviz/   # Dark data-viz style
  lottery-odds-warm/      # Warm editorial card style
reels/            # Rendered output (1080x1920 MP4, 30fps)
```

## Two Pipelines

### Volume: `reelgen.py` (FFmpeg)
Fast text-over-color reels. 6 built-in visual styles.

```bash
python3 scripts/reelgen.py scripts/reel-content.json all reels/
```

Styles: `dark-bold`, `cream-serif`, `neon-pop`, `blueprint`, `warm-minimal`, `ice-data`

### Quality: HyperFrames Compositions
Animated HTML compositions rendered frame-by-frame. GSAP-powered animations,
data visualizations, card transitions.

```bash
hyperframes render work/lottery-odds-dataviz --fps 30 --quality standard
```

## First Reel: Lottery Odds Translator

Turns "1 in 33 million" into something you can picture. 8 slides, 25 seconds.
Rendered in 8 visual styles (6 FFmpeg + 2 HyperFrames).

SEO: "Lotto Max odds explained", "what are the odds of winning the lottery"
