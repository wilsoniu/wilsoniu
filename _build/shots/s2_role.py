"""s2 — ROLE (1.5 → 3.5).

1.50  "Experience" whips in from the right letter by letter, "Designer" from the left; they pass
      each other, lock with a small overshoot and a lean that springs back, then keep drifting
      apart while the frame pushes in. One thin ACC rule shoots out of "Designer" to the margin.
2.45  Hard cut. The disciplines fire one every 0.26s, each hard-cut: a scale pop, letters that rise
      in a quick wave, tracking that breathes out while it holds. A [ ] frame slams in from the
      edges and opens just ahead of every cut, so the next (wider) word always lands inside it
      with clear air around it — the frame never touches a letter.
3.50  Hard cut out.
"""

from lib import ACC, DISCIPLINES, EXPO, INK, SINE, T, X0, X1, at, letters, num, off, text, width

K = "s2"
T0, T1 = 1.5, 3.5
CUT = 2.45      # lockup -> disciplines
STEP = 0.26     # one discipline per step
POP = 1.08      # each word lands 8% large and snaps to size
OPEN = 0.09     # the frame opens this long before each cut
SNAP = "cubic-bezier(.5,0,.1,1)"   # quick in, quick settle: the frame's opening move
ON = "opacity:1;visibility:visible;transform:none"


def gate(body: str, t0: float, t1: float) -> str:
    """Hard cut in at t0, hard cut out at t1 (no fades)."""
    return at(body, [(0, off(), "step-end"), (t0, ON, "step-end"), (t1, off()), (T, off())])


def fly(face: str, s: str, size: float, x: float, y: float, tracking: float, start: float, stagger: float,
        reverse: bool, dx: float, lean: float) -> str:
    """Per-letter whip-in: from dx (leaning into the motion) to a small overshoot, then settle."""
    ls = letters(face, s, size, x, y, tracking)
    sign = 1 if dx > 0 else -1
    out = []
    for i, (lx, _, ch) in enumerate(ls):
        if ch.isspace():
            continue
        t = start + stagger * ((len(ls) - 1 - i) if reverse else i)
        frm = f"transform:translateX({num(dx)}px) skewX({num(lean)}deg)"
        over = f"transform:translateX({num(-sign * 9)}px) skewX({num(-lean * 0.3)}deg)"
        stops = [(0, frm), (t, frm, EXPO), (t + 0.3, over, SINE), (t + 0.46, "transform:none"), (T, "transform:none")]
        out.append(at(text(face, ch, size, lx, y, "ink"), stops, f"{num(lx)}px {num(y)}px"))
    return "".join(out)


def lockup() -> str:
    ey, dy = 270, 384
    exp = fly("sans_bk", "Experience", 110, X0, ey, -0.03, T0, 0.024, False, 960, 16)
    des = fly("italic", "Designer", 130, X0, dy, 0, T0 + 0.06, 0.026, True, -960, -16)
    # after locking the lines keep drifting apart (they cross alignment at ~2.15)
    exp = at(exp, [(0, "transform:translateX(14px)"), (T0, "transform:translateX(14px)"), (CUT, "transform:none"), (T, "transform:none")])
    des = at(des, [(0, "transform:translateX(-4px)"), (T0, "transform:translateX(-4px)"), (CUT, "transform:translateX(10px)"),
                   (T, "transform:translateX(10px)")])
    # ACC rule shot out of "Designer" to the right margin, at mid x-height; it starts well clear of the
    # final "r" even with that letter's overshoot, the drift and the push-in
    rx = X0 + width("italic", "Designer", 130) + 48
    ry = dy - 33.5
    rule = at(f'<path d="M{num(rx)} {num(ry)}H{X1}" stroke="{ACC}" stroke-width="1.5" fill="none"/>',
              [(0, "transform:scaleX(0)"), (1.84, "transform:scaleX(0)", EXPO), (2.26, "transform:none"), (T, "transform:none")],
              f"{num(rx)}px {num(ry)}px")
    # slow push-in anchored on the left margin, so the type never crosses X0
    body = at(exp + des, [(0, "transform:none"), (T0, "transform:none"), (CUT, "transform:scale(1.02)"), (T, "transform:scale(1.02)")],
              f"{X0}px 320px")
    return gate(body + rule, T0, CUT)


def disciplines() -> str:
    cx, wy, size, track = 480, 336, 96, -0.03
    top, bot, arm, grow, air = 240, 372, 12, 5, 26
    mid = (top + bot) / 2
    times = [CUT + STEP * k for k in range(len(DISCIPLINES))]
    ends = times[1:] + [T1]
    widths = [width("sans_bk", w, size, track) for w in DISCIPLINES]

    words = []
    for word, w, t, e in zip(DISCIPLINES, widths, times, ends):
        glyphs = []
        for lx, adv, ch in letters("sans_bk", word, size, cx, wy, track, "middle"):
            if ch.isspace():
                continue
            d = (lx + adv / 2 - cx) / (w / 2) * grow   # tracking breathes out while the word holds
            ts = t + 0.009 * len(glyphs)                # letters rise in a quick wave under the pop
            mid_x = d * (ts + 0.14 - t) / (e - t)
            glyphs.append(at(text("sans_bk", ch, size, lx, wy, "ink"),
                             [(0, "transform:translate(0px,16px)"), (ts, "transform:translate(0px,16px)", EXPO),
                              (ts + 0.14, f"transform:translate({num(mid_x)}px,0px)"), (e, f"transform:translate({num(d)}px,0px)"),
                              (T, f"transform:translate({num(d)}px,0px)")]))
        pop = at("".join(glyphs), [(0, f"transform:scale({POP})"), (t, f"transform:scale({POP})", EXPO), (t + 0.12, "transform:none"),
                                   (T, "transform:none")], f"{cx}px {num(mid)}px")
        words.append(gate(pop, t, e))

    # [ ] frame. Each word's frame sits `air` px outside that word *at its pop size*, so the landing
    # word never reaches it. Every word is wider than the last, so the frame opens just before each
    # cut (moving away from the word on screen) and is already in place when the next word lands.
    pos = [POP * w / 2 + air for w in widths]

    def side(sgn: int) -> str:
        edge = 444
        sy = 3.7

        def st(x: float, s: float = 1) -> str:
            return f"transform:translateX({num(sgn * x)}px) scaleY({s})"
        stops = [(0, st(edge, sy)), (CUT, st(edge, sy), EXPO), (CUT + 0.16, st(pos[0] + grow * 0.16 / STEP))]
        for k in range(1, len(pos)):
            stops += [(times[k] - OPEN, st(pos[k - 1] + grow * (STEP - OPEN) / STEP), SNAP), (times[k], st(pos[k]))]
        stops += [(T1, st(pos[-1] + grow)), (T, st(pos[-1] + grow))]
        path = (f'<path d="M{cx - sgn * arm} {top}H{cx}V{bot}H{cx - sgn * arm}" fill="none" stroke="{INK}" stroke-width="1.4" '
                f'vector-effect="non-scaling-stroke"/>')
        return at(path, stops, f"{cx}px {num(mid)}px")

    body = "".join(words) + side(-1) + side(1)
    body = at(body, [(0, "transform:none"), (CUT, "transform:none"), (T1, "transform:scale(1.04)"), (T, "transform:scale(1.04)")],
              f"{cx}px {num(mid)}px")
    return gate(body, CUT, T1)


def build() -> str:
    return lockup() + disciplines()
