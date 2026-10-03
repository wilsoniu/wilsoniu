# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "uharfbuzz"]
# ///
"""Builds the profile reel for the README.

    uv run _build/build.py              # assets/card.svg (via card.py) + assets/reel.svg
    uv run _build/build.py --only s4    # _build/.cache/preview-s4.{svg,html}: HUD + one shot

A 12-second motion-graphics loop cut on a 120 BPM grid: six shots (modules in
_build/shots/). Type is outlined (README images can't load
web fonts); motion is CSS keyframes on one shared clock plus SMIL, which both run inside
GitHub's <img> sandbox. Frame 0 is the finished name lockup, so a renderer that doesn't
animate still shows something whole.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
from lib import ACC, BG, DIM, INK, SUB, H, W  # noqa: E402

SHOT_MODULES = [("s1", "s1_name"), ("s2", "s2_role"), ("s3", "s3_tagline"), ("s4", "s4_stack"), ("s5", "s5_now"), ("s6", "s6_studio")]


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

    css = f"""
.ink{{fill:{INK}}}.sub{{fill:{SUB}}}.dim{{fill:{DIM}}}.acc{{fill:{ACC}}}.name{{fill:url(#name)}}
""" + "\n".join(lib.CSS) + "\n" + "".join(f"@keyframes {name}{{{body}}}\n" for body, name in lib.KEYFRAMES.items())

    defs = [
        *(f'<path id="{gid}" d="{d}"/>' for gid, d in lib.GLYPHS.values() if d),
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
        # satin metal: a soft top light rolling into brushed grey, no mirror-chrome band
        '<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="780" x2="0" y2="-80">'
        '<stop offset="0" stop-color="#FCFCFD"/><stop offset=".42" stop-color="#E2E4E8"/><stop offset=".62" stop-color="#BDC1C8"/>'
        '<stop offset=".8" stop-color="#A4A8B0"/><stop offset="1" stop-color="#8C9098"/></linearGradient>',
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
        import card  # the still card shares the toolkit; it resets the registries itself
        card.main()


if __name__ == "__main__":
    main()
