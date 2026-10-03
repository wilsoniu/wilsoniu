"""SHOT 04 — THE STACK (5.5–8.0).

Beat map (reel seconds, 16th note = 0.125s):
  5.500  hard cut: camera dollies in; "THE STACK" types on; "00" rises into its slot
  5.56   "instruments" rises letter by letter out of a clip line
  5.625  column hits on 16ths (DESIGN, MOTION, 3D, AI, BUILD): an accent streak drops down the
         column, the hairline draws, every tool pops in behind the streak (BACK, 22ms stagger),
         and one slab letter of a ghost "S-T-A-C-K" cuts in behind the grid;
         the counter ticks once per tool that lands, 00 -> 27, and flashes accent on 27
  6.40   full grid holds, legible; columns drift in alternating parallax, slow push-in
  6.5    a skewed light band sweeps left -> right (one column per 0.2s): each column it crosses flashes its count and
         hairline accent, and its tools ripple in a diagonal wave
  7.70   implosion: tools collapse toward the centre in reverse order, counter counts back to 00,
         hairlines retract, ghost letters cut out K-C-A-T-S on 16ths, header exits — hard cut at 8.0
"""

import lib
from lib import ACC, BACK, DIM, EASE_IN, EXPO, INK, RULE, SINE, T, X0, X1, label, letters, mark, num, text, timeline

K = "s4"
T0, T1 = lib.SHOTS[K]
CUT_IN, CUT_OUT = T0 + 0.005, T1 - 0.005


def vis(tf: str = "none", op: float = 1) -> str:
    return f"opacity:{num(op)};visibility:visible;transform:{tf}"


def hid(tf: str = "none") -> str:
    return f"opacity:0;visibility:hidden;transform:{tf}"


def anim(body: str, stops: list[tuple], origin: str = "", extra: str = "") -> str:
    style = timeline([s if len(s) == 3 and s[2] else s[:2] for s in stops])
    if origin:
        style += f";transform-origin:{origin}"
    return f'<g style="{style}{extra}">{body}</g>'


def window(body: str, tf_in: str = "none", tf_out: str = "none", origin: str = "") -> str:
    """Linear drift inside the shot window with hard cuts on both edges."""
    return anim(body, [(0, hid(tf_in)), (T0, hid(tf_in)), (CUT_IN, vis(tf_in)), (CUT_OUT, vis(tf_out)), (T1, hid(tf_out)), (T, hid(tf_out))], origin)


# ---------------------------------------------------------------- layout

GUT = 16
COLW = (X1 - X0 - 4 * GUT) / 5
PITCH_X = COLW + GUT
Y_HEAD = 212          # group label baseline
Y_RULE = 222.5        # hairline
Y_ITEM = 238          # first mark top
PITCH_Y = 32
MK = 16

Y_TITLE = 162         # counter / "instruments" baseline
Y_LABEL = 98
CNT_P = 72            # counter strip pitch

HIT = [T0 + 0.125 + 0.125 * k for k in range(5)]          # column hits, on 16ths
BAND = [6.5 + 0.2 * k for k in range(5)]                  # band crosses column k
EXIT0, EXIT_STEP, EXIT_D = 7.70, 0.0065, 0.13


def col_x(k: int) -> float:
    return X0 + k * PITCH_X


# ---------------------------------------------------------------- pieces

