"""SHOT 06 — STUDIO. The wireframe valley at full frame; the CYTE LAB mark rises at the
vanishing point like a sun and the studio lockup is cut together on the beat.

    9.50  CUT. World cuts in dim; focus brackets snap from the frame onto the vanishing point.
    9.60  The mark slams in (1.8 -> 1, overshoot); the world flares, the horizon ignites.
    9.75  "CYTE LAB" rises letter by letter through a slot.
    9.875 "CREATIVE TECH STUDIO" types on behind an accent cursor; rules draw out.
   10.00  Brackets open out to frame the lockup. Focus tags hit on 8ths: 10.00, 10.25, 10.50,
          each with an accent flash, a glow pulse and a bump of the mark.
   10.50  One full beat of hold: push-in, drift, breathing brackets, a glint runs through the letters.
   11.00  Exit: tags/label snap away, letters leave upward, the camera dollies through the
          mark, white flash, hard cut at 11.30.
"""


import lib
from lib import ACC, BACK, BG, DIM, EASE_IN, EXPO, INK, SINE, T, W, H, at, cyte, num, off, text

K = "s6"
T0, T1 = lib.SHOTS[K]          # 9.5, 11.3
CX = W / 2
HOR = 252                      # terrain horizon / vanishing point height
ON = "opacity:1;visibility:visible"
E = 0.004                      # "instant" gap between two stops


def shown(css: str = "transform:none") -> str:
    return f"{ON};{css}"


def kf(stops: list[tuple], origin: str = "", body: str = "") -> str:
    """Reel-clock animation that is hidden before the first and after the last given stop."""
    first, last = stops[0], stops[-1]
    st = [(0, off(_tf(first[1]))), (max(0, first[0] - E), off(_tf(first[1])))] + list(stops)
    st += [(min(T, last[0] + E), off(_tf(last[1]))), (T, off(_tf(last[1])))]
    return at(body, st, origin)


def _tf(css: str) -> str:
    for part in css.split(";"):
        if part.strip().startswith("transform:"):
            return part.strip()
    return "transform:none"


# ---------------------------------------------------------------- world

