"""SHOT 03 — TAGLINE TRIPTYCH. Three hard cuts of 2/3 s, one phrase each.

  A  3.50-4.17  "Minimal systems,"    the phrase rises out of a line mask letter by letter; one
                                       hairline shoots out under it, an ACC square riding its head,
                                       and lands on the 4.0 downbeat.
  B  4.17-4.83  "cinematic details,"   fast wireframe valley flyover kept entirely below the phrase,
                                       which punches in, word by word, up in the sky; anamorphic
                                       bars slam in to 2.39:1.
  C  4.83-5.50  "timeless taste."      serif italic tracks in toward the centre on a fast push; a
                                       type stands alone, pushing in.

Every sub-shot is cut into motion (its first frame is already moving) and keeps moving
until the next cut. No captions, no counters: type, a hairline or terrain, nothing else.
Clearance: every stroke stays >= 16 px from every glyph in every frame (worked out below).
"""

import lib
from lib import ACC, BG, EXPO, INK, SINE, T, W, H, letters, num, text, timeline, width

K = "s3"
A0 = 3.5
A1 = B0 = 3.5 + 2 / 3
B1 = C0 = 3.5 + 4 / 3
C1 = 5.5

BAR = round((H - W / 2.39) / 2)     # 99: letterbox bar height for 2.39:1
HIDE = "opacity:0;visibility:hidden"
SHOW = "opacity:1;visibility:visible"
LAND = "cubic-bezier(.5,0,.1,1)"    # accelerate hard, brake onto the beat


def cut(body: str, t0: float, t1: float) -> str:
    """Hard cut: the body exists only in [t0, t1)."""
    stops = [(0, HIDE, "step-end"), (t0, SHOW, "step-end"), (t1, HIDE, "step-end"), (T, HIDE)]
    return f'<g style="{timeline(stops)}">{body}</g>'


def anim(body: str, stops: list[tuple], delay: float = 0.0, origin: str = "") -> str:
    """Reel-clock animation; `delay` shifts the whole timeline later (negative animation-delay, so no
    pre-start flash on load). Children of a cut() wrapper only, since the shift moves every stop."""
    style = timeline(stops)
    if delay:
        style += f";animation-delay:{delay - T:.3f}s"
    if origin:
        style += f";transform-origin:{origin}"
    return f'<g style="{style}">{body}</g>'


def drift(body: str, t0: float, t1: float, frm: str, to: str, origin: str = "", ease: str = "linear") -> str:
    """Continuous move from frm to to across [t0, t1] (held at the ends)."""
    return anim(body, [(0, frm), (t0, frm, ease), (t1, to), (T, to)], origin=origin)


# ---------------------------------------------------------------- A: Minimal systems,

def shot_a() -> str:
    # Geist 600 @72: 573 px wide, 51.7 px above the baseline, 11.3 px below (y, comma)
    size, base = 72, 300
    tw = width("sans_sb", TAG_A, size, -0.02)
    x0 = W / 2 - tw / 2
    # letters rise out of a line mask, left to right; the mask ends 14 px under the baseline
    clip_bottom = base + 14
    lib.add_def(f'<clipPath id="{K}-a-line"><rect x="0" y="{num(base - size)}" width="{W}" height="{num(clip_bottom - base + size)}"/></clipPath>')
    t0, dur, step = A0 - 0.05, 0.4, 0.013
    rise = [(0, "transform:translateY(96px)"), (t0, "transform:translateY(96px)", EXPO), (t0 + dur, "transform:none"), (T, "transform:none")]
    glyphs = []
    for i, (lx, _adv, ch) in enumerate(letters("sans_sb", TAG_A, size, x0, base, -0.02)):
        if ch.strip():
            glyphs.append(anim(text("sans_sb", ch, size, lx, base, "ink"), rise, delay=i * step))
    phrase = f'<g clip-path="url(#{K}-a-line)">{"".join(glyphs)}</g>'

    # one hairline under the phrase, exactly its width, 44 px below the baseline (32 px clear of
    # the descenders, 30 px clear of the mask edge); an ACC square rides its head onto the downbeat
    ly, sq = base + 44, 10
    draw = [(0, "transform:scaleX(0)"), (A0 - 0.1, "transform:scaleX(0)", LAND), (4.0, "transform:none"), (T, "transform:none")]
    line = anim(f'<path d="M{num(x0)} {ly + 0.5}H{num(x0 + tw)}" stroke="{INK}" stroke-opacity=".5" stroke-width="1" fill="none"/>',
                draw, origin=f"{num(x0)}px {ly}px")
    ride = [(0, "transform:none"), (A0 - 0.1, "transform:none", LAND), (4.0, f"transform:translateX({num(tw)}px)"), (T, f"transform:translateX({num(tw)}px)")]
    head = anim(f'<rect x="{num(x0 - sq / 2)}" y="{num(ly + 0.5 - sq / 2)}" width="{sq}" height="{sq}" fill="{ACC}"/>', ride)

    # the whole frame keeps sliding left through the cut
    return drift(phrase + line + head, A0, A1, "transform:translateX(0)", "transform:translateX(-16px)")


