#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh the "In the news" timeline on the Broadcast RTK project page.

Fetches recent news via Google News RSS (no API key needed) for
ATSC 3.0 / DTV+ (TV 3.0) / Broadcast RTK / EdgeBeam Wireless across the
US, Korea, and Brazil, then rewrites the block between
NEWS-TIMELINE:START / NEWS-TIMELINE:END markers in broadcast-rtk.md.

Queries are NOT fixed: they live in scripts/rtk_news_queries.json
(seeds + learned). With --evolve the script studies the articles it just
fetched (titles, plus best-effort body excerpts) and proposes new
queries — via the `claude` CLI when available, otherwise a frequency
heuristic — which you approve interactively. Learned queries that come
up empty three runs in a row are disabled automatically.

Usage (from the repository root):
    python scripts/fetch_rtk_news.py                  # fetch & update the page
    python scripts/fetch_rtk_news.py --dry-run        # preview only
    python scripts/fetch_rtk_news.py --evolve         # also propose new queries
    python scripts/fetch_rtk_news.py --evolve --yes   # accept proposals w/o asking
    python scripts/fetch_rtk_news.py --evolve --no-llm  # heuristic only
    python scripts/fetch_rtk_news.py --since 2026-06-01 --limit 50

Then review `git diff broadcast-rtk.md`, prune anything irrelevant, and
commit.
"""

import argparse
import email.utils
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PAGE = SCRIPT_DIR.parent / "broadcast-rtk.md"
QUERIES_FILE = SCRIPT_DIR / "rtk_news_queries.json"
MARK_START = "<!-- NEWS-TIMELINE:START -->"
MARK_END = "<!-- NEWS-TIMELINE:END -->"
USER_AGENT = "Mozilla/5.0 (compatible; rtk-news-fetcher/2.0)"

REGION_LOCALE = {
    "US": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
    "KR": {"hl": "ko", "gl": "KR", "ceid": "KR:ko"},
    "BR": {"hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"},
}

SEED_QUERIES = [
    {"region": "US", "q": '"ATSC 3.0" OR "NextGen TV"'},
    {"region": "US", "q": '"EdgeBeam"'},
    {"region": "US", "q": '"Broadcast RTK" OR "broadcast positioning system"'},
    # KR: unquoted — quoted ORs return stale results on the KR RSS endpoint
    {"region": "KR", "q": "ATSC 3.0"},
    {"region": "KR", "q": "정밀측위 방송 OR RTK OR eGPS"},
    {"region": "BR", "q": '"TV 3.0" OR "DTV+"'},
]

# Drop items whose title matches any of these (case-insensitive) patterns.
TITLE_BLOCKLIST = [
    r"\bhoroscope\b",
]

# Relevance scoring — (weight, regex on the title). Items below --min-score
# are dropped; when more than --limit remain, the highest-scored survive.
RELEVANCE_PATTERNS = [
    (3, r"broadcast\s*rtk|egps|broadcast positioning|\bbps\b|merkhet"),
    (2, r"atsc\s*3\.?0|nextgen\s*tv|tv\s*3\.0|dtv\+|edgebeam"),
    (2, r"측위|방송망|지상파"),
    (1, r"positioning|gnss|\bgps\b|\bpnt\b|timing|broadcast|방송|측량|위치정보"),
]

MAX_LEARNED_ACTIVE = 8      # cap on enabled learned queries
DISABLE_AFTER_MISSES = 3    # empty runs before a learned query is disabled
BODY_SAMPLE = 8             # articles to try fetching bodies from in --evolve
BODY_CHARS = 1200           # excerpt length per article

# ---------------------------------------------------------------------------
# Query store
# ---------------------------------------------------------------------------


def load_store() -> dict:
    if QUERIES_FILE.exists():
        return json.loads(QUERIES_FILE.read_text(encoding="utf-8"))
    store = {"seeds": SEED_QUERIES, "learned": []}
    save_store(store)
    return store


def save_store(store: dict) -> None:
    QUERIES_FILE.write_text(
        json.dumps(store, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")


def active_queries(store: dict) -> list[dict]:
    out = []
    for q in store["seeds"]:
        out.append({**REGION_LOCALE[q["region"]], **q, "learned": False})
    for q in store["learned"]:
        if q.get("enabled", True):
            out.append({**REGION_LOCALE[q["region"]], **q, "learned": True})
    return out


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------


def http_get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_rss(query: dict) -> list[dict]:
    params = {"q": query["q"], "hl": query["hl"],
              "gl": query["gl"], "ceid": query["ceid"]}
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)
    tree = ET.fromstring(http_get(url))
    items = []
    for it in tree.iter("item"):
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
        if source and title.endswith(" - " + source):
            title = title[: -len(" - " + source)].rstrip()
        items.append({"title": title, "link": link, "date": dt,
                      "source": source, "region": query["region"]})
    return items


def norm_title(title: str) -> str:
    return re.sub(r"[\W_]+", "", title.lower())


def find_claude() -> str | None:
    """Locate the claude CLI: PATH, then editor-bundled binaries."""
    exe = shutil.which("claude")
    if exe:
        return exe
    for base in (Path.home() / ".vscode" / "extensions",
                 Path.home() / ".cursor" / "extensions"):
        if base.exists():
            hits = sorted(base.glob(
                "anthropic.claude-code-*/resources/native-binary/claude.exe"),
                reverse=True)
            if hits:
                return str(hits[0])
    local = Path.home() / ".claude" / "local" / "claude.exe"
    return str(local) if local.exists() else None


def relevance(item: dict) -> int:
    """Keyword-weighted relevance score of an article title."""
    t = item["title"].lower()
    return sum(w for w, pat in RELEVANCE_PATTERNS if re.search(pat, t))


def curate_with_claude(items: list[dict]) -> list[dict]:
    """Ask the claude CLI to drop off-topic items (promos, tangents)."""
    claude = find_claude()
    if not claude or not items:
        return items
    numbered = "\n".join(f'{i}. [{it["region"]}] {it["title"]} ({it["source"]})'
                         for i, it in enumerate(items))
    prompt = (
        "These headlines were collected for a page tracking ATSC 3.0 / "
        "NextGen TV, Brazil TV 3.0 (DTV+), Broadcast RTK / eGPS, BPS "
        "(Broadcast Positioning System), and EdgeBeam Wireless.\n\n"
        f"{numbered}\n\n"
        "List the numbers of items that are NOT meaningfully about these "
        "topics (consumer promos, sweepstakes, tangential mentions). "
        "Respond with ONLY a JSON array of numbers, e.g. [2,7] or []."
    )
    try:
        res = subprocess.run(
            [claude, "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, timeout=180, encoding="utf-8")
        if res.returncode != 0:
            return items
        m = re.search(r"\[[\d,\s]*\]", res.stdout)
        if not m:
            return items
        drop = {int(n) for n in json.loads(m.group(0))}
        kept = [it for i, it in enumerate(items) if i not in drop]
        for i in sorted(drop):
            if i < len(items):
                print(f"  curated out: {items[i]['title'][:70]}")
        return kept
    except Exception:
        return items


def collect(store: dict, since: datetime, max_per_query: int) -> list[dict]:
    seen, out = set(), []
    block = [re.compile(p, re.I) for p in TITLE_BLOCKLIST]
    for query in active_queries(store):
        tag = "learned" if query["learned"] else "seed"
        try:
            items = fetch_rss(query)
        except Exception as exc:
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
        print(f"  {query['region']:2} [{tag}] '{query['q'][:42]}' -> {kept} kept")
        if query["learned"]:
            for lq in store["learned"]:
                if lq["q"] == query["q"] and lq["region"] == query["region"]:
                    lq["misses"] = 0 if kept else lq.get("misses", 0) + 1
                    if lq["misses"] >= DISABLE_AFTER_MISSES:
                        lq["enabled"] = False
                        print(f"    (disabled after {lq['misses']} empty runs)")
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


# ---------------------------------------------------------------------------
# Evolve: learn new queries from what the articles actually say
# ---------------------------------------------------------------------------


def fetch_body_excerpt(gn_link: str) -> str:
    """Best-effort: follow a Google News item to the publisher and grab text."""
    try:
        page = http_get(gn_link, timeout=15).decode("utf-8", "ignore")
        urls = re.findall(r'https?://[^\s"\'<>]+', page)
        target = next((u for u in urls
                       if "google.com" not in u and "gstatic" not in u
                       and "googleusercontent" not in u and len(u) > 25), None)
        if not target:
            return ""
        art = http_get(target, timeout=15).decode("utf-8", "ignore")
        art = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", art)
        text = re.sub(r"(?s)<[^>]+>", " ", art)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        return text[:BODY_CHARS]
    except Exception:
        return ""


def mine_candidates(items: list[dict], covered: str) -> list[tuple[str, str]]:
    """Heuristic fallback: frequent capitalized phrases not already covered.

    Returns (term, region) — region is the majority region of the articles
    the term appeared in.
    """
    freq: dict[str, list[str]] = {}
    pat = re.compile(r"\b([A-Z][A-Za-z0-9&.-]+(?:\s+[A-Z][A-Za-z0-9&.-]+){0,2})\b")
    stop = {"The", "This", "New", "With", "For", "From", "Says", "Win", "TV",
            "US", "FCC", "Congress", "House", "Brasil", "Brazil"}
    for it in items:
        for m in pat.findall(it["title"]):
            if m.split()[0] in stop or len(m) < 5:
                continue
            if m.lower() in covered:
                continue
            freq.setdefault(m, []).append(it["region"])
    ranked = sorted(freq.items(), key=lambda kv: -len(kv[1]))
    out = []
    for term, regions in ranked:
        if len(regions) >= 2:
            out.append((term, max(set(regions), key=regions.count)))
    return out[:5]


def _proposal_prompt(items: list[dict], store: dict,
                     bodies: dict[str, str]) -> str:
    current = [{"region": q["region"], "q": q["q"]} for q in active_queries(store)]
    lines = []
    for it in items:
        line = f'- [{it["region"]}] {it["title"]} ({it["source"]})'
        body = bodies.get(it["link"], "")
        if body:
            line += f'\n  excerpt: {body[:300]}'
        lines.append(line)
    return (
        "You maintain Google News RSS search queries that track news about "
        "ATSC 3.0 / NextGen TV, Brazil TV 3.0 (DTV+), Broadcast RTK / eGPS, "
        "BPS (Broadcast Positioning System), and EdgeBeam Wireless in the US, "
        "Korea (KR), and Brazil (BR).\n\n"
        f"Current queries:\n{json.dumps(current, ensure_ascii=False, indent=1)}\n\n"
        f"Articles fetched this run:\n" + "\n".join(lines) + "\n\n"
        "Based on what these articles actually discuss, propose up to 3 NEW "
        "queries that would catch important related coverage the current "
        "queries would miss — e.g. newly emerged companies, products, "
        "regulators, or programs central to this space. Prefer precise "
        "proper-noun queries over broad topics. Do not duplicate or trivially "
        "rephrase current queries. Korean queries must avoid quoted OR "
        "expressions.\n\n"
        'Respond with ONLY a JSON array: '
        '[{"q": "...", "region": "US|KR|BR", "why": "one short sentence"}] '
        "— return [] if nothing new is warranted."
    )


def propose_with_claude(items: list[dict], store: dict,
                        bodies: dict[str, str]) -> list[dict] | None:
    """Ask the claude CLI to propose new queries. None on any failure."""
    claude = find_claude()
    if not claude:
        return None
    prompt = _proposal_prompt(items, store, bodies)
    try:
        res = subprocess.run(
            [claude, "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, timeout=180, encoding="utf-8")
        if res.returncode != 0:
            return None
        m = re.search(r"\[.*\]", res.stdout, re.S)
        if not m:
            return None
        proposals = json.loads(m.group(0))
        return [p for p in proposals
                if isinstance(p, dict) and p.get("q")
                and p.get("region") in REGION_LOCALE]
    except Exception:
        return None


def propose_with_api(items: list[dict], store: dict,
                     bodies: dict[str, str]) -> list[dict] | None:
    """Same as propose_with_claude, but over the Anthropic API.

    Used where the claude CLI isn't installed (CI). None on any failure.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ImportError:
        return None

    schema = {
        "type": "object",
        "properties": {
            "queries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "q": {"type": "string"},
                        "region": {"type": "string",
                                   "enum": list(REGION_LOCALE)},
                        "why": {"type": "string"},
                    },
                    "required": ["q", "region", "why"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["queries"],
        "additionalProperties": False,
    }
    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2000,
            output_config={"format": {"type": "json_schema", "schema": schema},
                           "effort": "low"},
            messages=[{"role": "user",
                       "content": _proposal_prompt(items, store, bodies)}],
        )
        text = next(b.text for b in resp.content if b.type == "text")
        return json.loads(text)["queries"]
    except Exception as exc:
        print(f"  API proposal failed: {exc}", file=sys.stderr)
        return None