def world() -> str:
    lib.add_def(f'<radialGradient id="{K}-sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{ACC}" stop-opacity=".62"/>'
                f'<stop offset=".4" stop-color="{ACC}" stop-opacity=".16"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>')
    lib.add_def(f'<linearGradient id="{K}-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/>'
                f'<stop offset=".5" stop-color="{BG}" stop-opacity=".88"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>')
    lib.add_def(f'<linearGradient id="{K}-top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/>'
                f'<stop offset=".45" stop-color="{BG}" stop-opacity=".7"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>')
    lib.add_def(f'<linearGradient id="{K}-floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/>'
                f'<stop offset=".6" stop-color="{BG}" stop-opacity=".9"/><stop offset="1" stop-color="{BG}"/></linearGradient>')
    lib.add_def(f'<radialGradient id="{K}-vig" cx=".5" cy=".48" r=".72"><stop offset=".55" stop-color="{BG}" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="{BG}" stop-opacity=".9"/></radialGradient>')
    lib.add_def(f'<radialGradient id="{K}-scrim" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{BG}" stop-opacity=".9"/>'
                f'<stop offset=".62" stop-color="{BG}" stop-opacity=".66"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>')

    land = lib.terrain(prefix=f"{K}t", period=4.0, hor=HOR)
    o = f"{CX}px {HOR}px"
    # the camera: dim on the cut, a kick on the slam, slow push-in, then a dolly through the mark
    cam = kf([
        (T0, shown("opacity:.38;transform:scale(1.1)"), EXPO),
        (9.6 - E, shown("opacity:.5;transform:scale(1.02)")),
        (9.6, shown("opacity:1;transform:scale(1.075)"), EXPO),
        (9.95, shown("opacity:.92;transform:scale(1.03)"), SINE),
        (11.0, shown("opacity:.92;transform:scale(1.1)"), EASE_IN),
        (T1, shown("opacity:1;transform:scale(1.55)")),
    ], o, land)
    # roll: a slow handheld lean across the shot
    cam = kf([(T0, shown("transform:rotate(-.8deg)"), SINE), (T1, shown("transform:rotate(.9deg)"))], o, cam)

    # sun glow behind the mark: flares on the slam, pulses on every tag hit
    pulses = [(T0, shown("opacity:0;transform:scale(.6)")), (9.6 - E, shown("opacity:0;transform:scale(.6)")),
              (9.6, shown("opacity:1;transform:scale(1.25)"), EXPO), (9.95, shown("opacity:.55;transform:scale(1)"))]
    for tb in (10.0, 10.25, 10.5):
        pulses += [(tb - E, shown("opacity:.55;transform:scale(1)")), (tb, shown("opacity:.95;transform:scale(1.12)"), EXPO),
                   (tb + .22, shown("opacity:.55;transform:scale(1)"))]
    pulses += [(11.0, shown("opacity:.6;transform:scale(1.04)"), EASE_IN), (T1, shown("opacity:1;transform:scale(1.8)"))]
    sun = kf(pulses, f"{CX}px {HOR}px", f'<ellipse cx="{CX}" cy="{HOR}" rx="430" ry="86" fill="url(#{K}-sun)"/>')

    # horizon ignition: a hot line shoots out from the vanishing point on the slam
    line = (f'<path d="M{CX - 470} {HOR}.5H{CX + 470}" stroke="{ACC}" stroke-width="1.2"/>'
            f'<path d="M{CX - 160} {HOR}.5H{CX + 160}" stroke="#FFD2BF" stroke-width="1"/>')
    ignite = kf([(9.6, shown("opacity:1;transform:scaleX(0)"), EXPO), (9.85, shown("opacity:.9;transform:scaleX(1)"), SINE),
                 (10.4, shown("opacity:.16;transform:scaleX(1)")), (11.0, shown("opacity:.16;transform:scaleX(1)"), EASE_IN),
                 (11.15, shown("opacity:0;transform:scaleX(1.3)"))], f"{CX}px {HOR}px", line)

    veils = (f'<rect y="{HOR - 70}" width="{W}" height="140" fill="url(#{K}-haze)"/>'
             f'<rect width="{W}" height="110" fill="url(#{K}-top)"/>'
             f'<rect y="440" width="{W}" height="{H - 440}" fill="url(#{K}-floor)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#{K}-vig)"/>'
             f'<ellipse cx="{CX}" cy="352" rx="400" ry="122" fill="url(#{K}-scrim)"/>')
    return cam + sun + veils + ignite


# ---------------------------------------------------------------- focus brackets

def brackets() -> str:
    """Four corner brackets: lock onto the vanishing point, open out to the lockup, breathe, fly off."""
    arm = 14
    wide = (96, 92, 864, 512)          # just inside the HUD brackets
    tight = (424, 146, 536, 276)       # around the mark
    lock = (214, 128, 746, 448)        # around the whole lockup
    out = []
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        def p(box, grow=0.0):
            x0, y0, x1, y1 = box
            x = (x0 if sx < 0 else x1) + sx * grow
            y = (y0 if sy < 0 else y1) + sy * grow
            return f"transform:translate({num(x)}px,{num(y)}px)"
        d = f"M0 {-sy * arm}V0H{-sx * arm}"
        body = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.4" stroke-opacity=".85"/>'
        out.append(kf([
            (T0, shown(p(wide)), EXPO),
            (9.6, shown(p(tight))),
            (9.6 + E, shown(p(tight, -4)), BACK),   # the slam squeezes the lock
            (9.8, shown(p(tight))),
            (10.0, shown(p(tight)), EXPO),
            (10.35, shown(p(lock)), SINE),
            (11.0, shown(p(lock, 6)), EASE_IN),
            (11.2, f"opacity:0;visibility:visible;{p(wide, 40)}"),
        ], body=body))
    # an accent cross on the vanishing point, only while locking on
    cross = f'<path d="M{CX - 6} {HOR}.5H{CX + 6}M{CX}.5 {HOR - 6}V{HOR + 6}" stroke="{ACC}" stroke-width="1.2"/>'
    out.append(kf([(T0, shown("transform:scale(2.4)"), EXPO), (9.58, shown("transform:scale(1)"))], f"{CX}px {HOR}px", cross))
    return "".join(out)


# ---------------------------------------------------------------- lockup

MARK_H = 92
MARK_TOP = HOR - MARK_H + 2           # the mark stands on the horizon
NAME_Y = 330                          # "CYTE LAB" baseline
LABEL_Y = 366
TAG_Y = 390                           # tag top
TAG_H = 24
TAG_HITS = (10.0, 10.25, 10.5)
X0c = 40                              # slot clip inset


