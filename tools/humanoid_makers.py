#!/usr/bin/env python3
"""Turn the robolist.ai humanoid company board into the demand-side dataset.

Two figures on each row are wider than humanoids: RoboScore is the maker's
score across every category it lists in, and the robot count is its whole
catalogue. robolist ranks humanoids on a separate board that only exposes its
top 50, so mixing the two scales would be worse than labelling this one.

Source of truth is the snapshot in data/robolist-humanoid-2026-09-06.json, taken
from the board's own scores-as-of date. Re-scrape with --scrape when it moves on.

    python3 tools/humanoid_makers.py            # snapshots -> public/_assets/humanoid-makers.js
    python3 tools/humanoid_makers.py --scrape   # refresh the board snapshot first
    python3 tools/humanoid_makers.py --facts    # refresh the per-company snapshot (144 pages)
"""
import html
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "data", "robolist-humanoid-2026-09-06.json")
FACTS = os.path.join(ROOT, "data", "robolist-company-facts-2026-09-06.json")
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


def facts():
    """One page per maker: the site, the money, and who it has shipped to.

    Funding and deployments are thin on purpose over there — a round or a
    customer is only recorded against a public source — so most rows come back
    empty. That absence is carried through rather than filled in.
    """
    strip = lambda x: html.unescape(re.sub(r"<!--.*?-->|<[^>]+>", "", x)).strip()
    out = {}
    robots = {}
    for i, row in enumerate(json.load(open(SNAP)), 1):
        slug = row["slug"]
        req = urllib.request.Request("https://www.robolist.ai/companies/" + slug,
                                     headers={"User-Agent": "Mozilla/5.0"})
        try:
            body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        except Exception as exc:                       # a missing page is data too
            print("  %s: %s" % (slug, exc))
            continue

        def fact(label):
            m = re.search(r"<dt[^>]*>" + label + r"</dt><dd[^>]*>(.*?)</dd>", body, re.S)
            return strip(m.group(1)) if m else ""

        web = re.search(r'href="(https?://[^"]+)"[^>]*aria-label="Website', body)
        raised = re.search(r">Raised</p>\s*<p[^>]*>(.{0,80}?)</p>", body, re.S)
        raised = strip(raised.group(1)) if raised else ""
        ndep = re.search(r">Shipped</p>.{0,400}?tabular-nums sm:text-3xl\">(\d+)</span>", body, re.S)
        block = re.search(r">Shipped</p>(.*?)</ul>", body, re.S)
        deps = []
        if block:
            for item in re.findall(r"<li .*?</li>", block.group(1), re.S):
                who = re.search(r'<span class="font-medium text-brand-text">(.*?)</span>', item, re.S)
                if who:
                    deps.append(strip(who.group(1)))
        price = re.search(r">Price range</p>.{0,200}?tracking-tight text-brand-text\">(.*?)</p>", body, re.S)
        out[slug] = {
            "web": web.group(1) if web else "",
            "hq": fact("HQ"),
            "founded": fact("Founded"),
            "employees": fact("Employees"),
            "stage": fact("Stage"),
            "price": strip(price.group(1)) if price else "",
            "raised": "" if raised.startswith("No confirmed") else raised,
            "deployments": int(ndep.group(1)) if ndep else 0,
            "customers": deps[:4],
        }
        seen = []
        for m in re.finditer(r'href="/robots/[a-z0-9\-]+"[^>]*>(.*?)</a>', body, re.S):
            name = strip(m.group(1))
            if name and len(name) < 50 and name not in seen:
                seen.append(name)
        robots[slug] = seen
        if i % 25 == 0:
            print("  %d/%d" % (i, len(json.load(open(SNAP)))))
    # Every company page carries the same promoted models in its footer. They
    # are not that company's robots, and a name on more than half the pages is
    # the only reliable way to tell furniture from product.
    tally = {}
    for names in robots.values():
        for name in set(names):
            tally[name] = tally.get(name, 0) + 1
    furniture = {n for n, c in tally.items() if c > len(robots) * 0.5}
    for slug, names in robots.items():
        out[slug]["robots"] = [n for n in names if n not in furniture][:3]
    json.dump(out, open(FACTS, "w"), ensure_ascii=False, indent=1)
    print("company facts for %d makers -> %s" % (len(out), os.path.relpath(FACTS, ROOT)))
    print("  dropped %d promoted models that appear on most pages: %s"
          % (len(furniture), ", ".join(sorted(furniture))))


def build():
    raw = json.load(open(SNAP))
    facts_by_slug = json.load(open(FACTS)) if os.path.exists(FACTS) else {}
    out = []
    for r in raw:
        if not r["name"] or not r["score"]:
            continue
        # A bare "null", or a description that is only the maker's name again,
        # adds nothing to a card. A real sentence that happens to open with the
        # company name is not that, and was being thrown away.
        d = r["desc"]
        if d.lower() in ("null", "none", ""):
            d = ""
        elif d.startswith(r["name"]) and len(d) - len(r["name"]) < 15:
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

        f = facts_by_slug.get(r["slug"], {})
        if f.get("web"):
            row["w"] = f["web"]
        if f.get("hq"):
            row["hq"] = f["hq"]
        if f.get("founded"):
            row["f"] = f["founded"].split(" ·")[0]
        if f.get("price"):
            row["p"] = f["price"]
        if f.get("raised"):
            row["cap"] = f["raised"].replace("US$", "$")
        if f.get("deployments"):
            row["dep"] = f["deployments"]
        if f.get("customers"):
            row["dc"] = f["customers"]
        # Where the source carries no description at all, the models it does
        # list are the only real thing left to say about the company.
        if not d and f.get("robots"):
            row["rb"] = f["robots"]
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
    blank = [r["n"] for r in out if not r.get("d") and not r.get("rb")]
    print("  %d with a one-line description, %d falling back to their models, %d with neither%s"
          % (sum(1 for r in out if r.get("d")), sum(1 for r in out if r.get("rb")), len(blank),
             (": " + ", ".join(blank)) if blank else ""))
    print("  %d with a website, %d with funding on file, %d with a named deployment"
          % (sum(1 for r in out if r.get("w")), sum(1 for r in out if r.get("cap")),
             sum(1 for r in out if r.get("dep"))))


if __name__ == "__main__":
    if "--scrape" in sys.argv:
        scrape()
    if "--facts" in sys.argv:
        facts()
    build()
