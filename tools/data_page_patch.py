#!/usr/bin/env python3
"""Rework the data-network page: its banner, and its hardware section.

The page shipped with a single hero photograph under two darkening layers.
This swaps the photograph for the eight capture-scene stills laid out as a
grid, and leaves everything above it alone: both masks, the eyebrow, the
headline and the calls to action are untouched.

The grid is markup rather than one stitched file. Nothing on this machine can
composite images — no Pillow, no ImageMagick, and sips only scales and crops —
and the grid is the better answer anyway: no second round of JPEG encoding,
each tile cached on its own, and a layout that can reflow on a phone, where
eight columns of a 4x2 grid would each be a sliver.

The hardware section is rewritten too. It read as though FOUNTAIN built and
sold its own Ego terminal and data glove; the offer is deployment — putting
the customer's own capture devices on workers already in the field, or
sourcing third-party devices for customers who have none. The headline and
the lead-in change with the two cards, since leaving them would have the
section contradict itself.

The header's two routes back to the homepage are also closed. The page is
sent to customers on its own, and the homepage is not meant to be part of
what they receive: the wordmark stays as a mark rather than a link, and the
"Back" control goes, since a Back that goes nowhere is worse than none.

Run against a fresh export:  python3 tools/data_page_patch.py
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


OLD_H2 = ("Our own Ego terminal and data glove turn footage into "
          "action-labeled data.")
NEW_H2 = "We deploy capture hardware across the network — yours, or sourced for you."

OLD_LEAD = ("Lab-grade first-person capture needs trackers and instrumented "
            "gloves that never leave the lab. We build the same capability as "
            "low-cost wearables workers can put on for a shift, and distribute "
            "them through a network that already exists.")
NEW_LEAD = ("Hardware is rarely the constraint; distribution is. Bring the "
            "capture devices you already use and we put them on workers "
            "already on shift, or we source third-party devices to your spec "
            "where you have none — and run them either way.")

# (eyebrow, body) for the two cards, replacing the pair that described the
# hardware FOUNTAIN used to present as its own.
OLD_CARDS = [
    ("EGO TERMINAL",
     "Head- or chest-worn, both hands free. True first-person view; hand pose "
     "no longer entangled with camera motion."),
    ("DATA GLOVE",
     "Hand and wrist trajectories captured directly. Video becomes "
     "action-labeled video, ready for VLA pre-training rather than visual "
     "pre-training alone."),
]
NEW_CARDS = [
    ("CUSTOMER-SUPPLIED DEVICES",
     "Send us the capture devices you already run. We handle distribution, "
     "worker onboarding and day-to-day operation across the network."),
    ("THIRD-PARTY DEVICES",
     "No hardware of your own? We source, configure and deploy third-party "
     "capture devices to your spec, and operate them the same way."),
]


# The wordmark keeps its markup and styling and loses only its href, so it
# still reads as the mark it is; "Back" is removed outright.
OLD_LOGO_OPEN = '<a href="/" style="display: flex; align-items: center; gap: 12px; color: inherit">'
NEW_LOGO_OPEN = '<div style="display: flex; align-items: center; gap: 12px; color: inherit">'
OLD_BACK = '<a href="/" style="color: inherit">← Back</a>'


def close_homepage_routes(s):
    """Leave the header with no way back to the homepage."""
    if OLD_LOGO_OPEN not in s:
        return None, "header wordmark link not found"
    i = s.index(OLD_LOGO_OPEN)
    end = s.index("</a>", i)
    s = (s[:i] + NEW_LOGO_OPEN + s[i + len(OLD_LOGO_OPEN):end] + "</div>"
         + s[end + len("</a>"):])
    if OLD_BACK not in s:
        return None, "header Back link not found"
    return s.replace(OLD_BACK, "", 1), None


def rewrite_hardware(s):
    """Point the hardware section at deployment rather than at own hardware."""
    for old, new in [(OLD_H2, NEW_H2), (OLD_LEAD, NEW_LEAD)]:
        if old not in s:
            return None, "hardware section copy not found"
        s = s.replace(old, new, 1)
    for (old_eyebrow, old_body), (new_eyebrow, new_body) in zip(OLD_CARDS, NEW_CARDS):
        for old, new in [(old_eyebrow, new_eyebrow), (old_body, new_body)]:
            if old not in s:
                return None, f"card text not found: {old[:40]}…"
            s = s.replace(old, new, 1)
    return s, None


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

    s, err = rewrite_hardware(s)
    if err:
        print(err, file=sys.stderr)
        return 1

    s, err = close_homepage_routes(s)
    if err:
        print(err, file=sys.stderr)
        return 1

    PAGE.write_text(s)
    print(f"patched {PAGE.name}")
    print(f"  hero: {len(SCENES)}-tile grid (4x2, 2x4 under 760px)")
    print("  hardware section: now customer-supplied and third-party deployment")
    print("  header: wordmark unlinked, Back removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
