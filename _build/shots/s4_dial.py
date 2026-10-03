"""SHOT 04 — THE DIAL (5.5 → 7.5). A precision selector: a knurled satin-metal bezel, a 270°
scale and a needle that snaps through the six tool groups on 8ths. The light on the metal is
fixed; only the knurl turns under it, so the bezel reads as a solid machined ring.

5.50  Hard cut. The bezel lands from the camera (1.3 -> 1) while its knurl spins in; the scale
      sweeps in clockwise from the zero stop, five ticks per frame, each group stamping in from
      outside; the needle and hub drop onto the dial at zero.
5.75  The needle snaps to DESIGN, then MOTION, 3D, AI, CODE, SHIP on every 8th (6.00 … 7.00):
      a fast detent travel, overshoot and a damped settle. The knurled bezel turns with it (it is
      the knob), the inner dot ring counter-rotates a little for parallax, the selected detent
      lights up. On the right a counter drum rolls to the group name and its tool count with
      the same spring, so the needle selects what is shown.
7.25  The needle whips back to zero and bounces off the stop; the drums roll out to blank;
      the dial pushes into the camera. Hard cut at 7.50.
"""

import math

import lib
from lib import BACK, EASE_IN, EXPO, INK, SINE, SUB, T, at, num, off, text

K = "s4"
T0, T1 = lib.SHOTS[K]                 # 5.5, 7.5
E = 0.004                             # a hard cut: below one frame
ON = "opacity:1;visibility:visible"

CX, CY = 300, 300                     # dial centre (21:9 band is y 94..506)
R_BEZ_OUT, R_BEZ_IN, R_LIP = 152, 138, 133
R_TICK_OUT, R_FINE_IN, R_DET_IN = 125, 119, 111
R_DOTS = 93
R_NEEDLE = 106

ZERO = -135.0                         # the stop; the scale runs -135 .. +135
DET = [-112.5 + 45 * k for k in range(6)]
SNAPS = [5.75 + 0.25 * k for k in range(6)]
OUT = 7.25                            # needle whips home
PUSH = 7.31                           # dial pushes into the camera

TRAVEL = "cubic-bezier(.45,0,.2,1)"   # detent travel: rest -> turnaround

RX = 520                              # readout left edge
NAME_SIZE, NAME_B, NAME_P = 96, 312, 110   # name drum: size, baseline, row pitch
CNT_SIZE, CNT_B, CNT_P = 24, 360, 48      # count drum

CODE = {"VS Code", "Xcode", "GitHub", "Git"}  # same split as the card: Ship = Linear, Notion, Webflow, Firebase, Replit


def groups() -> list[tuple[str, int]]:
    s = dict(lib.STACK)
    build = s["BUILD"]
    return [("Design", len(s["DESIGN"])), ("Motion", len(s["MOTION"])), ("3D", len(s["3D"])), ("AI", len(s["AI"])),
            ("Code", sum(t[0] in CODE for t in build)), ("Ship", sum(t[0] not in CODE for t in build))]


def vis(css: str = "transform:none") -> str:
    return f"{ON};{css}"


