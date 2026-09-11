#!/usr/bin/env python3
"""Place the supplier index on a map, at the finest level each row supports.

The index carries a city for the 124 listed-company rows and nothing finer than
a country for the rest, so the map is drawn at two levels: Chinese rows are
aggregated to their province, everyone else to their country. That is not a
design choice so much as the shape of the data — claiming state-level detail
for the American rows would be inventing it.

The projection was recovered from the world map already in this repo rather
than assumed. Longitude is linear across the full 1000-unit width; latitude is
Mercator, anchored on the Singapore point that map draws at cx=788.3 cy=308.8
and scaled against the leader-line endpoints it draws for Thailand, Cambodia,
Malaysia and South Korea. The fit holds to about two pixels.

Emits public/_assets/supply-map.js.
"""
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "public" / "_assets" / "supply-chain-data.js"
WORLD = ROOT / "public" / "_assets" / "map-regions.html"
OUT = ROOT / "public" / "_assets" / "supply-map.js"

# --- the recovered projection ------------------------------------------------
def x_of(lon):
    return (lon + 180.0) * 1000.0 / 360.0


def y_of(lat):
    return 311.93 - 132.98 * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


# --- city -> province --------------------------------------------------------
# Taizhou is deliberately absent: 泰州 is in Jiangsu and 台州 in Zhejiang, the
# source says only "Taizhou", and the two are 600km apart. Those rows are
# counted in the national total and left off the province map.
PROVINCE = {
    "Zhejiang": ["Ningbo", "Hangzhou", "Jiaxing", "Shaoxing", "Wenzhou", "Quzhou",
                 "Lishui", "Xinchang", "Tiantaishan", "Zhejiang"],
    "Jiangsu": ["Changzhou", "Suzhou", "Wuxi", "Nanjing", "Nantong", "Yangzhou",
                "Huai'an", "Jingjiang"],
    "Guangdong": ["Shenzhen", "Dongguan", "Guangzhou", "Zhuhai", "Jiangmen",
                  "Foshan", "Huizhou"],
    "Shanghai": ["Shanghai"],
    "Beijing": ["Beijing"],
    "Chongqing": ["Chongqing"],
    "Fujian": ["Ningde", "Xiamen", "Zhangzhou"],
    "Shaanxi": ["Xi'an", "Baoji"],
    "Anhui": ["Wuhu", "Hefei"],
    "Sichuan": ["Mianyang", "Chengdu"],
    "Henan": ["Zhengzhou"],
    "Hebei": ["Handan"],
    "Jiangxi": ["Nanchang"],
    "Shandong": ["Jinan"],
    "Hubei": ["Wuhan"],
    "Hunan": ["Changsha"],
    "Ningxia": ["Yinchuan"],
    "Inner Mongolia": ["Hohhot"],
}
CITY_TO_PROVINCE = {c: p for p, cities in PROVINCE.items() for c in cities}

# Province centres, and capitals where the province is small or a municipality.
AT = {
    "Zhejiang": (29.6, 120.2), "Jiangsu": (32.9, 119.8), "Guangdong": (23.4, 113.4),
    "Shanghai": (31.23, 121.47), "Beijing": (39.90, 116.40), "Chongqing": (29.56, 106.55),
    "Fujian": (26.0, 118.3), "Shaanxi": (34.3, 108.9), "Anhui": (31.8, 117.2),
    "Sichuan": (30.6, 103.9), "Henan": (34.0, 113.6), "Hebei": (38.5, 115.5),
    "Jiangxi": (27.6, 115.9), "Shandong": (36.4, 117.0), "Hubei": (30.9, 112.3),
    "Hunan": (27.6, 111.7), "Ningxia": (38.5, 106.2), "Inner Mongolia": (40.8, 111.7),
    # Countries, for the rows that carry no city.
    "United States": (39.8, -98.6), "Germany": (51.1, 10.4), "Japan": (36.2, 138.3),
    "Switzerland": (46.8, 8.2), "Taiwan": (23.7, 121.0), "South Korea": (36.5, 127.9),
    "Sweden": (62.2, 15.0), "Israel": (31.4, 35.0), "Netherlands": (52.2, 5.3),
    "Italy": (42.8, 12.6), "United Kingdom": (54.0, -2.0), "Austria": (47.6, 14.1),
    "Slovakia": (48.7, 19.7), "China": (35.9, 104.2),
}


def main():
    rows = json.loads(re.search(r"(\[.*\])", SRC.read_text(), re.S).group(1))
    places, unplaced, no_country, no_city = {}, {}, 0, 0

    # Two layers, not one. The world panel rolls everything up to its country,
    # so China reads as its whole total; the China panel splits that total by
    # province. Mixing the levels on one map showed China as the eight rows
    # that happen to carry no city.
    for r in rows:
        co, city = r["co"], (r.get("city") or "").strip()
        if co == "—":
            no_country += 1
            continue
        keys = [(co, "country")]
        if co == "China":
            province = CITY_TO_PROVINCE.get(city) if city and city != "—" else None
            if province:
                keys.append((province, "province"))
            elif city and city != "—":
                unplaced[city] = unplaced.get(city, 0) + 1
            else:
                no_city += 1
        for key, level in keys:
            p = places.setdefault((key, level),
                                  {"n": key, "lv": level, "co": co, "c": 0, "cities": {}})
            p["c"] += 1
            if city and city != "—":
                p["cities"][city] = p["cities"].get(city, 0) + 1

    out = []
    for p in sorted(places.values(), key=lambda p: -p["c"]):
        lat, lon = AT[p["n"]]
        ranked = sorted(p["cities"].items(), key=lambda kv: -kv[1])
        out.append({"n": p["n"], "lv": p["lv"], "co": p["co"], "c": p["c"],
                    "x": round(x_of(lon), 1), "y": round(y_of(lat), 1),
                    # Full city list so a click on the bubble can filter the index.
                    **({"cs": [c for c, _ in ranked]} if ranked else {}),
                    **({"top": [f"{c} {n}" for c, n in ranked[:3]]} if ranked else {})})

    # The world silhouette is reused from the map already in the repo; only the
    # outlines are taken, not its activity shading.
    paths = re.findall(r'<path class="l[0-9]" d="([^"]+)"', WORLD.read_text())

    OUT.write_text(
        "window.SUPPLY_MAP = " + json.dumps(out, ensure_ascii=False) + ";\n"
        "window.WORLD_PATHS = " + json.dumps(paths) + ";\n")

    placed = sum(p["c"] for p in out if p["lv"] == "country")
    print("wrote %s: %d markers, %d of %d rows placed"
          % (OUT.name, len(out), placed, len(rows)))
    print("  %d provinces, %d countries"
          % (sum(1 for p in out if p["lv"] == "province"),
             sum(1 for p in out if p["lv"] == "country")))
    print("  top: " + ", ".join("%s %d" % (p["n"], p["c"]) for p in out[:8]))
    if unplaced:
        print("  city not assigned to a province: "
              + ", ".join("%s (%d rows)" % (c, n) for c, n in unplaced.items()))
    print("  %d Chinese rows carry no city and sit in the national count only" % no_city)
    print("  %d rows have no country in the source" % no_country)
    return 0


if __name__ == "__main__":
    sys.exit(main())
