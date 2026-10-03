"""SHOT 01 — NAME. Builds 11.30-12.00 (before the wrap), holds through frame 0, exits 1.20-1.50.

Storyboard (reel seconds):
  11.30  hard cut in: an orange registration square pops at centre; type guides
         (ascender / x-height / baseline, plus the name's side bearings) slash across
         the frame on a 40 ms stagger, alternating direction.
  11.36  the orange hairline shoots out from the square, its end ticks riding the tips.
  11.38  "wilsoniu" pops up out of a baseline slot letter by letter (BACK, 35 ms).
  11.58  the caption types on behind a stepping orange cursor (10 ms a character).
  12.00  = frame 0: complete, crisp lockup. Hold: the camera keeps pushing in, the
         guides sink back, a specular sweep crosses the chrome name, the cursor blinks
         on the beat.
  1.20   exit: caption drops, letters shoot up out of the slot (20 ms), guides
         retract, the hairline collapses into the square. Hard cut at 1.50.
"""

import re

from fontTools.pens.boundsPen import BoundsPen

import lib
from lib import ACC, BACK, BG, DIM, EASE_IN, EXPO, SINE, T, W, H, at, num, text

NAME = "wilsoniu"
SIZE = 168
TRACK = -0.05
BASE = 346            # name baseline
LINE = 373            # orange hairline
CAP_Y = 198           # caption baseline
CAPTION = "EXPERIENCE DESIGNER — CYTE LAB"
CAP_SIZE = 10
CAP_TRACK = 0.16
CX = W / 2

START, END = 11.30, 1.50   # shot window (wraps)


def vis(tf: str = "none", op: float = 1) -> str:
    return f"opacity:{num(op)};visibility:visible;transform:{tf}"


def hid(tf: str = "none") -> str:
    return f"opacity:0;visibility:hidden;transform:{tf}"


def ink_bounds(face: str, ch: str) -> tuple[float, float, float, float]:
    f = lib.F[face]
    pen = BoundsPen(f.glyphs)
    f.glyphs[f.cmap[ord(ch)]].draw(pen)
    k = SIZE / f.upem
    x0, y0, x1, y1 = pen.bounds
    return x0 * k, y0 * k, x1 * k, y1 * k


def glyph_uses(markup: str) -> str:
    """Turn a text() group into bare <use> elements (clipPath children can't be <g>)."""
    tf = re.search(r'transform="([^"]+)"', markup).group(1)
    out = []
    for gid, gx in re.findall(r'<use href="#(g\d+)" x="([^"]+)"', markup):
        out.append(f'<use href="#{gid}" transform="{tf} translate({gx} 0)"/>')
    return "".join(out)


