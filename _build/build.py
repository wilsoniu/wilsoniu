# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "uharfbuzz"]
# ///
"""Builds the profile reel for the README.

    uv run _build/build.py

The README shows one SVG: a camera viewfinder on a 10-second continuous flight over a
wireframe valley, with the profile laid over it and every element always in motion.
Type is shaped with HarfBuzz and written out as outlines (README images can't load web
fonts); tool logos come from Simple Icons / Iconify and are cached in _build/.cache.

Loop-synced elements run keyframe animations exactly T seconds long, so they share one
clock and their timelines are written in seconds. Frame 0 is a complete composition, so
a renderer that doesn't animate still shows something whole.
"""

import math
import re
import urllib.request
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "_build" / ".cache"
OUT = ROOT / "assets"

GOOGLE_FONTS = "https://github.com/google/fonts/raw/main/ofl/"
FONT_FILES = {
    "Geist[wght].ttf": "geist/Geist%5Bwght%5D.ttf",
    "GeistMono[wght].ttf": "geistmono/GeistMono%5Bwght%5D.ttf",
    "InstrumentSerif-Italic.ttf": "instrumentserif/InstrumentSerif-Italic.ttf",
}
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@16.33.0/icons/{}.svg"
ICONIFY = "https://api.iconify.design/{}.svg"

# (name, logo source or None for a keycap monogram, keycap letters)
STACK = [
    ("DESIGN", [("Figma", "si:figma", ""), ("Framer", "si:framer", ""), ("Photoshop", None, "Ps"),
                ("Illustrator", None, "Ai"), ("Canva", None, "Cv")]),
    ("MOTION", [("After Effects", None, "Ae"), ("Premiere Pro", None, "Pr"), ("DaVinci Resolve", "si:davinciresolve", ""),
                ("Final Cut Pro", None, "Fc"), ("Motion", None, "Mo")]),
    ("3D", [("Blender", "si:blender", ""), ("Unreal Engine", "si:unrealengine", ""), ("Spline", None, "Sp")]),
    ("AI", [("Claude Code", "si:claude", ""), ("OpenAI", "iconify:ri/openai-fill", ""), ("Grok", "iconify:thesvg/grok-xai", ""),
            ("Manus", "iconify:thesvg-color/manus-dark", ""), ("Cursor", "si:cursor", "")]),
    ("BUILD", [("VS Code", "iconify:devicon-plain/vscode", ""), ("Xcode", "si:xcode", ""), ("GitHub", "si:github", ""),
               ("Git", "si:git", ""), ("Linear", "si:linear", ""), ("Notion", "si:notion", ""), ("Webflow", "si:webflow", ""),
               ("Firebase", "si:firebase", ""), ("Replit", "si:replit", "")]),
]
EXPLORING = [("Claude Code", "si:claude"), ("Manus", "iconify:thesvg-color/manus-dark"),
             ("Grok", "iconify:thesvg/grok-xai"), ("Framer", "si:framer")]

