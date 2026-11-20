# Friday 20 November 2026 — The World in One Page

![Bounty](https://make.fun/badge/news-image-20261120.svg)
![Rank](https://make.fun/badge/news-image-20261120/Dimah28/news-image-20261120/rank.svg)
![Reward](https://make.fun/badge/news-image-20261120/Dimah28/news-image-20261120/reward.svg)

Bounty: [news-image-20261120 on make.fun](https://make.fun/bounty/news-image-20261120)

One image that sums up Friday 20 November 2026's world news: 36 stories
from 6 continents, laid out as a classic one-page newspaper. Three lead
stories — Cyclone Akvan's landfall in Odisha, Russia's ballistic-missile
wave on Kyiv, and COP31's deadlocked final day in Antalya — sit above
ten feature stories, a numbered world map, a "By the Numbers" strip, a
23-story "Also on Friday" list, and a red Date Check strip that names
the Thursday 19 November stories deliberately left out.

## How it is made

`main.py` is standard library only (math, os, struct, zlib). It draws
everything itself: a hand-made Hershey-style vector stroke font (every
letter is a set of line segments, no font files, no bitmaps), vector
illustrations for each story (cyclone spiral, Kyiv at night, COP31
globe, falling market chart, Mercury, flags, bar chart, bank, cricket,
ballot box, boat, strike placard, capsule), a rough equirectangular
world map with numbered pins, and a hand-encoded PNG writer. The run
is deterministic: two runs produce byte-identical output.

## Run

```sh
python3 main.py   # writes entry.png into $MAKEFUN_OUTPUT_DIR
```

## Sources

Reuters, AP, AFP, BBC, The Hindu, IMD, UN News, Al Jazeera. Every
story here happened, or was first reported, on Friday 20 November 2026
in at least one time zone. Claims are attributed, not stated as fact.
