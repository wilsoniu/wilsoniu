# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "uharfbuzz"]
# ///
"""The still card at the top of the profile.

    uv run _build/card.py     # assets/card.svg

Name, role, links and the whole tool stack, so everything worth reading is in one place;
the animated reel underneath is built by build.py. Pure black, white and satin metal.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
from lib import mark, num, text, width  # noqa: E402

BG, INK, SUB, DIM, RULE = "#000000", "#F5F5F5", "#8E9199", "#55575E", "#232328"
W = 960

# Six balanced groups so the whole stack reads at a glance.
GROUPS = [
    ("Design", [("Figma", "si:figma", ""), ("Framer", "si:framer", ""), ("Photoshop", None, "Ps"), ("Illustrator", None, "Ai"), ("Canva", None, "Cv")]),
    ("Motion", [("After Effects", None, "Ae"), ("Premiere Pro", None, "Pr"), ("DaVinci Resolve", "si:davinciresolve", ""), ("Final Cut Pro", None, "Fc"), ("Motion", None, "Mo")]),
    ("3D", [("Blender", "si:blender", ""), ("Unreal Engine", "si:unrealengine", ""), ("Spline", None, "Sp")]),
    ("AI", [("Claude Code", "si:claude", ""), ("OpenAI", "iconify:ri/openai-fill", ""), ("Grok", "iconify:thesvg/grok-xai", ""),
            ("Manus", "iconify:thesvg-color/manus-dark", ""), ("Cursor", "si:cursor", "")]),
    ("Code", [("VS Code", "iconify:devicon-plain/vscode", ""), ("Xcode", "si:xcode", ""), ("GitHub", "si:github", ""), ("Git", "si:git", "")]),
    ("Ship", [("Linear", "si:linear", ""), ("Notion", "si:notion", ""), ("Webflow", "si:webflow", ""), ("Firebase", "si:firebase", ""), ("Replit", "si:replit", "")]),
]

# Satin metal: a soft top light rolling into brushed grey (same as the reel's name).
SATIN = ('<linearGradient id="satin" gradientUnits="userSpaceOnUse" x1="0" y1="780" x2="0" y2="-80">'
         '<stop offset="0" stop-color="#FCFCFD"/><stop offset=".42" stop-color="#E2E4E8"/><stop offset=".62" stop-color="#BDC1C8"/>'
         '<stop offset=".8" stop-color="#A4A8B0"/><stop offset="1" stop-color="#8C9098"/></linearGradient>')


# The knob is turned by a hand that never stops: quick decisive moves with a small mechanical
# overshoot, short rests between them, one full revolution per loop so the loop is seamless.
_TURN = "cubic-bezier(.3,1.35,.45,1)"
KNOB_CSS = (".knob-turn{animation:knob-turn 7s infinite}"
            "@keyframes knob-turn{"
            f"0%{{transform:rotate(0deg);animation-timing-function:{_TURN}}}"
            f"9%,22%{{transform:rotate(128deg);animation-timing-function:{_TURN}}}"
            f"30%,44%{{transform:rotate(46deg);animation-timing-function:{_TURN}}}"
            f"55%,66%{{transform:rotate(232deg);animation-timing-function:{_TURN}}}"
            f"74%,84%{{transform:rotate(196deg);animation-timing-function:{_TURN}}}"
            "96%,100%{transform:rotate(360deg)}}")


def document(w: int, h: int, title: str, defs: list[str], body: list[str]) -> str:
    glyphs = [f'<path id="{gid}" d="{d}"/>' for gid, d in lib.GLYPHS.values() if d]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">',
        f"<title>{title}</title>",
        f"<style>.ink{{fill:{INK}}}.sub{{fill:{SUB}}}.dim{{fill:{DIM}}}.satin{{fill:url(#satin)}}{KNOB_CSS}</style>",
        f"<defs>{''.join(glyphs + defs)}</defs>",
        f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="20"/></clipPath>',
        f'<g clip-path="url(#frame)"><rect width="{w}" height="{h}" fill="{BG}"/>',
        *body,
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="19.5" fill="none" stroke="#fff" stroke-opacity=".08"/></g>',
        "</svg>",
    ])


# ---------------------------------------------------------------- the knob

def grey(v: float) -> str:
    c = max(0, min(255, round(v * 255)))
    return f"#{c:02X}{c:02X}{min(255, c + 4):02X}"


def knob(cx: float, cy: float, r: float) -> tuple[str, list[str]]:
    """A concentric-brushed aluminium knob lit from the upper left.

    Circular brushing scatters light into a bow-tie highlight along the light axis, so the
    top face is built from thin wedges whose brightness follows that lobe (SVG has no
    conic gradient). Faint irregular rings give the grain; a chamfer catches the light on
    one side and falls into shadow on the other; the indicator is an engraved groove.
    """
    light = math.radians(-135)  # from the upper left
    wedges = []
    n = 144
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1.35) / n   # slight overlap hides seams
        c = abs(math.cos((a0 + a1) / 2 - light))
        v = 0.50 + 0.36 * c ** 7 + 0.10 * c ** 1.5
        x0, y0, x1, y1 = r * math.cos(a0), r * math.sin(a0), r * math.cos(a1), r * math.sin(a1)
        wedges.append(f'<path d="M0 0L{num(x0)} {num(y0)}A{r} {r} 0 0 1 {num(x1)} {num(y1)}Z" fill="{grey(v)}"/>')
    rings = []
    for i in range(1, 60):
        rr = r * i / 60
        jitter = (math.sin(i * 12.9898) * 43758.5453) % 1          # deterministic noise
        rings.append(f'<circle r="{num(rr)}" fill="none" stroke="{"#fff" if jitter > .5 else "#000"}" '
                     f'stroke-opacity="{0.015 + 0.045 * abs(jitter - .5) * 2:.3f}" stroke-width=".7"/>')
    defs = [
        '<radialGradient id="knob-shadow" cy=".56"><stop offset=".55" stop-color="#000" stop-opacity=".6"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>',
        '<linearGradient id="knob-skirt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A3B40"/><stop offset="1" stop-color="#141417"/></linearGradient>',
        '<linearGradient id="knob-chamfer" x1=".15" y1=".1" x2=".85" y2=".9"><stop offset="0" stop-color="#fff" stop-opacity=".85"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient>',
        '<radialGradient id="knob-dimple" cx=".42" cy=".38"><stop offset="0" stop-color="#000" stop-opacity=".22"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>',
        '<linearGradient id="knob-dimple-edge" x1=".15" y1=".1" x2=".85" y2=".9"><stop offset="0" stop-color="#000" stop-opacity=".35"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity=".55"/></linearGradient>',
    ]
    a = math.radians(-58)
    knurl = '<path stroke="#000" stroke-opacity=".55" stroke-width="1.1" d="' + "".join(
        f"M{num((r + 2) * math.cos(t))} {num((r + 2) * math.sin(t))}L{num((r + 6.5) * math.cos(t))} {num((r + 6.5) * math.sin(t))}"
        for t in (math.radians(d) for d in range(0, 360, 6))) + '"/>'
    # a fixed scale around the knob, so every turn reads
    scale = '<path stroke="#fff" stroke-opacity=".28" stroke-width="1" d="' + "".join(
        f"M{num((r + 13) * math.cos(t))} {num((r + 13) * math.sin(t))}L{num((r + (19 if k % 5 == 0 else 16)) * math.cos(t))} {num((r + (19 if k % 5 == 0 else 16)) * math.sin(t))}"
        for k, t in ((k, math.radians(-90 + k * 7.5)) for k in range(48))) + '"/>'
    ind = f'M{num(r * .5 * math.cos(a))} {num(r * .5 * math.sin(a))}L{num(r * .8 * math.cos(a))} {num(r * .8 * math.sin(a))}'
    body = (
        f'<g transform="translate({cx} {cy})">'
        f'<ellipse rx="{num(r * 1.22)}" ry="{num(r * 1.16)}" cy="10" fill="url(#knob-shadow)"/>{scale}'
        f'<circle r="{num(r + 7)}" fill="url(#knob-skirt)"/><circle r="{num(r + 6.5)}" fill="none" stroke="#fff" stroke-opacity=".12"/>'
        + "".join(wedges) + "".join(rings)
        + f'<circle r="{num(r - 0.8)}" fill="none" stroke="url(#knob-chamfer)" stroke-width="1.6"/>'
        f'<circle r="{num(r * .3)}" fill="url(#knob-dimple)"/><circle r="{num(r * .3)}" fill="none" stroke="url(#knob-dimple-edge)" stroke-width="1"/>'
        # what turns: the engraved groove and the knurled skirt. The light lip of the groove is
        # offset in screen space (outside the rotation) so it always faces the fixed light.
        f'<g transform="translate(.5 .8)"><g class="knob-turn"><path d="{ind}" stroke="#fff" stroke-opacity=".55" stroke-width="3.4" stroke-linecap="round"/></g></g>'
        f'<g class="knob-turn"><path d="{ind}" stroke="#2B2C31" stroke-width="3.2" stroke-linecap="round"/>{knurl}</g>'
        "</g>"
    )
    return body, defs


def reset() -> None:
    lib.GLYPHS.clear()
    lib.KEYFRAMES.clear()
    lib.CSS.clear()
    lib.DEFS.clear()


# ---------------------------------------------------------------- card

def card() -> str:
    reset()
    P = 56
    b: list[str] = []
    b.append(text("sans_bk", "wilsoniu", 86, P - 4, 148, "satin", -0.045))
    lead = "Experience designer at "
    b.append(text("sans", lead, 18, P, 190, "sub", -0.01))
    lx = P + width("sans", lead, 18, -0.01)
    # the studio's wordmark at cap height, on the same baseline as the sentence
    b.append(lib.cyte_wordmark(lx + 1, 190, 18 * 0.71))
    tag = "Minimal systems, cinematic details, "
    b.append(text("sans", tag, 18, P, 220, "sub", -0.01))
    b.append(text("italic", "timeless taste.", 23, P + width("sans", tag, 18, -0.01), 220, "ink"))
    b.append(text("sans", "wilsoniu.com   ·   @WilsoniuDesign", 14, P, 256, "sub"))

    k, kdefs = knob(812, 164, 66)
    b.append(k)

    b.append(f'<path d="M{P} 300.5H{W - P}" stroke="{RULE}"/>')
    col = (W - 2 * P) / len(GROUPS)
    for c, (group, tools) in enumerate(GROUPS):
        x = P + c * col
        b.append(text("mono_md", group.upper(), 11, x, 337, "sub", 0.12))
        for r_, (name, src, cap) in enumerate(tools):
            y = 372 + r_ * 28
            b.append(f'<g fill="{INK}" color="{INK}">{mark(name, src, cap, x, y - 13, 16)}</g>')
            b.append(text("sans", name, 14, x + 25, y, "ink"))
    h = 372 + 4 * 28 + 44
    alt = "wilsoniu — experience designer at CYTE LAB"
    return document(W, h, alt, [SATIN, *kdefs], b)


def main():
    lib.init()
    path = lib.ROOT / "assets" / "card.svg"
    path.write_text(card())
    print(f"{path.relative_to(lib.ROOT)}  {path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