# Traced (potrace) from the CYTE LAB avatar at github.com/CYTE-LAB.
CYTE_MARK = (189, 204, "M41.2 169.1L41.2 134.1L20.7 134.1L0.2 134.1L0.2 124.6L0.2 115.1L22 115.1C51.4 115.1 56.9 116.9 62.6 128.3L65.2 133.5L65.2 168.8L65.2 204.1L53.2 204.1L41.2 204.1L41.2 169.1ZM89.2 177.1L89.2 150.1L133.7 150.1L178.2 150.1L178.2 151.9C178.2 155.5 173.6 162.6 169.4 165.6L165 168.6L139.1 168.9L113.2 169.2L113.2 177.2L113.2 185.1L150.7 185.1C171.3 185.1 188.2 185.3 188.2 185.4C188.2 185.6 186 189.8 183.4 194.7L178.5 203.6L133.9 203.9L89.2 204.1L89.2 177.1ZM89.2 124.6L89.2 115.1L139.3 115.1L189.4 115.1L188.7 117.9C186.7 125.8 182 131.2 175.4 133.1C173.1 133.7 155.7 134.1 130.4 134.1L89.2 134.1L89.2 124.6ZM22.3 86.9C14.5 84.7 7.6 78.3 3.5 69.6L0.7 63.6L0.4 46.9C0 32.1 0.2 29.3 2.1 23.2C4.6 14.9 10.9 7.4 18.6 3.3L23.7 0.6L65.4 0.3L107.1 0L109.7 4.1C111.2 6.4 114.9 11.8 118 16.1C121.1 20.3 126.6 28 130.1 33L136.4 42.1L141.6 34.6C144.4 30.5 151 21 156.2 13.6L165.7 0.1L177 0.1C183.1 0.1 188.2 0.3 188.2 0.6C188.2 1.3 182 10.5 174.8 20.6C171.2 25.5 165.3 34 161.5 39.4C157.8 44.7 153.2 51.1 151.4 53.6L148.2 58L148.2 73L148.2 88.1L136.7 88.1L125.2 88.1L125.2 73.5L125.2 58.9L117.2 47.8C112.9 41.6 106.5 32.7 103 27.9L96.8 19.1L65.4 19.1C30.9 19.1 30.4 19.2 26 25.3L23.7 28.6L23.7 44.1C23.7 62.2 24.6 65 31.5 68.2L35.7 70.1L70.9 70.1L106 70.1L101 79.1L96 88.1L60.8 88C41.1 88 24.2 87.5 22.3 86.9Z")

# Per-mark optical scale so dense and airy logos read at the same weight.
OPTICAL = {"Figma": 1.08, "OpenAI": 1.08, "Firebase": 1.08, "Manus": 1.08, "Grok": 1.06, "Unreal Engine": 1.06,
           "Linear": 0.88, "VS Code": 0.9, "Xcode": 0.92}

INK, SUB, DIM, RULE, BG, ACC = "#EDEEF0", "#80838B", "#5A5E67", "#1E2026", "#07080A", "#FF5A1F"
W, H, X0, X1 = 960, 600, 64, 896
T = 10.0  # loop length, seconds
EXPO = "cubic-bezier(.16,1,.3,1)"
EASE_IN = "cubic-bezier(.6,0,.9,.4)"


def num(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def fetch(url: str, dest: Path) -> bytes:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "wilsoniu-readme-build"})
        dest.write_bytes(urllib.request.urlopen(req).read())
    return dest.read_bytes()


# ---------------------------------------------------------------- type

class Face:
    def __init__(self, file: str, wght: int | None = None):
        blob = fetch(GOOGLE_FONTS + FONT_FILES[file], CACHE / file)
        self.tt = TTFont(BytesIO(blob))
        self.upem = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.hb = hb.Font(hb.Face(blob))
        if wght:
            self.hb.set_variations({"wght": wght})
            self.glyphs = self.tt.getGlyphSet(location={"wght": wght})
        else:
            self.glyphs = self.tt.getGlyphSet()
        self.name = f"{file}@{wght}"

    def layout(self, s: str, size: float, tracking: float = 0):
        """Glyph names with pen positions in font units, plus the set width in px."""
        missing = [c for c in s if ord(c) not in self.cmap and not c.isspace()]
        if missing:
            raise ValueError(f"{self.name} has no glyph for {missing!r}")
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        track = tracking * self.upem
        x, glyphs = 0.0, []
        for info, p in zip(buf.glyph_infos, buf.glyph_positions):
            glyphs.append((self.tt.getGlyphName(info.codepoint), x + p.x_offset, p.y_offset))
            x += p.x_advance + track
        return glyphs, (x - track) * size / self.upem

    def glyph(self, name: str) -> str:
        pen = SVGPathPen(self.glyphs, ntos=num)
        self.glyphs[name].draw(pen)
        return pen.getCommands()


F: dict[str, Face] = {}
# Glyphs drawn once in <defs> and placed with <use>.
GLYPHS: dict[tuple[str, str], tuple[str, str]] = {}


