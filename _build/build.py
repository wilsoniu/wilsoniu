# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "uharfbuzz"]
# ///
"""Builds the profile card for the README.

    uv run _build/build.py

Type is shaped with HarfBuzz and written out as outlines, since README images can't load
web fonts. Tool logos come from Simple Icons / Iconify and are cached in _build/.cache.
Motion is CSS transforms plus SMIL, both of which run inside GitHub's <img> sandbox.
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

STACK = [
    ("DESIGN", [("Figma", "si:figma"), ("Framer", "si:framer"), ("Photoshop", "iconify:devicon-plain/photoshop"),
                ("Illustrator", "iconify:devicon-plain/illustrator")]),
    ("MOTION", [("After Effects", "iconify:devicon-plain/aftereffects"), ("Premiere Pro", "iconify:devicon-plain/premierepro"),
                ("DaVinci Resolve", "si:davinciresolve")]),
    ("3D", [("Blender", "si:blender"), ("Unreal Engine", "si:unrealengine")]),
    ("AI", [("Claude Code", "si:claude"), ("OpenAI", "iconify:ri/openai-fill"), ("Grok", "iconify:thesvg/grok-xai"),
            ("Manus", "iconify:thesvg-color/manus-dark"), ("Cursor", "si:cursor")]),
    ("BUILD", [("VS Code", "iconify:devicon-plain/vscode"), ("Xcode", "si:xcode"), ("GitHub", "si:github"), ("Git", "si:git"),
               ("Linear", "si:linear"), ("Notion", "si:notion"), ("Webflow", "si:webflow"), ("Firebase", "si:firebase"),
               ("Replit", "si:replit")]),
]

# Traced (potrace) from the CYTE LAB avatar at github.com/CYTE-LAB.
CYTE_MARK = (189, 204, "M41.2 169.1L41.2 134.1L20.7 134.1L0.2 134.1L0.2 124.6L0.2 115.1L22 115.1C51.4 115.1 56.9 116.9 62.6 128.3L65.2 133.5L65.2 168.8L65.2 204.1L53.2 204.1L41.2 204.1L41.2 169.1ZM89.2 177.1L89.2 150.1L133.7 150.1L178.2 150.1L178.2 151.9C178.2 155.5 173.6 162.6 169.4 165.6L165 168.6L139.1 168.9L113.2 169.2L113.2 177.2L113.2 185.1L150.7 185.1C171.3 185.1 188.2 185.3 188.2 185.4C188.2 185.6 186 189.8 183.4 194.7L178.5 203.6L133.9 203.9L89.2 204.1L89.2 177.1ZM89.2 124.6L89.2 115.1L139.3 115.1L189.4 115.1L188.7 117.9C186.7 125.8 182 131.2 175.4 133.1C173.1 133.7 155.7 134.1 130.4 134.1L89.2 134.1L89.2 124.6ZM22.3 86.9C14.5 84.7 7.6 78.3 3.5 69.6L0.7 63.6L0.4 46.9C0 32.1 0.2 29.3 2.1 23.2C4.6 14.9 10.9 7.4 18.6 3.3L23.7 0.6L65.4 0.3L107.1 0L109.7 4.1C111.2 6.4 114.9 11.8 118 16.1C121.1 20.3 126.6 28 130.1 33L136.4 42.1L141.6 34.6C144.4 30.5 151 21 156.2 13.6L165.7 0.1L177 0.1C183.1 0.1 188.2 0.3 188.2 0.6C188.2 1.3 182 10.5 174.8 20.6C171.2 25.5 165.3 34 161.5 39.4C157.8 44.7 153.2 51.1 151.4 53.6L148.2 58L148.2 73L148.2 88.1L136.7 88.1L125.2 88.1L125.2 73.5L125.2 58.9L117.2 47.8C112.9 41.6 106.5 32.7 103 27.9L96.8 19.1L65.4 19.1C30.9 19.1 30.4 19.2 26 25.3L23.7 28.6L23.7 44.1C23.7 62.2 24.6 65 31.5 68.2L35.7 70.1L70.9 70.1L106 70.1L101 79.1L96 88.1L60.8 88C41.1 88 24.2 87.5 22.3 86.9Z")

# Adobe's solid tiles outweigh every other mark at 17px; draw them as outlined keycaps.
KEYCAP = {"Photoshop": "Ps", "Illustrator": "Ai", "After Effects": "Ae", "Premiere Pro": "Pr"}
# Per-mark optical scale so dense and airy logos read at the same weight.
OPTICAL = {"Figma": 1.08, "OpenAI": 1.08, "Firebase": 1.08, "Manus": 1.08, "Grok": 1.06, "Unreal Engine": 1.06,
           "Linear": 0.88, "VS Code": 0.9, "Xcode": 0.92}

INK, SUB, DIM, RULE, BG, ACC = "#EDEEF0", "#80838B", "#4A4D55", "#1E2026", "#07080A", "#FF5A1F"
EASE_OUT = "cubic-bezier(.16,1,.3,1)"
SPIN = 18  # seconds per revolution


def num(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def fetch(url: str, dest: Path) -> bytes:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "wilsoniu-readme-build"})
        dest.write_bytes(urllib.request.urlopen(req).read())
    return dest.read_bytes()


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


def label(s: str, x: float, y: float, cls: str = "sub", anchor: str = "start", size: float = 8) -> str:
    return text("mono", s, size, x, y, cls, 0.14, anchor)


def enter(body: str, delay: float) -> str:
    """Fade-and-rise on load; the wrapper keeps CSS transforms off the outlined text."""
    return f'<g class="in" style="animation-delay:{delay:.2f}s">{body}</g>'


def rule(x0: float, x1: float, y: float, delay: float) -> str:
    y += 0.5
    return (
        f'<path class="hl draw" pathLength="1" style="animation-delay:{delay:.2f}s" d="M{x0} {y}H{x1}"/>'
        + enter(f'<path class="hl" d="M{x0 + 0.5} {y - 3}V{y + 4}M{x1 - 0.5} {y - 3}V{y + 4}"/>', delay)
    )


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


ELEVATION = math.radians(16)
SKEW = math.degrees(math.atan(math.sin(ELEVATION)))


def globe(cx: float, cy: float, r: float, tilt: float = -14) -> list[str]:
    """An orthographic globe seen from slightly above, turning eastward.

    A meridian at longitude θ is the half-ellipse (rx=r, ry=r·cos e) transformed by
    scaleX(sin θ)·skewY(atan(cos θ·sin e)). Both factors are sinusoids in time, which CSS
    keyframes reproduce with sine easing, so each meridian is just nested transforms
    and the browser interpolates every frame. Inline styles hold the resting pose for
    renderers that don't animate.
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
    return out


