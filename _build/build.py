# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "uharfbuzz"]
# ///
"""Builds the profile reel for the README.

    uv run _build/build.py              # assets/reel.svg
    uv run _build/build.py --only s4    # _build/.cache/preview-s4.{svg,html}: HUD + one shot

A 12-second motion-graphics loop cut on a 120 BPM grid: six shots (modules in
_build/shots/) inside a camera-viewfinder HUD. Type is outlined (README images can't load
web fonts); motion is CSS keyframes on one shared clock plus SMIL, which both run inside
GitHub's <img> sandbox. Frame 0 is the finished name lockup, so a renderer that doesn't
animate still shows something whole.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
from lib import ACC, BG, DIM, INK, RULE, SUB, H, T, W, X0, X1, num, text, label, width, show  # noqa: E402

SHOT_MODULES = [("s1", "s1_name"), ("s2", "s2_role"), ("s3", "s3_tagline"), ("s4", "s4_stack"), ("s5", "s5_now"), ("s6", "s6_studio")]
NAMES = {"s1": "NAME", "s2": "ROLE", "s3": "TAGLINE", "s4": "STACK", "s5": "NOW", "s6": "STUDIO"}


def hud(keys: list[str]) -> str:
    b = []
    m, L = 36, 16
    corners = "".join(f"M{x} {y + L * sy}V{y}H{x + L * sx}" for x, y, sx, sy in
                      ((m, 56, 1, 1), (W - m, 56, -1, 1), (m, 540, 1, -1), (W - m, 540, -1, -1)))
    b.append(f'<path class="hud-bracket" d="{corners}"/>')
    b.append(f'<circle class="hud-rec" cx="{X0 - 6}" cy="30" r="3.6" fill="{ACC}"/>')
    b.append(text("mono_md", "REC", 9.5, X0 + 4, 33.5, "ink", 0.16))
    b.append(label("WILSONIU — REEL 2026", X0 + 4 + width("mono_md", "REC ", 9.5, 0.16) + 10, 33.5))
    # shot index, cut with the shots
    for key in keys:
        t0, t1 = lib.SHOTS[key]
        body = label(f"SHOT 0{key[1:]}", W / 2 - 4, 33.5, "ink", "end") + label(NAMES[key], W / 2 + 6, 33.5, "dim")
        b.append(show(body, t0, t1, din=0.05, dout=0.05, ein="linear", eout="linear") if len(keys) > 1 else body)
    # timecode: digit strips stepped by CSS (seconds over the loop, frames 00-23 each second)
    size, step = 9.5, 14
    wd = width("mono_md", "00", size, 0.16)
    colon = width("mono_md", ":", size, 0.16) + size * 0.16
    x_ff = X1 - wd
    x_ss = x_ff - colon - wd
    b.append(text("mono_md", "TC 00:00:", size, x_ss - size * 0.16, 33.5, "sub", 0.16, "end"))
    b.append(text("mono_md", ":", size, x_ff - colon, 33.5, "sub", 0.16))
    for key, x, count, dur in (("ss", x_ss, int(T), T), ("ff", x_ff, 24, 1)):
        strip = "".join(text("mono_md", f"{i:02d}", size, x, 33.5 + i * step, "ink", 0.16) for i in range(count))
        b.append(f'<clipPath id="hud-tc-{key}"><rect x="{num(x - 1)}" y="24" width="{num(wd + 2)}" height="12"/></clipPath>'
                 f'<g clip-path="url(#hud-tc-{key})"><g style="animation:hud-{key} {num(dur)}s steps({count}) infinite">{strip}</g></g>')
        lib.add_css(f"@keyframes hud-{key}{{to{{transform:translateY(-{count * step}px)}}}}")
    # bottom: progress with beat ticks, links
    ticks = "".join(f"M{num(round(X0 + (X1 - X0) * i * lib.BEAT / T) + 0.5)} 553V{559 if i % 4 == 0 else 557}"
                    for i in range(int(T / lib.BEAT) + 1))
    b.append(f'<path class="hud-tick" d="{ticks}"/><path class="hud-rule" d="M{X0} 552.5H{X1}"/>')
    b.append(f'<path d="M{X0} 552.5H{X1}" stroke="{ACC}" style="animation:hud-progress {num(T)}s linear infinite;transform-origin:{X0}px 552px"/>')
    b.append(label("WILSONIU.COM  ·  @WILSONIUDESIGN", X1, 580, "sub", "end", size=8.5))
    b.append(label("CYTE LAB / EXPERIENCE DESIGN", X0, 580, "dim", size=8.5))
    return "".join(b)


def compose(keys: list[str]) -> str:
    shots = []
    for key, module in SHOT_MODULES:
        if key not in keys:
            continue
        try:
            mod = importlib.import_module(f"shots.{module}")
        except ModuleNotFoundError:
            print(f"  (skipping {key}: shots/{module}.py not written yet)")
            continue
        shots.append(f'<g id="{key}">{mod.build()}</g>')
    frame = hud(keys)

    css = f"""
.ink{{fill:{INK}}}.sub{{fill:{SUB}}}.dim{{fill:{DIM}}}.acc{{fill:{ACC}}}.name{{fill:url(#name)}}
.hud-bracket{{stroke:{DIM};stroke-width:1.2;fill:none}}
.hud-rule{{stroke:{RULE};stroke-width:1;fill:none}}
.hud-tick{{stroke:{DIM};stroke-width:1;fill:none}}
.hud-rec{{animation:hud-rec 1s steps(1) infinite}}
@keyframes hud-rec{{50%{{opacity:.2}}}}
@keyframes hud-progress{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
""" + "\n".join(lib.CSS) + "\n" + "".join(f"@keyframes {name}{{{body}}}\n" for body, name in lib.KEYFRAMES.items())

    defs = [
        *(f'<path id="{gid}" d="{d}"/>' for gid, d in lib.GLYPHS.values() if d),
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
        '<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="760" x2="0" y2="-120"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#767A83"/></linearGradient>',
        *lib.DEFS,
    ]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="wilsoniu — experience designer at CYTE LAB. A 12-second motion reel.">',
        "<title>wilsoniu — reel</title>",
        f"<style>{css}</style>",
        f"<defs>{''.join(defs)}</defs>",
        '<g clip-path="url(#frame)">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        *shots,
        frame,
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="17.5" fill="none" stroke="#fff" stroke-opacity=".08"/>',
        "</g>",
        "</svg>",
    ])


def main():
    lib.init()
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    keys = [only] if only else [k for k, _ in SHOT_MODULES]
    svg = compose(keys)
    if only:
        out = lib.CACHE / f"preview-{only}.svg"
        out.write_text(svg)
        page = lib.CACHE / f"preview-{only}.html"
        page.write_text(f'<!doctype html><body style="margin:0;background:#0d1117;padding:16px">'
                        f'<img src="preview-{only}.svg" width="{W}" style="display:block"></body>')
        print(f"{out}  {out.stat().st_size / 1024:.0f} KB\nview: file://{page}")
    else:
        out = lib.ROOT / "assets" / "reel.svg"
        out.write_text(svg)
        print(f"{out.relative_to(lib.ROOT)}  {out.stat().st_size / 1024:.0f} KB  {len(lib.KEYFRAMES)} keyframes")


if __name__ == "__main__":
    main()