def text(face: str, s: str, size: float, x: float, y: float, cls: str = "ink", tracking: float = 0, anchor: str = "start") -> str:
    f = F[face]
    glyphs, w = f.layout(s, size, tracking)
    x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
    uses = []
    for name, gx, gy in glyphs:
        key = (f.name, name)
        if key not in GLYPHS:
            GLYPHS[key] = (f"g{len(GLYPHS)}", f.glyph(name))
        gid, d = GLYPHS[key]
        if d:
            uses.append(f'<use href="#{gid}" x="{num(gx)}"' + (f' y="{num(gy)}"' if gy else "") + "/>")
    scale = size / f.upem
    return f'<g class="{cls}" transform="translate({num(x)} {num(y)}) scale({scale:.5f} {-scale:.5f})">{"".join(uses)}</g>'


def width(face: str, s: str, size: float, tracking: float = 0) -> float:
    return F[face].layout(s, size, tracking)[1]


def label(s: str, x: float, y: float, cls: str = "sub", anchor: str = "start", size: float = 9.5) -> str:
    return text("mono", s, size, x, y, cls, 0.16, anchor)


# ---------------------------------------------------------------- timeline

KEYFRAMES: dict[str, str] = {}
SHOWN = "opacity:1;visibility:visible;transform:none"


def timeline(stops: list[tuple], duration: float = T) -> str:
    """Keyframes from (seconds, css[, easing to the next stop]); returns a style declaration."""
    body, seen = "", set()
    for t, css, *ease in stops:
        pct = num(t / duration * 100)
        if pct in seen:
            continue
        seen.add(pct)
        body += f"{pct}%{{{css}" + (f";animation-timing-function:{ease[0]}" if ease else "") + "}"
    name = KEYFRAMES.setdefault(body, f"k{len(KEYFRAMES)}")
    return f"animation:{name} {num(duration)}s linear infinite"


def hidden(dy: float = 0) -> str:
    return "opacity:0;visibility:hidden" + (f";transform:translateY({num(dy)}px)" if dy else ";transform:none")


# ---------------------------------------------------------------- marks

def icon(source: str) -> tuple[float, list[tuple[str, str]]]:
    kind, ref = source.split(":", 1)
    url = SIMPLE_ICONS.format(ref) if kind == "si" else ICONIFY.format(ref)
    svg = fetch(url, CACHE / "icons" / (ref.replace("/", "--") + ".svg")).decode()
    vb = float(re.search(r'viewBox="[\d.\s-]+?([\d.]+)"', svg).group(1))
    paths = []
    for attrs in re.findall(r"<path\b([^>]*?)/?>", svg):
        d = re.search(r'\bd="([^"]+)"', attrs).group(1)
        fill_rule = re.search(r'fill-rule="([^"]+)"', attrs)
        paths.append((d, fill_rule.group(1) if fill_rule else "nonzero"))
    return vb, paths


def mark(name: str, source: str | None, cap: str, x: float, y: float, size: float) -> str:
    """A tool logo, or an outlined keycap monogram where there is no usable vector mark."""
    if source is None:
        k = size / 17
        return (f'<g transform="translate({num(x)} {num(y)}) scale({k:.4f})"><rect x="1" y="1" width="15" height="15" rx="3.5" '
                f'style="fill:none;stroke:currentColor;stroke-width:1"/>{text("mono_md", cap, 7.6, 8.5, 11.2, "", 0, "middle")}</g>')
    vb, paths = icon(source)
    o = OPTICAL.get(name, 1)
    off = size * (1 - o) / 2
    inner = "".join(f'<path fill-rule="{fr}" d="{d}"/>' for d, fr in paths)
    return f'<g transform="translate({num(x + off)} {num(y + off)}) scale({size * o / vb:.4f})">{inner}</g>'


def cyte(x: float, y: float, height: float, fill: str = INK) -> str:
    _, mh, d = CYTE_MARK
    return f'<path fill="{fill}" transform="translate({num(x)} {num(y)}) scale({height / mh:.4f})" d="{d}"/>'


# ---------------------------------------------------------------- flight