def orbit(cx: float, cy: float, rx: float, ry: float, rot: float, dur: float, color: str, halo: str, layer: str, r: float) -> str:
    """A tilted orbit. The "under" layer is drawn whole beneath the sphere, which hides the
    part passing behind it; the "over" layer repeats it clipped to the sphere's front
    half-disk. Clip edges only fall inside the sphere, so nothing seams outside it.

    pathLength normalises the comet's dashes so they wrap seamlessly and stay locked to
    the satellite, which rides the same path with animateMotion.
    """
    d = f"M{rx} 0A{rx} {ry} 0 1 0 {-rx} 0A{rx} {ry} 0 1 0 {rx} 0"
    parts = [f'<path class="orbit" d="{d}"/>']
    for length, op, w in ((260, 0.12, 1.1), (130, 0.35, 1.3), (45, 0.9, 1.5)):
        parts.append(
            f'<path d="{d}" pathLength="1000" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-dasharray="{length} {1000 - length}">'
            f'<animate attributeName="stroke-dashoffset" values="{length};{length - 1000}" dur="{dur}s" repeatCount="indefinite"/></path>'
        )
    motion = f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{d}"/>'
    parts.append(f'<circle r="9" fill="url(#{halo})">{motion}</circle>')
    parts.append(f'<circle r="2.1" fill="#fff">{motion}</circle>')
    head = f'<g transform="translate({cx} {cy}) rotate({rot})">'
    if layer == "under":
        return head + "".join(parts) + "</g>"
    clip = f"orbit-{num(rx)}-over"
    return (
        head + f'<clipPath id="{clip}"><path d="M{-r} 0A{r} {r} 0 0 0 {r} 0Z"/></clipPath>'
        f'<g clip-path="url(#{clip})">{"".join(parts)}</g></g>'
    )


SWEEP_EVERY, SWEEP_FOR = 9, 2.6


def sweep_window(begin: float) -> str:
    """Show a masked sheen layer only during its sweep; a mask costs a re-composite every frame."""
    return (f'<animate attributeName="display" values="inline;none" keyTimes="0;{SWEEP_FOR / SWEEP_EVERY:.3f}" calcMode="discrete" '
            f'dur="{SWEEP_EVERY}s" begin="{begin}s" repeatCount="indefinite"/>')


def sweep(x0: float, x1: float, begin: float) -> str:
    return (f'<animate attributeName="x" values="{x0};{x1};{x1}" keyTimes="0;{SWEEP_FOR / SWEEP_EVERY:.3f};1" dur="{SWEEP_EVERY}s" '
            f'begin="{begin}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .25 1;0 0 1 1"/>')


