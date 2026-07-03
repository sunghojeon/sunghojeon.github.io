#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh the "In the news" timeline on the Broadcast RTK project page.

Fetches recent news via Google News RSS (no API key needed) for
ATSC 3.0 / DTV+ (TV 3.0) / Broadcast RTK / EdgeBeam Wireless across
the US, Korea, and Brazil, then rewrites the block between
NEWS-TIMELINE:START / NEWS-TIMELINE:END markers in broadcast-rtk.md.

Usage (from the repository root):
    python scripts/fetch_rtk_news.py                 # fetch & update the page
    python scripts/fetch_rtk_news.py --dry-run       # preview only, no write
    python scripts/fetch_rtk_news.py --since 2026-06-01 --limit 40

Then review `git diff broadcast-rtk.md`, prune anything irrelevant,
and commit.
"""

import argparse
import email.utils
import html
import io
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration — edit queries freely. `q` uses Google News search syntax.
# ---------------------------------------------------------------------------

QUERIES = [
    # United States
    {"region": "US", "q": '"ATSC 3.0" OR "NextGen TV"',
     "hl": "en-US", "gl": "US", "ceid": "US:en"},
    {"region": "US", "q": '"EdgeBeam"',
     "hl": "en-US", "gl": "US", "ceid": "US:en"},
    {"region": "US", "q": '"Broadcast RTK" OR "broadcast positioning system"',
     "hl": "en-US", "gl": "US", "ceid": "US:en"},
    # Korea (unquoted queries — quoted ORs return stale results on KR RSS)
    {"region": "KR", "q": 'ATSC 3.0',
     "hl": "ko", "gl": "KR", "ceid": "KR:ko"},
    {"region": "KR", "q": '정밀측위 방송 OR RTK OR eGPS',
     "hl": "ko", "gl": "KR", "ceid": "KR:ko"},
    # Brazil
    {"region": "BR", "q": '"TV 3.0" OR "DTV+"',
     "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"},
]

# Drop items whose title matches any of these (case-insensitive) patterns.
TITLE_BLOCKLIST = [
    r"\bhoroscope\b",
]

PAGE = Path(__file__).resolve().parent.parent / "broadcast-rtk.md"
MARK_START = "<!-- NEWS-TIMELINE:START -->"
MARK_END = "<!-- NEWS-TIMELINE:END -->"
USER_AGENT = "Mozilla/5.0 (compatible; rtk-news-fetcher/1.0)"

# ---------------------------------------------------------------------------


def fetch_rss(query: dict) -> list[dict]:
    """Fetch one Google News RSS query -> list of raw items."""
    params = {"q": query["q"], "hl": query["hl"],
              "gl": query["gl"], "ceid": query["ceid"]}
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        tree = ET.parse(resp)

    items = []
    for it in tree.getroot().iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        src = it.find("source")
        source = (src.text or "").strip() if src is not None else ""
        if not title or not link:
            continue
        try:
            dt = email.utils.parsedate_to_datetime(pub)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        # Google News titles usually end with " - Source"; strip the suffix.
        if source and title.endswith(" - " + source):
            title = title[: -len(" - " + source)].rstrip()
        items.append({"title": title, "link": link, "date": dt,
                      "source": source, "region": query["region"]})
    return items


def norm_title(title: str) -> str:
    """Normalization key for de-duplication across queries/regions."""
    return re.sub(r"[\W_]+", "", title.lower())


def collect(since: datetime, max_per_query: int) -> list[dict]:
    seen, out = set(), []
    block = [re.compile(p, re.I) for p in TITLE_BLOCKLIST]
    for query in QUERIES:
        try:
            items = fetch_rss(query)
        except Exception as exc:  # network hiccup: keep going, report
            print(f"  ! {query['region']} '{query['q']}': {exc}", file=sys.stderr)
            continue
        items.sort(key=lambda x: x["date"], reverse=True)
        kept = 0
        for item in items:
            if item["date"] < since or kept >= max_per_query:
                continue
            if any(p.search(item["title"]) for p in block):
                continue
            key = norm_title(item["title"])
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
            kept += 1
        print(f"  {query['region']:2} '{query['q'][:44]}...' -> {kept} kept")
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


def render(items: list[dict], since: datetime) -> str:
    """Render items as an .svc timeline block (site component)."""
    stamp = datetime.now().strftime("%Y-%m-%d")
    lines = [
        MARK_START,
        f'<p class="page-subtitle">ATSC 3.0 · DTV+ (TV 3.0) · Broadcast RTK · '
        f'EdgeBeam — auto-collected news since {since.strftime("%B %d, %Y")} '
        f'(last updated {stamp}).</p>',
        '<div class="svc">',
    ]
    for it in items:
        title = html.escape(it["title"], quote=False)
        source = html.escape(it["source"], quote=False)
        meta = f'{source} · {it["region"]}' if source else it["region"]
        lines.append(
            '  <div class="svc-item"><span class="svc-label">'
            f'<a href="{it["link"]}" target="_blank" rel="noopener">{title}</a> '
            f'<span class="ko-gloss">{meta}</span></span>'
            f'<span class="svc-date">{it["date"].strftime("%Y.%m.%d")}</span></div>'
        )
    lines += ["</div>", MARK_END]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", default="2026-06-01",
                    help="earliest article date, YYYY-MM-DD (default 2026-06-01)")
    ap.add_argument("--max-per-query", type=int, default=12,
                    help="cap per query after date filter (default 12)")
    ap.add_argument("--limit", type=int, default=50,
                    help="cap total items rendered (default 50)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the generated block; do not modify the page")
    args = ap.parse_args()

    since = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)

    print(f"Fetching news since {args.since} ...")
    items = collect(since, args.max_per_query)[: args.limit]
    print(f"Total: {len(items)} articles")

    blockText = render(items, since)

    if args.dry_run:
        print("\n" + blockText)
        return 0

    text = PAGE.read_text(encoding="utf-8")
    if MARK_START not in text or MARK_END not in text:
        print(f"error: markers not found in {PAGE}", file=sys.stderr)
        return 1
    pattern = re.compile(re.escape(MARK_START) + r".*?" + re.escape(MARK_END),
                         re.S)
    PAGE.write_text(pattern.sub(lambda _: blockText, text, count=1),
                    encoding="utf-8", newline="\n")
    print(f"Updated {PAGE}")
    print("Review with: git diff broadcast-rtk.md  (prune, then commit)")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