# Camera flies forward over a wireframe valley. The height field repeats every L in depth
# and the camera travels exactly L per loop, so frame T is frame 0.
CX, HOR, FX, FY, CAM = W / 2, 282, 420, 190, 0.66
ZNEAR, ZFAR, ROWS = 0.2, 2.95, 30
L = ZFAR - ZNEAR


def height(x: float, z: float) -> float:
    w = 2 * math.pi / L
    return (0.85 * (1 - math.exp(-x * x / 1.3))
            + 0.11 * math.sin(2 * w * z + 2.3 * x)
            + 0.07 * math.sin(3 * w * z - 4.1 * x + 1.0)
            + 0.05 * math.sin(w * z + 6.3 * x + 0.4)
            + 0.04 * math.cos(5 * w * z + 1.7 * x))


def fly_keyframes() -> str:
    """One shared keyframe set for every ridge line.

    A line of constant world depth, seen from a camera at relative depth zr, is a fixed
    profile scaled by 1/zr about the vanishing point. zr falls linearly with time, so the
    stops are placed at geometric depths (dense where 1/zr changes fastest).
    """
    stops = []
    for i in range(25):
        zr = ZFAR * (ZNEAR / ZFAR) ** (i / 24)
        p = (ZFAR - zr) / L * 100
        fog = min(1, (ZFAR - zr) / 0.9) * min(1, (zr - ZNEAR) / 0.08 + 0.001)
        op = fog * (0.22 + 0.68 * (1 - (zr - ZNEAR) / L) ** 1.6)
        stops.append(f"{num(p)}%{{transform:scale({1 / zr:.4f});opacity:{op:.3f}}}")
    return "@keyframes fly{" + "".join(stops) + "}"


def ridges() -> str:
    xs = [-3.5 + i * 0.1 for i in range(71)]
    out = []
    for k in range(ROWS):
        z = ZFAR - k * L / ROWS
        d = "M" + "L".join(f"{num(FX * x)} {num(FY * (CAM - height(x, z)))}" for x in xs)
        out.append(f'<path class="ridge" style="animation-delay:{num(-k * T / ROWS)}s" d="{d}"/>')
    return f'<g transform="translate({CX} {HOR})">{"".join(out)}</g>'


def meridians() -> str:
    """Lines of constant X: vertices sit at fixed depths ahead of the camera (so their x is
    fixed) and only their heights change as the ground scrolls under them."""
    # stop inside the horizon haze, where far samples would kink
    depths = [ZNEAR * (2.2 / ZNEAR) ** (j / 15) for j in range(16)]
    samples = 24
    out = []
    for c in range(31):
        x = -2.25 + c * 0.15
        frames = []
        for s in range(samples + 1):
            travel = L * s / samples
            frames.append(" ".join(f"{CX + FX * x / zr:.0f},{HOR + FY * (CAM - height(x, travel + zr)) / zr:.0f}" for zr in depths))
        out.append(f'<polyline class="mer" points="{frames[0]}"><animate attributeName="points" dur="{num(T)}s" '
                   f'repeatCount="indefinite" values="{";".join(frames)}"/></polyline>')
    return "".join(out)


# ---------------------------------------------------------------- overlays

def cycle(items: list[str], x: float, y: float, w: float, offset: float, dy: float = 20, tr: float = 0.6) -> str:
    """Slot-machine cycle through items, each on screen for T/len(items); item 0 is up at frame 0."""
    n, step = len(items), T / len(items)
    below, above = hidden(dy), hidden(-dy)
    out = []
    for i, body in enumerate(items):
        a = (offset + i * step) % T          # enter starts
        z = (a + step) % T                   # exit starts (= next item's enter)
        ev = sorted([(a, below, EXPO), ((a + tr) % T, SHOWN, None), (z, SHOWN, EXPO), ((z + tr) % T, above, None)])
        # state at t=0: walk the cycle backwards from 0 to the latest event
        state0 = ev[-1][1] if ev[-1][1] != above else below
        stops = [(0, state0)] + [(t, s, e) if e else (t, s) for t, s, e in ev] + [(T, state0)]
        out.append(f'<g style="{timeline(stops, T)}">{body}</g>')
    clip = f"slot-{num(x)}-{num(y)}"
    return (f'<clipPath id="{clip}"><rect x="{num(x - 2)}" y="{num(y - dy + 2)}" width="{num(w)}" height="{num(dy + 4)}"/></clipPath>'
            f'<g clip-path="url(#{clip})">{"".join(out)}</g>')