def build() -> str:
    lib.init()

    # ------------------------------------------------------------ layout
    lets = lib.letters("sans_bk", NAME, SIZE, CX, BASE, TRACK, "middle")
    name_l = lets[0][0] + ink_bounds("sans_bk", NAME[0])[0]
    name_r = lets[-1][0] + ink_bounds("sans_bk", NAME[-1])[2]
    asc = max(ink_bounds("sans_bk", c)[3] for c in NAME)          # 'i' dot / 'l' top
    xh = ink_bounds("sans_bk", "n")[3]
    lw = name_r - name_l
    mid = (name_l + name_r) / 2

    # ------------------------------------------------------------ type guides (behind everything)
    guides = []
    hlines = [(BASE - asc, "l"), (BASE - xh, "r"), (BASE, "l")]
    for i, (y, side) in enumerate(hlines):
        t0 = START + 0.01 + i * 0.04
        ox = 0 if side == "l" else W
        y = round(y) + 0.5
        g = f'<path d="M0 {num(y)}H{W}" stroke="{DIM}" stroke-width="1"/>'
        tout = 1.22 + i * 0.03
        guides.append(at(g, [
            (0, vis(op=0.32), SINE), (1.2, vis(op=0.2)),
            (tout, vis(op=0.2), EASE_IN), (tout + 0.16, vis("scaleX(0)", 0.2)),
            (END, hid("scaleX(0)")),
            (START, hid("scaleX(0)")), (t0, vis("scaleX(0)", 0.9), EXPO),
            (t0 + 0.3, vis(op=0.9), SINE), (T, vis(op=0.32)),
        ], origin=f"{ox}px {num(y)}px"))
    for i, (x, down) in enumerate([(name_l, True), (name_r, False)]):
        t0 = START + 0.02 + i * 0.04
        x = round(x) + 0.5
        oy = 0 if down else H
        g = f'<path d="M{num(x)} 0V{H}" stroke="{DIM}" stroke-width="1"/>'
        tout = 1.25 + i * 0.03
        guides.append(at(g, [
            (0, vis(op=0.26), SINE), (1.2, vis(op=0.16)),
            (tout, vis(op=0.16), EASE_IN), (tout + 0.16, vis("scaleY(0)", 0.16)),
            (END, hid("scaleY(0)")),
            (START, hid("scaleY(0)")), (t0, vis("scaleY(0)", 0.8), EXPO),
            (t0 + 0.3, vis(op=0.8), SINE), (T, vis(op=0.26)),
        ], origin=f"{num(x)}px {oy}px"))

    # ------------------------------------------------------------ name: letters rise out of a baseline slot
    slot_top = BASE - asc - 20   # just under the caption, room for the BACK overshoot
    lib.add_def(f'<clipPath id="s1-slot"><rect x="0" y="{num(slot_top)}" width="{W}" height="{num(BASE + 10 - slot_top)}"/></clipPath>')
    rise = asc + 30           # start fully below the slot
    lift = -(asc + 40)        # leave fully above it
    letter_groups, clip_uses = [], []
    for i, (x, _, ch) in enumerate(lets):
        glyph = text("sans_bk", ch, SIZE, x, BASE, "name")
        clip_uses.append(glyph_uses(glyph))
        tin, din = 11.38 + i * 0.035, 0.34
        tout, dout = 1.24 + i * 0.018, 0.12
        letter_groups.append(at(glyph, [
            (0, vis()), (tout, vis(), EASE_IN), (tout + dout, vis(f"translateY({num(lift)}px)")),
            (END, hid(f"translateY({num(lift)}px)")),
            (START, hid(f"translateY({num(rise)}px)")), (tin, vis(f"translateY({num(rise)}px)"), BACK),
            (tin + din, vis()), (T, vis()),
        ]))
    name = f'<g clip-path="url(#s1-slot)">{"".join(letter_groups)}</g>'

    # specular sweep across the resting name (clipped to the glyph outlines)
    lib.add_def(f'<clipPath id="s1-glyphs">{"".join(clip_uses)}</clipPath>')
    lib.add_def('<linearGradient id="s1-sheen" x1="0" x2="1" y1="0" y2="0">'
                '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/>'
                '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    band_w = 110
    top, bot = BASE - asc - 20, BASE + 20
    lean = (bot - top) * 0.32
    bx = name_l - band_w - lean - 10
    band = (f'<path d="M{num(bx + lean)} {num(top)}h{band_w}L{num(bx + band_w)} {num(bot)}h{-band_w}Z" fill="url(#s1-sheen)"/>')
    travel = lw + band_w + lean + 30
    sheen = at(band, [
        (0, hid()), (0.17, hid()), (0.18, vis(), SINE), (1.05, vis(f"translateX({num(travel)}px)")),
        (1.06, hid(f"translateX({num(travel)}px)")), (T, hid()),
    ])
    sheen = f'<g clip-path="url(#s1-glyphs)">{sheen}</g>'

    # ------------------------------------------------------------ hairline + registration square + end ticks
    line = f'<rect x="{num(name_l)}" y="{LINE - 0.5}" width="{num(lw)}" height="1" fill="{ACC}"/>'
    line = at(line, [
        (0, vis()), (1.32, vis(), EASE_IN), (1.46, vis("scaleX(0)")), (END, hid("scaleX(0)")),
        (START, hid("scaleX(0)")), (11.36, vis("scaleX(0)"), EXPO), (11.76, vis()), (T, vis()),
    ], origin=f"{num(mid)}px {LINE}px")
    ticks = []
    for x, d in ((name_l, 1), (name_r, -1)):
        tk = f'<path d="M{num(round(x) + 0.5 * d)} {LINE - 5}V{LINE + 5}" stroke="{ACC}" stroke-width="1"/>'
        far = f"translateX({num(d * lw / 2)}px)"
        ticks.append(at(tk, [
            (0, vis()), (1.32, vis(), EASE_IN), (1.46, vis(far)), (END, hid(far)),
            (START, hid(far)), (11.35, hid(far)), (11.36, vis(far), EXPO), (11.76, vis()), (T, vis()),
        ]))
    sq = f'<rect x="{num(mid - 2.5)}" y="{LINE - 2.5}" width="5" height="5" fill="{ACC}"/>'
    sq = at(sq, [
        (0, vis()), (END - 0.01, vis()), (END, hid()),
        (START, hid("scale(0)")), (START + 0.01, vis("scale(0)"), BACK), (START + 0.15, vis()), (T, vis()),
    ], origin=f"{num(mid)}px {LINE}px")

    # ------------------------------------------------------------ caption: typed on behind a stepping cursor
    n = len(CAPTION)
    cap_w = lib.width("mono", CAPTION, CAP_SIZE, CAP_TRACK)
    adv = (cap_w + CAP_SIZE * CAP_TRACK) / n            # mono: every cell is the same width
    cx0 = CX - cap_w / 2
    cap = text("mono", CAPTION, CAP_SIZE, CX, CAP_Y, "sub", CAP_TRACK, "middle")
    t_type0, t_type1 = 11.58, 11.88
    steps = f"steps({n},end)"
    cover = f'<rect x="{num(cx0)}" y="{CAP_Y - 11}" width="{num(n * adv)}" height="15" fill="{BG}"/>'
    cover = at(cover, [   # shrinks toward its right edge one cell per step, uncovering the caption
        (0, hid("scaleX(0)")), (START, hid()),
        (START + 0.01, vis()), (t_type0, vis(), steps), (t_type1, vis("scaleX(0)")),
        (t_type1 + 0.01, hid("scaleX(0)")), (T, hid("scaleX(0)")),
    ], origin=f"{num(cx0 + n * adv)}px {CAP_Y}px")
    cur = f'<rect x="{num(cx0 + 0.5)}" y="{CAP_Y - 8}" width="5.5" height="9" fill="{ACC}"/>'
    cur = at(cur, [  # blink on the beat while holding
        (0, "opacity:1", "steps(1,end)"), (0.25, "opacity:0", "steps(1,end)"), (0.5, "opacity:1", "steps(1,end)"),
        (0.75, "opacity:0", "steps(1,end)"), (1.0, "opacity:1"), (T, "opacity:1"),
    ])
    cur = at(cur, [
        (0, vis(f"translateX({num(n * adv)}px)")), (END - 0.01, vis(f"translateX({num(n * adv)}px)")),
        (END, hid(f"translateX({num(n * adv)}px)")),
        (START, hid()), (t_type0 - 0.05, hid()), (t_type0 - 0.04, vis()), (t_type0, vis(), steps),
        (t_type1, vis(f"translateX({num(n * adv)}px)")), (T, vis(f"translateX({num(n * adv)}px)")),
    ])
    caption = at(cap + cover + cur, [
        (0, vis()), (1.2, vis(), EASE_IN), (1.3, hid("translateY(12px)")), (END, hid("translateY(12px)")),
        (START, hid()), (START + 0.01, vis()), (T, vis()),
    ])

    # ------------------------------------------------------------ camera: one continuous push across the wrap
    k0, k1 = 1.0, 1.04
    span = (END + T) - START
    k_wrap = k0 + (k1 - k0) * (T - START) / span
    lockup = name + sheen + line + "".join(ticks) + sq + caption
    lockup = at(lockup, [
        (0, f"transform:scale({k_wrap:.4f})"), (END, f"transform:scale({k1})"),
        (START, f"transform:scale({k0})"), (T, f"transform:scale({k_wrap:.4f})"),
    ], origin=f"{num(CX)}px 300px")
    # guides sit on a slightly faster push, so the plate reads as parallax depth
    g_wrap = 1.0 + 0.06 * (T - START) / span
    guides_g = at("".join(guides), [
        (0, f"transform:scale({g_wrap:.4f})"), (END, "transform:scale(1.06)"),
        (START, "transform:scale(1)"), (T, f"transform:scale({g_wrap:.4f})"),
    ], origin=f"{num(CX)}px 300px")
    return guides_g + lockup
