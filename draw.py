#!/usr/bin/env python3
"""Draw the 27 November 2026 world-news front page (1024x1024, deterministic).

Run: python3 draw.py  ->  writes entry.png next to this file.
No network, no clock, no randomness: the same run always writes the same bytes.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

# ---------------------------------------------------------------- page setup
W, H = 1024, 1024
MX = 14                      # side margin
CW = W - 2 * MX              # content width = 996

PAPER = (247, 242, 231)      # warm newsprint
INK = (24, 24, 22)
NAVY = (22, 35, 63)
NAVY2 = (38, 58, 96)
RED = (178, 35, 27)
RED_DK = (140, 24, 18)
GREY = (110, 104, 92)
LINE = (196, 186, 168)
CARD_BG = (255, 253, 246)
TINT = (233, 226, 210)

REGION_COLORS = {
    "NORTH AMERICA": (46, 109, 180),
    "LATIN AMERICA": (122, 74, 158),
    "EUROPE": (31, 111, 139),
    "MIDDLE EAST": (179, 84, 30),
    "AFRICA": (138, 109, 31),
    "SOUTH ASIA": (192, 57, 43),
    "EAST ASIA": (176, 138, 20),
    "SOUTHEAST ASIA": (46, 139, 87),
    "OCEANIA": (63, 125, 92),
    "WORLD": (85, 85, 85),
}
REGION_SHORT = {
    "NORTH AMERICA": "N. AMERICA", "LATIN AMERICA": "LATIN AM.",
    "EUROPE": "EUROPE", "MIDDLE EAST": "M. EAST", "AFRICA": "AFRICA",
    "SOUTH ASIA": "S. ASIA", "EAST ASIA": "E. ASIA",
    "SOUTHEAST ASIA": "SE ASIA", "OCEANIA": "OCEANIA", "WORLD": "WORLD",
}
REGIONS = [  # (name, count) — counts must sum to 45
    ("NORTH AMERICA", 7), ("EUROPE", 14), ("EAST ASIA", 8),
    ("OCEANIA", 6), ("WORLD", 4), ("SOUTH ASIA", 2),
    ("AFRICA", 2), ("SOUTHEAST ASIA", 1), ("MIDDLE EAST", 1),
]
TAG_COLORS = {
    "OFFICIAL": (31, 111, 139), "REPORTED": (85, 85, 85),
    "ONGOING": (176, 110, 10), "CLAIM": (150, 60, 30),
}

# ---------------------------------------------------------------- fonts
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

F_TITLE = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
F_SERIFB = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)
F_SANSB = lambda s: font("DejaVuSans-Bold.ttf", s)

# Tracks every text that had to be cut to fit (a render warning, not a fix).
TRUNCATED = []

def text_w(f, s):
    return f.getlength(s)

def wrap(f, text, max_w):
    """Greedy word wrap to a pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(f, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def fit_lines(f, text, max_w, max_lines):
    """Wrap, then hard-truncate the last line with an ellipsis if too long."""
    lines = wrap(f, text, max_w)
    if len(lines) <= max_lines:
        return lines
    TRUNCATED.append((text[:48], len(lines), max_lines))
    lines = lines[:max_lines]
    while lines and text_w(f, lines[-1] + " …") > max_w:
        words = lines[-1].split()
        if len(words) <= 1:
            lines[-1] = lines[-1][:-1].rstrip()
        else:
            lines[-1] = " ".join(words[:-1])
    if lines:
        lines[-1] = (lines[-1] + " …").strip()
    return lines

# ---------------------------------------------------------------- the news
# Each card: number, region, place, field, tag, headline, body, source,
# why-it-matters (hero only), icon key, map pin (lat, lon).
CARDS = [
    dict(n=1, region="NORTH AMERICA", place="NEW YORK", field="RETAIL",
         tag="REPORTED",
         head="Black Friday: cautious shoppers, $1tn season",
         body="NRF sees holiday sales +4.2% to just over $1tn; Target, "
              "Dollar Tree and Kohl's flag belt-tightening.",
         src="Reuters",
         why="The season's first big test of US shoppers.",
         icon="bags", pin=(40.7, -74.0)),
    dict(n=2, region="OCEANIA", place="WELLINGTON", field="POLITICS",
         tag="OFFICIAL",
         head="New Zealand hung: Luxon loses majority",
         body="Right bloc 65 of 130, one short of 66; Labour 36, Greens 17, "
              "Opportunity 7. Wong holds the balance.",
         src="Reuters / Electoral Commission",
         why="A kingmaker decides who governs.",
         icon="ballot", pin=(-41.3, 174.8)),
    dict(n=3, region="EUROPE", place="BRUSSELS", field="POLITICS",
         tag="OFFICIAL",
         head="EU summit ends with no deal; de Cos to lead ECB",
         body="No deal on the €1.58tn budget or €45bn Ukraine loan; second "
              "day cancelled. De Cos named next ECB chief.",
         src="Consilium / Reuters",
         why="Europe's money fight rolls to December.",
         icon="stars", pin=(50.8, 4.4)),
    dict(n=4, region="EAST ASIA", place="BEIJING", field="ECONOMY",
         tag="OFFICIAL",
         head="China factory profits jump 16%",
         body="Industrial profits +16% Jan–Oct, official data out Friday; "
              "growth quickens.",
         src="Reuters", icon="factory", pin=(39.9, 116.4)),
    dict(n=5, region="EAST ASIA", place="TOKYO/SEOUL", field="MARKETS",
         tag="REPORTED",
         head="Asia shares extend rebound",
         body="MSCI Asia Pacific +0.6%, a second straight gain; Nikkei +0.7%, "
              "Kospi +1.5%.",
         src="MarketIndex / TopologyPro", icon="markets", pin=(35.7, 139.7)),
    dict(n=6, region="EUROPE", place="GENEVA", field="SPORT",
         tag="REPORTED",
         head="Chess title rests at 1½–1½",
         body="Friday is a rest day; Game 3 (26 Nov) a 60-move draw. Game 4 "
              "on Saturday, Gukesh White.",
         src="Guardian / FIDE", icon="chess", pin=(46.2, 6.1)),
    dict(n=7, region="MIDDLE EAST", place="GAZA", field="CONFLICT",
         tag="REPORTED",
         head="Gaza toll updated: 19 killed in 48 hours",
         body="Al Jazeera: 19 killed in 48 hours; 1,705 since the ceasefire; "
              "74,772 since 7 Oct 2023.",
         src="Al Jazeera", icon="blast", pin=(31.5, 34.5)),
    dict(n=8, region="SOUTHEAST ASIA", place="BOGOR", field="DISASTER",
         tag="REPORTED",
         head="Bogor mine: all 13 dead identified",
         body="All 13 recovered miners identified; search goes on for 13 still "
              "missing after the 23 Nov flood.",
         src="detikJabar / West Java Police", icon="mine", pin=(-6.6, 106.8)),
    dict(n=9, region="NORTH AMERICA", place="NEW YORK", field="MARKETS",
         tag="REPORTED",
         head="Wall Street reopens for a half day",
         body="Markets shut for Thanksgiving reopen and close 13:00 ET; S&P "
              "and Nasdaq futures +~1%.",
         src="Pipback / MarketIndex", icon="bank", pin=(40.7, -74.0)),
    dict(n=10, region="EUROPE", place="MADRID", field="POLITICS",
         tag="REPORTED",
         head="Spain's campaign closes; PP leads into Sunday vote",
         body="Campaign ends Fri; vote Sun. Polls: PP ~31%, PSOE ~29%, "
              "Vox ~18%; 350 seats.",
         src="Reuters", icon="defect", pin=(40.4, -3.7)),
    dict(n=11, region="EUROPE", place="LONDON", field="TRANSPORT",
         tag="REPORTED",
         head="Tube strike hits Friday commute",
         body="First of 8 RMT strikes runs to Fri 11:59; no Piccadilly or "
              "Circle until noon; normal by ~18:00.",
         src="Reuters / TfL", icon="train", pin=(51.5, -0.1)),
    dict(n=12, region="EUROPE", place="IBIZA", field="ACCIDENT",
         tag="REPORTED",
         head="Ibiza tanker: Friday checks begin",
         body="Salvage teams inspect the capsized Med Emre; 7,000 t diesel "
              "aboard, 1 dead, 17 rescued; no major spill.",
         src="BBC / Reuters", icon="ship", pin=(38.98, 1.43)),
    dict(n=13, region="AFRICA", place="JOHANNESBURG", field="POLITICS",
         tag="REPORTED",
         head="Joburg picks a mayor today",
         body="Council votes 10:00 SAST; DA 91 seats, ANC 63, ActionSA 43. "
              "Zille (DA) vs Mashaba (ActionSA).",
         src="IOL / Global South World", icon="city", pin=(-26.2, 28.0)),
    dict(n=14, region="SOUTH ASIA", place="INDIA", field="SPORT",
         tag="REPORTED",
         head="India v NZ: 2nd Test starts today",
         body="India eye a historic series win; the second Test starts Friday.",
         src="EIN", icon="cricket", pin=(22.0, 79.0)),
    dict(n=15, region="WORLD", place="GENEVA", field="DIPLOMACY",
         tag="REPORTED",
         head="UN backs Palestinian recovery aid",
         body="UNCTAD unanimously passes a measure to boost Palestinian "
              "financial recovery and aid.",
         src="UNCTAD", icon="minutes", pin=(46.2, 6.1)),
]

# ALSO ON rows: (number, region, short text, source). Every row is REPORTED.
ALSO = [
    (16, "WORLD", "Bitcoin $61,315, +0.7% Fri morning", "Finnhub"),
    (17, "NORTH AMERICA", "US markets close early at 13:00 ET", "Pipback"),
    (18, "NORTH AMERICA", "Macy's balloons up Fri for Sat parade", "CNN"),
    (19, "NORTH AMERICA", "No official Wall Street close Thu", "Pipback"),
    (20, "NORTH AMERICA", "S&P, Nasdaq futures +~1% at reopen", "MarketIndex"),
    (21, "NORTH AMERICA", "NYC winds ease after 60 mph gusts", "NWS"),
    (22, "EUROPE", "France faces S&P credit review Fri", "FXStreet"),
    (23, "EUROPE", "Spain enters pre-vote silence Fri", "PolitPro"),
    (24, "EUROPE", "Tube: 7 more strike days to 26 Feb", "TfL"),
    (25, "EUROPE", "Ibiza: spill ship on station; slick gone", "BBC"),
    (26, "EUROPE", "Ukraine loan: allies may add €25bn", "EU Council"),
    (27, "EUROPE", "Hungary, Slovakia, Czechia resist link", "europesays"),
    (28, "EUROPE", "Merz: Friday budget talks called off", "europesays"),
    (29, "EUROPE", "Spain: right bloc 51.2% vs left 38.7%", "Portside"),
    (30, "EUROPE", "ASLEF took 4-day week; RMT strikes on", "TfL"),
    (31, "EAST ASIA", "Samsung pays ~3tn won dividend today", "kimkj"),
    (32, "EAST ASIA", "Taiwan TAIEX slips 0.15% at open", "TopologyPro"),
    (33, "EAST ASIA", "Hang Seng opens +36 pts at 22,263", "Longbridge"),
    (34, "EAST ASIA", "HK: Lenovo +2.9%, CATL +2.4% at open", "Longbridge"),
    (35, "EAST ASIA", "Tokyo: Kioxia +3.3%, SoftBank −0.3%", "TradingKey"),
    (36, "EAST ASIA", "Seoul: Samsung +0.9%; SK Hynix −0.2%", "TradingKey"),
    (37, "SOUTH ASIA", "India: GIFT Nifty points to lower open", "7Globe"),
    (38, "OCEANIA", "NZ: special votes skew left; 3 flips", "Reuters"),
    (39, "OCEANIA", "NZ: recounts due 2 Dec, writ 3 Dec", "Electoral Comm."),
    (40, "OCEANIA", "Australia: ASX +0.32% at 8,791.9", "MarketIndex"),
    (41, "OCEANIA", "NZ: Wong, 38, kingmaker; either side", "AP"),
    (42, "OCEANIA", "NZ Parliament shrinks to 130 seats", "Electoral Comm."),
    (43, "AFRICA", "Ekurhuleni mayor vote also due Fri", "Global South"),
    (44, "WORLD", "OPEC+ meets Sun 29 Nov", "Pipback"),
    (45, "WORLD", "F1: Verstappen chases 4th Qatar win", "Bulletin"),
]

NUMBERS = [
    ("65–65", "NZ hung parliament"),
    ("+16%", "China factory profits"),
    ("$1tn", "NRF holiday sales forecast"),
    ("$61,315", "Bitcoin Fri morning"),
    ("€45bn", "EU Ukraine loan backed"),
    ("1½–1½", "chess at rest day"),
]

TIMELINE = [
    ("00:30", "EU no deal"), ("01:00", "NZ hung"),
    ("01:30", "China +16%"), ("02:10", "BTC $61,315"),
    ("08:00", "Joburg vote"), ("18:00", "US close"),
    ("19:00", "Macy's up"),
]

DATE_CHECK = (
    "Left out — earlier days, not 27 Nov: "
    "US tariffs on 14 partners (25 Nov) · F-16 sale to Ukraine (25 Nov) · "
    "Cairo tanker fire, 31 dead (25 Nov) · Gaza minister killed "
    "(26 Nov) · Houthi strikes (25–26 Nov) · Kuwait drone strike "
    "(26 Nov) · Bangkok refinery blast (26 Nov) · Ibiza tanker capsizes "
    "(26 Nov) · Trabuco Brazil post (26 Nov)."
)

FOOTER_SOURCES = (
    "Sources: Reuters, AP, BBC, Consilium, Electoral Commission NZ, NWS, "
    "Al Jazeera, detikJabar, FIDE, Guardian, TfL, IOL, CNN, MarketIndex, "
    "TradingKey, Longbridge, Finnhub, Pipback, EIN, UNCTAD. Every drawing original."
)

# ---------------------------------------------------------------- icons
# Each icon draws one small original scene inside (x0,y0,x1,y1).
def _skyline(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(52, 68, 96))
    d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(28, 38, 60))
    import math
    # buildings
    bx = x0 + w * 0.06
    for bw, bh in ((0.16, 0.62), (0.12, 0.85), (0.18, 0.55), (0.12, 0.95),
                   (0.16, 0.7), (0.12, 0.5)):
        d.rectangle([bx, y1 - h * bh, bx + w * bw, y1], fill=(16, 22, 38))
        for wy in range(3):
            d.rectangle([bx + 2, y1 - h * bh + 4 + wy * 7, bx + w * bw - 2,
                         y1 - h * bh + 7 + wy * 7], fill=(240, 200, 90))
        bx += w * (bw + 0.03)
    # rain slashes
    for i in range(9):
        rx = x0 + w * (0.05 + 0.11 * i)
        ry = y0 + h * (0.08 + (i % 3) * 0.12)
        d.line([rx, ry, rx - 5, ry + 12], fill=(180, 210, 240), width=2)
    # wind arc
    d.arc([x0 + w * 0.62, y0 + h * 0.05, x0 + w * 0.98, y0 + h * 0.4],
          200, 340, fill=(255, 255, 255), width=2)

