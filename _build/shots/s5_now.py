"""SHOT 05 — NOW EXPLORING (8.0-9.5s).

8.00  an ACC block and NOW EXPLORING type on huge in the middle of frame, then fly up into
      the top-left caption, where they stay for the rest of the shot
8.20  strobe montage of lib.EXPLORING, one tool per 0.30s, hard cuts. Every cut: the frame
      pops 1.06 -> 1 and keeps pushing, the logo springs in, the name's letters rise (or drop)
      out of a slot one by one, an ACC bar wipes under the name, index + category tick in,
      and a giant ghost of the logo slides the other way behind it. Compositions alternate:
      logo|name, name|logo, stacked, logo|name.
9.40  all four logos snap into a row on the beat, then cut
"""

import lib
from lib import ACC, BG, DIM, EXPO, BACK, INK, RULE, SINE, T, W, X0, X1, num, text, letters, width, label, mark

KEY = "s5"
T0, T1 = lib.SHOTS[KEY]
E = 0.004                 # a hard cut: 4ms ramp, below one frame
VIS = "opacity:1;visibility:visible;"
HID = "opacity:0;visibility:hidden;"
CY = 296                  # optical centre of the safe area

CUTS = [8.20, 8.50, 8.80, 9.10, 9.40]
CATEGORY = {"Claude Code": "AGENTIC CODING", "Manus": "GENERAL AI AGENT", "Grok": "AI MODEL · xAI", "Framer": "INTERACTIVE SITES"}


def anim(body: str, stops: list[tuple], origin: str = "") -> str:
    """Reel-clock animation that is hidden at 0 and T (stops are inside the shot)."""
    return lib.at(body, [(0, HID + "transform:none"), *stops, (T, HID + "transform:none")], origin)


def window(body: str, t0: float, t1: float, start: str, settle: str, end: str, pop: float = 0.12,
           ease: str = EXPO, origin: str = "", delay: float = 0.0, step: bool = False) -> str:
    """Hard cut on at t0 (+delay, holding `start` until then; hidden until then if step), animate
    start->settle over `pop`, drift settle->end until t1, hard cut off at t1."""
    a = t0 + delay
    on = a if step else t0
    stops = [(on - E, HID + start), (on, VIS + start)]
    stops.append((a, VIS + start, ease))
    stops += [(a + pop, VIS + settle, "linear"), (t1 - E, VIS + end), (t1, HID + end)]
    assert all(x[0] <= y[0] for x, y in zip(stops, stops[1:])), (t0, t1, delay, pop)
    return anim(body, stops, origin)


def kinetic_name(s: str, size: float, x: float, base: float, t0: float, t1: float, rise: int, stagger: float = 0.011,
                 anchor: str = "start", slot_id: str = "") -> str:
    """Per-letter type that rises (rise=1) or drops (rise=-1) out of a static slot clip."""
    cap = size * 0.71
    travel = (cap + size * 0.18) * rise
    lid = f"{KEY}-slot-{slot_id}"
    lx = letters("sans_bk", s, size, x, base, -0.035, anchor)
    x_lo, x_hi = lx[0][0] - size * 0.2, lx[-1][0] + lx[-1][1] + size * 0.2
    lib.add_def(f'<clipPath id="{lid}"><rect x="{num(x_lo)}" y="{num(base - cap - size * 0.12)}" '
                f'width="{num(x_hi - x_lo)}" height="{num(cap + size * 0.24)}"/></clipPath>')
    out = []
    k = 0
    for lx_, _, ch in lx:
        if ch == " ":
            continue
        g = text("sans_bk", ch, size, lx_, base, "ink")
        out.append(window(g, t0, t1, f"transform:translateY({num(travel)}px)", "transform:none", "transform:none",
                          pop=0.15, delay=0.02 + k * stagger))
        k += 1
    return f'<g clip-path="url(#{lid})">{"".join(out)}</g>'


def underline(x: float, y: float, w: float, t0: float, t1: float, from_right: bool = False) -> str:
    ox = x + w if from_right else x
    bar = f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="6" fill="{ACC}"/>'
    return window(bar, t0, t1, "transform:scaleX(0)", "transform:scaleX(1)", "transform:scaleX(1)",
                  pop=0.2, delay=0.05, origin=f"{num(ox)}px {num(y + 3)}px")


def tag(i: int, name: str, x: float, y: float, t0: float, t1: float, anchor: str = "start") -> str:
    """'01 — 04  CATEGORY' mono index, ACC number."""
    idx, rest, cat = f"{i + 1:02d}", " — 04", CATEGORY[name]
    w_idx = width("mono_md", idx, 11, 0.16) + 11 * 0.16
    w_rest = width("mono_md", rest, 11, 0.16) + 11 * 0.16
    w_cat = width("mono", cat, 11, 0.16)
    total = w_idx + w_rest + 18 + w_cat
    x0 = {"start": x, "middle": x - total / 2, "end": x - total}[anchor]
    body = (text("mono_md", idx, 11, x0, y, "acc", 0.16) + text("mono_md", rest, 11, x0 + w_idx, y, "dim", 0.16)
            + text("mono", cat, 11, x0 + w_idx + w_rest + 18, y, "sub", 0.16))
    return window(body, t0, t1, "transform:translateY(8px)", "transform:none", "transform:none", pop=0.14, delay=0.04)


