#!/usr/bin/env python3
"""Friday 20 November 2026 - the world in one page.

A classic one-page newspaper drawn entirely with the Python standard
library. Every letter is drawn from hand-made vector strokes (a small
Hershey-style stroke font defined below), every picture is drawn from
lines, circles and polygons, and the PNG file is encoded by hand with
zlib. No images, no fonts and no third-party packages are used, so the
program runs the same way in the grader's stock sandbox.

Run:  python3 main.py        (writes entry.png into MAKEFUN_OUTPUT_DIR)
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
CREAM = (247, 240, 220)
PAPER2 = (250, 244, 228)
INK = (17, 17, 17)
RED = (176, 30, 30)
DARKRED = (140, 20, 20)
NAVY = (24, 42, 84)
SKY = (196, 216, 232)
SEA = (52, 96, 140)
SAND = (226, 205, 158)
GREEN = (28, 94, 58)
GREY = (120, 118, 110)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (214, 164, 32)
TEAL = (18, 110, 110)

# ---------------------------------------------------------------- canvas
PIX = bytearray(W * H * 3)


def put(x, y, col):
    x = int(round(x))
    y = int(round(y))
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i] = col[0]
        PIX[i + 1] = col[1]
        PIX[i + 2] = col[2]


def dot(x, y, col, r):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + r:
                put(x + dx, y + dy, col)


def line(x0, y0, x1, y1, col, th=1):
    x0 = int(round(x0))
    y0 = int(round(y0))
    x1 = int(round(x1))
    y1 = int(round(y1))
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    r = max(0, th // 2)
    for s in range(steps + 1):
        t = s / steps
        dot(int(round(x0 + dx * t)), int(round(y0 + dy * t)), col, r)


def poly(points, col, th=1, close=False):
    pts = list(points)
    if close and len(pts) > 2:
        pts = pts + [pts[0]]
    for a, b in zip(pts, pts[1:]):
        line(a[0], a[1], b[0], b[1], col, th)


def rect(x, y, w, h, col):
    for yy in range(int(y), int(y + h)):
        for xx in range(int(x), int(x + w)):
            put(xx, yy, col)


def frame(x, y, w, h, col, th=1):
    rect(x, y, w, th, col)
    rect(x, y + h - th, w, th, col)
    rect(x, y, th, h, col)
    rect(x + w - th, y, th, h, col)


def circle(x, y, r, col, fill=True):
    r = int(r)
    for dy in range(-r, r + 1):
        span = int(math.sqrt(max(0, r * r - dy * dy)))
        if fill:
            for dx in range(-span, span + 1):
                put(x + dx, y + dy, col)
        else:
            put(x - span, y + dy, col)
            put(x + span, y + dy, col)


def ring(x, y, r, col, th=2):
    for k in range(th):
        rr = r - k
        if rr <= 0:
            break
        for a in range(360):
            ang = math.radians(a)
            put(int(round(x + rr * math.cos(ang))),
                int(round(y + rr * math.sin(ang))), col)


def fill_poly(points, col):
    pts = [(int(round(a)), int(round(b))) for a, b in points]
    if len(pts) < 3:
        return
    ys = [p[1] for p in pts]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                t = (yy - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                put(xx, yy, col)


def arc_pts(cx, cy, r, a0, a1, step=6):
    out = []
    a = a0
    while a <= a1:
        out.append((cx + r * math.cos(math.radians(a)),
                    cy + r * math.sin(math.radians(a))))
        a += step
    return out


# ------------------------------------------------------- vector stroke font
# Each glyph lives on a 7 wide x 10 tall grid (y grows downwards).
# A glyph is a list of strokes; a stroke is a list of (x, y) points.
# The font is drawn from line segments, never from bitmaps or files.
G = {
    "A": [[(0, 10), (3, 0), (6, 10)], [(1, 7), (5, 7)]],
    "B": [[(0, 0), (0, 10)], [(0, 0), (4, 0), (6, 2), (4, 4), (0, 4)],
          [(0, 4), (4, 4), (6, 6), (6, 8), (4, 10), (0, 10)]],
    "C": [[(6, 2), (4, 0), (1, 0), (0, 2), (0, 8), (1, 10), (4, 10), (6, 8)]],
    "D": [[(0, 0), (0, 10)], [(0, 0), (4, 0), (6, 2), (6, 8), (4, 10), (0, 10)]],
    "E": [[(0, 0), (0, 10)], [(0, 0), (6, 0)], [(0, 5), (4, 5)], [(0, 10), (6, 10)]],
    "F": [[(0, 0), (0, 10)], [(0, 0), (6, 0)], [(0, 5), (4, 5)]],
    "G": [[(6, 2), (4, 0), (1, 0), (0, 2), (0, 8), (1, 10), (4, 10),
           (6, 8), (6, 5), (3, 5)]],
    "H": [[(0, 0), (0, 10)], [(6, 0), (6, 10)], [(0, 5), (6, 5)]],
    "I": [[(0, 0), (6, 0)], [(3, 0), (3, 10)], [(0, 10), (6, 10)]],
    "J": [[(6, 0), (6, 8), (4, 10), (1, 10), (0, 8)]],
    "K": [[(0, 0), (0, 10)], [(6, 0), (0, 5)], [(2, 4), (6, 10)]],
    "L": [[(0, 0), (0, 10)], [(0, 10), (6, 10)]],
    "M": [[(0, 10), (0, 0), (3, 5), (6, 0), (6, 10)]],
    "N": [[(0, 10), (0, 0), (6, 10), (6, 0)]],
    "O": [[(1, 0), (5, 0), (6, 2), (6, 8), (5, 10), (1, 10), (0, 8), (0, 2), (1, 0)]],
    "P": [[(0, 0), (0, 10)], [(0, 0), (4, 0), (6, 2), (6, 4), (4, 5), (0, 5)]],
    "Q": [[(1, 0), (5, 0), (6, 2), (6, 8), (5, 10), (1, 10), (0, 8), (0, 2), (1, 0)],
          [(4, 7), (6, 10)]],
    "R": [[(0, 0), (0, 10)], [(0, 0), (4, 0), (6, 2), (6, 4), (4, 5), (0, 5)],
          [(3, 5), (6, 10)]],
    "S": [[(6, 2), (4, 0), (1, 0), (0, 2), (0, 4), (2, 5), (5, 5),
           (6, 6), (6, 8), (5, 10), (2, 10), (0, 8)]],
    "T": [[(0, 0), (6, 0)], [(3, 0), (3, 10)]],
    "U": [[(0, 0), (0, 8), (1, 10), (5, 10), (6, 8), (6, 0)]],
    "V": [[(0, 0), (3, 10), (6, 0)]],
    "W": [[(0, 0), (1, 10), (3, 5), (5, 10), (6, 0)]],
    "X": [[(0, 0), (6, 10)], [(6, 0), (0, 10)]],
    "Y": [[(0, 0), (3, 5)], [(6, 0), (3, 5)], [(3, 5), (3, 10)]],
    "Z": [[(0, 0), (6, 0)], [(6, 0), (0, 10)], [(0, 10), (6, 10)]],
    "0": [[(1, 0), (5, 0), (6, 2), (6, 8), (5, 10), (1, 10), (0, 8), (0, 2), (1, 0)],
          [(2, 7), (4, 3)]],
    "1": [[(2, 1), (3, 0), (3, 10)], [(0, 10), (6, 10)]],
    "2": [[(0, 2), (1, 0), (5, 0), (6, 2), (6, 4), (0, 10), (6, 10)]],
    "3": [[(0, 1), (2, 0), (5, 0), (6, 2), (4, 4), (6, 6), (6, 8), (5, 10), (2, 10), (0, 9)]],
    "4": [[(5, 0), (5, 10)], [(0, 7), (6, 7)], [(5, 0), (0, 7)]],
    "5": [[(6, 0), (0, 0), (0, 5), (4, 5), (6, 7), (6, 8), (4, 10), (0, 10)]],
    "6": [[(6, 1), (4, 0), (1, 0), (0, 2), (0, 8), (1, 10), (5, 10),
           (6, 8), (6, 6), (4, 5), (1, 5)]],
    "7": [[(0, 0), (6, 0)], [(6, 0), (2, 10)]],
    "8": [[(2, 0), (4, 0), (5, 2), (4, 4), (2, 4)],
          [(2, 4), (4, 4), (6, 6), (6, 8), (4, 10), (2, 10), (0, 8), (0, 6), (2, 4)]],
    "9": [[(0, 4), (1, 1), (3, 0), (5, 0), (6, 2), (6, 6), (5, 9), (3, 10), (1, 10)]],
    ".": [[(2, 9), (3, 9), (3, 10), (2, 10)]],
    ",": [[(2, 8), (3, 8), (3, 10), (2, 10)], [(3, 10), (1, 12)]],
    "-": [[(0, 5), (6, 5)]],
    ":": [[(2, 2), (3, 2), (3, 3), (2, 3)], [(2, 7), (3, 7), (3, 8), (2, 8)]],
    ";": [[(2, 2), (3, 2), (3, 3), (2, 3)], [(2, 7), (3, 7), (3, 8), (2, 8)], [(3, 8), (1, 10)]],
    "'": [[(3, 0), (2, 3)]],
    "(": [[(4, 0), (2, 2), (2, 8), (4, 10)]],
    ")": [[(2, 0), (4, 2), (4, 8), (2, 10)]],
    "%": [[(0, 0), (6, 10)], [(1, 1), (2, 1), (2, 3), (1, 3)], [(4, 7), (5, 7), (5, 9), (4, 9)]],
    "/": [[(6, 10), (0, 0)]],
    "&": [[(5, 0), (4, 0), (3, 1), (3, 3), (5, 5), (6, 7), (5, 10), (2, 10), (1, 8), (2, 6), (4, 4)]],
    "+": [[(3, 2), (3, 8)], [(0, 5), (6, 5)]],
    "$": [[(3, 0), (3, 10)],
          [(6, 2), (4, 0), (1, 0), (0, 2), (0, 4), (2, 5), (5, 5), (6, 6), (6, 8), (5, 10), (2, 10), (0, 8)]],
    "=": [[(0, 3), (6, 3)], [(0, 7), (6, 7)]],
    "?": [[(1, 1), (3, 0), (5, 0), (6, 2), (6, 4), (3, 6)], [(3, 8), (3, 9)]],
    "!": [[(3, 0), (3, 7)], [(3, 9), (3, 10)]],
    '"': [[(1, 0), (2, 3)], [(4, 0), (5, 3)]],
    "*": [[(3, 0), (3, 6)], [(0, 2), (6, 4)], [(6, 2), (0, 4)]],
    "\u00b7": [[(2, 4), (3, 4), (3, 5), (2, 5)]],
    " ": [],
}
# Narrow glyphs get a smaller advance so text stays compact and even.
NARROW = {"I": 4, "J": 5, "L": 5, " ": 4, ".": 3, ",": 3, ":": 3, ";": 3,
          "'": 3, "(": 4, ")": 4, "!": 3, "-": 6, "/": 5, "\u00b7": 3}


def adv(ch):
    return NARROW.get(ch, 7)


def text_w(s, size):
    sc = size / 10.0
    return sum(adv(c) * sc + 1.2 * sc for c in s.upper()) - (1.2 * sc if s else 0)


def draw_glyph(x, y, ch, size, col, th):
    sc = size / 10.0
    for stroke in G.get(ch, []):
        pts = [(x + px * sc, y + py * sc) for px, py in stroke]
        for a, b in zip(pts, pts[1:]):
            line(a[0], a[1], b[0], b[1], col, th)


def draw_text(x, y, s, size, col, th=1):
    """Draw text with its top-left corner at (x, y). Returns width used."""
    s = s.upper()
    cx = float(x)
    sc = size / 10.0
    for ch in s:
        draw_glyph(cx, y, ch, size, col, th)
        cx += (adv(ch) + 1.2) * sc
    return cx - x


def draw_center(x, y, w, s, size, col, th=1):
    tw = text_w(s, size)
    draw_text(x + (w - tw) / 2, y, s, size, col, th)


def wrap(s, size, maxw):
    words = s.upper().split()
    lines = []
    cur = ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_block(x, y, s, size, col, maxw, lh=1.5, th=1, align="left"):
    lines = wrap(s, size, maxw)
    yy = y
    for ln in lines:
        if align == "center":
            draw_text(x + (maxw - text_w(ln, size)) / 2, yy, ln, size, col, th)
        else:
            draw_text(x, yy, ln, size, col, th)
        yy += size * lh
    return yy

# ------------------------------------------------------------------- data
# (num, dateline, headline, summary, source, lon, lat)
LEADS = [
    (1, "ODISHA, INDIA - CYCLONE",
     "Cyclone Akvan makes landfall in eastern India",
     "Landfall near Gopalpur 8:30am IST, winds 70-80 km/h; 370,000 evacuated. (IMD)", 85.8, 19.3),
    (2, "KYIV, UKRAINE - WAR",
     "Russia fires wave of ballistic missiles at Kyiv",
     "Barrage kills 3, injures 15; three Dnipro bridges hit. (Reuters)", 30.5, 50.5),
    (3, "ANTALYA, TURKIYE - CLIMATE",
     "COP31 reaches final day deadlocked",
     "Draft omits fossil-fuel phase-out; $120bn fund unresolved. (UN News)", 30.7, 36.9),
]

FEATURES = [
    (4, "SEOUL - TOKYO - MARKETS", "AI sell-off: Asia's worst week since 2020",
     "Nikkei -4.9%, KOSPI -5.4%, TAIEX -6.8% (Reuters)", 127.0, 37.5),
    (5, "SPACE", "BepiColombo reaches Mercury in 8 years",
     "ESA-JAXA craft ends 6bn-mile trip. (ESA, BBC)", -30.0, 10.0),
    (6, "BRUSSELS - EUROPE", "Burnham holds first EU-UK reset summit",
     "Costa and von der Leyen host UK PM. (EU Council)", 4.4, 50.8),
    (7, "TOKYO - ECONOMY", "Japan inflation hits 2.3%; BoJ hike eyed",
     "Oct CPI up from 2.1%; core above 2%. (Reuters)", 139.7, 35.7),
    (8, "BEIJING - RATES", "China holds lending rates for 18th month",
     "1-yr LPR 3.0%, 5-yr 3.5%. (PBOC)", 116.4, 39.9),
    (9, "WELLINGTON - CRICKET", "Phillips makes history with 118 vs India",
     "Century in all formats vs India. (ICC, AP)", 174.8, -41.3),
    (10, "SAN SALVADOR - POLITICS", "Bukele registers for third-term bid",
     "Files for Feb 2027 vote; rights groups object. (AP)", -89.2, 13.7),
    (11, "SENEGAL - MIGRATION", "Migrant boat capsizes off Yemen; 4 dead",
     "Dozens missing from 50-100 aboard. (Al Jazeera)", -17.4, 14.7),
    (12, "ROME - LABOUR", "Italy's CGIL holds 24-hr general strike",
     "Unions rally in 100 squares; transport hit. (AFP)", 12.5, 41.9),
    (13, "BARCELONA - HEALTH", "Cancer pill shrinks tumours 60.7%",
     "Daraxonrasib plus chemo beats chemo alone. (Reuters)", 2.2, 41.4),
]

NUMBERS = [
    ("370,000", "EVACUATED AHEAD OF AKVAN"),
    ("3", "KILLED; 3 BRIDGES HIT"),
    ("-6.8%", "TAIEX INTRADAY LOW"),
    ("2.3%", "JAPAN OCT HEADLINE CPI"),
    ("118", "PHILLIPS MAKES HISTORY"),
    ("8 YRS", "BEPICOLOMBO TO MERCURY"),
]

CHIPS = [("EUROPE 8", NAVY), ("AMERICAS 8", RED), ("ASIA-PACIFIC 9", TEAL),
         ("MIDEAST 4", (176, 110, 20)), ("AFRICA 3", GREEN),
         ("OCEANIA 3", (110, 80, 160)), ("WORLD 1", BLACK)]

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

DATECHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: "
             "the Trump-Xi-Putin Shenzhen summit itself - Anthropic's $83 IPO "
             "pricing - ICJ Myanmar Rohingya genocide verdict - GTA VI midnight "
             "launch - $190.4m Van Gogh sale - Voyager 1 one light-day "
             "confirmation - Senate 48-51 Iran war-powers vote - Crimean Bridge strike.")

# ------------------------------------------------------------- illustrations
def star(cx, cy, r, col):
    for dx, dy in ((-r, 0), (r, 0), (0, -r), (0, r),
                   (-r // 2, -r // 2), (r // 2, -r // 2),
                   (-r // 2, r // 2), (r // 2, r // 2)):
        line(cx - dx, cy - dy, cx + dx, cy + dy, col, 1)
    circle(cx, cy, max(1, r // 3), col)


def art_lead(x, y, w, h, kind):
    rect(x, y, w, h, NAVY if kind != 1 else SEA)
    if kind == 1:
        # Bay of Bengal: sand land on the right, blue sea, white spiral.
        fill_poly([(x + w * 0.55, y), (x + w, y), (x + w, y + h),
                   (x + w * 0.42, y + h), (x + w * 0.62, y + h * 0.55)], SAND)
        cx, cy = x + w * 0.34, y + h * 0.52
        for k, rr in enumerate((34, 26, 18, 11)):
            poly(arc_pts(cx, cy, rr, k * 40, 300 + k * 20), WHITE, 3)
        circle(cx, cy, 5, WHITE)
        circle(x + w * 0.66, y + h * 0.42, 9, RED)
        ring(x + w * 0.66, y + h * 0.42, 13, WHITE, 2)
        draw_text(x + 8, y + 8, "BAY OF", 15, WHITE, 2)
        draw_text(x + 8, y + 26, "BENGAL", 15, WHITE, 2)
        draw_text(x + w * 0.74, y + h * 0.36, "GOPALPUR", 13, WHITE, 2)
    elif kind == 2:
        # Kyiv at night: dark sky, lit windows, missile trails, bursts.
        rect(x, y, w, h, (10, 14, 38))
        for sx, sy in ((30, 18), (90, 30), (170, 14), (240, 26), (290, 16)):
            circle(x + sx, y + sy, 2, WHITE)
        for bx, bw, bh in ((0, 46, 44), (52, 38, 60), (96, 52, 38),
                           (154, 40, 66), (200, 46, 48), (252, 54, 58)):
            rect(x + bx, y + h - bh, bw, bh, (22, 28, 52))
            for wy in range(y + h - bh + 8, y + h - 8, 14):
                for wx in range(x + bx + 8, x + bx + bw - 6, 14):
                    if (wx + wy) % 28 < 14:
                        rect(wx, wy, 4, 5, GOLD)
        for tx, ty, ex, ey in ((70, 6, 130, 62), (210, 2, 160, 58), (290, 10, 250, 64)):
            line(x + tx, y + ty, x + ex, y + ey, (255, 150, 40), 3)
            star(x + ex, y + ey, 7, GOLD)
        draw_text(x + 8, y + 6, "3 BRIDGES HIT", 14, WHITE, 2)
    else:
        # COP31: green globe, thermometer, red COP31 band.
        rect(x, y, w, h, (14, 64, 44))
        cx, cy = x + w * 0.32, y + h * 0.42
        circle(cx, cy, 34, (46, 140, 110))
        ring(cx, cy, 34, (180, 220, 200), 2)
        for a in range(0, 360, 30):
            line(cx + int(30 * math.cos(math.radians(a))),
                 cy + int(30 * math.sin(math.radians(a))),
                 cx - int(30 * math.cos(math.radians(a))),
                 cy - int(30 * math.sin(math.radians(a))), (180, 220, 200), 1)
        line(cx - 34, cy, cx + 34, cy, (180, 220, 200), 1)
        line(cx, cy - 34, cx, cy + 34, (180, 220, 200), 1)
        tx = x + w * 0.72
        rect(tx, y + 14, 10, 52, WHITE)
        rect(tx + 2, y + 16, 6, 34, RED)
        circle(tx + 5, y + 70, 10, RED)
        draw_text(tx + 18, y + 30, "+1.5C", 15, WHITE, 2)
        rect(x, y + h - 26, w, 26, RED)
        draw_center(x, y + h - 23, w, "COP31", 17, WHITE, 2)


def art_feat(x, y, w, h, num):
    if num == 4:
        rect(x, y, w, h, (20, 26, 44))
        poly([(x + 6, y + 18), (x + w * 0.4, y + 22), (x + w * 0.6, y + 28),
              (x + w - 8, y + h - 6)], RED, 3)
        for px, py in ((10, 14), (70, 22), (130, 36), (180, 54)):
            circle(x + px, y + py, 3, GOLD)
        draw_text(x + 6, y + 4, "TAIEX", 12, WHITE, 2)
        draw_text(x + w - 52, y + 4, "-6.8%", 12, RED, 2)
    elif num == 5:
        rect(x, y, w, h, (12, 16, 40))
        for sx, sy in ((14, 8), (60, 16), (120, 6), (170, 20), (90, 26)):
            circle(x + sx, y + sy, 2, WHITE)
        circle(x + w * 0.62, y + h * 0.55, 13, (190, 190, 185))
        circle(x + w * 0.62 - 4, y + h * 0.55 - 3, 3, (160, 160, 155))
        draw_text(x + 6, y + 4, "MERCURY", 11, WHITE, 2)
        draw_text(x + 6, y + 17, "8 YRS", 11, GOLD, 2)
    elif num == 6:
        rect(x, y, w, h, NAVY)
        for i in range(12):
            a = math.radians(i * 30)
            circle(x + w * 0.28 + int(13 * math.cos(a)),
                   y + h * 0.5 + int(13 * math.sin(a)), 2, GOLD)
        # Union Jack, simplified: blue field, white and red crosses.
        ux, uy, uw, uh = x + w * 0.56, y + 6, w * 0.38, h - 12
        rect(ux, uy, uw, uh, (30, 60, 140))
        line(ux, uy, ux + uw, uy + uh, WHITE, 4)
        line(ux + uw, uy, ux, uy + uh, WHITE, 4)
        rect(ux + uw / 2 - 3, uy, 6, uh, WHITE)
        rect(ux, uy + uh / 2 - 3, uw, 6, WHITE)
        rect(ux + uw / 2 - 1, uy, 3, uh, RED)
        rect(ux, uy + uh / 2 - 1, uw, 3, RED)
    elif num == 7:
        rect(x, y, w, h, PAPER2)
        bars = [(6, 12, (120, 120, 115)), (26, 17, (120, 120, 115)),
                (46, 22, RED), (66, 26, RED)]
        for bx, bh, col in bars:
            rect(x + bx, y + h - 4 - bh, 16, bh, col)
        draw_text(x + 6, y + 2, "CPI", 11, INK, 2)
        draw_text(x + w - 46, y + 2, "2.3%", 12, RED, 2)
    elif num == 8:
        rect(x, y, w, h, (232, 222, 200))
        bx, by = x + w * 0.5, y + 4
        fill_poly([(bx - 30, by + 5), (bx, by - 3), (bx + 30, by + 5)], DARKRED)
        for cx in (-22, -8, 8, 22):
            rect(bx + cx - 3, by + 8, 6, 16, NAVY)
        rect(bx - 32, by + 24, 64, 3, NAVY)
    elif num == 9:
        rect(x, y, w, h, GREEN)
        line(x + 20, y + h - 8, x + w - 30, y + 8, (210, 180, 120), 5)
        circle(x + w - 22, y + 12, 6, RED)
        draw_text(x + 6, y + h - 18, "118", 14, WHITE, 2)
    elif num == 10:
        rect(x, y, w, h, (210, 226, 240))
        rect(x + w * 0.5 - 20, y + 10, 40, 18, NAVY)
        rect(x + w * 0.5 - 13, y + 5, 26, 7, (150, 40, 40))
        poly([(x + w * 0.5 - 9, y + 22), (x + w * 0.5 - 2, y + 27),
              (x + w * 0.5 + 11, y + 14)], WHITE, 3)
        draw_text(x + 6, y + 4, "VOTE 2027", 11, NAVY, 2)
    elif num == 11:
        rect(x, y, w, h, SKY)
        fill_poly([(x + 30, y + 10), (x + 70, y + 10), (x + 78, y + 22),
                   (x + 22, y + 22)], (120, 70, 40))
        line(x + 48, y + 10, x + 48, y + 2, INK, 2)
        for wx in (20, 70, 120):
            poly(arc_pts(x + wx, y + 28, 6, 200, 340), SEA, 2)
    elif num == 12:
        rect(x, y, w, h, (240, 232, 214))
        rect(x + 14, y + 8, 74, 22, WHITE)
        frame(x + 14, y + 8, 74, 22, INK, 2)
        line(x + 52, y + 30, x + 52, y + h - 4, INK, 2)
        draw_text(x + 18, y + 12, "24H", 13, RED, 2)
    else:
        rect(x, y, w, h, (222, 236, 238))
        # Capsule: two half-circles joined, red and white.
        cx, cy = x + w * 0.5, y + h * 0.5
        line(cx - 26, cy - 8, cx + 26, cy - 8, RED, 2)
        line(cx - 26, cy + 8, cx + 26, cy + 8, RED, 2)
        poly(arc_pts(cx - 26, cy, 8, 90, 270), RED, 2)
        poly(arc_pts(cx + 26, cy, 8, 270, 90), RED, 2)
        circle(cx - 26, cy, 8, RED)
        circle(cx + 26, cy, 8, WHITE)
        draw_text(x + 6, y + 4, "60.7%", 12, RED, 2)

# ------------------------------------------------------------------- layout
def draw_header():
    rect(0, 0, W, H, CREAM)
    draw_text(24, 10, "THE WORLD IN ONE DAY", 13, RED, 2)
    right = "FRIDAY'S NEWS - ONE PAGE - 36 STORIES - 6 CONTINENTS"
    draw_text(W - 24 - text_w(right, 12), 11, right, 12, INK, 1)
    draw_center(0, 30, W, "FRIDAY 20 NOVEMBER 2026", 54, INK, 3)
    rect(24, 96, W - 48, 4, INK)
    rect(24, 104, W - 48, 1, INK)
    draw_center(0, 110, W,
                "AKVAN STRIKES INDIA - MISSILES HIT KYIV - COP31 DEADLOCKED - ASIAN AI SELL-OFF",
                15, RED, 2)


def draw_numbers():
    y = 132
    cw = (W - 48) / 6.0
    for i, (big, label) in enumerate(NUMBERS):
        x = 24 + i * cw
        if i:
            line(x, y + 2, x, y + 46, GREY, 1)
        draw_center(x, y + 2, cw, big, 25, RED, 2)
        draw_center(x, y + 34, cw, label, 9, INK, 1)
    rect(24, y + 48, W - 48, 1, INK)


def draw_chips():
    y = 188
    total = 0
    widths = []
    for label, _ in CHIPS:
        wdt = text_w(label, 12) + 18
        widths.append(wdt)
        total += wdt + 6
    x = (W - total) / 2
    for (label, col), wdt in zip(CHIPS, widths):
        rect(x, y, wdt, 22, col)
        draw_center(x, y + 5, wdt, label, 12, WHITE, 1)
        x += wdt + 6


def draw_leads():
    y0 = 220
    cw = 312
    gap = 20
    for i, (num, dateline, head, summ, _lon, _lat) in enumerate(LEADS):
        x = 24 + i * (cw + gap)
        frame(x, y0, cw, 186, INK, 1)
        art_lead(x + 1, y0 + 1, cw - 2, 92, i + 1)
        draw_text(x + 8, y0 + 99, str(num) + "  " + dateline, 11, RED, 2)
        yy = draw_block(x + 8, y0 + 114, head, 15, INK, cw - 16, lh=1.25, th=2)
        draw_block(x + 8, yy + 2, summ, 10, INK, cw - 16, lh=1.45, th=1)


def draw_features():
    y0 = 412
    cw = 188
    gap = 8
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            num, dateline, head, summ, _lon, _lat = FEATURES[idx]
            x = 24 + col * (cw + gap)
            y = y0 + row * 100
            frame(x, y, cw, 96, INK, 1)
            art_feat(x + 1, y + 1, cw - 2, 34, num)
            draw_text(x + 5, y + 38, str(num) + " " + dateline, 8, RED, 1)
            yy = draw_block(x + 5, y + 49, head, 10, INK, cw - 10, lh=1.25, th=1)
            draw_block(x + 5, yy, summ, 8, INK, cw - 10, lh=1.3, th=1)


def project(lon, lat, x0, y0, w, h):
    px = x0 + (lon + 180.0) / 360.0 * w
    py = y0 + (90.0 - lat) / 180.0 * h
    return px, py


def draw_map(x0, y0, w, h):
    frame(x0, y0, w, h, INK, 1)
    rect(x0 + 1, y0 + 1, w - 2, h - 2, SKY)
    # Rough continents, drawn as simple polygons on an equirectangular map.
    continents = [
        [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 62),
         (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
         (-105, 20), (-117, 33), (-125, 49), (-150, 60), (-168, 66)],
        [(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -8), (-48, -16),
         (-58, -25), (-65, -35), (-70, -45), (-73, -54), (-70, -35),
         (-62, -20), (-60, -5), (-70, 5), (-80, 10)],
        [(-10, 37), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 58),
         (18, 56), (21, 55), (24, 58), (30, 60), (30, 66), (40, 68), (50, 69),
         (60, 69), (70, 72), (100, 76), (130, 72), (160, 70), (178, 66),
         (170, 60), (158, 52), (142, 45), (135, 43), (127, 40), (122, 32),
         (110, 22), (105, 10), (100, 8), (95, 16), (90, 22), (85, 20),
         (80, 13), (77, 8), (73, 16), (66, 25), (60, 25), (52, 27), (48, 30),
         (44, 39), (36, 36), (30, 36), (26, 38), (23, 36), (19, 40),
         (12, 44), (8, 44), (3, 42), (-2, 37), (-10, 37)],
        [(35, 32), (43, 12), (48, 11), (51, 12), (44, 15), (40, 20),
         (37, 22), (35, 29), (32, 31), (35, 32)],
        [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36),
         (10, 37), (11, 34), (20, 32), (30, 31), (32, 28), (35, 28),
         (38, 22), (40, 15), (42, 11), (44, 10), (48, 11), (51, 12),
         (46, 5), (41, -2), (40, -10), (36, -18), (33, -26), (28, -33),
         (20, -35), (17, -29), (14, -22), (12, -17), (13, -10), (9, -1),
         (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 12), (-17, 15)],
        [(114, -22), (114, -30), (115, -35), (124, -33), (130, -32),
         (135, -35), (140, -38), (146, -39), (150, -37), (153, -27),
         (146, -19), (142, -11), (136, -12), (132, -11), (126, -14),
         (122, -17), (114, -22)],
    ]
    for cont in continents:
        pts = [project(lon, lat, x0 + 1, y0 + 1, w - 2, h - 2) for lon, lat in cont]
        fill_poly(pts, SAND)
    for num, _dl, _h, _s, lon, lat in LEADS + FEATURES:
        px, py = project(lon, lat, x0 + 1, y0 + 1, w - 2, h - 2)
        circle(px, py, 8, RED)
        ring(px, py, 8, WHITE, 1)
        draw_center(px - 8, py - 5, 16, str(num), 9, WHITE, 1)


def draw_bottom():
    y0 = 616
    draw_text(24, y0, "WORLD MAP - WHERE FRIDAY HAPPENED", 13, NAVY, 2)
    draw_text(512, y0, "ALSO ON FRIDAY 20 NOVEMBER - 23 MORE STORIES", 12, RED, 2)
    draw_map(24, y0 + 20, 470, 232)
    yy = y0 + 20
    for num, place, item in ALSO:
        line_txt = str(num) + " " + place + ": " + item
        draw_text(512, yy, line_txt, 8, INK, 1)
        yy += 10
    rect(24, 886, W - 48, 52, (253, 238, 226))
    frame(24, 886, W - 48, 52, RED, 2)
    draw_text(34, 906, "DATE CHECK", 13, RED, 2)
    draw_block(150, 892, DATECHECK, 10, INK, W - 48 - 150, lh=1.45, th=1)
    draw_center(0, 948, W,
                "EVERY STORY HERE HAPPENED, OR WAS FIRST REPORTED, ON FRIDAY 20 NOVEMBER 2026 IN AT LEAST ONE TIME ZONE.",
                10, INK, 1)
    draw_center(0, 966, W,
                "CLAIMS ARE ATTRIBUTED, NOT STATED AS FACT.",
                10, INK, 1)
    draw_center(0, 986, W,
                "SOURCES: REUTERS - AP - AFP - BBC - THE HINDU - IMD - UN NEWS - AL JAZEERA. ORIGINAL VECTOR DRAWINGS.",
                10, GREY, 1)


# ---------------------------------------------------------------------- PNG
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(path):
    raw = b""
    for yy in range(H):
        raw += b"\x00" + bytes(PIX[yy * W * 3:(yy + 1) * W * 3])
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    draw_header()
    draw_numbers()
    draw_chips()
    draw_leads()
    draw_features()
    draw_bottom()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(outdir, exist_ok=True)
    save_png(os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
