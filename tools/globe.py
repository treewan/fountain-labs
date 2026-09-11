#!/usr/bin/env python3
"""Turn the flat world outlines into lon/lat rings a globe can be drawn from.

The map in this repo is a picture, not geography: its paths are pixels in a
1000x470 box. But the projection that made it is known exactly — longitude is
linear across the width, latitude is Mercator anchored on the Singapore point
it draws — so every point can be inverted back to lon/lat and then re-projected
onto a sphere at runtime.

Rings are simplified on the way out. At globe scale a coastline wiggle below
about a third of a degree is under a pixel, and carrying it would triple the
file for nothing.

Emits public/_assets/globe-land.js.
"""
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORLD = ROOT / "public" / "_assets" / "map-regions.html"
OUT = ROOT / "public" / "_assets" / "globe-land.js"

MIN_STEP = 0.7      # degrees; below this two points land on the same pixel
MIN_RING = 6         # a ring this short is an islet, not a coastline


def lon_of(x):
    return x * 0.36 - 180.0


def lat_of(y):
    return math.degrees(2 * math.atan(math.exp((311.93 - y) / 132.98)) - math.pi / 2)


def main():
    text = WORLD.read_text()
    rings, dropped, points_in, points_out = [], 0, 0, 0

    for d in re.findall(r'<path class="l[0-9]" d="([^"]+)"', text):
        # Each M starts a new ring; the path data is plain absolute points.
        for chunk in d.split("M")[1:]:
            pts = re.findall(r"(-?[\d.]+)\s+(-?[\d.]+)", chunk.replace("Z", " "))
            points_in += len(pts)
            if len(pts) < MIN_RING:
                dropped += 1
                continue
            ring, last = [], None
            for sx, sy in pts:
                lon, lat = lon_of(float(sx)), lat_of(float(sy))
                if abs(lat) > 89.5:                 # the inverse blows up at the poles
                    continue
                if last and abs(lon - last[0]) < MIN_STEP and abs(lat - last[1]) < MIN_STEP:
                    continue
                ring.append([round(lon, 2), round(lat, 2)])
                last = ring[-1]
            if len(ring) < MIN_RING:
                dropped += 1
                continue
            rings.append([c for p in ring for c in p])   # flat, for a smaller file
            points_out += len(ring)

    rings.sort(key=len, reverse=True)
    OUT.write_text("window.GLOBE_LAND = " + json.dumps(rings) + ";\n")
    print("wrote %s: %d rings, %d points (from %d), %d islets dropped"
          % (OUT.name, len(rings), points_out, points_in, dropped))
    print("  %.0f KB" % (OUT.stat().st_size / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
