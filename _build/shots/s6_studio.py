"""SHOT 06 — STUDIO. A fast flyover of the wireframe valley; the CYTE LAB lockup stands in the
sky above the horizon and is cut together on the beat. The terrain stays below the horizon
band, so no line ever reaches the type.

    9.50  CUT into the flight: the camera is already rushing forward and pushes in.
    9.60  The mark slams in (1.8 -> 1, overshoot); a faint horizon line shoots out from the centre.
    9.75  "CYTE LAB" rises letter by letter through a slot.
    9.875 "CREATIVE TECH STUDIO" types on behind an accent cursor.
   10.00  The three focus words hit on 8ths (10.00, 10.25, 10.50), each rising through a slot,
          each with a step of the camera push.
   10.50  Hold: the world keeps flying, the lockup drifts toward camera.
   11.00  Exit: the small lines wipe up out of their slots, the mark and name launch up and toward
          camera while the camera dives into the valley; hard cut at 11.30.
"""


import lib
from lib import BG, EASE_IN, EXPO, BACK, INK, SINE, T, W, H, at, cyte, num, off, text

K = "s6"
T0, T1 = lib.SHOTS[K]          # 9.5, 11.3
CX = W / 2
HOR = 368                      # terrain horizon / vanishing point height (low: the sky holds the type)
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


# ---------------------------------------------------------------- lockup geometry

MARK_H = 76
MARK_TOP = 92
NAME_Y = 240                   # "CYTE LAB" baseline (cap top ~200)
LABEL_Y = 272                  # "CREATIVE TECH STUDIO" baseline
FOC_Y = 303                    # focus line baseline; lowest glyph ~307, 45+ px above any ridge
HITS = (10.0, 10.25, 10.5)


# ---------------------------------------------------------------- world

def world() -> str:
    lib.add_def(f'<linearGradient id="{K}-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/>'
                f'<stop offset=".5" stop-color="{BG}" stop-opacity=".85"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>')
    lib.add_def(f'<linearGradient id="{K}-floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="{BG}" stop-opacity=".55"/></linearGradient>')
    lib.add_def(f'<radialGradient id="{K}-vig" cx=".5" cy=".5" r=".72"><stop offset=".55" stop-color="{BG}" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="{BG}" stop-opacity=".9"/></radialGradient>')

    # a faster flight than the default (2 s per tile, six per loop) and a calmer grid
    land = lib.terrain(prefix=f"{K}t", period=2.0, hor=HOR, rows=26, cols=21)
    # depth haze on the horizon rides with the camera (wider than the frame so the roll never shows its ends)
    land += f'<rect x="-120" y="{HOR - 60}" width="{W + 240}" height="120" fill="url(#{K}-haze)"/>'
    # the horizon line: shoots out from the vanishing point on the slam, then rests low
    line = f'<path d="M{CX - 480} {HOR}.5H{CX + 480}" stroke="{INK}" stroke-opacity=".35" stroke-width="1"/>'
    land += kf([(9.6, shown("opacity:1;transform:scaleX(0)"), EXPO), (9.9, shown("opacity:1;transform:scaleX(1)"), SINE),
                (10.4, shown("opacity:.4;transform:scaleX(1)")), (T1 - E, shown("opacity:.4;transform:scaleX(1)"))],
               f"{CX}px {HOR}px", line)
    o = f"{CX}px {HOR}px"
    # the camera: already flying on the cut, a push that steps forward on each focus hit,
    # then an accelerating dive into the valley for the exit
    def c(scale: float, dy: float = 0) -> str:
        return shown(f"transform:translateY({num(dy)}px) scale({scale:.2f})")
    cam = [(T0, c(.95), EXPO), (9.9, c(1))]
    for i, h in enumerate(HITS):
        cam += [(h, c(1 + .03 * i), EXPO), (h + .25, c(1.03 + .03 * i))]
    # the dive tilts the world up as well; the type launches up faster, so the gap only grows
    cam += [(10.75, c(1.09), SINE), (11.0, c(1.1), EASE_IN), (T1 - E, c(1.7, -60))]
    land = kf(cam, o, land)
    # roll: a slow lean across the shot
    land = kf([(T0, shown("transform:rotate(-.7deg)"), SINE), (T1 - E, shown("transform:rotate(.8deg)"))], o, land)

    veils = (f'<rect y="500" width="{W}" height="{H - 500}" fill="url(#{K}-floor)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#{K}-vig)"/>')
    return land + veils