def logo(name: str, src: str, x: float, y: float, size: float, t0: float, t1: float, tilt: float) -> str:
    cx, cy = x + size / 2, y + size / 2
    body = f'<g fill="{INK}">{mark(name, src, "", x, y, size)}</g>'
    return window(body, t0, t1, f"transform:scale(.78) rotate({num(tilt)}deg)", "transform:none", "transform:scale(1.035)",
                  pop=0.2, ease=BACK, origin=f"{num(cx)}px {num(cy)}px")


def ghost(name: str, src: str, x: float, y: float, size: float, t0: float, t1: float, dx: float, rot: float) -> str:
    body = f'<g fill="{INK}" fill-opacity=".045">{mark(name, src, "", x, y, size)}</g>'
    cx, cy = x + size / 2, y + size / 2
    return window(body, t0, t1, f"transform:translateX({num(dx)}px) rotate({num(-rot)}deg) scale(1.06)",
                  f"transform:translateX({num(dx * 0.35)}px) rotate({num(-rot * 0.3)}deg)",
                  f"transform:translateX({num(-dx * 0.6)}px) rotate({num(rot)}deg) scale(.98)",
                  pop=0.1, origin=f"{num(cx)}px {num(cy)}px")


def frame_push(body: str, t0: float, t1: float, drift: float) -> str:
    """The cut's camera: pop 1.06 -> 1, then keep pushing in and sliding."""
    return window(body, t0, t1, "transform:scale(1.06)", "transform:none",
                  f"transform:translateX({num(drift)}px) scale(1.025)", pop=0.12, origin=f"480px {CY}px")


# ---------------------------------------------------------------- 8.00 slam -> caption

def slam() -> str:
    size, track = 11, 0.16
    sq, gap = 7, 9
    base = 96
    tx = X0 + sq + gap
    wtot = sq + gap + width("mono_md", "NOW EXPLORING", size, track)
    ox, oy = X0, base                       # transform origin: caption's left baseline
    cyc = base - size * 0.36                # caption's optical centre line

    def big(k: float) -> str:               # caption scaled k about its own centre, centred on frame
        a = 480 - ox - k * wtot / 2
        b = CY - oy - k * (cyc - oy)
        return f"transform:translate({num(a)}px,{num(b)}px) scale({k:.3f})"

    s = 4.9
    # the ACC block is the shot's metronome: it kicks on every cut of the montage
    sy = base - sq - 0.6
    kicks = [(T0 - E, HID + "transform:none"), (T0, VIS + "transform:none")]
    for c in CUTS:
        kicks += [(c - E, VIS + "transform:none"), (c, VIS + "transform:scale(1.9)", EXPO), (c + 0.14, VIS + "transform:none")]
    kicks += [(T1 - E, VIS + "transform:none"), (T1, HID + "transform:none")]
    parts = [anim(f'<rect x="{X0}" y="{num(sy)}" width="{sq}" height="{sq}" fill="{ACC}"/>', kicks,
                  f"{num(X0 + sq / 2)}px {num(sy + sq / 2)}px")]
    for i, (lx, _, ch) in enumerate(letters("mono_md", "NOW EXPLORING", size, tx, base, track)):
        if ch == " ":
            continue
        t = T0 + 0.02 + i * 0.0055
        g = text("mono_md", ch, size, lx, base, "ink")
        parts.append(anim(g, [(t - E, HID + "transform:translateY(-5px)"), (t, VIS + "transform:translateY(-5px)", EXPO),
                              (t + 0.05, VIS + "transform:none"), (T1 - E, VIS + "transform:none"), (T1, HID + "transform:none")]))
    stops = [(T0 - E, HID + big(s * 1.35)), (T0, VIS + big(s * 1.35), EXPO), (T0 + 0.08, VIS + big(s), "linear"),
             (T0 + 0.14, VIS + big(s * 0.965), EXPO), (T0 + 0.225, VIS + "transform:none"),
             (T1 - E, VIS + "transform:none"), (T1, HID + "transform:none")]
    caption = anim("".join(parts), stops, f"{ox}px {oy}px")

    # impact rules either side of the big word, there only while it is big
    rules = []
    for side in (-1, 1):
        x = 480 + side * (s * wtot / 2 + 22)
        d = f"M{num(x)} {CY}H{num(x + side * 140)}"
        rules.append(window(f'<path d="{d}" stroke="{INK}" stroke-width="1.2" fill="none"/>', T0, T0 + 0.14,
                            "transform:scaleX(0)", "transform:scaleX(1)", f"transform:translateX({side * 14}px) scaleX(1)",
                            pop=0.08, delay=0.02, origin=f"{num(x)}px {CY}px"))
    return caption + "".join(rules)