def items() -> tuple[list[str], list[float], list[float]]:
    """Per-column item markup, landing times and exit times."""
    flat = [(k, r, it) for k, (_, its) in enumerate(lib.STACK) for r, it in enumerate(its)]
    n = len(flat)
    cols: list[list[str]] = [[] for _ in lib.STACK]
    lands, exits = [], []
    for j, (k, r, (name, src, cap)) in enumerate(flat):
        x, y = col_x(k), Y_ITEM + r * PITCH_Y
        cx, cy = x + MK / 2, y + MK / 2
        ti = HIT[k] + 0.03 + r * 0.022
        tw = BAND[k] - 0.04 + r * 0.012
        te = EXIT0 + (n - 1 - j) * EXIT_STEP
        dx, dy = (480 - cx) * 0.38, (360 - cy) * 0.38
        body = (f'<g fill="{INK}" color="{INK}">{mark(name, src, cap, x, y, MK)}</g>'
                + text("sans", name, 14, x + MK + 10, y + 13, "ink"))
        pop = "translateY(10px) scale(.6)"
        stops = [(0, hid(pop)), (ti, hid(pop), BACK), (ti + 0.32, vis()),
                 (tw, vis(), EXPO), (tw + 0.08, vis("translateX(4px)"), SINE), (tw + 0.32, vis()),
                 (te, vis(), EASE_IN), (te + EXIT_D, hid(f"translate({num(dx)}px,{num(dy)}px) scale(0)")),
                 (T, hid(f"translate({num(dx)}px,{num(dy)}px) scale(0)"))]
        cols[k].append(anim(body, stops, f"{num(cx)}px {num(cy)}px"))
        lands.append(ti + 0.05)
        exits.append(te + 0.04)
    return ["".join(c) for c in cols], sorted(lands), sorted(exits)


def column_head(k: int, group: str, count: int) -> str:
    x, h, b = col_x(k), HIT[k], BAND[k]
    out = []
    # group label slides in from the left
    lab = label(group, x, Y_HEAD, "sub")
    out.append(anim(lab, [(0, hid("translateX(-12px)")), (h, hid("translateX(-12px)"), EXPO), (h + 0.3, vis()),
                          (7.80 + (4 - k) * 0.02, vis(), EASE_IN), (7.95 + (4 - k) * 0.01, hid("translateY(-10px)")),
                          (T, hid("translateY(-10px)"))]))
    # count, cut in a 32nd later; flashes accent as the band passes
    cnt = f"{count:02d}"
    out.append(anim(label(cnt, x + COLW, Y_HEAD, "dim", "end"),
                    [(0, hid()), (h + 0.06, hid()), (h + 0.065, vis()), (7.82, vis()), (7.825, hid()), (T, hid())]))
    out.append(anim(label(cnt, x + COLW, Y_HEAD, "acc", "end"),
                    [(0, hid()), (b - 0.02, hid()), (b - 0.015, vis()), (b + 0.2, vis()), (b + 0.205, hid()), (T, hid())]))
    # hairline draws in, retracts on exit
    ln = f'<path d="M{num(x)} {Y_RULE}H{num(x + COLW)}" stroke="{DIM}" stroke-opacity=".6" fill="none"/>'
    o = f"{num(x)}px {Y_RULE}px"
    out.append(anim(ln, [(0, hid("scaleX(0)")), (h, hid("scaleX(0)"), EXPO), (h + 0.45, vis()),
                         (7.72 + (4 - k) * 0.025, vis(), EASE_IN), (7.9 + (4 - k) * 0.02, vis("scaleX(0)")),
                         (7.9 + (4 - k) * 0.02 + 0.005, hid("scaleX(0)")), (T, hid("scaleX(0)"))], o))
    # accent wipe along the hairline when the band crosses
    acc = f'<path d="M{num(x)} {Y_RULE}H{num(x + COLW)}" stroke="{ACC}" stroke-width="1.5" fill="none"/>'
    out.append(anim(acc, [(0, hid("scaleX(0)")), (b - 0.08, hid("scaleX(0)"), EXPO), (b + 0.14, vis()),
                          (b + 0.22, vis(), SINE), (b + 0.5, vis(op=0)), (b + 0.505, hid()), (T, hid())], o))
    # accent streak drops down the column just ahead of the tools
    y0, y1 = Y_RULE - 26, Y_ITEM + len(lib.STACK[k][1]) * PITCH_Y + 6
    L, dash = y1 - y0, 56
    sx = x - 8
    streak = (f'<path d="M{num(sx)} {num(y0)}V{num(y1)}" stroke="{ACC}" stroke-width="1.5" fill="none" '
              f'stroke-dasharray="{dash} {num(L + dash + 40)}"/>')
    dur = (L + dash) / (PITCH_Y / 0.022)
    out.append(anim(streak, [(0, hid() + f";stroke-dashoffset:{dash}px"), (h, vis() + f";stroke-dashoffset:{dash}px"),
                             (h + dur, vis() + f";stroke-dashoffset:{num(-L)}px"), (h + dur + 0.005, hid()), (T, hid())]))
    return "".join(out)


