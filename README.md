# The World in One Day — Friday, 27 November 2026

[![make.fun](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/noorrahmadi92-coder/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/noorrahmadi92-coder/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127)

One image summing up Friday 27 November 2026's world news: **45 stories
across 9 regions** — 15 numbered cards (3 heroes + 12 grid) plus 30 more
in the "ALSO ON" list, a dotted world map with numbered pins, a UTC
timeline, a "Day in Numbers" strip, a red DATE CHECK box, and a HOW SURE
legend. Every story is tagged REPORTED, CLAIM, ONGOING, CONFIRMED or
OFFICIAL.

## Date gate

Every story on the page happened or was first reported on Friday
27 November 2026 (UTC), verified against a wire or primary source
(Reuters / AP / BBC / Consilium / Electoral Commission NZ / Al Jazeera /
detikJabar / FIDE / TfL / IOL / NWS / UNCTAD). Big stories from earlier
days — the US tariffs, the F-16 sale to Ukraine, the Cairo tanker fire,
the Ibiza tanker capsizing — are named in the red DATE CHECK box as
deliberately left out, not presented as today's news.

## How it is built

`draw.py` (Pillow + DejaVu, no network, no timestamps) renders the
1024×1024 image deterministically: two runs produce a byte-identical
`entry.png`. `main.ts` (Node 22) runs the draw script and checks the
output stays under the competition's 1 MiB limit.

```sh
python3 draw.py   # writes entry.png
```

## Competition

- Bounty: [Sum up 27 November's world news in one image](https://make.fun/bounty/news-image-20261127)
- Prize: $100 shared by the top 50
- Deadline: 29 November 2026, 00:00 UTC
- Entry: `entry.png`, 1024×1024, under 1 MiB