def progress() -> str:
    """Four segments top-right: the live one fills in ACC across its cut, then turns INK."""
    n, sw, gap, y = 4, 34, 6, 92
    x0 = X1 - n * sw - (n - 1) * gap
    out = []
    for i in range(n):
        x = x0 + i * (sw + gap)
        a, b = CUTS[i], CUTS[i + 1]
        base = f'<rect x="{x}" y="{y}" width="{sw}" height="3" fill="{RULE}"/>'
        out.append(anim(base, [(T0 + 0.18 - E, HID + "transform:none"), (T0 + 0.18, VIS + "transform:none"),
                               (T1 - E, VIS + "transform:none"), (T1, HID + "transform:none")]))
        fill = f'<rect x="{x}" y="{y}" width="{sw}" height="3" fill="{ACC}"/>'
        out.append(anim(fill, [(a - E, HID + "transform:scaleX(0)"), (a, VIS + "transform:scaleX(.08)", "linear"),
                               (b - E, VIS + "transform:scaleX(1)"), (b, HID + "transform:scaleX(1)")], f"{x}px {y}px"))
        done = f'<rect x="{x}" y="{y}" width="{sw}" height="3" fill="{INK}"/>'
        out.append(anim(done, [(b - E, HID + "transform:none"), (b, VIS + "transform:none"),
                               (T1 - E, VIS + "transform:none"), (T1, HID + "transform:none")]))
    return "".join(out)


# ---------------------------------------------------------------- the montage

def cut(i: int) -> str:
    name, src = lib.EXPLORING[i]
    t0, t1 = CUTS[i], CUTS[i + 1]
    LOGO, GAP = 170, 56
    parts = []
    if i in (0, 1, 3):                       # side by side
        size = {0: 84, 1: 124, 3: 120}[i]
        wn = width("sans_bk", name, size, -0.035)
        total = LOGO + GAP + wn
        x0 = 480 - total / 2
        logo_left = i != 1
        lx = x0 if logo_left else x0 + wn + GAP
        nx = x0 + LOGO + GAP if logo_left else x0
        base = CY + size * 0.71 / 2
        gx = 520 if logo_left else -150      # ghost on the far side from the logo
        parts.append(ghost(name, src, gx, CY - 300, 600, t0, t1, dx=-44 if logo_left else 44, rot=4 if logo_left else -4))
        parts.append(logo(name, src, lx, CY - LOGO / 2, LOGO, t0, t1, tilt=-10 if logo_left else 10))
        parts.append(kinetic_name(name, size, nx, base, t0, t1, rise=1 if i != 1 else -1, slot_id=str(i)))
        parts.append(underline(nx, base + 20, wn, t0, t1, from_right=not logo_left))
        parts.append(tag(i, name, nx, base - size * 0.71 - 30, t0, t1))
        drift = 10 if logo_left else -10
    else:                                     # stacked, centred
        size, L = 112, 150
        top = CY - 168
        base = top + L + 34 + size * 0.71
        wn = width("sans_bk", name, size, -0.035)
        parts.append(ghost(name, src, 480 - 380, CY - 380, 760, t0, t1, dx=30, rot=3))
        parts.append(logo(name, src, 480 - L / 2, top, L, t0, t1, tilt=-12))
        parts.append(kinetic_name(name, size, 480, base, t0, t1, rise=1, anchor="middle", slot_id=str(i)))
        parts.append(underline(480 - wn / 2, base + 20, wn, t0, t1))
        parts.append(tag(i, name, 480, base + 56, t0, t1, "middle"))
        drift = 0
    return frame_push("".join(parts), t0, t1, drift)


def lineup() -> str:
    """9.40: all four, small, in a row — then the cut."""
    t0, t1 = CUTS[4], T1
    L, gap = 64, 52
    total = 4 * L + 3 * gap
    x0 = 480 - total / 2
    out = []
    for i, (name, src) in enumerate(lib.EXPLORING):
        x = x0 + i * (L + gap)
        body = f'<g fill="{INK}">{mark(name, src, "", x, CY - L / 2 - 8, L)}</g>' + label(name.upper(), x + L / 2, CY + L / 2 + 22, "sub", "middle", 9)
        out.append(window(body, t0, t1, "transform:translateY(18px) scale(1.25)", "transform:none", "transform:scale(1.03)",
                          pop=0.045, delay=i * 0.012, step=True, origin=f"{num(x + L / 2)}px {CY}px"))
    return "".join(out)


def build() -> str:
    return slam() + progress() + "".join(cut(i) for i in range(4)) + lineup()
