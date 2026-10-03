"""SHOT 07 — SHIPPING (9.0-11.0). Real data only: this repo's own source, its own commits, and the
GitHub contribution calendar in _build/data/contributions.json.

 9.00  HARD CUT into an editor mid-session: lib.py itself, monochrome syntax greys, line numbers.
       A block cursor types the bottom line and the file streams upward; every line comes faster
       than the last (auto-indent, character steps) until the column whips up out of frame.
 9.50  HARD CUT. The year of contributions sweeps in left to right, one week per column, each
       column springing open with every active day popping; the year counter rolls with the sweep
       and lands on the total on the beat (10.00). Under the graph the commit log flicks by, one
       real commit per ~0.1 s, oldest to newest, landing on the latest on 10.50.
10.25  Punch: this week's number slams in above the week it counts, and that column kicks.
10.80  Exit: the rows launch upward at different speeds (top fastest, so gaps only grow); hard
       cut at 11.00.
"""

import json
import re
import subprocess
from itertools import pairwise

import lib
from lib import BACK, BG, EASE_IN, EXPO, INK, T, at, num, text, width

K = "s7"
T0, T1 = lib.SHOTS[K]          # 9.0, 11.0
CUT = 9.5                      # editor -> graph
PUNCH = 10.25                  # "this week"
EXIT = 10.8
E = 0.004
VIS = "opacity:1;visibility:visible;"
HID = "opacity:0;visibility:hidden;"

# Fallback if git isn't available at build time: `git log --format='%h %s' -n 12` when this shot was written.
COMMITS_SNAPSHOT = [
    "e68af81 Card: the CYTE wordmark replaces the small mark and studio name",
    "bd76f1b Describe the reel accurately in its alt text",
    "0cccb4c Split the profile into a still card and a fast reel, in black, white and metal",
    "666764b Recut the reel as a 12-second storyboard of six shots on a 120 BPM grid",
    "ec51e11 Reel becomes one continuous 10-second flight over a wireframe valley",
    "cd51e4a Turn the profile card into a 24-second looping reel",
    "1205a46 Card fills the README width; larger micro labels",
    "b90eaf2 Redesign profile README as an animated card",
    "1693cb9 Revise README to include updated visuals and skills",
    "184bea6 Enhance README with design focus and tools",
    "34580a7 Initial commit",
]


def anim(body: str, stops: list[tuple], origin: str = "") -> str:
    """Reel-clock animation hidden at 0 and T; `stops` carry their own visibility."""
    return at(body, [(0, HID + "transform:none"), *stops, (T, HID + "transform:none")], origin)


def win(body: str, t0: float, t1: float, frames: list[tuple] | None = None, origin: str = "") -> str:
    """Hard cut on at t0, hard cut off at t1; `frames` are (t, transform[, ease]) inside the window."""
    frames = frames or [(t0, "transform:none")]
    first, last = frames[0][1], frames[-1][1]
    # visibility flips exactly on the cut (step-end), so two slots never share a frame
    stops = [(t0 - E, HID + first, "step-end")]
    if frames[0][0] > t0:
        stops.append((t0, VIS + first))
    stops += [(t, VIS + css, *rest) for t, css, *rest in frames]
    if frames[-1][0] < t1 - E:
        stops.append((t1 - E, VIS + last))
    stops[-1] = (stops[-1][0], stops[-1][1], "step-end")
    stops.append((t1, HID + last))
    assert all(a[0] <= b[0] for a, b in pairwise(stops)), stops
    return anim(body, stops, origin)


# ---------------------------------------------------------------- act 1: the editor

FS, LH, ADV = 13, 19, 7.8      # code size, line height, mono advance
GUT, CX0 = 92, 116             # line numbers end at GUT; code starts at CX0
SLOT = 436                     # baseline of the line being typed
PRE = 18                       # lines already on screen at the cut
MAXC = 92                      # columns that fit before the right margin
KW = {"def", "return", "for", "in", "if", "else", "elif", "import", "from", "class", "not", "and", "or", "None",
      "True", "False", "lambda", "with", "while", "try", "except", "raise", "is", "self"}
TOKEN = re.compile(r'(?P<s>[rbf]?"[^"]*"?|[rbf]?\'[^\']*\'?)|(?P<m>#.*$)|(?P<w>[A-Za-z_]\w*)|(?P<n>\d[\d.]*)|(?P<o>\S)')