def _memorial(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(232, 222, 196))
    cx, base = x0 + w * 0.5, y1 - h * 0.12
    # Gateway arch
    d.rectangle([cx - w * 0.30, base - h * 0.62, cx + w * 0.30, base],
                fill=(196, 150, 90))
    d.pieslice([cx - w * 0.30, base - h * 0.98, cx + w * 0.30, base - h * 0.26],
               180, 360, fill=(196, 150, 90))
    d.pieslice([cx - w * 0.17, base - h * 0.72, cx + w * 0.17, base - h * 0.20],
               180, 360, fill=(232, 222, 196))
    d.rectangle([cx - w * 0.17, base - h * 0.46, cx + w * 0.17, base],
                fill=(232, 222, 196))
    d.rectangle([cx - w * 0.34, base, cx + w * 0.34, base + h * 0.06],
                fill=(140, 100, 55))
    # three candles
    for i, fx in enumerate((0.22, 0.5, 0.78)):
        fx0 = x0 + w * fx
        d.rectangle([fx0 - 3, base - 12, fx0 + 3, base], fill=(255, 255, 255),
                    outline=(120, 110, 90))
        d.ellipse([fx0 - 4, base - 22, fx0 + 4, base - 12],
                  fill=(240, 160, 40))

def _markets(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(20, 40, 58))
    # grid
    for i in range(1, 4):
        d.line([x0, y0 + h * i / 4, x1, y0 + h * i / 4], fill=(45, 70, 95))
    pts = [(x0 + w * f, y0 + h * v) for f, v in
           ((0.05, 0.78), (0.2, 0.66), (0.35, 0.72), (0.5, 0.5),
            (0.65, 0.55), (0.8, 0.3), (0.95, 0.16))]
    d.line(pts, fill=(90, 220, 130), width=3, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 11, ey + 2), (ex - 2, ey + 11)], fill=(90, 220, 130))
    d.text((x0 + w * 0.06, y0 + h * 0.38), "+1.9%", font=F_SANSB(13),
           fill=(90, 220, 130))