def polar(r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return CX + r * math.sin(a), CY - r * math.cos(a)


def seg(r0: float, r1: float, deg: float) -> str:
    x0, y0 = polar(r0, deg)
    x1, y1 = polar(r1, deg)
    return f"M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}"


def ring(r: float) -> str:
    return f"M{num(CX - r)} {CY}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0Z"


def spring(seq: list[tuple[float, float]], fmt, delay: float = 0.0, cap: float | None = None) -> list[tuple]:
    """Stops for a value that jumps to each target with a detent spring: travel to a small
    overshoot (the turnaround), back past the target, settle. seq = [(t, value)], first = rest."""
    prev = seq[0][1]
    stops = [(0, fmt(prev))]
    for t, v in seq[1:]:
        t += delay
        d = v - prev
        o = 0.12 * d if cap is None else math.copysign(min(abs(0.12 * d), cap), d)
        tt = 0.06 if abs(d) <= 60 or cap is None else 0.1
        stops += [(t, fmt(prev), TRAVEL), (t + tt, fmt(v + o), SINE), (t + tt + .05, fmt(v - o * .3), SINE),
                  (t + tt + .1, fmt(v + o * .08), SINE), (t + tt + .15, fmt(v))]
        prev = v
    stops.append((T, fmt(prev)))
    return stops


def needle_seq(ratio: float = 1.0) -> list[tuple[float, float]]:
    return [(0, 0.0)] + [(t, (a - ZERO) * ratio) for t, a in zip(SNAPS, DET)] + [(OUT, 0.0)]


def rot(v: float) -> str:
    return f"transform:rotate({num(v)}deg)"


# ---------------------------------------------------------------- the dial

def defs() -> None:
    # satin metal lit from the top left; the inner chamfer faces the other way, so it is lit at the bottom right
    lib.add_def(f'<linearGradient id="{K}-metal" gradientUnits="userSpaceOnUse" x1="{CX - 80}" y1="{CY - 160}" x2="{CX + 80}" y2="{CY + 160}">'
                '<stop offset="0" stop-color="#FAFBFC"/><stop offset=".3" stop-color="#DDE0E4"/><stop offset=".55" stop-color="#AEB2B9"/>'
                '<stop offset=".8" stop-color="#80848C"/><stop offset="1" stop-color="#5C5F66"/></linearGradient>')
    lib.add_def(f'<linearGradient id="{K}-lip" gradientUnits="userSpaceOnUse" x1="{CX - 80}" y1="{CY - 160}" x2="{CX + 80}" y2="{CY + 160}">'
                '<stop offset="0" stop-color="#1E2024"/><stop offset=".5" stop-color="#5A5D64"/><stop offset="1" stop-color="#C4C7CD"/></linearGradient>')
    lib.add_def(f'<linearGradient id="{K}-hub" gradientUnits="userSpaceOnUse" x1="{CX - 9}" y1="{CY - 13}" x2="{CX + 9}" y2="{CY + 13}">'
                '<stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#C9CCD1"/><stop offset="1" stop-color="#6A6E75"/></linearGradient>')


def bezel() -> str:
    o = f"{CX}px {CY}px"
    metal = (f'<path fill-rule="evenodd" fill="url(#{K}-metal)" d="{ring(R_BEZ_OUT)}{ring(R_BEZ_IN)}"/>'
             f'<path fill-rule="evenodd" fill="url(#{K}-lip)" d="{ring(R_BEZ_IN)}{ring(R_LIP)}"/>')
    # knurl: dark notches over the fixed light; it spins in on the landing, then turns with the needle
    notches = "".join(seg(R_BEZ_IN + 1.5, R_BEZ_OUT - 1.5, i * 3) for i in range(120))
    knurl = f'<path d="{notches}" stroke="#000" stroke-opacity=".5" stroke-width="1.1" fill="none"/>'
    turn = spring(needle_seq(), rot, cap=5)
    turn = [(0, rot(-150)), (T0, rot(-150), EXPO), (T0 + .24, rot(0))] + turn[1:]
    knurl = at(knurl, turn, o)
    land = [(0, "transform:scale(1.3)"), (T0, "transform:scale(1.3)", EXPO), (T0 + .24, "transform:none"), (T, "transform:none")]
    return at(metal + knurl, land, o)


def scale_ring() -> str:
    """61 ticks every 4.5° from the stop; the six detents are long. They sweep in clockwise in groups of five."""
    out = []
    for g in range(13):
        fine, det = [], []
        for j in range(5 * g, min(5 * g + 5, 61)):
            a = ZERO + 4.5 * j
            if j % 10 == 5:
                det.append(seg(R_DET_IN, R_TICK_OUT, a))
            elif j in (0, 60):
                fine.append(seg(R_DET_IN + 3, R_TICK_OUT, a))
            else:
                fine.append(seg(R_FINE_IN, R_TICK_OUT, a))
        body = f'<path d="{"".join(fine)}" stroke="{SUB}" stroke-opacity=".6" stroke-width="1" fill="none"/>'
        if det:
            body += f'<path d="{"".join(det)}" stroke="{SUB}" stroke-width="2.2" fill="none"/>'
        t = T0 + .02 + g * .012
        out.append(at(body, [(0, off("transform:scale(1.14)")), (t - E, off("transform:scale(1.14)")),
                             (t, vis("transform:scale(1.14)"), EXPO), (t + .14, vis()), (T, vis())], f"{CX}px {CY}px"))
    sweep = [(0, rot(-28)), (T0, rot(-28), EXPO), (T0 + .3, rot(0)), (T, rot(0))]
    return at("".join(out), sweep, f"{CX}px {CY}px")


def detents_lit() -> str:
    """The selected detent lights: white, a touch longer, stamped in as the needle arrives."""
    out = []
    ends = SNAPS[1:] + [OUT]
    for a, t, e in zip(DET, SNAPS, ends):
        on, offt = t + .045, e + .045
        mx, my = polar((R_DET_IN + R_TICK_OUT) / 2, a)
        tick = f'<path d="{seg(R_DET_IN - 3, R_TICK_OUT + 2, a)}" stroke="{INK}" stroke-width="2.8" fill="none"/>'
        out.append(at(tick, [(0, off("transform:scale(1.4)")), (on - E, off("transform:scale(1.4)")),
                             (on, vis("transform:scale(1.4)"), EXPO), (on + .12, vis()), (offt - E, vis()), (offt, off()), (T, off())],
                      f"{mx:.1f}px {my:.1f}px"))
    return "".join(out)


def face() -> str:
    """Inner dot ring: counter-rotates a fraction of each snap (parallax under the needle)."""
    dots = "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.1"/>' for x, y in (polar(R_DOTS, i * 6) for i in range(60)))
    body = f'<g fill="{SUB}" fill-opacity=".55">{dots}</g>'
    o = f"{CX}px {CY}px"
    body = at(body, spring(needle_seq(-0.16), rot), o)
    body = at(body, [(0, rot(0)), (T0, rot(0)), (T1, rot(-14)), (T, rot(-14))], o)   # and a slow drift under it all
    t = T0 + .07
    return at(body, [(0, off("transform:scale(1.12)")), (t - E, off("transform:scale(1.12)")), (t, vis("transform:scale(1.12)"), EXPO),
                     (t + .16, vis()), (T, vis())], o)


def needle() -> str:
    o = f"{CX}px {CY}px"
    shape = (f'<path fill="{INK}" d="M{num(CX - .7)} {CY - R_NEEDLE}H{num(CX + .7)}L{num(CX + 2.5)} {CY - 12}V{CY + 17}'
             f'H{num(CX - 2.5)}V{CY - 12}Z"/>'
             f'<rect x="{num(CX - 4.5)}" y="{CY + 14}" width="9" height="16" rx="4.5" fill="{INK}"/>')
    swing = spring([(0, ZERO)] + list(zip(SNAPS, DET)) + [(OUT, ZERO)], rot, cap=5)
    arm = at(shape, swing, o)
    hub = (f'<circle cx="{CX}" cy="{CY}" r="11.5" fill="url(#{K}-hub)"/>'
           f'<circle cx="{CX}" cy="{CY}" r="6" fill="none" stroke="#000" stroke-opacity=".35"/>'
           f'<circle cx="{CX}" cy="{CY}" r="2.2" fill="#000"/>')
    td = T0 + .1
    drop = [(0, off("transform:scale(1.6)")), (td - E, off("transform:scale(1.6)")), (td, vis("transform:scale(1.6)"), BACK),
            (td + .16, vis()), (T, vis())]
    return at(arm + hub, drop, o)


def dial() -> str:
    defs()
    body = face() + scale_ring() + detents_lit() + bezel() + needle()
    o = f"{CX}px {CY}px"
    # alive through the hold (slow push), then it pushes into the camera
    cam = [(0, "transform:none"), (SNAPS[0], "transform:none", SINE), (PUSH, "transform:scale(1.04)", EASE_IN),
           (T1, "transform:scale(2.6)"), (T, "transform:scale(2.6)")]
    return at(body, cam, o)


# ---------------------------------------------------------------- the readout: two counter drums

def drum(rows: list[str], face: str, size: float, base: float, pitch: float, cls: str, slot: tuple[float, float],
         delay: float, sid: str) -> str:
    """A strip of rows (blank, the six, blank) behind a static slot; it rolls one row per snap."""
    strip = "".join(text(face, s, size, RX, base + i * pitch, cls) for i, s in enumerate(rows) if s)
    top, bot = base - slot[0], base + slot[1]
    lib.add_def(f'<clipPath id="{K}-{sid}"><rect x="{RX - 40}" y="{num(top)}" width="{num(940 - RX)}" height="{num(bot - top)}"/></clipPath>')
    seq = [(0, 0.0)] + [(t, -(k + 1) * pitch) for k, t in enumerate(SNAPS)] + [(OUT, -(len(rows) - 1) * pitch)]
    rolled = at(strip, spring(seq, lambda v: f"transform:translateY({num(v)}px)", delay=delay))
    return f'<g clip-path="url(#{K}-{sid})">{rolled}</g>'


def readout() -> str:
    gs = groups()
    names = [""] + [n for n, _ in gs] + [""]
    counts = [""] + [f"{c} tools" for _, c in gs] + [""]
    body = (drum(names, "sans_bk", NAME_SIZE, NAME_B, NAME_P, "ink", (76, 24), 0.0, "name")
            + drum(counts, "sans_md", CNT_SIZE, CNT_B, CNT_P, "sub", (24, 9), 0.025, "count"))
    # a slow drift left through the hold keeps it alive
    return at(body, [(0, "transform:none"), (SNAPS[0], "transform:none", SINE), (OUT, "transform:translateX(-12px)"),
                     (T, "transform:translateX(-12px)")])


def build() -> str:
    body = dial() + readout()
    return at(body, [(0, off()), (T0 - E, off()), (T0, vis()), (T1 - E, vis()), (T1, off()), (T, off())])