# ---------------------------------------------------------------- lockup

def the_mark() -> str:
    mw = 189 / 204 * MARK_H
    body = cyte(CX - mw / 2, MARK_TOP, MARK_H, INK)
    o = f"{CX}px {MARK_TOP + MARK_H / 2}px"
    return kf([(9.6, shown("transform:scale(1.8)"), BACK), (9.92, shown("transform:none")), (T1 - E, shown("transform:none"))], o, body)


def wordmark() -> str:
    size = 56
    lib.add_def(f'<clipPath id="{K}-slot"><rect x="40" y="{NAME_Y - 52}" width="{W - 80}" height="64"/></clipPath>')
    out = []
    i = 0
    for x, adv, ch in lib.letters("sans_bk", "CYTE LAB", size, CX, NAME_Y, 0.01, "middle"):
        if ch == " ":
            continue
        tin = 9.75 + i * 0.03
        out.append(kf([(tin, shown("transform:translateY(62px)"), EXPO), (tin + .38, shown("transform:none")),
                       (T1 - E, shown("transform:none"))], body=text("sans_bk", ch, size, x, NAME_Y, "name")))
        i += 1
    return f'<g clip-path="url(#{K}-slot)">{"".join(out)}</g>'


def studio_label() -> str:
    s, size, tr, face = lib.STUDIO[1], 12, 0.3, "mono_md"
    w = lib.width(face, s, size, tr)
    t_start, step = 9.875, 0.012
    chars = lib.letters(face, s, size, CX, LABEL_Y, tr, "middle")
    out = []
    for i, (x, adv, ch) in enumerate(chars):
        if ch != " ":
            out.append(kf([(t_start + i * step, shown()), (T1 - E, shown())], body=text(face, ch, size, x, LABEL_Y, "sub")))
    lib.add_def(f'<clipPath id="{K}-lslot"><rect x="40" y="{LABEL_Y - 16}" width="{W - 80}" height="22"/></clipPath>')
    body = kf([(t_start, shown("transform:none")), (11.03, shown("transform:none"), EASE_IN),
               (11.13, shown("transform:translateY(-20px)"))], body="".join(out))
    return f'<g clip-path="url(#{K}-lslot)">{body}</g>'


def focus_line() -> str:
    """'Virtual production · Digital creation · Indie games', one phrase per 8th, each rising through a slot."""
    face, size = "sans_md", 15
    words = [wd.capitalize() for wd in lib.STUDIO[2]]
    sep = "  ·  "
    full = sep.join(words)
    x = CX - lib.width(face, full, size) / 2
    out = []
    for i, (wd, hit) in enumerate(zip(words, HITS)):
        part = ""
        if i:
            part += text(face, sep, size, x, FOC_Y, "dim")
            x += lib.width(face, sep, size)
        part += text(face, wd, size, x, FOC_Y, "ink")
        x += lib.width(face, wd, size)
        out.append(kf([(hit, shown("transform:translateY(22px)"), EXPO), (hit + .3, shown("transform:none")),
                       (T1 - E, shown("transform:none"))], body=part))
    lib.add_def(f'<clipPath id="{K}-fslot"><rect x="40" y="{FOC_Y - 18}" width="{W - 80}" height="25"/></clipPath>')
    body = kf([(HITS[0], shown("transform:none")), (11.0, shown("transform:none"), EASE_IN),
               (11.1, shown("transform:translateY(-24px)"))], body="".join(out))
    return f'<g clip-path="url(#{K}-fslot)">{body}</g>'


def build() -> str:
    # mark + name: a slow drift toward camera through the hold, then they launch up and past the
    # camera (scaled about the name's baseline, so nothing ever moves down toward the terrain)
    hero = kf([(9.6, shown("transform:translateY(0px) scale(1)"), SINE),
               (11.0, shown("transform:translateY(0px) scale(1.025)"), EASE_IN),
               (T1 - E, shown("transform:translateY(-130px) scale(3.2)"))],
              f"{CX}px {NAME_Y}px", the_mark() + wordmark())
    body = world() + hero + studio_label() + focus_line()
    # master window: hard cuts on both edges
    return at(body, [(0, off()), (T0 - E, off()), (T0, shown()), (T1 - E, shown()), (T1, off()), (T, off())])
