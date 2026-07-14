#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report newly-collected Broadcast RTK / ATSC 3.0 news to Telegram.

Reads the NEWS-TIMELINE block that fetch_rtk_news.py just wrote, works out
which articles are genuinely new, reads each one's body, has Claude vet it,
group duplicate coverage, and write a one-line Korean summary, then posts the
digest and carries the results onto the page itself.

Grouping: wire-copy coverage (the same announcement run by six outlets) is
folded into one REPRESENTATIVE article; the other outlets appear as a
small-print 관련기사 line under it, on the page and in Telegram alike.

Dedup subtleties learned the hard way:

  * Google News mints a DIFFERENT encoded URL for the same article on every
    fetch, and sometimes re-dates it. Dedup is by normalized title, never by
    link, against a persistent ledger (scripts/news_seen.json).
  * A run without any LLM (no ANTHROPIC_API_KEY, no claude CLI — e.g. CI
    before the secret is registered) reports articles unvetted. Those are
    re-vetted automatically on the next run that does have an LLM
    (self-heal), so summaries and grouping catch up on their own.

Usage (from the repository root):
    python scripts/news_notify.py OLD_PAGE NEW_PAGE

Environment:
    ANTHROPIC_API_KEY    vetting/summaries via the API (falls back to the
                         claude CLI; skipped when neither is available)
    TELEGRAM_BOT_TOKEN   required to send (dry-run prints to stdout if unset)
    TELEGRAM_CHAT_ID     required to send
    GITHUB_OUTPUT        if set, `changed=true|false` is appended to it

