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
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PAGE = SCRIPT_DIR.parent / "news.md"
QUERIES_FILE = SCRIPT_DIR / "rtk_news_queries.json"
# Written by news_notify.py: reported titles, Korean summaries, vetted-out junk.
LEDGER_FILE = SCRIPT_DIR / "news_seen.json"
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
# MBC RTK ecosystem partners are whitelisted by name: their headlines usually
# lack positioning words (긴트 → 스마트팜/자율주행), so without an entry here a
# partner query fetches articles that this filter then throws away.
RELEVANCE_PATTERNS = [
    (3, r"broadcast\s*rtk|egps|broadcast positioning|\bbps\b|merkhet"),
    (2, r"atsc\s*3\.?0|nextgen\s*tv|tv\s*3\.0|dtv\+|edgebeam"),
    (2, r"측위|방송망|지상파"),
    (2, r"긴트|\bgint\b|씨너렉스|지알엠"),
    (2, r"pearl\s*tv|zinwell|\btolka\b|cerinet"),
    (2, r"\bbmsb\b|\betri\b|한국전자통신연구원"),
    (1, r"positioning|gnss|\bgps\b|\bpnt\b|timing|broadcast|방송|측량|위치정보"),
]

MAX_LEARNED_ACTIVE = 12     # cap on enabled learned queries
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


def fetch_feed(feed: dict) -> list[dict]:
    """Fetch an outlet's own RSS — for Korean trade press (방송기술저널, 더비즈,
    …) that Google News doesn't index, so no search query can surface them."""
    tree = ET.fromstring(http_get(feed["url"]))
    items = []
    for it in tree.iter("item"):
        title = html.unescape((it.findtext("title") or "").strip())
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate")
               or it.findtext("{http://purl.org/dc/elements/1.1/}date")
               or "").strip()
        if not title or not link:
            continue
        dt = None
        try:
            dt = email.utils.parsedate_to_datetime(pub)
        except Exception:
            try:  # ndsoft CMS style: "2026-07-03 09:12:34"
                dt = datetime.fromisoformat(pub)
            except Exception:
                continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone(
                timedelta(hours=feed.get("tz_hours", 9))))
        items.append({"title": title, "link": link, "date": dt,
                      "source": feed.get("source", ""),
                      "region": feed.get("region", "KR")})
    return items


def fetch_watch_page(w: dict) -> list[dict]:
    """Scrape an org notice board (KIBME, TTA, …) that has no RSS.

    Every anchor text long enough to be a post title becomes a candidate;
    the relevance pre-filter in collect() keeps only on-topic announcements
    (ATSC 3.0 sessions, UHD workshops), not 휴무 안내 and the like. Dates are
    discovery dates — boards rarely expose machine-readable ones — and are
    pinned to first-seen by the ledger on later runs.
    """
    page = http_get(w["url"], timeout=20).decode("utf-8", "ignore")
    items, dedup = [], set()
    for href, text in re.findall(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page, re.S):
        t = html.unescape(re.sub(r"<[^>]+>", " ", text))
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 12 or t in dedup or href.startswith(("javascript", "#")):
            continue
        dedup.add(t)
        items.append({"title": t,
                      "link": urllib.parse.urljoin(w["url"], href),
                      "date": datetime.now(timezone.utc),
                      "source": w.get("source", ""),
                      "region": w.get("region", "KR"),
                      "_watch": True})
    return items


