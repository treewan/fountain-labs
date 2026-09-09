#!/usr/bin/env python3
"""Rework the homepage header nav and menu sheet.

The exported page already carries the menu machinery — a `menu` flag, a
MENU/CLOSE toggle, a full-screen sheet — but the button only showed under
760px, the sheet listed first-level sections alone, and every entry pointed
at the page's *mobile* section ids. Those ids belong to elements the page
hides above 760px, so on a desktop a menu click scrolled to something
invisible and appeared to do nothing.

What this does:

  · gives the button a desktop twin, in the empty `hdrR` grid slot the header
    already reserves on the right (the narrow-width button is untouched)
  · resolves section ids at click time, so one menu entry drives both the
    desktop section and its `m-` prefixed twin
  · lists the second level under each first-level row, on both widths
  · anchors the Accelerator, Venture Studio, Podcast and Blog blocks so the
    second level can land on them rather than on the section top
  · drops Insights and About from the header's inline nav — they stay in the
    sheet
  · widens the sheet's phone gutters above 760px and paints links brand blue
    on hover

Run against a fresh export:  python3 tools/menu_patch.py
"""

import pathlib
import re
import sys

PAGE = pathlib.Path(__file__).resolve().parent.parent / "public" / "index.html"

# label -> (href, handler). A handler is the name of a value exposed by
# renderVals; entries without one are ordinary page links.
SUB = {
    "Infrastructure": [("Robotics Supply Chain", "#platform", "mNavRobotics"),
                       ("Data Collection Network", "/data", None),
                       ("Motion Infra", "/nora", None)],
    "Production": [("Eden Factory", "/eden", None),
                   ("Global Routing", "#routing", "mNavRouting")],
    "Ventures": [("Accelerator", "#ventures", "mNavAccel"),
                 ("Venture Studio", "#ventures", "mNavStudio")],
    "Insights": [("Podcast", "#insights", "mNavPodcast"),
                 ("Blog", "#insights", "mNavBlog")],
    "About": [("Team", "/team", None), ("Contact", "/contact", None)],
}

# First-level rows point at the desktop anchors now; the resolver below falls
# back to the mobile twin when that is the one on screen.
L1_HREF = {
    "Infrastructure": "#platform", "Production": "#platform",
    "Ventures": "#ventures", "Insights": "#insights", "About": "/team",
}

SUB_FONT = "16.5px"

# The header's inline nav inherits this; the wordmark and the MENU button both
# set their own size, so raising it moves the nav links alone.
HDR_FONT = ("<div data-rw=\"hdr\" style=\"padding: 24px 48px; display: grid; "
            "grid-template-columns: 1fr auto 1fr; align-items: center; "
            "font-size: %s\">")

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

SHEET_CSS = (
    ' @media (min-width: 761px) { [data-rw="msheet"] { '
    'padding: 116px 48px 40px !important; } '
    '[data-rw="msheet"] > * { max-width: 1080px; width: 100%; '
    'margin-left: auto; margin-right: auto; } }'
    # Hover picks up the brand blue. Scoped to the nav so the sheet's black
    # CTA pill keeps its white label, and !important because every row
    # carries its own inline colour.
    ' [data-rw="msheet"] nav a { transition: color .18s; }'
    ' [data-rw="msheet"] nav a:hover { color: #1E48D8 !important; }'
    # Second-level entries read as one line divided by rules. On a phone the
    # row wraps, and a line beginning with a divider looks like a mistake, so
    # there the dividers give way to plain gaps.
    ' [data-rw="msheet"] nav a + a::before { content: "|"; color: #C9C9C4;'
    ' padding: 0 14px; font-weight: 400; }'
    ' @media (max-width: 760px) {'
    ' [data-rw="msheet"] nav a + a::before { content: none; }'
    ' [data-rw="msheet"] nav > div > div { gap: 8px 22px !important; } }'
)

OLD_MNAV = '''mnav(id, mp) {
    return (e) => {
      if (e && e.preventDefault) e.preventDefault();
      this.setState({ menu: false, ...(mp ? { mp } : {}) });
      document.body.style.overflow = "";
      setTimeout(() => this.scrollToId(id), 30);
    };
  }'''

