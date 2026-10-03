"""SHOT 05 — NOW EXPLORING (8.0-9.5s).

8.00  an ACC block and NOW EXPLORING slam in huge at the centre of frame, then whip straight up
      into a 16px caption centred above the montage, landing on the 8.20 cut; it stays there,
      and the ACC block kicks on every cut after that
8.20  strobe montage of lib.EXPLORING, one tool per 0.30s, hard cuts on the beat grid. The whole
      frame flows right-to-left through every cut on a speed ramp (fast in, slow middle, fast out,
      so the motion matches across each cut) while it settles from a punch-in; the logo springs
      in, the name's letters rise (or drop) out of a slot one by one, and an ACC bar wipes under
      the name. Compositions alternate: logo|name, name|logo, stacked, logo|name.
9.40  all four logos snap into a row on the beat, then cut
"""

import lib
from lib import ACC, EXPO, BACK, INK, T, num, text, letters, width, mark

KEY = "s5"
T0, T1 = lib.SHOTS[KEY]
E = 0.004                 # a hard cut: 4ms ramp, below one frame
VIS = "opacity:1;visibility:visible;"
HID = "opacity:0;visibility:hidden;"
CY = 304                  # optical centre of the montage (below the caption)

CUTS = [8.20, 8.50, 8.80, 9.10, 9.40]
# fast in, slow through the middle, fast out: a speed ramp whose ends match across a cut
RAMP = "cubic-bezier(.2,.75,.8,.25)"
DRIFT = "cubic-bezier(.4,0,.85,.55)"   # starts from rest after a settle, leans into the cut
WHIP = "cubic-bezier(.7,0,.2,1)"       # rest to rest, all the speed in the middle

CAP_SIZE, CAP_TRACK, CAP_BASE = 16, 0.16, 104


def anim(body: str, stops: list[tuple], origin: str = "") -> str:
    """Reel-clock animation that is hidden at 0 and T (stops are inside the shot)."""
    return lib.at(body, [(0, HID + "transform:none"), *stops, (T, HID + "transform:none")], origin)


def window(body: str, t0: float, t1: float, start: str, settle: str, end: str, pop: float = 0.12,
           ease: str = EXPO, origin: str = "", delay: float = 0.0, step: bool = False) -> str:
    """Hard cut on at t0 (+delay, holding `start` until then; hidden until then if step), animate
    start->settle over `pop`, drift settle->end until t1 (from rest, no velocity kink), hard cut off at t1."""
    a = t0 + delay
    on = a if step else t0
    stops = [(on - E, HID + start), (on, VIS + start)]
    stops.append((a, VIS + start, ease))
    stops += [(a + pop, VIS + settle, DRIFT), (t1 - E, VIS + end), (t1, HID + end)]
    assert all(x[0] <= y[0] for x, y in zip(stops, stops[1:])), (t0, t1, delay, pop)
    return anim(body, stops, origin)


def flow(body: str, t0: float, t1: float, dx: float, punch: float) -> str:
    """The cut's camera: on at t0 punched in and right of centre, ramps right-to-left through
    centre to the mirror position at t1, settling the punch on the way. Every cut flows the same
    way, so the hard cuts read as one continuous pass."""
    a = f"transform:translateX({num(dx)}px) scale({punch})"
    b = f"transform:translateX({num(-dx)}px) scale(1)"
    return anim(body, [(t0 - E, HID + a), (t0, VIS + a, RAMP), (t1 - E, VIS + b), (t1, HID + b)], f"480px {CY}px")


