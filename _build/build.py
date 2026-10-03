# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "uharfbuzz"]
# ///
"""Builds the profile reel for the README.

    uv run _build/build.py

The README shows one SVG: a camera viewfinder playing a 24-second loop of five scenes.
Type is shaped with HarfBuzz and written out as outlines (README images can't load web
fonts); tool logos come from Simple Icons / Iconify and are cached in _build/.cache.

Every scene element runs a keyframe animation exactly D seconds long, so they all share
one clock and the timeline is written in seconds. Frame 0 is the finished title scene,
so a renderer that doesn't animate still shows something whole.
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
D = 24.0  # loop length, seconds
SPIN = 18  # globe: seconds per revolution
EXPO = "cubic-bezier(.16,1,.3,1)"
EASE_IN = "cubic-bezier(.6,0,.9,.4)"
SCENES = [("IDENT", -1.2, 5.3), ("PRACTICE", 5.0, 10.3), ("INSTRUMENTS", 10.0, 15.3), ("NOW", 15.0, 19.8), ("STUDIO", 19.5, 23.0)]


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


def timeline(stops: list[tuple], duration: float = D) -> str:
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


def life(t0: float, t1: float, dy: float = 14, din: float = 0.8, dout: float = 0.45) -> str:
    """On screen from t0 to t1; a negative t0 enters before the loop wraps, so frame 0 shows it."""
    before, after = hidden(dy), hidden(-dy * 0.5)
    if t0 >= 0:
        return timeline([(0, before), (t0, before, EXPO), (t0 + din, SHOWN), (t1 - dout, SHOWN, EASE_IN), (t1, after), (D, after)])
    a = D + t0
    return timeline([(0, SHOWN), (t1 - dout, SHOWN, EASE_IN), (t1, after), (a, before, EXPO), (a + din, SHOWN), (D, SHOWN)])


def on(body: str, t0: float, t1: float, **kw) -> str:
    return f'<g style="{life(t0, t1, **kw)}">{body}</g>'


def draw(t0: float, dur: float = 1.0) -> str:
    """Stroke draw-in (needs pathLength="1"); stays drawn until the loop ends or its scene hides."""
    if t0 >= 0:
        return timeline([(0, "stroke-dashoffset:1"), (t0, "stroke-dashoffset:1", EXPO), (t0 + dur, "stroke-dashoffset:0"), (D, "stroke-dashoffset:0")])
    a = D + t0
    return timeline([(0, "stroke-dashoffset:0"), (a, "stroke-dashoffset:1", EXPO), (a + dur, "stroke-dashoffset:0"), (D, "stroke-dashoffset:0")])


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


# ---------------------------------------------------------------- globe

ELEVATION = math.radians(16)
SKEW = math.degrees(math.atan(math.sin(ELEVATION)))


def globe(cx: float, cy: float, r: float, tilt: float = -14) -> str:
    """An orthographic globe seen from slightly above, turning eastward.

    A meridian at longitude θ is the half-ellipse (rx=r, ry=r·cos e) transformed by
    scaleX(sin θ)·skewY(atan(cos θ·sin e)). Both factors are sinusoids in time, which CSS
    keyframes reproduce with sine easing, so each meridian is just nested transforms.
    Inline styles hold the resting pose for renderers that don't animate.
    """
    ce, se = math.cos(ELEVATION), math.sin(ELEVATION)
    out = [f'<g transform="translate({cx} {cy}) rotate({tilt})">']
    out.append(f'<circle r="{num(r * 1.32)}" fill="url(#atmo)"/>')
    out.append(f'<circle r="{r}" fill="url(#sphere)"/>')
    for lat in (-60, -30, 0, 30, 60):
        l = math.radians(lat)
        y, rx, ry = -r * math.sin(l) * ce, r * math.cos(l), r * math.cos(l) * se
        a = f"A{num(rx)} {num(ry)} 0 0 1"
        out.append(f'<path class="lat back" d="M{num(-rx)} {num(y)}{a} {num(rx)} {num(y)}"/>')
        out.append(f'<path class="lat{" eq" if lat == 0 else ""}" d="M{num(rx)} {num(y)}{a} {num(-rx)} {num(y)}"/>')
    pole = r * ce
    out.append(f'<path class="axis" d="M0 {num(-pole - 16)}V{num(pole + 16)}"/>')
    # Meridians stop at ±78° so the twelve of them don't pile into bright knots at the poles.
    cap = math.radians(78)
    mx, my = r * math.cos(cap), pole * math.sin(cap)
    half = f"M{num(mx)} {num(-my)}A{r} {num(pole)} 0 0 1 {num(mx)} {num(my)}"
    for i in range(12):
        th = math.radians(i * 30)
        delay = f"animation-delay:{num(-SPIN * i / 12)}s"
        sx = math.sin(th) if abs(math.sin(th)) > 1e-3 else 0.001
        skew = math.degrees(math.atan(math.cos(th) * se))
        op = 0.12 + 0.78 * ((1 + math.cos(th)) / 2) ** 1.6
        out.append(
            f'<g class="sx" style="{delay};transform:scaleX({sx:.3f})">'
            f'<g class="sk" style="{delay};transform:skewY({num(skew)}deg)">'
            f'<path class="mer" style="{delay};opacity:{num(op)}" d="{half}"/></g></g>'
        )
    out.append(f'<circle class="limb" r="{r}"/>')
    out.append("</g>")
    return "".join(out)


def orbit(cx: float, cy: float, rx: float, ry: float, rot: float, dur: float, color: str, halo: str, layer: str, r: float) -> str:
    """A tilted orbit. The "under" layer is drawn whole beneath the sphere, which hides the
    part passing behind it; the "over" layer repeats it clipped to the sphere's front
    half-disk, so clip edges only ever fall inside the sphere.
    """
    d = f"M{rx} 0A{rx} {ry} 0 1 0 {-rx} 0A{rx} {ry} 0 1 0 {rx} 0"
    parts = [f'<path class="orbit" d="{d}"/>']
    for length, op, w in ((260, 0.12, 1.1), (130, 0.35, 1.3), (45, 0.9, 1.6)):
        parts.append(
            f'<path d="{d}" pathLength="1000" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-dasharray="{length} {1000 - length}">'
            f'<animate attributeName="stroke-dashoffset" values="{length};{length - 1000}" dur="{dur}s" repeatCount="indefinite"/></path>'
        )
    motion = f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{d}"/>'
    parts.append(f'<circle r="10" fill="url(#{halo})">{motion}</circle>')
    parts.append(f'<circle r="2.3" fill="#fff">{motion}</circle>')
    head = f'<g transform="translate({cx} {cy}) rotate({rot})">'
    if layer == "under":
        return head + "".join(parts) + "</g>"
    clip = f"orbit-{num(rx)}-over"
    return (head + f'<clipPath id="{clip}"><path d="M{-r} 0A{r} {r} 0 0 0 {r} 0Z"/></clipPath>'
            f'<g clip-path="url(#{clip})">{"".join(parts)}</g></g>')


# ---------------------------------------------------------------- scenes

def scene_ident(t0: float, t1: float) -> str:
    b = []
    b.append(on(label("EXPERIENCE DESIGNER", X0 + 2, 206), -1.15, t1 - 0.6))
    b.append(on(f'<g class="name">{text("sans_sb", "wilsoniu", 104, X0 - 4, 296, "", -0.045)}</g>', -1.05, t1 - 0.5, dy=26))
    b.append(on(text("sans", "Minimal systems, cinematic details,", 21, X0, 350, "sub", -0.01)
                + text("italic", "timeless taste.", 28, X0, 384), -0.95, t1 - 0.45))
    b.append(on(cyte(X0, 425, 24) + text("sans_md", "CYTE LAB", 15, X0 + 34, 438, "ink", 0.04)
                + label("CREATIVE TECH STUDIO", X0 + 34, 455, size=8.5), -0.85, t1 - 0.4))

    gx, gy, gr = 690, 292, 116
    orbits = [(196, 42, -12, 7.5, ACC, "halo-acc"), (162, 54, 24, 11.5, INK, "halo-ink")]
    world = ("".join(orbit(gx, gy, *o, "under", gr) for o in orbits) + globe(gx, gy, gr)
             + "".join(orbit(gx, gy, *o, "over", gr) for o in orbits))
    gone = "opacity:0;visibility:hidden;transform:scale(2.4)"
    small = "opacity:0;visibility:hidden;transform:scale(.8) rotate(-10deg)"
    push = timeline([(0, SHOWN), (t1 - 1.0, SHOWN, EASE_IN), (t1, gone), (D - 1.3, small, EXPO), (D - 0.05, SHOWN), (D, SHOWN)])
    grid = (f'<rect x="{gx - 230}" y="{gy - 230}" width="460" height="460" fill="url(#grid)" opacity=".14"/>'
            f'<rect x="{gx - 230}" y="{gy - 230}" width="460" height="460" fill="url(#vignette)"/>')
    b.insert(0, f'<g style="{push};transform-origin:{gx}px {gy}px">{grid}{world}</g>')
    return "".join(b)


def tile_ui(t: float) -> str:
    b = ['<rect x="22" y="30" width="152" height="124" rx="8" class="line"/>',
         '<path class="line" d="M22 48H174"/>',
         "".join(f'<circle cx="{32 + i * 8}" cy="39" r="2" class="dimfill"/>' for i in range(3)),
         '<rect x="34" y="60" width="60" height="40" rx="4" class="block"/>',
         '<rect x="102" y="60" width="60" height="40" rx="4" class="block"/>',
         '<path class="line" d="M34 113H162M34 124H128"/>',
         '<rect x="34" y="134" width="50" height="12" rx="6" class="btn"/>']
    # cursor travels to the button, clicks, wanders off
    cursor = '<path d="M0 0L0 15L4 11L7 18L9.5 17L6.5 10L12 10Z" fill="#fff" stroke="#000" stroke-width=".8"/>'
    b.append('<circle cx="59" cy="140" r="5" class="ripple" style="transform-origin:59px 140px"/>')
    b.append(f'<g class="cursor">{cursor}</g>')
    return "".join(b)


def tile_motion(t: float) -> str:
    curve = "M28 168C51.7 28 72.4 28 176 28"
    return (
        '<path class="axisln" d="M28 28V168H176"/>'
        + "".join(f'<path class="axisln" d="M{28 + i * 37} 168v4"/>' for i in range(5))
        + '<path class="dash" d="M28 28H176M176 28V168"/>'
        + f'<path class="curve" pathLength="1" style="{draw(t + 0.3, 1.2)}" d="{curve}"/>'
        + f'<path class="handle" d="M28 168L51.7 28M176 28L72.4 28"/><circle cx="51.7" cy="28" r="2.5" class="knot"/><circle cx="72.4" cy="28" r="2.5" class="knot"/>'
        + '<g class="ex"><g class="ey"><circle cx="28" cy="168" r="4" fill="' + ACC + '"/></g></g>'
        + '<path class="axisln" d="M186 28V168"/><g class="ey"><rect x="182" y="164" width="8" height="8" rx="1.5" fill="#fff"/></g>'
        + text("mono", "cubic-bezier(.16, 1, .3, 1)", 7, 28, 186, "dim", 0.04)
    )


def tile_space(t: float) -> str:
    vx, vy = 98, 100
    verts = "".join(f"M{vx} {vy}L{num(vx + k * 34)} 196" for k in range(-8, 9))
    lines = "".join(
        f'<g transform="translate({vx} {vy})"><path class="floor" style="animation-delay:{num(-i * 2.4 / 7)}s" d="M-2.2 .88H2.2"/></g>'
        for i in range(7)
    )
    return (
        '<clipPath id="tile-space"><rect width="196" height="196" rx="10"/></clipPath>'
        f'<g clip-path="url(#tile-space)"><path class="gridln" d="M0 {vy}H196{verts}"/>{lines}'
        f'<ellipse cx="{vx}" cy="132" rx="26" ry="5" fill="#fff" opacity=".05"/>'
        f'{globe(vx, 62, 30)}</g>'
    )


def tile_type(t: float) -> str:
    f = F["italic"]
    os2 = f.tt["OS/2"]
    size, base, x = 118, 150, 34
    xh, ch, desc = os2.sxHeight * size / f.upem, os2.sCapHeight * size / f.upem, -os2.sTypoDescender * size / f.upem
    guides = [(base - ch, "cap"), (base - xh, "x"), (base, "base"), (base + desc * 0.55, "desc")]
    b = [text("italic", "Ag", size, x, base)]
    for i, (y, name) in enumerate(guides):
        cls = "accln" if name == "base" else "guide"
        b.append(f'<path class="{cls}" pathLength="1" style="{draw(t + 0.25 + i * 0.12, 0.9)}" d="M12 {num(y)}H184"/>')
        b.append(text("mono", name, 6.5, 184, y - 3, "dim", 0.06, "end"))
    b.append(f'<circle class="guide" pathLength="1" style="{draw(t + 0.7, 1.2)}" cx="128" cy="{num(base - xh / 2)}" r="{num(xh / 2 + 2)}"/>')
    b.append(f'<path class="accln" pathLength="1" style="{draw(t + 0.9, 1)}" d="M70 {num(base - ch - 6)}L58 {num(base + 6)}"/>')
    return "".join(b)


def scene_practice(t0: float, t1: float) -> str:
    b = [on(label("PRACTICE", X0, 100), t0 + 0.1, t1 - 0.3),
         on(text("sans", "Four disciplines, one sensibility.", 30, X0 - 1, 140, "ink", -0.02), t0 + 0.15, t1 - 0.25, dy=18)]
    tiles = [
        ("UI/UX", tile_ui, ["Products, flows and systems", "that feel inevitable."]),
        ("Motion", tile_motion, ["Timing as a material —", "cinematic, never loud."]),
        ("Real-time 3D", tile_space, ["Unreal, Blender, Spline.", "Spaces you can step into."]),
        ("Visual identity", tile_type, ["Marks, type, and the rules", "that hold them together."]),
    ]
    for i, (name, art, desc) in enumerate(tiles):
        x, y = X0 + i * 212, 172
        ti = t0 + 0.35 + i * 0.12
        body = (f'<rect x=".5" y=".5" width="196" height="196" rx="10" class="frame"/>'
                + art(ti) + text("mono", f"FIG.0{i + 1}", 7, 12, 18, "dim", 0.12)
                + label(f"0{i + 1}", 0, 226, "dim", size=8.5)
                + text("sans_md", name, 19, 0, 252, "ink", -0.01)
                + text("sans", desc[0], 13, 0, 276, "sub") + text("sans", desc[1], 13, 0, 294, "sub"))
        b.append(on(f'<g transform="translate({x} {y})">{body}</g>', ti, t1 - 0.2 - (3 - i) * 0.04, dy=22))
    return "".join(b)


def scene_instruments(t0: float, t1: float) -> str:
    n = sum(len(tools) for _, tools in STACK)
    b = [on(label("INSTRUMENTS", X0, 100), t0 + 0.1, t1 - 0.3),
         on(text("sans", f"{n} tools, one workflow.", 30, X0 - 1, 140, "ink", -0.02), t0 + 0.15, t1 - 0.25, dy=18)]
    for c, (group, tools) in enumerate(STACK):
        x = X0 + c * 172
        tc = t0 + 0.3 + c * 0.1
        b.append(on(label(group, x, 196) + label(f"{len(tools):02d}", x + 150, 196, "dim", "end")
                    + f'<path class="hl" d="M{x} 206.5H{x + 150}"/>', tc, t1 - 0.3))
        for r, (name, src, cap) in enumerate(tools):
            y = 236 + r * 30
            item = (f'<g fill="{INK}" color="{INK}">{mark(name, src, cap, x, y - 13, 16)}</g>'
                    + text("sans", name, 13.5, x + 26, y, "ink"))
            b.append(on(item, tc + 0.12 + r * 0.06, t1 - 0.25, dy=10, din=0.6))
    band = timeline([(0, "transform:translateX(-200px)"), (t0 + 1.6, "transform:translateX(-200px)", "cubic-bezier(.45,0,.25,1)"),
                     (t0 + 3.4, "transform:translateX(1100px)"), (D, "transform:translateX(1100px)")])
    b.append(f'<rect x="0" y="180" width="140" height="300" fill="url(#band)" opacity=".06" style="{band}"/>')
    return "".join(b)


def scene_now(t0: float, t1: float) -> str:
    b = [on(label("NOW", X0, 100), t0 + 0.1, t1 - 0.3),
         on(text("italic", "Currently exploring —", 40, X0, 214, "sub"), t0 + 0.15, t1 - 0.25, dy=18)]
    slot_y, step = 312, 1.05
    items = []
    for i, (name, src) in enumerate(EXPLORING):
        a = t0 + 0.45 + i * step
        z = a + step
        below, above = "opacity:0;visibility:hidden;transform:translateY(90px)", "opacity:0;visibility:hidden;transform:translateY(-90px)"
        last = i == len(EXPLORING) - 1
        # outgoing and incoming names move together on the same curve, one slot apart
        stops = [(0, below), (a, below, EXPO), (a + 0.6, SHOWN)]
        stops += [(t1 - 0.35, SHOWN, EASE_IN), (t1, above), (D, above)] if last else [(z, SHOWN, EXPO), (z + 0.6, above), (D, above)]
        art = f'<g fill="{INK}">{mark(name, src, "", X0, slot_y - 52, 56)}</g>' + text("sans_sb", name, 76, X0 + 80, slot_y, "name", -0.04)
        items.append(f'<g style="{timeline(stops)}">{art}</g>')
        # index list on the right, active entry lit
        ly = 236 + i * 26
        lit = timeline([(0, hidden()), (a, hidden(), EXPO), (a + 0.3, SHOWN), ((t1 - 0.3) if last else z, SHOWN), ((t1) if last else z + 0.25, hidden()), (D, hidden())])
        b.append(on(label(f"0{i + 1}  {name.upper()}", 700, ly, "dim"), t0 + 0.3 + i * 0.05, t1 - 0.25, dy=8))
        b.append(f'<g style="{lit}"><circle cx="688" cy="{ly - 3.5}" r="3" fill="{ACC}"/>{label(f"0{i + 1}  {name.upper()}", 700, ly, "ink")}</g>')
    b.append(f'<clipPath id="slot"><rect x="40" y="{slot_y - 72}" width="620" height="88"/></clipPath><g clip-path="url(#slot)">{"".join(items)}</g>')
    prog = timeline([(0, "transform:scaleX(0)"), (t0 + 0.45, "transform:scaleX(0)"), (t1 - 0.3, "transform:scaleX(1)"), (D, "transform:scaleX(1)")])
    b.append(on(f'<path class="hl" d="M{X0} 350.5H{X0 + 560}"/>'
                f'<path d="M{X0} 350.5H{X0 + 560}" stroke="{ACC}" style="{prog};transform-origin:{X0}px 350px"/>', t0 + 0.4, t1 - 0.25, dy=0))
    return "".join(b)


def terrain(t0: float, t1: float) -> str:
    cols, rows = 30, 20
    cam, cx, horizon = 0.66, W / 2, 238

    def height(x: float, z: float) -> float:
        return 0.16 * math.sin(3.1 * x + 1.7 * z) + 0.09 * math.sin(6.3 * x - 2.2 * z + 1) + 0.3 * x * x + 0.06 * math.cos(2.6 * z)

    def project(x: float, z: float) -> tuple[float, float]:
        return cx + x / z * 420, horizon + (cam - height(x, z)) / z * 190

    zs = [0.42 + i * 0.13 for i in range(rows)]
    xs = [-1.45 + j * 2.9 / (cols - 1) for j in range(cols)]
    out = []
    for i, z in enumerate(zs):
        pts = " ".join(f"{num(px)},{num(py)}" for px, py in (project(x, z) for x in xs))
        op = max(0.08, 0.75 - i * 0.034)
        out.append(f'<polyline class="mesh" pathLength="1" style="{draw(t0 + 0.2 + i * 0.05, 1.1)};stroke-opacity:{num(op)}" points="{pts}"/>')
    for j, x in enumerate(xs):
        pts = " ".join(f"{num(px)},{num(py)}" for px, py in (project(x, z) for z in zs))
        out.append(f'<polyline class="mesh" pathLength="1" style="{draw(t0 + 0.6 + abs(j - cols / 2) * 0.02, 1.2)};stroke-opacity:.22" points="{pts}"/>')
    drift = timeline([(0, "transform:translateX(30px) scale(1.04)"), (t0, "transform:translateX(30px) scale(1.04)"),
                      (t1, "transform:translateX(-30px) scale(1.12)"), (D, "transform:translateX(-30px) scale(1.12)")])
    return (f'<clipPath id="land"><rect x="1" y="150" width="{W - 2}" height="388"/></clipPath>'
            f'<g clip-path="url(#land)"><g style="{drift};transform-origin:{W / 2}px 400px">{"".join(out)}</g>'
            f'<rect x="0" y="150" width="{W}" height="200" fill="url(#haze)"/></g>')


def scene_studio(t0: float, t1: float) -> str:
    b = [terrain(t0, t1)]
    b.append(on(label("STUDIO", X0, 100), t0 + 0.1, t1 - 0.3))
    b.append(on(cyte(X0, 124, 66) + text("sans_sb", "CYTE LAB", 46, X0 + 82, 172, "name", -0.02)
                + label("CREATIVE TECH STUDIO", X0 + 84, 192, size=9), t0 + 0.3, t1 - 0.3, dy=20))
    b.append(on(label("VIRTUAL PRODUCTION  ·  DIGITAL CREATION  ·  INDIE GAMES", X0, 236, "ink", size=9.5), t0 + 0.55, t1 - 0.25))
    b.append(on(label("GITHUB.COM/CYTE-LAB", X1, 192, "dim", "end", size=9), t0 + 0.6, t1 - 0.25))
    return "".join(b)


# ---------------------------------------------------------------- frame

def hud() -> str:
    b = []
    # viewfinder corners
    m, L = 36, 16
    corners = "".join(f"M{x} {y + L * sy}V{y}H{x + L * sx}" for x, y, sx, sy in
                      ((m, 56, 1, 1), (W - m, 56, -1, 1), (m, 530, 1, -1), (W - m, 530, -1, -1)))
    b.append(f'<path class="bracket" d="{corners}"/>')
    # top bar
    b.append(f'<circle class="rec" cx="{X0 - 6}" cy="30" r="3.6" fill="{ACC}"/>')
    b.append(text("mono_md", "REC", 9.5, X0 + 4, 33.5, "ink", 0.16))
    b.append(label("WILSONIU — REEL 2026", X0 + 4 + width("mono_md", "REC ", 9.5, 0.16) + 10, 33.5))
    b.append(label("24 FPS  ·  LOOP 00:24", W / 2, 33.5, "dim", "middle"))
    # timecode: digit strips stepped by CSS
    size, step = 9.5, 14
    wd = width("mono_md", "00", size, 0.16)
    colon = width("mono_md", ":", size, 0.16) + size * 0.16
    x_ff = X1 - wd
    x_ss = x_ff - colon - wd
    lead = "TC 00:00:"
    b.append(text("mono_md", lead, size, x_ss - size * 0.16, 33.5, "sub", 0.16, "end"))
    b.append(text("mono_md", ":", size, x_ff - colon, 33.5, "sub", 0.16))
    for key, x, dur in (("ss", x_ss, D), ("ff", x_ff, 1)):
        strip = "".join(text("mono_md", f"{i:02d}", size, x, 33.5 + i * step, "ink", 0.16) for i in range(24))
        b.append(f'<clipPath id="tc-{key}"><rect x="{num(x - 1)}" y="24" width="{num(wd + 2)}" height="12"/></clipPath>'
                 f'<g clip-path="url(#tc-{key})"><g style="animation:{key} {num(dur)}s steps(24) infinite">{strip}</g></g>')
    # bottom: progress + scene label + links
    b.append(f'<path class="hl" d="M{X0} 552.5H{X1}"/>')
    b.append(f'<path d="M{X0} 552.5H{X1}" stroke="{INK}" stroke-opacity=".7" style="animation:progress {D}s linear infinite;transform-origin:{X0}px 552px"/>')
    for i, (name, t0, t1) in enumerate(SCENES):
        start = max(t0, 0) if i else 0
        tx = X0 + (X1 - X0) * start / D
        b.append(f'<path class="tick" d="M{num(round(tx) + 0.5)} 548V557"/>')
        b.append(f'<g style="{life(t0 if i else -0.4, t1 if i < len(SCENES) - 1 else 23.6, dy=6, din=0.4, dout=0.3)}">'
                 + label(f"SC 0{i + 1}", X0, 578, "ink") + label(name, X0 + 52, 578) + "</g>")
    b.append(label("WILSONIU.COM  ·  @WILSONIUDESIGN", X1, 578, "sub", "end"))
    return "".join(b)


def reel() -> str:
    scenes = []
    builders = [scene_ident, scene_practice, scene_instruments, scene_now, scene_studio]
    for (name, t0, t1), build in zip(SCENES, builders):
        scenes.append(f'<g style="{life(t0 if t0 >= 0 else -1.25, t1, dy=0, din=0.35, dout=0.35)}">{build(t0, t1)}</g>')
    frame = hud()

    css = f"""
