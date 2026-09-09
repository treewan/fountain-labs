#!/usr/bin/env python3
"""Turn the design tool's self-contained HTML exports into plain static pages.

Each exported page ships as three JSON script tags instead of markup:

    <script type="__bundler/manifest">   {uuid: {mime, compressed, data}}
    <script type="__bundler/template">   "<!DOCTYPE html>… src=\"<uuid>\" …"
    <script type="__bundler/page_order"> [uuid, …]   (nested page bundles)

plus a bootstrap that, on DOMContentLoaded, base64-decodes every asset into a
blob: URL, substitutes the uuids into the template and replaces the document.
Until that finishes there is nothing to paint, so the bootstrap covers the
viewport with a brand-blue splash — visible on every first visit to a page.

This script does the same work ahead of time: assets become real files named by
content hash (so the copy of a font that ships inside all eight pages is stored
and cached once), uuid references become paths, and each page becomes the plain
HTML document its template already describes. No bootstrap, no splash, and the
browser can cache assets across navigations.

Usage:  python3 tools/unbundle.py [--dry-run] [--assets-dir _assets] public/*.html
"""

import argparse
import base64
import hashlib
import json
import pathlib
import re
import sys
import zlib

TAG = re.compile(
    r'<script type="__bundler/(manifest|template|page_order)">(.*?)</script>',
    re.S,
)

# Extension per mime; anything unlisted keeps .bin and still works, since the
# reference is rewritten to whatever name we choose.
EXT = {
    "font/woff2": "woff2",
    "font/woff": "woff",
    "font/ttf": "ttf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "text/javascript": "js",
    "application/javascript": "js",
    "text/css": "css",
    "application/json": "json",
    "text/html": "html",
}

# Assets whose bytes may themselves contain uuid references to other assets.
TEXTUAL = {"image/svg+xml", "text/javascript", "application/javascript",
           "text/css", "application/json", "text/html"}

UUID = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I
)

# A nested page bundle (an iframe whose document ships in the parent's
# manifest) is referenced as a fragment on about:blank rather than as a bare
# uuid, so it has to be rewritten to the emitted file before the generic uuid
# pass turns the fragment into a nonsense "about:blank#/_assets/…".
FRAME = re.compile(r"about:blank#(" + UUID.pattern + ")", re.I)

# Nested bundles nest at most a couple of levels in practice; the cap is a
# guard against a malformed export pointing a page bundle at itself.
MAX_DEPTH = 8


def inflate(raw: bytes) -> bytes:
    """The bootstrap's compressed entries are deflate; try both framings."""
    for wbits in (15, -15, 47):
        try:
            return zlib.decompress(raw, wbits)
        except zlib.error:
            continue
    raise ValueError("entry marked compressed but no deflate framing matched")


def read_bundle(src: str):
    """Parse the three bundle script tags out of a document, if present."""
    found = {m.group(1): m.group(2) for m in TAG.finditer(src)}
    if "manifest" not in found or "template" not in found:
        return None
    return (
        json.loads(found["manifest"]),
        json.loads(found["template"]),
        json.loads(found.get("page_order") or "[]"),
    )


def resolve(manifest, ref, blobs, assets_dir, depth, warn):
    """Emit every asset in one manifest, filling ref: uuid -> served path.

    Binary assets are final the moment they are decoded, so they are hashed
    first. Textual ones can name other assets, so they are substituted once
    their own dependencies are known; a nested page bundle is unbundled in
    turn, its assets landing in the same shared pool.
    """
    pending = {}
    for uuid, entry in manifest.items():
        raw = base64.b64decode(entry["data"])
        if entry.get("compressed"):
            raw = inflate(raw)
        mime = entry.get("mime", "application/octet-stream")

        if mime == "text/html" and depth < MAX_DEPTH:
            text = raw.decode("utf-8", "surrogateescape")
            inner = read_bundle(text)
            if inner:
                warn(f"    nested bundle at depth {depth + 1}: "
                     f"{len(inner[0])} assets")
                text = build(*inner, ref, blobs, assets_dir, depth + 1, warn)
            pending[uuid] = (mime, text.encode("utf-8", "surrogateescape"))
        elif mime in TEXTUAL:
            pending[uuid] = (mime, raw)
        else:
            ref[uuid] = store(raw, mime, assets_dir, blobs)

    for _ in range(MAX_DEPTH):
        progressed = False
        for uuid in list(pending):
            mime, raw = pending[uuid]
            text = raw.decode("utf-8", "surrogateescape")
            if any(u in pending and u != uuid for u in UUID.findall(text)):
                continue
            ref[uuid] = store(
                substitute(text, ref).encode("utf-8", "surrogateescape"),
                mime, assets_dir, blobs)
            del pending[uuid]
            progressed = True
        if not pending or not progressed:
            break

    for uuid, (mime, raw) in pending.items():
        warn(f"    {uuid[:8]}… emitted unsubstituted (reference cycle)")
        ref[uuid] = store(raw, mime, assets_dir, blobs)


