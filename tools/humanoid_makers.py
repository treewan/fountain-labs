#!/usr/bin/env python3
"""Turn the robolist.ai humanoid company board into the demand-side dataset.

Two figures on each row are wider than humanoids: RoboScore is the maker's
score across every category it lists in, and the robot count is its whole
catalogue. robolist ranks humanoids on a separate board that only exposes its
top 50, so mixing the two scales would be worse than labelling this one.

Source of truth is the snapshot in data/robolist-humanoid-2026-09-06.json, taken
from the board's own scores-as-of date. Re-scrape with --scrape when it moves on.

    python3 tools/humanoid_makers.py            # snapshot -> public/_assets/humanoid-makers.js
    python3 tools/humanoid_makers.py --scrape   # refresh the snapshot first
"""
import html
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "data", "robolist-humanoid-2026-09-06.json")
OUT = os.path.join(ROOT, "public", "_assets", "humanoid-makers.js")
BOARD = "https://www.robolist.ai/companies?category=humanoid&sort=rating"

# A maker on this board is not automatically a customer for precision parts.
# Universities, national labs and agencies build one research platform and stop;
# they are kept, but tagged, so the page can show a commercial-only view.
RESEARCH = re.compile(
    r"universit|institut|\bIIT\b|KAIST|KIST|NASA|DARPA|AIST|DLR|Roscosmos|"
    r"Naval Research|Academy of Sciences|RoMeLa|NimbRo|Waseda|Monash|Delft|"
    r"Karlsruhe|Aerospace Center|Research Center|Laborator|\bLab\b|A\*STAR|"
    r"Innovation Center|Willow Garage|Imagineering",
    re.I,
)
# The four buyers already named on supplier rows in the index, so the two
# halves of the page can be joined.
BUYER = {
    "tesla": "Tesla",
    "agibot": "AGI Bot",
    "unitree": "Unitree",
    "figure": "Figure AI",
}
# Names carrying a legal suffix read badly in a card grid.
TRIM = re.compile(
    r",?\s*(Co\.,? ?Ltd\.?|Corp Ltd\.?|Pte\.? Ltd\.?|S\.r\.l\.|SAS|AS|GmbH|Inc\.?|LTD)\.?$",
    re.I,
)


def scrape():
    """Walk the board's pages and re-cut the snapshot."""
    strip = lambda x: html.unescape(re.sub(r"<!--.*?-->|<[^>]+>", "", x)).strip()
    rows = {}
    for page in range(1, 6):
        url = BOARD + ("" if page == 1 else "&page=%d" % page)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        found = re.findall(r'<li class="group relative grid.*?</li>', body, re.S)
        if not found:
            break
        for li in found:
            slug = re.search(r'href="/companies/([a-z0-9\-]+)"', li)
            if not slug:
                continue
            cell = re.search(
                r'<div class="pointer-events-none relative z-10 flex shrink-0 '
                r'items-center gap-3 text-right">(.*?)</div>', li, re.S)
            cell = cell.group(1) if cell else ""
            pick = lambda pat, hay: (strip(re.search(pat, hay, re.S).group(1))
                                     if re.search(pat, hay, re.S) else "")
            rows[slug.group(1)] = {
                "slug": slug.group(1),
                "name": pick(r'class="truncate text-sm font-medium text-brand-text">(.*?)</span>', li),
                "desc": pick(r'class="mt-0\.5 line-clamp-1 text-xs text-brand-muted">(.*?)</p>', li),
                "country": pick(r'class="text-xs text-brand-subtle">(.*?)</span>', cell),
                "score": pick(r'title="RoboScore">(.*?)</span>', cell),
                "robots": re.sub(r"\D", "", pick(
                    r'class="font-mono text-xs text-brand-text">(.*?)robots?</span>', cell)),
                "claimed": 1 if "Claimed" in li else 0,
            }
        if 'page=%d"' % (page + 1) not in body:
            break
    json.dump(list(rows.values()), open(SNAP, "w"), ensure_ascii=False, indent=1)
    print("scraped %d makers -> %s" % (len(rows), os.path.relpath(SNAP, ROOT)))


def build():
    raw = json.load(open(SNAP))
    out = []
    for r in raw:
        if not r["name"] or not r["score"]:
            continue
        # A description that is a marketing line in another language, a bare
        # "null", or the maker's own name adds nothing to a card.
        d = r["desc"]
        if d.lower() in ("null", "none", "") or d.startswith(r["name"]):
            d = ""
        row = {
            "n": TRIM.sub("", r["name"]).strip(),
            "c": r["country"] or "—",
            "s": int(r["score"]),
            "r": int(r["robots"] or 0),
        }
        if d:
            row["d"] = d if len(d) <= 130 else d[:127].rsplit(" ", 1)[0] + "…"
        if RESEARCH.search(r["name"]):
            row["lab"] = True
        if r["slug"] in BUYER:
            row["buy"] = BUYER[r["slug"]]
        if r["claimed"]:
            row["cl"] = True
        out.append(row)
    out.sort(key=lambda x: (-x["s"], x["n"]))
    with open(OUT, "w") as f:
        f.write("window.MAKERS = " + json.dumps(out, ensure_ascii=False) + ";\n")
    labs = sum(1 for r in out if r.get("lab"))
    print("%d makers -> %s" % (len(out), os.path.relpath(OUT, ROOT)))
    print("  %d research platforms, %d commercial" % (labs, len(out) - labs))
    print("  %d joined to a buyer in the supplier index" % sum(1 for r in out if r.get("buy")))
    print("  %d robots in their catalogues (all categories, not humanoid only)"
          % sum(r["r"] for r in out))
    print("  %d countries" % len({r["c"] for r in out if r["c"] != "—"}))


if __name__ == "__main__":
    if "--scrape" in sys.argv:
        scrape()
    build()