def _bank(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(238, 232, 214))
    cx = x0 + w * 0.5
    d.polygon([(cx - w * 0.38, y0 + h * 0.34), (cx + w * 0.38, y0 + h * 0.34),
               (cx, y0 + h * 0.10)], fill=(70, 90, 120))
    for i in range(4):
        px = x0 + w * (0.18 + 0.21 * i)
        d.rectangle([px, y0 + h * 0.38, px + w * 0.07, y1 - h * 0.16],
                    fill=(120, 130, 145))
    d.rectangle([x0 + w * 0.12, y1 - h * 0.16, x0 + w * 0.88, y1 - h * 0.08],
                fill=(70, 90, 120))

def _yen(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(24, 44, 66))
    d.text((x0 + w * 0.08, y0 + h * 0.10), "¥", font=F_SANSB(int(h * 0.55)),
           fill=(250, 210, 90))
    pts = [(x0 + w * f, y0 + h * v) for f, v in
           ((0.55, 0.85), (0.68, 0.62), (0.8, 0.68), (0.93, 0.42))]
    d.line(pts, fill=(120, 220, 160), width=3, joint="curve")

def _ship(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(214, 232, 238))
    # containers
    cols = [(200, 60, 50), (40, 110, 160), (220, 160, 40), (60, 140, 80)]
    cx = x0 + w * 0.10
    for i, c in enumerate(cols):
        d.rectangle([cx, y0 + h * (0.30 + 0.16 * (i % 2)), cx + w * 0.17,
                     y0 + h * (0.46 + 0.16 * (i % 2))], fill=c,
                    outline=(255, 255, 255))
        cx += w * 0.18
    # hull
    d.polygon([(x0 + w * 0.04, y0 + h * 0.52), (x0 + w * 0.96, y0 + h * 0.52),
               (x0 + w * 0.88, y0 + h * 0.78), (x0 + w * 0.12, y0 + h * 0.78)],
              fill=(30, 50, 80))
    for i in range(3):
        d.arc([x0 + w * (0.08 + 0.3 * i), y0 + h * 0.80, x0 + w * (0.32 + 0.3 * i),
               y0 + h * 0.98], 0, 180, fill=(40, 110, 160), width=2)

