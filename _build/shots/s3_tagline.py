"""SHOT 03 — TAGLINE TRIPTYCH. Three hard cuts of 2/3 s, one phrase each.

  A  3.50-4.17  "Minimal systems,"    an 8x5 module grid cascades in on the diagonal, the
                                       phrase rises out of a line mask letter by letter onto
                                       the grid; an ACC module ticks on the downbeat.
  B  4.17-4.83  "cinematic details,"   wireframe valley flyover; anamorphic bars slam in to
                                       2.39:1, the words punch in one after the other.
  C  4.83-5.50  "timeless taste."      a hairline horizon draws out from centre, an ACC sun
                                       rises behind it, serif italic tracks in; slow push.

Every sub-shot is cut into motion (its first frame is already moving) and keeps moving
until the next cut.
"""

import lib
from lib import ACC, BACK, BG, DIM, EASE_IN, EXPO, INK, SINE, SUB, T, W, H, X0, X1, label, letters, num, text, timeline, width

K = "s3"
A0 = 3.5
A1 = B0 = 3.5 + 2 / 3
B1 = C0 = 3.5 + 4 / 3
C1 = 5.5

BAR = round((H - W / 2.39) / 2)     # 99: letterbox bar height for 2.39:1
HIDE = "opacity:0;visibility:hidden"
SHOW = "opacity:1;visibility:visible"


def cut(body: str, t0: float, t1: float) -> str:
    """Hard cut: the body exists only in [t0, t1)."""
    stops = [(0, HIDE, "step-end"), (t0, SHOW, "step-end"), (t1, HIDE, "step-end"), (T, HIDE)]
    return f'<g style="{timeline(stops)}">{body}</g>'


def anim(body: str, stops: list[tuple], delay: float = 0.0, origin: str = "", tag: str = "g", attrs: str = "") -> str:
    """Reel-clock animation; `delay` shifts the whole timeline later (negative animation-delay, so no
    pre-start flash on load). Children of a cut() wrapper only, since the shift moves every stop."""
    style = timeline(stops)
    if delay:
        style += f";animation-delay:{delay - T:.3f}s"
    if origin:
        style += f";transform-origin:{origin}"
    if tag == "g":
        return f'<g style="{style}"{attrs}>{body}</g>'
    return f'<{tag} style="{style}"{attrs}/>'


def drift(body: str, t0: float, t1: float, frm: str, to: str, origin: str = "", ease: str = SINE) -> str:
    """Continuous move from frm to to across [t0, t1] (held at the ends)."""
    return anim(body, [(0, frm), (t0, frm, ease), (t1, to), (T, to)], origin=origin)


def index(n: str, t0: float) -> str:
    """Triptych counter, same spot in every sub-shot: the number cuts on a beat-sixteenth after the picture."""
    y = BAR - 14
    num_ = anim(label(n, X0, y, "ink"), [(0, "opacity:0"), (t0 + 0.06, "opacity:0", "step-end"), (t0 + 0.065, "opacity:1"), (T, "opacity:1")])
    return num_ + label("/ 03", X0 + width("mono", n + " ", 9.5, 0.16), y, "dim")


# ---------------------------------------------------------------- A: Minimal systems,

COLS, ROWS, CELL, GAP = 8, 5, 80, 12
PITCH = CELL + GAP
GX = W / 2 - (COLS * PITCH - GAP) / 2      # 118
GY = 74
TEXT_ROW, TEXT_SPAN = 2, 7