Exits 0 even when Telegram or Claude fail — a broken notification must not
fail the news refresh itself.
"""

import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from datetime import datetime  # noqa: E402

from fetch_rtk_news import (  # noqa: E402
    QUERIES_FILE,
    fetch_article_info,
    find_claude,
    http_get,
    norm_title,
)

MARK_START = "<!-- NEWS-TIMELINE:START -->"
MARK_END = "<!-- NEWS-TIMELINE:END -->"

SEEN_FILE = SCRIPT_DIR / "news_seen.json"
SEEN_KEEP = 800           # titles retained in the ledger
DICT_KEEP = 500           # summaries / reps / related entries retained

MODEL = "claude-opus-4-8"
VET_MAX = 60              # articles vetted per run (newest first)
RECENT_REPS = 25          # representatives offered as dup targets to the LLM
TELEGRAM_LIMIT = 3800     # chars per message; hard cap is 4096

ITEM_RE = re.compile(
    r'<li class="tl-item"><a class="tl-title" href="(?P<link>[^"]+)"[^>]*>'
    r'(?P<title>.*?)</a> <span class="tl-cat">(?P<source>.*?)</span>'
    r'(?:<div class="tl-note">.*?</div>)?'
    r'(?:<div class="tl-related">.*?</div>)?'
    r'<div class="tl-date">(?P<date>[\d.]+)</div></li>'
)

VET_SCHEMA = {
    "type": "object",
    "properties": {
        "articles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "keep": {
                        "type": "boolean",
                        "description": "False only for junk (not an article, "
                                       "or off-topic).",
                    },
                    "duplicate_of": {
                        "type": "string",
                        "description": "'' if this is its own story; a batch "
                                       "index like '3' if it duplicates that "
                                       "article in this list; 'R2' if it "
                                       "duplicates recent representative R2.",
                    },
                    "summary": {
                        "type": "string",
                        "description": "One Korean sentence, 40-80 chars. "
                                       "Only for keep=true with "
                                       "duplicate_of=''.",
                    },
                    "drop_reason": {
                        "type": "string",
                        "description": "Why it was dropped. Empty when kept.",
                    },
                },
                "required": ["index", "keep", "duplicate_of", "summary",
                             "drop_reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["articles"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Parsing and the ledger
# ---------------------------------------------------------------------------


def parse_items(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if MARK_START not in text or MARK_END not in text:
        return []
    block = text.split(MARK_START, 1)[1].split(MARK_END, 1)[0]
    return [
        {
            "link": m.group("link"),
            "title": html.unescape(m.group("title")),
            "source": html.unescape(m.group("source")),
            "date": m.group("date"),
        }
        for m in ITEM_RE.finditer(block)
    ]


def load_seen() -> dict:
    seen = {"titles": [], "summaries": {}, "dropped": [],
            "reps": {}, "related": {}, "related_members": {}, "outlets": {}}
    if SEEN_FILE.exists():
        try:
            seen.update(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    return seen


def save_seen(seen: dict) -> None:
    # Each structure is capped independently. (An earlier version pruned the
    # verdict dicts against the reported-titles window, which silently forgot
    # drop/summary verdicts and let vetted-out duplicates resurface.)
    seen["titles"] = seen["titles"][-SEEN_KEEP:]
    seen["dropped"] = seen["dropped"][-SEEN_KEEP:]
    for k in ("summaries", "reps", "related", "related_members", "outlets"):
        d = seen[k]
        if len(d) > DICT_KEEP:
            seen[k] = dict(list(d.items())[-DICT_KEEP:])
    SEEN_FILE.write_text(
        json.dumps(seen, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8", newline="\n")


def item_meta(it: dict) -> dict:
    return {"title": it["title"], "link": it["link"],
            "source": it["source"], "date": it["date"]}


# ---------------------------------------------------------------------------
# Vetting + Korean summaries + duplicate grouping
# ---------------------------------------------------------------------------


def _via_api(prompt: str) -> str | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ImportError:
        return None
    try:
        resp = anthropic.Anthropic().messages.create(
            model=MODEL,
            max_tokens=8000,
            output_config={
                "format": {"type": "json_schema", "schema": VET_SCHEMA},
                "effort": "low",
            },
            messages=[{"role": "user", "content": prompt}],
        )
        return next(b.text for b in resp.content if b.type == "text")
    except Exception as exc:
        print(f"  API call failed: {exc}", file=sys.stderr)
        return None


def _via_cli(prompt: str) -> str | None:
    """The claude CLI, for local runs with no API key.

    The prompt goes over stdin — as an argv element it blows past Windows'
    ~32K command-line limit once a few dozen article bodies are attached.
    """
    claude = find_claude()
    if not claude:
        return None
    try:
        res = subprocess.run(
            [claude, "-p", "--output-format", "text"],
            input=prompt + '\n\n오직 JSON만 출력하라: {"articles": '
            '[{"index": 0, "keep": true, "duplicate_of": "", '
            '"summary": "...", "drop_reason": ""}]}',
            capture_output=True, text=True, timeout=600, encoding="utf-8")
        if res.returncode != 0:
            print(f"  CLI exited {res.returncode}: {res.stderr[:200]}",
                  file=sys.stderr)
            return None
        m = re.search(r"\{.*\}", res.stdout, re.S)
        return m.group(0) if m else None
    except Exception as exc:
        print(f"  CLI call failed: {exc}", file=sys.stderr)
        return None


def vet_and_summarize(items: list[dict], recent_reps: list[dict],
                      outlets: dict | None = None) -> dict[int, dict]:
    """Vet each article, group duplicates, summarize keepers in Korean.

    recent_reps: representatives from earlier runs, offered as R0..Rn dup
    targets so a late-arriving outlet's copy folds under the original story.
    outlets: optional {domain: count} tally, incremented for kept articles.
    Returns {index: verdict}; {} when no LLM is reachable.
    """
    if not items:
        return {}

    infos = [fetch_article_info(it["link"]) for it in items]
    print(f"  body fetched for {sum(1 for i in infos if i['text'])}"
          f"/{len(items)} article(s)")

    out: dict[int, dict] = {}

    # Google News sometimes re-serves years-old archive pages under a fresh
    # date (a 2015 Samsung newsroom post came through dated 2026-07-07). When
    # the page's own publication date is much older than the feed date, drop
    # it before it reaches the LLM.
    live_idx = []
    for i, (it, info) in enumerate(zip(items, infos)):
        stale = False
        if info["date"]:
            try:
                listed = datetime.strptime(it["date"], "%Y.%m.%d")
                stale = (listed - info["date"]).days > 60
            except Exception:
                stale = False
        if stale:
            out[i] = {"index": i, "keep": False, "duplicate_of": "",
                      "summary": "",
                      "drop_reason": f"재색인된 옛 기사(실제 게재일 "
                                     f"{info['date']:%Y-%m-%d})"}
        else:
            live_idx.append(i)

    CHUNK = 15
    for base in range(0, len(live_idx), CHUNK):
        idxs = live_idx[base:base + CHUNK]
        out.update(_vet_chunk([items[i] for i in idxs],
                              [infos[i]["text"] for i in idxs],
                              recent_reps, idxs))

    # Outlet tracking — which publishers keep producing on-topic coverage.
    # evolve_outlets() turns the frequent ones into direct-RSS subscriptions.
    if outlets is not None:
        for i, info in enumerate(infos):
            v = out.get(i)
            if info["domain"] and v is not None and v["keep"]:
                outlets[info["domain"]] = outlets.get(info["domain"], 0) + 1

    kept = sum(1 for a in out.values() if a["keep"] and not a["duplicate_of"])
    grouped = sum(1 for a in out.values() if a["keep"] and a["duplicate_of"])
    print(f"  vetted: {kept} kept / {grouped} grouped as related / "
          f"{len(out) - kept - grouped} dropped")
    for i, a in sorted(out.items()):
        if not a["keep"]:
            print(f"    dropped: {items[i]['title'][:52]} "
                  f"-- {a['drop_reason']}")
        elif a["duplicate_of"]:
            print(f"    related({a['duplicate_of']}): "
                  f"{items[i]['title'][:52]}")
    return out


def _vet_chunk(items: list[dict], bodies: list[str],
               recent_reps: list[dict],
               numbers: list[int]) -> dict[int, dict]:
    """numbers: the global index shown for (and returned with) each item, so
    duplicate_of references stay valid across chunks."""
    lines = []
    for i, it in enumerate(items):
        entry = f'{numbers[i]}. [{it["source"]} · {it["date"]}] {it["title"]}'
        if bodies[i]:
            entry += f"\n   본문: {bodies[i][:700]}"
        else:
            entry += "\n   본문: (본문을 가져오지 못함)"
        lines.append(entry)

    rep_lines = [f'R{j}. [{r["date"]}] {r["title"]}'
                 for j, r in enumerate(recent_reps)]
    rep_block = ("\n\n이미 보도된 대표기사 목록 (R번호):\n"
                 + "\n".join(rep_lines)) if rep_lines else ""

    prompt = (
        "다음은 방송·측위 뉴스 피드가 수집한 기사 목록이다. 이 피드는 다음을 "
        "폭넓게 추적한다:\n"
        "  (가) ATSC 3.0 / NextGen TV, 브라질 TV 3.0(DTV+), EdgeBeam 등 차세대 "
        "지상파 방송 (표준화·특허 분쟁 포함),\n"
        "  (나) GNSS RTK·정밀측위·측량·BPS(방송 측위)·PNT 전반 — 방송망 기반에 "
        "국한하지 않는다,\n"
        "  (다) MBC RTK 생태계의 파트너·고객·응용 — 지알엠(GRM)·씨너렉스·"
        "서울도시가스(측위/측량 사업), 긴트(GINT, 정밀농업·자율주행 트랙터), "
        "얀마(농기계), 그린라이드(이륜차), 시스테크(드론), Pearl TV·Zinwell·"
        "Tolka(수신기), Merkhet·Cerinet, ETRI·IEEE BMSB 학술 성과 등.\n\n"
        f"{chr(10).join(lines)}{rep_block}\n\n"
        "각 기사(번호별)에 대해 판단하라.\n\n"
        "1) keep — 위 (가)(나)(다) 중 하나에 해당하는 실제 기사면 true.\n"
        "   다음만 keep=false: 실제 기사가 아닌 것(사진 라이브러리, 아카이브 "
        "색인, 행사 안내 스텁, 경품 응모, 주가·공시 단신), 또는 위 주제와 "
        "무관한 것(단어만 우연히 겹친 경우).\n\n"
        "2) duplicate_of — 같은 사건·발표를 다룬 기사가 목록이나 R목록에 있으면 "
        "그 번호를 문자열로 적는다 (목록 내 기사면 '3'처럼 번호, 이미 보도된 "
        "대표기사면 'R2'처럼). 스스로가 대표가 될 기사(가장 상세하거나 원 "
        "출처에 가까운 것 하나)는 ''로 둔다. 같은 회사의 서로 다른 소식은 "
        "중복이 아니다.\n\n"
        "3) summary — duplicate_of가 ''이고 keep=true인 기사만, 한국어 한 문장"
        "(40~80자). 읽는 사람은 포르투갈어·영어를 편하게 읽지 못한다 — 요약만 "
        "읽고 내용을 파악할 수 있어야 한다. 본문을 반영하고 제목 직역은 "
        "피하라. 회사·기관·표준 이름은 원문 표기 유지 (ATSC 3.0, Anatel, "
        "Globo, Sinclair, NAB 등). 본문이 없으면 제목의 확실한 사실만 쓰라.\n\n"
        "index는 위 목록의 번호를 그대로 쓴다."
    )

    text = _via_api(prompt) or _via_cli(prompt)
    if not text:
        print("  no LLM available (ANTHROPIC_API_KEY / claude CLI) "
              "-> deferring vetting to a later run", file=sys.stderr)
        return {}
    try:
        data = json.loads(text)
        valid = set(numbers)
        return {a["index"]: a for a in data["articles"]
                if a["index"] in valid}
    except Exception as exc:
        print(f"  vet parse failed: {exc}", file=sys.stderr)
        return {}


def apply_verdicts(fresh: list[dict], verdicts: dict[int, dict],
                   seen: dict, recent_reps: list[dict]) -> tuple[list, int]:
    """Fold verdicts into the ledger. Returns (kept_for_telegram, dropped_n).

    kept_for_telegram: [(item, summary, [related_meta...])] — only new
    representatives; related articles ride along under their representative.
    """
    kept: dict[str, tuple[dict, str, list]] = {}   # rep_key -> entry
    dropped = 0

    def resolve_rep_key(ref: str, hop: int = 0) -> str | None:
        """duplicate_of reference -> representative's norm key."""
        if hop > 4 or not ref:
            return None
        if ref.startswith("R"):
            try:
                return norm_title(recent_reps[int(ref[1:])]["title"])
            except Exception:
                return None
        try:
            j = int(ref)
            v = verdicts.get(j)
            if v is None or not v["keep"]:
                return None
            if v["duplicate_of"]:
                return resolve_rep_key(v["duplicate_of"], hop + 1)
            return norm_title(fresh[j]["title"])
        except Exception:
            return None

    for i, it in enumerate(fresh):
        v = verdicts.get(i)
        key = norm_title(it["title"])
        if v is None:                     # not vetted (no LLM / over cap)
            kept[key] = (it, "", [])
            continue
        if not v["keep"]:
            dropped += 1
            if key not in set(seen["dropped"]):
                seen["dropped"].append(key)
            continue
        rep_key = resolve_rep_key(v["duplicate_of"])
        if rep_key and rep_key != key:
            seen["related_members"][key] = rep_key
            seen["related"].setdefault(rep_key, [])
            if not any(norm_title(m["title"]) == key
                       for m in seen["related"][rep_key]):
                seen["related"][rep_key].append(item_meta(it))
            if rep_key in kept:           # rep is in this batch — ride along
                kept[rep_key][2].append(item_meta(it))
        else:
            summary = v["summary"].strip()
            seen["reps"][key] = item_meta(it)
            if summary:
                seen["summaries"][key] = summary
            kept[key] = (it, summary, [])
    return list(kept.values()), dropped


