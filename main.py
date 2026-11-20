#!/usr/bin/env python3
"""news-image-20261120 — Sum up 20 November's world news in one image.

Draws a one-page newspaper front page (1024x1024 PNG) from the day's real
news, using only the Python standard library. No network, no fonts on disk:
every letter is drawn from a small vector stroke font defined below, and the
PNG is encoded by hand (zlib + struct). Fully deterministic: two runs write
byte-identical files.

Usage: python3 main.py   (writes entry.png to $MAKEFUN_OUTPUT_DIR, else the current directory)
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER   = (247, 242, 230)
INK     = (26, 26, 26)
NAVY    = (21, 42, 69)
NAVY2   = (28, 56, 92)
GOLD    = (200, 162, 74)
GOLD_L  = (226, 196, 120)
RED     = (179, 53, 43)
BLUE    = (43, 95, 138)
TEAL    = (47, 125, 109)
CREAM   = (255, 253, 246)
BORDER  = (216, 208, 189)
GREY    = (110, 105, 92)
ORANGE  = (214, 110, 44)
GREEN   = (74, 124, 74)
PURPLE  = (112, 84, 150)
SKY     = (214, 228, 238)
SEA     = (206, 219, 228)
LAND    = (232, 222, 196)
WHITE   = (255, 255, 255)
BLACK   = (10, 10, 14)

# ------------------------------------------------------- vector stroke font
# Grid: x 0..8, y 0..10, baseline y=10. Strokes are polylines "x,y x,y ...",
# separated by "|". All text on the poster is uppercase by design.
FONT = {
    "A": "0,10 4,0 8,10|2,7 6,7",
    "B": "0,10 0,0 5,0 7,2 7,4 5,5 0,5|5,5 7,6 7,8 5,10 0,10",
    "C": "7,2 5,0 2,0 0,2 0,8 2,10 5,10 7,8",
    "D": "0,10 0,0 5,0 7,2 7,8 5,10 0,10",
    "E": "7,0 0,0 0,10 7,10|0,5 5,5",
    "F": "0,10 0,0 7,0|0,5 5,5",
    "G": "7,2 5,0 2,0 0,2 0,8 2,10 5,10 7,8 7,5 4,5",
    "H": "0,10 0,0|8,10 8,0|0,5 8,5",
    "I": "4,0 4,10|1,0 7,0|1,10 7,10",
    "J": "7,0 7,8 5,10 2,10 1,8",
    "K": "0,10 0,0|7,0 0,5 7,10",
    "L": "0,0 0,10 7,10",
    "M": "0,10 0,0 4,6 8,0 8,10",
    "N": "0,10 0,0 8,10 8,0",
    "O": "2,0 6,0 8,2 8,8 6,10 2,10 0,8 0,2 2,0",
    "P": "0,10 0,0 6,0 8,2 8,4 6,6 0,6",
    "Q": "2,0 6,0 8,2 8,8 6,10 2,10 0,8 0,2 2,0|5,8 8,11",
    "R": "0,10 0,0 6,0 8,2 8,4 6,6 0,6|5,6 8,10",
    "S": "7,2 5,0 2,0 0,2 0,4 2,5 6,5 8,6 8,8 6,10 3,10 1,8",
    "T": "0,0 8,0|4,0 4,10",
    "U": "0,0 0,8 2,10 6,10 8,8 8,0",
    "V": "0,0 4,10 8,0",
    "W": "0,0 2,10 4,5 6,10 8,0",
    "X": "0,0 8,10|8,0 0,10",
    "Y": "0,0 4,5 8,0|4,5 4,10",
    "Z": "0,0 8,0 0,10 8,10",
    "0": "2,0 6,0 8,2 8,8 6,10 2,10 0,8 0,2 2,0|2,8 6,2",
    "1": "3,1 4,0 4,10|2,10 6,10",
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
    "–": "0,5 8,5",
    "—": "0,5 8,5",
    "·": "3,4 4,4",
    "•": "3,4 5,4 5,6 3,6 3,4",
    "(": "6,0 3,2 3,8 6,10",
    ")": "2,0 5,2 5,8 2,10",
    "!": "4,0 4,7|4,9 4,10",
    "?": "1,2 2,0 6,0 7,2 7,4 5,6 4,7 4,8|4,9 4,10",
    "$": "4,0 4,11|7,2 5,0 2,0 0,2 0,4 2,5 6,5 8,6 8,8 6,10 3,10 1,8",
    "%": "7,0 1,10|2,1 4,1 4,3 2,3|6,7 8,7 8,9 6,9",
    "/": "7,0 1,10",
    "+": "4,2 4,8|1,5 7,5",
    "°": "3,0 5,0 5,2 3,2 3,0",
    " ": "",
}
NARROW = {".": 4, ",": 4, ":": 4, ";": 4, "'": 3, '"': 6, "!": 4, "(": 5,
          ")": 5, "-": 6, "–": 8, "—": 8, "·": 4, "•": 6, "/": 6, "1": 6,
          "I": 5, "°": 6, "%": 10, "$": 8, "?": 8}
WIDE = {"M": 10, "W": 10, "O": 9, "Q": 9, "G": 9, "D": 9, "0": 9, "8": 9}


def adv(ch):
    if ch in NARROW:
        return NARROW[ch]
    if ch in WIDE:
        return WIDE[ch]
    return 8


def text_w(s, sc):
    return sum(adv(c) for c in s) * sc + max(0, len(s) - 1) * sc * 0.12


def parse_font():
    out = {}
    for ch, spec in FONT.items():
        strokes = []
        if spec:
            for st in spec.split("|"):
                pts = []
                for tok in st.split():
                    x, y = tok.split(",")
                    pts.append((int(x), int(y)))
                strokes.append(pts)
        out[ch] = strokes
    return out


GLYPHS = parse_font()

# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def _set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def dot(self, cx, cy, r, c):
        r = int(r)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self._set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        self.dot(int(cx), int(cy), int(r), c)

    def line(self, x0, y0, x1, y1, c, w=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        half = w // 2
        while True:
            if w == 2:
                for yy in range(y, y + 2):
                    for xx in range(x, x + 2):
                        self._set(xx, yy, c)
            else:
                for yy in range(y - half, y + half + 1):
                    for xx in range(x - half, x + half + 1):
                        self._set(xx, yy, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def poly(self, pts, c):
        # filled polygon, scanline even-odd
        pts = [(int(x), int(y)) for x, y in pts]
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                xa, xb = int(nodes[k]), int(nodes[k + 1])
                for x in range(max(0, xa), min(self.w, xb + 1)):
                    self._set(x, y, c)

    def ring(self, cx, cy, r, c, w=2):
        steps = max(24, int(2 * math.pi * r))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            self.dot(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), w, c)


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ------------------------------------------------------- lowercase glyphs
# Same 0..8 x grid as FONT; x-height band y=4..10, baseline y=10,
# descenders to y=13. My own stroke designs, drawn for small body text.
LOW = {
    'a': [[(8, 4), (8, 10)], [(8, 5), (6, 4), (3, 4), (1, 6), (1, 8), (3, 10), (6, 10), (8, 8)]],
    'b': [[(1, 0), (1, 10)], [(1, 4), (4, 4), (7, 5), (8, 7), (8, 9), (6, 10), (3, 10), (1, 8)]],
    'c': [[(8, 5), (6, 4), (3, 4), (1, 6), (1, 8), (3, 10), (6, 10), (8, 9)]],
    'd': [[(8, 0), (8, 10)], [(8, 4), (5, 4), (2, 5), (1, 7), (1, 9), (3, 10), (6, 10), (8, 8)]],
    'e': [[(8, 7), (6, 4), (3, 4), (1, 6), (1, 8), (3, 10), (6, 10), (8, 8)], [(1, 7), (8, 7)]],
    'f': [[(6, 0), (4, 1), (3, 3), (3, 10)], [(1, 4), (7, 4)]],
    'g': [[(2, 5), (5, 4), (7, 4), (8, 6), (8, 8), (6, 10), (3, 10), (1, 8), (1, 6), (2, 5)],
          [(8, 4), (8, 10), (6, 12), (3, 12), (1, 10)]],
    'h': [[(1, 0), (1, 10)], [(1, 4), (4, 4), (7, 5), (8, 7), (8, 10)]],
    'i': [[(4, 4), (4, 10)], [(4, 1), (4, 1)]],
    'j': [[(6, 4), (6, 10), (4, 12), (2, 12), (1, 10)], [(6, 1), (6, 1)]],
    'k': [[(1, 0), (1, 10)], [(8, 4), (2, 8)], [(4, 9), (8, 10)]],
    'l': [[(4, 0), (4, 10)]],
    'm': [[(1, 10), (1, 4), (4, 4), (5, 7), (5, 10)], [(5, 4), (7, 4), (8, 6), (8, 10)]],
    'n': [[(1, 10), (1, 4), (4, 4), (7, 5), (8, 7), (8, 10)]],
    'o': [[(2, 4), (5, 4), (7, 5), (8, 7), (8, 9), (6, 10), (3, 10), (1, 9), (1, 7), (2, 4)]],
    'p': [[(1, 4), (1, 12)], [(1, 4), (4, 4), (7, 5), (8, 7), (8, 9), (6, 10), (3, 10), (1, 8)]],
    'q': [[(8, 4), (8, 12)], [(8, 4), (5, 4), (2, 5), (1, 7), (1, 9), (3, 10), (6, 10), (8, 8)]],
    'r': [[(1, 10), (1, 4)], [(1, 4), (5, 4), (7, 6), (8, 8)]],
    's': [[(7, 5), (5, 4), (2, 4), (1, 6), (1, 7), (2, 9), (5, 9), (7, 10), (8, 9)]],
    't': [[(5, 0), (5, 10)], [(2, 3), (7, 3)], [(5, 10), (7, 9)]],
    'u': [[(1, 4), (1, 8), (3, 10), (6, 10), (8, 8), (8, 4)]],
    'v': [[(1, 4), (4, 10), (8, 4)]],
    'w': [[(1, 4), (2.5, 10), (4.5, 7), (6.5, 10), (8, 4)]],
    'x': [[(1, 4), (8, 10)], [(8, 4), (1, 10)]],
    'y': [[(1, 4), (4, 9), (8, 4)], [(4, 9), (4, 12), (2, 13)]],
    'z': [[(1, 4), (8, 4), (1, 10), (8, 10)]],
}
LOW_ADV = {'i': 3.5, 'l': 3.5, 'j': 4.0, 't': 4.5, 'f': 4.5, 'r': 5.0}


def _aw(ch):
    """Advance width of one character, in font grid units."""
    if ch == ' ':
        return 4.0
    if ch.islower():
        return LOW_ADV.get(ch, 7.0)
    return adv(ch)


def tw(s, size):
    """Pixel width of string s at cap-height size."""
    sc = size / 10.0
    return sum(_aw(c) for c in s) * sc + max(0, len(s) - 1) * sc * 0.15


def draw_text(cv, x, y, s, size, color, bold=False, align='l'):
    """Draw string s with cap-top at y. align l/c/r relative to x."""
    if align == 'c':
        x -= tw(s, size) / 2
    elif align == 'r':
        x -= tw(s, size)
    sc = size / 10.0
    if bold:
        lw = max(2, int(size * 0.11)) if size <= 16 else int(size * 0.11)
    else:
        lw = 2 if size <= 13 else max(1, int(size * 0.075))
    cx = float(x)
    for ch in s:
        if ch == ' ':
            cx += _aw(ch) * sc + sc * 0.15
            continue
        if ch.islower() and ch in LOW:
            strokes = LOW[ch]
        elif ch in GLYPHS and GLYPHS[ch]:
            strokes = GLYPHS[ch]
        elif ch.upper() in GLYPHS and GLYPHS[ch.upper()]:
            strokes = GLYPHS[ch.upper()]
        else:
            cx += _aw(ch) * sc + sc * 0.15
            continue
        for st in strokes:
            if len(st) == 1:
                px, py = st[0]
                cv.dot(int(round(cx + px * sc)), int(round(y + py * sc)),
                       max(1, lw // 2), color)
            else:
                for a, b in zip(st, st[1:]):
                    cv.line(cx + a[0] * sc, y + a[1] * sc,
                            cx + b[0] * sc, y + b[1] * sc, color, w=lw)
        cx += _aw(ch) * sc + sc * 0.15
    return cx


def wrap(s, size, max_w):
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if tw(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, size, max_w, color, bold=False, lh=None,
              max_lines=None):
    lines = wrap(s, size, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = lh or int(size * 1.35)
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * lh, ln, size, color, bold=bold)
    return y + len(lines) * lh


def circ_num(cv, x, y, n, r=7, bg=RED, fg=WHITE, size=10):
    cv.disc(x + r, y + r, r, bg)
    cv.ring(x + r, y + r, r, fg, w=1)
    draw_text(cv, x + r, y + r - size // 2, str(n), size, fg, bold=True,
              align='c')


def hline(cv, x, y, w, c=INK, t=2):
    cv.rect(x, y, w, t, c)


def vline(cv, x, y, h, c=BORDER, t=1):
    cv.rect(x, y, t, h, c)

# ------------------------------------------------------------- story data
# Every story below happened, or was first reported, on Friday 20 November
# 2026 in at least one time zone. Figures are as reported by the outlet
# named in each summary; disputed claims are labelled CLAIM or FORECAST.
MASTHEAD = "Friday 20 November 2026"
SUBHEAD = ("Akvan strikes India  \u2022  Missiles hit Kyiv  \u2022  COP31 "
           "deadlocked  \u2022  Asian AI sell-off")
NUMBERS = [
    ("370,000", "evacuated ahead of Akvan"),
    ("3", "3 killed; 3 bridges hit"),
    ("-6.8%", "TAIEX intraday low"),
    ("2.3%", "Japan Oct headline CPI"),
    ("118", "Phillips makes history"),
    ("8 yrs", "BepiColombo to Mercury"),
]
CHIPS = [("EUROPE", 8, NAVY2), ("AMERICAS", 8, RED), ("ASIA-PACIFIC", 9, TEAL),
         ("MIDEAST", 4, ORANGE), ("AFRICA", 3, GREEN), ("OCEANIA", 3, PURPLE),
         ("WORLD", 1, INK)]
# (num, kicker, headline, summary, art)
LEADS = [
    (1, "ODISHA, INDIA \u00b7 CYCLONE", "Cyclone Akvan makes landfall in eastern India",
     "Crosses near Gopalpur at 8:30am IST, winds 70-80 km/h gusting 90; "
     "370,000 evacuated, no major damage. (IMD)",
     "cyclone"),
    (2, "KYIV, UKRAINE \u00b7 WAR", "Russia fires wave of ballistic missiles at Kyiv",
     "Overnight barrage kills 3, injures 15; three Dnipro bridges hit in "
     "the biggest bridge attack of the war. (Reuters)",
     "kyiv"),
    (3, "ANTALYA, TURKIYE · CLIMATE", "COP31 reaches final day deadlocked",
     "Draft omits fossil-fuel phase-out; $120bn adaptation finance "
     "unresolved as hosts push a \u201935 by 35\u2019 clean power. (UN News)", "cop31"),
]
FEATURES = [
    (4, "SEOUL \u00b7 TOKYO \u00b7 MARKETS", "AI sell-off: Asia's worst week since 2020",
     "Nikkei -4.9%, KOSPI -5.4%, TAIEX -6.8% (Reuters)", "chart"),
    (5, "SPACE", "BepiColombo reaches Mercury in 8 years",
     "ESA-JAXA probe ends 6bn-mile trip. (ESA, BBC)", "moon"),
    (6, "BRUSSELS \u00b7 EUROPE", "Burnham holds first EU-UK reset summit",
     "Costa and von der Leyen host UK PM. (EU Council)", "flags"),
    (7, "TOKYO \u00b7 ECONOMY", "Japan inflation hits 2.3%; BoJ hike eyed",
     "Oct CPI up from 2.1%; core above 2%. (Reuters)", "bars"),
    (8, "BEIJING \u00b7 RATES", "China holds lending rates for 18th month",
     "One-year LPR 3.0%, five-year 3.5%. (PBOC)", "bank"),
    (9, "WELLINGTON \u00b7 CRICKET", "Phillips makes history with 118 vs India",
     "Centuries in all 3 formats vs India. (ICC, AP)", "cricket"),
    (10, "SAN SALVADOR \u00b7 POLITICS", "Bukele registers for third-term bid",
     "Files for Feb 2027 vote; rights groups object. (AP)", "ballot"),
    (11, "SENEGAL \u00b7 MIGRATION", "Migrant boat capsizes off Yemen; 4 dead",
     "Dozens missing from 50-100 aboard. (Al Jazeera)", "boat"),
    (12, "ROME \u00b7 LABOUR", "Italy\u2019s CGIL holds 24-hr general strike",
     "Unions rally in 100 squares; transit hit. (AFP)", "strike"),
    (13, "BARCELONA \u00b7 HEALTH", "Cancer pill shrinks tumours 60.7%",
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
DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday\u2019s news: "
              "the Trump\u2013Xi\u2013Putin Shenzhen summit itself \u00b7 Anthropic\u2019s $83 "
              "IPO pricing \u00b7 ICJ Myanmar Rohingya genocide verdict \u00b7 GTA VI "
              "midnight launch \u00b7 $190.4m Van Gogh sale \u00b7 Voyager 1 one "
              "light-day confirmation \u00b7 Senate 48\u201351 Iran war-powers vote "
              "\u00b7 Crimean Bridge strike.")
# (lon, lat) for stories 1-13, in story order, for the map pins.
PINS = [(85.8, 19.3), (30.5, 50.5), (30.7, 36.9), (127.0, 37.5), (0, 0),
        (4.4, 50.8), (139.7, 35.7), (116.4, 39.9), (174.8, -41.3),
        (-89.2, 13.7), (-17.4, 14.7), (12.5, 41.9), (2.2, 41.4)]

# ------------------------------------------------------------ illustrations
def art_cyclone(cv, x, y, w, h):
    cv.rect(x, y, w, h, (31, 68, 99))
    cv.rect(x, y + int(h * 0.55), w, h - int(h * 0.55), (43, 95, 138))
    # coastline: India's east coast, sand polygon
    cv.poly([(x + int(w * 0.42), y), (x + int(w * 0.62), y + int(h * 0.30)),
             (x + int(w * 0.58), y + int(h * 0.62)), (x + int(w * 0.66), y + h),
             (x + w, y + h), (x + w, y)], (222, 206, 168))
    draw_text(cv, x + 12, y + 8, "BAY OF", 12, (226, 232, 238), bold=True)
    draw_text(cv, x + 12, y + 22, "BENGAL", 12, (226, 232, 238), bold=True)
    # cyclone spiral, centred offshore
    cx, cy = x + int(w * 0.27), y + int(h * 0.60)
    for r in (5, 9, 13, 17, 21):
        a0, a1 = -0.4 * r / 6, 4.6 - 0.4 * r / 6
        steps = int(r * 2)
        for i in range(steps):
            a = a0 + (a1 - a0) * i / steps
            rr = r * (1 - i / steps * 0.35)
            cv.dot(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)),
                   2, WHITE)
    cv.disc(cx, cy, 5, WHITE)
    # landfall marker on the coast
    lx, ly = x + int(w * 0.56), y + int(h * 0.46)
    cv.disc(lx, ly, 6, RED)
    cv.ring(lx, ly, 10, RED, w=2)
    draw_text(cv, lx + 14, ly - 6, "GOPALPUR", 11, WHITE, bold=True)
    draw_text(cv, x + 12, y + h - 16, "8:30AM IST", 11, (226, 232, 238),
              bold=True)


def art_kyiv(cv, x, y, w, h):
    cv.rect(x, y, w, h, (13, 22, 40))
    # stars
    for sx, sy in ((0.08, 0.15), (0.2, 0.08), (0.36, 0.18), (0.55, 0.07),
                   (0.7, 0.16), (0.84, 0.08), (0.93, 0.2), (0.45, 0.22)):
        cv.dot(x + int(w * sx), y + int(h * sy), 1, (200, 210, 220))
    # skyline silhouettes
    base = y + h
    for bx, bw, bh in ((0.0, 0.16, 0.34), (0.17, 0.12, 0.48), (0.30, 0.14, 0.40),
                       (0.45, 0.10, 0.55), (0.56, 0.15, 0.38),
                       (0.72, 0.12, 0.5), (0.85, 0.15, 0.42)):
        cv.rect(x + int(w * bx), base - int(h * bh), int(w * bw), int(h * bh),
                (24, 36, 58))
    # lit windows
    for wx, wy in ((0.05, 0.72), (0.19, 0.62), (0.33, 0.68), (0.48, 0.55),
                   (0.60, 0.70), (0.75, 0.60), (0.88, 0.66), (0.22, 0.78)):
        cv.rect(x + int(w * wx), y + int(h * wy), 4, 5, GOLD_L)
    # river band
    cv.rect(x, base - 10, w, 10, (30, 62, 96))
    # missile trails
    for (mx, my, tx, ty) in ((0.12, 0.06, 0.30, 0.52), (0.55, 0.02, 0.48, 0.62),
                             (0.88, 0.05, 0.76, 0.55)):
        cv.line(x + int(w * mx), y + int(h * my), x + int(w * tx),
                y + int(h * ty), (255, 190, 90), w=2)
        cv.disc(x + int(w * tx), y + int(h * ty), 4, (255, 120, 40))
    # explosion bursts
    for ex, ey in ((0.30, 0.52), (0.76, 0.55)):
        for dx, dy in ((0, -9), (7, -6), (9, 0), (7, 6), (0, 9), (-7, 6),
                       (-9, 0), (-7, -6)):
            cv.line(x + int(w * ex), y + int(h * ey),
                    x + int(w * ex) + dx, y + int(h * ey) + dy,
                    (255, 200, 90), w=2)
        cv.disc(x + int(w * ex), y + int(h * ey), 4, (255, 220, 130))
    draw_text(cv, x + 12, y + 8, "3 BRIDGES HIT", 11, (255, 210, 160),
              bold=True)


def art_cop31(cv, x, y, w, h):
    cv.rect(x, y, w, h, (20, 62, 46))
    # globe
    gx, gy, gr = x + int(w * 0.30), y + int(h * 0.52), int(h * 0.34)
    cv.disc(gx, gy, gr, (42, 110, 88))
    cv.ring(gx, gy, gr, (120, 200, 170), w=2)
    for k in range(-2, 3):
        a = k * 0.55
        pts = []
        for i in range(25):
            t = -1 + 2 * i / 24
            px = gx + int(gr * math.cos(a) * math.sqrt(1 - t * t))
            py = gy + int(gr * t)
            pts.append((px, py))
        for a2, b2 in zip(pts, pts[1:]):
            cv.line(a2[0], a2[1], b2[0], b2[1], (120, 200, 170), w=1)
    cv.line(gx - gr, gy, gx + gr, gy, (120, 200, 170), w=1)
    cv.line(gx, gy - gr, gx, gy + gr, (120, 200, 170), w=1)
    # thermometer
    tx = x + int(w * 0.68)
    cv.rect(tx, y + int(h * 0.14), 12, int(h * 0.62), WHITE)
    cv.rect(tx + 3, y + int(h * 0.14), 6, int(h * 0.50), RED)
    cv.disc(tx + 6, y + int(h * 0.80), 11, RED)
    cv.disc(tx + 6, y + int(h * 0.80), 7, (255, 160, 140))
    draw_text(cv, tx + 20, y + int(h * 0.30), "+1.5C", 12, WHITE, bold=True)
    # banner
    cv.rect(x, y + h - 26, w, 26, (179, 53, 43))
    draw_text(cv, x + w // 2, y + h - 18, "COP31", 13, WHITE, bold=True,
              align='c')


def art_chart(cv, x, y, w, h):
    cv.rect(x, y, w, h, (28, 38, 52))
    pts = [(x + int(w * k / 5), y + h - int(h * (0.25 + 0.14 * k)))
           for k in range(6)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], (255, 110, 90), w=2)
    for px, py in pts:
        cv.disc(px, py, 3, (255, 150, 120))
    draw_text(cv, x + 8, y + 6, "TAIEX", 11, (255, 210, 190), bold=True)
    draw_text(cv, x + w - 8, y + 6, "-6.8%", 12, (255, 120, 100), bold=True,
              align='r')


def art_moon(cv, x, y, w, h):
    cv.rect(x, y, w, h, (18, 26, 44))
    for sx, sy in ((0.12, 0.2), (0.25, 0.12), (0.8, 0.16), (0.9, 0.3),
                   (0.6, 0.1), (0.15, 0.55)):
        cv.dot(x + int(w * sx), y + int(h * sy), 1, WHITE)
    cv.disc(x + int(w * 0.32), y + int(h * 0.55), 18, (208, 208, 196))
    cv.disc(x + int(w * 0.28), y + int(h * 0.5), 4, (170, 170, 160))
    cv.disc(x + int(w * 0.38), y + int(h * 0.62), 3, (170, 170, 160))
    draw_text(cv, x + int(w * 0.58), y + int(h * 0.28), "MERCURY", 11,
              WHITE, bold=True)
    draw_text(cv, x + int(w * 0.58), y + int(h * 0.52), "8 YRS", 12, GOLD_L,
              bold=True)


def art_flags(cv, x, y, w, h):
    cv.rect(x, y, w, h, (24, 48, 84))
    # EU flag: blue field, circle of gold stars
    cx, cy = x + int(w * 0.26), y + int(h * 0.5)
    cv.disc(cx, cy, 20, (0, 51, 153))
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        cv.dot(int(cx + 13 * math.cos(a)), int(cy + 13 * math.sin(a)), 2,
               (255, 204, 0))
    # UK flag: simplified union jack
    ux, uy, uw, uh = x + int(w * 0.60), y + int(h * 0.22), 34, 22
    cv.rect(ux, uy, uw, uh, (0, 36, 125))
    cv.line(ux, uy, ux + uw, uy + uh, WHITE, w=2)
    cv.line(ux + uw, uy, ux, uy + uh, WHITE, w=2)
    cv.rect(ux + uw // 2 - 3, uy, 6, uh, (200, 16, 46))
    cv.rect(ux, uy + uh // 2 - 3, uw, 6, (200, 16, 46))


def art_bars(cv, x, y, w, h):
    cv.rect(x, y, w, h, (250, 246, 236))
    cv.rect(x + 8, y + h - 6, w - 16, 2, (200, 192, 172))
    for i, bh in enumerate((0.35, 0.52, 0.72)):
        bw = 22
        bx = x + 16 + i * 34
        cv.rect(bx, y + h - 8 - int(h * bh), bw, int(h * bh),
                (21, 42, 69) if i < 2 else RED)
    draw_text(cv, x + w - 8, y + 6, "2.3%", 13, RED, bold=True, align='r')
    draw_text(cv, x + 8, y + 6, "CPI", 11, NAVY, bold=True)


def art_bank(cv, x, y, w, h):
    cv.rect(x, y, w, h, (240, 236, 224))
    bx, by, bw, bh = x + int(w * 0.18), y + int(h * 0.18), int(w * 0.64), int(h * 0.62)
    cv.poly([(bx - 6, by), (bx + bw // 2, by - 12), (bx + bw + 6, by)],
            (179, 53, 43))
    cv.rect(bx, by, bw, 6, NAVY)
    for i in range(4):
        cv.rect(bx + 6 + i * (bw - 12) // 4, by + 6, 6, bh - 12, NAVY)
    cv.rect(bx, by + bh - 4, bw, 6, NAVY)
    draw_text(cv, x + w // 2, y + h - 14, "3.0% / 3.5%", 11, RED, bold=True,
              align='c')


def art_cricket(cv, x, y, w, h):
    cv.rect(x, y, w, h, (36, 92, 52))
    cv.line(x + int(w * 0.30), y + int(h * 0.12), x + int(w * 0.52),
            y + int(h * 0.62), (210, 180, 130), w=5)
    cv.rect(x + int(w * 0.44), y + int(h * 0.58), 10, 22, (210, 180, 130))
    cv.disc(x + int(w * 0.70), y + int(h * 0.70), 7, (200, 60, 50))
    cv.disc(x + int(w * 0.70), y + int(h * 0.70), 3, (255, 220, 200))
    draw_text(cv, x + int(w * 0.76), y + int(h * 0.12), "118", 16, WHITE,
              bold=True)


def art_ballot(cv, x, y, w, h):
    cv.rect(x, y, w, h, (232, 238, 244))
    bx, by, bw, bh = x + int(w * 0.28), y + int(h * 0.34), int(w * 0.44), int(h * 0.44)
    cv.rect(bx, by, bw, bh, (43, 95, 138))
    cv.rect(bx + bw // 2 - 14, by - 8, 28, 8, INK)
    cv.line(bx + 6, by + bh // 2, bx + bw // 2 - 4, by + bh - 6, WHITE, w=3)
    cv.line(bx + bw // 2 - 4, by + bh - 6, bx + bw - 6, by + 6, WHITE, w=3)
    draw_text(cv, x + w // 2, y + 6, "VOTE 2027", 11, NAVY, bold=True,
              align='c')


def art_boat(cv, x, y, w, h):
    cv.rect(x, y, w, h, (186, 214, 228))
    cv.line(x + int(w * 0.30), y + int(h * 0.08), x + int(w * 0.30),
            y + int(h * 0.42), (60, 50, 40), w=2)
    cv.poly([(x + int(w * 0.30), y + int(h * 0.10)),
             (x + int(w * 0.58), y + int(h * 0.38)),
             (x + int(w * 0.30), y + int(h * 0.38))], (200, 220, 230))
    cv.poly([(x + int(w * 0.12), y + int(h * 0.42)),
             (x + int(w * 0.88), y + int(h * 0.42)),
             (x + int(w * 0.78), y + int(h * 0.62)),
             (x + int(w * 0.22), y + int(h * 0.62))], (90, 60, 40))
    for k, wy in enumerate((0.70, 0.82, 0.92)):
        for wx in range(0, w, 14):
            cv.line(x + wx, y + int(h * wy) + (3 if (wx // 14 + k) % 2 else 0),
                    x + wx + 7, y + int(h * wy) + (3 if (wx // 14 + k) % 2 else 0),
                    (43, 95, 138), w=2)


def art_strike(cv, x, y, w, h):
    cv.rect(x, y, w, h, (250, 244, 230))
    for i, (px, ph) in enumerate(((0.16, 0.42), (0.48, 0.52), (0.78, 0.40))):
        sx = x + int(w * px)
        cv.line(sx, y + int(h * ph) + 14, sx, y + h - 6, (80, 70, 60), w=3)
        cv.rect(sx - 18, y + int(h * ph), 36, 16,
                (179, 53, 43) if i != 1 else NAVY)
        cv.line(sx - 12, y + int(h * ph) + 4, sx - 12, y + int(h * ph) + 12,
                WHITE, w=2)
        cv.line(sx - 12, y + int(h * ph) + 8, sx + 2, y + int(h * ph) + 8,
                WHITE, w=2)
    draw_text(cv, x + w // 2, y + 6, "24H", 12, RED, bold=True, align='c')


def art_pill(cv, x, y, w, h):
    cv.rect(x, y, w, h, (238, 246, 240))
    cx, cy = x + int(w * 0.5), y + int(h * 0.42)
    cv.line(cx - 34, cy - 8, cx + 34, cy + 8, (43, 95, 138), w=16)
    cv.disc(cx - 34, cy - 8, 8, (43, 95, 138))
    cv.disc(cx + 34, cy + 8, 8, (255, 120, 90))
    cv.line(cx - 30, cy - 6, cx + 30, cy + 6, WHITE, w=2)
    draw_text(cv, x + w // 2, y + h - 15, "60.7%", 12, TEAL, bold=True,
              align='c')


ARTS = {'cyclone': art_cyclone, 'kyiv': art_kyiv, 'cop31': art_cop31,
        'chart': art_chart, 'moon': art_moon, 'flags': art_flags,
        'bars': art_bars, 'bank': art_bank, 'cricket': art_cricket,
        'ballot': art_ballot, 'boat': art_boat, 'strike': art_strike,
        'pill': art_pill}


def draw_map(cv, x, y, w, h):
    cv.rect(x, y, w, h, SEA)
    cv.rect(x, y + int(h * 0.78), w, h - int(h * 0.78), (196, 210, 222))
    # simplified continent blobs (stylised, not to scale)
    cv.poly([(x + 26, y + 40), (x + 62, y + 28), (x + 92, y + 46),
             (x + 78, y + 78), (x + 46, y + 86), (x + 24, y + 66)], LAND)  # N America
    cv.poly([(x + 92, y + 112), (x + 128, y + 108), (x + 142, y + 132),
             (x + 132, y + 176), (x + 108, y + 196), (x + 96, y + 150)],
            LAND)  # S America
    cv.poly([(x + 218, y + 34), (x + 268, y + 26), (x + 292, y + 44),
             (x + 280, y + 72), (x + 240, y + 84), (x + 214, y + 60)],
            LAND)  # Europe
    cv.poly([(x + 230, y + 100), (x + 268, y + 94), (x + 292, y + 112),
             (x + 282, y + 158), (x + 256, y + 176), (x + 232, y + 142)],
            LAND)  # Africa
    cv.poly([(x + 320, y + 30), (x + 396, y + 22), (x + 428, y + 52),
             (x + 412, y + 92), (x + 368, y + 112), (x + 330, y + 84),
             (x + 312, y + 56)], LAND)  # Asia
    cv.poly([(x + 400, y + 180), (x + 430, y + 176), (x + 436, y + 196),
             (x + 414, y + 210), (x + 396, y + 196)], LAND)  # Oceania
    draw_text(cv, x + 10, y + 8, "WORLD MAP \u2014 WHERE FRIDAY HAPPENED",
              10, NAVY, bold=True)
    # pins: (lon, lat) -> x, y with a simple equirectangular projection
    # nudge clustered pins apart so none overlap (Europe + East Asia)
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
        cv.disc(px, py, 8, RED)
        cv.ring(px, py, 8, WHITE, w=1)
        draw_text(cv, px, py - 5, str(i), 9, WHITE, bold=True, align='c')

# ------------------------------------------------------------------ layout
FOOTER1 = ("Every story here happened, or was first reported, on Friday "
           "20 November 2026 in at least one time zone. Claims are "
           "attributed, not stated as fact.")
FOOTER2 = ("Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 The Hindu "
           "\u00b7 IMD \u00b7 UN News \u00b7 Al Jazeera. Original vector drawings.")


def _card(cv, x, y, w, h):
    cv.rect(x, y, w, h, CREAM)
    hline(cv, x, y, w, BORDER, 1)
    hline(cv, x, y + h - 1, w, BORDER, 1)
    vline(cv, x, y, h)
    vline(cv, x + w - 1, y, h)


def build():
    cv = Canvas(W, H, PAPER)
    X, CW = 28, 968
    # top strip
    draw_text(cv, X, 8, "THE WORLD IN ONE DAY", 12, RED, bold=True)
    draw_text(cv, X + CW, 8,
              "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 6 CONTINENTS",
              12, INK, bold=True, align='r')
    # masthead
    draw_text(cv, X + CW // 2, 24, MASTHEAD, 50, INK, bold=True, align='c')
    hline(cv, X, 80, CW, INK, 3)
    hline(cv, X, 84, CW, INK, 1)
    draw_text(cv, X + CW // 2, 90, SUBHEAD, 13, RED, bold=True, align='c')
    # numbers band
    cv.rect(X, 106, CW, 48, CREAM)
    hline(cv, X, 106, CW, INK, 1)
    hline(cv, X, 153, CW, INK, 1)
    for i, (num, lab) in enumerate(NUMBERS):
        cx0 = X + i * 161
        if i:
            vline(cv, cx0, 110, 40)
        draw_text(cv, cx0 + 80, 108, num, 22, RED, bold=True, align='c')
        draw_para(cv, cx0 + 6, 134, lab, 8.5, 149, INK, lh=10, max_lines=2)
    # region chips, centred
    widths = [int(tw(f"{name} {n}", 10)) + 16 for name, n, _ in CHIPS]
    total = sum(widths) + 8 * (len(CHIPS) - 1)
    cx = X + (CW - total) // 2
    for (name, n, col), wd in zip(CHIPS, widths):
        cv.rect(cx, 160, wd, 18, col)
        draw_text(cv, cx + wd // 2, 164, f"{name} {n}", 10, WHITE, bold=True,
                  align='c')
        cx += wd + 8
    # three lead cards
    for i, (num, kicker, head, summ, art) in enumerate(LEADS):
        x, y, w, h = X + i * 327, 186, 314, 200
        _card(cv, x, y, w, h)
        ARTS[art](cv, x + 6, y + 6, w - 12, 84)
        circ_num(cv, x + 8, y + 94, num)
        draw_text(cv, x + 28, y + 96, kicker, 10, RED, bold=True)
        draw_para(cv, x + 10, y + 112, head, 16, w - 20, INK, bold=True,
                  lh=19, max_lines=2)
        draw_para(cv, x + 10, y + 152, summ, 10, w - 20, INK, lh=13,
                  max_lines=3)
    # ten feature cards, 2 rows x 5
    xs = [28, 223, 419, 614, 810]
    for r in range(2):
        for c in range(5):
            num, kicker, head, summ, art = FEATURES[r * 5 + c]
            x, y, w, h = xs[c], 394 + r * 118, 186, 110
            _card(cv, x, y, w, h)
            ARTS[art](cv, x + 4, y + 4, w - 8, 36)
            draw_text(cv, x + 7, y + 44, kicker, 8.5, RED, bold=True)
            draw_para(cv, x + 7, y + 54, head, 11.5, w - 14, INK, bold=True,
                      lh=13.5, max_lines=2)
            draw_para(cv, x + 7, y + 83, summ, 9, w - 14, (60, 60, 60),
                      lh=11.5, max_lines=2)
    # world map (left) and ALSO list (right)
    _card(cv, 28, 630, 470, 292)
    draw_map(cv, 34, 636, 458, 280)
    _card(cv, 510, 630, 486, 292)
    draw_text(cv, 518, 638, "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES",
              11, NAVY, bold=True)
    for i, (num, city, text) in enumerate(ALSO):
        col, row = divmod(i, 12)
        cx0 = 518 + col * 243
        y0 = 658 + row * 22
        draw_text(cv, cx0, y0, str(num), 9, RED, bold=True)
        draw_text(cv, cx0 + 22, y0, city, 9, NAVY, bold=True)
        draw_text(cv, cx0, y0 + 10, text, 9, INK)
    # date check
    cv.rect(X, 930, CW, 44, CREAM)
    hline(cv, X, 930, CW, RED, 2)
    hline(cv, X, 972, CW, RED, 2)
    vline(cv, X, 930, 44, RED, 2)
    vline(cv, X + CW - 2, 930, 44, RED, 2)
    draw_text(cv, X + 10, 947, "DATE CHECK", 10, RED, bold=True)
    draw_para(cv, X + 100, 938, DATE_CHECK, 9.5, CW - 110, INK, lh=12,
              max_lines=3)
    # footer
    draw_para(cv, X, 978, FOOTER1, 10, CW, GREY, lh=13, max_lines=2)
    draw_text(cv, X, 1006, FOOTER2, 10, GREY)
    return cv


def main():
    cv = build()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(png_bytes(cv))


# The copy uses the typographic apostrophe; map it to the ASCII one.
GLYPHS["\u2019"] = GLYPHS["'"]


if __name__ == "__main__":
    main()