def kinetic_name(s: str, size: float, x: float, base: float, t0: float, t1: float, rise: int, stagger: float = 0.007,
                 anchor: str = "start", slot_id: str = "") -> str:
    """Per-letter type that rises (rise=1) or drops (rise=-1) out of a static slot clip. The slot's
    floor sits on the baseline, so no glyph ever dips toward the ACC bar underneath."""
    cap = size * 0.71
    travel = (cap + size * 0.18) * rise
    lid = f"{KEY}-slot-{slot_id}"
    lx = letters("sans_bk", s, size, x, base, -0.035, anchor)
    x_lo, x_hi = lx[0][0] - size * 0.2, lx[-1][0] + lx[-1][1] + size * 0.2
    top, bot = base - cap - size * 0.12, base + size * 0.03
    lib.add_def(f'<clipPath id="{lid}"><rect x="{num(x_lo)}" y="{num(top)}" '
                f'width="{num(x_hi - x_lo)}" height="{num(bot - top)}"/></clipPath>')
    out = []
    k = 0
    for lx_, _, ch in lx:
        if ch == " ":
            continue
        g = text("sans_bk", ch, size, lx_, base, "ink")
        out.append(window(g, t0, t1, f"transform:translateY({num(travel)}px)", "transform:none", "transform:none",
                          pop=0.12, delay=0.012 + k * stagger))
        k += 1
    return f'<g clip-path="url(#{lid})">{"".join(out)}</g>'


def underline(x: float, y: float, w: float, t0: float, t1: float, from_right: bool = False) -> str:
    """ACC bar 20px under the baseline (none of the names has a descender)."""
    ox = x + w if from_right else x
    bar = f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="6" fill="{ACC}"/>'
    return window(bar, t0, t1, "transform:scaleX(0)", "transform:scaleX(1)", "transform:scaleX(1)",
                  pop=0.16, delay=0.04, origin=f"{num(ox)}px {num(y + 3)}px")


def logo(name: str, src: str, x: float, y: float, size: float, t0: float, t1: float, tilt: float) -> str:
    cx, cy = x + size / 2, y + size / 2
    body = f'<g fill="{INK}">{mark(name, src, "", x, y, size)}</g>'
    return window(body, t0, t1, f"transform:scale(.78) rotate({num(tilt)}deg)", "transform:none", "transform:scale(1.035)",
                  pop=0.2, ease=BACK, origin=f"{num(cx)}px {num(cy)}px")


def ghost(name: str, src: str, x: float, y: float, size: float, t0: float, t1: float, dx: float, rot: float) -> str:
    """The cut's logo, huge and faint, sliding against the foreground."""
    body = f'<g fill="{INK}" fill-opacity=".07">{mark(name, src, "", x, y, size)}</g>'
    cx, cy = x + size / 2, y + size / 2
    return window(body, t0, t1, f"transform:translateX({num(dx)}px) rotate({num(-rot)}deg) scale(1.06)",
                  f"transform:translateX({num(dx * 0.35)}px) rotate({num(-rot * 0.3)}deg)",
                  f"transform:translateX({num(-dx * 0.6)}px) rotate({num(rot)}deg) scale(.98)",
                  pop=0.1, origin=f"{num(cx)}px {num(cy)}px")


# ---------------------------------------------------------------- 8.00 slam -> caption

def slam() -> str:
    size, track, base = CAP_SIZE, CAP_TRACK, CAP_BASE
    sq, gap = 10, 12
    wtxt = width("mono_md", "NOW EXPLORING", size, track)
    x_left = 480 - (sq + gap + wtxt) / 2
    tx = x_left + sq + gap
    cyc = base - size * 0.36                # caption's optical centre line; also the transform origin

    def big(k: float) -> str:               # caption scaled k about its own centre, centred on frame
        return f"transform:translate(0px,{num(CY - cyc)}px) scale({k:.3f})"

    s = 3.5
    # the ACC block is the shot's metronome: it kicks on every cut of the montage
    sy = cyc - sq / 2
    kicks = [(T0 - E, HID + "transform:none"), (T0, VIS + "transform:none")]
    for c in CUTS:
        kicks += [(c - E, VIS + "transform:none"), (c, VIS + "transform:scale(1.8)", EXPO), (c + 0.14, VIS + "transform:none")]
    kicks += [(T1 - E, VIS + "transform:none"), (T1, HID + "transform:none")]
    parts = [anim(f'<rect x="{num(x_left)}" y="{num(sy)}" width="{sq}" height="{sq}" fill="{ACC}"/>', kicks,
                  f"{num(x_left + sq / 2)}px {num(cyc)}px")]
    k = 0
    for lx, _, ch in letters("mono_md", "NOW EXPLORING", size, tx, base, track):
        if ch == " ":
            continue
        t = T0 + 0.015 + k * 0.004
        k += 1
        g = text("mono_md", ch, size, lx, base, "ink")
        parts.append(anim(g, [(t - E, HID + "transform:translateY(-6px)"), (t, VIS + "transform:translateY(-6px)", EXPO),
                              (t + 0.05, VIS + "transform:none"), (T1 - E, VIS + "transform:none"), (T1, HID + "transform:none")]))
    # slam 1.3 -> .96 (the expo tail is the push), rest, whip up to the caption landing on the first cut
    stops = [(T0 - E, HID + big(s * 1.3)), (T0, VIS + big(s * 1.3), EXPO), (T0 + 0.1, VIS + big(s * 0.96), WHIP),
             (CUTS[0], VIS + "transform:none"), (T1 - E, VIS + "transform:none"), (T1, HID + "transform:none")]
    return anim("".join(parts), stops, f"480px {num(cyc)}px")