# ---------------------------------------------------------------------------
# Rendering: Telegram + the page itself
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def outlet(source: str) -> str:
    """'와우테일 · KR' -> '와우테일' (for the compact related-articles line)."""
    return source.split(" · ")[0]


def related_line_html(rels: list[dict]) -> str:
    links = " · ".join(
        f'<a href="{esc(m["link"])}" target="_blank" rel="noopener">'
        f'{esc(outlet(m["source"]))}</a>'
        for m in rels)
    return f'<div class="tl-related">관련기사 {len(rels)} — {links}</div>'


def query_digest() -> str:
    try:
        store = json.loads(QUERIES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return ""
    seeds = store.get("seeds", [])
    learned = [q for q in store.get("learned", []) if q.get("enabled", True)]
    feeds = [f for f in store.get("feeds", []) if f.get("enabled", True)]
    lines = [f'  <code>[{q["region"]}] {esc(q["q"])}</code>' for q in seeds]
    lines += [f'  <code>[{q["region"]}] {esc(q["q"])}</code> 🆕'
              for q in learned]
    lines += [f'  <code>[{f["region"]}] 매체구독: {esc(f["source"])}</code>'
              for f in feeds]
    if not lines:
        return ""
    head = f"🔎 <b>검색 키워드</b> — 시드 {len(seeds)}"
    if learned:
        head += f" + 학습 {len(learned)}"
    if feeds:
        head += f" + 매체 {len(feeds)}"
    return head + "\n" + "\n".join(lines)


def build_messages(kept: list[tuple[dict, str, list]], dropped: int,
                   grouped: int, total: int) -> list[str]:
    queries = query_digest()

    if not kept:
        msg = f"📡 <b>Broadcast RTK 뉴스</b>\n\n새로 보낼 기사 없음 (수집 {total}건)."
        if dropped or grouped:
            msg += f"\n제외 {dropped}건 · 관련기사 묶음 {grouped}건."
        return [msg + "\n\n" + queries] if queries else [msg]

    header = f"📡 <b>Broadcast RTK 뉴스 — 신규 {len(kept)}건</b> (수집 {total}건)"
    extras = []
    if grouped:
        extras.append(f"관련기사 묶음 {grouped}건")
    if dropped:
        extras.append(f"제외 {dropped}건")
    if extras:
        header += f"\n<i>{' · '.join(extras)}</i>"

    blocks = []
    for it, summary, rels in kept:
        parts = [f'• <a href="{esc(it["link"])}">{esc(it["title"])}</a>']
        if summary:
            parts.append(f"  {esc(summary)}")
        parts.append(f'  <i>{esc(it["source"])} · {esc(it["date"])}</i>')
        if rels:
            links = " · ".join(
                f'<a href="{esc(m["link"])}">{esc(outlet(m["source"]))}</a>'
                for m in rels)
            parts.append(f"  ↳ 관련기사: {links}")
        blocks.append("\n".join(parts))

    if queries:
        blocks.append(queries)

    messages, current = [], header
    for block in blocks:
        if len(current) + len(block) + 2 > TELEGRAM_LIMIT:
            messages.append(current)
            current = block
        else:
            current += "\n\n" + block
    messages.append(current)
    return messages


def send_telegram(messages: list[str]) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID unset -> dry run:\n")
        print("\n\n---\n\n".join(messages))
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for msg in messages:
        payload = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }).encode()
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, data=payload), timeout=30
            ) as resp:
                resp.read()
            print(f"  telegram: sent ({len(msg)} chars)")
        except Exception as exc:
            print(f"  telegram send failed: {exc}", file=sys.stderr)


