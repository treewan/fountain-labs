#!/usr/bin/env python3
"""Fold the supplier capability document into the data-network page.

The page carried a single monthly figure, three named regions and no account
of what work the footage actually shows. The source document reports daily as
well as monthly actives, nineteen countries rather than three regions, an
industry breakdown, eight task scenes, four structural moats, and a delivery
unit defined precisely enough to price against. This brings the page in line
with it.

Two things the document says are withheld stay withheld: per-country
absolutes and sample packs sit behind an NDA, so coverage is shown as bands,
never as counts. Compliance is stated in the positive — which supply can open
batches today — rather than by listing what is still in progress.

Section numbering shifts: a new 05 lands after cost structure, and everything
below it moves down one.

Run after data_page_patch.py:  python3 tools/data_content_patch.py
"""

import pathlib
import sys

PAGE = pathlib.Path(__file__).resolve().parent.parent / "public" / "data-network.html"

MONO = ("font-family: 'Geist Mono', monospace; font-size: 11px; "
        "letter-spacing: 1.5px; color: #8A8A85")
BODY = "margin: 10px 0 0; font-size: 15px; line-height: 1.6; color: #3A3A38"

# Straight swaps of visible copy. Ordered: the eyebrow goes before the tiles,
# so that replacing "65M" cannot catch the eyebrow's "65M MAU".
SWAPS = [
    ("DATA COLLECTION NETWORK · 65M MAU · SINGAPORE",
     "DATA COLLECTION NETWORK · 19 COUNTRIES · SINGAPORE"),

    ("65 million workers capturing their own work every day, built with "
     "Timemark. Order by spec, receive by the hour, delivered through our "
     "Singapore entity.",
     "60–70 million workers a month capture their own work, across 19 "
     "countries, built with Timemark. Order by spec, receive by effective "
     "hour, delivered through our Singapore entity."),

    # The hero's copy block had been clearing the fixed header by a couple of
    # pixels on a phone; a longer lead pushed it under. Give it the room.
    ('[data-rw="hero"] { height: 72vh !important; min-height: 480px !important; }',
     '[data-rw="hero"] { height: 84vh !important; min-height: 620px !important; }'),

    # The four headline tiles now carry the document's four headline figures.
    (">65M<", ">15–20M<"),
    ("monthly active capturers, co-operated with Timemark",
     "daily active capturers, co-operated with Timemark"),
    (">20M<", ">60–70M<"),
    ("videos a day, uploaded on capture with GPS and timestamp",
     "monthly active users across the network"),
    (">160M<", ">19<"),
    (">photos a day<", ">countries with standing capture pools<"),
    (">10M+<", ">20M<"),
    ("hours already in the pool", "videos uploaded a day, with GPS and timestamp"),

    # The daily video and photograph counts leave the tiles, so they are kept
    # here, where the scale argument is actually made.
    ("This pool adds 80K to 170K hours of new video every day and grows "
     "without a collection budget.",
     "This pool adds 80K to 170K hours of new video every day and grows "
     "without a collection budget. Every upload is stamped with time and "
     "location at the moment it is taken, not afterwards."),

    ("Three regions, one capture behaviour.",
     "Nineteen countries, one capture behaviour."),

    ("By spec, by the hour.", "By spec, by the effective hour."),
]

# Renumbering runs bottom-up so a number never lands on one not yet moved.
RENUMBER = [
    ("08 · WHY IT EXISTS", "10 · WHY IT EXISTS"),
    ("07 · HOW IT FLOWS", "09 · HOW IT FLOWS"),
    ("06 · CAPTURE HARDWARE", "08 · CAPTURE HARDWARE"),
    ("05 · WHAT YOU CAN ORDER", "07 · WHAT YOU CAN ORDER"),
    ("04 · COST STRUCTURE", "05 · COST STRUCTURE"),
]