NEW_MNAV = '''pickId(ids) {
    // The page ships two parallel section sets — desktop ids and their m-
    // prefixed twins — and hides whichever does not apply at this width. An
    // entry names its targets most-specific first and the first one actually
    // on screen wins, so one entry works at both widths.
    for (const id of ids) {
      const el = document.getElementById(id);
      if (el && el.offsetParent !== null) return id;
    }
    return ids[ids.length - 1];
  }
  mnav(id, mp) {
    const ids = Array.isArray(id) ? id : [id];
    return (e) => {
      if (e && e.preventDefault) e.preventDefault();
      // mp drives the narrow layout's open pillar, pillar the wide one's
      // highlight; a menu click means the same thing on both, so set both.
      this.setState({ menu: false, ...(mp ? { mp, pillar: mp, pinned: true } : {}) });
      if (mp) {
        clearTimeout(this._pinT);
        this._pinT = setTimeout(() => this.setState({ pinned: false }), 1800);
      }
      document.body.style.overflow = "";
      setTimeout(() => this.scrollToId(this.pickId(ids)), 30);
    };
  }'''

OLD_VALS = ('mNavInfra: this.mnav("m-platform", "infra"), '
            'mNavProd: this.mnav("m-platform", "prod"), '
            'mNavVent: this.mnav("m-ventures"), '
            'mNavInsights: this.mnav("m-insights"), '
            'mNavCta: this.mnav("m-cta"),')

NEW_VALS = ('mNavInfra: this.mnav(["platform", "m-platform"], "infra"), '
            'mNavProd: this.mnav(["platform", "m-platform"], "prod"), '
            'mNavVent: this.mnav(["ventures", "m-ventures"]), '
            'mNavInsights: this.mnav(["insights", "m-insights"]), '
            'mNavCta: this.mnav(["cta", "m-cta"]), '
            'mNavRouting: this.mnav(["routing", "m-routing"], "prod"), '
            'mNavRobotics: this.mnav(["robotics-supply", "m-robotics-supply", "platform", "m-platform"], "infra"), '
            'mNavAccel: this.mnav(["accelerator", "m-accelerator", "ventures", "m-ventures"]), '
            'mNavStudio: this.mnav(["venture-studio", "m-venture-studio", "ventures", "m-ventures"]), '
            'mNavPodcast: this.mnav(["podcast", "m-podcast", "insights", "m-insights"]), '
            'mNavBlog: this.mnav(["blog", "m-blog", "insights", "m-insights"]),')

# Each of these blocks is laid out twice — once for the narrow layout, once
# for the wide one — and the two copies differ only in type size. Both get an
# anchor so a menu entry lands on the block itself at either width, rather
# than on the top of the section containing it.
#
# The anchor is a zero-size span placed *before* the block's flex row: putting
# it inside would add a third item to a `space-between` row and shift it.
ANCHORS = [
    ("accelerator", 'font-size: 15px; font-weight: 500; letter-spacing: .18em; '
                    'color: #1E48D8">ACCELERATOR'),
    ("m-accelerator", 'font-size: 14px; font-weight: 500; letter-spacing: .18em; '
                      'color: #1E48D8">ACCELERATOR'),
    ("venture-studio", 'font-size: 15px; font-weight: 500; letter-spacing: .18em; '
                       'color: #1F9D55">VENTURE STUDIO'),
    ("m-venture-studio", 'font-size: 14px; font-weight: 500; letter-spacing: .18em; '
                         'color: #1F9D55">VENTURE STUDIO'),
    ("podcast", 'font-size: 22px; font-weight: 500; letter-spacing: -.02em">Podcast'),
    ("m-podcast", 'font-size: 18px; font-weight: 500; letter-spacing: -.02em">Podcast'),
    ("blog", 'font-size: 22px; font-weight: 500; letter-spacing: -.02em">Blog'),
    ("m-blog", 'font-size: 18px; font-weight: 500; letter-spacing: -.02em">Blog'),
    ("robotics-supply", 'width: 7px; height: 7px; background: #111; transform: '
                        'rotate(45deg); display: block; flex-shrink: 0"></span>'
                        'Robotics supply chain Infra'),
    ("m-robotics-supply", 'width: 6px; height: 6px; background: #111; transform: '
                          'rotate(45deg); display: block; flex-shrink: 0"></span>'
                          'Robotics supply chain Infra'),
]

HEADER_NAV_DROP = [
    '<a href="#insights" sc-camel-on-click="{{ navInsights }}" '
    'style="color: inherit">Insights</a>',
    '<a href="/team" style="color: inherit">About</a>',
]


def fail(msg):
    print(f"  ! {msg}", file=sys.stderr)
    return 1