def _chess(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    s = min(w, h) * 0.86
    ox, oy = x0 + (w - s) / 2, y0 + (h - s) / 2
    cell = s / 4
    for r in range(4):
        for c in range(4):
            col = (245, 240, 225) if (r + c) % 2 == 0 else (60, 50, 40)
            d.rectangle([ox + c * cell, oy + r * cell,
                         ox + (c + 1) * cell, oy + (r + 1) * cell], fill=col)
    d.ellipse([ox + 0.6 * cell, oy + 0.5 * cell, ox + 1.4 * cell, oy + 1.3 * cell],
              fill=(255, 255, 255), outline=(30, 30, 30), width=2)
    d.ellipse([ox + 2.6 * cell, oy + 2.5 * cell, ox + 3.4 * cell, oy + 3.3 * cell],
              fill=(25, 25, 25), outline=(200, 200, 200), width=2)

def _stars(d, x0, y0, x1, y1, accent):
    import math
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(30, 55, 110))
    cx, cy, r = x0 + w * 0.5, y0 + h * 0.46, min(w, h) * 0.36
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(250, 210, 90))
    d.rectangle([cx - w * 0.16, cy - h * 0.10, cx + w * 0.16, cy + h * 0.10],
                fill=(255, 255, 255))
    d.rectangle([cx - w * 0.16, cy - h * 0.10, cx + w * 0.16, cy - h * 0.02],
                fill=(200, 40, 40))

def _minutes(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(238, 234, 222))
    d.rectangle([x0 + w * 0.12, y0 + h * 0.12, x0 + w * 0.62, y1 - h * 0.12],
                fill=(255, 255, 255), outline=(120, 120, 120))
    for i in range(4):
        d.line([x0 + w * 0.18, y0 + h * (0.24 + 0.14 * i),
                x0 + w * 0.56, y0 + h * (0.24 + 0.14 * i)],
               fill=(90, 90, 90), width=2)
    d.ellipse([x0 + w * 0.66, y0 + h * 0.18, x0 + w * 0.94, y0 + h * 0.52],
              fill=(255, 255, 255), outline=(40, 60, 100), width=2)
    d.line([x0 + w * 0.80, y0 + h * 0.35, x0 + w * 0.80, y0 + h * 0.25],
           fill=(40, 60, 100), width=2)
    d.line([x0 + w * 0.80, y0 + h * 0.35, x0 + w * 0.88, y0 + h * 0.35],
           fill=(40, 60, 100), width=2)
    d.text((x0 + w * 0.68, y0 + h * 0.62), "€", font=F_SANSB(int(h * 0.3)),
           fill=(40, 60, 100))

def _intercept(d, x0, y0, x1, y1, accent):
    import math
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(40, 34, 30))
    cx, cy = x0 + w * 0.30, y0 + h * 0.42
    for i in range(8):
        a = math.pi * i / 4
        d.line([cx, cy, cx + w * 0.24 * math.cos(a), cy + h * 0.30 * math.sin(a)],
               fill=(250, 180, 60), width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(250, 220, 120))
    # shield
    sx, sy = x0 + w * 0.72, y0 + h * 0.30
    d.polygon([(sx, sy), (sx + w * 0.20, sy + h * 0.06),
               (sx + w * 0.20, sy + h * 0.34), (sx + w * 0.10, sy + h * 0.50),
               (sx, sy + h * 0.34)], fill=(60, 120, 180),
              outline=(255, 255, 255))
    d.line([(sx + w * 0.04, sy + h * 0.26), (sx + w * 0.09, sy + h * 0.33),
            (sx + w * 0.17, sy + h * 0.16)], fill=(255, 255, 255), width=3)

def _cross(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(226, 238, 230))
    cx, cy = x0 + w * 0.5, y0 + h * 0.48
    d.ellipse([cx - w * 0.26, cy - h * 0.30, cx + w * 0.26, cy + h * 0.30],
              fill=(255, 255, 255), outline=(180, 60, 50), width=2)
    d.rectangle([cx - 4, cy - 16, cx + 4, cy + 16], fill=(200, 50, 40))
    d.rectangle([cx - 16, cy - 4, cx + 16, cy + 4], fill=(200, 50, 40))
    for (vx, vy) in ((0.16, 0.2), (0.84, 0.24), (0.82, 0.8)):
        px, py = x0 + w * vx, y0 + h * vy
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(120, 90, 140))

def _naira(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(24, 44, 40))
    d.text((x0 + w * 0.06, y0 + h * 0.08), "₦", font=F_SANSB(int(h * 0.5)),
           fill=(250, 210, 90))
    pts = [(x0 + w * f, y0 + h * v) for f, v in
           ((0.52, 0.30), (0.66, 0.55), (0.80, 0.48), (0.94, 0.82))]
    d.line(pts, fill=(240, 90, 70), width=3, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 11, ey - 2), (ex - 2, ey - 11)], fill=(240, 90, 70))

def _defect(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(238, 232, 218))
    # two benches: left blue, right gold
    d.rectangle([x0 + w * 0.08, y0 + h * 0.55, x0 + w * 0.38, y1 - h * 0.14],
                fill=(60, 100, 160))
    d.rectangle([x0 + w * 0.62, y0 + h * 0.55, x0 + w * 0.92, y1 - h * 0.14],
                fill=(200, 160, 40))
    d.polygon([(x0 + w * 0.40, y0 + h * 0.30), (x0 + w * 0.60, y0 + h * 0.30),
               (x0 + w * 0.60, y0 + h * 0.22), (x0 + w * 0.72, y0 + h * 0.38),
               (x0 + w * 0.60, y0 + h * 0.54), (x0 + w * 0.60, y0 + h * 0.46),
               (x0 + w * 0.40, y0 + h * 0.46)], fill=RED)
    d.ellipse([x0 + w * 0.44, y0 + h * 0.60, x0 + w * 0.56, y0 + h * 0.74],
              fill=(255, 255, 255), outline=(30, 30, 30), width=2)

