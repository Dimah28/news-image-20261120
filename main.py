#!/usr/bin/env python3
"""news-image-20261120 -- one-page newspaper of Friday 20 November 2026.

A 1024x1024 front page drawn procedurally with the Python standard
library only (math, os, struct, zlib). No network, no image files, no
system fonts: every letter is a Hershey-style single-stroke vector glyph
drawn as polylines, so the poster stays sharp at any size. The program
is deterministic: two runs write byte-identical PNG files.

Run:  MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
Writes entry.png into that directory (or the current directory).
"""
import math
import os
import struct
import zlib

SIZE = 1024

# ------------------------------------------------------------ colours
PAPER = (248, 243, 231)
CREAM = (255, 253, 247)
INK = (24, 24, 24)
NAVY = (20, 42, 68)
NAVY2 = (30, 58, 94)
RED = (178, 52, 42)
BLUE = (44, 96, 140)
TEAL = (46, 124, 108)
GOLD = (198, 160, 72)
GOLDL = (228, 198, 122)
GREY = (108, 103, 90)
FAINT = (214, 206, 188)
ORANGE = (212, 108, 44)
GREEN = (72, 122, 72)
PURPLE = (110, 82, 148)
SKY = (212, 226, 236)
SEA = (204, 218, 226)
LAND = (230, 220, 194)
WHITE = (255, 255, 255)
DARK = (12, 20, 38)

# ------------------------------------------------- Hershey-style font
# One glyph = one string of strokes. A stroke is "x,y x,y ..." on a
# 0..8 wide, 0..10 tall grid, cap-top y=0, baseline y=10. Strokes are
# separated by "|". Lowercase letters are rendered as small caps: the
# same glyph scaled to 0.72 and dropped to the x-height band, which
# keeps body copy readable without a second glyph set.
GLYPH = {
    "A": "0,10 4,0 8,10|2,6 6,6",
    "B": "0,10 0,0 5,0 7,2 7,4 5,6 0,6|5,6 7,7 7,9 5,10 0,10",
    "C": "7,2 5,0 2,0 0,2 0,8 2,10 5,10 7,8",
    "D": "0,10 0,0 5,0 8,2 8,8 5,10 0,10",
    "E": "7,0 0,0 0,10 7,10|0,5 5,5",
    "F": "0,10 0,0 7,0|0,5 5,5",
    "G": "7,2 5,0 2,0 0,2 0,8 2,10 5,10 7,8 7,5 4,5",
    "H": "0,0 0,10|8,0 8,10|0,5 8,5",
    "I": "4,0 4,10|1,0 7,0|1,10 7,10",
    "J": "7,0 7,8 5,10 2,10 1,8",
    "K": "0,10 0,0|8,0 0,5 8,10",
    "L": "0,0 0,10 7,10",
    "M": "0,10 0,0 4,6 8,0 8,10",
    "N": "0,10 0,0 8,10 8,0",
    "O": "2,0 6,0 8,2 8,8 6,10 2,10 0,8 0,2 2,0",
    "P": "0,10 0,0 6,0 8,2 8,4 6,6 0,6",
    "Q": "2,0 6,0 8,2 8,8 6,10 2,10 0,8 0,2 2,0|5,7 8,10",
    "R": "0,10 0,0 6,0 8,2 8,4 6,6 0,6|5,6 8,10",
    "S": "7,2 5,0 2,0 0,2 0,4 2,6 6,6 8,8 8,9 6,10 3,10 1,8",
    "T": "0,0 8,0|4,0 4,10",
    "U": "0,0 0,8 2,10 6,10 8,8 8,0",
    "V": "0,0 4,10 8,0",
    "W": "0,0 2,10 4,5 6,10 8,0",
    "X": "0,0 8,10|8,0 0,10",
    "Y": "0,0 4,5 8,0|4,5 4,10",
    "Z": "0,0 8,0 0,10 8,10",
    "0": "2,0 6,0 8,2 8,8 6,10 2,10 0,8 0,2 2,0|2,8 6,2",
    "1": "3,1 4,0 4,10|1,10 7,10",
    "2": "1,2 2,0 6,0 7,2 7,4 0,10 8,10",
    "3": "1,1 3,0 6,0 7,2 7,4 5,5|5,5 7,6 7,8 6,10 3,10 1,9",
    "4": "0,7 6,0 6,10|0,7 8,7",
    "5": "7,0 1,0 1,4 5,4 7,6 7,8 5,10 2,10 0,8",
    "6": "7,1 5,0 2,0 1,2 0,5 0,8 2,10 5,10 7,8 7,6 5,5 1,5",
    "7": "0,0 8,0 4,10",
    "8": "3,0 6,0 7,2 7,4 5,5 3,5 1,4 0,2 0,1 1,0|5,5 7,6 7,8 6,10 3,10 1,9 0,7 1,5",
    "9": "0,9 0,6 1,4 2,3 5,3 7,5 7,8 6,10 3,10 1,9|1,5 7,5",
    ".": "3,9 4,9",
    ",": "3,9 4,9|4,9 2,12",
    ":": "3,3 4,3|3,8 4,8",
    ";": "3,3 4,3|3,8 4,8|4,8 2,12",
    "'": "3,0 4,3",
    '"': "2,0 3,3|5,0 6,3",
    "-": "1,5 7,5",
    ".": "3,9 4,9",
    "(": "6,0 3,2 3,8 6,10",
    ")": "2,0 5,2 5,8 2,10",
    "!": "4,0 4,7|4,9 4,10",
    "?": "1,2 2,0 6,0 7,2 7,4 5,6 4,7 4,8|4,9 4,10",
    "$": "4,0 4,11|7,2 5,0 2,0 0,2 0,4 2,5 6,5 8,6 8,8 6,10 3,10 1,8",
    "%": "7,0 1,10|2,1 4,1 4,3 2,3|6,7 8,7 8,9 6,9",
    "/": "7,0 1,10",
    "+": "4,2 4,8|1,5 7,5",
    "=": "1,3 7,3|1,7 7,7",
    "&": "7,2 5,0 2,0 0,2 0,5 2,7 8,10|0,10 8,3",
    " ": "",
}
# Advance widths (grid units). Most letters 8, narrow ones less.
ADV = {".": 4, ",": 4, ":": 4, ";": 4, "'": 3, '"': 6, "!": 4, "(": 5,
       ")": 5, "-": 6, "/": 6, "1": 6, "I": 5, "%": 10, "$": 8, "?": 8,
       "M": 10, "W": 10, "O": 9, "Q": 9, "G": 9, "D": 9, "0": 9, "8": 9,
       "&": 9, "=": 8}