def counter(lands: list[float], exits: list[float]) -> tuple[str, float]:
    """Two-digit counter on a stepped strip: +1 per tool landing, -1 per tool leaving."""
    cell = max(lib.width("sans_bk", d, 64) for d in "0123456789")
    n = len(lands)
    strip = []
    for i in range(n + 1):
        for c, d in enumerate(f"{i:02d}"):
            strip.append(text("sans_bk", d, 64, X0 + cell * (c + 0.5), Y_TITLE + i * CNT_P, "ink", anchor="middle"))
    # stepped keyframes: each value holds until the next stop
    frames = [(0, "transform:translateY(0)", "step-end")]
    frames += [(t, f"transform:translateY({-i * CNT_P}px)", "step-end") for i, t in enumerate(lands, 1)]
    frames += [(t, f"transform:translateY({-(n - i) * CNT_P}px)", "step-end") for i, t in enumerate(exits, 1)]
    frames.append((T, "transform:translateY(0)"))
    strip_g = f'<g style="{timeline(frames)}">{"".join(strip)}</g>'
    # accent flash on reaching the full count
    t_full = lands[-1]
    flash = "".join(text("sans_bk", d, 64, X0 + cell * (c + 0.5), Y_TITLE, "acc", anchor="middle") for c, d in enumerate(f"{n:02d}"))
    flash_g = anim(flash, [(0, hid()), (t_full, hid()), (t_full + 0.005, vis()), (t_full + 0.16, vis()), (t_full + 0.165, hid()), (T, hid())])
    # slot entrance / exit on a parent so it composes with the steps
    t_zero = exits[-1]
    slot = anim(strip_g + flash_g, [(0, hid(f"translateY({CNT_P}px)")), (T0, hid(f"translateY({CNT_P}px)")),
                                     (CUT_IN, vis(f"translateY({CNT_P}px)"), EXPO), (T0 + 0.25, vis()),
                                     (t_zero + 0.01, vis(), EASE_IN), (t_zero + 0.08, vis(f"translateY({CNT_P}px)")),
                                     (t_zero + 0.085, hid(f"translateY({CNT_P}px)")), (T, hid(f"translateY({CNT_P}px)"))])
    lib.add_def(f'<clipPath id="{K}-cnt"><rect x="{X0 - 4}" y="{Y_TITLE - 54}" width="{num(cell * 2 + 8)}" height="66"/></clipPath>')
    return f'<g clip-path="url(#{K}-cnt)">{slot}</g>', 2 * cell


def title_word(x: float) -> str:
    """'instruments' rising out of a clip line, letter by letter."""
    word = "instruments"
    lib.add_def(f'<clipPath id="{K}-word"><rect x="{num(x - 6)}" y="{Y_TITLE - 70}" width="{num(lib.width("italic", word, 64) + 20)}" height="84"/></clipPath>')
    out = []
    for i, (lx, adv, ch) in enumerate(letters("italic", word, 64, x, Y_TITLE)):
        g = text("italic", ch, 64, lx, Y_TITLE, "name")
        tin = T0 + 0.06 + i * 0.025
        tout = 7.86 + i * 0.01
        out.append(anim(g, [(0, hid("translateY(80px)")), (tin, hid("translateY(80px)"), EXPO), (tin + 0.38, vis()),
                            (tout, vis(), EASE_IN), (tout + 0.11, vis("translateY(-80px)")),
                            (tout + 0.115, hid("translateY(-80px)")), (T, hid("translateY(-80px)"))]))
    return f'<g clip-path="url(#{K}-word)">{"".join(out)}</g>'