def code_lines() -> list[tuple[int, str]]:
    src = (lib.ROOT / "_build" / "lib.py").read_text().splitlines()
    start = next(i for i, s in enumerate(src) if s.startswith("class Face"))
    mono = lib.F["mono"].cmap
    out = []
    for n, s in enumerate(src[start:], start + 1):
        s = s.rstrip()
        if s and all(ord(c) in mono for c in s):
            out.append((n, s[:MAXC]))
    return out


def code_row(s: str, y: float) -> str:
    """One line in monochrome syntax greys, each token placed on the mono grid."""
    out = []
    doc = s.strip().startswith(('"""', "'''"))
    for m in TOKEN.finditer(s):
        kind, tok = m.lastgroup, m.group()
        cls = {"s": f"{K}-s", "m": f"{K}-m", "n": "ink", "o": f"{K}-c"}.get(kind) or ("ink" if tok in KW else f"{K}-c")
        if doc:
            cls = f"{K}-s"
        out.append(text("mono", tok, FS, CX0 + m.start() * ADV, y, cls))
    return "".join(out)


def editor() -> str:
    lib.add_css(f".{K}-c{{fill:#BCBFC5}}.{K}-s{{fill:#7E8189}}.{K}-m{{fill:#55575E}}")
    lines = code_lines()
    # the typing schedule: each line faster than the last
    durs = [0.075, 0.054, 0.043, 0.036, 0.031, 0.028, 0.026]
    t, i, sched = T0 + 0.03, 0, []      # (start typing a_i, step-up before it s_i, line duration d_i)
    while True:
        d = durs[min(i, len(durs) - 1)]
        s = 0 if i == 0 else min(0.03, 0.6 * sched[-1][2])
        if t >= CUT - 0.11 or PRE + i >= len(lines):
            break
        sched.append((t, s, d))
        t += d
        i += 1

    rows = []
    for j in range(PRE):                                   # already written
        n, s = lines[j]
        y = SLOT + (j - PRE) * LH
        rows.append(text("mono", str(n), FS, GUT, y, f"{K}-m", anchor="end") + code_row(s, y))
    for i, (a, s, d) in enumerate(sched):                  # typed on screen
        n, src = lines[PRE + i]
        y = SLOT + i * LH
        on = a - s if i else T0
        nxt = sched[i + 1][0] - sched[i + 1][1] if i + 1 < len(sched) else CUT
        row = text("mono", str(n), FS, GUT, y, f"{K}-m", anchor="end") + code_row(src, y)
        rows.append(win(row, on, CUT))
        # cursor + a BG cover to its right ride with the line; the cover hides what isn't typed yet
        indent = len(src) - len(src.lstrip())
        n_ch = len(src) - indent
        reveal = max(0.01, (nxt - a) - 0.008)
        typer = (f'<rect x="{num(CX0 + ADV)}" y="{y - 11}" width="{num(MAXC * ADV + 40)}" height="15" fill="{BG}"/>'
                 f'<rect x="{num(CX0 + 0.5)}" y="{y - 11}" width="{num(ADV - 1)}" height="14" fill="{INK}"/>')
        x0, x1 = f"transform:translateX({num(indent * ADV)}px)", f"transform:translateX({num(len(src) * ADV)}px)"
        rows.append(win(typer, on, nxt if i + 1 < len(sched) else CUT,
                        [(on, x0), (a, x0, f"steps({n_ch},end)"), (min(a + reveal, nxt - E), x1)]))

    # scroll: the file steps up one line per typed line (eased), then whips up and out before the cut
    stops = [(T0, "transform:translateY(0px)")]
    for i, (a, s, d) in enumerate(sched[1:], 1):
        stops += [(a - s, f"transform:translateY({num(-(i - 1) * LH)}px)", EXPO), (a, f"transform:translateY({num(-i * LH)}px)")]
    last = -(len(sched) - 1) * LH
    stops += [(CUT - 0.1, f"transform:translateY({num(last)}px)", EASE_IN), (CUT - E, f"transform:translateY({num(last - 260)}px)")]
    col = win("".join(rows), T0, CUT, [(t_, css, *r) for t_, css, *r in stops])

    lib.add_def(f'<linearGradient id="{K}-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/>'
                f'<stop offset=".35" stop-color="{BG}" stop-opacity=".85"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>')
    fade = f'<rect x="0" y="{lib.VIEW_Y}" width="{lib.W}" height="170" fill="url(#{K}-fade)"/>'
    return win(col + fade, T0, CUT, [(T0, "transform:scale(1)"), (CUT - E, "transform:scale(1.05)")], f"{CX0}px {SLOT}px")