# ---------------------------------------------------------------- B: cinematic details,

def shot_b() -> str:
    # Phrase in the sky: Geist 600 @72, baseline 214 -> glyphs span 162..226. With the 1.14 punch
    # (about y 188) the lowest glyph pixel reaches 231. Terrain: horizon 300; its lines rise at most
    # 41.4 px above the horizon anywhere on screen (ridges and cross lines, checked numerically),
    # 45.5 px under the 1.1 camera push -> top 254.5, 23 px clear. A clip at 247 (16 px under the
    # lowest glyph pixel) guarantees it whatever happens.
    size, base, hor = 72, 214, 300
    push = 1.1
    land = lib.terrain(prefix=f"{K}t", period=2.0, hor=hor)
    land = drift(land, B0, B1, "transform:scale(1)", f"transform:scale({push})", origin=f"480px {hor}px")
    lib.add_def(f'<clipPath id="{K}-ground"><rect x="0" y="247" width="{W}" height="{H - 247}"/></clipPath>')
    land = f'<g clip-path="url(#{K}-ground)">{land}</g>'

    # anamorphic bars slam in from the frame edges, each with a hairline on its inner edge
    edge = f'stroke="{INK}" stroke-opacity=".22" stroke-width="1" fill="none"'

    def slam(dy: int) -> list[tuple]:
        return [(0, f"transform:translateY({dy}px)"), (B0 - 0.03, f"transform:translateY({dy}px)", EXPO), (B0 + 0.24, "transform:none"), (T, "transform:none")]

    top = anim(f'<rect x="0" y="0" width="{W}" height="{BAR}" fill="{BG}"/><path d="M0 {BAR - 0.5}H{W}" {edge}/>', slam(-BAR))
    bot = anim(f'<rect x="0" y="{H - BAR}" width="{W}" height="{BAR}" fill="{BG}"/><path d="M0 {H - BAR + 0.5}H{W}" {edge}/>', slam(BAR))

    # the words punch in on a triplet: cut on at 1.14, settle with EXPO
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
    words = drift("".join(words), B0, B1, "transform:scale(1)", "transform:scale(1.05)", origin=f"480px {base - 26}px")
    return land + words + top + bot


# ---------------------------------------------------------------- C: timeless taste.

def shot_c() -> str:
    # Instrument Serif italic @132: 98 px above the baseline, 1.3 below. Push 1.08 about y 300 puts
    # the lowest glyph pixel at 345. No horizon line: the type stands alone.
    size, base = 132, 340

    # letters track in toward the centre (EXPO); a quick opacity ramp rides the first part of the move
    lay = letters("italic", TAG_C, size, W / 2, base, 0, "middle")
    t0 = C0 - 0.08
    glyphs = []
    for i, (lx, adv, ch) in enumerate(lay):
        if not ch.strip():
            continue
        dx = (lx + adv / 2 - W / 2) * 0.3
        lag = abs(i - (len(lay) - 1) / 2) * 0.008
        g = anim(text("italic", ch, size, lx, base, "ink"),
                 [(0, f"transform:translateX({num(dx)}px)"), (t0, f"transform:translateX({num(dx)}px)", EXPO),
                  (t0 + 0.5, "transform:none"), (T, "transform:none")], delay=lag)
        glyphs.append(anim(g, [(0, "opacity:0"), (t0, "opacity:0", SINE), (t0 + 0.12, "opacity:1"), (T, "opacity:1")], delay=lag))
    words = drift("".join(glyphs), C0, C1, "transform:scale(1)", "transform:scale(1.08)", origin=f"480px {base - 40}px")
    return words


TAG_A, TAG_B, TAG_C = lib.TAGLINE


def build() -> str:
    return cut(shot_a(), A0, A1) + cut(shot_b(), B0, B1) + cut(shot_c(), C0, C1)
