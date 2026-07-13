#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report newly-collected Broadcast RTK / ATSC 3.0 news to Telegram.

Reads the NEWS-TIMELINE block that fetch_rtk_news.py just wrote, works out
which articles are genuinely new, reads each one's body, has Claude vet it and
write a one-line Korean summary, and posts the digest with the active search
queries appended.

Two things make "genuinely new" harder than it looks:

  * Google News mints a DIFFERENT encoded URL for the same article on every
    fetch, and sometimes re-dates it (a Samsung item first seen 2026-06-24 came
    back as 2026-07-07). Deduping on the URL therefore re-reports old articles
    as new. We dedup on the normalized title instead.
  * The page only holds the newest ~50 items, so an article that scrolls off and
    is later re-indexed would look new again. A persistent ledger
    (scripts/news_seen.json) records every title ever reported, so nothing is
    ever sent twice.

Claude also vets each article against its body text and drops the ones that
aren't real, on-topic coverage — Google indexes photo-library and archive pages
that carry a fresh date but no news in them.

Usage (from the repository root):
    python scripts/news_notify.py OLD_PAGE NEW_PAGE

Environment:
    ANTHROPIC_API_KEY    summaries via the API (falls back to the claude CLI)
    TELEGRAM_BOT_TOKEN   required to send (dry-run prints to stdout if unset)
    TELEGRAM_CHAT_ID     required to send
    GITHUB_OUTPUT        if set, `changed=true|false` is appended to it

Exits 0 even when Telegram or Claude fail — a broken notification must not fail
the news refresh itself.
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

from fetch_rtk_news import (  # noqa: E402
    QUERIES_FILE,
    fetch_body_excerpt,
    find_claude,
    norm_title,
)

MARK_START = "<!-- NEWS-TIMELINE:START -->"
MARK_END = "<!-- NEWS-TIMELINE:END -->"

SEEN_FILE = SCRIPT_DIR / "news_seen.json"
SEEN_KEEP = 600           # titles retained in the ledger

MODEL = "claude-opus-4-8"
VET_MAX = 60              # articles vetted+summarized per run (newest first);
                         # one LLM call, so this only bounds a huge first run.
                         # Steady-state runs have a handful of new articles.
TELEGRAM_LIMIT = 3800     # chars per message; hard cap is 4096