def fetch_naver(query: dict) -> list[dict]:
    """Naver News search — reaches the Korean outlets Google News misses.

    Active only when NAVER_CLIENT_ID / NAVER_CLIENT_SECRET are set (free keys
    from developers.naver.com). Returns [] otherwise.
    """
    cid = os.environ.get("NAVER_CLIENT_ID")
    secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not cid or not secret:
        return []
    url = ("https://openapi.naver.com/v1/search/news.json?"
           + urllib.parse.urlencode({"query": query["q"], "display": 30,
                                     "sort": "date"}))
    req = urllib.request.Request(url, headers={
        "X-Naver-Client-Id": cid, "X-Naver-Client-Secret": secret})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    items = []
    for it in data.get("items", []):
        title = html.unescape(re.sub(r"</?b>", "", it.get("title", ""))).strip()
        link = it.get("originallink") or it.get("link", "")
        try:
            dt = email.utils.parsedate_to_datetime(it.get("pubDate", ""))
        except Exception:
            continue
        if not title or not link:
            continue
        source = urllib.parse.urlparse(link).netloc.removeprefix("www.")
        items.append({"title": title, "link": link, "date": dt,
                      "source": source, "region": "KR"})
    return items


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
    score = sum(w for w, pat in RELEVANCE_PATTERNS if re.search(pat, t))
    # Watch-page notices already passed a curated source + the pre-filter;
    # don't let them lose the over-limit ranking to score-2 wire copy.
    if item.get("_watch") and score >= 1:
        score += 2
    return score


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

    def keep_items(items: list[dict], cap: int, pre_relevance: bool = False) -> int:
        items.sort(key=lambda x: x["date"], reverse=True)
        kept = 0
        for item in items:
            if item["date"] < since or kept >= cap:
                continue
            if any(p.search(item["title"]) for p in block):
                continue
            if pre_relevance and relevance(item) < 1:
                continue
            key = norm_title(item["title"])
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
            kept += 1
        return kept

    for query in active_queries(store):
        tag = "learned" if query["learned"] else "seed"
        try:
            items = fetch_rss(query)
        except Exception as exc:
            print(f"  ! {query['region']} '{query['q']}': {exc}", file=sys.stderr)
            items = []
        # Google News barely indexes the Korean trade press — for KR queries,
        # also ask Naver News (active when NAVER_CLIENT_ID/SECRET are set).
        if query["region"] == "KR":
            try:
                items += fetch_naver(query)
            except Exception as exc:
                print(f"  ! naver '{query['q']}': {exc}", file=sys.stderr)
        kept = keep_items(items, max_per_query)
        print(f"  {query['region']:2} [{tag}] '{query['q'][:42]}' -> {kept} kept")
        if query["learned"]:
            for lq in store["learned"]:
                if lq["q"] == query["q"] and lq["region"] == query["region"]:
                    lq["misses"] = 0 if kept else lq.get("misses", 0) + 1
                    # pinned = user-designated partner/ecosystem keyword: keep
                    # polling even through dry spells (news may be sporadic).
                    if (lq["misses"] >= DISABLE_AFTER_MISSES
                            and not lq.get("pinned")):
                        lq["enabled"] = False
                        print(f"    (disabled after {lq['misses']} empty runs)")

    # Outlet feeds: whole-site RSS from unindexed trade press. Everything
    # off-topic is pre-filtered by the relevance patterns (the feeds carry the
    # outlet's full output, not a search result).
    for feed in store.get("feeds", []):
        if not feed.get("enabled", True):
            continue
        try:
            items = fetch_feed(feed)
        except Exception as exc:
            print(f"  ! feed '{feed.get('source', feed['url'])}': {exc}",
                  file=sys.stderr)
            continue
        kept = keep_items(items, max_per_query, pre_relevance=True)
        print(f"  {feed.get('region', 'KR'):2} [feed] "
              f"'{feed.get('source', feed['url'])[:42]}' -> {kept} kept")

    # Org notice boards (no RSS): announcements and events. Relevance
    # pre-filter is what keeps this from swallowing whole homepages.
    for w in store.get("watch_pages", []):
        if not w.get("enabled", True):
            continue
        try:
            items = fetch_watch_page(w)
        except Exception as exc:
            print(f"  ! watch '{w.get('source', w['url'])}': {exc}",
                  file=sys.stderr)
            continue
        kept = keep_items(items, max_per_query, pre_relevance=True)
        print(f"  {w.get('region', 'KR'):2} [board] "
              f"'{w.get('source', w['url'])[:42]}' -> {kept} kept")

    out.sort(key=lambda x: x["date"], reverse=True)
    return out


# ---------------------------------------------------------------------------
# Evolve: learn new queries from what the articles actually say
# ---------------------------------------------------------------------------


_GN_URL_CACHE: dict[str, str | None] = {}


