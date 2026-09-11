#!/usr/bin/env python3
"""Country markers for the globe in the makers section.

Twenty-six of the 156 makers name no country in either source. They stay in the
index and off the globe — a marker has to sit somewhere, and there is nowhere
honest to put them.

Emits public/_assets/maker-globe.js.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "public" / "_assets" / "humanoid-makers.js"
OUT = ROOT / "public" / "_assets" / "maker-globe.js"

# Country centres, or the main cluster where the makers actually sit.
AT = {
    "China": (35.0, 110.0), "United States": (39.0, -98.0), "Japan": (36.2, 138.3),
    "Germany": (51.1, 10.4), "South Korea": (36.5, 127.9), "United Kingdom": (54.0, -2.0),
    "Singapore": (1.35, 103.8), "Italy": (42.8, 12.6), "Canada": (56.1, -106.3),
    "Spain": (40.0, -3.7), "Taiwan": (23.7, 121.0), "France": (46.6, 2.4),
    "Poland": (52.0, 19.1), "Hong Kong": (22.3, 114.2), "Luxembourg": (49.8, 6.1),
    "Sweden": (62.2, 15.0), "Thailand": (15.9, 101.0), "Switzerland": (46.8, 8.2),
    "Israel": (31.4, 35.0), "Iran": (32.4, 53.7), "Netherlands": (52.2, 5.3),
}


def main():
    rows = json.loads(re.search(r"(\[.*\])", SRC.read_text(), re.S).group(1))
    by = {}
    unplaced = 0
    for r in rows:
        co = r.get("c") or "—"
        if co == "—":
            unplaced += 1
            continue
        b = by.setdefault(co, {"n": co, "c": 0, "top": []})
        b["c"] += 1
        b["top"].append((r.get("s", 0), r["n"]))

    out = []
    for b in sorted(by.values(), key=lambda b: -b["c"]):
        lat, lon = AT[b["n"]]
        names = [n for _, n in sorted(b["top"], key=lambda t: -t[0])[:4]]
        out.append({"n": b["n"], "c": b["c"], "lat": lat, "lon": lon, "top": names})

    OUT.write_text("window.MAKER_GLOBE = " + json.dumps(out, ensure_ascii=False) + ";\n")
    print("wrote %s: %d countries, %d makers placed, %d with no country"
          % (OUT.name, len(out), sum(b["c"] for b in out), unplaced))
    print("  " + ", ".join("%s %d" % (b["n"], b["c"]) for b in out[:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