def bump_stops(base0: float, base1: float, t0: float, t1: float, hits, amp: float, ease_end=None):
    """Scale keyframes drifting base0 -> base1 over t0..t1 with a quick bump at each hit."""
    def base(t):
        return base0 + (base1 - base0) * (t - t0) / (t1 - t0)
    st = [(t0, shown(f"transform:scale({base0:.4f})"))]
    for h in hits:
        st += [(h - E, shown(f"transform:scale({base(h):.4f})")),
               (h, shown(f"transform:scale({base(h) * amp:.4f})"), EXPO),
               (h + .2, shown(f"transform:scale({base(h + .2):.4f})"))]
    st.append((t1, shown(f"transform:scale({base1:.4f})"), ease_end) if ease_end else (t1, shown(f"transform:scale({base1:.4f})")))
    return st


def the_mark() -> str:
    mw = 189 / 204 * MARK_H
    body = cyte(CX - mw / 2, MARK_TOP, MARK_H, INK)
    o = f"{CX}px {MARK_TOP + MARK_H / 2}px"
    slam = kf([
        (9.6, shown("transform:scale(1.8)"), BACK),
        (9.92, shown("transform:none")),
        (11.06, shown("transform:none"), EASE_IN),
        (11.27, "opacity:0;visibility:visible;transform:scale(5)"),
    ], o, body)
    # rhythmic bumps on the tag hits, riding a slow grow
    st = bump_stops(1, 1.035, 9.92, 11.0, TAG_HITS, 1.045)
    return kf([(9.6, shown())] + st + [(T1 - E, shown("transform:scale(1.035)"))], o, slam)


def shockwave() -> str:
    """A thin ring that rips out of the mark on impact."""
    cy = MARK_TOP + MARK_H / 2
    ring = f'<circle cx="{CX}" cy="{num(cy)}" r="60" fill="none" stroke="{INK}" stroke-width="1.2"/>'
    return kf([(9.66, shown("opacity:.7;transform:scale(.7)"), EXPO), (10.05, "opacity:0;visibility:visible;transform:scale(2.6)")],
              f"{CX}px {num(cy)}px", ring)


def wordmark() -> str:
    size = 56
    lib.add_def(f'<clipPath id="{K}-slot"><rect x="{X0c}" y="{NAME_Y - 52}" width="{W - 2 * X0c}" height="68"/></clipPath>')
    out = []
    i = 0
    for x, adv, ch in lib.letters("sans_bk", "CYTE LAB", size, CX, NAME_Y, 0.01, "middle"):
        if ch == " ":
            continue
        glyph = text("sans_bk", ch, size, x, NAME_Y, "name")
        # a glint that runs through the resting letters during the hold, left to right
        tg = 10.56 + i * 0.045
        glyph += kf([(tg, shown("opacity:0"), EXPO), (tg + .07, shown("opacity:.95"), SINE), (tg + .34, shown("opacity:0"))],
                    body=text("sans_bk", ch, size, x, NAME_Y, "", 0).replace("<g class=\"\"", '<g fill="#fff"'))
        tin = 9.75 + i * 0.035
        tout = 11.02 + i * 0.013
        out.append(kf([
            (tin, shown("transform:translateY(64px)"), EXPO),
            (tin + .42, shown("transform:none")),
            (tout, shown("transform:none"), EASE_IN),
            (tout + .12, shown("transform:translateY(-62px)")),
        ], body=glyph))
        i += 1
    return f'<g clip-path="url(#{K}-slot)">{"".join(out)}</g>'