def card() -> str:
    W, H, X0, X1 = 720, 374, 24, 696
    b: list[str] = []

    # Top bar
    b.append(enter(
        f'<circle cx="{X0 + 3}" cy="21" r="2.6" fill="{ACC}"/>'
        f'<circle class="ping" cx="{X0 + 3}" cy="21" r="2.6" fill="none" stroke="{ACC}"/>'
        + text("mono_md", "WILSONIU", 8.5, X0 + 13, 24, "ink", 0.18)
        + label("/ EXPERIENCE DESIGNER", X0 + 13 + width("mono_md", "WILSONIU", 8.5, 0.18) + 8, 24),
        0.05))
    b.append(enter(label("PROFILE / 2026", X1, 24, anchor="end"), 0.1))
    b.append(rule(X0, X1, 38, 0.1))

    # Identity
    b.append(enter(f'<g class="name"><g id="wordmark">{text("sans_sb", "wilsoniu", 58, X0 - 2, 106, "", -0.045)}</g></g>', 0.18))
    b.append(f'<g fill="#fff" mask="url(#name-sheen)" display="none">{sweep_window(6.1)}<use href="#wordmark"/></g>')
    b.append(enter(label("UI/UX  ·  MOTION  ·  REAL-TIME 3D  ·  VISUAL IDENTITY", X0, 131, size=8.5), 0.26))
    b.append(enter(
        text("sans", "Minimal systems, cinematic details,", 15.5, X0, 170, "sub", -0.01)
        + text("italic", "timeless taste.", 20, X0, 194, "ink"),
        0.34))

    _, mh, mark = CYTE_MARK
    chip_w = 46 + max(width("sans_md", "CYTE LAB", 13, 0.04), width("mono", "CREATIVE TECH STUDIO", 7, 0.14)) + 16
    b.append(enter(
        f'<rect class="chip" x="{X0 + 0.5}" y="214.5" width="{num(chip_w)}" height="42" rx="10"/>'
        f'<path fill="{INK}" transform="translate({X0 + 12} 224.5) scale({22 / mh:.4f})" d="{mark}"/>'
        + text("sans_md", "CYTE LAB", 13, X0 + 46, 234, "ink", 0.04)
        + text("mono", "CREATIVE TECH STUDIO", 7, X0 + 46, 247, "sub", 0.14),
        0.42))

    px = X0 + 12
    lead, now = "now exploring ", "Claude Code / Manus / Grok / Framer"
    b.append(enter(
        text("mono_md", "›", 10, X0, 284, "acc")
        + text("mono", lead.strip(), 9, px, 284, "dim")
        + text("mono", now, 9, px + width("mono", lead, 9), 284, "sub")
        + f'<rect class="caret" x="{num(px + width("mono", lead + now + " ", 9))}" y="276" width="5" height="10" fill="{INK}"/>',
        0.5))

    # Instrument panel
    px0, py0, px1, py1 = 404, 52, X1, 286
    corners = "".join(
        f"M{x + 0.5 * sx} {y + 10 * sy}V{y + 0.5 * sy}H{x + 10 * sx}"
        for x, y, sx, sy in ((px0, py0, 1, 1), (px1, py0, -1, 1), (px0, py1, 1, -1), (px1, py1, -1, -1))
    )
    b.append(enter(
        f'<path class="bracket" d="{corners}"/>'
        + label("FIG.01 — ORBIT", px0 + 14, py0 + 14, "dim", size=7)
        + label(f"REV {SPIN}S", px1 - 14, py1 - 8, "dim", "end", size=7),
        0.3))
    gx, gy, gr = 550, 168, 72
    orbits = [(122, 27, -12, 7.5, ACC, "halo-acc"), (100, 34, 24, 11.5, INK, "halo-ink")]
    globe_body = (
        "".join(orbit(gx, gy, *o, "under", gr) for o in orbits)
        + "".join(globe(gx, gy, gr))
        + "".join(orbit(gx, gy, *o, "over", gr) for o in orbits)
    )
    b.append(f'<g class="pop" style="transform-origin:{gx}px {gy}px">{globe_body}</g>')

    # Stack
    b.append(rule(X0, X1, 300, 0.45))
    size, group_gap = 17, 28
    n = sum(len(tools) for _, tools in STACK)
    gap = (X1 - X0 - n * size - (len(STACK) - 1) * group_gap) / (n - len(STACK))
    x, k, logos = X0, 0, []
    for group, tools in STACK:
        b.append(enter(label(group, x, 324, "dim", size=7), 0.5))
        build_label_end = x + width("mono", group, 7, 0.14)
        for name, src in tools:
            if name in KEYCAP:
                mark = (f'<g transform="translate({num(x)} 335)"><rect x="1" y="1" width="15" height="15" rx="3.5" '
                        f'style="fill:none;stroke:currentColor;stroke-width:1"/>{text("mono_md", KEYCAP[name], 8, 8.5, 11.35, "", 0, "middle")}</g>')
            else:
                vb, paths = icon(src)
                o = OPTICAL.get(name, 1)
                off = size * (1 - o) / 2
                inner = "".join(f'<path fill-rule="{fr}" d="{d}"/>' for d, fr in paths)
                mark = f'<g transform="translate({num(x + off)} {num(335 + off)}) scale({size * o / vb:.4f})">{inner}</g>'
            logos.append(enter(mark, 0.55 + k * 0.025))
            x += size + gap
            k += 1
        x += group_gap - gap
    # Tools with no public vector mark get named instead.
    also = "+ CANVA / FCP / MOTION / SPLINE"
    assert X1 - width("mono", also, 7, 0.14) > build_label_end + 12, "stack note collides with the BUILD label"
    b.append(enter(label(also, X1, 324, "dim", "end", size=7), 0.5))
    b.append(f'<g fill="{SUB}" color="{SUB}"><g id="logos">{"".join(logos)}</g></g>')
    b.append(f'<g fill="#fff" color="#fff" mask="url(#sheen)" display="none">{sweep_window(1.6)}<use href="#logos"/></g>')

    css = f"""
.ink{{fill:{INK}}}.sub{{fill:{SUB}}}.dim{{fill:{DIM}}}.acc{{fill:{ACC}}}.name{{fill:url(#name)}}
.hl{{stroke:{RULE};stroke-width:1;fill:none}}
.bracket{{stroke:{DIM};stroke-width:1;fill:none}}
.chip{{fill:{INK};fill-opacity:.025;stroke:{RULE}}}
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
.in{{animation:rise 1s {EASE_OUT} both}}
@keyframes rise{{from{{opacity:0;transform:translateY(7px)}}to{{opacity:1;transform:none}}}}
.draw{{stroke-dasharray:1;animation:draw 1.4s {EASE_OUT} both}}
@keyframes draw{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
.pop{{animation:pop 1.6s {EASE_OUT} .2s both}}
@keyframes pop{{from{{opacity:0;transform:scale(.86) rotate(-8deg)}}to{{opacity:1;transform:none}}}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 2.2s cubic-bezier(0,0,.2,1) infinite}}
@keyframes ping{{0%{{transform:scale(1);opacity:.8}}100%{{transform:scale(3.4);opacity:0}}}}
.caret{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
"""
    defs = [
        *(f'<path id="{gid}" d="{d}"/>' for gid, d in GLYPHS.values() if d),
        f'<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
        f'<radialGradient id="halo-acc"><stop offset="0" stop-color="{ACC}" stop-opacity=".5"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="halo-ink"><stop offset="0" stop-color="{INK}" stop-opacity=".4"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>',
        '<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="760" x2="0" y2="-120"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#767A83"/></linearGradient>',
        f'<radialGradient id="sphere" cx=".18" cy=".12" r=".95"><stop offset="0" stop-color="#1B1D23"/><stop offset="1" stop-color="{BG}"/></radialGradient>',
        f'<radialGradient id="atmo"><stop offset=".7" stop-color="{INK}" stop-opacity="0"/><stop offset=".76" stop-color="{INK}" stop-opacity=".09"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="vignette" cx="{gx}" cy="{gy}" r="150" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></radialGradient>',
        f'<pattern id="grid" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="{INK}"/></pattern>',
        '<linearGradient id="band"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<mask id="name-sheen" maskUnits="userSpaceOnUse" x="0" y="50" width="400" height="70"><rect x="-200" y="50" width="70" height="70" fill="url(#band)" opacity=".85" transform="skewX(-24)">'
        f'{sweep(-120, 560, 6.1)}</rect></mask>',
        f'<mask id="sheen" maskUnits="userSpaceOnUse" x="0" y="300" width="{W}" height="{H - 300}"><rect x="-300" y="300" width="110" height="{H - 300}" fill="url(#band)" transform="skewX(-24)">'
        f'{sweep(-200, 900, 1.6)}</rect></mask>',
    ]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="wilsoniu — experience designer at CYTE LAB. Minimal systems, cinematic details, timeless taste.">',
        "<title>wilsoniu — experience designer at CYTE LAB</title>",
        f"<style>{css}</style>",
        f"<defs>{''.join(defs)}</defs>",
        '<g clip-path="url(#c)">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<rect x="{gx - 150}" y="{gy - 150}" width="300" height="300" fill="url(#grid)" opacity=".13"/>',
        f'<rect x="{gx - 150}" y="{gy - 150}" width="300" height="300" fill="url(#vignette)"/>',
        *b,
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="#fff" stroke-opacity=".08"/>',
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
    path = OUT / "card.svg"
    path.write_text(card())
    print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