def evolve(store: dict, items: list[dict], use_llm: bool, auto_yes: bool) -> None:
    print("\nEvolving queries from fetched articles ...")
    enabled = [q for q in store["learned"] if q.get("enabled", True)]
    if len(enabled) >= MAX_LEARNED_ACTIVE:
        print(f"  learned-query cap reached ({MAX_LEARNED_ACTIVE}); "
              "disable some in rtk_news_queries.json first")
        return

    proposals = None
    if use_llm:
        bodies = {}
        for it in items[:BODY_SAMPLE]:
            body = fetch_body_excerpt(it["link"])
            if body:
                bodies[it["link"]] = body
        print(f"  body excerpts fetched: {len(bodies)}/{min(BODY_SAMPLE, len(items))}")
        proposals = propose_with_claude(items, store, bodies)
        if proposals is None:
            print("  claude CLI unavailable/failed -> trying the Anthropic API")
            proposals = propose_with_api(items, store, bodies)
        if proposals is None:
            print("  no LLM available -> falling back to heuristic")

    if proposals is None:
        covered = " ".join(q["q"].lower() for q in active_queries(store))
        proposals = [{"q": f'"{t}"', "region": r,
                      "why": "frequent new entity in fetched titles"}
                     for t, r in mine_candidates(items, covered)][:3]

    if not proposals:
        print("  no new queries proposed")
        return

    existing = {(q["region"], q["q"]) for q in store["seeds"]}
    existing |= {(q["region"], q["q"]) for q in store["learned"]}
    today = datetime.now().strftime("%Y-%m-%d")
    for p in proposals:
        key = (p["region"], p["q"])
        if key in existing:
            continue
        print(f'\n  proposal: [{p["region"]}] {p["q"]}\n    why: {p.get("why", "-")}')
        if auto_yes:
            ok = True
        else:
            try:
                ok = input("  add this query? [y/N] ").strip().lower() == "y"
            except EOFError:
                ok = False
        if ok:
            store["learned"].append(
                {"q": p["q"], "region": p["region"], "why": p.get("why", ""),
                 "added": today, "misses": 0, "enabled": True})
            print("    added (takes effect next run)")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render(items: list[dict], since: datetime) -> str:
    """Render as the site's dot-and-line timeline (.timeline / .tl-item)."""
    stamp = datetime.now().strftime("%Y-%m-%d")
    lines = [
        MARK_START,
        f'<p class="page-subtitle">ATSC 3.0 · DTV+ (TV 3.0) · Broadcast RTK · '
        f'EdgeBeam — auto-collected news since {since.strftime("%B %d, %Y")} '
        f'(last updated {stamp}).</p>',
        '<ol class="timeline">',
    ]
    for it in items:
        title = html.escape(it["title"], quote=False)
        source = html.escape(it["source"], quote=False)
        meta = f'{source} · {it["region"]}' if source else it["region"]
        lines.append(
            '  <li class="tl-item">'
            f'<a class="tl-title" href="{it["link"]}" target="_blank" '
            f'rel="noopener">{title}</a> <span class="tl-cat">{meta}</span>'
            f'<div class="tl-date">{it["date"].strftime("%Y.%m.%d")}</div></li>'
        )
    lines += ["</ol>", MARK_END]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", default="2026-06-01",
                    help="earliest article date, YYYY-MM-DD (default 2026-06-01)")
    ap.add_argument("--max-per-query", type=int, default=12,
                    help="cap per query after date filter (default 12)")
    ap.add_argument("--limit", type=int, default=50,
                    help="cap total items rendered (default 50)")
    ap.add_argument("--min-score", type=int, default=1,
                    help="drop articles below this relevance score (default 1)")
    ap.add_argument("--curate", action="store_true",
                    help="ask the claude CLI to drop off-topic items")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the generated block; do not modify the page")
    ap.add_argument("--evolve", action="store_true",
                    help="propose new queries from fetched article content")
    ap.add_argument("--no-llm", action="store_true",
                    help="with --evolve: skip claude CLI, heuristic only")
    ap.add_argument("--yes", action="store_true",
                    help="with --evolve: accept proposals without asking")
    args = ap.parse_args()

    since = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
    store = load_store()

    print(f"Fetching news since {args.since} ...")
    items = collect(store, since, args.max_per_query)

    # Relevance: drop low scorers; if still over the cap, keep highest-scored.
    scored = [(relevance(it), it) for it in items]
    dropped = [it for s, it in scored if s < args.min_score]
    for it in dropped[:10]:
        print(f"  low relevance (<{args.min_score}): {it['title'][:70]}")
    items = [it for s, it in scored if s >= args.min_score]
    if len(items) > args.limit:
        items.sort(key=lambda it: (relevance(it), it["date"]), reverse=True)
        print(f"  over limit: keeping top {args.limit} of {len(items)} by relevance")
        items = items[: args.limit]
        items.sort(key=lambda it: it["date"], reverse=True)
    if args.curate:
        items = curate_with_claude(items)
    print(f"Total: {len(items)} articles"
          + (f" ({len(dropped)} dropped as low-relevance)" if dropped else ""))

    if args.evolve:
        evolve(store, items, use_llm=not args.no_llm, auto_yes=args.yes)
    save_store(store)

    blockText = render(items, since)
    if args.dry_run:
        print("\n" + blockText)
        return 0

    text = PAGE.read_text(encoding="utf-8")
    if MARK_START not in text or MARK_END not in text:
        print(f"error: markers not found in {PAGE}", file=sys.stderr)
        return 1
    pattern = re.compile(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), re.S)
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