def readouts() -> str:
    lx, vx, ys = 600, 700, (110, 140, 170)
    b = [label(k, lx, y, "dim", size=8.5) for k, y in zip(("PRACTICE", "EXPLORING", "STUDIO"), ys)]
    practice = [text("sans_md", s, 15, vx, ys[0], "ink", -0.01) for s in ("UI/UX", "Motion", "Real-time 3D", "Visual identity")]
    exploring = [f'<g fill="{INK}">{mark(name, src, "", vx, ys[1] - 12, 14)}</g>' + text("sans_md", name, 15, vx + 22, ys[1], "ink", -0.01)
                 for name, src in EXPLORING]
    b.append(cycle(practice, vx, ys[0], 200, offset=-0.65))
    b.append(cycle(exploring, vx, ys[1], 200, offset=T / 8 - 0.65))
    b.append(cyte(vx, ys[2] - 12, 13) + text("sans_md", "CYTE LAB", 15, vx + 22, ys[2], "ink", 0.03))
    b.append(label("VIRTUAL PRODUCTION · DIGITAL CREATION · INDIE GAMES", lx, 196, "sub", size=7.4))
    b.append(f'<path class="hl" d="M{lx} 84.5H{X1}M{lx} 210.5H{X1}"/>')
    return "".join(b)


def identity() -> str:
    lead = "Minimal systems, cinematic details, "
    return (label("EXPERIENCE DESIGNER", X0 + 2, 104)
            + f'<g class="name">{text("sans_sb", "wilsoniu", 92, X0 - 4, 184, "", -0.045)}</g>'
            + text("sans", lead, 17, X0, 220, "sub", -0.01)
            + text("italic", "timeless taste.", 22, X0 + width("sans", lead, 17, -0.01), 220, "ink"))


def marquee(x0: float, x1: float, y: float) -> str:
    """Every tool, scrolling; group names ride along as section markers."""
    items, x = [], 0.0
    for group, tools in STACK:
        items.append(label(group, x, y, "acc", size=8))
        x += width("mono", group, 8, 0.16) + 14
        for name, src, cap in tools:
            items.append(f'<g fill="{SUB}" color="{SUB}">{mark(name, src, cap, x, y - 11, 13)}</g>' + text("sans", name, 12.5, x + 19, y, "sub"))
            x += 19 + width("sans", name, 12.5) + 22
        x += 10
    period = x
    strip = "".join(items)
    return (f'<clipPath id="marquee"><rect x="{x0}" y="{y - 16}" width="{x1 - x0}" height="24"/></clipPath>'
            f'<g clip-path="url(#marquee)"><g transform="translate({x0} 0)"><g style="animation:marquee {num(period / 45)}s linear infinite">'
            f'{strip}<g transform="translate({num(period)} 0)">{strip}</g></g></g>'
            f'<rect x="{x0}" y="{y - 16}" width="40" height="24" fill="url(#fade-l)"/><rect x="{x1 - 40}" y="{y - 16}" width="40" height="24" fill="url(#fade-r)"/></g>'
            f'<style>@keyframes marquee{{to{{transform:translateX(-{num(period)}px)}}}}</style>')


