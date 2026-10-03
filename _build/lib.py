"""Shared toolkit for the reel: type, logos, the reel clock, and the wireframe terrain.

Shots (modules in _build/shots/) import this and return SVG markup. Everything that
follows the reel clock runs a keyframe animation exactly T seconds long, so every shot
shares one timeline written in seconds.
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

# ---------------------------------------------------------------- canvas, palette, clock

W, H = 960, 600
X0, X1 = 64, 896          # left/right text margins
SAFE_TOP, SAFE_BOTTOM = 64, 528  # keep shot content between these (HUD lives outside)
INK, SUB, DIM, RULE, BG, ACC = "#EDEEF0", "#80838B", "#5A5E67", "#1E2026", "#07080A", "#FF5A1F"

T = 12.0     # loop length, seconds
BEAT = 0.5   # 120 BPM; cut on beats
# Shot windows in reel seconds. s1 starts before the wrap so frame 0 shows the finished name.
SHOTS = {"s1": (-0.7, 1.5), "s2": (1.5, 3.5), "s3": (3.5, 5.5), "s4": (5.5, 8.0), "s5": (8.0, 9.5), "s6": (9.5, 11.3)}

EXPO = "cubic-bezier(.16,1,.3,1)"        # snappy entrance
BACK = "cubic-bezier(.34,1.56,.64,1)"    # entrance with overshoot
EASE_IN = "cubic-bezier(.6,0,.9,.4)"     # quick exit
SINE = "cubic-bezier(.37,0,.63,1)"       # drifts

# ---------------------------------------------------------------- tools

# (name, logo source or None for an outlined keycap monogram, keycap letters)
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
DISCIPLINES = ["UI/UX", "Motion", "Real-time 3D", "Visual identity"]
TAGLINE = ["Minimal systems,", "cinematic details,", "timeless taste."]
STUDIO = ("CYTE LAB", "CREATIVE TECH STUDIO", ["VIRTUAL PRODUCTION", "DIGITAL CREATION", "INDIE GAMES"])
# Per-mark optical scale so dense and airy logos read at the same weight.
OPTICAL = {"Figma": 1.08, "OpenAI": 1.08, "Firebase": 1.08, "Manus": 1.08, "Grok": 1.06, "Unreal Engine": 1.06,
           "Linear": 0.88, "VS Code": 0.9, "Xcode": 0.92}

# Traced (potrace) from the CYTE LAB avatar at github.com/CYTE-LAB; 189 x 204 units.
CYTE_MARK = (189, 204, "M41.2 169.1L41.2 134.1L20.7 134.1L0.2 134.1L0.2 124.6L0.2 115.1L22 115.1C51.4 115.1 56.9 116.9 62.6 128.3L65.2 133.5L65.2 168.8L65.2 204.1L53.2 204.1L41.2 204.1L41.2 169.1ZM89.2 177.1L89.2 150.1L133.7 150.1L178.2 150.1L178.2 151.9C178.2 155.5 173.6 162.6 169.4 165.6L165 168.6L139.1 168.9L113.2 169.2L113.2 177.2L113.2 185.1L150.7 185.1C171.3 185.1 188.2 185.3 188.2 185.4C188.2 185.6 186 189.8 183.4 194.7L178.5 203.6L133.9 203.9L89.2 204.1L89.2 177.1ZM89.2 124.6L89.2 115.1L139.3 115.1L189.4 115.1L188.7 117.9C186.7 125.8 182 131.2 175.4 133.1C173.1 133.7 155.7 134.1 130.4 134.1L89.2 134.1L89.2 124.6ZM22.3 86.9C14.5 84.7 7.6 78.3 3.5 69.6L0.7 63.6L0.4 46.9C0 32.1 0.2 29.3 2.1 23.2C4.6 14.9 10.9 7.4 18.6 3.3L23.7 0.6L65.4 0.3L107.1 0L109.7 4.1C111.2 6.4 114.9 11.8 118 16.1C121.1 20.3 126.6 28 130.1 33L136.4 42.1L141.6 34.6C144.4 30.5 151 21 156.2 13.6L165.7 0.1L177 0.1C183.1 0.1 188.2 0.3 188.2 0.6C188.2 1.3 182 10.5 174.8 20.6C171.2 25.5 165.3 34 161.5 39.4C157.8 44.7 153.2 51.1 151.4 53.6L148.2 58L148.2 73L148.2 88.1L136.7 88.1L125.2 88.1L125.2 73.5L125.2 58.9L117.2 47.8C112.9 41.6 106.5 32.7 103 27.9L96.8 19.1L65.4 19.1C30.9 19.1 30.4 19.2 26 25.3L23.7 28.6L23.7 44.1C23.7 62.2 24.6 65 31.5 68.2L35.7 70.1L70.9 70.1L106 70.1L101 79.1L96 88.1L60.8 88C41.1 88 24.2 87.5 22.3 86.9Z")

# ---------------------------------------------------------------- registries

KEYFRAMES: dict[str, str] = {}   # keyframe body -> generated name
CSS: list[str] = []              # extra rules (classes, named @keyframes) added by shots
DEFS: list[str] = []             # extra <defs> children (gradients, clipPaths) added by shots


def add_css(rule: str) -> None:
    if rule not in CSS:
        CSS.append(rule)


def add_def(markup: str) -> None:
    if markup not in DEFS:
        DEFS.append(markup)


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

GOOGLE_FONTS = "https://github.com/google/fonts/raw/main/ofl/"
FONT_FILES = {
    "Geist[wght].ttf": "geist/Geist%5Bwght%5D.ttf",
    "GeistMono[wght].ttf": "geistmono/GeistMono%5Bwght%5D.ttf",
    "InstrumentSerif-Italic.ttf": "instrumentserif/InstrumentSerif-Italic.ttf",
}


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
GLYPHS: dict[tuple[str, str], tuple[str, str]] = {}   # drawn once in <defs>, placed with <use>


def init() -> None:
    """Faces: sans (400), sans_md (500), sans_sb (600), sans_bk (800), mono, mono_md, italic (Instrument Serif)."""
    if F:
        return
    F.update({
        "sans": Face("Geist[wght].ttf", 400),
        "sans_md": Face("Geist[wght].ttf", 500),
        "sans_sb": Face("Geist[wght].ttf", 600),
        "sans_bk": Face("Geist[wght].ttf", 800),
        "mono": Face("GeistMono[wght].ttf", 400),
        "mono_md": Face("GeistMono[wght].ttf", 500),
        "italic": Face("InstrumentSerif-Italic.ttf"),
    })


def text(face: str, s: str, size: float, x: float, y: float, cls: str = "ink", tracking: float = 0, anchor: str = "start") -> str:
    """Outlined text with its baseline at y. cls: ink | sub | dim | acc | name (silver gradient) | "" (inherit fill)."""
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


def letters(face: str, s: str, size: float, x: float, y: float, tracking: float = 0, anchor: str = "start") -> list[tuple[float, float, str]]:
    """Per-letter layout for kinetic type: [(x, advance, char)] with x already anchored."""
    glyphs, w = F[face].layout(s, size, tracking)
    x0 = x - {"start": 0, "middle": w / 2, "end": w}[anchor]
    k = size / F[face].upem
    out = []
    for i, ch in enumerate(s):
        gx = glyphs[i][1] * k
        nx = glyphs[i + 1][1] * k if i + 1 < len(glyphs) else w
        out.append((x0 + gx, nx - gx, ch))
    return out


def width(face: str, s: str, size: float, tracking: float = 0) -> float:
    return F[face].layout(s, size, tracking)[1]


def label(s: str, x: float, y: float, cls: str = "sub", anchor: str = "start", size: float = 9.5) -> str:
    """Letter-spaced uppercase mono caption."""
    return text("mono", s, size, x, y, cls, 0.16, anchor)


# ---------------------------------------------------------------- the reel clock

SHOWN = "opacity:1;visibility:visible;transform:none"


def timeline(stops: list[tuple], duration: float = T) -> str:
    """CSS keyframes from [(seconds, css[, easing to the next stop])]; returns a style declaration.

    Put it in a style attribute on a <g> that has no transform attribute of its own (CSS
    transform replaces it). Stops must be in ascending time within [0, duration].
    """
    frames: dict[str, str] = {}   # a later stop at the same instant wins
    for t, css, *ease in stops:
        frames[num(t / duration * 100)] = css + (f";animation-timing-function:{ease[0]}" if ease else "")
    body = "".join(f"{pct}%{{{css}}}" for pct, css in frames.items())
    name = KEYFRAMES.setdefault(body, f"k{len(KEYFRAMES)}")
    return f"animation:{name} {num(duration)}s linear infinite"


def off(css: str = "") -> str:
    """A hidden state: opacity 0, visibility hidden, plus an optional transform etc."""
    return "opacity:0;visibility:hidden;" + (css or "transform:none")


def show(body: str, t0: float, t1: float, frm: str = "", to: str = "", din: float = 0.4, dout: float = 0.25,
         ein: str = EXPO, eout: str = EASE_IN, hold: str = "", origin: str = "") -> str:
    """Wrap body so it enters at t0 (from `frm`), holds, and leaves by t1 (to `to`).

    frm/to are transforms etc. for the hidden states, e.g. frm="transform:translateY(40px)".
    hold is an optional end-of-hold state (e.g. "transform:scale(1.04)") so the element
    keeps drifting while on screen. A negative t0 enters before the loop wraps (only s1).
    origin sets transform-origin, e.g. "480px 300px".
    """
    a, b = off(frm), off(to)
    held_end = ("opacity:1;visibility:visible;" + hold) if hold else SHOWN
    if t0 >= 0:
        stops = [(0, a), (t0, a, ein), (t0 + din, SHOWN, SINE if hold else None), (t1 - dout, held_end, eout), (t1, b), (T, b)]
    else:
        s = T + t0
        # during the hold the drift runs from the start state at s+din to held_end at t1-dout; split it across the wrap
        stops = [(0, SHOWN, SINE if hold else None), (t1 - dout, held_end, eout), (t1, b), (s, a, ein), (s + din, SHOWN), (T, SHOWN)]
    stops = [st if len(st) == 3 and st[2] else st[:2] for st in stops]
    style = timeline(stops) + (f";transform-origin:{origin}" if origin else "")
    return f'<g style="{style}">{body}</g>'


def at(body: str, stops: list[tuple], origin: str = "") -> str:
    """Wrap body in a fully custom reel-clock animation (see timeline)."""
    return f'<g style="{timeline(stops)}' + (f';transform-origin:{origin}' if origin else "") + f'">{body}</g>'


# ---------------------------------------------------------------- logos

SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@16.33.0/icons/{}.svg"
ICONIFY = "https://api.iconify.design/{}.svg"


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
    """A tool logo (top-left at x, y), or an outlined keycap monogram when there's no vector mark.
    Wrap it in <g fill=... color=...>: logos use fill, keycaps use currentColor for the outline."""
    if source is None:
        k = size / 17
        return (f'<g transform="translate({num(x)} {num(y)}) scale({k:.4f})"><rect x="1" y="1" width="15" height="15" rx="3.5" '
                f'style="fill:none;stroke:currentColor;stroke-width:1"/>{text("mono_md", cap, 7.6, 8.5, 11.2, "", 0, "middle")}</g>')
    vb, paths = icon(source)
    o = OPTICAL.get(name, 1)
    off_ = size * (1 - o) / 2
    inner = "".join(f'<path fill-rule="{fr}" d="{d}"/>' for d, fr in paths)
    return f'<g transform="translate({num(x + off_)} {num(y + off_)}) scale({size * o / vb:.4f})">{inner}</g>'


def cyte(x: float, y: float, height: float, fill: str = INK) -> str:
    """The CYTE LAB mark, top-left at x, y."""
    _, mh, d = CYTE_MARK
    return f'<path fill="{fill}" transform="translate({num(x)} {num(y)}) scale({height / mh:.4f})" d="{d}"/>'


# ---------------------------------------------------------------- wireframe terrain

def terrain(prefix: str, period: float = 4.0, hor: float = 282, cx: float = W / 2, fx: float = 420, fy: float = 190,
            cam: float = 0.66, rows: int = 30, cols: int = 31, ridge_opacity: float = 1.0, col_opacity: float = 0.3) -> str:
    """A camera flying forward over a wireframe valley, looping every `period` seconds (its own
    clock, independent of T). Returns markup covering the full frame; clip/position it yourself.

    Ridge lines (constant depth) are fixed profiles scaled by 1/zr about the vanishing point
    (cx, hor); cross lines (constant x) have vertices at fixed depths whose heights are
    animated with SMIL. The height field repeats every L in depth and the camera covers L per
    period, so the flight is seamless. `prefix` must be unique per instance.
    """
    znear, zfar = 0.2, 2.95
    span = zfar - znear

    def height(x: float, z: float) -> float:
        w = 2 * math.pi / span
        return (0.85 * (1 - math.exp(-x * x / 1.3)) + 0.11 * math.sin(2 * w * z + 2.3 * x)
                + 0.07 * math.sin(3 * w * z - 4.1 * x + 1.0) + 0.05 * math.sin(w * z + 6.3 * x + 0.4)
                + 0.04 * math.cos(5 * w * z + 1.7 * x))

    stops = []
    for i in range(25):
        zr = zfar * (znear / zfar) ** (i / 24)
        fog = min(1, (zfar - zr) / 0.9) * min(1, (zr - znear) / 0.08 + 0.001)
        op = fog * (0.22 + 0.68 * (1 - (zr - znear) / span) ** 1.6) * ridge_opacity
        stops.append(f"{num((zfar - zr) / span * 100)}%{{transform:scale({1 / zr:.4f});opacity:{op:.3f}}}")
    add_css(f"@keyframes {prefix}-fly{{{''.join(stops)}}}")
    add_css(f".{prefix}-ridge{{fill:none;stroke:{INK};stroke-width:1;vector-effect:non-scaling-stroke;stroke-linejoin:round;"
            f"animation:{prefix}-fly {num(period)}s linear infinite}}")
    add_css(f".{prefix}-col{{fill:none;stroke:{INK};stroke-opacity:{col_opacity};stroke-width:.8;stroke-linejoin:round}}")

    xs = [-3.5 + i * 0.1 for i in range(71)]
    ridges = []
    for k in range(rows):
        z = zfar - k * span / rows
        d = "M" + "L".join(f"{num(fx * x)} {num(fy * (cam - height(x, z)))}" for x in xs)
        ridges.append(f'<path class="{prefix}-ridge" style="animation-delay:{num(-k * period / rows)}s" d="{d}"/>')

    depths = [znear * (2.2 / znear) ** (j / 15) for j in range(16)]
    samples, cross = 24, []
    for c in range(cols):
        x = -2.25 + c * 4.5 / max(cols - 1, 1)
        frames = []
        for s in range(samples + 1):
            travel = span * s / samples
            frames.append(" ".join(f"{cx + fx * x / zr:.0f},{hor + fy * (cam - height(x, travel + zr)) / zr:.0f}" for zr in depths))
        cross.append(f'<polyline class="{prefix}-col" points="{frames[0]}"><animate attributeName="points" dur="{num(period)}s" '
                     f'repeatCount="indefinite" values="{";".join(frames)}"/></polyline>')
    return "".join(cross) + f'<g transform="translate({num(cx)} {num(hor)})">{"".join(ridges)}</g>'