def _ambulance(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(228, 236, 240))
    d.rectangle([x0 + w * 0.08, y0 + h * 0.30, x0 + w * 0.78, y0 + h * 0.72],
                fill=(255, 255, 255), outline=(180, 40, 40), width=2)
    d.polygon([(x0 + w * 0.78, y0 + h * 0.42), (x0 + w * 0.94, y0 + h * 0.52),
               (x0 + w * 0.94, y0 + h * 0.72), (x0 + w * 0.78, y0 + h * 0.72)],
              fill=(255, 255, 255), outline=(180, 40, 40))
    d.rectangle([x0 + w * 0.38, y0 + h * 0.38, x0 + w * 0.50, y0 + h * 0.64],
                fill=(200, 50, 40))
    d.rectangle([x0 + w * 0.43, y0 + h * 0.33, x0 + w * 0.45, y0 + h * 0.69],
                fill=(255, 255, 255))
    d.rectangle([x0 + w * 0.33, y0 + h * 0.48, x0 + w * 0.55, y0 + h * 0.54],
                fill=(255, 255, 255))
    for wx in (0.24, 0.80):
        cx = x0 + w * wx
        d.ellipse([cx - 7, y0 + h * 0.70, cx + 7, y0 + h * 0.86], fill=(30, 30, 30))

def _blast(d, x0, y0, x1, y1, accent):
    import math
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(60, 50, 42))
    cx, cy = x0 + w * 0.5, y0 + h * 0.42
    for i in range(10):
        a = math.pi * i / 5
        r = w * (0.30 if i % 2 == 0 else 0.18)
        d.line([cx, cy, cx + r * math.cos(a), cy + r * 0.9 * math.sin(a)],
               fill=(250, 170, 50), width=4)
    d.ellipse([cx - 10, cy - 8, cx + 10, cy + 8], fill=(250, 220, 120))
    for bx in (0.14, 0.68):
        d.rectangle([x0 + w * bx, y1 - h * 0.30, x0 + w * (bx + 0.18),
                     y1 - h * 0.06], fill=(120, 110, 100),
                    outline=(60, 55, 50))
        d.line([x0 + w * bx, y1 - h * 0.22, x0 + w * (bx + 0.18), y1 - h * 0.22],
               fill=(60, 55, 50))

def _bags(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(238, 228, 210))
    # big red bag
    d.rectangle([x0 + w * 0.12, y0 + h * 0.34, x0 + w * 0.52, y1 - h * 0.10],
                fill=(178, 35, 27))
    d.arc([x0 + w * 0.20, y0 + h * 0.14, x0 + w * 0.44, y0 + h * 0.44],
          180, 360, fill=(90, 30, 25), width=3)
    d.text((x0 + w * 0.24, y0 + h * 0.50), "$", font=F_SANSB(int(h * 0.32)),
           fill=(255, 255, 255))
    # small navy bag
    d.rectangle([x0 + w * 0.56, y0 + h * 0.44, x0 + w * 0.90, y1 - h * 0.10],
                fill=(38, 58, 96))
    d.arc([x0 + w * 0.63, y0 + h * 0.26, x0 + w * 0.83, y0 + h * 0.52],
          180, 360, fill=(20, 30, 55), width=3)
    d.text((x0 + w * 0.66, y0 + h * 0.56), "%", font=F_SANSB(int(h * 0.26)),
           fill=(255, 255, 255))

def _ballot(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(232, 236, 240))
    # ballot paper going into the slot
    d.rectangle([x0 + w * 0.34, y0 + h * 0.08, x0 + w * 0.66, y0 + h * 0.44],
                fill=(255, 255, 255), outline=(120, 120, 120))
    d.line([x0 + w * 0.40, y0 + h * 0.30, x0 + w * 0.46, y0 + h * 0.38,
            x0 + w * 0.60, y0 + h * 0.18], fill=(40, 140, 70), width=3)
    # box
    d.rectangle([x0 + w * 0.14, y0 + h * 0.44, x0 + w * 0.86, y1 - h * 0.10],
                fill=(38, 58, 96))
    d.rectangle([x0 + w * 0.38, y0 + h * 0.44, x0 + w * 0.62, y0 + h * 0.50],
                fill=(20, 30, 55))
    d.text((x0 + w * 0.30, y0 + h * 0.58), "VOTE",
           font=F_SANSB(int(h * 0.20)), fill=(255, 255, 255))

def _factory(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(214, 226, 232))
    # chimney with smoke
    d.rectangle([x0 + w * 0.72, y0 + h * 0.14, x0 + w * 0.84, y0 + h * 0.72],
                fill=(120, 110, 100))
    for fx, fy, r in ((0.78, 0.10, 4), (0.70, 0.05, 3)):
        d.ellipse([x0 + w * fx - r, y0 + h * fy - r, x0 + w * fx + r,
                   y0 + h * fy + r], fill=(200, 200, 200))
    # sawtooth roof + body
    d.polygon([(x0 + w * 0.06, y0 + h * 0.72), (x0 + w * 0.06, y0 + h * 0.42),
               (x0 + w * 0.26, y0 + h * 0.26), (x0 + w * 0.26, y0 + h * 0.42),
               (x0 + w * 0.46, y0 + h * 0.26), (x0 + w * 0.46, y0 + h * 0.42),
               (x0 + w * 0.66, y0 + h * 0.26), (x0 + w * 0.66, y0 + h * 0.72)],
              fill=(70, 90, 120))
    d.rectangle([x0 + w * 0.06, y0 + h * 0.72, x0 + w * 0.66, y1 - h * 0.08],
                fill=(90, 110, 140))
    for i in range(3):
        d.rectangle([x0 + w * (0.13 + 0.18 * i), y0 + h * 0.78,
                     x0 + w * (0.23 + 0.18 * i), y0 + h * 0.90],
                    fill=(250, 210, 90))

def _mine(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(196, 178, 140))
    # hillside
    d.polygon([(x0, y1), (x0, y0 + h * 0.55), (x1, y0 + h * 0.30),
               (x1, y1)], fill=(140, 115, 75))
    # tunnel mouth
    cx = x0 + w * 0.5
    d.pieslice([cx - w * 0.22, y0 + h * 0.34, cx + w * 0.22, y0 + h * 0.98],
               180, 360, fill=(30, 25, 20))
    d.rectangle([cx - w * 0.22, y0 + h * 0.66, cx + w * 0.22, y1 - h * 0.06],
                fill=(30, 25, 20))
    # timber frame
    d.rectangle([cx - w * 0.26, y0 + h * 0.62, cx + w * 0.26, y0 + h * 0.70],
                fill=(110, 80, 45))
    # rails
    d.line([x0 + w * 0.30, y1 - h * 0.04, cx - w * 0.06, y0 + h * 0.82],
           fill=(200, 200, 200), width=2)
    d.line([x0 + w * 0.70, y1 - h * 0.04, cx + w * 0.06, y0 + h * 0.82],
           fill=(200, 200, 200), width=2)
    # lamp
    d.ellipse([cx - 4, y0 + h * 0.44, cx + 4, y0 + h * 0.54],
              fill=(250, 210, 90))