ITEM_RE = re.compile(
    r'<li class="tl-item"><a class="tl-title" href="(?P<link>[^"]+)"[^>]*>'
    r'(?P<title>.*?)</a> <span class="tl-cat">(?P<source>.*?)</span>'
    r'(?:<div class="tl-note">.*?</div>)?'
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
                        "description": "False if this is not real, current, "
                                       "on-topic news coverage.",
                    },
                    "summary": {
                        "type": "string",
                        "description": "One Korean sentence, 40-80 chars. "
                                       "Empty when keep is false.",
                    },
                    "drop_reason": {
                        "type": "string",
                        "description": "Why it was dropped. Empty when kept.",
                    },
                },
                "required": ["index", "keep", "summary", "drop_reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["articles"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Parsing and the seen-ledger
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
    seen = {"titles": [], "summaries": {}, "dropped": []}
    if SEEN_FILE.exists():
        try:
            seen.update(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    return seen


def save_seen(seen: dict) -> None:
    seen["titles"] = seen["titles"][-SEEN_KEEP:]
    kept = set(seen["titles"])
    seen["summaries"] = {k: v for k, v in seen["summaries"].items() if k in kept}
    seen["dropped"] = [k for k in seen["dropped"] if k in kept]
    SEEN_FILE.write_text(
        json.dumps(seen, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8", newline="\n")


def patch_page(path: Path, seen: dict) -> None:
    """Re-render the page's timeline items with summaries; drop vetted-out junk.

    fetch_rtk_news.py applies the same ledger on its next run — this patch makes
    the current commit carry the summaries instead of trailing one run behind.
    """
    text = path.read_text(encoding="utf-8")
    if MARK_START not in text or MARK_END not in text:
        return
    summaries = seen.get("summaries", {})
    dropped = set(seen.get("dropped", []))

    def rewrite(m: re.Match) -> str:
        key = norm_title(html.unescape(m.group("title")))
        if key in dropped:
            return ""
        item = m.group(0)
        item = re.sub(r'<div class="tl-note">.*?</div>', "", item)
        note = summaries.get(key)
        if note:
            note_html = (f'<div class="tl-note">'
                         f'{html.escape(note, quote=False)}</div>')
            item = item.replace('<div class="tl-date">',
                                note_html + '<div class="tl-date">', 1)
        return item

    block, rest = text.split(MARK_START, 1)[1].split(MARK_END, 1)[0], None
    new_block = ITEM_RE.sub(rewrite, block)
    new_block = re.sub(r"\n\s*\n+", "\n", new_block)
    path.write_text(text.replace(block, new_block, 1),
                    encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# Vetting + Korean summaries
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
    """The claude CLI, for local runs with no API key."""
    claude = find_claude()
    if not claude:
        return None
    try:
        res = subprocess.run(
            [claude, "-p", prompt + '\n\n오직 JSON만 출력하라: {"articles": '
             '[{"index": 0, "keep": true, "summary": "...", '
             '"drop_reason": ""}]}',
             "--output-format", "text"],
            capture_output=True, text=True, timeout=600, encoding="utf-8")
        if res.returncode != 0:
            return None
        m = re.search(r"\{.*\}", res.stdout, re.S)
        return m.group(0) if m else None
    except Exception as exc:
        print(f"  CLI call failed: {exc}", file=sys.stderr)
        return None


def vet_and_summarize(items: list[dict]) -> dict[int, dict]:
    """Read each article's body, drop the junk, summarize the rest in Korean.

    Returns {index: {"keep": bool, "summary": str, "drop_reason": str}}. On any
    failure returns {} and the caller sends everything unsummarized rather than
    sending nothing.
    """
    if not items:
        return {}

    lines = []
    with_body = 0
    for i, it in enumerate(items):
        excerpt = fetch_body_excerpt(it["link"])
        entry = f'{i}. [{it["source"]} · {it["date"]}] {it["title"]}'
        if excerpt:
            entry += f"\n   본문: {excerpt[:700]}"
            with_body += 1
        else:
            entry += "\n   본문: (본문을 가져오지 못함)"
        lines.append(entry)
    print(f"  body fetched for {with_body}/{len(items)} article(s)")

    prompt = (
        "다음은 방송·측위 뉴스 피드가 수집한 기사 목록이다. 이 피드는 다음을 "
        "폭넓게 추적한다:\n"
        "  (가) ATSC 3.0 / NextGen TV, 브라질 TV 3.0(DTV+), EdgeBeam 등 차세대 "
        "지상파 방송,\n"
        "  (나) GNSS RTK·정밀측위·측량 전반 — 방송망 기반(Broadcast RTK·eGPS·BPS)에 "
        "국한하지 말고 일반 GNSS RTK 측위/측량도 포함,\n"
        "  (다) MBC RTK 생태계의 파트너·고객·응용 — 지알엠(GRM)·씨너렉스·서울도시가스"
        "(측위/측량 사업), 긴트(GINT, 정밀농업·자율주행 트랙터), 얀마(농기계), "
        "그린라이드(이륜차), 시스테크(드론) 등과 이들의 정밀측위·측량·자율주행·드론·"
        "모빌리티 사업.\n\n"
        f"{chr(10).join(lines)}\n\n"
        "각 기사에 대해 두 가지를 판단하라.\n\n"
        "1) keep — 이걸 알림으로 보낼 가치가 있는가?\n"
        "   위 (가)(나)(다) 중 하나에 해당하면 keep=true. '방송망 기반이 아닌 일반 "
        "GNSS RTK/측량'이라는 이유로 버리지 마라 — 그것도 (나)로 포함한다.\n"
        "   다음만 keep=false로 버려라:\n"
        "   - 실제 기사가 아닌 것 (사진 라이브러리, 아카이브 색인, 태그 목록, "
        "행사 안내 스텁, 경품 응모, 주가/공시 단신 등). 구글이 오래된 아카이브 "
        "페이지에 최근 날짜를 붙여 색인하는 일이 잦다.\n"
        "   - 위 (가)(나)(다) 어디에도 해당하지 않는 기사 (회사명·단어가 우연히 "
        "겹쳤을 뿐, 예: 얀마 굴삭기 중고매물, 그린라이트 예능/골프앱, 서울도시가스의 "
        "측위와 무관한 에너지 사업).\n"
        "   - 이미 목록의 다른 기사와 내용이 사실상 동일한 중복. 중복이면 하나만 "
        "keep=true로 남기고 나머지는 keep=false, drop_reason에 'N번과 중복'.\n"
        "   본문을 가져오지 못한 경우, 제목이 위 주제와 명확히 관련되면 keep=true로 "
        "두되 추측해서 요약하지는 마라.\n\n"
        "2) summary — keep=true인 기사만, 한국어 한 문장(40~80자).\n"
        "   - 읽는 사람은 포르투갈어를 모른다. 브라질 기사도 요약만 읽고 내용을 "
        "파악할 수 있어야 한다. 제목을 다시 읽을 필요가 없게 쓰라.\n"
        "   - 본문 내용을 반영하라. 제목 직역은 하지 마라.\n"
        "   - 회사·기관·표준 이름은 원문 표기 유지 (ATSC 3.0, Anatel, Globo, "
        "Sinclair, NAB 등).\n"
        "   - keep=false면 summary는 빈 문자열, drop_reason에 버린 이유를 짧게 쓰라.\n\n"
        "index는 위 목록의 번호를 그대로 쓴다."
    )

    text = _via_api(prompt) or _via_cli(prompt)
    if not text:
        print("  no LLM available (ANTHROPIC_API_KEY / claude CLI) "
              "-> sending unvetted", file=sys.stderr)
        return {}
    try:
        data = json.loads(text)
        out = {
            a["index"]: a
            for a in data["articles"]
            if 0 <= a["index"] < len(items)
        }
        kept = sum(1 for a in out.values() if a["keep"])
        print(f"  vetted: {kept} kept / {len(out) - kept} dropped")
        for i, a in sorted(out.items()):
            if not a["keep"]:
                print(f"    dropped: {items[i]['title'][:55]} "
                      f"-- {a['drop_reason']}")
        return out
    except Exception as exc:
        print(f"  vet parse failed: {exc}", file=sys.stderr)
        return {}


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def query_digest() -> str:
    """The active search queries, so the reader sees what the feed is watching."""
    try:
        store = json.loads(QUERIES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return ""
    seeds = store.get("seeds", [])
    learned = [q for q in store.get("learned", []) if q.get("enabled", True)]
    lines = [f'  <code>[{q["region"]}] {esc(q["q"])}</code>' for q in seeds]
    lines += [f'  <code>[{q["region"]}] {esc(q["q"])}</code> 🆕' for q in learned]
    if not lines:
        return ""
    head = f"🔎 <b>검색 키워드</b> — 시드 {len(seeds)}"
    if learned:
        head += f" + 학습 {len(learned)}"
    return head + "\n" + "\n".join(lines)


def build_messages(kept: list[tuple[dict, str]], dropped: int,
                   total: int) -> list[str]:
    """kept: [(item, summary)]. Split to stay under the Telegram length limit."""
    queries = query_digest()

    if not kept:
        msg = f"📡 <b>Broadcast RTK 뉴스</b>\n\n새로 보낼 기사 없음 (수집 {total}건)."
        if dropped:
            msg += f"\n신규 {dropped}건은 관련성 없어 제외."
        return [msg + "\n\n" + queries] if queries else [msg]

    header = f"📡 <b>Broadcast RTK 뉴스 — 신규 {len(kept)}건</b> (수집 {total}건)"
    if dropped:
        header += f"\n<i>관련성 없어 제외 {dropped}건</i>"

    blocks = []
    for it, summary in kept:
        parts = [f'• <a href="{esc(it["link"])}">{esc(it["title"])}</a>']
        if summary:
            parts.append(f"  {esc(summary)}")
        parts.append(f'  <i>{esc(it["source"])} · {esc(it["date"])}</i>')
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


# ---------------------------------------------------------------------------


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    old_items = parse_items(Path(sys.argv[1]))
    new_items = parse_items(Path(sys.argv[2]))

    # Whether the PAGE changed (drives the commit) — by title, since the same
    # article gets a fresh URL on every fetch.
    changed = ({norm_title(i["title"]) for i in new_items}
               != {norm_title(i["title"]) for i in old_items})

    # Whether an article is NEW TO REPORT — against the persistent ledger, so a
    # re-dated or re-linked article is never announced twice.
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

    to_vet = fresh[:VET_MAX]
    if len(fresh) > VET_MAX:
        print(f"  vetting the {VET_MAX} newest of {len(fresh)}; the rest are "
              f"listed unvetted")
    verdicts = vet_and_summarize(to_vet)

    kept, dropped = [], 0
    for i, it in enumerate(fresh):
        v = verdicts.get(i)
        key = norm_title(it["title"])
        if v is None:                     # not vetted (over cap, or LLM down)
            kept.append((it, ""))
        elif v["keep"]:
            kept.append((it, v["summary"]))
            if v["summary"]:
                seen["summaries"][key] = v["summary"]
        else:
            dropped += 1
            seen["dropped"].append(key)

    send_telegram(build_messages(kept, dropped, len(new_items)))

    # Record everything we looked at — including the dropped ones, so a junk
    # article that keeps getting re-indexed is only ever evaluated once.
    seen["titles"].extend(sorted(fresh_keys))
    save_seen(seen)

    # Carry the summaries onto the page itself and remove the vetted-out junk.
    patch_page(Path(sys.argv[2]), seen)

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
            f.write(f"added={len(kept)}\n")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
