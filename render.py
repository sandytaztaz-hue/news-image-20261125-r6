#!/usr/bin/env python3
"""Sum 25 round 6 — Wednesday 25 November 2026 in one image.

Renders the 1024x1024 broadsheet described in BRIEF-R6.md (Revisions A+B):
3 heroes + 8 medium cards + 39 briefs = 50 stories, all first reported on
Wednesday 25 November 2026. Revision B: the hot topic (US tariffs) leads
as one LARGE card on the left, with Kospi and Tiangong stacked on the
right. Deterministic: no randomness, no timestamps, no network.
Writes entry.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _load(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def serif_b(size):
    return _load("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return _load("DejaVuSerif.ttf", size)


def sans_b(size):
    return _load("DejaVuSans-Bold.ttf", size)


def sans(size):
    return _load("DejaVuSans.ttf", size)


def sans_i(size):
    return _load("DejaVuSans-Oblique.ttf", size)


NAVY = (16, 28, 52)
INK = (24, 28, 36)
GREY = (100, 108, 120)
LIGHT_GREY = (148, 156, 168)
RED = (178, 34, 34)
GREEN = (26, 122, 58)
DARK_GREEN = (16, 96, 44)
AMBER = (176, 116, 10)
ORANGE = (200, 96, 10)
PAPER = (255, 255, 255)
HAIR = (214, 220, 226)
PALE = (244, 246, 248)
SKY = (214, 232, 244)
SEA = (46, 111, 168)


def tw(draw, text, font):
    return draw.textlength(text, font=font)


def fit_font(draw, text, max_w, start, minimum, bold=False, serif_f=False):
    """Largest font size <= start that fits text in max_w (never below minimum)."""
    size = start
    while size > minimum:
        f = (serif_b(size) if serif_f and bold else
             serif(size) if serif_f else
             sans_b(size) if bold else sans(size))
        if tw(draw, text, f) <= max_w:
            return f, size
        size -= 1
    f = (serif_b(minimum) if serif_f and bold else
         serif(minimum) if serif_f else
         sans_b(minimum) if bold else sans(minimum))
    return f, minimum


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines (never splits a word)."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, max_w, text, start, minimum, fill, lh_factor=1.25,
         max_lines=2, bold=False, serif_f=False, italic=False):
    """Draw text wrapped to at most max_lines lines, shrinking the font first.
    Returns the y just below the last line drawn."""
    size = start
    while size > minimum:
        f = (serif_b(size) if serif_f and bold else
             serif(size) if serif_f else
             sans_b(size) if bold else
             sans_i(size) if italic else sans(size))
        if len(wrap(draw, text, f, max_w)) <= max_lines:
            break
        size -= 1
    f = (serif_b(size) if serif_f and bold else
         serif(size) if serif_f else
         sans_b(size) if bold else
         sans_i(size) if italic else sans(size))
    lines = wrap(draw, text, f, max_w)[:max_lines]
    lh = int(size * lh_factor)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def chip(draw, x, y, text, bg, fg=(255, 255, 255), size=9, pad_x=5, pad_y=2):
    """Small rounded status chip; returns (width, height)."""
    f = sans_b(size)
    w = int(tw(draw, text, f)) + pad_x * 2
    h = size + pad_y * 2 + 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    draw.text((x + pad_x, y + pad_y), text, font=f, fill=fg)
    return w, h


def badge(draw, cx, cy, number, r=13):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                 outline=(255, 255, 255), width=2)
    f = sans_b(13 if r >= 13 else 10)
    t = str(number)
    draw.text((cx - tw(draw, t, f) / 2, cy - (13 if r >= 13 else 10) / 2 - 1),
              t, font=f, fill=(255, 255, 255))


def centered(draw, y, text, font, fill, cx=W // 2):
    draw.text((cx - tw(draw, text, font) / 2, y), text, font=font, fill=fill)


def chip_w(draw, text, size=9, pad_x=5, pad_y=2):
    """Width/height of a chip without drawing it (never draw to measure)."""
    return (int(tw(draw, text, sans_b(size))) + pad_x * 2,
            size + pad_y * 2 + 2)


def draw_scene(img, name, x, y, w, h):
    """Draw a scene onto its own layer and paste it, so nothing in a
    scene can paint outside its own rectangle."""
    layer = Image.new("RGB", (w, h), PAPER)
    ld = ImageDraw.Draw(layer)
    SCENES[name](ld, 0, 0, w, h)
    img.paste(layer, (x, y))


# ---------------------------------------------------------------- inventory
# Field / region per story, recomputed from the 50-story inventory.
# Fields: War 11, Disaster 5, Diplomacy 5, Economy 3, Tech 3, Rights 3,
# Sport 3, Security 2, Labour 2, Markets 2, Business 3, Politics 2,
# Justice 1, Crime 1, Trade 1, Climate 1, Energy 1, Space 1 = 50.
# (Business is 3, not 2 as printed in the brief: stories 18 Lukoil buy,
# 45 Poundland collapse, 50 Pete Edochie dies. Item 20, the Macy's parade
# postponement, is filed under Climate as a weather postponement.)
# Regions: N. America 9, Latin America 2, Europe 15, Middle East 5,
# N. Africa 2, Sub-Saharan Africa 3, South Asia 3, East & SE Asia 7,
# Oceania 2, Global 2 = 50. (Story 27, NATO space defence, is Global;
# story 19, the UN women-killed figure, is Global.)

REGION_STRIP = [
    ("N. AMERICA", 9, (37, 99, 235)),
    ("LATIN AMERICA", 2, (13, 148, 136)),
    ("EUROPE", 15, (124, 58, 237)),
    ("MIDDLE EAST", 5, (234, 88, 12)),
    ("N. AFRICA", 2, (146, 64, 14)),
    ("SUB-SAHARAN AFRICA", 3, (120, 53, 15)),
    ("SOUTH ASIA", 3, (219, 39, 119)),
    ("EAST & SE ASIA", 7, (22, 163, 74)),
    ("OCEANIA", 2, (101, 163, 13)),
    ("GLOBAL", 2, (107, 114, 128)),
]

FIELD_STRIP = [
    ("War", 11), ("Disaster", 5), ("Diplomacy", 5), ("Economy", 3),
    ("Tech", 3), ("Rights", 3), ("Sport", 3), ("Security", 2),
    ("Labour", 2), ("Markets", 2), ("Business", 3), ("Politics", 2),
    ("Justice", 1), ("Crime", 1), ("Trade", 1), ("Climate", 1),
    ("Energy", 1), ("Space", 1),
]

NUMBERS = [
    ("35%", "TOP PROPOSED US TARIFF (VIETNAM)"),
    ("-6.2%", "KOSPI CLOSE, WORST IN AI SELL-OFF"),
    ("+26%", "UK ENERGY PRICE CAP FROM 1 JANUARY"),
    ("30+", "KILLED IN CAIRO TANKER FIRE"),
    ("9", "DEAD, 17 TRAPPED IN JAVA GOLD PIT"),
    ("1st", "FOREIGNER ABOARD TIANGONG"),
]

MARKETS = [
    ("KOSPI -6.2%", RED),
    ("TAIEX -4.8%", RED),
    ("NIKKEI -2.8%", RED),
    ("NASDAQ -0.6%", RED),
    ("DOW +0.3%", GREEN),
]

UTC_TICKS = [
    ("00:18", "SHENZHOU-24 LIFTS OFF"),
    ("03:56", "TIANGONG DOCKS"),
    ("05:30", "TAIEX CLOSES -4.8%"),
    ("06:30", "KOSPI CLOSES -6.2%"),
    ("06:35", "CREW ENTERS TIANGONG"),
    ("07:00", "OFGEM CAP +26%"),
    ("13:00", "US TARIFFS PROPOSED"),
    ("21:00", "DOW ENDS ABOVE 50,000"),
]

# ------------------------------------------------------------------- stories
# Revision B heroes: HERO 1 is the large lead (tariffs, the hot topic);
# HEROES 2 and 3 stack in the right column.
HEROES = [
    {
        "num": 1,
        "kicker": "WASHINGTON \u00b7 TRADE",
        "headline": "US proposes tariffs of up to 35% on 14 economies",
        "deck": "Section 301 cites 'excess capacity': Vietnam faces the top "
                "35% rate, India 25%, China 20%, EU 15%; hearings open "
                "January 2027. The world's reply: the EU 'strongly rejects' "
                "the premise, Beijing calls overcapacity 'a false issue', "
                "and the other named partners weigh responses.",
        "why": "The widest tariff salvo in months \u2014 every top US trade "
               "partner faces duties.",
        "source": "USTR \u00b7 Reuters \u00b7 CNBC",
        "chip": ("REPORTED", AMBER),
        "scene": "ship",
    },
    {
        "num": 2,
        "kicker": "SEOUL \u00b7 TOKYO \u00b7 TAIPEI \u00b7 MARKETS",
        "headline": "AI doubts sink Asian chip stocks: Kospi closes -6.2%",
        "deck": "Kospi ends at 4,697.51, under 5,000; SK Hynix -11.1%, "
                "Samsung -9.9% as banks cut targets.",
        "why": "Markets ask whether the AI boom can ever pay for itself.",
        "source": "Yonhap \u00b7 Korea Times \u00b7 Al Jazeera",
        "chip": ("CONFIRMED", GREEN),
        "scene": "chart",
    },
    {
        "num": 3,
        "kicker": "JIUQUAN, CHINA \u00b7 SPACE",
        "headline": "Pakistan's first astronaut docks at China's space station",
        "deck": "Muhammad Zeeshan Ali, 40, first foreigner on Tiangong, flew "
                "on Shenzhou-24 with Tang Hongbo and Wu Li; docking 03:56, "
                "stays 5 to 10 days.",
        "why": "A first for Pakistan \u2014 and a first foreign crew member "
               "for Tiangong.",
        "source": "CMSA \u00b7 Xinhua",
        "chip": ("OFFICIAL", DARK_GREEN),
        "scene": "space",
    },
]

MEDIUMS = [
    {
        "num": 4, "kicker": "HODEIDAH, YEMEN \u00b7 MIDDLE EAST",
        "chip_label": "PORT",
        "headline": "Saudi-led strikes hit Hodeidah port",
        "deck": "Raids early Wednesday 25 November; Houthis also claim a hit "
                "on the Ras Tanura refinery.",
        "source": "Arab News \u00b7 Reuters",
        "chip": ("CONFIRMED", GREEN), "scene": "port",
    },
    {
        "num": 5, "kicker": "STRAIT OF HORMUZ \u00b7 MIDDLE EAST",
        "chip_label": "2 TANKERS",
        "headline": "Two tankers hit by mines in the Strait of Hormuz",
        "deck": "Iran's IRGC says two oil tankers struck naval mines and "
                "caught fire on an unauthorised route.",
        "source": "IRGC \u00b7 Reuters",
        "chip": ("CLAIM", ORANGE), "scene": "strait",
    },
    {
        "num": 6, "kicker": "LONDON \u00b7 ENERGY",
        "chip_label": "+26%",
        "headline": "UK energy price cap to jump 26% in January",
        "deck": "Ofgem lifts the typical dual-fuel bill from \u00a31,723 to "
                "\u00a32,166 a year from 1 Jan.",
        "source": "Ofgem \u00b7 BBC",
        "chip": ("OFFICIAL", DARK_GREEN), "scene": "energy",
    },
    {
        "num": 7, "kicker": "CANBERRA \u00b7 DIPLOMACY",
        "chip_label": "A$740m",
        "headline": "Solomon Islands signs A$740m security pact",
        "deck": "Ten-year treaty names Australia primary security partner, "
                "bars foreign bases.",
        "source": "DFAT \u00b7 ABC",
        "chip": ("CONFIRMED", GREEN), "scene": "treaty",
    },
    {
        "num": 8, "kicker": "GIZA, EGYPT \u00b7 DISASTER",
        "chip_label": "30+",
        "headline": "Fuel tanker fire kills at least 30 near Cairo",
        "deck": "Tanker overturned and exploded on the Al-Warraq ring road, "
                "engulfing nearby cars; at least 30 killed.",
        "source": "AP \u00b7 Reuters",
        "chip": ("REPORTED", AMBER), "scene": "tanker",
    },
    {
        "num": 9, "kicker": "BOGOR, INDONESIA \u00b7 DISASTER",
        "chip_label": "9 DEAD",
        "headline": "9 dead, 17 trapped in flooded gold mine",
        "deck": "Rescuers pull bodies from the 100-metre unlicensed pit in "
                "West Java; rain hampers pumps.",
        "source": "BNPB \u00b7 AP",
        "chip": ("REPORTED", AMBER), "scene": "mine",
    },
    {
        "num": 10, "kicker": "CARTAGENA \u00b7 CRIME",
        "chip_label": "ALL FREED",
        "headline": "Cartagena hostages freed in dawn raid",
        "deck": "Security forces storm the \u00c9xito supermarket, freeing "
                "all remaining hostages; one captor killed.",
        "source": "AP \u00b7 El Tiempo",
        "chip": ("CONFIRMED", GREEN), "scene": "supermarket",
    },
    {
        "num": 11, "kicker": "GAZA CITY \u00b7 WAR",
        "chip_label": "SHATI CAMP",
        "headline": "Israeli strike kills Hamas security chief",
        "deck": "Abu al-Awf, his wife and two daughters die in a strike on "
                "the Shati camp.",
        "source": "Al Jazeera \u00b7 AFP",
        "chip": ("REPORTED", AMBER), "scene": "gaza",
    },
]

# (number, status, headline) — status C green, R grey, CL orange.
BRIEFS = [
    (12, "R", "Thanksgiving-eve data pile: PCE, jobless claims"),
    (13, "R", "Sudan drone strikes kill 19 civilians"),
    (14, "R", "Houthis 60 km from Aden"),
    (15, "C", "Russian strike kills two in Odesa, hits Kyiv"),
    (16, "C", "US Q3 GDP revised to 4.3%"),
    (17, "R", "EU-Balkans summit opens"),
    (18, "R", "US-led group buys Lukoil overseas assets"),
    (19, "C", "47,000 women killed in 2023 (UN)"),
    (20, "R", "Macy's parade postponed, first time in 100 years"),
    (21, "C", "Fed Beige Book at 19:00 UTC"),
    (22, "R", "Storms kill 6 in Brazil, hit 10 towns (Parana)"),
    (23, "R", "EU announces new Russia sanctions"),
    (24, "R", "Kyiv hit a Russian ship in the Gulf of Finland"),
    (25, "C", "Dell record Q3: $54.9bn revenue, AI servers $22bn"),
    (26, "R", "China probes Politburo member Chen"),
    (27, "R", "NATO vows space defence vs Russia"),
    (28, "C", "Dow closes above 50,000 for the first time"),
    (29, "C", "US to host Copa America again in 2028"),
    (30, "C", "Real Madrid rout PSG 5-1 in UCL"),
    (31, "R", "Malaysia to return 6,300 Rohingya"),
    (32, "R", "North Koreans jailed for being Christian, defectors say"),
    (33, "R", "Russia's own figures show nearly 500,000 war dead"),
    (34, "C", "Flinders Island bushfire: 3,000 ha burning"),
    (35, "C", "15-year-old smashes 204 off 53 balls"),
    (36, "R", "Pyongyang: North Korea gives Swiss envoy 48 hours to leave"),
    (37, "R", "Brussels: EU proposes \u20ac500bn quantum fund"),
    (38, "R", "Benghazi: 2 Libyan officers die of raid wounds"),
    (39, "R", "London: UK warns companies of Russian sabotage threat"),
    (40, "R", "Kyiv: Zelensky seeks \u20ac115bn in aid for 2027"),
    (41, "CL", "Moscow: Kremlin won't comment on reports of 700,000 dead"),
    (42, "R", "Paris: Surprise Eurostar strike cancels trains"),
    (43, "R", "Jerusalem: Knesset advances bill for 7 October inquiry"),
    (44, "R", "Washington: FCC clears SpaceX for 1 million orbital data centres"),
    (45, "R", "London: Poundland collapses, putting 11,000 jobs at risk"),
    (46, "R", "Karachi: Building collapse kills at least 3, injures 14"),
    (47, "R", "Russian strikes kill 5, cut power in 5 regions"),
    (48, "C", "Dhaka: Garment workers offered higher minimum wage"),
    (49, "C", "Cape Town: Court lifts 'Farmgate' ruling against Ramaphosa"),
    (50, "R", "Enugu: Nollywood legend Pete Edochie dies at 79"),
]

TAG_FILL = {"C": GREEN, "R": (107, 114, 128), "CL": ORANGE}

DATE_CHECK = (
    "DATE CHECK \u2014 Every story above happened or was first reported on "
    "Wednesday 25 November 2026. Left out, not 25 November: Houthi strike "
    "on Riyadh's tallest tower (Tue 24) \u00b7 CAS reinstates Senegal as "
    "AFCON champions (Tue 24) \u00b7 CIA\u2013ODNI system breach first "
    "reported (Tue 24) \u00b7 Huawei verdict (Tue 24) \u00b7 Miss Universe "
    "crowned in San Juan (Tue 24, local) \u00b7 Argentina's recession data "
    "(Tue 24) \u00b7 WHO Ebola staff evacuated from Akwe hospital (Tue 24) "
    "\u00b7 Nvidia's 31.5% surge on Huang's return (Mon 23). NOT YET: US "
    "Thanksgiving (Thu 26) \u00b7 Bundestag budget vote (Fri 27) \u00b7 "
    "Bangladesh wage starts (December)."
)

LEGEND = ("OFFICIAL an authority's own word \u00b7 REPORTED press report "
          "\u00b7 CLAIM one side's account, unverified")
SOURCES = ("Sources: Al Jazeera, Reuters, AP, AFP, DW, France 24, CNBC, "
           "Korea Times/Yonhap, ABS, Ofgem, ESA. Every drawing original.")

TOMORROW = [
    "US Thanksgiving: markets shut; travel peaks",
    "Tariff comment period opens; firms file",
    "Shenzhou-24 crew begins station experiments",
]


# -------------------------------------------------------------------- scenes
def scene_ship(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    draw.rectangle([x, y, x + w, y + int(h * 0.42)], fill=(238, 244, 250))
    base = y + int(h * 0.58)
    draw.rectangle([x, y + int(h * 0.58), x + w, y + h], fill=SEA)
    draw.rectangle([x, y + int(h * 0.58), x + w, y + int(h * 0.58) + 3],
                   fill=(120, 180, 215))
    # waves in the lower sea
    for wy, wx0, wx1 in [(base + 34, 20, 90), (base + 46, 120, 210),
                         (base + 40, 260, 340), (base + 54, 40, 130),
                         (base + 56, 300, 400)]:
        if wy < y + h - 4:
            draw.line([x + wx0, wy, x + wx1, wy], fill=(140, 195, 225),
                      width=2)
    # stacked containers on the deck (3 rows on the tall lead scene)
    cols = [(178, 34, 34), (37, 99, 235), (22, 163, 74), (220, 160, 20),
            (124, 58, 237)]
    rows = 3 if h >= 120 else 2
    cw, chh = int(w * 0.085), 14
    for row in range(rows):
        for i in range(9):
            cx = x + 10 + i * (cw + 3)
            cy = base - (row + 1) * (chh + 2)
            draw.rectangle([cx, cy, cx + cw, cy + chh],
                           fill=cols[(i + row) % len(cols)],
                           outline=(255, 255, 255), width=1)
    # hull
    draw.polygon([(x + 4, base), (x + w - 4, base), (x + w - 18, base + 24),
                  (x + 20, base + 24)], fill=(30, 41, 59))
    draw.rectangle([x + 4, base, x + w - 4, base + 3], fill=(178, 34, 34))
    # bridge tower
    draw.rectangle([x + w - 56, base - rows * 16 - 22, x + w - 32, base],
                   fill=(226, 232, 240), outline=(148, 156, 168))
    draw.rectangle([x + w - 56, base - rows * 16 - 22, x + w - 32,
                    base - rows * 16 - 13], fill=(37, 99, 235))
    # country-rate chips painted on the hull side
    rates = ["CHINA 20%", "INDIA 25%", "EU 15%", "VIETNAM 35%"]
    f = sans_b(10)
    rx = x + 12
    for label in rates:
        twd = int(tw(draw, label, f))
        draw.rounded_rectangle([rx, base + 7, rx + twd + 9, base + 19],
                               radius=2, fill=(255, 255, 255))
        draw.text((rx + 4, base + 8), label, font=f, fill=INK)
        rx += twd + 14
    # big labels baked into the sky
    f2 = sans_b(30)
    label = "UP TO 35%"
    draw.text((x + 50, y + 6), label, font=f2, fill=(255, 255, 255),
              stroke_width=2, stroke_fill=NAVY)
    f3 = sans_b(13)
    badge_t = "14 ECONOMIES"
    bw = int(tw(draw, badge_t, f3)) + 16
    draw.rounded_rectangle([x + w - bw - 10, y + 8, x + w - 10, y + 28],
                           radius=3, fill=NAVY)
    draw.text((x + w - bw - 2, y + 11), badge_t, font=f3,
              fill=(255, 220, 120))


def scene_chart(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(10, 14, 24))
    for gy in range(1, 4):
        gyv = y + int(h * gy / 4)
        draw.line([x + 6, gyv, x + w - 6, gyv], fill=(38, 48, 66), width=1)
    top = y + int(h * 0.42)
    bot = y + int(h * 0.86)
    pts = [(x + 12, top), (x + int(w * 0.25), top + 6),
           (x + int(w * 0.42), top + 4), (x + int(w * 0.58), top + 16),
           (x + int(w * 0.74), top + 26), (x + int(w * 0.88), bot)]
    draw.line(pts, fill=(220, 60, 60), width=3, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 90, 90),
                     outline=(255, 255, 255), width=1)
    fbig = sans_b(22 if h < 80 else 26)
    draw.text((x + w - tw(draw, "-6.2%", fbig) - 10, y + 3), "-6.2%",
              font=fbig, fill=(255, 255, 255))
    fsmall = sans(9)
    labels = [("KOSPI -6.2%", (255, 255, 255)),
              ("SK HYNIX -11.1%", (255, 150, 150)),
              ("SAMSUNG -9.9%", (255, 150, 150)),
              ("TAIEX -4.8%", (200, 205, 215)),
              ("NIKKEI -2.8%", (200, 205, 215))]
    ly = y + h - 11
    lx = x + 8
    for label, col in labels:
        lw = int(tw(draw, label, fsmall))
        if lx + lw > x + w - 8:
            break
        draw.text((lx, ly), label, font=fsmall, fill=col)
        lx += lw + 10
    fend = sans_b(14)
    end = "4,697.51"
    draw.text((x + w - tw(draw, end, fend) - 8, bot - 16), end,
              font=fend, fill=(255, 255, 255))


def scene_space(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(8, 12, 30))
    for i in range(40):
        sx = x + 6 + ((i * 37) % (w - 12))
        sy = y + 4 + ((i * 53) % max(10, (h - 34)))
        r = 1 if i % 5 else 2
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    # Earth curve below
    draw.ellipse([x - int(w * 0.35), y + int(h * 0.86), x + int(w * 1.35),
                  y + int(h * 2.2)], fill=(28, 90, 160))
    draw.ellipse([x - int(w * 0.35), y + int(h * 0.86), x + int(w * 1.35),
                  y + int(h * 2.2)], outline=(120, 190, 240), width=2)
    # solar panels
    ph0, ph1 = y + int(h * 0.52), y + int(h * 0.78)
    draw.rectangle([x + 12, ph0, x + 58, ph1], fill=(30, 90, 180),
                   outline=(150, 200, 250), width=1)
    draw.rectangle([x + w - 58, ph0, x + w - 12, ph1],
                   fill=(30, 90, 180), outline=(150, 200, 250), width=1)
    mid = (ph0 + ph1) // 2
    draw.line([x + 58, mid, x + w - 58, mid], fill=(180, 190, 205), width=3)
    # station modules
    draw.rounded_rectangle([x + int(w * 0.30), ph0 - 4, x + int(w * 0.70),
                            ph1 + 2], radius=6, fill=(200, 208, 218),
                           outline=(120, 130, 145), width=1)
    draw.ellipse([x + int(w * 0.30) - 10, ph0 - 2, x + int(w * 0.30) + 2,
                  ph1], fill=(160, 170, 185), outline=(120, 130, 145))
    # capsule docking below the modules
    draw.ellipse([x + int(w * 0.60), ph1 + 2, x + int(w * 0.70) + 10,
                  y + h - 2], fill=(230, 235, 242),
                 outline=(120, 130, 145))
    # flags on the station
    fy = ph0 + 2
    draw.rectangle([x + int(w * 0.33), fy, x + int(w * 0.33) + 14, fy + 7],
                   fill=(20, 90, 50))
    draw.rectangle([x + int(w * 0.33), fy, x + int(w * 0.33) + 4, fy + 7],
                   fill=(255, 255, 255))
    draw.rectangle([x + int(w * 0.62), fy, x + int(w * 0.62) + 14, fy + 7],
                   fill=(200, 30, 30))
    draw.ellipse([x + int(w * 0.62) + 3, fy + 2, x + int(w * 0.62) + 6,
                  fy + 5], fill=(255, 220, 60))
    # labels
    f = sans_b(11)
    draw.text((x + 34, y + 3), "SHENZHOU-24", font=f, fill=(255, 255, 255))
    f2 = sans_b(10)
    t2 = "TIANGONG"
    draw.text((x + w - tw(draw, t2, f2) - 8, y + 3), t2, font=f2,
              fill=(255, 220, 120))

def scene_port(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 231, 240))
    draw.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(70, 130, 180))
    # cranes
    for cx in (x + 18, x + 58):
        draw.line([cx, y + 6, cx, y + int(h * 0.62)], fill=(60, 70, 80),
                  width=2)
        draw.line([cx, y + 8, cx + 26, y + 8], fill=(60, 70, 80), width=2)
        draw.line([cx + 26, y + 8, cx + 26, y + 20], fill=(60, 70, 80),
                  width=1)
    # smoke on the horizon
    for sx, sy, sr in [(x + w - 30, y + 10, 7), (x + w - 18, y + 6, 9),
                       (x + w - 40, y + 14, 5)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(150, 150, 150))
    # containers and a ship
    for i, c in enumerate([(178, 34, 34), (37, 99, 235), (22, 163, 74)]):
        draw.rectangle([x + 90 + i * 16, y + int(h * 0.62) - 12,
                        x + 90 + i * 16 + 14, y + int(h * 0.62)],
                       fill=c, outline=(255, 255, 255), width=1)
    draw.polygon([(x + 130, y + int(h * 0.62)), (x + w - 8, y + int(h * 0.62)),
                  (x + w - 16, y + h - 4), (x + 138, y + h - 4)],
                 fill=(30, 41, 59))


def scene_strait(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + int(h * 0.45)], fill=(250, 205, 150))
    draw.rectangle([x, y + int(h * 0.45), x + w, y + h], fill=(90, 115, 145))
    draw.ellipse([x + w - 26, y + 2, x + w - 8, y + 20], fill=(255, 220, 140))
    # two tankers
    draw.rectangle([x + 10, y + int(h * 0.55), x + 88, y + int(h * 0.78)],
                   fill=(40, 50, 62))
    draw.rectangle([x + 12, y + int(h * 0.50), x + 86, y + int(h * 0.55)],
                   fill=(200, 210, 220))
    draw.rectangle([x + 120, y + int(h * 0.58), x + 200, y + int(h * 0.80)],
                   fill=(52, 62, 76))
    draw.rectangle([x + 122, y + int(h * 0.53), x + 198, y + int(h * 0.58)],
                   fill=(200, 210, 220))
    # flame on the second tanker
    draw.polygon([(x + 150, y + int(h * 0.53)), (x + 142, y + int(h * 0.30)),
                  (x + 152, y + int(h * 0.40)), (x + 158, y + int(h * 0.22)),
                  (x + 166, y + int(h * 0.40)), (x + 172, y + int(h * 0.53))],
                 fill=(240, 120, 20))
    draw.polygon([(x + 152, y + int(h * 0.53)), (x + 150, y + int(h * 0.38)),
                  (x + 156, y + int(h * 0.44)), (x + 160, y + int(h * 0.36)),
                  (x + 164, y + int(h * 0.53))], fill=(255, 210, 60))
    # mines in the water
    for mx, my in [(x + 100, y + h - 8), (x + 210, y + h - 6),
                   (x + 60, y + h - 5)]:
        draw.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=(20, 26, 34))


def scene_energy(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    # house
    draw.polygon([(x + 12, y + 26), (x + 34, y + 10), (x + 56, y + 26)],
                 fill=(150, 60, 50))
    draw.rectangle([x + 16, y + 26, x + 52, y + h - 4], fill=(232, 222, 205),
                   outline=(120, 100, 80), width=1)
    draw.rectangle([x + 30, y + 32, x + 38, y + h - 4], fill=(90, 60, 40))
    # rising red arrow
    pts = [(x + 66, y + h - 8), (x + 96, y + 26), (x + 126, y + 20),
           (x + 158, y + 6)]
    draw.line(pts, fill=(200, 40, 40), width=3, joint="curve")
    draw.polygon([(x + 158, y + 6), (x + 146, y + 4), (x + 156, y + 16)],
                 fill=(200, 40, 40))
    f = sans_b(13)
    draw.text((x + 72, y + 3), "\u00a32,166", font=f, fill=NAVY)


def scene_treaty(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 234, 226))
    # table
    draw.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(120, 84, 50))
    draw.rectangle([x, y + int(h * 0.62), x + w, y + int(h * 0.62) + 3],
                   fill=(90, 60, 34))
    # flags: Australia (blue) and Solomon Islands (blue/green)
    draw.rectangle([x + 14, y + 8, x + 44, y + 26], fill=(0, 40, 120))
    for dx, dy in [(6, 5), (20, 12), (10, 14)]:
        draw.ellipse([x + 14 + dx, y + 8 + dy, x + 17 + dx, y + 11 + dy],
                     fill=(255, 255, 255))
    draw.rectangle([x + 58, y + 8, x + 88, y + 26], fill=(0, 90, 160))
    draw.polygon([(x + 58, y + 26), (x + 88, y + 8), (x + 88, y + 26)],
                 fill=(0, 140, 70))
    draw.line([x + 58, y + 17, x + 88, y + 17], fill=(255, 220, 60), width=2)
    # signed document
    draw.rectangle([x + 100, y + 14, x + 150, y + 34], fill=(255, 255, 255),
                   outline=(120, 120, 120), width=1)
    for i in range(3):
        draw.line([x + 105, y + 19 + i * 4, x + 145, y + 19 + i * 4],
                  fill=(150, 150, 150), width=1)
    draw.line([x + 128, y + 31, x + 145, y + 31], fill=(30, 60, 160), width=1)
    # small map of the islands
    for ix, iy, ir in [(180, 14, 5), (192, 20, 4), (204, 12, 3), (214, 22, 4)]:
        draw.ellipse([x + ix - ir, y + iy - ir, x + ix + ir, y + iy + ir],
                     fill=(30, 120, 70))


def scene_tanker(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(18, 22, 38))
    draw.rectangle([x, y + int(h * 0.66), x + w, y + h], fill=(60, 64, 72))
    draw.line([x, y + int(h * 0.82), x + w, y + int(h * 0.82)],
              fill=(220, 200, 80), width=1)
    # overturned tanker (tilted)
    draw.polygon([(x + 60, y + 26), (x + 150, y + 12), (x + 156, y + 26),
                  (x + 66, y + 38)], fill=(180, 180, 185),
                 outline=(120, 120, 125))
    draw.ellipse([x + 70, y + 30, x + 82, y + 42], fill=(90, 95, 105))
    # flames
    draw.polygon([(x + 96, y + 30), (x + 88, y + 8), (x + 100, y + 18),
                  (x + 108, y + 4), (x + 118, y + 18), (x + 126, y + 30)],
                 fill=(240, 120, 20))
    draw.polygon([(x + 102, y + 30), (x + 100, y + 16), (x + 108, y + 22),
                  (x + 114, y + 14), (x + 118, y + 30)], fill=(255, 210, 60))
    # nearby cars
    for cx in (x + 20, x + 170):
        draw.rectangle([cx, y + int(h * 0.68), cx + 26, y + int(h * 0.68) + 8],
                       fill=(140, 150, 165))
        draw.rectangle([cx + 4, y + int(h * 0.68) - 5,
                        cx + 20, y + int(h * 0.68)], fill=(120, 130, 145))
    draw.ellipse([x + 30, y + 12, x + 38, y + 20], fill=(220, 220, 200))


def scene_mine(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 220, 205))
    # pit walls
    draw.polygon([(x + 20, y + 10), (x + w - 20, y + 10), (x + w - 46, y + h),
                  (x + 46, y + h)], fill=(140, 105, 70))
    draw.polygon([(x + 40, y + 20), (x + w - 40, y + 20), (x + w - 58, y + h),
                  (x + 58, y + h)], fill=(90, 65, 40))
    # flood water at the bottom
    draw.polygon([(x + 62, y + h - 12), (x + w - 62, y + h - 12),
                  (x + w - 58, y + h), (x + 58, y + h)], fill=(40, 110, 180))
    # rescue figures on the rim
    for fx in (x + 30, x + 52, x + w - 40):
        draw.ellipse([fx - 3, y + 2, fx + 3, y + 8], fill=(200, 60, 40))
        draw.line([fx, y + 8, fx, y + 16], fill=(40, 40, 40), width=2)
        draw.line([fx, y + 16, fx - 3, y + 22], fill=(40, 40, 40), width=1)
        draw.line([fx, y + 16, fx + 3, y + 22], fill=(40, 40, 40), width=1)
    # depth marker
    f = sans_b(11)
    draw.text((x + w - 52, y + 4), "100 m", font=f, fill=NAVY)


def scene_supermarket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + int(h * 0.4)], fill=(250, 225, 170))
    draw.rectangle([x, y + int(h * 0.4), x + w, y + h], fill=(210, 210, 205))
    # shopfront
    draw.rectangle([x + 8, y + 10, x + w - 8, y + h - 4], fill=(235, 235, 230),
                   outline=(150, 150, 145), width=1)
    draw.rectangle([x + 8, y + 10, x + w - 8, y + 22], fill=(0, 130, 70))
    f = sans_b(11)
    t = "\u00c9XITO"
    draw.text((x + w / 2 - tw(draw, t, f) / 2, y + 11), t, font=f,
              fill=(255, 255, 255))
    # open shutters / door
    draw.rectangle([x + 30, y + 26, x + 66, y + h - 4], fill=(60, 70, 80))
    draw.rectangle([x + 76, y + 26, x + w - 30, y + h - 4],
                   fill=(180, 200, 215))
    for sx in range(x + 80, x + w - 34, 8):
        draw.line([sx, y + 26, sx, y + h - 4], fill=(140, 160, 180), width=1)
    # figures walking out
    for fx in (x + 40, x + 52, x + 150):
        draw.ellipse([fx - 3, y + h - 18, fx + 3, y + h - 12],
                     fill=(30, 30, 30))
        draw.line([fx, y + h - 12, fx, y + h - 4], fill=(30, 30, 30),
                  width=2)


def scene_gaza(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + int(h * 0.55)], fill=(120, 90, 130))
    draw.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(70, 60, 75))
    draw.ellipse([x + w - 30, y + 4, x + w - 12, y + 22], fill=(255, 200, 130))
    # city blocks
    for bx, bw, bh in [(x + 8, 34, 22), (x + 46, 30, 30), (x + 120, 36, 26),
                       (x + 160, 40, 20), (x + 204, 30, 28)]:
        draw.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(52, 48, 60))
        for wy in range(y + h - bh + 4, y + h - 4, 7):
            for wx in range(bx + 5, bx + bw - 5, 9):
                draw.rectangle([wx, wy, wx + 4, wy + 4], fill=(255, 210, 110))
    # damaged building with a jagged top
    draw.polygon([(x + 80, y + h), (x + 80, y + 14), (x + 88, y + 20),
                  (x + 94, y + 10), (x + 100, y + 18), (x + 108, y + 12),
                  (x + 114, y + h)], fill=(38, 34, 44))
    # smoke column
    for sx, sy, sr in [(x + 96, y + 6, 6), (x + 100, y + 2, 8),
                       (x + 92, y + 12, 5)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(160, 155, 160))


SCENES = {
    "ship": scene_ship, "chart": scene_chart, "space": scene_space,
    "port": scene_port, "strait": scene_strait, "energy": scene_energy,
    "treaty": scene_treaty, "tanker": scene_tanker, "mine": scene_mine,
    "supermarket": scene_supermarket, "gaza": scene_gaza,
}

# ---------------------------------------------------------------------- map
NA_POLY = [(-168, 66), (-145, 70), (-125, 71), (-110, 73), (-95, 80),
           (-85, 80), (-78, 74), (-68, 62), (-58, 52), (-60, 46),
           (-68, 44), (-74, 40), (-76, 35), (-80, 30), (-81, 25),
           (-84, 20), (-87, 15), (-90, 14), (-92, 15), (-95, 17),
           (-97, 20), (-100, 22), (-105, 23), (-108, 25), (-112, 28),
           (-116, 32), (-120, 35), (-124, 42), (-124, 48), (-130, 55),
           (-140, 60), (-155, 58), (-162, 58), (-166, 62)]
SA_POLY = [(-80, 9), (-77, 6), (-79, -2), (-81, -6), (-80, -12),
           (-76, -16), (-72, -20), (-70, -24), (-70, -30), (-70, -38),
           (-68, -45), (-66, -50), (-68, -54), (-64, -52), (-60, -45),
           (-56, -38), (-50, -32), (-46, -26), (-40, -20), (-36, -12),
           (-35, -6), (-38, -4), (-44, -2), (-50, 0), (-54, 4), (-58, 7),
           (-62, 9), (-68, 11), (-72, 11), (-77, 8)]
AF_POLY = [(-6, 35), (-10, 31), (-15, 27), (-17, 22), (-17, 15),
           (-16, 12), (-13, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4),
           (9, 1), (12, -2), (13, -6), (12, -12), (13, -18), (14, -24),
           (16, -28), (18, -32), (20, -35), (26, -33), (31, -29),
           (34, -26), (36, -22), (39, -17), (40, -12), (41, -8), (43, -3),
           (46, -1), (50, 2), (51, 10), (48, 11), (44, 11), (41, 13),
           (39, 16), (38, 19), (37, 22), (35, 27), (33, 30), (28, 31),
           (22, 32), (16, 32), (11, 34), (6, 37), (0, 36)]
EU_POLY = [(-10, 36), (-9, 38), (-9, 42), (-4, 44), (-2, 47), (-4, 48),
           (-2, 50), (0, 51), (3, 52), (6, 54), (8, 56), (8, 58),
           (10, 59), (6, 61), (6, 63), (11, 65), (14, 67), (19, 69),
           (25, 71), (30, 70), (32, 68), (35, 66), (38, 64), (42, 62),
           (46, 60), (48, 58), (45, 55), (43, 51), (41, 48), (39, 45),
           (36, 44), (32, 45), (29, 44), (27, 42), (25, 40), (23, 37),
           (21, 39), (19, 41), (17, 43), (14, 44), (11, 44), (8, 44),
           (6, 43), (3, 42), (0, 40), (-2, 37), (-6, 36)]
AS_POLY = [(30, 36), (33, 36), (36, 33), (39, 30), (42, 28), (45, 26),
           (48, 29), (50, 29), (52, 27), (55, 26), (58, 25), (61, 25),
           (64, 25), (66, 25), (69, 23), (72, 21), (75, 19), (77, 16),
           (80, 13), (80, 10), (78, 8), (80, 7), (83, 10), (86, 14),
           (88, 19), (90, 22), (92, 21), (94, 18), (96, 16), (98, 14),
           (100, 12), (102, 10), (104, 8), (105, 5), (107, 2), (110, -2),
           (112, -5), (115, -8), (117, -10), (120, -12), (122, -15),
           (125, -18), (128, -20), (130, -22), (133, -25), (136, -28),
           (139, -31), (141, -34), (144, -37), (147, -39), (150, -38),
           (152, -35), (154, -30), (156, -25), (158, -20), (160, -16),
           (162, -12), (162, -8), (160, -4), (158, 0), (156, 3), (153, 5),
           (150, 8), (147, 10), (144, 13), (141, 16), (139, 19), (137, 22),
           (135, 25), (132, 29), (130, 33), (128, 36), (126, 39),
           (124, 40), (122, 38), (120, 35), (118, 31), (115, 28),
           (112, 25), (110, 22), (108, 20), (105, 20), (102, 22),
           (100, 25), (98, 28), (95, 30), (92, 32), (90, 35), (88, 38),
           (86, 41), (83, 43), (80, 45), (78, 48), (75, 50), (72, 52),
           (70, 55), (68, 58), (66, 60), (63, 62), (60, 65), (58, 68),
           (55, 70), (51, 72), (47, 73), (43, 72), (39, 71), (35, 69),
           (32, 67), (30, 65), (28, 62), (25, 60), (22, 58), (19, 55),
           (16, 52), (13, 50), (10, 48), (8, 45), (5, 42), (3, 40),
           (0, 38)]
AU_POLY = [(113, -22), (114, -30), (115, -34), (118, -35), (122, -34),
           (126, -32), (129, -32), (132, -32), (135, -35), (137, -35),
           (139, -37), (141, -38), (144, -38), (146, -39), (149, -37),
           (150, -35), (152, -32), (153, -28), (152, -24), (150, -22),
           (147, -19), (144, -15), (142, -12), (141, -10), (139, -12),
           (137, -13), (135, -14), (133, -12), (131, -12), (128, -14),
           (125, -15), (122, -17), (119, -19), (116, -20)]
NG_POLY = [(131, -1), (134, -3), (137, -4), (140, -6), (143, -7),
           (146, -8), (149, -10), (147, -9), (144, -8), (141, -8),
           (138, -7), (135, -5), (132, -3)]
NZ_POLY = [(167, -45), (169, -43), (171, -41), (173, -40), (175, -38),
           (177, -37), (178, -38), (176, -40), (174, -42), (171, -44),
           (168, -46)]
CONTINENTS = [NA_POLY, SA_POLY, AF_POLY, EU_POLY, AS_POLY, AU_POLY,
              NG_POLY, NZ_POLY]

MAP_X, MAP_W = 16, 330
MAP_Y, MAP_H = 916, 42


def _inside(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and (
                lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def lonlat_to_xy(lon, lat):
    mx = MAP_X + (lon + 168.0) / 360.0 * MAP_W
    my = MAP_Y + (78.0 - lat) / 136.0 * MAP_H
    return mx, my


# (story number, lon, lat, nudge dx, nudge dy in map px)
PINS = [
    (1, -77.0, 39.0, 0, 0),
    (2, 127.0, 37.5, 0, 0),
    (3, 98.5, 39.7, -6, -8),
    (4, 42.9, 14.8, 0, 0),
    (5, 56.5, 26.5, 0, 0),
    (6, -0.1, 51.5, 0, 0),
    (7, 160.0, -9.0, 0, 0),
    (8, 31.2, 30.0, -9, -7),
    (9, 106.8, -6.6, 0, 0),
    (10, -75.5, 10.4, 6, 7),
    (11, 34.5, 31.5, 11, -8),
]


def draw_map(draw):
    # light grid
    for gx in range(MAP_X, MAP_X + MAP_W + 1, 55):
        draw.line([gx, MAP_Y, gx, MAP_Y + MAP_H], fill=(238, 240, 242),
                  width=1)
    for gy in range(MAP_Y, MAP_Y + MAP_H + 1, 16):
        draw.line([MAP_X, gy, MAP_X + MAP_W, gy], fill=(238, 240, 242),
                  width=1)
    # continent dots on a regular pitch
    pitch = 4
    for gy in range(MAP_Y + 2, MAP_Y + MAP_H - 1, pitch):
        lat = 78.0 - (gy - MAP_Y) / MAP_H * 136.0
        for gx in range(MAP_X + 2, MAP_X + MAP_W - 1, pitch):
            lon = (gx - MAP_X) / MAP_W * 360.0 - 168.0
            if any(_inside(lon, lat, poly) for poly in CONTINENTS):
                draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1],
                             fill=(216, 203, 184))
    # pins with leader lines for nudged ones
    for num, lon, lat, dx, dy in PINS:
        tx, ty = lonlat_to_xy(lon, lat)
        px, py = tx + dx, ty + dy
        if dx or dy:
            draw.line([tx, ty, px, py], fill=(120, 120, 120), width=1)
        r = 6
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        f = sans_b(8)
        t = str(num)
        draw.text((px - tw(draw, t, f) / 2, py - 5), t, font=f,
                  fill=(255, 255, 255))


# ------------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 14  # side margin

    # 1. black kicker bar
    d.rectangle([0, 0, W, 20], fill=(0, 0, 0))
    d.text((mx, 4), "THE WORLD IN ONE DAY", font=sans_b(11),
           fill=(255, 255, 255))
    right = ("50 STORIES \u00b7 10 REGIONS \u00b7 18 FIELDS \u00b7 ALL FIRST "
             "REPORTED ON WEDNESDAY 25 NOVEMBER 2026")
    f_r = sans_b(9)
    d.text((W - mx - tw(d, right, f_r), 5), right, font=f_r,
           fill=(255, 255, 255))

    # 2. masthead
    centered(d, 24, "Wednesday 25 November 2026", serif_b(38), NAVY)

    # 3. red deck line
    deck = ("US proposes tariffs on 14 economies \u00b7 AI doubts sink "
            "Asian chip stocks \u00b7 Pakistan's first astronaut docks "
            "at Tiangong")
    f_deck, _ = fit_font(d, deck, W - 2 * mx, 14, 11, bold=True)
    centered(d, 72, deck, f_deck, RED)

    # 4. region strip — dark navy bar with coloured segments, white counts
    d.rectangle([0, 86, W, 106], fill=NAVY)
    seg_w = W / len(REGION_STRIP)
    for i, (name, count, colour) in enumerate(REGION_STRIP):
        sx = int(i * seg_w)
        ex = int((i + 1) * seg_w) - 1
        d.rectangle([sx + 1, 87, ex, 105], fill=colour)
        label = "%s %d" % (name, count)
        f_seg, _ = fit_font(d, label, seg_w - 6, 9, 7, bold=True)
        d.text((sx + (seg_w - tw(d, label, f_seg)) / 2, 92), label,
               font=f_seg, fill=(255, 255, 255))

    # 5. fields strip
    fields = "18 FIELDS \u2014 " + " \u00b7 ".join(
        "%s %d" % (name, count) for name, count in FIELD_STRIP)
    f_f, _ = fit_font(d, fields, W - 2 * mx, 10, 8)
    centered(d, 109, fields, f_f, GREY)

    # 6. IN NUMBERS strip
    cell_w = (W - 2 * mx) / 6.0
    for i, (num, label) in enumerate(NUMBERS):
        cx = mx + i * cell_w
        if i:
            d.line([cx, 124, cx, 168], fill=HAIR, width=1)
        f_n = sans_b(24)
        centered(d, 124, num, f_n, NAVY, cx=cx + cell_w / 2)
        lines = wrap(d, label, sans_b(9), cell_w - 10)
        ly = 152
        for line in lines[:2]:
            centered(d, ly, line, sans_b(9), RED, cx=cx + cell_w / 2)
            ly += 11
    d.line([mx, 172, W - mx, 172], fill=HAIR, width=1)

    # 7. market strip
    parts, total_w = [], 0
    f_m = sans_b(12)
    sep = "   \u00b7   "
    for label, colour in MARKETS:
        parts.append((label, colour))
        total_w += tw(d, label, f_m)
    total_w += tw(d, sep, f_m) * (len(parts) - 1)
    cx = (W - total_w) / 2
    for j, (label, colour) in enumerate(parts):
        d.text((cx, 176), label, font=f_m, fill=colour)
        cx += tw(d, label, f_m)
        if j < len(parts) - 1:
            d.text((cx, 176), sep, font=f_m, fill=GREY)
            cx += tw(d, sep, f_m)

    # 8. THE DAY IN UTC strip
    d.rectangle([0, 190, W, 212], fill=NAVY)
    utc = "THE DAY IN UTC  \u2014  " + "  \u00b7  ".join(
        "%s %s" % (t, txt) for t, txt in UTC_TICKS)
    f_u, _ = fit_font(d, utc, W - 2 * mx, 9, 7)
    centered(d, 197, utc, f_u, (255, 255, 255))

    # 9. hero band — LEAD + STACKED (Revision B)
    hy, hh = 212, 295
    lead_x, lead_w = 14, 548
    right_x, right_w = 570, 440
    # --- lead hero 1
    h1 = HEROES[0]
    d.rectangle([lead_x, hy, lead_x + lead_w, hy + hh], outline=HAIR, width=1)
    draw_scene(img, h1["scene"], lead_x + 1, hy + 1, lead_w - 2, 165)
    badge(d, lead_x + 17, hy + 17, 1, r=14)
    tx = lead_x + 8
    twd = lead_w - 16
    d.text((tx, hy + 170), h1["kicker"], font=sans_b(11), fill=RED)
    para(d, tx, hy + 184, twd, h1["headline"], 22, 18, INK,
         lh_factor=1.1, max_lines=2, bold=True, serif_f=True)
    para(d, tx, hy + 234, twd, h1["deck"], 11, 9, INK,
         lh_factor=1.1, max_lines=3)
    para(d, tx, hy + 272, twd, h1["why"], 11, 9, GREY,
         lh_factor=1.1, max_lines=1, italic=True)
    d.text((tx, hy + hh - 11), h1["source"], font=sans(9), fill=GREY)
    cw, chh = chip_w(d, h1["chip"][0], 9)
    chip(d, lead_x + lead_w - cw - 8, hy + hh - chh - 6, h1["chip"][0],
         h1["chip"][1], size=9)
    # --- stacked heroes 2 and 3
    stack = [(HEROES[1], hy, 142), (HEROES[2], hy + 150, 145)]
    for hero, cy, ch in stack:
        d.rectangle([right_x, cy, right_x + right_w, cy + ch], outline=HAIR,
                    width=1)
        draw_scene(img, hero["scene"], right_x + 1, cy + 1, right_w - 2, 50)
        badge(d, right_x + 15, cy + 15, hero["num"], r=12)
        stx = right_x + 8
        stw = right_w - 16
        d.text((stx, cy + 53), hero["kicker"], font=sans_b(9), fill=RED)
        para(d, stx, cy + 64, stw, hero["headline"], 15, 13, INK,
             lh_factor=1.1, max_lines=2, bold=True, serif_f=True)
        para(d, stx, cy + 97, stw, hero["deck"], 10, 8, INK,
             lh_factor=1.1, max_lines=2)
        para(d, stx, cy + 120, stw, hero["why"], 10, 8, GREY,
             lh_factor=1.1, max_lines=1, italic=True)
        d.text((stx, cy + ch - 11), hero["source"], font=sans(8), fill=GREY)
        cw2, chh2 = chip_w(d, hero["chip"][0], 8)
        chip(d, right_x + right_w - cw2 - 8, cy + ch - chh2 - 5,
             hero["chip"][0], hero["chip"][1], size=8)

    # 10. medium cards, two rows of four
    mw = 243
    mxs = [14, 265, 516, 767]
    for row in range(2):
        for col in range(4):
            med = MEDIUMS[row * 4 + col]
            cx = mxs[col]
            cy = 507 + row * 110
            ch = 110
            d.rectangle([cx, cy, cx + mw, cy + ch], outline=HAIR, width=1)
            draw_scene(img, med["scene"], cx + 1, cy + 1, mw - 2, 40)
            badge(d, cx + 12, cy + 12, med["num"], r=10)
            # scene data chip, top-right inside the scene
            f_sc = sans_b(9)
            lab = med["chip_label"]
            lw = int(tw(d, lab, f_sc)) + 10
            d.rounded_rectangle([cx + mw - lw - 5, cy + 5,
                                 cx + mw - 5, cy + 20], radius=2,
                                fill=(255, 255, 255))
            d.text((cx + mw - lw, cy + 7), lab, font=f_sc, fill=INK)
            mtx = cx + 6
            mtw = mw - 12
            d.text((mtx, cy + 43), med["kicker"], font=sans_b(8), fill=RED)
            para(d, mtx, cy + 53, mtw, med["headline"], 12, 10, INK,
                 lh_factor=1.0, max_lines=2, bold=True)
            para(d, mtx, cy + 78, mtw, med["deck"], 9, 8, INK,
                 lh_factor=1.0, max_lines=2)
            d.text((mtx, cy + ch - 11), med["source"], font=sans(8),
                   fill=GREY)
            cw3, chh3 = chip_w(d, med["chip"][0], 8)
            chip(d, cx + mw - cw3 - 6, cy + ch - chh3, med["chip"][0],
                 med["chip"][1], size=8)

    # 11. navy bar over the brief list
    d.rectangle([0, 727, W, 746], fill=NAVY)
    d.text((mx, 732), "ALSO ON WEDNESDAY 25 NOVEMBER \u2014 39 MORE STORIES",
           font=sans_b(11), fill=(255, 255, 255))
    rbar = "12\u201350 \u00b7 NUMBERED \u00b7 PINNED ON THE MAP BELOW"
    f_rb = sans_b(10)
    d.text((W - mx - tw(d, rbar, f_rb), 733), rbar, font=f_rb,
           fill=(255, 255, 255))

    # 12. brief list, 3 columns x 13 rows
    col_x = [14, 349, 684]
    for idx, (num, tag, head) in enumerate(BRIEFS):
        col = idx // 13
        row = idx % 13
        bx = col_x[col]
        by = 746 + row * 12
        d.text((bx, by), str(num), font=sans_b(10), fill=INK)
        tag_w = 16 if tag != "CL" else 20
        d.rectangle([bx + 22, by + 1, bx + 22 + tag_w, by + 11],
                    fill=TAG_FILL[tag])
        f_t = sans_b(8)
        d.text((bx + 22 + (tag_w - tw(d, tag, f_t)) / 2, by + 2), tag,
               font=f_t, fill=(255, 255, 255))
        f_h, _ = fit_font(d, head, 326 - 46, 10, 8)
        d.text((bx + 46, by), head, font=f_h, fill=INK)

    # 13. bottom band — map left, TOMORROW box right
    d.text((16, 904), "WHERE IT HAPPENED \u00b7 PINS = STORY NUMBERS",
           font=sans_b(9), fill=INK)
    draw_map(d)
    legend_items = [("N.AM", (37, 99, 235)), ("LAT", (13, 148, 136)),
                    ("EUR", (124, 58, 237)), ("ME", (234, 88, 12)),
                    ("N.AF", (146, 64, 14)), ("SSA", (120, 53, 15)),
                    ("S.AS", (219, 39, 119)), ("E&SE", (22, 163, 74)),
                    ("OCE", (101, 163, 13)), ("GLO", (107, 114, 128))]
    lx = 16
    f_l = sans(7)
    for name, colour in legend_items:
        d.ellipse([lx, 961, lx + 6, 967], fill=colour)
        d.text((lx + 8, 960), name, font=f_l, fill=GREY)
        lx += int(tw(d, name, f_l)) + 16
    d.rectangle([360, 904, 1010, 968], fill=NAVY)
    d.text((374, 909), "TOMORROW: WHAT TO WATCH", font=sans_b(12),
           fill=(255, 255, 255))
    for i, line in enumerate(TOMORROW):
        d.text((374, 927 + i * 15), "\u2022  " + line, font=sans(11),
               fill=(255, 255, 255))

    # 14. DATE CHECK strip (R6 fix: the legend line shared the box with the
    # DATE CHECK text and the footer sat on the page edge; rebuilt with real
    # padding throughout — smaller type, legend on its own row inside the
    # box, footer clear of the bottom edge)
    d.rectangle([14, 970, 1010, 1011], outline=RED, width=1, fill=PAPER)
    y4 = 972
    for line in wrap(d, DATE_CHECK, sans(7), 980):
        d.text((22, y4), line, font=sans(7), fill=INK)
        y4 += 9
    combined = LEGEND + "   |   " + SOURCES
    f_c, _ = fit_font(d, combined, 980, 7, 7)
    d.text((22, 1000), combined, font=f_c, fill=GREY)

    # footer
    centered(d, 1013, "Drawn by an AI agent for make.fun \u00b7 Wednesday "
                      "25 November 2026 \u00b7 One page, one day",
             sans(7), GREY)

    img.save(OUT, "PNG")
    return OUT


if __name__ == "__main__":
    render()
    print("wrote", OUT)