def resolve_google_news(link: str) -> str | None:
    """news.google.com/rss/articles/<token> -> the publisher's article URL.

    Google encrypts the token, so the only reliable route is its own
    batchexecute endpoint: read a signature + timestamp off the article page,
    then ask DotsSplashUi to expand the token. Returns None on any failure.
    """
    if link in _GN_URL_CACHE:
        return _GN_URL_CACHE[link]
    result = None
    try:
        m = re.search(r"/articles/([^?]+)", link)
        token = m.group(1)
        page = http_get(link, timeout=15).decode("utf-8", "ignore")
        sig = re.search(r'data-n-a-sg="([^"]+)"', page).group(1)
        ts = re.search(r'data-n-a-ts="([^"]+)"', page).group(1)
        inner = json.dumps([
            "garturlreq",
            [["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1,
              None, None, None, None, None, 0, 1], "X", "X", 1, [1, 1, 1],
             1, 1, None, 0, 0, None, 0],
            token, int(ts), sig,
        ])
        payload = urllib.parse.urlencode({
            "f.req": json.dumps([[["Fbv4je", inner, None, "generic"]]])
        }).encode()
        req = urllib.request.Request(
            "https://news.google.com/_/DotsSplashUi/data/batchexecute",
            data=payload,
            headers={"User-Agent": USER_AGENT,
                     "Content-Type":
                         "application/x-www-form-urlencoded;charset=UTF-8"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", "ignore")
        chunk = json.loads(body.split("\n\n", 1)[1])  # strip )]}' preamble
        result = json.loads(chunk[0][2])[1]
    except Exception:
        result = None
    _GN_URL_CACHE[link] = result
    return result

_PUB_DATE_RES = [
    re.compile(r'property=["\']article:published_time["\'][^>]*?'
               r'content=["\']([^"\']+)', re.I),
    re.compile(r'content=["\']([^"\']+)["\'][^>]*?'
               r'property=["\']article:published_time', re.I),
    re.compile(r'"datePublished"\s*:\s*"([^"]+)"'),
    re.compile(r'<time[^>]+datetime=["\']([^"\']+)', re.I),
]


def _parse_pub_date(raw: str):
    raw = raw.strip()[:19].replace("/", "-").replace(".", "-")
    try:
        return datetime.fromisoformat(raw).replace(tzinfo=None)
    except Exception:
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d")
        except Exception:
            return None


def fetch_article_info(link: str) -> dict:
    """Best-effort {text, date, domain} for an article.

    Google News links are followed to the publisher; direct links (Naver /
    outlet RSS) are read as-is. `date` is the page's own publication date —
    Google News sometimes re-serves years-old archive pages with a fresh
    date, and the page metadata is how we catch that.
    """
    info = {"text": "", "date": None, "domain": ""}
    try:
        target = link
        if "news.google.com" in link:
            target = resolve_google_news(link)
            if not target:
                return info
        art = http_get(target, timeout=15).decode("utf-8", "ignore")
        info["domain"] = urllib.parse.urlparse(target).netloc.removeprefix("www.")

        for pat in _PUB_DATE_RES:
            m = pat.search(art)
            if m:
                info["date"] = _parse_pub_date(m.group(1))
                if info["date"]:
                    break

        art = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>",
                     " ", art)
        text = re.sub(r"(?s)<[^>]+>", " ", art)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        info["text"] = text[:BODY_CHARS]

        if info["date"] is None:  # visible byline date, e.g. "2015/06/18"
            m = re.search(r"\b(20\d{2})[./-](\d{1,2})[./-](\d{1,2})\b",
                          text[:2500])
            if m:
                info["date"] = _parse_pub_date(
                    f"{m.group(1)}-{m.group(2):0>2}-{m.group(3):0>2}")
    except Exception:
        pass
    return info


def fetch_body_excerpt(link: str) -> str:
    """Back-compat wrapper: just the article text."""
    return fetch_article_info(link)["text"]


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
        "regulators, or programs central to this space. Pay special "
        "attention to article tags/hashtags visible in the excerpts and to "
        "entities that recur across several articles — those are the "
        "strongest signals. Prefer precise proper-noun queries over broad "
        "topics. Do not duplicate or trivially rephrase current queries. "
        "Korean queries must avoid quoted OR expressions.\n\n"
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


def load_ledger() -> dict:
    """news_notify.py's ledger: seen titles, Korean summaries, vetted-out junk."""
    if LEDGER_FILE.exists():
        try:
            return json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def render(items: list[dict], since: datetime, ledger: dict | None = None) -> str:
    """Render as the site's dot-and-line timeline (.timeline / .tl-item).

    Articles that the notifier vetted out (photo-library stubs, giveaways,
    off-topic name collisions) are excluded, and its one-line Korean summaries
    are carried onto the page as .tl-note.
    """
    ledger = ledger or {}
    summaries = ledger.get("summaries", {})
    dropped = set(ledger.get("dropped", []))
    members = ledger.get("related_members", {})
    related = ledger.get("related", {})
    stamp = datetime.now().strftime("%Y-%m-%d")
    lines = [
        MARK_START,
        f'<p class="page-subtitle">ATSC 3.0 · DTV+ (TV 3.0) · Broadcast RTK · '
        f'EdgeBeam · MBC RTK ecosystem — auto-collected news since '
        f'{since.strftime("%B %d, %Y")} (last updated {stamp}).</p>',
        '<ol class="timeline">',
    ]
    for it in items:
        key = norm_title(it["title"])
        if key in dropped or key in members:
            continue
        title = html.escape(it["title"], quote=False)
        source = html.escape(it["source"], quote=False)
        meta = f'{source} · {it["region"]}' if source else it["region"]
        note = summaries.get(key, "")
        note_html = (f'<div class="tl-note">{html.escape(note, quote=False)}'
                     f'</div>') if note else ""
        rel_html = ""
        if related.get(key):
            rows = "<br>".join(
                f'· <a href="{html.escape(m["link"])}" target="_blank" '
                f'rel="noopener">{html.escape(m["title"], quote=False)}</a> '
                f'({html.escape(m["source"].split(" · ")[0], quote=False)})'
                for m in related[key])
            rel_html = (f'<div class="tl-related">관련기사 '
                        f'{len(related[key])}<br>{rows}</div>')
        lines.append(
            '  <li class="tl-item">'
            f'<a class="tl-title" href="{it["link"]}" target="_blank" '
            f'rel="noopener">{title}</a> <span class="tl-cat">{meta}</span>'
            f'{note_html}{rel_html}'
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

    ledger = load_ledger()
    # Watch-page items carry discovery dates; pin them to first-seen so they
    # don't drift forward on every run.
    known = dict(ledger.get("reps", {}))
    for rels in ledger.get("related", {}).values():
        for m in rels:
            known.setdefault(norm_title(m["title"]), m)
    for it in items:
        if it.get("_watch"):
            meta = known.get(norm_title(it["title"]))
            if meta:
                try:
                    it["date"] = datetime.strptime(
                        meta["date"], "%Y.%m.%d").replace(tzinfo=timezone.utc)
                except Exception:
                    pass

    blockText = render(items, since, ledger)
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