# What the corpus contains, as distinct from where it comes from. These are
# properties of the footage itself; the moats two sections down are properties
# of the supply that produces it.
QUALITIES = [
    ("LONG TAIL", "Enough trades to reach past the head",
     "Eighteen industry classes inside China and ten more outside it, running "
     "past construction and logistics into utilities, agriculture, waste and "
     "repair. A curated set stops near the head of that distribution. "
     "Deployment happens along the tail."),
    ("DEPTH PER INDUSTRY", "Enough of any one trade to train on",
     "Volume does not thin out as the list lengthens. A single industry "
     "carries enough hours to train against on its own, rather than being "
     "sampled a handful of clips at a time."),
    ("FAILURE AND RECOVERY", "Work that goes wrong, then gets put right",
     "This is footage of real jobs, so it holds mis-grasps, dropped parts, the "
     "wrong tool reached for first, and the correction that follows. "
     "Demonstration data is filmed to succeed. A policy learns to recover only "
     "from footage where something needed recovering."),
    ("GLOBAL VARIANCE", "The same task, done differently",
     "The same job runs differently across nineteen countries — different "
     "tools, materials, layouts and pace. That variance is what tells you how "
     "a robot behaves once it leaves the site it was tuned on."),
]

SCENES = [
    ("Construction · façade · height", "Climbing, aligning members, fastening, setting out", "S", "Greater China · SEA"),
    ("Loading and handling", "Grasping, lifting, stacking, dragging, loading", "S", "All regions"),
    ("Delivery and last mile", "Collection, stairs, doors, hand-off", "S", "Greater China · SEA · LatAm"),
    ("Equipment inspection", "Walking rounds, reading meters, opening cabinets", "A", "Greater China · Middle East"),
    ("Cleaning and public space", "Wiping, sweeping, waste collection, swapping fittings", "A", "Greater China · SEA"),
    ("Kitchen and food service", "Prep, cooking, plating, washing up", "A", "Greater China · LatAm"),
    ("Outdoor repair", "Assembly, tool changes, two-handed work, confined spaces", "B", "All regions"),
    ("Facilities management", "Access control, work orders, starting and stopping plant", "B", "Greater China"),
]

MOATS = [
    ("01", "The pool is already there",
     "This footage is produced every day whether or not an order exists. Ten "
     "times the order volume adds QC and labeling staff, not capture staff — "
     "where a crowdsourced shoot pays proportionally more for every extra hour."),
    ("02", "Spec is enforced at the moment of capture",
     "The app prompts during filming: put both hands in frame, hold the "
     "camera still for ten seconds, that step did not read — take it again. A "
     "few questions follow on tool type and whether the task completed. "
     "Footage is produced to your spec rather than filtered to it afterwards."),
    ("03", "Capturers carry a score",
     "Head- and chest-worn devices are not issued to everyone. Capturers are "
     "scored on delivery record, footage quality and device return, and "
     "hardware goes to those who clear the bar. At fleet scale loss and damage "
     "stop being a cost question and become a capacity one: an unpredictable "
     "attrition rate is a delivery volume you cannot commit to. Higher-scoring "
     "capturers also return a markedly better effective rate."),
    ("04", "Provenance is written at the capture end",
     "Time, coordinates, device fingerprint and upload path are written as the "
     "footage is taken, not attached afterwards. Every sampled clip traces "
     "back to its original upload record."),
]

COMPLIANCE = [
    ("CONSENT CHAIN",
     "Capturer consent covers purpose, retention period and third-party use, "
     "traceable to the individual and the moment it was given."),
    ("DE-IDENTIFICATION",
     "Faces and identifying marks blurred by default; coordinates can be "
     "coarsened on request. Where your licence allows it, unblurred delivery "
     "is available."),
    ("CUSTOMER INFORMATION",
     "Client names, work orders, drawings and nameplates are removed or "
     "masked during QC."),
    ("READY TO RUN",
     "Southeast Asia, Latin America and Middle East supply can open batches "
     "now."),
]


def section(eyebrow, headline, lead, inner):
    return (
        '<section data-rw="sec" style="padding: 96px 0; border-bottom: 1px '
        'solid #E6E6E2">'
        f'<div style="font-family: \'Geist Mono\', monospace; font-size: 14px; '
        f'letter-spacing: 2px; color: #55554F">{eyebrow}</div>'
        f'<h2 data-rw="h2" style="margin: 20px 0 0; font-size: 40px; '
        f'line-height: 1.08; font-weight: 500; letter-spacing: -.03em; '
        f'max-width: 760px; text-wrap: balance">{headline}</h2>'
        '<div style="margin-top: 56px">'
        f'<p style="margin: 0; font-size: 16px; line-height: 1.65; '
        f'color: #3A3A38; max-width: 720px; text-wrap: pretty">{lead}</p>'
        f'{inner}</div></section>'
    )