# ---------------------------------------------------------------- the montage

def cut(i: int) -> str:
    name, src = lib.EXPLORING[i]
    t0, t1 = CUTS[i], CUTS[i + 1]
    LOGO, GAP = 170, 56
    parts, back = [], ""
    if i in (0, 1, 3):                       # side by side
        size = {0: 84, 1: 124, 3: 120}[i]
        wn = width("sans_bk", name, size, -0.035)
        total = LOGO + GAP + wn
        x0 = 480 - total / 2
        logo_left = i != 1
        lx = x0 if logo_left else x0 + wn + GAP
        nx = x0 + LOGO + GAP if logo_left else x0
        base = CY + size * 0.71 / 2
        back = ghost(name, src, 500 if logo_left else -160, CY - 310, 620, t0, t1, dx=-44 if logo_left else 44, rot=4 if logo_left else -4)
        parts.append(logo(name, src, lx, CY - LOGO / 2, LOGO, t0, t1, tilt=-10 if logo_left else 10))
        parts.append(kinetic_name(name, size, nx, base, t0, t1, rise=1 if i != 1 else -1, slot_id=str(i)))
        parts.append(underline(nx, base + 20, wn, t0, t1, from_right=not logo_left))
    else:                                     # stacked, centred as a block on CY
        size, L, gap = 112, 150, 34
        cap = size * 0.71
        top = CY - (L + gap + cap + 26) / 2
        base = top + L + gap + cap
        wn = width("sans_bk", name, size, -0.035)
        back = ghost(name, src, 480 - 380, CY - 380, 760, t0, t1, dx=30, rot=3)
        parts.append(logo(name, src, 480 - L / 2, top, L, t0, t1, tilt=-12))
        parts.append(kinetic_name(name, size, 480, base, t0, t1, rise=1, anchor="middle", slot_id=str(i)))
        parts.append(underline(480 - wn / 2, base + 20, wn, t0, t1))
    return back + flow("".join(parts), t0, t1, dx=30, punch=1.05)


def lineup() -> str:
    """9.40: all four logos in a row, snapping on left to right — then the cut."""
    t0, t1 = CUTS[4], T1
    L, gap = 76, 64
    total = 4 * L + 3 * gap
    x0 = 480 - total / 2
    out = []
    for i, (name, src) in enumerate(lib.EXPLORING):
        x = x0 + i * (L + gap)
        body = f'<g fill="{INK}">{mark(name, src, "", x, CY - L / 2, L)}</g>'
        out.append(window(body, t0, t1, "transform:translateY(14px) scale(1.2)", "transform:none", "transform:scale(1.03)",
                          pop=0.05, delay=i * 0.012, step=True, origin=f"{num(x + L / 2)}px {CY}px"))
    return flow("".join(out), t0, t1, dx=8, punch=1.02)


def build() -> str:
    return slam() + "".join(cut(i) for i in range(4)) + lineup()