def _train(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(30, 40, 55))
    # tunnel arch
    d.pieslice([x0 + w * 0.06, y0 + h * 0.02, x0 + w * 0.94, y0 + h * 0.98],
               180, 360, fill=(60, 70, 85))
    # train front
    tx0, tx1 = x0 + w * 0.24, x0 + w * 0.76
    d.rounded_rectangle([tx0, y0 + h * 0.22, tx1, y1 - h * 0.12], radius=8,
                        fill=(200, 40, 40))
    d.rectangle([tx0 + 4, y0 + h * 0.30, tx1 - 4, y0 + h * 0.52],
                fill=(220, 235, 245))
    for hx in (0.34, 0.62):
        cx = x0 + w * hx
        d.ellipse([cx - 5, y0 + h * 0.62, cx + 5, y0 + h * 0.74],
                  fill=(250, 220, 120))
    # rails
    d.line([x0 + w * 0.30, y1 - h * 0.06, x0 + w * 0.44, y0 + h * 0.92],
           fill=(180, 180, 180), width=2)
    d.line([x0 + w * 0.70, y1 - h * 0.06, x0 + w * 0.56, y0 + h * 0.92],
           fill=(180, 180, 180), width=2)

def _cricket(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(120, 170, 90))
    # pitch strip
    d.rectangle([x0 + w * 0.36, y0, x0 + w * 0.64, y1], fill=(214, 196, 150))
    # stumps
    for sx in (0.42, 0.50, 0.58):
        d.rectangle([x0 + w * sx, y0 + h * 0.12, x0 + w * sx + 3,
                     y0 + h * 0.30], fill=(250, 220, 120))
    # bat, leaning
    d.polygon([(x0 + w * 0.60, y0 + h * 0.30), (x0 + w * 0.72, y0 + h * 0.30),
               (x0 + w * 0.86, y0 + h * 0.86), (x0 + w * 0.74, y0 + h * 0.86)],
              fill=(200, 160, 100), outline=(120, 85, 50))
    d.line([x0 + w * 0.66, y0 + h * 0.30, x0 + w * 0.56, y0 + h * 0.14],
           fill=(120, 85, 50), width=3)
    # ball
    d.ellipse([x0 + w * 0.16, y0 + h * 0.66, x0 + w * 0.16 + 12,
               y0 + h * 0.66 + 12], fill=(178, 35, 27),
              outline=(255, 255, 255))

def _city(d, x0, y0, x1, y1, accent):
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(220, 228, 236))
    cx = x0 + w * 0.5
    # flag pole + flag
    d.line([cx, y0 + h * 0.02, cx, y0 + h * 0.10], fill=(60, 100, 160), width=2)
    d.polygon([(cx, y0 + h * 0.02), (cx + w * 0.09, y0 + h * 0.045),
               (cx, y0 + h * 0.07)], fill=RED)
    # dome
    d.pieslice([cx - w * 0.20, y0 + h * 0.08, cx + w * 0.20, y0 + h * 0.48],
               180, 360, fill=(60, 100, 160))
    # pediment + columns
    d.polygon([(cx - w * 0.36, y0 + h * 0.48), (cx + w * 0.36, y0 + h * 0.48),
               (cx, y0 + h * 0.32)], fill=(90, 110, 130))
    for i in range(4):
        px = x0 + w * (0.20 + 0.20 * i)
        d.rectangle([px, y0 + h * 0.52, px + w * 0.06, y1 - h * 0.14],
                    fill=(245, 245, 240), outline=(150, 150, 150))
    d.rectangle([x0 + w * 0.14, y1 - h * 0.14, x0 + w * 0.86, y1 - h * 0.06],
                fill=(90, 110, 130))

ICONS = {"storm": _skyline, "memorial": _memorial, "markets": _markets,
         "bank": _bank, "yen": _yen, "ship": _ship, "chess": _chess,
         "stars": _stars, "minutes": _minutes, "intercept": _intercept,
         "cross": _cross, "naira": _naira, "defect": _defect,
         "ambulance": _ambulance, "blast": _blast, "bags": _bags,
         "ballot": _ballot, "factory": _factory, "mine": _mine,
         "train": _train, "cricket": _cricket, "city": _city}

# ---------------------------------------------------------------- world map
# Hand-drawn land mask: 72 columns (5 deg each, lon -180..180) x 36 rows.
# Ranges are (first_col, last_col) inclusive per row; row r covers
# lat 90-5r-5 .. 90-5r.
LAND_ROWS = {
    1: [(19, 23), (24, 31)],
    2: [(12, 20), (24, 32), (38, 41)],
    3: [(2, 8), (8, 22), (25, 31), (39, 42), (49, 71)],
    4: [(2, 8), (8, 24), (26, 30), (31, 33), (37, 42), (42, 71)],
    5: [(3, 8), (9, 25), (27, 28), (35, 36), (37, 43), (43, 71)],
    6: [(10, 27), (35, 36), (37, 40), (41, 71)],
    7: [(11, 27), (35, 44), (44, 71)],
    8: [(12, 27), (35, 42), (44, 55), (55, 68), (64, 65)],
    9: [(13, 26), (34, 42), (42, 46), (47, 56), (56, 66), (62, 64)],
    10: [(13, 25), (34, 36), (38, 41), (42, 48), (50, 56), (56, 66), (62, 64)],
    11: [(14, 25), (34, 43), (43, 49), (50, 55), (57, 66)],
    12: [(14, 24), (34, 44), (44, 49), (51, 55), (58, 62), (64, 64)],
    13: [(15, 21), (34, 45), (45, 49), (52, 55), (58, 62), (60, 61)],
    14: [(16, 20), (33, 46), (53, 55), (58, 61), (60, 61)],
    15: [(17, 20), (34, 47), (54, 54), (58, 63)],
    16: [(21, 24), (35, 47), (58, 66), (64, 66)],
    17: [(21, 27), (36, 47), (59, 67), (65, 67)],
    18: [(22, 28), (37, 47), (60, 67)],
    19: [(23, 28), (38, 47), (61, 66), (62, 64)],
    20: [(23, 29), (39, 46), (44, 46), (60, 67)],
    21: [(24, 29), (39, 45), (45, 46), (60, 67)],
    22: [(24, 29), (39, 45), (60, 66)],
    23: [(24, 29), (40, 44), (61, 66), (70, 71)],
    24: [(25, 29), (40, 43), (61, 66), (70, 71)],
    25: [(25, 28), (62, 65), (69, 71)],
    26: [(25, 27), (70, 70)],
    27: [(26, 27)],
    28: [(26, 26)],
}