def shot_a() -> str:
    lib.add_css(f".{K}-cell{{fill:none;stroke:{DIM};stroke-opacity:.75;stroke-width:1}}")
    # cells: one shared keyframe, staggered on the diagonal by delay
    t0, dur, step = A0 - 0.07, 0.34, 0.024
    cell_stops = [(0, "transform:scale(0)"), (t0, "transform:scale(0)", EXPO), (t0 + dur, "transform:scale(1)"), (T, "transform:scale(1)")]
    cells = []
    for r in range(ROWS):
        for c in range(COLS):
            if r == TEXT_ROW and c < TEXT_SPAN:
                continue        # the phrase takes these modules
            x, y = GX + c * PITCH, GY + r * PITCH
            cells.append(anim("", cell_stops, delay=(c + r) * step, origin=f"{num(x + CELL / 2)}px {num(y + CELL / 2)}px", tag="rect",
                              attrs=f' class="{K}-cell" x="{num(x)}" y="{num(y)}" width="{CELL}" height="{CELL}"'))
    # registration ticks on the outer corners of the module
    gx1, gy1 = GX + COLS * PITCH - GAP, GY + ROWS * PITCH - GAP
    ticks = "".join(f"M{num(x - 6)} {num(y)}H{num(x + 6)}M{num(x)} {num(y - 6)}V{num(y + 6)}"
                    for x, y in ((GX - GAP / 2, GY - GAP / 2), (gx1 + GAP / 2, GY - GAP / 2), (GX - GAP / 2, gy1 + GAP / 2), (gx1 + GAP / 2, gy1 + GAP / 2)))
    ticks = anim(f'<path d="{ticks}" stroke="{SUB}" stroke-width="1" fill="none"/>',
                 [(0, "opacity:0"), (A0 + 0.12, "opacity:0", "step-end"), (A0 + 0.16, "opacity:1"), (T, "opacity:1")])
    grid = drift("".join(cells) + ticks, A0, A1, "transform:scale(1)", "transform:scale(1.045)", origin="480px 298px", ease="linear")

    # the ACC module: ticks on with the downbeat at 4.0, blinks once
    ac, ar = 7, 0
    ax, ay = GX + ac * PITCH, GY + ar * PITCH
    acc = anim(f'<rect x="{num(ax)}" y="{num(ay)}" width="{CELL}" height="{CELL}" fill="{ACC}"/>',
               [(0, "transform:scale(0)"), (3.86, "transform:scale(0)", BACK), (3.98, "transform:scale(1)"),
                (4.06, "transform:scale(1)", "step-end"), (4.065, "transform:scale(.18)", EXPO), (4.12, "transform:scale(.5)"), (T, "transform:scale(.5)")],
               origin=f"{num(ax + CELL / 2)}px {num(ay + CELL / 2)}px")
    acc = drift(acc, A0, A1, "transform:scale(1)", "transform:scale(1.045)", origin="480px 298px", ease="linear")

    # phrase: letters rise out of a line mask, left to right; baseline on the row-2 module edge
    size, base = 72, GY + TEXT_ROW * PITCH + CELL      # 338
    x0 = GX
    lib.add_def(f'<clipPath id="{K}-a-line"><rect x="0" y="{num(base - size)}" width="{W}" height="{num(size + 24)}"/></clipPath>')
    t0, dur, step = A0 - 0.05, 0.4, 0.013
    rise = [(0, "transform:translateY(96px)"), (t0, "transform:translateY(96px)", EXPO), (t0 + dur, "transform:none"), (T, "transform:none")]
    glyphs = []
    for i, (lx, _adv, ch) in enumerate(letters("sans_sb", TAG_A, size, x0, base, -0.02)):
        if ch.strip():
            glyphs.append(anim(text("sans_sb", ch, size, lx, base, "ink"), rise, delay=i * step))
    phrase = f'<g clip-path="url(#{K}-a-line)">{"".join(glyphs)}</g>'
    phrase = drift(phrase, A0, A1, "transform:translateX(0)", "transform:translateX(-12px)", ease="linear")

    return grid + acc + phrase + index("01", A0)


# ---------------------------------------------------------------- B: cinematic details,


def shot_b() -> str:
    hor = 268
    land = lib.terrain(prefix=f"{K}t", period=2.5, hor=hor)
    # camera: a slight push into the valley across the sub-shot
    land = drift(land, B0, B1, "transform:scale(1)", "transform:scale(1.06)", origin=f"480px {hor}px", ease="linear")
    lib.add_def(f'<linearGradient id="{K}-haze" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset=".42" stop-color="{BG}" stop-opacity=".88"/>'
                f'<stop offset=".58" stop-color="{BG}" stop-opacity=".88"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>')
    haze = f'<rect x="0" y="{hor - 110}" width="{W}" height="220" fill="url(#{K}-haze)"/>'

    # anamorphic bars slam in from the frame edges, each with a hairline on its inner edge
    edge = f'stroke="{INK}" stroke-opacity=".22" stroke-width="1" fill="none"'
    top = anim(f'<rect x="0" y="0" width="{W}" height="{BAR}" fill="{BG}"/><path d="M0 {BAR - 0.5}H{W}" {edge}/>',
               [(0, f"transform:translateY(-{BAR}px)"), (B0 - 0.03, f"transform:translateY(-{BAR}px)", EXPO), (B0 + 0.24, "transform:none"), (T, "transform:none")])
    bot = anim(f'<rect x="0" y="{H - BAR}" width="{W}" height="{BAR}" fill="{BG}"/><path d="M0 {H - BAR + 0.5}H{W}" {edge}/>',
               [(0, f"transform:translateY({BAR}px)"), (B0 - 0.03, f"transform:translateY({BAR}px)", EXPO), (B0 + 0.24, "transform:none"), (T, "transform:none")])

    # spec details inside the bars, ticking on one after another
    specs = [("ANAMORPHIC  2.39 : 1", X0 + 74, "dim", "start"),
             ("35MM  ·  T1.9  ·  180°", X1, "dim", "end")]
    tags = []
    for i, (s, x, cls, anchor) in enumerate(specs):
        t = B0 + 0.12 + i * 0.07
        tags.append(anim(label(s, x, BAR - 14, cls, anchor), [(0, "opacity:0"), (t, "opacity:0", "step-end"), (t + 0.01, "opacity:1"), (T, "opacity:1")]))

    # the words punch in on a triplet: scale settle from 1.08, each cut on
    size, base = 72, hor + 26
    w1, w2 = "cinematic", "details,"
    sp = width("sans_sb", " ", size)
    total = width("sans_sb", w1, size, -0.02) + sp + width("sans_sb", w2, size, -0.02)
    x1 = W / 2 - total / 2
    x2 = x1 + width("sans_sb", w1, size, -0.02) + sp
    words = []
    for s, x, t in ((w1, x1, B0 - 0.02), (w2, x2, B0 + 0.15)):
        w = width("sans_sb", s, size, -0.02)
        o = f"{num(x + w / 2)}px {num(base - 26)}px"
        words.append(anim(text("sans_sb", s, size, x, base, "ink", -0.02),
                          [(0, "opacity:0;transform:scale(1.14)"), (t, "opacity:0;transform:scale(1.14)", "step-end"),
                           (t + 0.005, "opacity:1;transform:scale(1.14)", EXPO), (t + 0.3, "opacity:1;transform:none"), (T, "opacity:1;transform:none")],
                          origin=o))
    words = drift("".join(words), B0, B1, "transform:scale(1)", "transform:scale(1.05)", origin=f"480px {base - 26}px", ease="linear")
    return land + haze + words + top + bot + "".join(tags) + index("02", B0)