def hud() -> str:
    b = []
    m, Lb = 36, 16
    corners = "".join(f"M{x} {y + Lb * sy}V{y}H{x + Lb * sx}" for x, y, sx, sy in
                      ((m, 56, 1, 1), (W - m, 56, -1, 1), (m, 530, 1, -1), (W - m, 530, -1, -1)))
    b.append(f'<path class="bracket" d="{corners}"/>')
    b.append(f'<circle class="rec" cx="{X0 - 6}" cy="30" r="3.6" fill="{ACC}"/>')
    b.append(text("mono_md", "REC", 9.5, X0 + 4, 33.5, "ink", 0.16))
    b.append(label("WILSONIU — REEL 2026", X0 + 4 + width("mono_md", "REC ", 9.5, 0.16) + 10, 33.5))
    # heading tape, swaying with the camera
    ticks = "".join(f"M{num(i * 8)} {36 if i % 5 else 33}V40" for i in range(-40, 41))
    nums = "".join(label(f"{(i * 5) % 360:03d}", i * 40, 30, "dim", "middle", 7) for i in range(-8, 9))
    b.append(f'<clipPath id="tape"><rect x="{CX - 90}" y="20" width="180" height="24"/></clipPath>'
             f'<g clip-path="url(#tape)"><g transform="translate({CX} 0)"><g class="tape"><path class="tick" d="{ticks}"/>{nums}</g></g></g>'
             f'<path d="M{CX} 42l-3 4h6z" fill="{ACC}"/>')
    # timecode: digit strips stepped by CSS (seconds 00–09 over the loop, frames 00–23 each second)
    size, step = 9.5, 14
    wd = width("mono_md", "00", size, 0.16)
    colon = width("mono_md", ":", size, 0.16) + size * 0.16
    x_ff = X1 - wd
    x_ss = x_ff - colon - wd
    b.append(text("mono_md", "TC 00:00:", size, x_ss - size * 0.16, 33.5, "sub", 0.16, "end"))
    b.append(text("mono_md", ":", size, x_ff - colon, 33.5, "sub", 0.16))
    for key, x, count, dur in (("ss", x_ss, int(T), T), ("ff", x_ff, 24, 1)):
        strip = "".join(text("mono_md", f"{i:02d}", size, x, 33.5 + i * step, "ink", 0.16) for i in range(count))
        b.append(f'<clipPath id="tc-{key}"><rect x="{num(x - 1)}" y="24" width="{num(wd + 2)}" height="12"/></clipPath>'
                 f'<g clip-path="url(#tc-{key})"><g style="animation:{key} {num(dur)}s steps({count}) infinite">{strip}</g></g>'
                 f'<style>@keyframes {key}{{to{{transform:translateY(-{count * step}px)}}}}</style>')
    # focus reticle on the vanishing point
    b.append(f'<g transform="translate({CX} {HOR})"><g class="reticle">'
             f'<path class="bracket" d="M-22 -10V-14H-18M22 -10V-14H18M-22 10V14H-18M22 10V14H18"/></g>'
             f'<path d="M-5 0H5M0 -5V5" stroke="{ACC}" stroke-width="1"/></g>')
    # bottom: loop progress, scrolling stack, links
    b.append(f'<path class="hl" d="M{X0} 548.5H{X1}"/>')
    b.append(f'<path d="M{X0} 548.5H{X1}" stroke="{INK}" stroke-opacity=".75" style="animation:progress {num(T)}s linear infinite;transform-origin:{X0}px 548px"/>')
    b.append(marquee(X0, 640, 578))
    b.append(label("WILSONIU.COM  ·  @WILSONIUDESIGN", X1, 578, "sub", "end", size=8.5))
    return "".join(b)