def slate() -> str:
    """Accent block + 'THE STACK' typed on, deleted on the way out."""
    out = [anim(f'<rect x="{X0}" y="{Y_LABEL - 7}" width="7" height="7" fill="{ACC}"/>',
                [(0, hid()), (T0, hid()), (CUT_IN, vis()), (7.975, vis()), (7.98, hid()), (T, hid())])]
    s = "THE STACK"
    for i, (lx, adv, ch) in enumerate(letters("mono", s, 9.5, X0 + 15, Y_LABEL, 0.16)):
        if ch == " ":
            continue
        tin = T0 + 0.02 + i * 0.022
        tout = 7.80 + (len(s) - 1 - i) * 0.018
        out.append(anim(text("mono", ch, 9.5, lx, Y_LABEL, "ink", 0.16),
                        [(0, hid()), (tin, hid()), (tin + 0.004, vis()), (tout, vis()), (tout + 0.004, hid()), (T, hid())]))
    return "".join(out)


def band() -> str:
    """A skewed full-height glint crossing column k at BAND[k]; it also catches the ghost letters."""
    lib.add_def(f'<linearGradient id="{K}-band" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                f'<stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    skew = 0.21   # tan(12deg)
    rect = (f'<rect x="-80" y="0" width="160" height="{lib.H}" fill="url(#{K}-band)" '
            f'transform="matrix(1 0 {-skew} 1 {num(skew * 360)} 0)"/>')
    speed = PITCH_X / 0.2
    c0 = col_x(0) + 70

    def tx(t: float) -> str:
        return f"translateX({num(c0 + (t - BAND[0]) * speed)}px)"
    ta, tb = 6.22, 7.52
    return anim(rect, [(0, hid(tx(ta))), (ta, hid(tx(ta))), (ta + 0.12, vis(tx(ta + 0.12))), (tb - 0.12, vis(tx(tb - 0.12))),
                       (tb, hid(tx(tb))), (T, hid(tx(tb)))])


def ghost() -> str:
    """Slab letters S-T-A-C-K behind the grid: one cuts in on each column hit, out in reverse on the exit."""
    size, base = 270, 522
    out = []
    for k, (lx, adv, ch) in enumerate(letters("sans_bk", "STACK", size, 480, base, -0.02, "middle")):
        g = text("sans_bk", ch, size, lx, base, "")
        tin, tout = HIT[k], 7.70 + (4 - k) * 0.0625
        o = f"{num(lx + adv / 2)}px {base - 96}px"
        out.append(anim(g, [(0, hid("scale(1.12)")), (tin, hid("scale(1.12)")), (tin + 0.005, vis("scale(1.12)"), EXPO),
                            (tin + 0.35, vis()), (tout, vis()), (tout + 0.005, hid()), (T, hid())], o))
    return window(f'<g fill="{RULE}" fill-opacity=".6">{"".join(out)}</g>', "translateX(70px)", "translateX(-90px)")


# ---------------------------------------------------------------- shot

def build() -> str:
    cols, lands, exits = items()
    heads = [column_head(k, g, len(its)) for k, (g, its) in enumerate(lib.STACK)]
    columns = []
    for k in range(5):
        a = 5 if k % 2 == 0 else -5
        columns.append(window(heads[k] + cols[k], f"translateY({a}px)", f"translateY({-a}px)"))
    # camera: dollies in and settles, keeps creeping in through the hold, pulls back on the exit
    # (never above scale 1, so text stays inside the 64..896 margins)
    c0 = "translateY(22px) scale(.95)"
    cam = [(0, hid(c0)), (T0, hid(c0)), (CUT_IN, vis(c0), EXPO), (6.45, vis("scale(.988)")), (7.70, vis(), EASE_IN),
           (CUT_OUT, vis("scale(.92)")), (T1, hid("scale(.92)")), (T, hid("scale(.92)"))]
    grid = anim("".join(columns), cam, "480px 360px")

    cnt, cw = counter(lands, exits)
    header = window(slate() + cnt + title_word(X0 + cw + 16), "translateX(9px)", "translateX(0)")
    return ghost() + band() + grid + header
