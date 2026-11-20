#!/usr/bin/env python3
"""Friday 20 November 2026, in one picture.

A broadsheet front page, 1024 by 1024, drawn by this program alone:
Python standard library only, no network, no fonts, no image files.
Lettering is a single-stroke vector alphabet I drew stroke by stroke
below -- every glyph a list of polylines on an 8-wide, 10-tall grid --
so the page is sharp at any size and byte-identical on every run.

    MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py   # writes entry.png
"""
import math
import os
import struct
import zlib

EDGE = 1024

# ink and paper
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
SEA = (204, 218, 226)
LAND = (230, 220, 194)
WHITE = (255, 255, 255)
NIGHT = (12, 20, 38)

# ---------------------------------------------------------------- alphabet
# Each glyph: a list of strokes; a stroke is a tuple of (x, y) points.
# Grid x 0..8, y 0..10, cap-top 0, baseline 10. Small letters are the
# capitals shrunk to 0.72 and set on the x-height band (small caps).
ALPHA = {
    "A": [((0, 10), (4, 0), (8, 10)), ((2, 6), (6, 6))],
    "B": [((0, 10), (0, 0), (5, 0), (7, 2), (7, 4), (5, 6), (0, 6)),
          ((5, 6), (7, 7), (7, 9), (5, 10), (0, 10))],
    "C": [((7, 2), (5, 0), (2, 0), (0, 2), (0, 8), (2, 10), (5, 10), (7, 8))],
    "D": [((0, 10), (0, 0), (5, 0), (8, 2), (8, 8), (5, 10), (0, 10))],
    "E": [((7, 0), (0, 0), (0, 10), (7, 10)), ((0, 5), (5, 5))],
    "F": [((0, 10), (0, 0), (7, 0)), ((0, 5), (5, 5))],
    "G": [((7, 2), (5, 0), (2, 0), (0, 2), (0, 8), (2, 10), (5, 10),
           (7, 8), (7, 5), (4, 5))],
    "H": [((0, 0), (0, 10)), ((8, 0), (8, 10)), ((0, 5), (8, 5))],
    "I": [((4, 0), (4, 10)), ((1, 0), (7, 0)), ((1, 10), (7, 10))],
    "J": [((7, 0), (7, 8), (5, 10), (2, 10), (1, 8))],
    "K": [((0, 10), (0, 0)), ((8, 0), (0, 5), (8, 10))],
    "L": [((0, 0), (0, 10), (7, 10))],
    "M": [((0, 10), (0, 0), (4, 6), (8, 0), (8, 10))],
    "N": [((0, 10), (0, 0), (8, 10), (8, 0))],
    "O": [((2, 0), (6, 0), (8, 2), (8, 8), (6, 10), (2, 10), (0, 8),
           (0, 2), (2, 0))],
    "P": [((0, 10), (0, 0), (6, 0), (8, 2), (8, 4), (6, 6), (0, 6))],
    "Q": [((2, 0), (6, 0), (8, 2), (8, 8), (6, 10), (2, 10), (0, 8),
           (0, 2), (2, 0)), ((5, 7), (8, 10))],
    "R": [((0, 10), (0, 0), (6, 0), (8, 2), (8, 4), (6, 6), (0, 6)),
          ((5, 6), (8, 10))],
    "S": [((7, 2), (5, 0), (2, 0), (0, 2), (0, 4), (2, 6), (6, 6), (8, 8),
           (8, 9), (6, 10), (3, 10), (1, 8))],
    "T": [((0, 0), (8, 0)), ((4, 0), (4, 10))],
    "U": [((0, 0), (0, 8), (2, 10), (6, 10), (8, 8), (8, 0))],
    "V": [((0, 0), (4, 10), (8, 0))],
    "W": [((0, 0), (2, 10), (4, 5), (6, 10), (8, 0))],
    "X": [((0, 0), (8, 10)), ((8, 0), (0, 10))],
    "Y": [((0, 0), (4, 5), (8, 0)), ((4, 5), (4, 10))],
    "Z": [((0, 0), (8, 0), (0, 10), (8, 10))],
    "0": [((2, 0), (6, 0), (8, 2), (8, 8), (6, 10), (2, 10), (0, 8),
           (0, 2), (2, 0)), ((2, 8), (6, 2))],
    "1": [((3, 1), (4, 0), (4, 10)), ((1, 10), (7, 10))],
    "2": [((1, 2), (2, 0), (6, 0), (7, 2), (7, 4), (0, 10), (8, 10))],
    "3": [((1, 1), (3, 0), (6, 0), (7, 2), (7, 4), (5, 5)),
          ((5, 5), (7, 6), (7, 8), (6, 10), (3, 10), (1, 9))],
    "4": [((0, 7), (6, 0), (6, 10)), ((0, 7), (8, 7))],
    "5": [((7, 0), (1, 0), (1, 4), (5, 4), (7, 6), (7, 8), (5, 10),
           (2, 10), (0, 8))],
    "6": [((7, 1), (5, 0), (2, 0), (1, 2), (0, 5), (0, 8), (2, 10),
           (5, 10), (7, 8), (7, 6), (5, 5), (1, 5))],
    "7": [((0, 0), (8, 0), (4, 10))],
    "8": [((3, 0), (6, 0), (7, 2), (7, 4), (5, 5), (3, 5), (1, 4), (0, 2),
           (0, 1), (1, 0)),
          ((5, 5), (7, 6), (7, 8), (6, 10), (3, 10), (1, 9), (0, 7), (1, 5))],
    "9": [((0, 9), (0, 6), (1, 4), (2, 3), (5, 3), (7, 5), (7, 8), (6, 10),
           (3, 10), (1, 9)), ((1, 5), (7, 5))],
    ".": [((3, 9), (4, 9))],
    ",": [((3, 9), (4, 9)), ((4, 9), (2, 12))],
    ":": [((3, 3), (4, 3)), ((3, 8), (4, 8))],
    ";": [((3, 3), (4, 3)), ((3, 8), (4, 8)), ((4, 8), (2, 12))],
    "'": [((3, 0), (4, 3))],
    '"': [((2, 0), (3, 3)), ((5, 0), (6, 3))],
    "-": [((1, 5), (7, 5))],
    "(": [((6, 0), (3, 2), (3, 8), (6, 10))],
    ")": [((2, 0), (5, 2), (5, 8), (2, 10))],
    "!": [((4, 0), (4, 7)), ((4, 9), (4, 10))],
    "?": [((1, 2), (2, 0), (6, 0), (7, 2), (7, 4), (5, 6), (4, 7), (4, 8)),
          ((4, 9), (4, 10))],
    "$": [((4, 0), (4, 11)),
          ((7, 2), (5, 0), (2, 0), (0, 2), (0, 4), (2, 5), (6, 5), (8, 6),
           (8, 8), (6, 10), (3, 10), (1, 8))],
    "%": [((7, 0), (1, 10)), ((2, 1), (4, 1), (4, 3), (2, 3)),
          ((6, 7), (8, 7), (8, 9), (6, 9))],
    "/": [((7, 0), (1, 10))],
    "+": [((4, 2), (4, 8)), ((1, 5), (7, 5))],
    "=": [((1, 3), (7, 3)), ((1, 7), (7, 7))],
    "&": [((7, 2), (5, 0), (2, 0), (0, 2), (0, 5), (2, 7), (8, 10)),
          ((0, 10), (8, 3))],
    " ": [],
}
# How wide each glyph steps, in grid units. Capitals step 8 by default.
STEP = {
    ".": 4, ",": 4, ":": 4, ";": 4, "'": 3, '"': 6, "!": 4, "(": 5, ")": 5,
    "-": 6, "/": 6, "1": 6, "I": 5, "%": 10, "$": 8, "?": 8, "M": 10,
    "W": 10, "O": 9, "Q": 9, "G": 9, "D": 9, "0": 9, "8": 9, "&": 9, "=": 8,
}
# Small-cap steps for the narrow lower-case letters.
SMALL_STEP = {"i": 5.0, "l": 5.0, "j": 5.0, "t": 6.0, "f": 6.0, "r": 6.0}


