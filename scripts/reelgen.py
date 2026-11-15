#!/usr/bin/env python3
"""reelgen.py — Fast ffmpeg-based reel generator for volume production.

Usage: python3 reelgen.py <content.json> <style> [output_dir]
       python3 reelgen.py <content.json> all [output_dir]   # render all 6 styles
Styles: dark-bold, cream-serif, neon-pop, blueprint, warm-minimal, ice-data
Output: 1080x1920 MP4 at 30fps
"""
import json, subprocess, sys, tempfile
from pathlib import Path

STYLES = {
    "dark-bold": {
        "bg": "#0A0A0A", "text": "#FFFFFF", "sub": "#FFD700",
        "font": "Helvetica-Bold", "size": 72, "sub_size": 48,
    },
    "cream-serif": {
        "bg": "#FAF4ED", "text": "#1A1A1A", "sub": "#8B6914",
        "font": "Georgia", "size": 68, "sub_size": 44,
    },
    "neon-pop": {
        "bg": "#0F0A1F", "text": "#00FF88", "sub": "#FF3366",
        "font": "Helvetica-Bold", "size": 76, "sub_size": 50,
    },
    "blueprint": {
        "bg": "#0B1929", "text": "#E8F4FD", "sub": "#4DA6FF",
        "font": "Courier-Bold", "size": 64, "sub_size": 42,
    },
    "warm-minimal": {
        "bg": "#F5E6D3", "text": "#2C1810", "sub": "#D4A847",
        "font": "Helvetica", "size": 66, "sub_size": 44,
    },
    "ice-data": {
        "bg": "#0D1117", "text": "#C9D1D9", "sub": "#58A6FF",
        "font": "Menlo-Bold", "size": 60, "sub_size": 40,
    },
}


def esc(s: str) -> str:
    """Escape for ffmpeg drawtext within -vf. Must escape: ' : \\ [ ] ; , %"""
    out = []
    for ch in s:
        if ch in ("'", ":", "\\", "[", "]", ";", ","):
            out.append("\\" + ch)
        elif ch == "%":
            out.append("%%")
        else:
            out.append(ch)
    return "".join(out)


def build_filtergraph(slides: list, style: dict) -> tuple[str, int]:
    """Build a filtergraph string for -vf."""
    lines = []
    t = 0
    for slide in slides:
        text_lines = slide["text"].split("\n")
        text = "\\n".join(esc(l) for l in text_lines)
        sub = esc(slide.get("sub", ""))
        dur = slide.get("duration", 3)
        end = t + dur

        lines.append(
            f"drawtext=text='{text}'"
            f":font={style['font']}:fontsize={style['size']}"
            f":fontcolor={style['text']}:x=(w-text_w)/2:y=(h/2)-100"
            f":enable='between(t\\,{t}\\,{end})'"
        )
        if sub:
            lines.append(
                f"drawtext=text='{sub}'"
                f":font={style['font']}:fontsize={style['sub_size']}"
                f":fontcolor={style['sub']}:x=(w-text_w)/2:y=(h/2)+60"
                f":enable='between(t\\,{t}\\,{end})'"
            )
        t = end
    return ",".join(lines), t


def render_one(content_path: str, style_name: str, outdir: Path) -> Path:
    style = STYLES[style_name]
    with open(content_path) as f:
        data = json.load(f)

    slug = Path(content_path).stem
    outfile = outdir / f"{slug}-{style_name}.mp4"

    vf_str, total_dur = build_filtergraph(data["slides"], style)

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={style['bg']}:s=1080x1920:d={total_dur}:r=30",
        "-vf", vf_str,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-t", str(total_dur),
        str(outfile),
    ]

    print(f"  {style_name}: {len(data['slides'])} slides, {total_dur}s", end=" ", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"FAIL")
        print(result.stderr[-800:])
        return None

    size = outfile.stat().st_size / 1024
    print(f"→ {outfile.name} ({size:.0f} KB)")
    return outfile


def main():
    content_path = sys.argv[1]
    style_name = sys.argv[2]
    outdir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(content_path).parent.parent / "reels"
    outdir.mkdir(parents=True, exist_ok=True)

    if style_name == "all":
        styles_to_render = list(STYLES.keys())
    elif style_name not in STYLES:
        print(f"Unknown style: {style_name}. Available: {', '.join(STYLES)}, all")
        sys.exit(1)
    else:
        styles_to_render = [style_name]

    print(f"Rendering {len(styles_to_render)} style(s) from {Path(content_path).name}")
    results = []
    for s in styles_to_render:
        out = render_one(content_path, s, outdir)
        if out:
            results.append(out)

    print(f"\n✓ {len(results)}/{len(styles_to_render)} reels rendered to {outdir}/")


if __name__ == "__main__":
    main()