.ink{{fill:{INK}}}.sub{{fill:{SUB}}}.dim{{fill:{DIM}}}.acc{{fill:{ACC}}}.name{{fill:url(#name)}}
.hl{{stroke:{RULE};stroke-width:1;fill:none}}
.tick{{stroke:{DIM};stroke-width:1}}
.bracket{{stroke:{DIM};stroke-width:1.2;fill:none}}
.frame{{fill:#fff;fill-opacity:.015;stroke:{RULE}}}
.line{{fill:none;stroke:{SUB};stroke-width:1}}
.dimfill{{fill:{DIM}}}
.block{{fill:#fff;fill-opacity:.05;stroke:{INK};stroke-opacity:.25}}
.btn{{fill:{ACC};animation:btn 3s infinite}}
@keyframes btn{{0%,44%,70%,100%{{fill-opacity:.55}}50%,60%{{fill-opacity:1}}}}
.cursor{{animation:cursor 3s infinite}}
@keyframes cursor{{0%{{transform:translate(150px,168px);animation-timing-function:{EXPO}}}40%,62%{{transform:translate(58px,139px)}}48%{{transform:translate(58px,139px) scale(.85)}}66%{{transform:translate(58px,139px);animation-timing-function:cubic-bezier(.5,0,.75,0)}}100%{{transform:translate(150px,168px)}}}}
.ripple{{fill:none;stroke:{ACC};stroke-width:1.2;animation:ripple 3s infinite}}
@keyframes ripple{{0%,46%{{transform:scale(.2);opacity:0}}50%{{transform:scale(1);opacity:.9}}75%,100%{{transform:scale(3.4);opacity:0}}}}
.axisln{{fill:none;stroke:{DIM};stroke-width:1}}
.dash{{fill:none;stroke:{RULE};stroke-dasharray:2 3}}
.curve{{fill:none;stroke:{INK};stroke-width:1.6;stroke-dasharray:1}}
.handle{{fill:none;stroke:{ACC};stroke-opacity:.6;stroke-width:.8}}
.knot{{fill:{BG};stroke:{ACC};stroke-width:1}}
.ex{{animation:ex 2.6s infinite}}
@keyframes ex{{0%{{transform:none}}72%,100%{{transform:translateX(148px)}}}}
.ey{{animation:ey 2.6s infinite}}
@keyframes ey{{0%{{transform:none;animation-timing-function:cubic-bezier(.16,1,.3,1)}}72%,100%{{transform:translateY(-140px)}}}}
.gridln{{fill:none;stroke:{INK};stroke-opacity:.16;stroke-width:.8}}
.floor{{fill:none;stroke:{INK};stroke-width:1;vector-effect:non-scaling-stroke;animation:floor 2.4s infinite cubic-bezier(.7,0,1,.6)}}
@keyframes floor{{0%{{transform:scale(1);opacity:0}}25%{{opacity:.6}}100%{{transform:scale(110);opacity:.9}}}}
.guide{{fill:none;stroke:{SUB};stroke-opacity:.6;stroke-width:.8;stroke-dasharray:1}}
.accln{{fill:none;stroke:{ACC};stroke-width:1;stroke-dasharray:1}}
.mesh{{fill:none;stroke:{INK};stroke-width:.8;stroke-dasharray:1;stroke-linejoin:round}}
.lat{{fill:none;stroke:{INK};stroke-width:.8;stroke-opacity:.42;stroke-dasharray:0 3.2;stroke-linecap:round}}
.lat.back{{stroke-opacity:.13}}.lat.eq{{stroke-opacity:.7}}
.axis{{stroke:{SUB};stroke-width:.7;stroke-dasharray:1.5 3;fill:none}}
.limb{{fill:none;stroke:{INK};stroke-opacity:.5;stroke-width:1}}
.orbit{{fill:none;stroke:{INK};stroke-opacity:.16;stroke-width:.7}}
.mer{{fill:none;stroke:{INK};stroke-width:.8;vector-effect:non-scaling-stroke;animation:mo {SPIN}s infinite cubic-bezier(.37,0,.63,1)}}
.sx{{animation:sx {SPIN}s infinite}}
.sk{{animation:sk {SPIN}s infinite cubic-bezier(.37,0,.63,1)}}
@keyframes sx{{0%,50%{{transform:scaleX(.001);animation-timing-function:cubic-bezier(.61,1,.88,1)}}25%{{transform:scaleX(1);animation-timing-function:cubic-bezier(.12,0,.39,0)}}75%{{transform:scaleX(-1);animation-timing-function:cubic-bezier(.12,0,.39,0)}}100%{{transform:scaleX(.001)}}}}
@keyframes sk{{0%,100%{{transform:skewY({num(SKEW)}deg)}}50%{{transform:skewY(-{num(SKEW)}deg)}}}}
@keyframes mo{{0%,100%{{opacity:.9}}25%,75%{{opacity:.42}}50%{{opacity:.12}}}}
.rec{{animation:rec 1s steps(1) infinite}}
@keyframes rec{{50%{{opacity:.2}}}}
@keyframes ss{{to{{transform:translateY(-336px)}}}}
@keyframes ff{{to{{transform:translateY(-336px)}}}}
@keyframes progress{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
""" + "".join(f"@keyframes {name}{{{body}}}\n" for body, name in KEYFRAMES.items())

    defs = [
        *(f'<path id="{gid}" d="{d}"/>' for gid, d in GLYPHS.values() if d),
        f'<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
        '<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="760" x2="0" y2="-120"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#767A83"/></linearGradient>',
        f'<radialGradient id="sphere" cx=".18" cy=".12" r=".95"><stop offset="0" stop-color="#1B1D23"/><stop offset="1" stop-color="{BG}"/></radialGradient>',
        f'<radialGradient id="atmo"><stop offset=".7" stop-color="{INK}" stop-opacity="0"/><stop offset=".76" stop-color="{INK}" stop-opacity=".09"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="halo-acc"><stop offset="0" stop-color="{ACC}" stop-opacity=".5"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="halo-ink"><stop offset="0" stop-color="{INK}" stop-opacity=".4"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="vignette"><stop offset=".2" stop-color="{BG}" stop-opacity="0"/><stop offset=".5" stop-color="{BG}"/></radialGradient>',
        f'<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".45" stop-color="{BG}" stop-opacity=".6"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>',
        f'<pattern id="grid" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="{INK}"/></pattern>',
        '<linearGradient id="band"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
    ]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="wilsoniu — experience designer at CYTE LAB. A 24-second reel: ident, practice, instruments, now exploring, studio.">',
        "<title>wilsoniu — reel</title>",
        f"<style>{css}</style>",
        f"<defs>{''.join(defs)}</defs>",
        '<g clip-path="url(#c)">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        *scenes,
        frame,
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