# ---------------------------------------------------------------- act 2: the year

CELL, PITCH = 11, 15
XL = (lib.W - (52 * PITCH + CELL)) / 2        # 84.5
XR = lib.W - XL                                # 875.5
YN = 241                                       # big numbers' baseline
NUM = 84                                       # big numbers' size
HY = 275                                       # graph top
YT = 420                                       # commit log baseline
SWEEP = (CUT + 0.02, 10.0)                     # first and last column on


def calendar() -> tuple[list[list[int]], int]:
    data = json.loads((lib.ROOT / "_build" / "data" / "contributions.json").read_text())
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]], cal["totalContributions"]


def level(n: int) -> str:
    return "#1A1A1D" if n == 0 else "#46484E" if n == 1 else "#7D8087" if n <= 3 else "#BCBFC5" if n <= 6 else INK


def col_time(c: int, n: int) -> float:
    return SWEEP[0] + (SWEEP[1] - SWEEP[0]) * c / (n - 1)


def graph(weeks: list[list[int]]) -> str:
    out = []
    last = len(weeks) - 1
    for c, days in enumerate(weeks):
        tc = col_time(c, len(weeks))
        x = XL + c * PITCH
        cells = []
        for r, n in enumerate(days):
            y = HY + (r + 7 - len(days) if c == 0 else r) * PITCH
            cell = f'<rect x="{num(x)}" y="{num(y)}" width="{CELL}" height="{CELL}" rx="2.5" fill="{level(n)}"/>'
            if n:   # an active day hits as its column lands; this week's days kick again on the punch
                o = f"{num(x + CELL / 2)}px {num(y + CELL / 2)}px"
                fr = [(tc + 0.05, "transform:none"), (tc + 0.05 + E, "transform:scale(1.8)", EXPO), (min(tc + 0.27, PUNCH - 0.01), "transform:none")]
                if c == last:
                    fr += [(PUNCH, "transform:none"), (PUNCH + E, "transform:scale(1.75)", BACK), (PUNCH + 0.24, "transform:none")]
                cell = at(cell, [(0, "transform:none"), *fr, (T, "transform:none")], o)
            cells.append(cell)
        o = f"{num(x + CELL / 2)}px {num(HY + 3 * PITCH + CELL / 2)}px"
        out.append(win("".join(cells), tc, T1, [(tc, "transform:scaleY(.3)", BACK), (tc + 0.16, "transform:none")], o))
    return "".join(out)


def roll(values: list[tuple[float, int]], x_end: float, slot: str) -> str:
    """A rolling counter: each value rolls up into a clipped slot as the last rolls out."""
    cap = NUM * 0.726
    rise = cap + 22
    lib.add_def(f'<clipPath id="{slot}"><rect x="{num(XL - 12)}" y="{num(YN - cap - 10)}" width="{num(x_end - XL + 24)}" '
                f'height="{num(cap + 18)}"/></clipPath>')
    out = []
    for k, (t, v) in enumerate(values):
        body = text("sans_bk", str(v), NUM, x_end, YN, "name", -0.02, "end")
        nxt = values[k + 1][0] if k + 1 < len(values) else None
        r_in = 0.05 if nxt is None else min(0.05, nxt - t - E)
        fr = [(t, f"transform:translateY({num(rise)}px)", EXPO), (t + r_in, "transform:none")]
        if nxt is None:
            out.append(win(body, t, T1, fr))
        else:
            r_out = min(0.05, values[k + 2][0] - nxt - E) if k + 2 < len(values) else 0.05
            fr += [(nxt, "transform:none", EXPO), (nxt + r_out, f"transform:translateY({num(-rise)}px)")]
            out.append(win(body, t, nxt + r_out + E, fr))
    return f'<g clip-path="url(#{slot})">{"".join(out)}</g>'