def step_of(ch):
    if ch == " ":
        return 4.0
    if ch.islower():
        return SMALL_STEP.get(ch, 7.0)
    return STEP.get(ch, 8.0)


def glyph_of(ch):
    """Return (strokes, scale, drop) for one character."""
    if ch.islower() and ch.upper() in ALPHA:
        return ALPHA[ch.upper()], 0.72, 3.0
    return ALPHA.get(ch, []), 1.0, 0.0


def measure(text, size):
    """Pixel width of text at cap-height `size`."""
    sc = size / 10.0
    total = sum(step_of(c) for c in text) * sc
    return total + max(0, len(text) - 1) * sc * 0.18


def fold(text, size, width):
    """Greedy word wrap into lines no wider than `width` pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        nxt = word if not cur else cur + " " + word
        if measure(nxt, size) <= width or not cur:
            cur = nxt
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ sheet
class Sheet:
    """A flat RGB picture with the handful of marks this page needs."""

    def __init__(self, w, h, bg):
        self.w, self.h, self.buf = w, h, bytearray(bg * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def box(self, x, y, w, h, c):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def dot(self, cx, cy, r, c):
        r = int(r)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, c)

    def stroke(self, x0, y0, x1, y1, c, w=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        half = w // 2
        while True:
            for yy in range(y - half, y + half + 1):
                for xx in range(x - half, x + half + 1):
                    self.px(xx, yy, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def polyfill(self, pts, c):
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
                    self.px(x, y, c)

    def ring(self, cx, cy, r, c, w=2):
        steps = max(24, int(2 * math.pi * r))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            self.dot(int(cx + r * math.cos(a)),
                     int(cy + r * math.sin(a)), w, c)

    def hbar(self, x, y, w, c, t=1):
        self.box(x, y, w, t, c)

    def vbar(self, x, y, h, c, t=1):
        self.box(x, y, t, h, c)


def encode_png(sh):
    raw = bytearray()
    stride = sh.w * 3
    for y in range(sh.h):
        raw.append(0)
        raw += sh.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    hdr = struct.pack(">IIBBBBB", sh.w, sh.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", hdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# -------------------------------------------------------------- lettering
def draw(sh, x, y, text, size, color, bold=False, align="l"):
    """Set `text` with its cap-top at y; align l/c/r around x."""
    if align == "c":
        x -= measure(text, size) / 2
    elif align == "r":
        x -= measure(text, size)
    sc = size / 10.0
    lw = max(2, int(size * 0.12)) if bold else (2 if size <= 13 else 1)
    cx = float(x)
    for ch in text:
        if ch == " ":
            cx += step_of(ch) * sc + sc * 0.18
            continue
        strokes, scale, drop = glyph_of(ch)
        if not strokes:
            cx += step_of(ch) * sc + sc * 0.18
            continue
        ssc = sc * scale
        for pts in strokes:
            if len(pts) == 1:
                px, py = pts[0]
                sh.dot(int(round(cx + px * ssc)),
                       int(round(y + (py * scale + drop) * sc)),
                       max(1, lw // 2), color)
            else:
                for a, b in zip(pts, pts[1:]):
                    sh.stroke(cx + a[0] * ssc, y + (a[1] * scale + drop) * sc,
                              cx + b[0] * ssc, y + (b[1] * scale + drop) * sc,
                              color, w=lw)
        cx += step_of(ch) * sc + sc * 0.18
    return cx


def para(sh, x, y, text, size, width, color, bold=False, lh=None,
         limit=None, align="l"):
    lines = fold(text, size, width)
    if limit:
        lines = lines[:limit]
    lh = lh or int(size * 1.6)
    for i, ln in enumerate(lines):
        if align == "c":
            draw(sh, x + width / 2, y + i * lh, ln, size, color, bold=bold,
                 align="c")
        else:
            draw(sh, x, y + i * lh, ln, size, color, bold=bold)
    return y + len(lines) * lh


def circled(sh, x, y, n, r=8, bg=RED, fg=WHITE, size=11):
    sh.dot(x + r, y + r, r, bg)
    sh.ring(x + r, y + r, r, fg, w=1)
    draw(sh, x + r, y + r - size // 2, str(n), size, fg, bold=True, align="c")


# ------------------------------------------------------------ the day's news
# One record per story, fields joined by "|": number | dateline | headline
# | one-line summary (outlet in brackets) | picture key. Every story
# happened, or was first reported, on Friday 20 November 2026 in at
# least one time zone.
TITLE = "Friday 20 November 2026"
DEK = "Akvan strikes India - Missiles hit Kyiv - COP31 deadlocked - Asian AI sell-off"
BIG = """1|ODISHA, INDIA - CYCLONE|Cyclone Akvan makes landfall in eastern India|Crosses near Gopalpur at 8:30am IST, winds 70-80 km/h gusting 90; 370,000 evacuated, no major damage. (IMD)|cyclone
2|KYIV, UKRAINE - WAR|Russia fires wave of ballistic missiles at Kyiv|Overnight barrage kills 3, injures 15; three Dnipro bridges hit in the biggest bridge attack of the war. (Reuters)|kyiv
3|ANTALYA, TURKIYE - CLIMATE|COP31 reaches final day deadlocked|Draft omits fossil-fuel phase-out; $120bn adaptation finance unresolved as hosts push a '35 by 35' clean power. (UN News)|cop31"""
SMALL = """4|SEOUL - TOKYO - MARKETS|AI sell-off: Asia's worst week since 2020|Nikkei -4.9%, KOSPI -5.4%, TAIEX -6.8% (Reuters)|chart
5|SPACE|BepiColombo reaches Mercury in 8 years|ESA-JAXA probe ends 6bn-mile trip. (ESA, BBC)|moon
6|BRUSSELS - EUROPE|Burnham holds first EU-UK reset summit|Costa and von der Leyen host UK PM. (EU Council)|flags
7|TOKYO - ECONOMY|Japan inflation hits 2.3%; BoJ hike eyed|Oct CPI up from 2.1%; core above 2%. (Reuters)|bars
8|BEIJING - RATES|China holds lending rates for 18th month|One-year LPR 3.0%, five-year 3.5%. (PBOC)|bank
9|WELLINGTON - CRICKET|Phillips makes history with 118 vs India|Centuries in all 3 formats vs India. (ICC, AP)|cricket
10|SAN SALVADOR - POLITICS|Bukele registers for third-term bid|Files for Feb 2027 vote; rights groups object. (AP)|ballot
11|SENEGAL - MIGRATION|Migrant boat capsizes off Yemen; 4 dead|Dozens missing from 50-100 aboard. (Al Jazeera)|boat
12|ROME - LABOUR|Italy's CGIL holds 24-hr general strike|Unions rally in 100 squares; transit hit. (AFP)|strike
13|BARCELONA - HEALTH|Cancer pill shrinks tumours 60.7%|Daraxonrasib plus chemo beats chemo alone. (Reuters)|pill"""
REST = """14|NEW YORK|Anthropic up 17% on debut ($97.17)
15|WASHINGTON|Senate rejects Iran bid, 51-48
16|SHENZHEN|Leaders issue peace declaration
17|GAZA|Aid groups score peace plan 4 of 26
18|HORMUZ|Four attacks on vessels in 96 hours
19|WASHINGTON|Pentagon: US war cost vs Iran $48.3bn
20|LONDON|UK, Norway fund GBP100m+ navy vessels
21|COPENHAGEN|Denmark OKs Greenland defence bill
22|JAKARTA|Indonesia OKs asset-forfeiture bill
23|CINCINNATI|Hippo Fiona dies after swallowing hat
24|DAKAR|Faye enacts budget by decree
25|LAS VEGAS|Russell fastest in wet F1 practice
26|TURIN|ATP Finals groups close, semis Sat
27|LOS ANGELES|Thomas Markle fit to stand trial
28|TAIPEI|TAIEX set for worst week since 1991
29|HONG KONG|Hang Seng about 20% off January peak
30|SYDNEY|General Pants enters administration
31|CANBERRA|CBO warns AUKUS sales shrink US fleet
32|MALAWI|Fuel crisis: 20L a day, petrol $3.24
33|NEW DELHI|Modi opens SCO civilisations forum
34|FLORIDA|St. Johns River hits record 18.3 ft
35|QATAR|U17: Austria stun Argentina 2-0
36|SAO PAULO|Markets shut for Consciousness Day"""
FIGURES = [
    ("370,000", "evacuated ahead of Akvan"),
    ("3", "killed; 3 bridges hit"),
    ("-6.8%", "TAIEX intraday low"),
    ("2.3%", "Japan Oct headline CPI"),
    ("118", "Phillips makes history"),
    ("8 yrs", "BepiColombo to Mercury"),
]
REGIONS = [("EUROPE", 8, NAVY2), ("AMERICAS", 8, RED), ("ASIA-PACIFIC", 9, TEAL),
           ("MIDEAST", 4, ORANGE), ("AFRICA", 3, GREEN), ("OCEANIA", 3, PURPLE),
           ("WORLD", 1, INK)]
# Map pins, story order 1-13: (longitude, latitude). Story 5 has no
# single ground position, so it is pinned in the mid-Atlantic.
PINS = [(85.8, 19.3), (30.5, 50.5), (30.7, 36.9), (127.0, 37.5), (0, 0),
        (4.4, 50.8), (139.7, 35.7), (116.4, 39.9), (174.8, -41.3),
        (-89.2, 13.7), (-17.4, 14.7), (12.5, 41.9), (2.2, 41.4)]
CHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: "
         "the Trump-Xi-Putin Shenzhen summit itself - Anthropic's $83 "
         "IPO pricing - ICJ Myanmar Rohingya genocide verdict - GTA VI "
         "midnight launch - $190.4m Van Gogh sale - Voyager 1 one "
         "light-day confirmation - Senate 48-51 Iran war-powers vote "
         "- Crimean Bridge strike.")
NOTE1 = ("Every story here happened, or was first reported, on Friday "
         "20 November 2026 in at least one time zone. Claims are "
         "attributed, not stated as fact.")
NOTE2 = ("Sources: Reuters - AP - AFP - BBC - The Hindu - IMD - UN News "
         "- Al Jazeera. Original vector drawings.")


def parse(block, fields):
    rows = []
    for line in block.strip().split("\n"):
        parts = line.split("|")
        rows.append(tuple(parts[:fields]))
    return rows


# ---------------------------------------------------------------- pictures
def pic_cyclone(sh, x, y, w, h):
    sh.box(x, y, w, h, (31, 68, 99))
    sh.box(x, y + int(h * 0.6), w, h - int(h * 0.6), (44, 96, 140))
    sh.polyfill([(x + int(w * 0.5), y), (x + int(w * 0.66), y + int(h * 0.35)),
                 (x + int(w * 0.6), y + int(h * 0.7)), (x + int(w * 0.72), y + h),
                 (x + w, y + h), (x + w, y)], (222, 206, 168))
    draw(sh, x + 10, y + 8, "BAY OF", 11, (226, 232, 238), bold=True)
    draw(sh, x + 10, y + 22, "BENGAL", 11, (226, 232, 238), bold=True)
    cx, cy = x + int(w * 0.28), y + int(h * 0.55)
    for r in (4, 8, 12, 16, 20, 24):
        a0 = -0.5 * r / 6
        steps = int(r * 2)
        for i in range(steps):
            a = a0 + (4.8 - 0.5 * r / 6 - a0) * i / steps
            rr = r * (1 - i / steps * 0.3)
            sh.dot(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)), 2,
                   WHITE)
    sh.dot(cx, cy, 5, WHITE)
    lx, ly = x + int(w * 0.58), y + int(h * 0.48)
    sh.dot(lx, ly, 6, RED)
    sh.ring(lx, ly, 11, RED, w=2)
    draw(sh, lx + 15, ly - 6, "GOPALPUR", 11, WHITE, bold=True)
    draw(sh, x + 10, y + h - 16, "8:30AM IST", 11, (226, 232, 238), bold=True)


def pic_kyiv(sh, x, y, w, h):
    sh.box(x, y, w, h, NIGHT)
    for sx, sy in ((0.07, 0.12), (0.22, 0.07), (0.38, 0.15), (0.52, 0.06),
                   (0.68, 0.14), (0.82, 0.07), (0.92, 0.18), (0.44, 0.2)):
        sh.dot(x + int(w * sx), y + int(h * sy), 1, (200, 210, 220))
    base = y + h
    for bx, bw, bh in ((0.02, 0.14, 0.36), (0.18, 0.11, 0.5), (0.31, 0.13, 0.42),
                       (0.46, 0.1, 0.56), (0.58, 0.13, 0.4),
                       (0.73, 0.11, 0.52), (0.86, 0.12, 0.44)):
        sh.box(x + int(w * bx), base - int(h * bh), int(w * bw), int(h * bh),
               (24, 36, 58))
    for wx, wy in ((0.06, 0.7), (0.2, 0.6), (0.34, 0.66), (0.49, 0.54),
                   (0.61, 0.68), (0.76, 0.58), (0.89, 0.64), (0.23, 0.76)):
        sh.box(x + int(w * wx), y + int(h * wy), 4, 5, GOLDL)
    sh.box(x, base - 10, w, 10, (30, 62, 96))
    for mx, my, tx, ty in ((0.1, 0.05, 0.28, 0.5), (0.52, 0.02, 0.46, 0.6),
                           (0.86, 0.04, 0.74, 0.53)):
        sh.stroke(x + int(w * mx), y + int(h * my), x + int(w * tx),
                  y + int(h * ty), (255, 190, 90), w=2)
        sh.dot(x + int(w * tx), y + int(h * ty), 4, (255, 120, 40))
    for ex, ey in ((0.28, 0.5), (0.74, 0.53)):
        for dx, dy in ((0, -9), (7, -6), (9, 0), (7, 6), (0, 9), (-7, 6),
                       (-9, 0), (-7, -6)):
            sh.stroke(x + int(w * ex), y + int(h * ey),
                      x + int(w * ex) + dx, y + int(h * ey) + dy,
                      (255, 200, 90), w=2)
        sh.dot(x + int(w * ex), y + int(h * ey), 4, (255, 220, 130))
    draw(sh, x + 10, y + 8, "3 BRIDGES HIT", 11, (255, 210, 160), bold=True)


def pic_cop(sh, x, y, w, h):
    sh.box(x, y, w, h, (20, 62, 46))
    gx, gy, gr = x + int(w * 0.3), y + int(h * 0.5), int(h * 0.36)
    sh.dot(gx, gy, gr, (42, 110, 88))
    sh.ring(gx, gy, gr, (120, 200, 170), w=2)
    for k in range(-2, 3):
        a = k * 0.55
        pts = []
        for i in range(25):
            t = -1 + 2 * i / 24
            pts.append((gx + int(gr * math.cos(a) * math.sqrt(1 - t * t)),
                        gy + int(gr * t)))
        for a2, b2 in zip(pts, pts[1:]):
            sh.stroke(a2[0], a2[1], b2[0], b2[1], (120, 200, 170), w=1)
    sh.stroke(gx - gr, gy, gx + gr, gy, (120, 200, 170), w=1)
    sh.stroke(gx, gy - gr, gx, gy + gr, (120, 200, 170), w=1)
    tx = x + int(w * 0.7)
    sh.box(tx, y + int(h * 0.12), 12, int(h * 0.64), WHITE)
    sh.box(tx + 3, y + int(h * 0.12), 6, int(h * 0.52), RED)
    sh.dot(tx + 6, y + int(h * 0.82), 11, RED)
    sh.dot(tx + 6, y + int(h * 0.82), 7, (255, 160, 140))
    draw(sh, tx + 20, y + int(h * 0.28), "+1.5C", 12, WHITE, bold=True)
    sh.box(x, y + h - 26, w, 26, RED)
    draw(sh, x + w // 2, y + h - 18, "COP31", 13, WHITE, bold=True, align="c")


def pic_chart(sh, x, y, w, h):
    sh.box(x, y, w, h, (28, 38, 52))
    pts = [(x + int(w * k / 5), y + h - int(h * (0.28 + 0.13 * k)))
           for k in range(6)]
    for a, b in zip(pts, pts[1:]):
        sh.stroke(a[0], a[1], b[0], b[1], (255, 110, 90), w=2)
    for px, py in pts:
        sh.dot(px, py, 3, (255, 150, 120))
    draw(sh, x + 8, y + 6, "TAIEX", 11, (255, 210, 190), bold=True)
    draw(sh, x + w - 8, y + 6, "-6.8%", 12, (255, 120, 100), bold=True,
         align="r")


def pic_moon(sh, x, y, w, h):
    sh.box(x, y, w, h, (18, 26, 44))
    for sx, sy in ((0.1, 0.18), (0.24, 0.1), (0.78, 0.14), (0.88, 0.28),
                   (0.58, 0.08), (0.14, 0.52)):
        sh.dot(x + int(w * sx), y + int(h * sy), 1, WHITE)
    sh.dot(x + int(w * 0.3), y + int(h * 0.55), 17, (208, 208, 196))
    sh.dot(x + int(w * 0.26), y + int(h * 0.48), 4, (170, 170, 160))
    sh.dot(x + int(w * 0.36), y + int(h * 0.62), 3, (170, 170, 160))
    draw(sh, x + int(w * 0.56), y + int(h * 0.26), "MERCURY", 11, WHITE,
         bold=True)
    draw(sh, x + int(w * 0.56), y + int(h * 0.5), "8 YRS", 12, GOLDL, bold=True)


def pic_flags(sh, x, y, w, h):
    sh.box(x, y, w, h, (24, 48, 84))
    cx, cy = x + int(w * 0.24), y + int(h * 0.5)
    sh.dot(cx, cy, 19, (0, 51, 153))
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        sh.dot(int(cx + 12 * math.cos(a)), int(cy + 12 * math.sin(a)), 2,
               (255, 204, 0))
    ux, uy, uw, uh = x + int(w * 0.58), y + int(h * 0.24), 34, 22
    sh.box(ux, uy, uw, uh, (0, 36, 125))
    sh.stroke(ux, uy, ux + uw, uy + uh, WHITE, w=2)
    sh.stroke(ux + uw, uy, ux, uy + uh, WHITE, w=2)
    sh.box(ux + uw // 2 - 3, uy, 6, uh, (200, 16, 46))
    sh.box(ux, uy + uh // 2 - 3, uw, 6, (200, 16, 46))


def pic_bars(sh, x, y, w, h):
    sh.box(x, y, w, h, (250, 246, 236))
    sh.box(x + 8, y + h - 6, w - 16, 2, (200, 192, 172))
    for i, bh in enumerate((0.32, 0.5, 0.7)):
        bx = x + 14 + i * 34
        sh.box(bx, y + h - 8 - int(h * bh), 22, int(h * bh),
               NAVY if i < 2 else RED)
    draw(sh, x + w - 8, y + 6, "2.3%", 13, RED, bold=True, align="r")
    draw(sh, x + 8, y + 6, "CPI", 11, NAVY, bold=True)


def pic_bank(sh, x, y, w, h):
    sh.box(x, y, w, h, (240, 236, 224))
    bx, by = x + int(w * 0.18), y + int(h * 0.18)
    bw, bh = int(w * 0.64), int(h * 0.62)
    sh.polyfill([(bx - 6, by), (bx + bw // 2, by - 12), (bx + bw + 6, by)],
                RED)
    sh.box(bx, by, bw, 6, NAVY)
    for i in range(4):
        sh.box(bx + 6 + i * (bw - 12) // 4, by + 6, 6, bh - 12, NAVY)
    sh.box(bx, by + bh - 4, bw, 6, NAVY)
    draw(sh, x + w // 2, y + h - 14, "3.0% / 3.5%", 11, RED, bold=True,
         align="c")


def pic_cricket(sh, x, y, w, h):
    sh.box(x, y, w, h, (36, 92, 52))
    sh.stroke(x + int(w * 0.28), y + int(h * 0.1), x + int(w * 0.5),
              y + int(h * 0.6), (210, 180, 130), w=5)
    sh.box(x + int(w * 0.42), y + int(h * 0.56), 10, 22, (210, 180, 130))
    sh.dot(x + int(w * 0.68), y + int(h * 0.68), 7, (200, 60, 50))
    sh.dot(x + int(w * 0.68), y + int(h * 0.68), 3, (255, 220, 200))
    draw(sh, x + int(w * 0.74), y + int(h * 0.1), "118", 16, WHITE, bold=True)


def pic_ballot(sh, x, y, w, h):
    sh.box(x, y, w, h, (232, 238, 244))
    bx, by = x + int(w * 0.28), y + int(h * 0.32)
    bw, bh = int(w * 0.44), int(h * 0.44)
    sh.box(bx, by, bw, bh, BLUE)
    sh.box(bx + bw // 2 - 14, by - 8, 28, 8, INK)
    sh.stroke(bx + 6, by + bh // 2, bx + bw // 2 - 4, by + bh - 6, WHITE, w=3)
    sh.stroke(bx + bw // 2 - 4, by + bh - 6, bx + bw - 6, by + 6, WHITE, w=3)
    draw(sh, x + w // 2, y + 6, "VOTE 2027", 11, NAVY, bold=True, align="c")


def pic_boat(sh, x, y, w, h):
    sh.box(x, y, w, h, (186, 214, 228))
    sh.stroke(x + int(w * 0.3), y + int(h * 0.08), x + int(w * 0.3),
              y + int(h * 0.42), (60, 50, 40), w=2)
    sh.polyfill([(x + int(w * 0.3), y + int(h * 0.1)),
                 (x + int(w * 0.58), y + int(h * 0.38)),
                 (x + int(w * 0.3), y + int(h * 0.38))], (200, 220, 230))
    sh.polyfill([(x + int(w * 0.12), y + int(h * 0.42)),
                 (x + int(w * 0.88), y + int(h * 0.42)),
                 (x + int(w * 0.78), y + int(h * 0.62)),
                 (x + int(w * 0.22), y + int(h * 0.62))], (90, 60, 40))
    for k, wy in enumerate((0.7, 0.82, 0.92)):
        for wx in range(0, w, 14):
            off = 3 if (wx // 14 + k) % 2 else 0
            sh.stroke(x + wx, y + int(h * wy) + off, x + wx + 7,
                      y + int(h * wy) + off, BLUE, w=2)


def pic_strike(sh, x, y, w, h):
    sh.box(x, y, w, h, (250, 244, 230))
    for i, (px, ph) in enumerate(((0.16, 0.42), (0.48, 0.52), (0.78, 0.4))):
        sx = x + int(w * px)
        sh.stroke(sx, y + int(h * ph) + 14, sx, y + h - 6, (80, 70, 60), w=3)
        sh.box(sx - 18, y + int(h * ph), 36, 16, RED if i != 1 else NAVY)
        sh.stroke(sx - 12, y + int(h * ph) + 4, sx - 12, y + int(h * ph) + 12,
                  WHITE, w=2)
        sh.stroke(sx - 12, y + int(h * ph) + 8, sx + 2, y + int(h * ph) + 8,
                  WHITE, w=2)
    draw(sh, x + w // 2, y + 6, "24H", 12, RED, bold=True, align="c")


def pic_pill(sh, x, y, w, h):
    sh.box(x, y, w, h, (238, 246, 240))
    cx, cy = x + int(w * 0.5), y + int(h * 0.42)
    sh.stroke(cx - 34, cy - 8, cx + 34, cy + 8, BLUE, w=16)
    sh.dot(cx - 34, cy - 8, 8, BLUE)
    sh.dot(cx + 34, cy + 8, 8, (255, 120, 90))
    sh.stroke(cx - 30, cy - 6, cx + 30, cy + 6, WHITE, w=2)
    draw(sh, x + w // 2, y + h - 15, "60.7%", 12, TEAL, bold=True, align="c")


PICS = {"cyclone": pic_cyclone, "kyiv": pic_kyiv, "cop31": pic_cop,
        "chart": pic_chart, "moon": pic_moon, "flags": pic_flags,
        "bars": pic_bars, "bank": pic_bank, "cricket": pic_cricket,
        "ballot": pic_ballot, "boat": pic_boat, "strike": pic_strike,
        "pill": pic_pill}


def draw_world(sh, x, y, w, h):
    sh.box(x, y, w, h, SEA)
    sh.box(x, y + int(h * 0.78), w, h - int(h * 0.78), (196, 210, 222))
    sh.polyfill([(x + 26, y + 40), (x + 62, y + 28), (x + 92, y + 46),
                 (x + 78, y + 78), (x + 46, y + 86), (x + 24, y + 66)], LAND)
    sh.polyfill([(x + 92, y + 112), (x + 128, y + 108), (x + 142, y + 132),
                 (x + 132, y + 176), (x + 108, y + 196), (x + 96, y + 150)],
                LAND)
    sh.polyfill([(x + 218, y + 34), (x + 268, y + 26), (x + 292, y + 44),
                 (x + 280, y + 72), (x + 240, y + 84), (x + 214, y + 60)],
                LAND)
    sh.polyfill([(x + 230, y + 100), (x + 268, y + 94), (x + 292, y + 112),
                 (x + 282, y + 158), (x + 256, y + 176), (x + 232, y + 142)],
                LAND)
    sh.polyfill([(x + 320, y + 30), (x + 396, y + 22), (x + 428, y + 52),
                 (x + 412, y + 92), (x + 368, y + 112), (x + 330, y + 84),
                 (x + 312, y + 56)], LAND)
    sh.polyfill([(x + 400, y + 180), (x + 430, y + 176), (x + 436, y + 196),
                 (x + 414, y + 210), (x + 396, y + 196)], LAND)
    draw(sh, x + 10, y + 8, "WORLD MAP - WHERE FRIDAY HAPPENED", 10, NAVY,
         bold=True)
    NUDGE = {2: (14, -10), 3: (18, 14), 4: (16, -12), 6: (-16, -8),
             7: (14, 12), 8: (-14, 10), 12: (10, 12), 13: (-12, 10)}
    for i, (lon, lat) in enumerate(PINS, 1):
        if lon == 0 and lat == 0:
            px, py = x + int(w * 0.28), y + int(h * 0.72)
        else:
            px = x + int((lon + 180) / 360 * w)
            py = y + int((90 - lat) / 180 * h)
        dx, dy = NUDGE.get(i, (0, 0))
        px, py = px + dx, py + dy
        sh.dot(px, py, 8, RED)
        sh.ring(px, py, 8, WHITE, w=1)
        draw(sh, px, py - 5, str(i), 9, WHITE, bold=True, align="c")


# ------------------------------------------------------------------ page
def frame(sh, x, y, w, h):
    sh.box(x, y, w, h, CREAM)
    sh.hbar(x, y, w, FAINT, 1)
    sh.hbar(x, y + h - 1, w, FAINT, 1)
    sh.vbar(x, y, h, FAINT, 1)
    sh.vbar(x + w - 1, y, h, FAINT, 1)


def compose():
    sh = Sheet(EDGE, EDGE, PAPER)
    X, CW = 26, 972
    draw(sh, X, 8, "THE WORLD IN ONE DAY", 11, RED, bold=True)
    draw(sh, X + CW, 8, "FRIDAY'S NEWS - ONE PAGE - 36 STORIES - 6 CONTINENTS",
         11, INK, bold=True, align="r")
    draw(sh, X + CW // 2, 26, TITLE, 42, INK, bold=True, align="c")
    sh.hbar(X, 80, CW, INK, 3)
    sh.hbar(X, 84, CW, INK, 1)
    draw(sh, X + CW // 2, 90, DEK, 12, RED, bold=True, align="c")
    sh.box(X, 108, CW, 54, CREAM)
    sh.hbar(X, 108, CW, INK, 1)
    sh.hbar(X, 161, CW, INK, 1)
    for i, (num, lab) in enumerate(FIGURES):
        cell = X + i * 162
        if i:
            sh.vbar(cell, 112, 46, FAINT, 1)
        draw(sh, cell + 81, 111, num, 21, RED, bold=True, align="c")
        para(sh, cell + 6, 137, lab, 8.5, 150, INK, lh=11, limit=2, align="c")
    widths = [int(measure("%s %d" % (name, n), 10)) + 16
              for name, n, _ in REGIONS]
    total = sum(widths) + 8 * (len(REGIONS) - 1)
    cx = X + (CW - total) // 2
    for (name, n, col), wd in zip(REGIONS, widths):
        sh.box(cx, 168, wd, 20, col)
        draw(sh, cx + wd // 2, 173, "%s %d" % (name, n), 10, WHITE,
             bold=True, align="c")
        cx += wd + 8
    for i, row in enumerate(parse(BIG, 5)):
        num, kicker, head, summ, key = row
        x, y, w, h = X + i * 328, 196, 316, 216
        frame(sh, x, y, w, h)
        PICS[key](sh, x + 6, y + 6, w - 12, 92)
        circled(sh, x + 8, y + 106, int(num))
        draw(sh, x + 30, y + 108, kicker, 9.5, RED, bold=True)
        para(sh, x + 10, y + 126, head, 15, w - 20, INK, bold=True, lh=19,
             limit=2)
        para(sh, x + 10, y + 168, summ, 10, w - 20, INK, lh=14, limit=3)
    xs = [26, 222, 418, 614, 810]
    for r in range(2):
        for c in range(5):
            num, kicker, head, summ, key = parse(SMALL, 5)[r * 5 + c]
            x, y, w, h = xs[c], 424 + r * 132, 188, 124
            frame(sh, x, y, w, h)
            PICS[key](sh, x + 4, y + 4, w - 8, 38)
            draw(sh, x + 7, y + 48, kicker, 8, RED, bold=True)
            para(sh, x + 7, y + 60, head, 11, w - 14, INK, bold=True, lh=14,
                 limit=2)
            para(sh, x + 7, y + 90, summ, 8.5, w - 14, (60, 60, 60), lh=11.5,
                 limit=2)
    frame(sh, 26, 692, 462, 222)
    draw_world(sh, 32, 698, 450, 210)
    frame(sh, 500, 692, 498, 222)
    draw(sh, 508, 700, "ALSO ON FRIDAY 20 NOVEMBER - 23 MORE STORIES", 11,
         NAVY, bold=True)
    for i, row in enumerate(parse(REST, 3)):
        num, city, text = row
        col, rr = divmod(i, 12)
        cx0 = 508 + col * 245
        y0 = 720 + rr * 16
        line = "%s %s: %s" % (num, city, text)
        while measure(line, 8) > 240 and len(text) > 10:
            text = text[:-1]
            line = "%s %s: %s..." % (num, city, text)
        draw(sh, cx0, y0, line, 8, INK)
    sh.box(X, 922, CW, 56, CREAM)
    sh.hbar(X, 922, CW, RED, 2)
    sh.hbar(X, 976, CW, RED, 2)
    sh.vbar(X, 922, 56, RED, 2)
    sh.vbar(X + CW - 2, 922, 56, RED, 2)
    draw(sh, X + 10, 944, "DATE CHECK", 10, RED, bold=True)
    para(sh, X + 100, 930, CHECK, 9.5, CW - 110, INK, lh=12, limit=3)
    para(sh, X, 984, NOTE1, 9.5, CW, GREY, lh=12, limit=1)
    draw(sh, X, 1002, NOTE2, 9.5, GREY)
    return sh


def main():
    sh = compose()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(encode_png(sh))


if __name__ == "__main__":
    main()