def studio_label() -> str:
    s, size, tr = lib.STUDIO[1], 11, 0.3
    face = "mono_md"
    w = lib.width(face, s, size, tr)
    t_start, step = 9.875, 0.012
    out = []
    chars = lib.letters(face, s, size, CX, LABEL_Y, tr, "middle")
    n = len(chars)
    for i, (x, adv, ch) in enumerate(chars):
        if ch == " ":
            continue
        t = t_start + i * step
        out.append(kf([(t, shown()), (11.02 + (n - i) * 0.004, shown())], body=text(face, ch, size, x, LABEL_Y, "sub")))
    # the cursor that types it on
    x_start = CX - w / 2
    cur = f'<rect x="{num(x_start)}" y="{LABEL_Y - 9}" width="7" height="11" fill="{ACC}"/>'
    t_end = t_start + n * step
    out.append(kf([
        (t_start, shown("transform:none"), "linear"),
        (t_end, shown(f"transform:translateX({num(w + 4)}px)")),
        (t_end + .08, f"opacity:0;visibility:visible;transform:translateX({num(w + 4)}px)", "steps(1)"),
        (t_end + .16, shown(f"transform:translateX({num(w + 4)}px)"), "steps(1)"),
        (t_end + .24, f"opacity:0;visibility:visible;transform:translateX({num(w + 4)}px)"),
    ], body=cur))
    # flanking rules draw outward from the label
    gap, run = 18, 56
    for side in (-1, 1):
        x_in = CX + side * (w / 2 + gap)
        x_out = x_in + side * run
        rule = f'<path d="M{num(x_in)} {LABEL_Y - 4}.5H{num(x_out)}" stroke="{DIM}" stroke-width="1"/>'
        out.append(kf([
            (9.9, shown("transform:scaleX(0)"), EXPO),
            (10.3, shown("transform:none")),
            (11.0, shown("transform:none"), EASE_IN),
            (11.14, shown("transform:scaleX(0)")),
        ], f"{num(x_in)}px {LABEL_Y - 4}px", rule))
    return "".join(out)


def tags() -> str:
    face, size, tr = "mono_md", 10, 0.16
    pad, gap_in, gap = 12, 8, 10
    words = lib.STUDIO[2]
    iw = lib.width(face, "00", size, tr)
    widths = [pad + iw + gap_in + lib.width(face, wd, size, tr) + pad for wd in words]
    x = CX - (sum(widths) + gap * (len(words) - 1)) / 2
    out = []
    for i, (wd, tw, hit) in enumerate(zip(words, widths, TAG_HITS)):
        base = TAG_Y + TAG_H / 2 + 3.6
        box = (f'<rect x="{num(x + .5)}" y="{TAG_Y + .5}" width="{num(tw - 1)}" height="{TAG_H - 1}" rx="3" '
               f'fill="{BG}" fill-opacity=".82" stroke="{INK}" stroke-opacity=".28"/>')
        flash = kf([(hit, shown("opacity:1"), EXPO), (hit + .3, "opacity:0;visibility:visible")],
                   body=f'<rect x="{num(x)}" y="{TAG_Y}" width="{num(tw)}" height="{TAG_H}" rx="3" fill="{ACC}"/>')
        idx = text(face, f"{i + 1:02d}", size, x + pad, base, "acc", tr)
        word = text(face, wd, size, x + pad + iw + gap_in, base, "ink", tr)
        # index reads accent normally; during the flash it would vanish, so it sits above in ink-on-accent order
        body = box + flash + idx + word
        o = f"{num(x + tw / 2)}px {TAG_Y + TAG_H / 2}px"
        t_out = 11.0 + (len(words) - 1 - i) * 0.03
        out.append(kf([
            (hit, shown("transform:translateY(10px) scale(.86)"), BACK),
            (hit + .32, shown("transform:none"), SINE),
            (t_out, shown("transform:translateY(-1px)"), EASE_IN),
            (t_out + .12, "opacity:0;visibility:visible;transform:translateY(-1px) scaleY(.1)"),
        ], o, body))
        x += tw + gap
    return "".join(out)


# ---------------------------------------------------------------- exit flash

def flash() -> str:
    return kf([(11.19, shown("opacity:0"), EASE_IN), (11.245, shown("opacity:.55"), EXPO), (T1 - E, shown("opacity:.04"))],
              body=f'<rect width="{W}" height="{H}" fill="#fff"/>')


def build() -> str:
    lockup = the_mark() + shockwave() + wordmark() + studio_label() + tags()
    # the whole lockup drifts toward camera through the hold
    lockup = kf([(9.6, shown("transform:none"), SINE), (11.0, shown("transform:scale(1.025)")), (T1 - E, shown("transform:scale(1.025)"))],
                f"{CX}px 300px", lockup)
    body = world() + brackets() + lockup + flash()
    # master window: hard cuts on both edges
    return at(body, [(0, off()), (T0 - E, off()), (T0, shown()), (T1 - E, shown()), (T1, off()), (T, off())])
