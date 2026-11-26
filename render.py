#!/usr/bin/env python3
"""Sum 25 round 6 renderer. PIL only, deterministic, no network, no timestamps."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def text_w(draw, s, f):
    b = draw.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def text_h(draw, s, f):
    b = draw.textbbox((0, 0), s, font=f)
    return b[3] - b[1]


def fit_font(draw, s, path, start, max_w, min_size=7):
    size = start
    while size > min_size and text_w(draw, s, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def fit_text(draw, s, path, start, max_w, min_size=7):
    """Return (font, text) shrunk so it fits max_w; never truncates with ellipsis."""
    f = fit_font(draw, s, path, start, max_w, min_size)
    return f, s


def wrap(draw, s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(draw, t, f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_n(draw, s, f, max_w, n):
    lines = wrap(draw, s, f, max_w)
    if len(lines) <= n:
        return lines
    # merge extra lines into the last allowed line, shrinking font is handled by caller
    out = lines[:n - 1]
    out.append(" ".join(lines[n - 1:]))
    return out


def fit_wrap(draw, s, path, start, max_w, n, min_size=7):
    """Shrink font until the text wraps to at most n lines; return (font, lines)."""
    size = start
    while size > min_size:
        f = font(path, size)
        lines = wrap(draw, s, f, max_w)
        if len(lines) <= n:
            return f, lines
        size -= 1
    f = font(path, min_size)
    lines = wrap(draw, s, f, max_w)
    while len(lines) > n:
        lines = lines[:n - 1] + [" ".join(lines[n - 1:])]
    return f, lines


NAVY = (16, 32, 64)
DARK = (20, 20, 20)
RED = (178, 24, 24)
GREEN = (22, 120, 60)
AMBER = (176, 120, 0)
GREY = (90, 90, 90)
LGREY = (120, 120, 120)
BG = (255, 255, 255)
CREAM = (250, 247, 240)
SKY = (214, 232, 245)
SEA = (46, 110, 168)

HEROES = [
    {
        "num": 1, "kicker": "WASHINGTON \u00b7 TRADE", "chip": "REPORTED",
        "chip_col": (176, 120, 0),
        "headline": "US proposes tariffs of up to 35% on 14 economies",
        "deck": "Section 301 cites \u2018excess capacity\u2019: Vietnam faces the top 35% rate, India 25%, China 20%, EU 15%; hearings open January 2027.",
        "why": "The widest tariff salvo in months \u2014 every top US trade partner faces duties.",
        "source": "USTR \u00b7 Reuters \u00b7 CNBC",
    },
    {
        "num": 2, "kicker": "SEOUL \u00b7 TOKYO \u00b7 TAIPEI \u00b7 MARKETS", "chip": "CONFIRMED",
        "chip_col": GREEN,
        "headline": "AI doubts sink Asian chip stocks: Kospi closes -6.2%",
        "deck": "Kospi ends at 4,697.51, under 5,000; SK Hynix -11.1%, Samsung -9.9% as banks cut targets; Taiex -4.8% after falling 6.2% intraday.",
        "why": "Markets ask whether the AI boom can ever pay for itself.",
        "source": "Yonhap \u00b7 Korea Times \u00b7 Al Jazeera",
    },
    {
        "num": 3, "kicker": "JIUQUAN, CHINA \u00b7 SPACE", "chip": "OFFICIAL",
        "chip_col": (16, 90, 60),
        "headline": "Pakistan\u2019s first astronaut docks at China\u2019s space station",
        "deck": "Muhammad Zeeshan Ali, 40, first foreigner on Tiangong, flew on Shenzhou-24 with Tang Hongbo and Wu Li; lift-off 00:18 UTC, docking 03:56, stays 5 to 10 days.",
        "why": "A first for Pakistan \u2014 and a first foreign crew member for Tiangong.",
        "source": "CMSA \u00b7 Xinhua",
    },
]

MEDIUM = [
    {"num": 4, "kicker": "HODEIDAH, YEMEN \u00b7 MIDDLE EAST", "chip": "PORT",
     "headline": "Saudi-led strikes hit Hodeidah port",
     "deck": "Raids early Wednesday; Houthis also claim a hit on the Ras Tanura refinery.",
     "source": "Arab News \u00b7 Reuters", "status": "CONFIRMED"},
    {"num": 5, "kicker": "STRAIT OF HORMUZ \u00b7 MIDDLE EAST", "chip": "2 TANKERS",
     "headline": "Two tankers hit by mines in the Strait of Hormuz",
     "deck": "Iran\u2019s IRGC says two oil tankers struck naval mines and caught fire on an unauthorised route.",
     "source": "IRGC \u00b7 Reuters", "status": "CLAIM"},
    {"num": 6, "kicker": "LONDON \u00b7 ENERGY", "chip": "+26%",
     "headline": "UK energy price cap to jump 26% in January",
     "deck": "Ofgem lifts the typical dual-fuel bill from \u00a31,723 to \u00a32,166 a year from 1 Jan.",
     "source": "Ofgem \u00b7 BBC", "status": "OFFICIAL"},
    {"num": 7, "kicker": "CANBERRA \u00b7 DIPLOMACY", "chip": "A$740m",
     "headline": "Solomon Islands signs A$740m security pact",
     "deck": "Ten-year treaty names Australia primary security partner, bars foreign bases.",
     "source": "DFAT \u00b7 ABC", "status": "CONFIRMED"},
    {"num": 8, "kicker": "GIZA, EGYPT \u00b7 DISASTER", "chip": "30+",
     "headline": "Fuel tanker fire kills at least 30 near Cairo",
     "deck": "Tanker overturned and exploded on the Al-Warraq ring road, engulfing nearby cars.",
     "source": "AP \u00b7 Reuters", "status": "REPORTED"},
    {"num": 9, "kicker": "BOGOR, INDONESIA \u00b7 DISASTER", "chip": "9 DEAD",
     "headline": "9 dead, 17 trapped in flooded gold mine",
     "deck": "Rescuers pull bodies from the 100-metre unlicensed pit in West Java; rain hampers pumps.",
     "source": "BNPB \u00b7 AP", "status": "REPORTED"},
    {"num": 10, "kicker": "CARTAGENA \u00b7 CRIME", "chip": "ALL FREED",
     "headline": "Cartagena hostages freed in dawn raid",
     "deck": "Security forces storm the \u00c9xito supermarket, freeing all remaining hostages; one captor killed.",
     "source": "AP \u00b7 El Tiempo", "status": "CONFIRMED"},
    {"num": 11, "kicker": "GAZA CITY \u00b7 WAR", "chip": "SHATI CAMP",
     "headline": "Israeli strike kills Hamas security chief",
     "deck": "Abu al-Awf, his wife and two daughters die in a strike on the Shati camp.",
     "source": "Al Jazeera \u00b7 AFP", "status": "REPORTED"},
    {"num": 12, "kicker": "BROOKLYN, USA \u00b7 JUSTICE", "chip": "10/12",
     "headline": "Huawei guilty on 10 of 12 counts",
     "deck": "Brooklyn jury ends an 11-week trial: bank fraud, sanctions violations, trade-secret theft.",
     "source": "DOJ \u00b7 Bloomberg \u00b7 BBC", "status": "CONFIRMED"},
    {"num": 13, "kicker": "UKRAINE \u00b7 WAR", "chip": "5 REGIONS",
     "headline": "Russian strikes kill 5, cut power in 5 regions",
     "deck": "Zaporizhzhia nuclear plant on diesel after its 17th grid loss this year.",
     "source": "Reuters \u00b7 AP", "status": "REPORTED"},
    {"num": 14, "kicker": "DHAKA \u00b7 LABOUR", "chip": "17,500 TAKA",
     "headline": "Garment workers offered higher minimum wage",
     "deck": "Wage board: 12,500 to 17,500 taka ($100 to $136) a month from December.",
     "source": "AFP", "status": "OFFICIAL"},
    {"num": 15, "kicker": "CAPE TOWN \u00b7 JUSTICE", "chip": "RULING",
     "headline": "Court lifts \u2018Farmgate\u2019 ruling against Ramaphosa",
     "deck": "Judges void the 2022 panel report that opened the way to impeachment.",
     "source": "Reuters", "status": "CONFIRMED"},
]

BRIEFS = [
    (16, "R", "Thanksgiving-eve data pile: PCE, jobless claims"),
    (17, "R", "Sudan drone strikes kill 19 civilians"),
    (18, "R", "Houthis 60 km from Aden"),
    (19, "C", "Russian strike kills two in Odesa, hits Kyiv"),
    (20, "C", "US Q3 GDP revised to 4.3%"),
    (21, "R", "EU-Balkans summit opens"),
    (22, "R", "US-led group buys Lukoil overseas assets"),
    (23, "C", "47,000 women killed in 2023 (UN)"),
    (24, "R", "Macy\u2019s parade postponed, first time in 100 years"),
    (25, "C", "Fed Beige Book at 19:00 UTC"),
    (26, "R", "Storms kill 6 in Brazil, hit 10 towns (Parana)"),
    (27, "R", "EU announces new Russia sanctions"),
    (28, "R", "Kyiv hit a Russian ship in the Gulf of Finland"),
    (29, "C", "Dell record Q3: $54.9bn revenue, AI servers $22bn"),
    (30, "R", "China probes Politburo member Chen"),
    (31, "R", "NATO vows space defence vs Russia"),
    (32, "C", "Dow closes above 50,000 for the first time"),
    (33, "C", "US to host Copa America again in 2028"),
    (34, "C", "Real Madrid rout PSG 5-1 in UCL"),
    (35, "R", "Malaysia to return 6,300 Rohingya"),
    (36, "R", "North Koreans jailed for being Christian, defectors say"),
    (37, "R", "Russia\u2019s own figures show nearly 500,000 war dead"),
    (38, "C", "Flinders Island bushfire: 3,000 ha burning"),
    (39, "C", "15-year-old smashes 204 off 53 balls"),
    (40, "R", "Pyongyang: North Korea gives Swiss envoy 48 hours to leave"),
    (41, "R", "Brussels: EU proposes \u20ac500bn quantum fund"),
    (42, "R", "Benghazi: 2 Libyan officers die of raid wounds"),
    (43, "R", "London: UK warns companies of Russian sabotage threat"),
    (44, "R", "Kyiv: Zelensky seeks \u20ac115bn in aid for 2027"),
    (45, "CL", "Moscow: Kremlin won\u2019t comment on reports of 700,000 dead"),
    (46, "R", "Paris: Surprise Eurostar strike cancels trains"),
    (47, "R", "Jerusalem: Knesset advances bill for 7 October inquiry"),
    (48, "R", "Washington: FCC clears SpaceX for 1 million orbital data centres"),
    (49, "R", "London: Poundland collapses, putting 11,000 jobs at risk"),
    (50, "R", "Karachi: Building collapse kills at least 3, injures 14"),
]

REGIONS = [("N. AMERICA", 10, (40, 90, 160)), ("LATIN AM.", 2, (0, 140, 140)),
           ("EUROPE", 15, (110, 70, 160)), ("MIDDLE EAST", 5, (220, 110, 20)),
           ("N. AFRICA", 2, (160, 110, 60)), ("SUB-SAH. AFRICA", 2, (110, 70, 30)),
           ("SOUTH ASIA", 3, (220, 80, 140)), ("E. & SE ASIA", 7, (20, 140, 70)),
           ("OCEANIA", 2, (90, 170, 90)), ("GLOBAL", 2, (110, 110, 110))]

FIELDS_TXT = ("18 FIELDS \u2014 War 11 \u00b7 Disaster 5 \u00b7 Diplomacy 5 \u00b7 Security 3 \u00b7 Tech 3 \u00b7 "
              "Rights 3 \u00b7 Sport 3 \u00b7 Justice 2 \u00b7 Economy 2 \u00b7 Labour 2 \u00b7 Markets 2 \u00b7 "
              "Business 2 \u00b7 Politics 2 \u00b7 Crime 1 \u00b7 Trade 1 \u00b7 Climate 1 \u00b7 Energy 1 \u00b7 Space 1")

NUMBERS = [("35%", "TOP PROPOSED TARIFF \u00b7 VIETNAM"),
           ("-6.2%", "KOSPI CLOSE \u00b7 AI SELL-OFF"),
           ("+26%", "UK ENERGY CAP FROM 1 JAN"),
           ("30+", "KILLED IN CAIRO TANKER FIRE"),
           ("9", "DEAD, 17 TRAPPED IN JAVA PIT"),
           ("1st", "FOREIGNER ABOARD TIANGONG")]

UTC_TICKS = ["00:18 SHENZHOU-24 LIFTS OFF", "03:56 TIANGONG DOCKS",
             "05:30 TAIEX CLOSES -4.8%", "06:30 KOSPI CLOSES -6.2%",
             "06:35 CREW ENTERS TIANGONG", "07:00 OFGEM CAP +26%",
             "13:00 US TARIFFS PROPOSED", "21:00 DOW ENDS ABOVE 50,000"]

DATE_CHECK = ("DATE CHECK \u2014 Every story above happened or was first reported on Wednesday 25 November 2026. "
              "Left out, not 25 November: Houthi strike on Riyadh\u2019s tallest tower (Tue 24) \u00b7 "
              "CAS reinstates Senegal as AFCON champions (Tue 24) \u00b7 CIA\u2013ODNI system breach first reported (Tue 24) \u00b7 "
              "Miss Universe crowned in San Juan (Tue 24, local) \u00b7 Argentina\u2019s recession data (Tue 24) \u00b7 "
              "WHO Ebola staff evacuated from Akwe hospital (Tue 24) \u00b7 Nvidia\u2019s 31.5% surge on Huang\u2019s return (Mon 23). "
              "NOT YET: US Thanksgiving (Thu 26) \u00b7 Bundestag budget vote (Fri 27) \u00b7 Bangladesh wage starts (December).")

LEGEND_TXT = ("OFFICIAL an authority\u2019s own word \u00b7 REPORTED press report \u00b7 "
              "CLAIM one side\u2019s account, unverified   |   Sources: Al Jazeera, Reuters, AP, AFP, DW, "
              "France 24, CNBC, Korea Times/Yonhap, ABS, Ofgem, ESA. Every drawing original.")

def badge(draw, x, y, num, r=11):
    draw.ellipse([x, y, x + 2 * r, y + 2 * r], fill=RED, outline=(255, 255, 255), width=2)
    f = font(SANS_B, 12)
    t = str(num)
    draw.text((x + r - text_w(draw, t, f) / 2, y + r - text_h(draw, t, f) / 2 - 1),
              t, font=f, fill=(255, 255, 255))


def status_chip(draw, x, y, label, col):
    f = font(SANS_B, 8)
    w = text_w(draw, label, f) + 10
    draw.rounded_rectangle([x, y, x + w, y + 14], radius=7, fill=col)
    draw.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def chip_on_scene(draw, x, y, label):
    f = font(SANS_B, 10)
    w = text_w(draw, label, f) + 12
    draw.rounded_rectangle([x, y, x + w, y + 18], radius=4, fill=(0, 0, 0))
    draw.text((x + 6, y + 3), label, font=f, fill=(255, 255, 255))
    return w


# ---------------- hero scenes ----------------

def hero_ship(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    draw.ellipse([x + w - 52, y + 6, x + w - 20, y + 38], fill=(255, 244, 190))
    # big label top-left, clear of the badge (badge occupies x+6..x+28, y+6..y+28)
    f = font(SANS_B, 24)
    draw.text((x + 34, y + 7), "UP TO 35%", font=f, fill=RED)
    # containers, two rows (stop short of the bridge at the right)
    cols = [(200, 40, 40), (40, 90, 180), (40, 150, 70), (230, 180, 30), (200, 40, 40), (40, 90, 180)]
    cw = (w - 105) // 6
    for i, c in enumerate(cols):
        cx = x + 35 + i * cw
        draw.rectangle([cx, y + 42, cx + cw - 3, y + 60], fill=c)
        draw.rectangle([cx, y + 62, cx + cw - 3, y + 80], fill=c)
    # bridge
    draw.rectangle([x + w - 62, y + 30, x + w - 30, y + 62], fill=(240, 240, 240))
    draw.rectangle([x + w - 58, y + 34, x + w - 34, y + 46], fill=(60, 120, 180))
    # sea + hull
    draw.rectangle([x, y + 96, x + w, y + h], fill=SEA)
    draw.polygon([(x + 18, y + 82), (x + w - 18, y + 82),
                  (x + w - 40, y + 104), (x + 40, y + 104)], fill=(30, 40, 60))
    # rate chips on the hull side
    rates = ["CHINA 20%", "INDIA 25%", "EU 15%", "VIETNAM 35%"]
    cx = x + 46
    f2 = font(SANS_B, 8)
    for r in rates:
        rw = text_w(draw, r, f2) + 10
        draw.rounded_rectangle([cx, y + 86, cx + rw, y + 100], radius=3, fill=(255, 255, 255))
        draw.text((cx + 5, y + 89), r, font=f2, fill=NAVY)
        cx += rw + 5


def hero_chart(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(12, 14, 20))
    # grid
    for gy in range(y + 24, y + h - 20, 22):
        draw.line([(x + 8, gy), (x + w - 8, gy)], fill=(45, 50, 65))
    pts = [(x + 14, y + 22), (x + 60, y + 30), (x + 105, y + 26), (x + 150, y + 44),
           (x + 195, y + 56), (x + 240, y + 74), (x + w - 16, y + 92)]
    draw.line(pts, fill=(230, 40, 40), width=4)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 90, 90))
    f = font(SANS_B, 24)
    t = "-6.2%"
    draw.text((x + w - text_w(draw, t, f) - 10, y + 4), t, font=f, fill=(255, 80, 80))
    f2 = font(SANS_B, 9)
    row1 = ["KOSPI -6.2%", "SK HYNIX -11.1%", "SAMSUNG -9.9%"]
    row2 = ["TAIEX -4.8%", "NIKKEI -2.8%"]
    lx = x + 10
    for lab in row1:
        draw.text((lx, y + h - 34), lab, font=f2, fill=(200, 200, 210))
        lx += text_w(draw, lab, f2) + 12
    lx = x + 10
    for lab in row2:
        draw.text((lx, y + h - 20), lab, font=f2, fill=(200, 200, 210))
        lx += text_w(draw, lab, f2) + 12
    f3 = font(SANS_B, 14)
    draw.text((x + w - text_w(draw, "4,697.51", f3) - 10, y + h - 20),
              "4,697.51", font=f3, fill=(255, 255, 255))


def hero_space(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(8, 10, 28))
    stars = [(18, 14), (60, 30), (110, 12), (160, 26), (210, 10), (260, 30), (300, 16),
             (40, 55), (90, 70), (140, 48), (200, 62), (250, 52), (290, 68), (30, 90), (320, 95)]
    for sx, sy in stars:
        draw.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # Earth curve as a chord polygon, strictly inside the scene
    pts = [(x, y + h - 12)]
    for i in range(21):
        px = x + i * w / 20
        py = y + h - 12 + 10 * (1 - ((px - (x + w / 2)) / (w / 2)) ** 2)
        pts.append((px, py))
    pts.append((x + w, y + h - 12))
    draw.polygon(pts, fill=(70, 140, 210))
    draw.line([(x, y + h - 12), (x + w, y + h - 12)], fill=(30, 90, 170), width=2)
    # station modules
    draw.rectangle([x + 95, y + 62, x + 235, y + 84], fill=(200, 205, 215))
    draw.rectangle([x + 120, y + 46, x + 150, y + 100], fill=(170, 175, 190))
    draw.rectangle([x + 180, y + 46, x + 210, y + 100], fill=(170, 175, 190))
    draw.rectangle([x + 60, y + 68, x + 95, y + 78], fill=(40, 80, 160))
    draw.rectangle([x + 235, y + 68, x + 270, y + 78], fill=(40, 80, 160))
    # capsule docking
    draw.ellipse([x + 268, y + 58, x + 296, y + 88], fill=(240, 240, 240))
    draw.rectangle([x + 258, y + 66, x + 272, y + 80], fill=(220, 60, 60))
    # flags: Pakistan green + white, China red
    draw.rectangle([x + 128, y + 52, x + 144, y + 60], fill=(20, 110, 60))
    draw.rectangle([x + 128, y + 52, x + 132, y + 60], fill=(255, 255, 255))
    draw.rectangle([x + 188, y + 52, x + 204, y + 60], fill=(220, 40, 40))
    draw.text((x + 192, y + 52), "*", font=font(SANS_B, 8), fill=(255, 230, 0))
    f = font(SANS_B, 15)
    t = "SHENZHOU-24"
    draw.text((x + w - text_w(draw, t, f) - 10, y + 6), t, font=f, fill=(255, 255, 255))
    f2 = font(SANS_B, 11)
    draw.text((x + 12, y + h - 28), "TIANGONG", font=f2, fill=(160, 200, 255))


# ---------------- medium scenes (52px tall) ----------------

def scene_port(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(190, 215, 230))
    draw.rectangle([x, y + h - 16, x + w, y + h], fill=(60, 110, 150))
    for cx in (14, 60, 106):
        draw.rectangle([x + cx, y + 6, x + cx + 4, y + h - 16], fill=(70, 70, 80))
        draw.rectangle([x + cx - 8, y + 6, x + cx + 22, y + 10], fill=(70, 70, 80))
    draw.rectangle([x + 20, y + h - 30, x + 44, y + h - 16], fill=(200, 60, 60))
    draw.rectangle([x + 48, y + h - 30, x + 72, y + h - 16], fill=(40, 110, 180))
    draw.ellipse([x + w - 34, y + 4, x + w - 14, y + 20], fill=(150, 150, 150))


def scene_tankers(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(235, 205, 150))
    draw.rectangle([x, y + h - 20, x + w, y + h], fill=(70, 100, 130))
    draw.rectangle([x + 8, y + h - 34, x + 66, y + h - 20], fill=(60, 60, 70))
    draw.rectangle([x + 78, y + h - 34, x + 136, y + h - 20], fill=(90, 60, 60))
    draw.polygon([(x + 96, y + h - 44), (x + 104, y + h - 34), (x + 88, y + h - 34)], fill=(255, 140, 0))
    draw.ellipse([x + 88, y + 6, x + 104, y + 20], fill=(120, 120, 120))
    draw.ellipse([x + 14, y + h - 12, x + 20, y + h - 6], fill=(30, 30, 30))
    draw.ellipse([x + 40, y + h - 10, x + 46, y + h - 4], fill=(30, 30, 30))


def scene_energy(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(250, 240, 220))
    draw.polygon([(x + 20, y + h - 14), (x + 44, y + h - 34), (x + 68, y + h - 14)], fill=(180, 60, 60))
    draw.rectangle([x + 26, y + h - 16, x + 62, y + h - 4], fill=(200, 90, 70))
    draw.line([(x + 78, y + h - 10), (x + 100, y + 22), (x + 118, y + 14), (x + 140, y + 6)],
              fill=(200, 30, 30), width=3)
    draw.polygon([(x + 140, y + 6), (x + 130, y + 4), (x + 138, y + 14)], fill=(200, 30, 30))
    f = font(SANS_B, 11)
    draw.text((x + 84, y + 26), "\u00a32,166", font=f, fill=NAVY)


def scene_treaty(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(220, 225, 240))
    draw.rectangle([x + 10, y + 8, x + 34, y + 24], fill=(0, 60, 140))
    draw.rectangle([x + 40, y + 8, x + 64, y + 24], fill=(0, 130, 90))
    draw.rectangle([x + 74, y + 10, x + 140, y + h - 8], fill=(255, 255, 255))
    draw.line([(x + 80, y + 18), (x + 134, y + 18)], fill=(120, 120, 120))
    draw.line([(x + 80, y + 26), (x + 134, y + 26)], fill=(120, 120, 120))
    draw.line([(x + 80, y + 34), (x + 118, y + 34)], fill=(150, 40, 40), width=2)


def scene_fire(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 28, 40))
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(60, 60, 70))
    draw.rectangle([x + 20, y + h - 30, x + 90, y + h - 12], fill=(150, 150, 160))
    draw.ellipse([x + 30, y + h - 26, x + 34, y + h - 22], fill=(20, 20, 20))
    draw.ellipse([x + 76, y + h - 26, x + 80, y + h - 22], fill=(20, 20, 20))
    draw.polygon([(x + 100, y + h - 12), (x + 112, y + 8), (x + 124, y + h - 12)], fill=(255, 140, 0))
    draw.polygon([(x + 108, y + h - 12), (x + 118, y + 20), (x + 128, y + h - 12)], fill=(255, 220, 0))
    draw.ellipse([x + 116, y + 4, x + 132, y + 18], fill=(90, 90, 90))


def scene_mine(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(200, 185, 150))
    draw.polygon([(x + 20, y + h - 4), (x + 60, y + 10), (x + 100, y + h - 4)], fill=(140, 110, 70))
    draw.rectangle([x, y + h - 14, x + w, y + h], fill=(50, 90, 140))
    draw.rectangle([x + 108, y + 12, x + 124, y + 30], fill=(230, 230, 230))
    draw.rectangle([x + 112, y + 30, x + 120, y + 40], fill=(200, 200, 200))
    f = font(SANS_B, 9)
    draw.text((x + 66, y + 6), "100 m", font=f, fill=(120, 40, 40))


def scene_shop(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 225, 190))
    draw.rectangle([x + 8, y + 10, x + w - 8, y + h - 10], fill=(250, 250, 250))
    draw.rectangle([x + 8, y + 10, x + w - 8, y + 26], fill=(0, 140, 70))
    f = font(SANS_B, 11)
    draw.text((x + 14, y + 13), "\u00c9XITO", font=f, fill=(255, 255, 255))
    draw.rectangle([x + 60, y + 30, x + 84, y + h - 10], fill=(120, 90, 60))
    for fx in (20, 100, 122):
        draw.ellipse([x + fx, y + 32, x + fx + 6, y + 38], fill=(40, 40, 40))
        draw.rectangle([x + fx, y + 38, x + fx + 6, y + h - 4], fill=(60, 60, 180))


def scene_gaza(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 200, 160))
    draw.rectangle([x + 10, y + 18, x + 50, y + h - 6], fill=(170, 160, 150))
    draw.rectangle([x + 58, y + 26, x + 96, y + h - 6], fill=(120, 110, 100))
    draw.polygon([(x + 100, y + h - 6), (x + 112, y + 4), (x + 124, y + h - 6)], fill=(90, 85, 80))
    draw.ellipse([x + 108, y + 2, x + 126, y + 18], fill=(140, 140, 140))
    draw.rectangle([x + 20, y + 26, x + 28, y + 34], fill=(60, 60, 60))


def scene_court(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(235, 225, 205))
    draw.rectangle([x + 8, y + h - 18, x + w - 8, y + h - 6], fill=(120, 80, 40))
    draw.rectangle([x + 50, y + 8, x + 100, y + h - 18], fill=(90, 60, 30))
    draw.ellipse([x + 66, y + 14, x + 84, y + 32], fill=(240, 210, 170))
    draw.rectangle([x + 58, y + 30, x + 92, y + h - 6], fill=(30, 30, 30))
    draw.rectangle([x + 116, y + 10, x + 134, y + 26], fill=(40, 60, 140))


def scene_power(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 70, 90))
    draw.polygon([(x + 70, y + 2), (x + 62, y + 20), (x + 70, y + 20), (x + 62, y + 38)],
                 fill=(255, 220, 0))
    for px in (14, 100):
        draw.line([(x + px, y + h - 6), (x + px + 10, y + 14)], fill=(200, 200, 200), width=3)
        draw.line([(x + px + 20, y + h - 6), (x + px + 10, y + 14)], fill=(200, 200, 200), width=3)
        draw.line([(x + px + 10, y + 14), (x + px + 10, y + 34)], fill=(200, 200, 200), width=3)
    draw.line([(x + 24, y + 20), (x + 110, y + 20)], fill=(180, 180, 180))


def scene_sewing(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(225, 240, 225))
    draw.rectangle([x + 10, y + h - 20, x + 90, y + h - 12], fill=(120, 90, 50))
    draw.rectangle([x + 20, y + 12, x + 60, y + h - 20], fill=(80, 80, 90))
    draw.rectangle([x + 44, y + 24, x + 52, y + h - 20], fill=(200, 200, 200))
    draw.line([(x + 96, y + h - 8), (x + 118, y + 16), (x + 132, y + 10)], fill=(20, 140, 60), width=3)
    for i, cy in enumerate((34, 40, 46)):
        draw.ellipse([x + 100 + i * 12, y + cy, x + 112 + i * 12, y + cy + 8], fill=(230, 190, 60))


def scene_gavel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 235, 225))
    draw.rectangle([x + 30, y + 16, x + 120, y + h - 12], fill=(255, 255, 255))
    draw.line([(x + 40, y + 22), (x + 110, y + 22)], fill=(150, 150, 150))
    draw.line([(x + 40, y + 28), (x + 110, y + 28)], fill=(150, 150, 150))
    draw.rectangle([x + 46, y + 32, x + 96, y + h - 4], fill=(255, 255, 255),
                   outline=RED, width=2)
    f = font(SANS_B, 10)
    draw.text((x + 58, y + 33), "VOID", font=f, fill=RED)
    draw.rectangle([x + 104, y + 8, x + 140, y + 16], fill=(120, 80, 40))


SCENES = {4: scene_port, 5: scene_tankers, 6: scene_energy, 7: scene_treaty,
          8: scene_fire, 9: scene_mine, 10: scene_shop, 11: scene_gaza,
          12: scene_court, 13: scene_power, 14: scene_sewing, 15: scene_gavel}
HERO_SCENES = {1: hero_ship, 2: hero_chart, 3: hero_space}

# ---------------- dotted world map ----------------
# Rough continent polygons in (lon, lat); equirectangular projection.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66), (-75, 62),
     (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35), (-80, 26), (-85, 20),
     (-92, 15), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-155, 58), (-168, 66)],
    [(-80, 9), (-75, 7), (-70, 10), (-62, 9), (-55, 5), (-50, 0), (-45, -5),
     (-40, -10), (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-62, -41),
     (-68, -50), (-72, -54), (-74, -45), (-73, -35), (-72, -25), (-78, -15), (-81, -5),
     (-80, 9)],
    [(-10, 36), (-5, 36), (0, 38), (3, 42), (8, 44), (12, 45), (18, 40), (23, 36),
     (28, 41), (30, 46), (28, 55), (21, 58), (18, 65), (12, 60), (5, 58), (0, 52),
     (-5, 50), (-10, 44), (-10, 36)],
    [(-17, 15), (-15, 27), (-10, 31), (-5, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (48, 11), (44, 15), (40, 20), (35, 22), (32, 29),
     (30, 30), (25, 32), (15, 30), (5, 28), (-5, 25), (-15, 20), (-17, 15)],
    [(-10, 5), (0, 5), (8, 4), (12, -5), (12, -12), (15, -18), (18, -28),
     (20, -35), (28, -33), (32, -28), (35, -20), (40, -15), (40, -10), (35, -2),
     (30, 0), (20, 3), (10, 5), (-10, 5)],
    [(60, 25), (68, 24), (72, 20), (77, 8), (80, 7), (85, 20), (89, 22), (92, 16),
     (95, 16), (100, 8), (103, 2), (105, 8), (108, 12), (110, 20), (115, 25),
     (120, 30), (122, 38), (127, 40), (130, 33), (135, 35), (140, 40), (142, 45),
     (140, 52), (135, 58), (130, 62), (120, 70), (105, 72), (90, 75), (75, 72),
     (68, 68), (60, 60), (55, 50), (50, 45), (48, 40), (52, 38), (58, 30), (60, 25)],
    [(113, -22), (114, -30), (118, -35), (125, -33), (130, -32), (135, -35),
     (140, -38), (146, -39), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -11), (136, -12), (132, -11), (126, -14), (120, -20), (113, -22)],
]

PINS = {1: (-77, 39), 2: (127, 37), 3: (98, 40), 4: (43, 15), 5: (56, 26),
        6: (0, 51), 7: (149, -35), 8: (31, 30), 9: (107, -6), 10: (-75, 10),
        11: (34, 31), 12: (-74, 41), 13: (32, 49), 14: (90, 24), 15: (18, -34)}

PIN_COLOURS = {1: (40, 90, 160), 2: (20, 140, 70), 3: (20, 140, 70), 4: (220, 110, 20),
               5: (220, 110, 20), 6: (110, 70, 160), 7: (90, 170, 90), 8: (160, 110, 60),
               9: (20, 140, 70), 10: (0, 140, 140), 11: (220, 110, 20), 12: (40, 90, 160),
               13: (110, 70, 160), 14: (220, 80, 140), 15: (110, 70, 30)}


def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_map(draw, mx, my, mw, mh):
    draw.rectangle([mx, my, mx + mw, my + mh], fill=(252, 250, 246),
                   outline=(200, 200, 200))
    lon0, lon1, lat0, lat1 = -170, 190, 75, -55
    pitch = 4
    for gy in range(my + 3, my + mh - 2, pitch):
        lat = lat0 + (gy - my) / mh * (lat1 - lat0)
        for gx in range(mx + 3, mx + mw - 2, pitch):
            lon = lon0 + (gx - mx) / mw * (lon1 - lon0)
            if any(point_in_poly(lon, lat, p) for p in CONTINENTS):
                draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(190, 180, 160))
    # pins with leader nudges for the crowded Europe/Levant cluster
    nudge = {1: (-20, 10), 6: (-18, 4), 12: (18, 8), 13: (6, -4),
             11: (14, 12), 8: (-20, 8), 4: (-14, 10), 5: (12, -6), 14: (-14, 10)}
    for num, (lon, lat) in PINS.items():
        px = mx + (lon - lon0) / (lon1 - lon0) * mw
        py = my + (lat0 - lat) / (lat0 - lat1) * mh
        dx, dy = nudge.get(num, (0, 0))
        lx, ly = px + dx, py + dy
        if dx or dy:
            draw.line([(px, py), (lx, ly)], fill=(120, 120, 120), width=1)
        draw.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], fill=PIN_COLOURS[num],
                     outline=(255, 255, 255), width=1)
        f = font(SANS_B, 7)
        t = str(num)
        draw.text((lx - text_w(draw, t, f) / 2, ly - text_h(draw, t, f) / 2 - 1),
                  t, font=f, fill=(255, 255, 255))


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0, x1 = 10, W - 10
    cw = x1 - x0

    # 1. kicker bar
    d.rectangle([0, 0, W, 20], fill=(0, 0, 0))
    f = font(SANS_B, 10)
    d.text((10, 4), "THE WORLD IN ONE DAY", font=f, fill=(255, 255, 255))
    r = "50 STORIES \u00b7 10 REGIONS \u00b7 18 FIELDS \u00b7 ALL FIRST REPORTED ON WEDNESDAY 25 NOVEMBER 2026"
    d.text((W - 10 - text_w(d, r, f), 4), r, font=f, fill=(255, 255, 255))

    # 2. masthead
    f = font(SERIF_B, 52)
    t = "Wednesday 25 November 2026"
    d.text(((W - text_w(d, t, f)) / 2, 22), t, font=f, fill=NAVY)

    # 3. red deck
    f = font(SANS_B, 15)
    t = ("US proposes tariffs on 14 economies \u00b7 AI doubts sink Asian chip stocks \u00b7 "
         "Pakistan\u2019s first astronaut docks at Tiangong")
    d.text(((W - text_w(d, t, f)) / 2, 74), t, font=f, fill=RED)

    # 4. region strip
    y = 94
    seg_w = cw / len(REGIONS)
    for i, (name, cnt, col) in enumerate(REGIONS):
        sx = x0 + i * seg_w
        d.rectangle([sx, y, sx + seg_w - 1, y + 16], fill=col)
        f = font(SANS_B, 8)
        t = "%s %d" % (name, cnt)
        f, t = fit_text(d, t, SANS_B, 8, seg_w - 4, 6)
        d.text((sx + (seg_w - text_w(d, t, f)) / 2, y + 3), t, font=f, fill=(255, 255, 255))

    # 5. fields strip (shrink until it fits the full width)
    y = 112
    f = fit_font(d, FIELDS_TXT, SANS, 10, cw, 7)
    d.text(((W - text_w(d, FIELDS_TXT, f)) / 2, y), FIELDS_TXT, font=f, fill=GREY)

    # 6. IN NUMBERS
    y = 128
    d.rectangle([x0, y, x1, y + 54], fill=(255, 255, 255), outline=(200, 200, 200))
    cell_w = cw / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = x0 + i * cell_w
        if i:
            d.line([(cx, y + 6), (cx, y + 48)], fill=(210, 210, 210))
        f1 = font(SANS_B, 26)
        d.text((cx + (cell_w - text_w(d, num, f1)) / 2, y + 3), num, font=f1, fill=NAVY)
        f2, lines = fit_wrap(d, lab, SANS_B, 8, cell_w - 8, 2, 7)
        ly = y + 32
        for ln in lines[:2]:
            d.text((cx + (cell_w - text_w(d, ln, f2)) / 2, ly), ln, font=f2, fill=RED)
            ly += 9

    # 7. UTC strip (shrink until all 8 ticks fit)
    y = 186
    d.rectangle([x0, y, x1, y + 22], fill=NAVY)
    size = 9
    while size > 7:
        f = font(SANS_B, size)
        if sum(text_w(d, t, f) for t in UTC_TICKS) <= cw - 16 - 7 * 10:
            break
        size -= 1
    f = font(SANS_B, size)
    total = sum(text_w(d, t, f) for t in UTC_TICKS)
    gap = (cw - total - 16) / (len(UTC_TICKS) - 1)
    tx = x0 + 8
    for t in UTC_TICKS:
        d.text((tx, y + 6), t, font=f, fill=(255, 255, 255))
        tx += text_w(d, t, f) + gap

    # 8. heroes
    hy = 212
    hh = 250
    hw = int((cw - 16) / 3)
    scene_h = 118
    for i, hero in enumerate(HEROES):
        hx = x0 + i * (hw + 8)
        d.rectangle([hx, hy, hx + hw, hy + hh], outline=(190, 190, 190), width=1)
        HERO_SCENES[hero["num"]](d, hx + 1, hy + 1, hw - 2, scene_h)
        badge(d, hx + 6, hy + 6, hero["num"])
        ty = hy + scene_h + 6
        f = font(SANS_B, 9)
        t = hero["kicker"]
        f, t = fit_text(d, t, SANS_B, 9, hw - 10, 7)
        d.text((hx + 6, ty), t, font=f, fill=RED)
        ty += 13
        f, lines = fit_wrap(d, hero["headline"], SERIF_B, 17, hw - 12, 2, 13)
        for ln in lines:
            d.text((hx + 6, ty), ln, font=f, fill=NAVY)
            ty += 21
        f, lines = fit_wrap(d, hero["deck"], SANS, 11, hw - 12, 2, 8)
        for ln in lines:
            d.text((hx + 6, ty), ln, font=f, fill=(40, 40, 40))
            ty += 13
        f, lines = fit_wrap(d, "WHY IT MATTERS: " + hero["why"], SANS, 10, hw - 12, 2, 8)
        for ln in lines:
            d.text((hx + 6, ty), ln, font=f, fill=(90, 60, 20))
            ty += 12
        f = font(SANS, 9)
        d.text((hx + 6, hy + hh - 16), hero["source"], font=f, fill=GREY)
        status_chip(d, hx + hw - 78, hy + hh - 18, hero["chip"], hero["chip_col"])
    return img, d

def build_rest(img, d):
    x0, x1 = 10, W - 10
    cw = x1 - x0

    # 9. medium cards, two rows of six
    my = 460
    mh = 118
    mw = int((cw - 5 * 8) / 6)
    for row in range(2):
        for col in range(6):
            m = MEDIUM[row * 6 + col]
            mx = x0 + col * (mw + 8)
            myy = my + row * (mh + 4)
            d.rectangle([mx, myy, mx + mw, myy + mh], outline=(190, 190, 190), width=1)
            SCENES[m["num"]](d, mx + 1, myy + 1, mw - 2, 44)
            chip_on_scene(d, mx + 5, myy + 5, m["chip"])
            badge(d, mx + mw - 26, myy + 4, m["num"], r=9)
            ty = myy + 48
            f = font(SANS_B, 8)
            t = m["kicker"]
            f, t = fit_text(d, t, SANS_B, 8, mw - 8, 6)
            d.text((mx + 4, ty), t, font=f, fill=RED)
            ty += 11
            f, lines = fit_wrap(d, m["headline"], SERIF_B, 11, mw - 8, 2, 9)
            for ln in lines:
                d.text((mx + 4, ty), ln, font=f, fill=NAVY)
                ty += 13
            f, lines = fit_wrap(d, m["deck"], SANS, 8, mw - 8, 2, 7)
            for ln in lines:
                d.text((mx + 4, ty), ln, font=f, fill=(40, 40, 40))
                ty += 10
            f = font(SANS, 8)
            d.text((mx + 4, myy + mh - 11), m["source"], font=f, fill=GREY)

    # 10. navy bar
    y = 704
    d.rectangle([x0, y, x1, y + 20], fill=NAVY)
    f = font(SANS_B, 10)
    d.text((x0 + 6, y + 4), "ALSO ON WEDNESDAY 25 NOVEMBER \u2014 35 MORE STORIES",
           font=f, fill=(255, 255, 255))
    r = "16\u201350 \u00b7 NUMBERED \u00b7 PINNED ON THE MAP BELOW"
    d.text((x1 - 6 - text_w(d, r, f), y + 4), r, font=f, fill=(255, 255, 255))

    # 11. brief list, 3 columns x 12 rows
    by = 728
    col_w = (cw - 16) / 3
    row_h = 10.5
    tag_col = {"C": GREEN, "R": GREY, "CL": (200, 120, 0)}
    for idx, (num, tag, text) in enumerate(BRIEFS):
        col = idx // 12
        row = idx % 12
        bx = x0 + col * (col_w + 8)
        yy = by + row * row_h
        fnum = font(SANS_B, 9)
        d.text((bx, yy), str(num), font=fnum, fill=NAVY)
        nw = text_w(d, str(num), fnum)
        tf = font(SANS_B, 7)
        tw = text_w(d, tag, tf) + 6
        d.rounded_rectangle([bx + nw + 2, yy + 1, bx + nw + 2 + tw, yy + 9], radius=3,
                            fill=tag_col[tag])
        d.text((bx + nw + 5, yy + 1), tag, font=tf, fill=(255, 255, 255))
        tx = bx + nw + 2 + tw + 3
        f = fit_font(d, text, SANS, 9, bx + col_w - tx, 7)
        d.text((tx, yy), text, font=f, fill=(30, 30, 30))

    # 12. bottom band: map left, TOMORROW box right
    by = 860
    bh = 72
    map_w = 330
    draw_map(d, x0, by, map_w, 56)
    f = font(SANS_B, 8)
    leg = "WHERE IT HAPPENED \u00b7 PINS = STORY NUMBERS"
    d.text((x0, by + 58), leg, font=f, fill=NAVY)
    tx = x0 + text_w(d, leg, f) + 8
    # region colour dots (first five fit; rest implied by pin colours)
    dot_cols = [(40, 90, 160), (0, 140, 140), (110, 70, 160), (220, 110, 20), (20, 140, 70)]
    for c in dot_cols:
        if tx + 8 > x0 + map_w:
            break
        d.ellipse([tx, by + 60, tx + 6, by + 66], fill=c)
        tx += 9
    bx = x0 + map_w + 10
    bw = x1 - bx
    d.rectangle([bx, by, bx + bw, by + bh], fill=NAVY)
    f = font(SANS_B, 11)
    d.text((bx + 8, by + 6), "TOMORROW: WHAT TO WATCH", font=f, fill=(255, 220, 100))
    f = font(SANS, 11)
    tom = ("US Thanksgiving: markets shut; travel peaks \u00b7 Tariff comment period opens; "
           "firms file \u00b7 Shenzhou-24 crew begins station experiments")
    lines = wrap(d, tom, f, bw - 16)
    ly = by + 24
    for ln in lines[:3]:
        d.text((bx + 8, ly), ln, font=f, fill=(255, 255, 255))
        ly += 14

    # 13. DATE CHECK strip
    y = 936
    d.rectangle([x0, y, x1, y + 72], fill=(255, 255, 255), outline=RED, width=2)
    f = font(SANS, 9)
    lines = wrap(d, DATE_CHECK, f, cw - 16)
    ly = y + 4
    for ln in lines:
        d.text((x0 + 8, ly), ln, font=f, fill=(30, 30, 30))
        ly += 11
    f2 = font(SANS, 9)
    lines2 = wrap(d, LEGEND_TXT, f2, cw - 16)
    for ln in lines2:
        d.text((x0 + 8, ly), ln, font=f2, fill=GREY)
        ly += 11

    # footer
    f = font(SANS, 8)
    t = "Drawn by an AI agent for make.fun \u00b7 Wednesday 25 November 2026 \u00b7 One page, one day"
    d.text(((W - text_w(d, t, f)) / 2, 1012), t, font=f, fill=LGREY)


def main():
    img, d = build()
    build_rest(img, d)
    img.save(os.path.join(HERE, "entry.png"), "PNG")


if __name__ == "__main__":
    main()