def patch_page(path: Path, seen: dict) -> None:
    """Rebuild the timeline items from the ledger: drop vetted-out junk, fold
    related coverage under its representative, attach Korean summaries."""
    text = path.read_text(encoding="utf-8")
    if MARK_START not in text or MARK_END not in text:
        return
    summaries = seen["summaries"]
    dropped = set(seen["dropped"])
    members = seen["related_members"]
    related = seen["related"]

    def rewrite(m: re.Match) -> str:
        title = html.unescape(m.group("title"))
        key = norm_title(title)
        if key in dropped or key in members:
            return ""
        note = summaries.get(key, "")
        note_html = (f'<div class="tl-note">{esc(note)}</div>'
                     if note else "")
        rel_html = (related_line_html(related[key])
                    if related.get(key) else "")
        return (
            '<li class="tl-item">'
            f'<a class="tl-title" href="{m.group("link")}" target="_blank" '
            f'rel="noopener">{m.group("title")}</a> '
            f'<span class="tl-cat">{m.group("source")}</span>'
            f'{note_html}{rel_html}'
            f'<div class="tl-date">{m.group("date")}</div></li>'
        )

    block = text.split(MARK_START, 1)[1].split(MARK_END, 1)[0]
    new_block = ITEM_RE.sub(rewrite, block)
    new_block = re.sub(r"\n\s*\n+", "\n", new_block)
    path.write_text(text.replace(block, new_block, 1),
                    encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------


def recent_rep_list(seen: dict) -> list[dict]:
    return list(seen["reps"].values())[-RECENT_REPS:]


# ---------------------------------------------------------------------------
# 검색 대상 진화 — outlets that keep producing on-topic coverage get their own
# RSS subscription, so their articles arrive even when no query matches.
# ---------------------------------------------------------------------------

FEED_MAX = 8
OUTLET_MIN = 4            # kept articles before an outlet earns a feed slot
RSS_PATHS = ("/feed/", "/rss/allArticle.xml", "/feed", "/rss")


def _discover_rss(domain: str) -> str | None:
    for path in RSS_PATHS:
        url = f"https://{domain}{path}"
        try:
            head = http_get(url, timeout=12)[:300].decode("utf-8", "ignore")
            if "<rss" in head or "<feed" in head or "<?xml" in head:
                return url
        except Exception:
            continue
    try:  # homepage <link rel="alternate" type="application/rss+xml">
        page = http_get(f"https://{domain}/", timeout=12).decode(
            "utf-8", "ignore")
        m = re.search(r'<link[^>]+type=["\']application/(?:rss|atom)\+xml'
                      r'["\'][^>]+href=["\']([^"\']+)', page, re.I)
        if m:
            return urllib.parse.urljoin(f"https://{domain}/", m.group(1))
    except Exception:
        pass
    return None


def evolve_outlets(seen: dict) -> list[str]:
    """Promote frequently-on-topic outlets to direct-RSS subscriptions."""
    try:
        store = json.loads(QUERIES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    feeds = store.setdefault("feeds", [])
    have = {urllib.parse.urlparse(f["url"]).netloc.removeprefix("www.")
            for f in feeds}
    added = []
    for domain, count in sorted(seen["outlets"].items(),
                                key=lambda kv: -kv[1]):
        if len(feeds) >= FEED_MAX:
            break
        if count < OUTLET_MIN or domain in have:
            continue
        url = _discover_rss(domain)
        if not url:
            continue
        if domain.endswith(".kr"):
            region, tz = "KR", 9
        elif domain.endswith(".br"):
            region, tz = "BR", -3
        else:
            region, tz = "US", 0
        feeds.append({"url": url, "source": domain, "region": region,
                      "tz_hours": tz, "enabled": True,
                      "why": f"auto-subscribed: {count} on-topic articles "
                             f"collected from this outlet"})
        have.add(domain)
        added.append(f"{domain} ({count}건 → {url})")
    if added:
        QUERIES_FILE.write_text(
            json.dumps(store, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")
        for a in added:
            print(f"  outlet promoted to feed: {a}")
    return added


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    old_items = parse_items(Path(sys.argv[1]))
    new_items = parse_items(Path(sys.argv[2]))

    changed = ({norm_title(i["title"]) for i in new_items}
               != {norm_title(i["title"]) for i in old_items})

    seen = load_seen()
    seen_keys = set(seen["titles"])
    fresh, fresh_keys = [], set()
    for it in new_items:
        k = norm_title(it["title"])
        if k in seen_keys or k in fresh_keys:
            continue
        fresh_keys.add(k)
        fresh.append(it)

    print(f"page: {len(old_items)} -> {len(new_items)} articles "
          f"(changed={changed})")
    print(f"unreported: {len(fresh)} (ledger holds {len(seen_keys)} titles)")

    if len(fresh) > VET_MAX:
        print(f"  capping this run at the {VET_MAX} newest of {len(fresh)}")
        fresh = fresh[:VET_MAX]
        fresh_keys = {norm_title(it["title"]) for it in fresh}

    verdicts = vet_and_summarize(fresh, recent_rep_list(seen),
                                 seen["outlets"])
    kept, dropped = apply_verdicts(fresh, verdicts, seen, recent_rep_list(seen))
    grouped = len(fresh) - len(kept) - dropped

    send_telegram(build_messages(kept, dropped, grouped, len(new_items)))
    seen["titles"].extend(sorted(fresh_keys))

    # Self-heal: articles reported by an LLM-less run sit on the page without
    # a verdict. Re-vet them now (no re-send — they were already announced).
    healed = 0
    if verdicts or not fresh:      # only when an LLM is actually reachable
        resolved = (set(seen["summaries"]) | set(seen["dropped"])
                    | set(seen["related_members"]))
        stale = [it for it in new_items
                 if norm_title(it["title"]) in set(seen["titles"])
                 and norm_title(it["title"]) not in resolved
                 and norm_title(it["title"]) not in fresh_keys]
        stale = stale[:VET_MAX]
        if stale:
            print(f"self-heal: re-vetting {len(stale)} article(s) reported "
                  f"without a verdict")
            heal_verdicts = vet_and_summarize(stale, recent_rep_list(seen),
                                              seen["outlets"])
            if heal_verdicts:
                apply_verdicts(stale, heal_verdicts, seen,
                               recent_rep_list(seen))
                healed = len(heal_verdicts)

    evolve_outlets(seen)
    save_seen(seen)
    patch_page(Path(sys.argv[2]), seen)

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        page_changed = changed or healed > 0
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if page_changed else 'false'}\n")
            f.write(f"added={len(kept)}\n")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
