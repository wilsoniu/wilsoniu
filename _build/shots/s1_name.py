"""SHOT 01 — NAME. Builds 11.30-12.00 (before the wrap), holds through frame 0, exits 1.18-1.50.

Storyboard (reel seconds):
  11.30  hard cut in: the white hairline shoots out from the centre of an empty frame.
  11.36  "wilsoniu" pops up out of a baseline slot letter by letter (BACK, 35 ms stagger).
  11.54  the caption rises word by word out of its own slot (EXPO, 30 ms stagger).
  12.00  = frame 0: complete, crisp lockup. Hold: the camera keeps pushing in and one
         the metal name rests.
  1.18   exit: caption words drop back into their slot, the letters shoot up out of
         theirs (18 ms), the hairline collapses to its centre. Hard cut at 1.50.

Minimal by design: one line (the hairline, 25 px under the lowest ink), no guides, no
ticks, no cursor; every reveal is motion behind a static clip, never a dissolve.
"""

import re

from fontTools.pens.boundsPen import BoundsPen

import lib
from lib import ACC, BACK, EASE_IN, EXPO, SINE, T, W, at, num, text

NAME = "wilsoniu"
SIZE = 168
TRACK = -0.05
BASE = 354            # name baseline (ink 232..356)
LINE = 381            # hairline: 25 px under the lowest ink (o/s/u overshoot)
CAP_Y = 204           # caption baseline: 28 px above the name's ink (cap top ~195)
CAPTION = "EXPERIENCE DESIGNER — CYTE LAB"
CAP_FACE = "mono"
CAP_SIZE = 13
CAP_TRACK = 0.16
CX = W / 2

START, END = 11.30, 1.50   # shot window (wraps)


def vis(tf: str = "none", op: float = 1) -> str:
    return f"opacity:{num(op)};visibility:visible;transform:{tf}"


def hid(tf: str = "none") -> str:
    return f"opacity:0;visibility:hidden;transform:{tf}"


def ink_bounds(face: str, ch: str, size: float = SIZE) -> tuple[float, float, float, float]:
    f = lib.F[face]
    pen = BoundsPen(f.glyphs)
    f.glyphs[f.cmap[ord(ch)]].draw(pen)
    k = size / f.upem
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
    lw = name_r - name_l
    mid = (name_l + name_r) / 2

    # ------------------------------------------------------------ name: letters rise out of a baseline slot
    slot_top = BASE - asc - 20   # room for the BACK overshoot, still clear of the caption slot
    slot_bot = BASE + 6          # just under the round overshoots; the hairline sits 21 px lower
    lib.add_def(f'<clipPath id="s1-slot"><rect x="0" y="{num(slot_top)}" width="{W}" height="{num(slot_bot - slot_top)}"/></clipPath>')
    rise = asc + 16           # start fully below the slot
    lift = -(asc + 40)        # leave fully above it
    letter_groups, clip_uses = [], []
    for i, (x, _, ch) in enumerate(lets):
        glyph = text("sans_bk", ch, SIZE, x, BASE, "name")
        clip_uses.append(glyph_uses(glyph))
        tin, din = 11.36 + i * 0.035, 0.34
        tout, dout = 1.24 + i * 0.018, 0.12
        letter_groups.append(at(glyph, [
            (0, vis()), (tout, vis(), EASE_IN), (tout + dout, vis(f"translateY({num(lift)}px)")),
            (END, hid(f"translateY({num(lift)}px)")),
            (START, hid(f"translateY({num(rise)}px)")), (tin, vis(f"translateY({num(rise)}px)"), BACK),
            (tin + din, vis()), (T, vis()),
        ]))
    name = f'<g clip-path="url(#s1-slot)">{"".join(letter_groups)}</g>'


    # ------------------------------------------------------------ the one line: hairline under the name
    line = f'<rect x="{num(name_l)}" y="{LINE - 0.75}" width="{num(lw)}" height="1.5" fill="{ACC}"/>'
    line = at(line, [
        (0, vis()), (1.32, vis(), EASE_IN), (1.46, vis("scaleX(0)")), (END, hid("scaleX(0)")),
        (START, hid("scaleX(0)")), (START + 0.01, vis("scaleX(0)"), EXPO), (START + 0.46, vis()), (T, vis()),
    ], origin=f"{num(mid)}px {LINE}px")

    # ------------------------------------------------------------ caption: words rise out of their own slot
    n = len(CAPTION)
    cap_w = lib.width(CAP_FACE, CAPTION, CAP_SIZE, CAP_TRACK)
    adv = (cap_w + CAP_SIZE * CAP_TRACK) / n            # mono: every cell is the same width
    cx0 = mid - cap_w / 2                               # centred on the name's ink, not its advance
    cap_top = CAP_Y - ink_bounds(CAP_FACE, "E", CAP_SIZE)[3]
    drop = CAP_Y + 4 - cap_top + 4                      # past the slot, round overshoots included
    lib.add_def(f'<clipPath id="s1-cap"><rect x="0" y="{num(cap_top - 4)}" width="{W}" height="{num(CAP_Y + 4 - (cap_top - 4))}"/></clipPath>')
    words = [(m.start(), m.group()) for m in re.finditer(r"\S+", CAPTION)]
    cap_groups = []
    for j, (i, word) in enumerate(words):
        w = text(CAP_FACE, word, CAP_SIZE, cx0 + i * adv, CAP_Y, "sub", CAP_TRACK)
        tin, din = 11.54 + j * 0.03, 0.32
        tout, dout = 1.18 + j * 0.02, 0.12
        cap_groups.append(at(w, [
            (0, vis()), (tout, vis(), EASE_IN), (tout + dout, vis(f"translateY({num(drop)}px)")),
            (END, hid(f"translateY({num(drop)}px)")),
            (START, hid(f"translateY({num(drop)}px)")), (tin, vis(f"translateY({num(drop)}px)"), EXPO),
            (tin + din, vis()), (T, vis()),
        ]))
    caption = f'<g clip-path="url(#s1-cap)">{"".join(cap_groups)}</g>'

    # ------------------------------------------------------------ camera: one continuous push across the wrap
    k0, k1 = 1.0, 1.04
    span = (END + T) - START
    k_wrap = k0 + (k1 - k0) * (T - START) / span
    lockup = name + line + caption
    return at(lockup, [
        (0, f"transform:scale({k_wrap:.4f})"), (END, f"transform:scale({k1})"),
        (START, f"transform:scale({k0})"), (T, f"transform:scale({k_wrap:.4f})"),
    ], origin=f"{num(CX)}px 300px")