def reel() -> str:
    world = (f'<clipPath id="land"><rect x="0" y="150" width="{W}" height="{H - 150}"/></clipPath>'
             f'<g clip-path="url(#land)"><g class="camera">{meridians()}{ridges()}</g></g>')
    sky = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
           f'<ellipse cx="{CX}" cy="{HOR + 6}" rx="420" ry="34" fill="url(#sun)" class="sun"/>')
    veils = (f'<rect y="{HOR - 60}" width="{W}" height="120" fill="url(#haze)"/>'
             f'<rect y="500" width="{W}" height="100" fill="url(#floor)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
    overlays = identity() + readouts()
    frame = hud()

    css = f"""
.ink{{fill:{INK}}}.sub{{fill:{SUB}}}.dim{{fill:{DIM}}}.acc{{fill:{ACC}}}.name{{fill:url(#name)}}
.hl{{stroke:{RULE};stroke-width:1;fill:none}}
.tick{{stroke:{DIM};stroke-width:1;fill:none}}
.bracket{{stroke:{DIM};stroke-width:1.2;fill:none}}
.ridge{{fill:none;stroke:{INK};stroke-width:1;vector-effect:non-scaling-stroke;stroke-linejoin:round;animation:fly {num(T)}s linear infinite}}
.mer{{fill:none;stroke:{INK};stroke-opacity:.3;stroke-width:.8;stroke-linejoin:round}}
.camera{{transform-origin:{CX}px {HOR}px;animation:camera {num(T)}s infinite}}
@keyframes camera{{0%,100%{{transform:none;animation-timing-function:cubic-bezier(.37,0,.63,1)}}25%{{transform:rotate(1.1deg) translateY(-4px);animation-timing-function:cubic-bezier(.37,0,.63,1)}}50%{{transform:translateY(2px);animation-timing-function:cubic-bezier(.37,0,.63,1)}}75%{{transform:rotate(-1.1deg) translateY(-4px);animation-timing-function:cubic-bezier(.37,0,.63,1)}}}}
.tape{{animation:tape {num(T)}s infinite cubic-bezier(.37,0,.63,1)}}
@keyframes tape{{0%,100%{{transform:none}}25%{{transform:translateX(-14px)}}75%{{transform:translateX(14px)}}}}
.sun{{animation:sun 5s infinite cubic-bezier(.37,0,.63,1)}}
@keyframes sun{{0%,100%{{opacity:.75}}50%{{opacity:1}}}}
.reticle{{animation:reticle 2.5s infinite cubic-bezier(.37,0,.63,1)}}
@keyframes reticle{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.18)}}}}
.rec{{animation:rec 1s steps(1) infinite}}
@keyframes rec{{50%{{opacity:.2}}}}
@keyframes progress{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
{fly_keyframes()}
""" + "".join(f"@keyframes {name}{{{body}}}\n" for body, name in KEYFRAMES.items())

    defs = [
        *(f'<path id="{gid}" d="{d}"/>' for gid, d in GLYPHS.values() if d),
        f'<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
        '<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="760" x2="0" y2="-120"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#767A83"/></linearGradient>',
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".47" stop-color="#0E1014"/><stop offset=".6" stop-color="{BG}"/></linearGradient>',
        f'<radialGradient id="sun"><stop offset="0" stop-color="{ACC}" stop-opacity=".28"/><stop offset=".5" stop-color="{ACC}" stop-opacity=".07"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>',
        f'<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset=".5" stop-color="{BG}" stop-opacity=".85"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset=".55" stop-color="{BG}" stop-opacity=".92"/><stop offset="1" stop-color="{BG}"/></linearGradient>',
        f'<radialGradient id="vignette" cx=".5" cy=".46" r=".75"><stop offset=".6" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".85"/></radialGradient>',
        f'<linearGradient id="fade-l"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="fade-r"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>',
    ]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="wilsoniu — experience designer at CYTE LAB. A 10-second loop flying over a wireframe valley.">',
        "<title>wilsoniu — reel</title>",
        f"<style>{css}</style>",
        f"<defs>{''.join(defs)}</defs>",
        '<g clip-path="url(#c)">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        sky, world, veils, overlays, frame,
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="17.5" fill="none" stroke="#fff" stroke-opacity=".08"/>',
        "</g>",
        "</svg>",
    ])


def main():
    F.update({
        "sans": Face("Geist[wght].ttf", 400),
        "sans_md": Face("Geist[wght].ttf", 500),
        "sans_sb": Face("Geist[wght].ttf", 600),
        "mono": Face("GeistMono[wght].ttf", 400),
        "mono_md": Face("GeistMono[wght].ttf", 500),
        "italic": Face("InstrumentSerif-Italic.ttf"),
    })
    OUT.mkdir(exist_ok=True)
    path = OUT / "reel.svg"
    path.write_text(reel())
    print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KB  {len(KEYFRAMES)} keyframes")


if __name__ == "__main__":
    main()