def scenes_block():
    rows = "".join(
        '<div style="display: grid; grid-template-columns: 1.3fr 2fr .4fr 1.3fr; '
        'gap: 20px; padding: 14px 0; border-top: 1px solid #E6E6E2; '
        'font-size: 14.5px; line-height: 1.5; color: #3A3A38">'
        f'<div style="color: #111; font-weight: 500">{name}</div>'
        f'<div>{actions}</div>'
        f'<div style="font-family: \'Geist Mono\', monospace; color: #8A8A85">{band}</div>'
        f'<div style="color: #55554F">{regions}</div></div>'
        for name, actions, band, regions in SCENES)
    return (
        '<div data-rw="scenes" style="margin-top: 32px">'
        '<div style="display: grid; grid-template-columns: 1.3fr 2fr .4fr 1.3fr; '
        f'gap: 20px; padding-bottom: 10px; {MONO}">'
        '<div>SCENE</div><div>TYPICAL ACTIONS</div><div>DAU</div>'
        '<div>MAIN REGIONS</div></div>'
        f'{rows}'
        '<p style="margin: 20px 0 0; font-size: 13.5px; line-height: 1.6; '
        'color: #8A8A85; max-width: 720px">Bands are 90-day averages, not a '
        'single-day snapshot: S is above 2M daily, A 500K–2M, B 100K–500K. '
        'Per-scene absolutes are released under NDA.</p></div>')


def industry_block():
    china = [("Construction / engineering", "23%"), ("Accommodation / food", "13%"),
             ("Property management", "11%"), ("Wholesale", "8%"),
             ("Transport / warehousing", "7%"), ("Domestic services / repair", "7%"),
             ("Public and environment", "6%"), ("Government / health", "4%"),
             ("Retail", "4%"), ("Other", "4%")]
    world = [("Construction", "20%"), ("Logistics", "17%"), ("Delivery", "13%"),
             ("Public services", "11%"), ("Wholesale", "6%"),
             ("Agriculture / forestry", "4%"), ("Utilities", "3%"),
             ("Manufacturing", "3%"), ("Cleaning / security / repair", "1%"),
             ("Other or self-declared", "23%")]

    def column(title, note, rows):
        items = "".join(
            '<div style="display: flex; justify-content: space-between; '
            'gap: 16px; padding: 9px 0; border-top: 1px solid #E6E6E2; '
            'font-size: 14.5px; color: #3A3A38">'
            f'<span>{label}</span><span style="color: #111; font-weight: 500">'
            f'{pct}</span></div>' for label, pct in rows)
        return (f'<div><div style="{MONO}">{title}</div>'
                f'<p style="margin: 8px 0 14px; font-size: 13px; line-height: 1.55; '
                f'color: #8A8A85">{note}</p>{items}</div>')

    return (
        '<div data-rw="g2" style="margin-top: 32px; display: grid; '
        'grid-template-columns: 1fr 1fr; gap: 32px">'
        + column("CHINA · TOP 10 OF 18",
                 "By national industry classification. Labeled for about "
                 "two-thirds of the region's daily actives.", china)
        + column("REST OF WORLD · TOP 10",
                 "Self-declared in-app. Low coverage, so this shows the shape "
                 "of those who declared, not the size of the pool.", world)
        + '</div>'
        '<p style="margin: 20px 0 0; font-size: 13.5px; line-height: 1.6; '
        'color: #8A8A85; max-width: 720px">The two columns are counted '
        'differently and are not comparable side by side. Each is a share of '
        'that region\'s labeled users.</p>')