def draw_map(d, mx0, my0, mw, mh):
    """Dotted world map (lat 90..-55) with numbered pins for cards 1-15."""
    cols, rows = 72, 29
    cw, ch = mw / cols, mh / rows
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=(238, 234, 222))
    for r, spans in LAND_ROWS.items():
        for a, b in spans:
            for c in range(a, b + 1):
                cx = mx0 + (c + 0.5) * cw
                cy = my0 + (r + 0.5) * ch
                d.ellipse([cx - 2.0, cy - 2.0, cx + 2.0, cy + 2.0],
                          fill=(175, 158, 125))
    # pins
    for card in CARDS:
        lat, lon = card["pin"]
        px = mx0 + (lon + 180) / 360 * mw
        py = my0 + (90 - lat) / 145 * mh
        if card["n"] in (9, 15):  # shares a pin with cards 1 and 6: nudge so both show
            px += 10
            py -= 7
        col = REGION_COLORS[card["region"]]
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col,
                  outline=(255, 255, 255), width=1)
        num = str(card["n"])
        f = F_SANSB(8)
        d.text((px - f.getlength(num) / 2, py - 5.5), num, font=f,
               fill=(255, 255, 255))
    return

# ---------------------------------------------------------------- small parts
def tag_pill(d, x, y, tag):
    """Right-aligned status pill; returns its left edge."""
    f = F_SANSB(8)
    tw = f.getlength(tag) + 8
    col = TAG_COLORS.get(tag, (85, 85, 85))
    d.rounded_rectangle([x - tw, y, x, y + 12], radius=3, fill=col)
    d.text((x - tw + 4, y + 1.5), tag, font=f, fill=(255, 255, 255))
    return x - tw

def number_badge(d, cx, cy, n, r=9):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
              outline=(255, 255, 255), width=1)
    f = F_SANSB(10)
    s = str(n)
    d.text((cx - f.getlength(s) / 2, cy - 7), s, font=f, fill=(255, 255, 255))

def kicker_line(d, x, y, w, card):
    """Place · field in the region colour, tag pill at the right."""
    col = REGION_COLORS[card["region"]]
    f = F_SANSB(9)
    kick = f"{card['place']} · {card['field']}"
    d.text((x, y), kick, font=f, fill=col)
    tag_pill(d, x + w, y, card["tag"])

# ---------------------------------------------------------------- cards
def draw_hero(d, x, y, w, h, card):
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE)
    ICONS[card["icon"]](d, x + 1, y + 1, x + w - 1, y + 57,
                        REGION_COLORS[card["region"]])
    number_badge(d, x + 15, y + 15, card["n"], r=10)
    kicker_line(d, x + 8, y + 62, w - 16, card)
    f = F_SERIFB(15)
    lines = fit_lines(f, card["head"], w - 16, 2)
    yy = y + 77
    for ln in lines:
        d.text((x + 8, yy), ln, font=f, fill=INK)
        yy += 18
    f = F_SANS(10)
    lines = fit_lines(f, card["body"], w - 16, 2)
    for ln in lines:
        d.text((x + 8, yy), ln, font=f, fill=(50, 48, 44))
        yy += 12.5
    why = card.get("why")
    if why:
        fw = F_SANSB(9.5)
        lead = "WHY IT MATTERS  "
        d.text((x + 8, yy + 1.5), lead, font=fw, fill=RED)
        rest = fit_lines(F_SANS(9.5), why, w - 16 - fw.getlength(lead), 1)
        if rest:
            d.text((x + 8 + fw.getlength(lead), yy + 1.5), rest[0],
                   font=F_SANS(9.5), fill=(50, 48, 44))

def draw_grid(d, x, y, w, h, card):
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE)
    ICONS[card["icon"]](d, x + 1, y + 1, x + 84, y + h - 1,
                        REGION_COLORS[card["region"]])
    number_badge(d, x + 14, y + 14, card["n"], r=9)
    tx, tw = x + 92, w - 100
    kicker_line(d, tx, y + 5, tw, card)
    f = F_SERIFB(12)
    lines = fit_lines(f, card["head"], tw, 2)
    yy = y + 19
    for ln in lines:
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += 15
    f = F_SANS(9)
    lines = fit_lines(f, card["body"], tw, 3)
    for ln in lines:
        d.text((tx, yy), ln, font=f, fill=(50, 48, 44))
        yy += 11.5

# ---------------------------------------------------------------- also on
def draw_also(d, ax0, ay, col_w, rows_h):
    """30 one-liners in 2 columns; auto-trims any row that would overflow."""
    f = F_SANS(8.5)
    fb = F_SANSB(8.5)
    warnings = []
    row_h = 14
    per_col = 15
    for ci in range(2):
        rows = ALSO[ci * per_col:(ci + 1) * per_col]
        cx = ax0 + ci * (col_w + 8)
        yy = ay
        for n, region, text, src in rows:
            tag = "[REPORTED]"
            full = f"{n} {text} {tag} {src}"
            trimmed = False
            while f.getlength(full) > col_w and len(text) > 12:
                text = text.rsplit(" ", 1)[0] + " …"
                full = f"{n} {text} {tag} {src}"
                trimmed = True
            if trimmed:
                warnings.append(f"ALSO {n} trimmed to fit: '{text}'")
            if f.getlength(full) > col_w:
                warnings.append(f"ALSO {n} still wide: {f.getlength(full):.0f}px")
            d.text((cx, yy), str(n), font=fb, fill=RED)
            nx = cx + fb.getlength(str(n)) + 4
            d.text((nx, yy), text, font=f, fill=INK)
            tx = nx + f.getlength(text) + 4
            d.text((tx, yy), tag, font=fb, fill=GREY)
            sx = tx + fb.getlength(tag) + 4
            d.text((sx, yy), src, font=f, fill=GREY)
            yy += row_h
    return warnings

