# Friday 20 November 2026 — in one picture

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Dimah28/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Dimah28/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

My entry for the make.fun bounty **"Sum up 20 November's world news in one image"** ([news-image-20261120](https://make.fun/bounty/news-image-20261120), $250, entries close Sun 22 Nov 2026 07:00 WIB).

## What the picture shows

`entry.png` is a 1024×1024 broadsheet front page, drawn entirely by `main.py`:

- The masthead reads **Friday 20 November 2026**, with the day's three biggest stories up top: **Cyclone Akvan** coming ashore near Gopalpur (370,000 evacuated), **Russia's ballistic-missile barrage on Kyiv** (3 killed, three Dnipro bridges hit), and **COP31** ending deadlocked on a fossil-fuel phase-out.
- Ten smaller cards cover the **AI sell-off across Asia** (TAIEX −6.8%), **BepiColombo arriving at Mercury after 8 years**, the first **EU–UK reset summit**, **Japan's 2.3% inflation**, **China holding lending rates**, **Phillips' 118 against India**, **Bukele filing for a third term**, a **migrant boat capsizing off Yemen**, **Italy's CGIL general strike**, and a **pancreatic-cancer pill shrinking tumours 60.7%**.
- A **BY THE NUMBERS** strip (370,000 evacuated · 3 killed, 3 bridges hit · −6.8% TAIEX · 2.3% Japan CPI · 118 Phillips · 8 yrs to Mercury), region chips (Europe 8 · Americas 8 · Asia-Pacific 9 · Mideast 4 · Africa 3 · Oceania 3 · World 1), a **world map** with numbered pins for stories 1–13, and **ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES** (stories 14–36, one line each).
- A **DATE CHECK** strip lists Thursday 19 November stories that are deliberately left out of Friday's news (the Shenzhen summit itself, Anthropic's $83 IPO pricing, the ICJ Myanmar verdict, the GTA VI launch, and more).

Every story happened, or was first reported, on Friday 20 November 2026 in at least one time zone, and each claim names its outlet.

## How it is made

`main.py` uses only the Python standard library (`math`, `os`, `struct`, `zlib`): no Pillow, no system fonts, no network. All lettering is a single-stroke vector alphabet written for this page — glyphs stored as lists of polylines, lowercase set as small caps — with per-glyph step widths and 1.4–1.6× line heights, so words never collide and wrapped lines never overlap. The page reads cleanly at full size and at 300 px. The cyclone, the Kyiv skyline, the COP31 globe, the small pictures and the map are built from the same few drawing marks (filled boxes, polygons, dots, strokes).

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
# writes /tmp/out/entry.png — 1024×1024, deterministic (two runs are byte-identical)
```

The grader runs it the same way: read-only, no network, under 60 seconds.