def qualities_section():
    cards = "".join(
        '<div style="border-top: 1px solid #111; padding-top: 16px">'
        f'<div style="{MONO}">{tag}</div>'
        f'<div style="margin-top: 10px; font-size: 17px; font-weight: 500; '
        f'letter-spacing: -.01em; color: #111">{title}</div>'
        f'<p style="{BODY}">{body}</p></div>'
        for tag, title, body in QUALITIES)
    return section(
        "04 · WHY IT TRAINS WELL",
        "Breadth, depth, and the parts a demonstration set edits out.",
        "Scale gets a corpus considered. What a policy learns from is which "
        "trades are in it, how much of each, and whether the footage contains "
        "work going wrong as well as work going right.",
        '<div data-rw="g4" style="margin-top: 32px; display: grid; '
        'grid-template-columns: repeat(2, minmax(0,1fr)); gap: 32px">'
        f'{cards}</div>')


def moats_section():
    cards = "".join(
        '<div style="border-top: 1px solid #111; padding-top: 16px">'
        f'<div style="{MONO}">{num}</div>'
        f'<div style="margin-top: 10px; font-size: 17px; font-weight: 500; '
        f'letter-spacing: -.01em; color: #111">{title}</div>'
        f'<p style="{BODY}">{body}</p></div>'
        for num, title, body in MOATS)
    return section(
        "06 · WHY IT IS HARD TO COPY",
        "Four things a competing supplier cannot simply spend its way into.",
        "Capture capacity here is a by-product of work that happens anyway. "
        "That changes what scaling costs, what quality control can enforce, "
        "and what can be promised on a delivery date.",
        '<div data-rw="g4" style="margin-top: 32px; display: grid; '
        'grid-template-columns: repeat(2, minmax(0,1fr)); gap: 32px">'
        f'{cards}</div>')


def compliance_block():
    cards = "".join(
        '<div style="border-top: 1px solid #E6E6E2; padding-top: 16px">'
        f'<div style="{MONO}">{title}</div>'
        f'<p style="{BODY}">{body}</p></div>'
        for title, body in COMPLIANCE)
    return ('<div data-rw="g4" style="margin-top: 40px; display: grid; '
            'grid-template-columns: repeat(4, minmax(0,1fr)); gap: 24px">'
            f'{cards}</div>')


DELIVERY_DETAIL = (
    '<div style="margin-top: 40px; border-top: 1px solid #111; padding-top: 20px">'
    f'<div style="{MONO}">WHAT COUNTS AS AN EFFECTIVE HOUR</div>'
    '<p style="margin: 12px 0 0; font-size: 15px; line-height: 1.65; '
    'color: #3A3A38; max-width: 760px">Hands or the worked object in frame '
    'and not persistently occluded; duration and clarity above threshold; the '
    'task reaching a definite end state — failure counts as an end state; '
    'nothing that cannot be de-identified. Where your standard differs from '
    'ours, yours governs.</p>'
    '<p style="margin: 14px 0 0; font-size: 15px; line-height: 1.65; '
    'color: #3A3A38; max-width: 760px">Every batch ships with its own '
    'effective rate. That rate is the first thing our own production line is '
    'measured on: capture-end prompting, automatic QC and de-duplication, '
    'rejection, labeling — task segmentation, action tags, hand-object '
    'interaction, failure flags — then sampling, then delivery.</p>'
    '<p style="margin: 14px 0 0; font-size: 15px; line-height: 1.65; '
    'color: #3A3A38; max-width: 760px">One week to align on spec, two to '
    'three for a pilot batch delivered with its effective-rate report and '
    'labeling samples, one week to freeze the spec, then rolling delivery — '
    'capacity stepped up scene by scene.</p></div>')


# The scene table is four columns of prose; below 760px that leaves the
# actions column about 100px wide. There the row stacks instead: name and band
# on one line, actions and regions on their own, and the column headings drop
# away since a stacked row does not need them.
SCENES_MOBILE = (
    '@media (max-width: 760px) { '
    '[data-rw="scenes"] > div { grid-template-columns: 1fr auto !important; '
    'gap: 4px 12px !important; } '
    '[data-rw="scenes"] > div > :nth-child(1) { grid-area: 1 / 1; } '
    '[data-rw="scenes"] > div > :nth-child(3) { grid-area: 1 / 2; } '
    '[data-rw="scenes"] > div > :nth-child(2) { grid-area: 2 / 1 / auto / -1; } '
    '[data-rw="scenes"] > div > :nth-child(4) { grid-area: 3 / 1 / auto / -1; '
    'color: #8A8A85 !important; } '
    '[data-rw="scenes"] > div:first-child { display: none !important; } }\n  ')


