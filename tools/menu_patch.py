#!/usr/bin/env python3
"""Give the homepage a menu button on desktop, and a two-level menu sheet.

The exported page already carries the whole menu machinery — a `menu` flag,
a MENU/CLOSE toggle and a full-screen sheet — but the button is only shown
under 760px, and the sheet lists first-level sections alone.

Two things change here. The button gets a desktop twin, placed in the empty
`hdrR` grid slot that the header already reserves on the right (the existing
`mbtn` keeps the narrow layout to itself, so nothing about mobile moves). And
each first-level row in the sheet gains the pages that sit under it.

The sheet itself needed no unhiding: its visibility rides on an inline
`display: {{ menuD }}`, which outranks the stylesheet rule that hides it, so
it already worked at any width.
"""

import pathlib
import re
import sys

PAGE = pathlib.Path(__file__).resolve().parent.parent / "public" / "index.html"

# Second level, as agreed: the pages and sections that live under each
# first-level entry.
SUB = {
    "Infrastructure": [("Data Collection Network", "/data"),
                       ("Nora · Motion Infra", "/nora")],
    "Production": [("Eden Factory", "/eden")],
    "Ventures": [("Cortexa", "#ventures"), ("Mark", "#ventures"),
                 ("Sparkring", "#ventures")],
    "Insights": [("Nora Memo", "/nora-memo"), ("All posts", "#insights")],
    "About": [("Team", "/team"), ("Contact", "/contact")],
}

ROW = re.compile(
    r'<a href="(?P<href>[^"]+)"(?P<attrs>[^>]*?)style="(?P<style>[^"]+)">'
    r'<span>(?P<label>[^<]+)</span>'
    r'<span style="(?P<numstyle>[^"]+)">(?P<num>\d+)</span></a>'
)

DESKTOP_BUTTON = (
    '<button sc-camel-on-click="{{ menuToggle }}" aria-label="Menu" '
    'style="display: flex; align-items: center; gap: 10px; background: none; '
    'border: 0; padding: 8px 0; color: inherit; font: inherit; '
    'font-family: \'Geist Mono\', monospace; font-size: 12px; '
    'letter-spacing: 1.5px; cursor: pointer; min-height: 44px">'
    '<span>{{ menuLabel }}</span>'
    '<span style="width: 18px; height: 12px; display: flex; '
    'flex-direction: column; justify-content: space-between">'
    '<span style="height: 1.5px; background: currentColor; display: block">'
    '</span>'
    '<span style="height: 1.5px; background: currentColor; display: block">'
    '</span></span></button>'
)

SHEET_DESKTOP_CSS = (
    ' @media (min-width: 761px) { [data-rw="msheet"] { '
    'padding: 116px 48px 40px !important; } '
    '[data-rw="msheet"] > * { max-width: 1080px; width: 100%; '
    'margin-left: auto; margin-right: auto; } }'
    # Hover picks up the brand blue. Scoped to the nav so the sheet's black
    # CTA pill keeps its white label, and !important because every row
    # carries its own inline colour.
    ' [data-rw="msheet"] nav a { transition: color .18s; }'
    ' [data-rw="msheet"] nav a:hover { color: #1E48D8 !important; }'
)


def sub_row(label: str) -> str:
    """The second-level strip that sits under one first-level row."""
    if label not in SUB:
        return ""
    links = "".join(
        f'<a href="{href}" style="color: #55554F; font-size: 14.5px; '
        f'letter-spacing: -.01em">{text}</a>'
        for text, href in SUB[label]
    )
    return (f'<div style="display: flex; flex-wrap: wrap; gap: 8px 26px; '
            f'padding: 0 0 20px">{links}</div>')


def main() -> int:
    s = PAGE.read_text()
    before = s

    # 1 · The desktop button, in the header slot that is already empty and
    #     already hidden under 760px.
    slot = '<div data-rw="hdrR" style="display: flex; justify-content: flex-end; gap: 28px"></div>'
    if slot not in s:
        print("header right slot not found", file=sys.stderr)
        return 1
    s = s.replace(slot, slot.replace("></div>", f">{DESKTOP_BUTTON}</div>"), 1)

    # 2 · Second level under each row. The row keeps its own top border, so the
    #     sub-strip goes inside a wrapper that owns the divider instead.
    start = s.find('data-rw="msheet"')
    nav_start = s.find('<nav style="display: flex; flex-direction: column">', start)
    nav_end = s.find("</nav>", nav_start)
    nav = s[nav_start:nav_end]

    added = []

    def wrap(m):
        label = m.group("label")
        sub = sub_row(label)
        if not sub:
            return m.group(0)
        added.append(label)
        # Move the divider to the wrapper and tighten the row's own padding so
        # the pair reads as one block rather than two stacked rules.
        style = m.group("style")
        wrapper_border = "border-top: 1px solid #E6E6E2"
        if "border-bottom" in style:
            wrapper_border += "; border-bottom: 1px solid #E6E6E2"
        row_style = (style
                     .replace("padding: 22px 0", "padding: 22px 0 10px")
                     .replace("; border-top: 1px solid #E6E6E2", "")
                     .replace("; border-bottom: 1px solid #E6E6E2", ""))
        row = (f'<a href="{m.group("href")}"{m.group("attrs")}'
               f'style="{row_style}"><span>{label}</span>'
               f'<span style="{m.group("numstyle")}">{m.group("num")}</span></a>')
        return f'<div style="{wrapper_border}">{row}{sub}</div>'

    new_nav = ROW.sub(wrap, nav)
    if len(added) != len(SUB):
        print(f"expected {len(SUB)} rows, rewrote {len(added)}: {added}",
              file=sys.stderr)
        return 1
    s = s[:nav_start] + new_nav + s[nav_end:]

    # 3 · Give the sheet room on wide screens; it was only ever laid out for a
    #     phone, and full-bleed 20px gutters read as broken at 1440.
    anchor = '[data-rw="m"], [data-rw="mbtn"], [data-rw="msheet"] { display: none; }'
    if anchor not in s:
        print("base rw rule not found", file=sys.stderr)
        return 1
    s = s.replace(anchor, anchor + SHEET_DESKTOP_CSS, 1)

    PAGE.write_text(s)
    print(f"patched {PAGE.name}: +{len(s) - len(before)} bytes")
    print("second level added under:", ", ".join(added))
    return 0


if __name__ == "__main__":
    sys.exit(main())