# ---------------------------------------------------------------- C: timeless taste.

def shot_c() -> str:
    hor, size, base = 412, 132, 352
    # hairline horizon, drawn out from the centre
    line = anim(f'<path d="M{X0} {hor + 0.5}H{X1}" stroke="{INK}" stroke-opacity=".55" stroke-width="1" fill="none"/>',
                [(0, "transform:scaleX(0)"), (C0 - 0.05, "transform:scaleX(.08)", EXPO), (C0 + 0.45, "transform:none"), (T, "transform:none")],
                origin=f"480px {hor}px")
    # the sun: rises slowly behind the horizon, clipped by it
    lib.add_def(f'<clipPath id="{K}-sky"><rect x="0" y="0" width="{W}" height="{hor}"/></clipPath>')
    lib.add_def(f'<radialGradient id="{K}-glow"><stop offset="0" stop-color="{ACC}" stop-opacity=".55"/>'
                f'<stop offset=".35" stop-color="{ACC}" stop-opacity=".16"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>')
    lib.add_def(f'<linearGradient id="{K}-glint" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ACC}" stop-opacity="0"/>'
                f'<stop offset=".5" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient>')
    sun = (f'<circle cx="480" cy="{hor}" r="130" fill="url(#{K}-glow)"/>'
           f'<circle cx="480" cy="{hor}" r="15" fill="{ACC}"/>')
    sun = anim(sun, [(0, "transform:translateY(24px)"), (C0 - 0.05, "transform:translateY(24px)", "cubic-bezier(.2,.6,.4,1)"),
                     (C1, "transform:translateY(-9px)"), (T, "transform:translateY(-9px)")])
    sun = f'<g clip-path="url(#{K}-sky)">{sun}</g>'
    glint = anim(f'<rect x="360" y="{hor}" width="240" height="1" fill="url(#{K}-glint)"/>',
                 [(0, "transform:scaleX(.1);opacity:0"), (C0 + 0.05, "transform:scaleX(.1);opacity:0", SINE), (C1, "transform:none;opacity:1"), (T, "transform:none;opacity:1")],
                 origin=f"480px {hor}px")

    # serif italic tracks in toward the centre while fading up
    lay = letters("italic", TAG_C, size, W / 2, base, 0, "middle")
    t0 = C0 - 0.06
    glyphs = []
    for i, (lx, adv, ch) in enumerate(lay):
        if not ch.strip():
            continue
        dx = (lx + adv / 2 - W / 2) * 0.22
        glyphs.append(anim(text("italic", ch, size, lx, base, "ink"),
                           [(0, f"opacity:0;transform:translateX({num(dx)}px)"), (t0, f"opacity:0;transform:translateX({num(dx)}px)", EXPO),
                            (t0 + 0.55, "opacity:1;transform:none"), (T, "opacity:1;transform:none")],
                           delay=abs(i - (len(lay) - 1) / 2) * 0.012))
    words = drift("".join(glyphs), C0, C1, "transform:scale(1)", "transform:scale(1.06)", origin=f"480px {base - 40}px", ease="linear")
    scene = drift(sun + glint + line, C0, C1, "transform:scale(1)", "transform:scale(1.03)", origin=f"480px {hor}px", ease="linear")
    return scene + words + index("03", C0)


TAG_A, TAG_B, TAG_C = lib.TAGLINE


def build() -> str:
    return cut(shot_a(), A0, A1) + cut(shot_b(), B0, B1) + cut(shot_c(), C0, C1)