SMALL = {"i": 5.0, "l": 5.0, "j": 5.0, "t": 6.0, "f": 6.0, "r": 6.0}


def _strokes(spec):
    out = []
    if not spec:
        return out
    for piece in spec.split("|"):
        pts = []
        for tok in piece.split():
            a, b = tok.split(",")
            pts.append((int(a), int(b)))
        out.append(pts)
    return out


STROKES = {ch: _strokes(spec) for ch, spec in GLYPH.items()}


def _adv(ch):
    if ch == " ":
        return 4.0
    if ch.islower():
        return SMALL.get(ch, 7.0)
    return ADV.get(ch, 8.0)


def _glyph_for(ch):
    """(strokes, scale, y_offset) for one character."""
    if ch.islower():
        up = ch.upper()
        if up in STROKES:
            return STROKES[up], 0.72, 3.0
        return [], 1.0, 0.0
    return STROKES.get(ch, []), 1.0, 0.0


def text_width(s, size):
    sc = size / 10.0
    total = 0.0
    for ch in s:
        # _adv already gives the advance in grid units (lowercase values
        # already allow for the 0.72 small-cap scale), so multiply by
        # sc only -- multiplying by scale again overlaps the glyphs.
        total += _adv(ch) * sc
    total += max(0, len(s) - 1) * sc * 0.18
    return total