# The map lives in a 1470x620 frame that scales to the column it sits in. At
# 375px that is 287x93 — a thumbnail, where 13.5px country labels render at
# 2.6px. Below 760px the map is replaced by the same information as a list.
BANDS_LIST = [
    ("10M+", "China"),
    ("1M – 10M", "Vietnam · Indonesia"),
    ("100K – 1M", "Malaysia · Mexico · Philippines · Thailand"),
    ("10K – 100K",
     "Cambodia · South Korea · Ecuador · Colombia · Saudi Arabia · Bolivia · "
     "Peru · India · United Kingdom · Brazil · United States"),
    ("MARKED AS A POINT", "Singapore"),
]

OLD_MAP_BOX = ('<div style="aspect-ratio: 1470/620; width: 100%; background: '
               '#F4F4F2; border-radius: 8px; overflow: hidden; padding: 24px; '
               'box-sizing: border-box">')
NEW_MAP_BOX = ('<div data-rw="mapbox" style="aspect-ratio: 1000/470; width: '
               '100%; background: #F4F4F2; border-radius: 8px; overflow: '
               'hidden; padding: 24px; box-sizing: border-box">')

MAP_LIST_CSS = (
    '[data-rw="maplist"] { display: none; } '
    '@media (max-width: 760px) { '
    '[data-rw="mapbox"] { display: none !important; } '
    '[data-rw="maplist"] { display: block !important; } }\n  ')


def map_list():
    rows = "".join(
        '<div style="padding: 12px 0; border-top: 1px solid #E6E6E2">'
        f'<div style="{MONO}">{band}</div>'
        f'<div style="margin-top: 6px; font-size: 14.5px; line-height: 1.5; '
        f'color: #3A3A38">{names}</div></div>'
        for band, names in BANDS_LIST)
    return ('<div data-rw="maplist" style="background: #F4F4F2; '
            'border-radius: 8px; padding: 20px">'
            f'<div style="{MONO}">DAILY ACTIVE CAPTURERS</div>'
            f'<div style="margin-top: 14px">{rows}</div></div>')


# Eight headline figures rather than four: the document's four, then the
# volume the network actually moves. Four across, two down — reach on the top
# row, throughput on the bottom.
STAT_GRID_OLD = ('data-rw="g4" style="display: grid; grid-template-columns: '
                 'repeat(4, minmax(0,1fr)); gap: 32px; padding-top: 28px; '
                 'border-top: 1px solid rgba(255,255,255,.2)"')
STAT_GRID_NEW = ('data-rw="stats" style="display: grid; grid-template-columns: '
                 'repeat(3, minmax(0,1fr)); gap: 34px 32px; padding-top: 28px; '
                 'border-top: 1px solid rgba(255,255,255,.2)"')

EXTRA_STATS = [
    ("160M", "photographs a day"),
    ("10M+", "hours of video already in the pool"),
]

# Eight tiles in one column is a long scroll on a phone, and g4's own rule
# would do exactly that, so the stat grid gets its own breakpoints.
# Eight numbers set at one size read as a slab. The first row — who, where,
# what work — stays primary; the second row is the volume that backs it up and
# sits a step down, which gives the block a hierarchy to read rather than a
# grid to scan. Both come down from 48px, which was shouting.
STATS_CSS = (
    '[data-rw="stats"] [data-rw="stat"] { font-size: 30px !important; } '
    '[data-rw="stats"] > div:nth-child(n+4) [data-rw="stat"] { '
    'font-size: 24px !important; } '
    '[data-rw="stats"] > div:nth-child(n+4) > div + div { '
    'margin-top: 9px !important; } '
    '@media (max-width: 900px) { [data-rw="stats"] { grid-template-columns: '
    'repeat(2, minmax(0,1fr)) !important; } '
    '[data-rw="stats"] > div:nth-child(n+4) [data-rw="stat"] { '
    'font-size: 30px !important; } } '
    '@media (max-width: 760px) { '
    '[data-rw="stats"] [data-rw="stat"] { font-size: 26px !important; } '
    '[data-rw="stats"] > div:nth-child(n+4) [data-rw="stat"] { '
    'font-size: 26px !important; } }\n  ')