def build(manifest, template, page_order, ref, blobs, assets_dir, depth, warn):
    """Unbundle one document and return its plain HTML."""
    resolve(manifest, ref, blobs, assets_dir, depth, warn)
    html = substitute(template, ref)
    left = [u for u in UUID.findall(html) if u in ref]
    if left:
        warn(f"    {len(left)} uuid(s) unresolved after substitution")
    return html


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="+", type=pathlib.Path)
    ap.add_argument("--assets-dir", default="_assets",
                    help="directory under the page's own dir (default: _assets)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pages = [p for p in args.pages if p.suffix == ".html"]
    if not pages:
        print("no .html inputs", file=sys.stderr)
        return 2

    out_root = pages[0].parent / args.assets_dir

    # uuid -> served path, accumulated across every page so identical bytes
    # under different uuids collapse onto one file.
    ref: dict[str, str] = {}
    blobs: dict[str, bytes] = {}      # served path -> bytes
    results = []                      # (page, html, nested_count)
    skipped = []

    print(f"{'page':22}{'before':>10}{'after':>10}{'refs':>7}")
    total_before = total_after = 0
    for page in pages:
        bundle = read_bundle(page.read_text(errors="replace"))
        if bundle is None:
            skipped.append(page)
            continue
        manifest, template, page_order = bundle
        nested = len(page_order)
        before = page.stat().st_size

        html = build(manifest, template, page_order, ref, blobs,
                     args.assets_dir, 0,
                     lambda m, p=page: print(f"  {p.name}:{m}"))

        after = len(html.encode())
        total_before += before
        total_after += after
        note = f"  (+{nested} nested)" if nested else ""
        print(f"{page.name:22}{before/1048576:9.2f}M{after/1024:9.0f}K"
              f"{len(UUID.findall(template)):7}{note}")
        results.append((page, html))

    if not results:
        print("no bundled pages found; nothing to do", file=sys.stderr)
        return 1

    if not args.dry_run:
        for page, html in results:
            page.write_text(html)
        out_root.mkdir(parents=True, exist_ok=True)
        for name, data in blobs.items():
            (pages[0].parent / name).write_bytes(data)

    asset_bytes = sum(len(b) for b in blobs.values())
    print(f"\nHTML   {total_before/1048576:.2f} MB -> {total_after/1048576:.2f} MB")
    print(f"assets {len(blobs)} unique files, {asset_bytes/1048576:.2f} MB"
          f" -> {args.assets_dir}/")
    print(f"total  {total_before/1048576:.2f} MB -> "
          f"{(total_after+asset_bytes)/1048576:.2f} MB")
    for page in skipped:
        print(f"skipped (not a bundle): {page.name}")
    if args.dry_run:
        print("\n--dry-run: nothing written")
    return 0


def store(data: bytes, mime: str, assets_dir: str,
          blobs: dict[str, bytes]) -> str:
    name = (f"{assets_dir}/{hashlib.sha256(data).hexdigest()[:16]}"
            f".{EXT.get(mime, 'bin')}")
    blobs[name] = data
    return "/" + name


def substitute(text: str, ref: dict[str, str]) -> str:
    text = FRAME.sub(
        lambda m: ref.get(m.group(1), m.group(0)), text)
    return UUID.sub(lambda m: ref.get(m.group(0), m.group(0)), text)


if __name__ == "__main__":
    sys.exit(main())