def caption(lines: list[tuple[str, str]], x: float, anchor: str, t: float) -> str:
    """Two caption lines (16px) that rise into place through a slot, bottom line on YN."""
    lid = f"{K}-cap-{anchor}"
    w = max(width("sans_md", s, 16) for s, _ in lines)
    x0 = x if anchor == "start" else x - w
    lib.add_def(f'<clipPath id="{lid}"><rect x="{num(x0 - 4)}" y="{YN - 24 - 16}" width="{num(w + 8)}" height="46"/></clipPath>')
    out = []
    for k, (s, cls) in enumerate(lines):
        y = YN - 24 * (len(lines) - 1 - k)
        out.append(win(text("sans_md", s, 16, x, y, cls, anchor=anchor), t + k * 0.03, T1,
                       [(t + k * 0.03, "transform:translateY(30px)", EXPO), (t + k * 0.03 + 0.22, "transform:none")]))
    return f'<g clip-path="url(#{lid})">{"".join(out)}</g>'


def counters(weeks: list[list[int]], total: int) -> str:
    # the year counter follows the sweep: the running total each time a column with activity lands,
    # thinned so every value gets at least a few frames (always ending on the real total)
    run, events = 0, [(SWEEP[0], 0)]
    for c, days in enumerate(weeks):
        if sum(days):
            run += sum(days)
            events.append((col_time(c, len(weeks)), run))
    assert run == total, (run, total)
    kept = [events[-1]]
    for ev in reversed(events[:-1]):
        if ev[0] <= kept[-1][0] - 0.03:
            kept.append(ev)
    year = roll(kept[::-1], XL + width("sans_bk", str(total), NUM, -0.02), f"{K}-yslot")
    year += caption([("contributions", "ink"), ("in the last year", "sub")],
                    XL + width("sans_bk", str(total), NUM, -0.02) + 22, "start", SWEEP[0] + 0.03)

    # this week: the last column of the calendar (the latest seven days)
    wk = sum(weeks[-1])
    ww = width("sans_bk", str(wk), NUM, -0.02)
    big = text("sans_bk", str(wk), NUM, XR, YN, "name", -0.02, "end")
    o = f"{num(XR - ww / 2)}px {num(YN - NUM * 0.36)}px"
    week = win(big, PUNCH, T1, [(PUNCH, "transform:scale(1.3)", EXPO), (PUNCH + 0.2, "transform:none")], o)
    week += caption([("contributions", "ink"), ("this week", "sub")], XR - ww - 22, "end", PUNCH + 0.02)
    return year + week


def commits() -> list[tuple[str, str]]:
    try:
        raw = subprocess.run(["git", "-C", str(lib.ROOT), "log", "--format=%h %s", "-n", "12"],
                             capture_output=True, text=True, check=True).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        raw = []
    if len(raw) < 6:
        raw = COMMITS_SNAPSHOT
    mono, md = lib.F["mono"].cmap, lib.F["mono_md"].cmap
    out = []
    for line in raw:
        h, _, msg = line.partition(" ")
        if not all(ord(c) in md for c in h) or not all(ord(c) in mono or c == " " for c in msg):
            continue
        if width("mono", f"{h}  {msg}", 14) > XR - XL:
            continue
        out.append((h, msg))
    return out[::-1]          # oldest first, landing on the newest


def ticker() -> str:
    log = commits()
    t0, t_land = SWEEP[0], 10.5
    step = (t_land - t0) / max(len(log) - 1, 1)
    out = []
    for k, (h, msg) in enumerate(log):
        t = t0 + k * step
        t_off = t + step if k + 1 < len(log) else T1
        body = text("mono_md", h, 14, XL, YT, "ink") + text("mono", msg, 14, XL + width("mono", h + "  ", 14), YT, "sub")
        out.append(win(body, t, t_off, [(t, "transform:translateY(7px)", EXPO), (t + 0.05, "transform:none")]))
    return "".join(out)


def year() -> str:
    weeks, total = calendar()

    def lift(body: str, dy: float) -> str:
        """Hold, then launch upward on the exit (accelerating)."""
        return win(body, CUT, T1, [(CUT, "transform:none"), (EXIT, "transform:none", EASE_IN),
                                   (T1 - E, f"transform:translateY({num(dy)}px)")])

    body = lift(counters(weeks, total), -280) + lift(graph(weeks), -200) + lift(ticker(), -130)
    # a slow push-in through the hold keeps the frame alive
    return win(body, CUT, T1, [(CUT, "transform:scale(1)"), (EXIT, "transform:scale(1.02)"), (T1 - E, "transform:scale(1.03)")],
               "480px 300px")


def build() -> str:
    return editor() + year()