# ---------------------------------------------------------------- page
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # top bar
    d.rectangle([0, 0, W, 22], fill=NAVY)
    d.text((MX, 5), "THE WORLD IN ONE DAY", font=F_SANSB(11),
           fill=(255, 255, 255))
    right = "45 STORIES · 9 REGIONS · ALL FROM THIS ONE DAY"
    f = F_SANSB(10)
    d.text((W - MX - f.getlength(right), 6), right, font=f,
           fill=(230, 225, 210))

    # title
    title = "Friday 27 November 2026"
    fs = 54
    while fs > 30 and F_TITLE(fs).getlength(title) > CW:
        fs -= 1
    f = F_TITLE(fs)
    d.text(((W - f.getlength(title)) / 2, 28), title, font=f, fill=INK)

    # red subhead: the 3 biggest stories
    sub = ("BLACK FRIDAY SHOPPERS BRACE FOR $1TN SEASON · NEW ZEALAND HUNG "
           "AT 65–65 · EU SUMMIT ENDS WITH NO DEAL")
    fs = 16
    while fs > 10 and F_SERIFB(fs).getlength(sub) > CW:
        fs -= 1
    f = F_SERIFB(fs)
    d.text(((W - f.getlength(sub)) / 2, 90), sub, font=f, fill=RED)

    # region chips (counts sum to 45)
    y = 114
    chips = []
    for name, count in REGIONS:
        chips.append((name, F_SANSB(10).getlength(f"{name} {count}") + 16))
    total = sum(w for _, w in chips) + 8 * (len(chips) - 1)
    x = (W - total) / 2
    for (name, count), (_, cw) in zip(REGIONS, chips):
        d.rounded_rectangle([x, y, x + cw, y + 21], radius=4,
                            fill=REGION_COLORS[name])
        d.text((x + 8, y + 5), f"{name} {count}",
               font=F_SANSB(10), fill=(255, 255, 255))
        x += cw + 8

    # day in numbers
    y = 140
    bw = CW / 6
    d.line([MX, y, W - MX, y], fill=LINE, width=1)
    d.line([MX, y + 42, W - MX, y + 42], fill=LINE, width=1)
    for i, (val, lab) in enumerate(NUMBERS):
        cx = MX + bw * i
        d.text((cx + 8, y + 4), val, font=F_SERIFB(19), fill=NAVY)
        d.text((cx + 8, y + 26), lab, font=F_SANS(9), fill=GREY)
        if i:
            d.line([cx, y + 4, cx, y + 38], fill=LINE, width=1)

    # UTC timeline
    y = 188
    d.text((MX, y), "THE DAY IN UTC", font=F_SANSB(10), fill=RED)
    segs = "   ·   ".join(f"{t}  {e}" for t, e in TIMELINE)
    f = F_SANS(10)
    lab_w = F_SANSB(10).getlength("THE DAY IN UTC") + 14
    sx = MX + lab_w + (CW - lab_w - f.getlength(segs)) / 2
    d.text((sx, y), segs, font=f, fill=INK)

    # hero row: cards 1-3
    y = 214
    hero_h = 154
    gw = 9
    cw3 = (CW - 2 * gw) // 3
    for i, card in enumerate(CARDS[:3]):
        draw_hero(d, MX + i * (cw3 + gw), y, cw3, hero_h, card)

    # grid: cards 4-15, 3 cols x 4 rows
    y = y + hero_h + 6
    grid_h = 78
    for r in range(4):
        for c in range(3):
            draw_grid(d, MX + c * (cw3 + gw), y + r * (grid_h + 6),
                      cw3, grid_h, CARDS[3 + r * 3 + c])
    y = y + 4 * grid_h + 3 * 6

    # lower band header
    y = y + 6
    d.text((MX, y), "WHERE IT HAPPENED", font=F_SANSB(11), fill=INK)
    right = "ALSO ON FRIDAY 27 NOVEMBER — 30 MORE STORIES"
    f = F_SANSB(11)
    d.text((W - MX - f.getlength(right), y), right, font=f, fill=INK)

    # map (left) + ALSO ON (right)
    y = y + 18
    map_w, map_h = 350, 141
    draw_map(d, MX, y, map_w, map_h)
    ly = y + map_h + 6
    d.text((MX, ly), "Numbers match the pictures.", font=F_SANS(8.5),
           fill=GREY)
    d.text((MX, ly + 12), "Pins are coloured by region.",
           font=F_SANS(8.5), fill=GREY)
    ax0 = MX + map_w + 8
    acol_w = (W - MX - ax0 - 8) // 2
    warnings = draw_also(d, ax0, y, acol_w, 210)

    # DATE CHECK (red box)
    y = y + 216
    d.rounded_rectangle([MX, y, W - MX, y + 44], radius=4,
                        outline=RED, width=2)
    d.text((MX + 8, y + 5), "DATE CHECK", font=F_SANSB(10), fill=RED)
    f = F_SANS(9.5)
    lines = fit_lines(f, DATE_CHECK, CW - 110, 2)
    yy = y + 5
    for ln in lines:
        d.text((MX + 100, yy), ln, font=f, fill=(60, 40, 35))
        yy += 13
    if len(lines) > 2:
        warnings.append(f"DATE CHECK needs {len(lines)} lines, box holds 2")
    for text, needed, allowed in TRUNCATED:
        warnings.append(f"TRUNCATED ({needed}>{allowed} lines): '{text}…'")

    # footer: HOW SURE legend + sources
    y = y + 50
    f = F_SANS(8.5)
    leg = ("HOW SURE:  OFFICIAL — an authority's own figure or act   ·   "
           "REPORTED — press report   ·   ONGOING — still developing")
    d.text((MX, y), leg, font=f, fill=(70, 66, 58))
    lines = fit_lines(f, FOOTER_SOURCES, CW, 2)
    yy = y + 13
    for ln in lines:
        d.text((MX, yy), ln, font=f, fill=(70, 66, 58))
        yy += 11
    y = yy
    assert y <= 1022, f"page overflow: final y={y}"
    return img, warnings

def main():
    img, warnings = build()
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    data = open(out, "rb").read()
    print(f"entry.png: {len(data)} bytes, "
          f"{img.width}x{img.height}, sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"stories: {len(CARDS) + len(ALSO)}, "
          f"regions: {len(REGIONS)} (sum {sum(c for _, c in REGIONS)}), "
          f"cards: {len(CARDS)}, also-on: {len(ALSO)}")
    for w in warnings:
        print("WARNING:", w)
    print("OK" if not warnings else "OK with warnings")

if __name__ == "__main__":
    main()