def stat_tiles():
    return "".join(
        '<div><div data-rw="stat" style="font-size: 48px; font-weight: 500; '
        f'letter-spacing: -.04em; line-height: 1">{n}</div>'
        '<div style="margin-top: 12px; font-size: 13.5px; line-height: 1.45; '
        f'color: rgba(255,255,255,.6)">{cap}</div></div>'
        for n, cap in EXTRA_STATS)


def fail(msg):
    print(f"  ! {msg}", file=sys.stderr)
    return 1


def main():
    s = PAGE.read_text()

    for old, new in SWAPS + RENUMBER:
        if old not in s:
            return fail(f"not found: {old[:60]}…")
        s = s.replace(old, new, 1)

    # Coverage section gains the industry split and the scene list, under the
    # map that now carries the nineteen countries.
    anchor = ('<p style="margin: 20px 0 0; font-size: 15px; line-height: 1.6; '
              'color: #55554F')
    idx = s.find("Nineteen countries, one capture behaviour.")
    close = s.find("</section>", idx)
    if idx < 0 or close < 0:
        return fail("coverage section not found")
    s = s[:close] + industry_block() + scenes_block() + s[close:]

    at = s.find("05 · COST STRUCTURE")
    start = s.rfind("<section", 0, at)
    if at < 0 or start < 0:
        return fail("insertion point for the qualities section not found")
    s = s[:start] + qualities_section() + s[start:]

    # The new section sits between cost structure and what you can order.
    marker = "07 · WHAT YOU CAN ORDER"
    at = s.find(marker)
    start = s.rfind("<section", 0, at)
    if at < 0 or start < 0:
        return fail("insertion point for the new section not found")
    s = s[:start] + moats_section() + s[start:]

    # Delivery detail goes at the end of what-you-can-order.
    at = s.find("07 · WHAT YOU CAN ORDER")
    close = s.find("</section>", at)
    if close < 0:
        return fail("order section end not found")
    s = s[:close] + DELIVERY_DETAIL + s[close:]

    # Compliance, stated in the positive, closes the flow section.
    at = s.find("09 · HOW IT FLOWS")
    close = s.find("</section>", at)
    if at < 0 or close < 0:
        return fail("flow section not found")
    s = s[:close] + compliance_block() + s[close:]

    if STAT_GRID_OLD not in s:
        return fail("stat grid not found")
    s = s.replace(STAT_GRID_OLD, STAT_GRID_NEW, 1)
    at = s.find("videos uploaded a day, with GPS and timestamp")
    close = s.find("</div></div>", at)
    if at < 0 or close < 0:
        return fail("end of the stat tiles not found")
    close += len("</div></div>")
    s = s[:close] + stat_tiles() + s[close:]

    if OLD_MAP_BOX not in s:
        return fail("map container not found")
    s = s.replace(OLD_MAP_BOX, NEW_MAP_BOX, 1)
    close = s.find("</iframe></div>") + len("</iframe></div>")
    s = s[:close] + map_list() + s[close:]

    css_anchor = "@media (max-width: 760px) {"
    if css_anchor not in s:
        return fail("mobile media block not found")
    s = s.replace(css_anchor, SCENES_MOBILE + MAP_LIST_CSS + STATS_CSS + css_anchor, 1)

    PAGE.write_text(s)
    print(f"patched {PAGE.name}")
    print("  headline figures: 8 tiles — reach on row one, throughput on row two")
    print(f"  coverage section: industry split + {len(SCENES)} task scenes")
    print(f"  new 04: {len(QUALITIES)} corpus qualities")
    print(f"  new 06: {len(MOATS)} structural moats; sections renumbered to 01–10")
    print(f"  delivery: effective-hour definition, production line, schedule")
    print(f"  compliance: {len(COMPLIANCE)} items, stated in the positive")
    return 0


if __name__ == "__main__":
    sys.exit(main())
