#!/usr/bin/env python3
"""reelgen.py — Fast ffmpeg-based reel generator for volume production."""
import json, subprocess, sys
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

def esc(s):
    out = []
    for ch in s:
        if ch in ("'", ":", "\\", "[", "]", ";", ","):
            out.append("\\" + ch)
        elif ch == "%":
            out.append("%%")
        else:
            out.append(ch)
    return "".join(out)

def build_vf(slides, style):
    parts, t = [], 0
    for slide in slides:
        text = "\\n".join(esc(l) for l in slide["text"].split("\n"))
        sub = esc(slide.get("sub", ""))
        dur = slide.get("duration", 3)
        end = t + dur
        parts.append(
            f"drawtext=text='{text}':font={style['font']}:fontsize={style['size']}"
            f":fontcolor={style['text']}:x=(w-text_w)/2:y=(h/2)-100"
            f":enable='between(t\\,{t}\\,{end})'"
        )
        if sub:
            parts.append(
                f"drawtext=text='{esc(sub)}':font={style['font']}:fontsize={style['sub_size']}"
                f":fontcolor={style['sub']}:x=(w-text_w)/2:y=(h/2)+60"
                f":enable='between(t\\,{t}\\,{end})'"
            )
        t = end
    return ",".join(parts), t

def render(content_path, style_name, outdir):
    style = STYLES[style_name]
    with open(content_path) as f:
        data = json.load(f)
    slug = Path(content_path).stem
    outfile = outdir / f"{slug}-{style_name}.mp4"
    vf, dur = build_vf(data["slides"], style)
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i",
           f"color=c={style['bg']}:s=1080x1920:d={dur}:r=30",
           "-vf", vf, "-c:v", "libx264", "-preset", "fast",
           "-crf", "18", "-pix_fmt", "yuv420p", "-t", str(dur), str(outfile)]
    print(f"  {style_name}: {len(data['slides'])} slides, {dur}s", end=" ", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL"); print(r.stderr[-400:]); return None
    print(f"→ {outfile.name} ({outfile.stat().st_size/1024:.0f} KB)")
    return outfile

def main():
    content, style_name = sys.argv[1], sys.argv[2]
    outdir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(content).parent / "reels"
    outdir.mkdir(parents=True, exist_ok=True)
    styles = list(STYLES) if style_name == "all" else [style_name]
    print(f"Rendering {len(styles)} style(s)")
    ok = [render(content, s, outdir) for s in styles]
    ok = [x for x in ok if x]
    print(f"\n✓ {len(ok)}/{len(styles)} rendered to {outdir}/")

if __name__ == "__main__":
    main()
