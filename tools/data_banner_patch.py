#!/usr/bin/env python3
"""Rebuild the data-network banner as a grid of work-scene photographs.

The page shipped with a single hero photograph under two darkening layers.
This swaps the photograph for the eight capture-scene stills laid out as a
grid, and leaves everything above it alone: both masks, the eyebrow, the
headline and the calls to action are untouched.

The grid is markup rather than one stitched file. Nothing on this machine can
composite images — no Pillow, no ImageMagick, and sips only scales and crops —
and the grid is the better answer anyway: no second round of JPEG encoding,
each tile cached on its own, and a layout that can reflow on a phone, where
eight columns of a 4x2 grid would each be a sliver.

Run against a fresh export:  python3 tools/data_banner_patch.py
"""

import pathlib
import sys

PAGE = pathlib.Path(__file__).resolve().parent.parent / "public" / "data-network.html"
ASSETS = PAGE.parent / "_assets"

SCENES = [f"scene-{i:02d}.jpg" for i in range(1, 9)]

OLD_IMG = ('<img src="/_assets/01f80f95f37d3652.jpg" alt="" '
           'style="position: absolute; inset: 0; width: 100%; height: 100%; '
           'object-fit: cover; display: block">')

TILE = ('<img src="/_assets/{name}" alt="" loading="{loading}" '
        'style="width: 100%; height: 100%; object-fit: cover; display: block">')

# Four across, two down. Below 760px the media-query rule turns it two across.
# minmax(0, …) rather than a bare 1fr: a track's automatic minimum is the
# content's own size, so eight tall photographs would otherwise push the rows
# past the hero and overflow it.
GRID_OPEN = ('<div data-rw="hgrid" style="position: absolute; inset: 0; '
             'display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); '
             'grid-template-rows: repeat(2, minmax(0, 1fr)); gap: 0">')

# The page has several 760px blocks; this one stands on its own and is the
# only rule touching hgrid, so it can sit in front of the first of them.
MOBILE_ANCHOR = '@media (max-width: 760px) {'
MOBILE_RULE = ('@media (max-width: 760px) { [data-rw="hgrid"] { '
               'grid-template-columns: repeat(2, minmax(0, 1fr)) !important; '
               'grid-template-rows: repeat(4, minmax(0, 1fr)) !important; } }\n  ')


def main():
    missing = [n for n in SCENES if not (ASSETS / n).exists()]
    if missing:
        print(f"missing tiles in _assets: {', '.join(missing)}", file=sys.stderr)
        return 1

    s = PAGE.read_text()
    if OLD_IMG not in s:
        print("hero image not found (already patched?)", file=sys.stderr)
        return 1

    # The first tile carries the headline's backdrop, so it loads eagerly; the
    # rest can wait, since the masks cover them until they arrive.
    tiles = "".join(
        TILE.format(name=n, loading="eager" if i == 0 else "lazy")
        for i, n in enumerate(SCENES))
    s = s.replace(OLD_IMG, GRID_OPEN + tiles + "</div>", 1)

    if MOBILE_ANCHOR not in s:
        print("mobile media block not found", file=sys.stderr)
        return 1
    s = s.replace(MOBILE_ANCHOR, MOBILE_RULE + MOBILE_ANCHOR, 1)

    PAGE.write_text(s)
    print(f"patched {PAGE.name}: hero is now a {len(SCENES)}-tile grid "
          f"(4x2, 2x4 under 760px)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
