# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Dimah28/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Dimah28/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

Entry for the make.fun bounty **"Sum up 20 November's world news in one image"** ([news-image-20261120](https://make.fun/bounty/news-image-20261120), $250, ends Sun 22 Nov 2026 07:00 WIB).

## The image

`entry.png` — a 1024×1024 newspaper front page drawn entirely procedurally, in the style of a classic broadsheet:

- masthead: **FRIDAY 20 NOVEMBER 2026** (36 stories · 6 continents · one page)
- three lead stories, each with its own illustration: **Cyclone Akvan makes landfall in eastern India** (370,000 evacuated near Gopalpur), **Russia fires a wave of ballistic missiles at Kyiv** (3 killed, three Dnipro bridges hit) and **COP31 reaches its final day deadlocked** (fossil-fuel phase-out omitted from the draft)
- ten feature cards with mini illustrations: the **AI sell-off sinking Asia** (TAIEX −6.8%), **BepiColombo reaching Mercury after 8 years**, the first **EU–UK reset summit**, **Japan inflation at 2.3%**, **China holding lending rates**, **Phillips' historic 118 vs India**, **Bukele registering for a third term**, a **migrant boat capsizing off Yemen**, **Italy's CGIL 24-hour general strike**, and a **pancreatic cancer pill shrinking tumours 60.7%**
- a **BY THE NUMBERS** band (370,000 evacuated · 3 killed, 3 bridges hit · −6.8% TAIEX · 2.3% Japan CPI · 118 Phillips · 8 yrs to Mercury) and region chips (Europe 8 · Americas 8 · Asia-Pacific 9 · Mideast 4 · Africa 3 · Oceania 3 · World 1)
- a **world map** with numbered pins marking stories 1–13, and **ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES** (stories 14–36, one line each)
- a **DATE CHECK** strip naming Thursday 19 November stories that are deliberately NOT shown as Friday's news (the Shenzhen summit itself, Anthropic's $83 IPO pricing, the ICJ Myanmar verdict, the GTA VI launch, and more)
- footer: sources Reuters · AP · AFP · BBC · The Hindu · IMD · UN News · Al Jazeera, "Original vector drawings."

Every story here happened, or was first reported, on Friday 20 November 2026 in at least one time zone. Claims are attributed, not stated as fact.

## How it is drawn

`main.py` is standard library only (`math`, `os`, `struct`, `zlib`) — no Pillow, no system fonts, no network. All lettering uses a hand-built vector stroke font (polylines on a grid, with true lowercase glyphs), so text stays crisp at any size and never looks pixelated. The cyclone spiral, the Kyiv skyline, the COP31 globe, the mini illustrations and the world map are all drawn with the same small canvas primitives (rectangles, polygons, circles, thick lines).

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
# writes /tmp/out/entry.png — 1024×1024, deterministic (two runs are byte-identical)
```

The grader runs it the same way, read-only, with no network, in under 60 seconds.