def wrap_text(s, size, max_w):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------- canvas
class Page:
    """A flat RGB canvas with the few primitives the poster needs."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def spot(self, cx, cy, r, c):
        r = int(r)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, c)

    def seg(self, x0, y0, x1, y1, c, w=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        half = w // 2
        while True:
            for yy in range(y - half, y + half + 1):
                for xx in range(x - half, x + half + 1):
                    self.put(xx, yy, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def fill_poly(self, pts, c):
        pts = [(int(a), int(b)) for a, b in pts]
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            nodes = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                for x in range(max(0, int(nodes[k])),
                               min(self.w, int(nodes[k + 1]) + 1)):
                    self.put(x, y, c)

    def circle(self, cx, cy, r, c, w=2):
        steps = max(24, int(2 * math.pi * r))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            self.spot(int(cx + r * math.cos(a)),
                      int(cy + r * math.sin(a)), w, c)

    def hrule(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vrule(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)


def write_png(pg):
    raw = bytearray()
    stride = pg.w * 3
    for y in range(pg.h):
        raw.append(0)
        raw += pg.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    hdr = struct.pack(">IIBBBBB", pg.w, pg.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", hdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ------------------------------------------------------------ text out
def draw_text(pg, x, y, s, size, color, bold=False, align="l"):
    """Draw s with its cap-top at y. align l/c/r is relative to x."""
    if align == "c":
        x -= text_width(s, size) / 2
    elif align == "r":
        x -= text_width(s, size)
    sc = size / 10.0
    lw = max(2, int(size * 0.12)) if bold else (2 if size <= 13 else 1)
    cx = float(x)
    for ch in s:
        if ch == " ":
            cx += _adv(ch) * sc + sc * 0.18
            continue
        strokes, scale, yoff = _glyph_for(ch)
        if not strokes:
            cx += _adv(ch) * sc + sc * 0.18
            continue
        ssc = sc * scale
        for st in strokes:
            if len(st) == 1:
                px, py = st[0]
                pg.spot(int(round(cx + px * ssc)),
                        int(round(y + (py * scale + yoff) * sc)),
                        max(1, lw // 2), color)
            else:
                for a, b in zip(st, st[1:]):
                    pg.seg(cx + a[0] * ssc, y + (a[1] * scale + yoff) * sc,
                           cx + b[0] * ssc, y + (b[1] * scale + yoff) * sc,
                           color, w=lw)
        cx += _adv(ch) * sc + sc * 0.18
    return cx


def draw_para(pg, x, y, s, size, max_w, color, bold=False, lh=None,
              max_lines=None, align="l"):
    lines = wrap_text(s, size, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = lh or int(size * 1.6)
    for i, ln in enumerate(lines):
        if align == "c":
            draw_text(pg, x + max_w / 2, y + i * lh, ln, size, color,
                      bold=bold, align="c")
        else:
            draw_text(pg, x, y + i * lh, ln, size, color, bold=bold)
    return y + len(lines) * lh


def badge_num(pg, x, y, n, r=8, bg=RED, fg=WHITE, size=11):
    pg.spot(x + r, y + r, r, bg)
    pg.circle(x + r, y + r, r, fg, w=1)
    draw_text(pg, x + r, y + r - size // 2, str(n), size, fg, bold=True,
              align="c")


# ------------------------------------------------------------ the news
# All 36 stories happened, or were first reported, on Friday 20 Nov
# 2026 in at least one time zone. Outlet in brackets; disputed claims
# are labelled CLAIM or FORECAST in the text.
MASTHEAD = "Friday 20 November 2026"
SUBHEAD = ("Akvan strikes India - Missiles hit Kyiv - COP31 deadlocked "
           "- Asian AI sell-off")
NUMBERS = [
    ("370,000", "evacuated ahead of Akvan"),
    ("3", "killed; 3 bridges hit"),
    ("-6.8%", "TAIEX intraday low"),
    ("2.3%", "Japan Oct headline CPI"),
    ("118", "Phillips makes history"),
    ("8 yrs", "BepiColombo to Mercury"),
]
CHIPS = [("EUROPE", 8, NAVY2), ("AMERICAS", 8, RED), ("ASIA-PACIFIC", 9, TEAL),
         ("MIDEAST", 4, ORANGE), ("AFRICA", 3, GREEN), ("OCEANIA", 3, PURPLE),
         ("WORLD", 1, INK)]
LEADS = [
    (1, "ODISHA, INDIA - CYCLONE", "Cyclone Akvan makes landfall in eastern India",
     "Crosses near Gopalpur at 8:30am IST, winds 70-80 km/h gusting 90; "
     "370,000 evacuated, no major damage. (IMD)", "cyclone"),
    (2, "KYIV, UKRAINE - WAR", "Russia fires wave of ballistic missiles at Kyiv",
     "Overnight barrage kills 3, injures 15; three Dnipro bridges hit in "
     "the biggest bridge attack of the war. (Reuters)", "kyiv"),
    (3, "ANTALYA, TURKIYE - CLIMATE", "COP31 reaches final day deadlocked",
     "Draft omits fossil-fuel phase-out; $120bn adaptation finance "
     "unresolved as hosts push a '35 by 35' clean power. (UN News)", "cop31"),
]
FEATURES = [
    (4, "SEOUL - TOKYO - MARKETS", "AI sell-off: Asia's worst week since 2020",
     "Nikkei -4.9%, KOSPI -5.4%, TAIEX -6.8% (Reuters)", "chart"),
    (5, "SPACE", "BepiColombo reaches Mercury in 8 years",
     "ESA-JAXA probe ends 6bn-mile trip. (ESA, BBC)", "moon"),
    (6, "BRUSSELS - EUROPE", "Burnham holds first EU-UK reset summit",
     "Costa and von der Leyen host UK PM. (EU Council)", "flags"),
    (7, "TOKYO - ECONOMY", "Japan inflation hits 2.3%; BoJ hike eyed",
     "Oct CPI up from 2.1%; core above 2%. (Reuters)", "bars"),
    (8, "BEIJING - RATES", "China holds lending rates for 18th month",
     "One-year LPR 3.0%, five-year 3.5%. (PBOC)", "bank"),
    (9, "WELLINGTON - CRICKET", "Phillips makes history with 118 vs India",
     "Centuries in all 3 formats vs India. (ICC, AP)", "cricket"),
    (10, "SAN SALVADOR - POLITICS", "Bukele registers for third-term bid",
     "Files for Feb 2027 vote; rights groups object. (AP)", "ballot"),
    (11, "SENEGAL - MIGRATION", "Migrant boat capsizes off Yemen; 4 dead",
     "Dozens missing from 50-100 aboard. (Al Jazeera)", "boat"),
    (12, "ROME - LABOUR", "Italy's CGIL holds 24-hr general strike",
     "Unions rally in 100 squares; transit hit. (AFP)", "strike"),
    (13, "BARCELONA - HEALTH", "Cancer pill shrinks tumours 60.7%",
     "Daraxonrasib plus chemo beats chemo alone. (Reuters)", "pill"),
]
ALSO = [
    (14, "NEW YORK", "Anthropic up 17% on debut ($97.17)"),
    (15, "WASHINGTON", "Senate rejects Iran bid, 51-48"),
    (16, "SHENZHEN", "Leaders issue peace declaration"),
    (17, "GAZA", "Aid groups score peace plan 4 of 26"),
    (18, "HORMUZ", "Four attacks on vessels in 96 hours"),
    (19, "WASHINGTON", "Pentagon: US war cost vs Iran $48.3bn"),
    (20, "LONDON", "UK, Norway fund GBP100m+ navy vessels"),
    (21, "COPENHAGEN", "Denmark OKs Greenland defence bill"),
    (22, "JAKARTA", "Indonesia OKs asset-forfeiture bill"),
    (23, "CINCINNATI", "Hippo Fiona dies after swallowing hat"),
    (24, "DAKAR", "Faye enacts budget by decree"),
    (25, "LAS VEGAS", "Russell fastest in wet F1 practice"),
    (26, "TURIN", "ATP Finals groups close, semis Sat"),
    (27, "LOS ANGELES", "Thomas Markle fit to stand trial"),
    (28, "TAIPEI", "TAIEX set for worst week since 1991"),
    (29, "HONG KONG", "Hang Seng about 20% off January peak"),
    (30, "SYDNEY", "General Pants enters administration"),
    (31, "CANBERRA", "CBO warns AUKUS sales shrink US fleet"),
    (32, "MALAWI", "Fuel crisis: 20L a day, petrol $3.24"),
    (33, "NEW DELHI", "Modi opens SCO civilisations forum"),
    (34, "FLORIDA", "St. Johns River hits record 18.3 ft"),
    (35, "QATAR", "U17: Austria stun Argentina 2-0"),
    (36, "SAO PAULO", "Markets shut for Consciousness Day"),
]
DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: "
              "the Trump-Xi-Putin Shenzhen summit itself - Anthropic's $83 "
              "IPO pricing - ICJ Myanmar Rohingya genocide verdict - GTA VI "
              "midnight launch - $190.4m Van Gogh sale - Voyager 1 one "
              "light-day confirmation - Senate 48-51 Iran war-powers vote "
              "- Crimean Bridge strike.")
PINS = [(85.8, 19.3), (30.5, 50.5), (30.7, 36.9), (127.0, 37.5), (0, 0),
        (4.4, 50.8), (139.7, 35.7), (116.4, 39.9), (174.8, -41.3),
        (-89.2, 13.7), (-17.4, 14.7), (12.5, 41.9), (2.2, 41.4)]
FOOTER1 = ("Every story here happened, or was first reported, on Friday "
           "20 November 2026 in at least one time zone. Claims are "
           "attributed, not stated as fact.")
FOOTER2 = ("Sources: Reuters - AP - AFP - BBC - The Hindu - IMD - UN News "
           "- Al Jazeera. Original vector drawings.")


# ------------------------------------------------------------ pictures
def art_cyclone(pg, x, y, w, h):
    pg.fill(x, y, w, h, (31, 68, 99))
    pg.fill(x, y + int(h * 0.58), w, h - int(h * 0.58), (44, 96, 140))
    pg.fill_poly([(x + int(w * 0.44), y), (x + int(w * 0.62), y + int(h * 0.32)),
                  (x + int(w * 0.58), y + int(h * 0.64)), (x + int(w * 0.68), y + h),
                  (x + w, y + h), (x + w, y)], (222, 206, 168))
    draw_text(pg, x + 10, y + 8, "BAY OF", 11, (226, 232, 238), bold=True)
    draw_text(pg, x + 10, y + 22, "BENGAL", 11, (226, 232, 238), bold=True)
    cx, cy = x + int(w * 0.26), y + int(h * 0.58)
    for r in (5, 9, 13, 17, 21):
        a0 = -0.4 * r / 6
        steps = int(r * 2)
        for i in range(steps):
            a = a0 + (4.6 - 0.4 * r / 6 - a0) * i / steps
            rr = r * (1 - i / steps * 0.35)
            pg.spot(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)), 2, WHITE)
    pg.spot(cx, cy, 5, WHITE)
    lx, ly = x + int(w * 0.56), y + int(h * 0.46)
    pg.spot(lx, ly, 6, RED)
    pg.circle(lx, ly, 10, RED, w=2)
    draw_text(pg, lx + 14, ly - 6, "GOPALPUR", 11, WHITE, bold=True)
    draw_text(pg, x + 10, y + h - 16, "8:30AM IST", 11, (226, 232, 238), bold=True)


def art_kyiv(pg, x, y, w, h):
    pg.fill(x, y, w, h, DARK)
    for sx, sy in ((0.08, 0.15), (0.2, 0.08), (0.36, 0.18), (0.55, 0.07),
                   (0.7, 0.16), (0.84, 0.08), (0.93, 0.2), (0.45, 0.22)):
        pg.spot(x + int(w * sx), y + int(h * sy), 1, (200, 210, 220))
    base = y + h
    for bx, bw, bh in ((0.0, 0.16, 0.34), (0.17, 0.12, 0.48), (0.30, 0.14, 0.40),
                       (0.45, 0.10, 0.55), (0.56, 0.15, 0.38),
                       (0.72, 0.12, 0.5), (0.85, 0.15, 0.42)):
        pg.fill(x + int(w * bx), base - int(h * bh), int(w * bw), int(h * bh), (24, 36, 58))
    for wx, wy in ((0.05, 0.72), (0.19, 0.62), (0.33, 0.68), (0.48, 0.55),
                   (0.60, 0.70), (0.75, 0.60), (0.88, 0.66), (0.22, 0.78)):
        pg.fill(x + int(w * wx), y + int(h * wy), 4, 5, GOLDL)
    pg.fill(x, base - 10, w, 10, (30, 62, 96))
    for mx, my, tx, ty in ((0.12, 0.06, 0.30, 0.52), (0.55, 0.02, 0.48, 0.62),
                           (0.88, 0.05, 0.76, 0.55)):
        pg.seg(x + int(w * mx), y + int(h * my), x + int(w * tx), y + int(h * ty),
               (255, 190, 90), w=2)
        pg.spot(x + int(w * tx), y + int(h * ty), 4, (255, 120, 40))
    for ex, ey in ((0.30, 0.52), (0.76, 0.55)):
        for dx, dy in ((0, -9), (7, -6), (9, 0), (7, 6), (0, 9), (-7, 6), (-9, 0), (-7, -6)):
            pg.seg(x + int(w * ex), y + int(h * ey), x + int(w * ex) + dx,
                   y + int(h * ey) + dy, (255, 200, 90), w=2)
        pg.spot(x + int(w * ex), y + int(h * ey), 4, (255, 220, 130))
    draw_text(pg, x + 10, y + 8, "3 BRIDGES HIT", 11, (255, 210, 160), bold=True)


def art_cop31(pg, x, y, w, h):
    pg.fill(x, y, w, h, (20, 62, 46))
    gx, gy, gr = x + int(w * 0.30), y + int(h * 0.52), int(h * 0.34)
    pg.spot(gx, gy, gr, (42, 110, 88))
    pg.circle(gx, gy, gr, (120, 200, 170), w=2)
    for k in range(-2, 3):
        a = k * 0.55
        pts = []
        for i in range(25):
            t = -1 + 2 * i / 24
            pts.append((gx + int(gr * math.cos(a) * math.sqrt(1 - t * t)),
                        gy + int(gr * t)))
        for a2, b2 in zip(pts, pts[1:]):
            pg.seg(a2[0], a2[1], b2[0], b2[1], (120, 200, 170), w=1)
    pg.seg(gx - gr, gy, gx + gr, gy, (120, 200, 170), w=1)
    pg.seg(gx, gy - gr, gx, gy + gr, (120, 200, 170), w=1)
    tx = x + int(w * 0.68)
    pg.fill(tx, y + int(h * 0.14), 12, int(h * 0.62), WHITE)
    pg.fill(tx + 3, y + int(h * 0.14), 6, int(h * 0.50), RED)
    pg.spot(tx + 6, y + int(h * 0.80), 11, RED)
    pg.spot(tx + 6, y + int(h * 0.80), 7, (255, 160, 140))
    draw_text(pg, tx + 20, y + int(h * 0.30), "+1.5C", 12, WHITE, bold=True)
    pg.fill(x, y + h - 26, w, 26, RED)
    draw_text(pg, x + w // 2, y + h - 18, "COP31", 13, WHITE, bold=True, align="c")


def art_chart(pg, x, y, w, h):
    pg.fill(x, y, w, h, (28, 38, 52))
    pts = [(x + int(w * k / 5), y + h - int(h * (0.25 + 0.14 * k))) for k in range(6)]
    for a, b in zip(pts, pts[1:]):
        pg.seg(a[0], a[1], b[0], b[1], (255, 110, 90), w=2)
    for px, py in pts:
        pg.spot(px, py, 3, (255, 150, 120))
    draw_text(pg, x + 8, y + 6, "TAIEX", 11, (255, 210, 190), bold=True)
    draw_text(pg, x + w - 8, y + 6, "-6.8%", 12, (255, 120, 100), bold=True, align="r")


def art_moon(pg, x, y, w, h):
    pg.fill(x, y, w, h, (18, 26, 44))
    for sx, sy in ((0.12, 0.2), (0.25, 0.12), (0.8, 0.16), (0.9, 0.3),
                   (0.6, 0.1), (0.15, 0.55)):
        pg.spot(x + int(w * sx), y + int(h * sy), 1, WHITE)
    pg.spot(x + int(w * 0.32), y + int(h * 0.55), 18, (208, 208, 196))
    pg.spot(x + int(w * 0.28), y + int(h * 0.5), 4, (170, 170, 160))
    pg.spot(x + int(w * 0.38), y + int(h * 0.62), 3, (170, 170, 160))
    draw_text(pg, x + int(w * 0.58), y + int(h * 0.28), "MERCURY", 11, WHITE, bold=True)
    draw_text(pg, x + int(w * 0.58), y + int(h * 0.52), "8 YRS", 12, GOLDL, bold=True)


def art_flags(pg, x, y, w, h):
    pg.fill(x, y, w, h, (24, 48, 84))
    cx, cy = x + int(w * 0.26), y + int(h * 0.5)
    pg.spot(cx, cy, 20, (0, 51, 153))
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        pg.spot(int(cx + 13 * math.cos(a)), int(cy + 13 * math.sin(a)), 2, (255, 204, 0))
    ux, uy, uw, uh = x + int(w * 0.60), y + int(h * 0.22), 34, 22
    pg.fill(ux, uy, uw, uh, (0, 36, 125))
    pg.seg(ux, uy, ux + uw, uy + uh, WHITE, w=2)
    pg.seg(ux + uw, uy, ux, uy + uh, WHITE, w=2)
    pg.fill(ux + uw // 2 - 3, uy, 6, uh, (200, 16, 46))
    pg.fill(ux, uy + uh // 2 - 3, uw, 6, (200, 16, 46))


def art_bars(pg, x, y, w, h):
    pg.fill(x, y, w, h, (250, 246, 236))
    pg.fill(x + 8, y + h - 6, w - 16, 2, (200, 192, 172))
    for i, bh in enumerate((0.35, 0.52, 0.72)):
        bx = x + 16 + i * 34
        pg.fill(bx, y + h - 8 - int(h * bh), 22, int(h * bh),
                NAVY if i < 2 else RED)
    draw_text(pg, x + w - 8, y + 6, "2.3%", 13, RED, bold=True, align="r")
    draw_text(pg, x + 8, y + 6, "CPI", 11, NAVY, bold=True)


def art_bank(pg, x, y, w, h):
    pg.fill(x, y, w, h, (240, 236, 224))
    bx, by, bw, bh = x + int(w * 0.18), y + int(h * 0.18), int(w * 0.64), int(h * 0.62)
    pg.fill_poly([(bx - 6, by), (bx + bw // 2, by - 12), (bx + bw + 6, by)], RED)
    pg.fill(bx, by, bw, 6, NAVY)
    for i in range(4):
        pg.fill(bx + 6 + i * (bw - 12) // 4, by + 6, 6, bh - 12, NAVY)
    pg.fill(bx, by + bh - 4, bw, 6, NAVY)
    draw_text(pg, x + w // 2, y + h - 14, "3.0% / 3.5%", 11, RED, bold=True, align="c")


def art_cricket(pg, x, y, w, h):
    pg.fill(x, y, w, h, (36, 92, 52))
    pg.seg(x + int(w * 0.30), y + int(h * 0.12), x + int(w * 0.52), y + int(h * 0.62),
           (210, 180, 130), w=5)
    pg.fill(x + int(w * 0.44), y + int(h * 0.58), 10, 22, (210, 180, 130))
    pg.spot(x + int(w * 0.70), y + int(h * 0.70), 7, (200, 60, 50))
    pg.spot(x + int(w * 0.70), y + int(h * 0.70), 3, (255, 220, 200))
    draw_text(pg, x + int(w * 0.76), y + int(h * 0.12), "118", 16, WHITE, bold=True)


def art_ballot(pg, x, y, w, h):
    pg.fill(x, y, w, h, (232, 238, 244))
    bx, by, bw, bh = x + int(w * 0.28), y + int(h * 0.34), int(w * 0.44), int(h * 0.44)
    pg.fill(bx, by, bw, bh, BLUE)
    pg.fill(bx + bw // 2 - 14, by - 8, 28, 8, INK)
    pg.seg(bx + 6, by + bh // 2, bx + bw // 2 - 4, by + bh - 6, WHITE, w=3)
    pg.seg(bx + bw // 2 - 4, by + bh - 6, bx + bw - 6, by + 6, WHITE, w=3)
    draw_text(pg, x + w // 2, y + 6, "VOTE 2027", 11, NAVY, bold=True, align="c")


def art_boat(pg, x, y, w, h):
    pg.fill(x, y, w, h, (186, 214, 228))
    pg.seg(x + int(w * 0.30), y + int(h * 0.08), x + int(w * 0.30), y + int(h * 0.42),
           (60, 50, 40), w=2)
    pg.fill_poly([(x + int(w * 0.30), y + int(h * 0.10)),
                  (x + int(w * 0.58), y + int(h * 0.38)),
                  (x + int(w * 0.30), y + int(h * 0.38))], (200, 220, 230))
    pg.fill_poly([(x + int(w * 0.12), y + int(h * 0.42)),
                  (x + int(w * 0.88), y + int(h * 0.42)),
                  (x + int(w * 0.78), y + int(h * 0.62)),
                  (x + int(w * 0.22), y + int(h * 0.62))], (90, 60, 40))
    for k, wy in enumerate((0.70, 0.82, 0.92)):
        for wx in range(0, w, 14):
            off = 3 if (wx // 14 + k) % 2 else 0
            pg.seg(x + wx, y + int(h * wy) + off, x + wx + 7,
                   y + int(h * wy) + off, BLUE, w=2)


def art_strike(pg, x, y, w, h):
    pg.fill(x, y, w, h, (250, 244, 230))
    for i, (px, ph) in enumerate(((0.16, 0.42), (0.48, 0.52), (0.78, 0.40))):
        sx = x + int(w * px)
        pg.seg(sx, y + int(h * ph) + 14, sx, y + h - 6, (80, 70, 60), w=3)
        pg.fill(sx - 18, y + int(h * ph), 36, 16, RED if i != 1 else NAVY)
        pg.seg(sx - 12, y + int(h * ph) + 4, sx - 12, y + int(h * ph) + 12, WHITE, w=2)
        pg.seg(sx - 12, y + int(h * ph) + 8, sx + 2, y + int(h * ph) + 8, WHITE, w=2)
    draw_text(pg, x + w // 2, y + 6, "24H", 12, RED, bold=True, align="c")


def art_pill(pg, x, y, w, h):
    pg.fill(x, y, w, h, (238, 246, 240))
    cx, cy = x + int(w * 0.5), y + int(h * 0.42)
    pg.seg(cx - 34, cy - 8, cx + 34, cy + 8, BLUE, w=16)
    pg.spot(cx - 34, cy - 8, 8, BLUE)
    pg.spot(cx + 34, cy + 8, 8, (255, 120, 90))
    pg.seg(cx - 30, cy - 6, cx + 30, cy + 6, WHITE, w=2)
    draw_text(pg, x + w // 2, y + h - 15, "60.7%", 12, TEAL, bold=True, align="c")


ARTS = {"cyclone": art_cyclone, "kyiv": art_kyiv, "cop31": art_cop31,
        "chart": art_chart, "moon": art_moon, "flags": art_flags,
        "bars": art_bars, "bank": art_bank, "cricket": art_cricket,
        "ballot": art_ballot, "boat": art_boat, "strike": art_strike,
        "pill": art_pill}


def draw_map(pg, x, y, w, h):
    pg.fill(x, y, w, h, SEA)
    pg.fill(x, y + int(h * 0.78), w, h - int(h * 0.78), (196, 210, 222))
    pg.fill_poly([(x + 26, y + 40), (x + 62, y + 28), (x + 92, y + 46),
                  (x + 78, y + 78), (x + 46, y + 86), (x + 24, y + 66)], LAND)
    pg.fill_poly([(x + 92, y + 112), (x + 128, y + 108), (x + 142, y + 132),
                  (x + 132, y + 176), (x + 108, y + 196), (x + 96, y + 150)], LAND)
    pg.fill_poly([(x + 218, y + 34), (x + 268, y + 26), (x + 292, y + 44),
                  (x + 280, y + 72), (x + 240, y + 84), (x + 214, y + 60)], LAND)
    pg.fill_poly([(x + 230, y + 100), (x + 268, y + 94), (x + 292, y + 112),
                  (x + 282, y + 158), (x + 256, y + 176), (x + 232, y + 142)], LAND)
    pg.fill_poly([(x + 320, y + 30), (x + 396, y + 22), (x + 428, y + 52),
                  (x + 412, y + 92), (x + 368, y + 112), (x + 330, y + 84),
                  (x + 312, y + 56)], LAND)
    pg.fill_poly([(x + 400, y + 180), (x + 430, y + 176), (x + 436, y + 196),
                  (x + 414, y + 210), (x + 396, y + 196)], LAND)
    draw_text(pg, x + 10, y + 8, "WORLD MAP - WHERE FRIDAY HAPPENED", 10, NAVY, bold=True)
    OFF = {2: (14, -10), 3: (18, 14), 4: (16, -12), 6: (-16, -8),
           7: (14, 12), 8: (-14, 10), 12: (10, 12), 13: (-12, 10)}
    for i, (lon, lat) in enumerate(PINS, 1):
        if lon == 0 and lat == 0:
            px, py = x + int(w * 0.28), y + int(h * 0.72)
        else:
            px = x + int((lon + 180) / 360 * w)
            py = y + int((90 - lat) / 180 * h)
        dx, dy = OFF.get(i, (0, 0))
        px += dx
        py += dy
        pg.spot(px, py, 8, RED)
        pg.circle(px, py, 8, WHITE, w=1)
        draw_text(pg, px, py - 5, str(i), 9, WHITE, bold=True, align="c")


# ------------------------------------------------------------- layout
def _card(pg, x, y, w, h):
    pg.fill(x, y, w, h, CREAM)
    pg.hrule(x, y, w, FAINT, 1)
    pg.hrule(x, y + h - 1, w, FAINT, 1)
    pg.vrule(x, y, h, FAINT, 1)
    pg.vrule(x + w - 1, y, h, FAINT, 1)


def build():
    pg = Page(SIZE, SIZE, PAPER)
    X, CW = 26, 972
    draw_text(pg, X, 8, "THE WORLD IN ONE DAY", 11, RED, bold=True)
    draw_text(pg, X + CW, 8, "FRIDAY'S NEWS - ONE PAGE - 36 STORIES - 6 CONTINENTS",
              11, INK, bold=True, align="r")
    draw_text(pg, X + CW // 2, 26, MASTHEAD, 42, INK, bold=True, align="c")
    pg.hrule(X, 80, CW, INK, 3)
    pg.hrule(X, 84, CW, INK, 1)
    draw_text(pg, X + CW // 2, 90, SUBHEAD, 12, RED, bold=True, align="c")
    # numbers band: number on top, label below, generous line height
    pg.fill(X, 108, CW, 54, CREAM)
    pg.hrule(X, 108, CW, INK, 1)
    pg.hrule(X, 161, CW, INK, 1)
    for i, (num, lab) in enumerate(NUMBERS):
        cx0 = X + i * 162
        if i:
            pg.vrule(cx0, 112, 46, FAINT, 1)
        draw_text(pg, cx0 + 81, 111, num, 21, RED, bold=True, align="c")
        draw_para(pg, cx0 + 6, 137, lab, 8.5, 150, INK, lh=11, max_lines=2,
                  align="c")
    # region chips, centred
    widths = [int(text_width("%s %d" % (name, n), 10)) + 16 for name, n, _ in CHIPS]
    total = sum(widths) + 8 * (len(CHIPS) - 1)
    cx = X + (CW - total) // 2
    for (name, n, col), wd in zip(CHIPS, widths):
        pg.fill(cx, 168, wd, 20, col)
        draw_text(pg, cx + wd // 2, 173, "%s %d" % (name, n), 10, WHITE,
                  bold=True, align="c")
        cx += wd + 8
    # three lead cards
    for i, (num, kicker, head, summ, art) in enumerate(LEADS):
        x, y, w, h = X + i * 328, 196, 316, 216
        _card(pg, x, y, w, h)
        ARTS[art](pg, x + 6, y + 6, w - 12, 92)
        badge_num(pg, x + 8, y + 106, num)
        draw_text(pg, x + 30, y + 108, kicker, 9.5, RED, bold=True)
        draw_para(pg, x + 10, y + 126, head, 15, w - 20, INK, bold=True,
                  lh=19, max_lines=2)
        draw_para(pg, x + 10, y + 168, summ, 10, w - 20, INK, lh=14,
                  max_lines=3)
    # ten feature cards, 2 rows x 5
    xs = [26, 222, 418, 614, 810]
    for r in range(2):
        for c in range(5):
            num, kicker, head, summ, art = FEATURES[r * 5 + c]
            x, y, w, h = xs[c], 424 + r * 132, 188, 124
            _card(pg, x, y, w, h)
            ARTS[art](pg, x + 4, y + 4, w - 8, 38)
            draw_text(pg, x + 7, y + 48, kicker, 8, RED, bold=True)
            draw_para(pg, x + 7, y + 60, head, 11, w - 14, INK, bold=True,
                      lh=14, max_lines=2)
            draw_para(pg, x + 7, y + 90, summ, 8.5, w - 14, (60, 60, 60),
                      lh=11.5, max_lines=2)
    # world map (left) and ALSO list (right), one line per story
    _card(pg, 26, 692, 462, 222)
    draw_map(pg, 32, 698, 450, 210)
    _card(pg, 500, 692, 498, 222)
    draw_text(pg, 508, 700, "ALSO ON FRIDAY 20 NOVEMBER - 23 MORE STORIES",
              11, NAVY, bold=True)
    for i, (num, city, text) in enumerate(ALSO):
        col, row = divmod(i, 12)
        cx0 = 508 + col * 245
        y0 = 720 + row * 16
        line = "%d %s: %s" % (num, city, text)
        while text_width(line, 8) > 240 and len(text) > 10:
            text = text[:-1]
            line = "%d %s: %s..." % (num, city, text)
        draw_text(pg, cx0, y0, line, 8, INK)
    # date check
    pg.fill(X, 922, CW, 56, CREAM)
    pg.hrule(X, 922, CW, RED, 2)
    pg.hrule(X, 976, CW, RED, 2)
    pg.vrule(X, 922, 56, RED, 2)
    pg.vrule(X + CW - 2, 922, 56, RED, 2)
    draw_text(pg, X + 10, 944, "DATE CHECK", 10, RED, bold=True)
    draw_para(pg, X + 100, 930, DATE_CHECK, 9.5, CW - 110, INK, lh=12,
              max_lines=3)
    # footer
    draw_para(pg, X, 984, FOOTER1, 9.5, CW, GREY, lh=12, max_lines=1)
    draw_text(pg, X, 1002, FOOTER2, 9.5, GREY)
    return pg


def main():
    pg = build()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(write_png(pg))


if __name__ == "__main__":
    main()
