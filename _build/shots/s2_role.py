"""s2 — ROLE (1.5 → 3.5).

1.50  "Experience" whips in from the right letter by letter, "Designer" from the left; they pass
      each other, lock with a small overshoot and a lean that springs back, then keep drifting
      apart while the frame pushes in. An ACC rule draws out of "Designer" to a typed ROLE caption.
2.45  Hard cut. The disciplines fire one every 0.26s, each hard-cut: a scale pop, tracking that
      breathes out while it holds, a [ ] reticle that slams in from the viewfinder edges and then
      snaps to each word's width, and an odometer counter 01 / 04 … 04 / 04.
3.50  Hard cut out.
"""

from lib import ACC, DISCIPLINES, EXPO, INK, SINE, T, X0, X1, add_def, at, letters, num, off, text, width

K = "s2"
T0, T1 = 1.5, 3.5
CUT = 2.45      # lockup -> disciplines
STEP = 0.26     # one discipline per step
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


def typed(s: str, x: float, y: float, cls: str, anchor: str, size: float, start: float, end: float, gap: float = 0.022) -> str:
    """Mono caption that types on letter by letter (each letter a hard cut)."""
    out = []
    for i, (lx, _, ch) in enumerate(letters("mono", s, size, x, y, 0.16, anchor)):
        if not ch.isspace():
            out.append(gate(text("mono", ch, size, lx, y, cls), start + i * gap, end))
    return "".join(out)


def lockup() -> str:
    ey, dy = 270, 384
    exp = fly("sans_bk", "Experience", 110, X0, ey, -0.03, T0, 0.024, False, 960, 16)
    des = fly("italic", "Designer", 130, X0, dy, 0, T0 + 0.06, 0.026, True, -960, -16)
    # after locking the lines keep drifting apart (they cross alignment at ~2.15)
    exp = at(exp, [(0, "transform:translateX(14px)"), (T0, "transform:translateX(14px)"), (CUT, "transform:none"), (T, "transform:none")])
    des = at(des, [(0, "transform:translateX(-4px)"), (T0, "transform:translateX(-4px)"), (CUT, "transform:translateX(10px)"),
                   (T, "transform:translateX(10px)")])
    # ACC rule drawn out of "Designer" toward the caption (kept out of the push-in so ROLE stays inside X1)
    rx = X0 + width("italic", "Designer", 130) + 38
    ry = dy - 33.5
    rule = at(f'<path d="M{num(rx)} {num(ry)}H{X1}" stroke="{ACC}" stroke-width="1.5" fill="none"/>',
              [(0, "transform:scaleX(0)"), (1.84, "transform:scaleX(0)", EXPO), (2.26, "transform:none"), (T, "transform:none")],
              f"{num(rx)}px {num(ry)}px")
    tick = gate(f'<path d="M{X1 - 0.75} {num(ry - 5)}V{num(ry + 5)}" stroke="{ACC}" stroke-width="1.5"/>', 2.0, CUT)
    cap = typed("ROLE", X1, ry - 12, "sub", "end", 11, 1.96, CUT, 0.035)
    # slow push-in anchored on the left margin, so the type never crosses X0
    body = at(exp + des, [(0, "transform:none"), (T0, "transform:none"), (CUT, "transform:scale(1.02)"), (T, "transform:scale(1.02)")],
              f"{X0}px 320px")
    return gate(body + rule + tick + cap, T0, CUT)


def disciplines() -> str:
    cx, wy, size, track = 480, 336, 96, -0.03
    top, bot, arm, pad, grow = 240, 372, 18, 34, 5
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
        pop = at("".join(glyphs), [(0, "transform:scale(1.08)"), (t, "transform:scale(1.08)", EXPO), (t + 0.12, "transform:none"),
                                   (T, "transform:none")], f"{cx}px {num(mid)}px")
        words.append(gate(pop, t, e))

    # [ ] reticle: slams in from the viewfinder edges, then snaps to each word's width
    def side(sgn: int) -> str:
        edge = 36 if sgn < 0 else 924
        pos = [cx + sgn * (w / 2 + pad) for w in widths]
        sy = 3.7

        def st(x: float, s: float = 1) -> str:
            return f"transform:translateX({num(x)}px) scaleY({s})"
        stops = [(0, st(edge, sy)), (CUT, st(edge, sy), EXPO), (CUT + 0.16, st(pos[0]))]
        for k in range(1, len(pos)):
            stops += [(times[k], st(pos[k - 1] + sgn * grow), EXPO), (times[k] + 0.11, st(pos[k]))]
        stops += [(T1, st(pos[-1] + sgn * grow)), (T, st(pos[-1] + sgn * grow))]
        a = -sgn * arm
        path = (f'<path d="M{a} {top}H0V{bot}H{a}M0 {num(mid)}h{-sgn * 7}" fill="none" stroke="{INK}" stroke-width="1.4" '
                f'vector-effect="non-scaling-stroke"/>')
        return at(path, stops, f"0px {num(mid)}px")

    # counter: 0N / 04, N on an odometer strip
    cy, csize = 405, 12
    pos = letters("mono_md", "01 / 04", csize, cx, cy, 0.14, "middle")
    dx = pos[1][0]
    add_def(f'<clipPath id="{K}-odo"><rect x="{num(dx - 2)}" y="{cy - 12}" width="{num(pos[1][1] + 4)}" height="16"/></clipPath>')
    strip = "".join(text("mono_md", str(j + 1), csize, dx, cy + 16 * j, "acc") for j in range(len(DISCIPLINES)))
    ostops = [(0, "transform:none")]
    for k in range(1, len(times)):
        ostops += [(times[k], f"transform:translateY({-16 * (k - 1)}px)", EXPO), (times[k] + 0.1, f"transform:translateY({-16 * k}px)")]
    ostops += [(T, f"transform:translateY({-16 * (len(times) - 1)}px)")]
    counter = (text("mono_md", "0", csize, pos[0][0], cy, "acc") + f'<g clip-path="url(#{K}-odo)">{at(strip, ostops)}</g>'
               + text("mono_md", "/ 04", csize, pos[3][0], cy, "sub", 0.14))

    head = typed("DISCIPLINES", cx, 216, "sub", "middle", 10, CUT, T1, 0.016)
    body = "".join(words) + side(-1) + side(1) + counter + head
    body = at(body, [(0, "transform:none"), (CUT, "transform:none"), (T1, "transform:scale(1.04)"), (T, "transform:scale(1.04)")],
              f"{cx}px {num(mid)}px")
    return gate(body, CUT, T1)


def build() -> str:
    return lockup() + disciplines()