def sub_row(label):
    links = []
    for text, href, handler in SUB.get(label, []):
        on = f' sc-camel-on-click="{{{{ {handler} }}}}"' if handler else ""
        links.append(
            f'<a href="{href}"{on} style="color: #55554F; '
            f'font-size: {SUB_FONT}; letter-spacing: -.01em">{text}</a>')
    if not links:
        return ""
    return ('<div style="display: flex; flex-wrap: wrap; gap: 8px 0; '
            f'padding: 0 0 22px">{"".join(links)}</div>')


def main():
    s = PAGE.read_text()
    before = len(s)

    # 1 · Desktop button, in the header slot that is already empty and already
    #     hidden under 760px.
    slot = ('<div data-rw="hdrR" style="display: flex; '
            'justify-content: flex-end; gap: 28px"></div>')
    if slot not in s:
        return fail("header right slot not found")
    s = s.replace(slot, slot.replace("></div>", f">{DESKTOP_BUTTON}</div>"), 1)

    # 2 · Header nav: slightly larger type, and Insights and About drop out
    #     of it — they keep their place in the sheet.
    if HDR_FONT % "13.5px" not in s:
        return fail("header container not found")
    s = s.replace(HDR_FONT % "13.5px", HDR_FONT % "15px", 1)
    for frag in HEADER_NAV_DROP:
        if frag not in s:
            return fail(f"header nav entry not found: {frag[:48]}…")
        s = s.replace(frag, "", 1)

    # 3 · Click-time id resolution, and pillar kept in step with mp.
    if OLD_MNAV not in s:
        return fail("mnav definition not found")
    s = s.replace(OLD_MNAV, NEW_MNAV, 1)
    if OLD_VALS not in s:
        return fail("renderVals menu entries not found")
    s = s.replace(OLD_VALS, NEW_VALS, 1)

    # 4 · Anchors for the second-level destinations, wide and narrow copies
    #     alike. Each marker locates the block's label; the anchor goes in
    #     front of the row that label sits in. Collected first and applied
    #     back-to-front so earlier insertions do not shift later offsets.
    points = []
    for anchor_id, marker in ANCHORS:
        hits = [m.start() for m in re.finditer(re.escape(marker), s)]
        if len(hits) != 1:
            return fail(f"{anchor_id}: expected 1 match for its marker, got "
                        f"{len(hits)}")
        row = s.rfind("<div", 0, hits[0])
        if row < 0:
            return fail(f"{anchor_id}: no row element before the label")
        points.append((row, anchor_id))
    for row, anchor_id in sorted(points, reverse=True):
        s = s[:row] + f'<span id="{anchor_id}"></span>' + s[row:]

    # 5 · Second level under each first-level row.
    start = s.find('data-rw="msheet"')
    nav_start = s.find('<nav style="display: flex; flex-direction: column">', start)
    nav_end = s.find("</nav>", nav_start)
    if min(start, nav_start, nav_end) < 0:
        return fail("menu sheet nav not found")

    added = []

    def wrap(m):
        label = m.group("label")
        sub = sub_row(label)
        if not sub:
            return m.group(0)
        added.append(label)
        style = m.group("style")
        wrapper_border = "border-top: 1px solid #E6E6E2"
        if "border-bottom" in style:
            wrapper_border += "; border-bottom: 1px solid #E6E6E2"
        row_style = (style
                     .replace("padding: 22px 0", "padding: 22px 0 10px")
                     .replace("; border-top: 1px solid #E6E6E2", "")
                     .replace("; border-bottom: 1px solid #E6E6E2", ""))
        row = (f'<a href="{L1_HREF.get(label, m.group("href"))}"'
               f'{m.group("attrs")}style="{row_style}"><span>{label}</span>'
               f'<span style="{m.group("numstyle")}">{m.group("num")}</span></a>')
        return f'<div style="{wrapper_border}">{row}{sub}</div>'

    new_nav = ROW.sub(wrap, s[nav_start:nav_end])
    if len(added) != len(SUB):
        return fail(f"expected {len(SUB)} rows, rewrote {len(added)}: {added}")
    s = s[:nav_start] + new_nav + s[nav_end:]

    # 6 · Sheet gutters above 760px, and the hover colour.
    css_anchor = ('[data-rw="m"], [data-rw="mbtn"], [data-rw="msheet"] '
                  '{ display: none; }')
    if css_anchor not in s:
        return fail("base rw rule not found")
    s = s.replace(css_anchor, css_anchor + SHEET_CSS, 1)

    PAGE.write_text(s)
    print(f"patched {PAGE.name}: {before} -> {len(s)} bytes")
    print("  second level:", "; ".join(
        f"{k} → {', '.join(t for t, _, _ in v)}" for k, v in SUB.items()))
    print("  header nav: Insights and About removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
