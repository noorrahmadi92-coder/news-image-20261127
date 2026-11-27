#!/usr/bin/env python3
"""Render 'The World in One Day - Friday, 27 November 2026' (1024x1024).

Deterministic news image for the make.fun competition news-image-20261127.
45 stories across 9 regions. Every story happened or was first reported on
Friday 27 November 2026 (UTC); the big stories from earlier days are named
in the red DATE CHECK box instead of being shown as today's news.

Pillow + DejaVu only, no network, no timestamps: two runs produce a
byte-identical PNG. Run: python3 draw.py  (writes entry.png next to it,
or to $MAKEFUN_OUTPUT_DIR/entry.png when that variable is set).
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

NAVY = (11, 32, 64)
RED = (178, 30, 30)
PAPER = (252, 250, 244)
INK = (22, 22, 22)
MUTED = (96, 94, 88)
LINE = (208, 203, 192)
CARD = (255, 255, 255)
BAND = (238, 235, 226)
DATE_BG = (253, 238, 236)

REGION_COLORS = {
    "NORTH AMERICA": (31, 119, 180),
    "EUROPE": (44, 160, 44),
    "EAST ASIA": (214, 39, 40),
    "OCEANIA": (148, 103, 189),
    "WORLD": (110, 110, 110),
    "SOUTH ASIA": (255, 127, 14),
    "AFRICA": (140, 86, 75),
    "SOUTHEAST ASIA": (23, 160, 175),
    "MIDDLE EAST": (170, 170, 30),
}

TAG_COLORS = {
    "REPORTED": (31, 119, 180),
    "OFFICIAL": (34, 139, 34),
    "CLAIM": (230, 120, 0),
    "ONGOING": (214, 39, 40),
    "CONFIRMED": (0, 128, 128),
}

GLYPHS = {
    "RETAIL": "\u25c6",
    "POLITICS": "\u2691",
    "ECONOMY": "\u25b2",
    "MARKETS": "\u25cf",
    "SPORT": "\u2605",
    "CONFLICT": "\u2716",
    "DISASTER": "\u25bc",
    "TRANSPORT": "\u2630",
    "ACCIDENT": "\u271a",
    "DIPLOMACY": "\u25c7",
}

REGIONS = [
    ("NORTH AMERICA", 7),
    ("EUROPE", 14),
    ("EAST ASIA", 8),
    ("OCEANIA", 6),
    ("WORLD", 4),
    ("SOUTH ASIA", 2),
    ("AFRICA", 2),
    ("SOUTHEAST ASIA", 1),
    ("MIDDLE EAST", 1),
]

NUMBERS = [
    ("65\u201365", "NZ hung parliament"),
    ("+16%", "China factory profits"),
    ("$1tn", "NRF holiday sales"),
    ("$61,315", "Bitcoin Fri morning"),
    ("\u20ac45bn", "EU Ukraine loan backed"),
    ("1\u00bd\u20131\u00bd", "chess at rest day"),
]

TIMELINE = [
    ("00:30", "EU summit ends"),
    ("01:00", "NZ results"),
    ("01:30", "China +16%"),
    ("02:10", "Bitcoin $61,315"),
    ("08:00", "Joburg vote"),
    ("18:00", "US close early"),
    ("19:00", "Macy's balloons"),
]

# Cards 1-15. Hero cards 1-3 carry a "why it matters" line.
CARDS = [
    dict(n=1, region="NORTH AMERICA", field="RETAIL", place="NEW YORK",
         tag="REPORTED", headline="Black Friday: cautious shoppers, $1tn season",
         body="NRF sees Nov\u2013Dec holiday sales +4.2% YoY to just above $1tn; "
              "Target, Dollar Tree, Kohl's flag belt-tightening.",
         source="Reuters", why="The season's first big test of US shoppers."),
    dict(n=2, region="OCEANIA", field="POLITICS", place="WELLINGTON",
         tag="OFFICIAL", headline="New Zealand hung: Luxon loses majority",
         body="Final count: right bloc 65 of 130, one short of 66. Labour 36, "
              "Greens 17, Opportunity 7, Te P\u0101ti M\u0101ori 5; turnout 77.2%.",
         source="Reuters / Electoral Commission",
         why="A kingmaker decides who governs."),
    dict(n=3, region="EUROPE", field="POLITICS", place="BRUSSELS",
         tag="OFFICIAL", headline="EU summit ends with no deal; de Cos to lead ECB",
         body="12 hours, no deal on the \u20ac1.58tn budget or \u20ac45bn Ukraine loan; "
              "second day cancelled; de Cos named next ECB chief.",
         source="Consilium / Reuters",
         why="Europe's money fight rolls to December."),
    dict(n=4, region="EAST ASIA", field="ECONOMY", place="BEIJING",
         tag="OFFICIAL", headline="China factory profits jump 16%",
         body="Industrial profits +16% Jan\u2013Oct; data out Fri.",
         source="Reuters"),
    dict(n=5, region="EAST ASIA", field="MARKETS", place="TOKYO/SEOUL",
         tag="REPORTED", headline="Asia shares extend rebound",
         body="MSCI Asia +0.6%; Nikkei +0.7%, Kospi +1.5%.",
         source="MarketIndex"),
    dict(n=6, region="EUROPE", field="SPORT", place="GENEVA",
         tag="REPORTED", headline="Chess title rests at 1\u00bd\u20131\u00bd",
         body="Rest day; Game 3 a 60-move draw; Game 4 Sat.",
         source="Guardian / FIDE"),
    dict(n=7, region="MIDDLE EAST", field="CONFLICT", place="GAZA",
         tag="REPORTED", headline="Gaza toll updated: 19 killed in 48 hours",
         body="1,705 dead since 10 Oct ceasefire; total 74,772.",
         source="Al Jazeera"),
    dict(n=8, region="SOUTHEAST ASIA", field="DISASTER", place="BOGOR",
         tag="REPORTED", headline="Bogor mine: all 13 dead identified",
         body="Bodies handed over; search on for 13 missing.",
         source="detikJabar"),
    dict(n=9, region="NORTH AMERICA", field="MARKETS", place="NEW YORK",
         tag="REPORTED", headline="Wall Street reopens for a half day",
         body="Shut Thu; closes 13:00 ET; futures +~1%.",
         source="Pipback"),
    dict(n=10, region="EUROPE", field="POLITICS", place="MADRID",
         tag="REPORTED", headline="Spain's campaign closes; PP leads",
         body="Vote Sun 29 Nov; PP ~31%, PSOE ~29%, Vox ~18%.",
         source="Reuters"),
    dict(n=11, region="EUROPE", field="TRANSPORT", place="LONDON",
         tag="REPORTED", headline="Tube strike hits Friday commute",
         body="First of 8 RMT strikes; normal by ~18:00.",
         source="Reuters / TfL"),
    dict(n=12, region="EUROPE", field="ACCIDENT", place="IBIZA",
         tag="REPORTED", headline="Ibiza tanker: Friday checks begin",
         body="Salvage inspects Med Emre; 7,000 t diesel aboard.",
         source="BBC / Reuters"),
    dict(n=13, region="AFRICA", field="POLITICS", place="JOHANNESBURG",
         tag="REPORTED", headline="Joburg picks a mayor today",
         body="Votes 10:00 SAST; DA 91, ANC 63, ActionSA 43.",
         source="IOL"),
    dict(n=14, region="SOUTH ASIA", field="SPORT", place="INDIA",
         tag="REPORTED", headline="India v NZ: 2nd Test starts today",
         body="India eye historic series win; 2nd Test Fri.",
         source="EIN"),
    dict(n=15, region="WORLD", field="DIPLOMACY", place="GENEVA",
         tag="REPORTED", headline="UN backs Palestinian recovery aid",
         body="UNCTAD passes measure to boost Palestinian aid.",
         source="UNCTAD"),
]

# ALSO ON rows 16-45: (number, place, one-liner, source). All REPORTED.
ALSO_ON = [
    (16, "GLOBAL", "Bitcoin $61,315, +0.7% Fri", "Finnhub"),
    (17, "NEW YORK", "US close early, 13:00 ET", "Pipback"),
    (18, "NEW YORK", "Macy's balloons re-inflated", "CNN"),
    (19, "NEW YORK", "No Wall St close Thu", "Pipback"),
    (20, "NEW YORK", "S&P, Nasdaq futures +1%", "MarketIndex"),
    (21, "NEW YORK", "NYC winds ease; warning ends", "NWS"),
    (22, "PARIS", "France faces S&P review Fri", "Reuters"),
    (23, "MADRID", "Spain pre-vote silence Fri", "PolitPro"),
    (24, "LONDON", "Tube: 7 more strike days", "TfL"),
    (25, "IBIZA", "Ibiza spill ship on station", "BBC"),
    (26, "BRUSSELS", "Allies may add \u20ac25bn to loan", "EU Council"),
    (27, "BUDAPEST", "Hungary, Slovakia refuse", "europesays"),
    (28, "BERLIN", "Merz: Friday talks off", "europesays"),
    (29, "MADRID", "Right 51.2%, left 38.7%", "Portside"),
    (30, "LONDON", "ASLEF takes 4-day week", "TfL"),
    (31, "SEOUL", "Samsung pays ~\u20a93tn dividend", "kimkj"),
    (32, "TAIPEI", "TAIEX slips 0.15% at open", "TopologyPro"),
    (33, "HONG KONG", "Hang Seng opens +36", "Longbridge"),
    (34, "HONG KONG", "Lenovo +2.9%, CATL +2.4%", "Longbridge"),
    (35, "TOKYO", "Tokyo: Kioxia +3.3%", "TradingKey"),
    (36, "SEOUL", "Seoul: Samsung +0.9%", "TradingKey"),
    (37, "MUMBAI", "GIFT Nifty points lower", "7Globe"),
    (38, "WELLINGTON", "NZ special votes skew left", "Reuters"),
    (39, "WELLINGTON", "Recounts due 2 Dec", "Electoral Comm."),
    (40, "SYDNEY", "ASX +0.32% at 8,791.9", "MarketIndex"),
    (41, "WELLINGTON", "Wong, 38, kingmaker", "AP/Reuters"),
    (42, "WELLINGTON", "Parliament to 130", "Electoral Comm."),
    (43, "JOHANNESBURG", "Ekurhuleni vote due Fri", "GSW"),
    (44, "VIENNA", "OPEC+ meets Sun 29 Nov", "Pipback"),
    (45, "DOHA", "Verstappen chases 4th Qatar win", "Bulletin"),
]

DATE_CHECK = (
    "US tariffs on 14 partners (25 Nov) \u00b7 India capped 17% (25 Nov) \u00b7 "
    "F-16 sale to Ukraine, $622m (25 Nov) \u00b7 Cairo tanker fire, 31 dead "
    "(25 Nov) \u00b7 Gaza deputy minister killed (26 Nov) \u00b7 Houthi refinery "
    "strikes (25\u201326 Nov) \u00b7 Kuwait drone strike, 2 Italians killed "
    "(26 Nov) \u00b7 Bangkok refinery blast, 7 hurt (26 Nov) \u00b7 Ibiza tanker "
    "capsizes (26 Nov) \u00b7 Trabuco takes Brazil finance post (26 Nov) \u00b7 "
    "ICJ Myanmar genocide ruling (19 Nov)"
)

# Dotted world map: row -> list of (first_col, last_col), 100 cols x 34 rows.
# Columns map lon -180..180, rows map lat 90..-60. Rough but recognisable.
LAND = {
    0: [(33, 38)],
    1: [(24, 28), (33, 43)],
    2: [(20, 29), (34, 42)],
    3: [(2, 8), (18, 31), (35, 41), (62, 95)],
    4: [(1, 9), (15, 33), (37, 41), (58, 97)],
    5: [(2, 9), (12, 34), (44, 46), (50, 55), (56, 98)],
    6: [(4, 8), (12, 35), (44, 46), (51, 57), (58, 99)],
    7: [(13, 36), (49, 99)],
    8: [(14, 37), (48, 95)],
    9: [(15, 38), (46, 57), (60, 97)],
    10: [(16, 39), (47, 56), (60, 95)],
    11: [(17, 39), (47, 55), (57, 89)],
    12: [(18, 39), (46, 55), (56, 62), (66, 87), (88, 89)],
    13: [(19, 38), (45, 56), (57, 62), (66, 72), (74, 86)],
    14: [(20, 27), (38, 38), (45, 56), (58, 62), (67, 72), (76, 83)],
    15: [(21, 29), (45, 52), (58, 61), (68, 70), (77, 83)],
    16: [(24, 27), (45, 52), (70, 72), (77, 84), (84, 90)],
    17: [(23, 26), (30, 36), (46, 54), (79, 84), (86, 89)],
    18: [(29, 37), (46, 55), (82, 84), (86, 92)],
    19: [(29, 38), (47, 56), (87, 92)],
    20: [(30, 38), (47, 56), (88, 91)],
    21: [(30, 38), (48, 55), (88, 90)],
    22: [(31, 37), (48, 54), (62, 64), (86, 89)],
    23: [(31, 37), (48, 53), (62, 64), (84, 91)],
    24: [(32, 37), (48, 53), (62, 63), (81, 92)],
    25: [(32, 36), (48, 52), (62, 63), (81, 92)],
    26: [(32, 36), (48, 51), (81, 91)],
    27: [(31, 37), (48, 51), (81, 90), (98, 99)],
    28: [(30, 34), (49, 50), (82, 92), (97, 99)],
    29: [(30, 33), (89, 92), (96, 98)],
    30: [(30, 32), (90, 91)],
    31: [(30, 32)],
    32: [(30, 31)],
    33: [],
}

# Map pins: (card number, longitude, latitude, nudge dx, nudge dy).
# Cards 9 and 15 share pins with cards 1 and 6, so they are nudged apart.
PINS = [
    (1, -74.0, 40.7, 0, 0),
    (2, 174.8, -41.3, 0, 0),
    (3, 4.35, 50.85, 10, -6),
    (4, 116.4, 39.9, 0, 0),
    (5, 139.7, 35.7, 0, 0),
    (6, 6.14, 46.2, -6, 10),
    (7, 34.5, 31.5, 0, 0),
    (8, 106.8, -6.6, 0, 0),
    (9, -74.0, 40.7, 12, 12),
    (10, -3.7, 40.4, -10, 8),
    (11, -0.1, 51.5, -12, -10),
    (12, 1.4, 38.98, 10, 10),
    (13, 28.0, -26.2, 0, 0),
    (14, 77.2, 28.6, 0, 0),
    (15, 6.14, 46.2, 12, 12),
]


def load_font(size, bold=False, serif=False):
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    step = int(fnt.size * 1.28)
    for i, line in enumerate(lines):
        draw.text((x, y + i * step), line, font=fnt, fill=fill)
    return y + len(lines) * step


def truncate_to(draw, text, fnt, max_w):
    """Shorten text with an ellipsis until it fits max_w."""
    while text and draw.textlength(text, font=fnt) > max_w:
        text = text[:-4].rstrip() + "\u2026"
    return text


def draw_top_bar(draw):
    draw.rectangle([0, 0, W, 30], fill=NAVY)
    draw.text((12, 8), "THE WORLD IN ONE DAY", font=load_font(14, bold=True),
              fill=(255, 255, 255))
    right = "make.fun  \u00b7  $100  \u00b7  TOP 50"
    rw = draw.textlength(right, font=load_font(11, bold=True))
    draw.text((W - 12 - rw, 9), right, font=load_font(11, bold=True),
              fill=(200, 210, 225))


def draw_title(draw):
    draw.text((12, 38), "Friday, 27 November 2026",
              font=load_font(34, bold=True, serif=True), fill=NAVY)
    right = "45 STORIES \u00b7 9 REGIONS"
    fnt = load_font(15, bold=True)
    rw = draw.textlength(right, font=fnt)
    draw.text((W - 12 - rw, 50), right, font=fnt, fill=RED)


def draw_subhead(draw):
    text = ("BLACK FRIDAY SHOPPERS BRACE FOR $1TN SEASON \u00b7 NEW ZEALAND "
            "HUNG AT 65\u201365 \u00b7 EU SUMMIT ENDS WITH NO DEAL")
    fnt = load_font(13, bold=True)
    tw = draw.textlength(text, font=fnt)
    draw.text(((W - tw) / 2, 84), text, font=fnt, fill=RED)


def draw_chips(draw):
    fnt = load_font(10, bold=True)
    chips = []
    for name, count in REGIONS:
        label = "%s %d" % (name, count)
        chips.append((label, draw.textlength(label, font=fnt) + 18))
    gap = 8
    total = sum(w for _, w in chips) + gap * (len(chips) - 1)
    x = (W - total) / 2
    y = 106
    for label, w in chips:
        draw.rounded_rectangle([x, y, x + w, y + 20], radius=10,
                               fill=(255, 255, 255), outline=LINE, width=1)
        tw = draw.textlength(label, font=fnt)
        draw.text((x + (w - tw) / 2, y + 5), label, font=fnt, fill=NAVY)
        x += w + gap


def draw_numbers(draw):
    col_w = (W - 24) / 6
    big = load_font(15, bold=True)
    small = load_font(9)
    for i, (value, label) in enumerate(NUMBERS):
        cx = 12 + i * col_w + col_w / 2
        vw = draw.textlength(value, font=big)
        draw.text((cx - vw / 2, 132), value, font=big, fill=NAVY)
        lw = draw.textlength(label, font=small)
        draw.text((cx - lw / 2, 150), label, font=small, fill=MUTED)
        if i:
            draw.line([12 + i * col_w, 134, 12 + i * col_w, 160], fill=LINE)


def draw_timeline(draw):
    draw.rectangle([0, 160, W, 180], fill=BAND)
    parts = []
    for i, (time, event) in enumerate(TIMELINE):
        if i:
            parts.append((" \u00b7 ", False))
        parts.append((time, True))
        parts.append((" " + event, False))
    fnt_b = load_font(10, bold=True)
    fnt_r = load_font(10)
    total = 0
    for text, is_bold in parts:
        total += draw.textlength(text, font=fnt_b if is_bold else fnt_r)
    x = (W - total) / 2
    for text, is_bold in parts:
        fnt = fnt_b if is_bold else fnt_r
        draw.text((x, 167), text, font=fnt, fill=NAVY if is_bold else INK)
        x += draw.textlength(text, font=fnt)


def draw_hero_card(draw, card, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    draw.rectangle([x, y, x + w, y + 3],
                   fill=REGION_COLORS[card["region"]])
    # Number badge, kicker, status tag.
    draw.ellipse([x + 10, y + 12, x + 28, y + 30], fill=RED)
    num = str(card["n"])
    nf = load_font(10, bold=True)
    nw = draw.textlength(num, font=nf)
    draw.text((x + 19 - nw / 2, y + 16), num, font=nf, fill=(255, 255, 255))
    kicker = "%s \u00b7 %s \u00b7 %s" % (card["region"], card["field"],
                                       card["place"])
    draw.text((x + 34, y + 16), kicker, font=load_font(9, bold=True),
              fill=MUTED)
    tag = card["tag"]
    tf = load_font(9, bold=True)
    tw = draw.textlength(tag, font=tf)
    draw.text((x + w - 10 - tw, y + 16), tag, font=tf,
              fill=TAG_COLORS[tag])
    # Headline, body, why-it-matters, source.
    draw_wrapped(draw, x + 10, y + 36, card["headline"],
                 load_font(14, bold=True), w - 20, fill=NAVY, max_lines=2)
    draw_wrapped(draw, x + 10, y + 66, card["body"],
                 load_font(10), w - 20, fill=INK, max_lines=3)
    why = "Why it matters: " + card["why"]
    draw_wrapped(draw, x + 10, y + 100, why, load_font(10), w - 20,
                 fill=INK, max_lines=2)
    draw.text((x + 10, y + h - 16), card["source"],
              font=load_font(9), fill=MUTED)


def draw_grid_card(draw, card, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    color = REGION_COLORS[card["region"]]
    # Small icon tile on the left.
    draw.rectangle([x + 8, y + 8, x + 38, y + 38], fill=color)
    glyph = GLYPHS[card["field"]]
    gf = load_font(16, bold=True)
    gw = draw.textlength(glyph, font=gf)
    draw.text((x + 23 - gw / 2, y + 14), glyph, font=gf,
              fill=(255, 255, 255))
    tx = x + 46
    tw = w - 56
    # Number, kicker, status tag on one line.
    draw.ellipse([tx, y + 8, tx + 14, y + 22], fill=RED)
    num = str(card["n"])
    nf = load_font(8, bold=True)
    nw = draw.textlength(num, font=nf)
    draw.text((tx + 7 - nw / 2, y + 10), num, font=nf,
              fill=(255, 255, 255))
    kicker = "%s \u00b7 %s" % (card["field"], card["place"])
    draw.text((tx + 19, y + 9), kicker, font=load_font(8, bold=True),
              fill=MUTED)
    tag = card["tag"]
    tf = load_font(8, bold=True)
    twd = draw.textlength(tag, font=tf)
    draw.text((x + w - 8 - twd, y + 9), tag, font=tf,
              fill=TAG_COLORS[tag])
    # Headline (up to 2 lines), body (1 line), source.
    draw_wrapped(draw, tx, y + 24, card["headline"],
                 load_font(11, bold=True), tw, fill=NAVY, max_lines=2)
    body = truncate_to(draw, card["body"], load_font(9), tw)
    draw.text((tx, y + 50), body, font=load_font(9), fill=INK)
    draw.text((tx, y + 63), card["source"], font=load_font(8), fill=MUTED)


def draw_map(draw, x0, y0, w, h):
    draw.text((x0, y0), "WHERE IT HAPPENED", font=load_font(11, bold=True),
              fill=NAVY)
    mx, my, mw, mh = x0 + 4, y0 + 22, w - 8, h - 24
    for row, spans in LAND.items():
        cy = my + (row + 0.5) / 34.0 * mh
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = mx + (c + 0.5) / 100.0 * mw
                draw.ellipse([cx - 1.6, cy - 2.2, cx + 1.6, cy + 2.2],
                             fill=(130, 128, 122))
    pin_font = load_font(8, bold=True)
    for n, lon, lat, dx, dy in PINS:
        px = mx + (lon + 180.0) / 360.0 * mw
        py = my + (90.0 - lat) / 150.0 * mh
        qx, qy = px + dx, py + dy
        if dx or dy:
            draw.line([px, py, qx, qy], fill=(150, 150, 150), width=1)
        draw.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=(255, 255, 255),
                     outline=NAVY, width=1)
        label = str(n)
        lw = draw.textlength(label, font=pin_font)
        draw.text((qx - lw / 2, qy - 5), label, font=pin_font, fill=NAVY)


def draw_also_on(draw, x0, y0, w, h):
    draw.text((x0, y0), "ALSO ON \u2014 30 MORE STORIES",
              font=load_font(11, bold=True), fill=NAVY)
    col_w = 320
    col_gap = 20
    row_h = 16
    f_num = load_font(9, bold=True)
    f_place = load_font(9, bold=True)
    f_text = load_font(9)
    f_tag = load_font(9, bold=True)
    f_src = load_font(9)
    for i, (n, place, text, src) in enumerate(ALSO_ON):
        col = i // 15
        row = i % 15
        x = x0 + col * (col_w + col_gap)
        y = y0 + 22 + row * row_h
        tag = "REPORTED"
        # Trim the one-liner until the whole row fits the column.
        while True:
            parts = [(str(n) + " ", f_num, RED),
                     (place + " ", f_place, INK),
                     (text, f_text, INK),
                     (" [" + tag + "]", f_tag, TAG_COLORS[tag]),
                     (" " + src, f_src, MUTED)]
            total = sum(draw.textlength(t, font=f) for t, f, _ in parts)
            if total <= col_w or len(text) <= 8:
                break
            text = text[:-4].rstrip() + "\u2026"
        cx = x
        for t, f, fill in parts:
            draw.text((cx, y), t, font=f, fill=fill)
            cx += draw.textlength(t, font=f)


def draw_date_check(draw):
    y0, y1 = 896, 960
    draw.rectangle([0, y0, W, y1], fill=DATE_BG)
    draw.rectangle([0, y0, W, y0 + 2], fill=RED)
    draw.text((12, y0 + 6), "DATE CHECK \u2014 DELIBERATELY LEFT OUT",
              font=load_font(11, bold=True), fill=RED)
    draw_wrapped(draw, 12, y0 + 22, DATE_CHECK, load_font(10), W - 24,
                 fill=INK, max_lines=3)


def draw_footer(draw):
    y = 964
    legend = ("HOW SURE:  REPORTED = reported by a wire  \u00b7  CLAIM = an "
              "attributed claim  \u00b7  ONGOING = still developing  \u00b7  "
              "CONFIRMED = officially confirmed  \u00b7  OFFICIAL = official "
              "data or results")
    draw.text((12, y), legend, font=load_font(9, bold=True), fill=NAVY)
    sources = ("Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 Consilium \u00b7 "
               "Electoral Commission NZ \u00b7 Al Jazeera \u00b7 detikJabar "
               "\u00b7 FIDE \u00b7 TfL \u00b7 IOL \u00b7 NWS \u00b7 UNCTAD "
               "\u00b7 MarketIndex \u00b7 Pipback \u00b7 Finnhub")
    draw.text((12, y + 13), sources, font=load_font(9), fill=MUTED)
    note = ("Every story happened or was first reported on Friday 27 November "
            "2026 (UTC). No Latin America story verified for 27 Nov. "
            "\u00b7 The World in One Day \u00b7 make.fun")
    draw.text((12, y + 26), note, font=load_font(9), fill=MUTED)
    draw.line([12, y + 42, W - 12, y + 42], fill=LINE)
    draw.text((12, y + 46), "45 stories \u00b7 9 regions \u00b7 Friday, 27 "
              "November 2026", font=load_font(9, bold=True), fill=MUTED)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_top_bar(draw)
    draw_title(draw)
    draw_subhead(draw)
    draw_chips(draw)
    draw_numbers(draw)
    draw_timeline(draw)
    # Hero cards 1-3.
    hero_x = [12, 349, 686]
    for i, card in enumerate(CARDS[:3]):
        draw_hero_card(draw, card, hero_x[i], 178, 324, 136)
    # Grid cards 4-15: 3 columns x 4 rows.
    grid_x = [12, 349, 686]
    grid_y = [318, 398, 478, 558]
    for i, card in enumerate(CARDS[3:]):
        draw_grid_card(draw, card, grid_x[i % 3], grid_y[i // 3], 324, 76)
    # Lower band: map left, ALSO ON right.
    draw_map(draw, 12, 640, 328, 256)
    draw_also_on(draw, 352, 640, 660, 256)
    draw_date_check(draw)
    draw_footer(draw)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(
        os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "entry.png")
    img = build()
    img.save(out_path, format="PNG")
    print("wrote %s (%dx%d)" % (out_path, img.width, img.height))


if __name__ == "__main__":
    main()
