"""SHOT 04 — THE STACK (5.5–8.0).

Beat map (reel seconds, 16th note = 0.125s):
  5.500  hard cut: camera dollies in; "00" rises into its slot
  5.56   "instruments" rises letter by letter out of a clip line
  5.625  column hits on 16ths (DESIGN, MOTION, 3D, AI, BUILD): the hairline draws and every tool
         pops in (BACK, 22ms stagger); the counter ticks once per tool, 00 -> 27, flashing accent on 27
  6.40   full grid holds, legible; columns drift in alternating parallax, slow push-in
  6.5    tools ripple in a diagonal wave, column by column
  7.70   implosion: tools collapse toward the centre in reverse order, counter counts back to 00,
         hairlines retract, header exits — hard cut at 8.0
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
Y_RULE = 228.5        # hairline (16px under the labels)
Y_ITEM = 244          # first mark top (16px under the hairline)
PITCH_Y = 32
MK = 16

Y_TITLE = 162         # counter / "instruments" baseline
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
    lab = label(group, x, Y_HEAD, "sub", size=11.5)
    out.append(anim(lab, [(0, hid("translateX(-12px)")), (h, hid("translateX(-12px)"), EXPO), (h + 0.3, vis()),
                          (7.80 + (4 - k) * 0.02, vis(), EASE_IN), (7.95 + (4 - k) * 0.01, hid("translateY(-10px)")),
                          (T, hid("translateY(-10px)"))]))
    # hairline draws in, retracts on exit
    ln = f'<path d="M{num(x)} {Y_RULE}H{num(x + COLW)}" stroke="{DIM}" stroke-opacity=".6" fill="none"/>'
    o = f"{num(x)}px {Y_RULE}px"
    out.append(anim(ln, [(0, hid("scaleX(0)")), (h, hid("scaleX(0)"), EXPO), (h + 0.45, vis()),
                         (7.72 + (4 - k) * 0.025, vis(), EASE_IN), (7.9 + (4 - k) * 0.02, vis("scaleX(0)")),
                         (7.9 + (4 - k) * 0.02 + 0.005, hid("scaleX(0)")), (T, hid("scaleX(0)"))], o))
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
    header = window(cnt + title_word(X0 + cw + 16), "translateX(9px)", "translateX(0)")
    return grid + header
