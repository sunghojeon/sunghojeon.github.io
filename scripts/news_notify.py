#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diff the "In the news" timeline and report the new articles to Telegram.

Compares the NEWS-TIMELINE block of two versions of broadcast-rtk.md (the
committed one and the one fetch_rtk_news.py just rewrote), summarizes each
newly-added article in one Korean line via the Claude API, and posts the
result to a Telegram chat.

The timeline block carries a "last updated <date>" stamp that changes on
every run, so the page always looks modified even when no article changed.
`changed` in the output reflects the *article list*, not the file — the
workflow uses it to decide whether the commit is worth making.

Usage (from the repository root):
    python scripts/news_notify.py OLD_PAGE NEW_PAGE

Environment:
    ANTHROPIC_API_KEY    required for Korean summaries (skipped if unset)
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
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from fetch_rtk_news import fetch_body_excerpt  # noqa: E402

MARK_START = "<!-- NEWS-TIMELINE:START -->"
MARK_END = "<!-- NEWS-TIMELINE:END -->"

MODEL = "claude-opus-4-8"
SUMMARY_MAX = 12          # articles summarized per run (newest first)
TELEGRAM_LIMIT = 3800     # chars per message; hard cap is 4096

ITEM_RE = re.compile(
    r'<li class="tl-item"><a class="tl-title" href="(?P<link>[^"]+)"[^>]*>'
    r'(?P<title>.*?)</a> <span class="tl-cat">(?P<source>.*?)</span>'
    r'<div class="tl-date">(?P<date>[\d.]+)</div></li>'
)

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "summaries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "summary": {"type": "string"},
                },
                "required": ["index", "summary"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["summaries"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def parse_items(path: Path) -> list[dict]:
    """Extract the timeline items from a broadcast-rtk.md file."""
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


# ---------------------------------------------------------------------------
# Korean summaries (Claude API)
# ---------------------------------------------------------------------------


def summarize_korean(items: list[dict]) -> dict[int, str]:
    """One short Korean line per article. Returns {} on any failure."""
    if not items or not os.environ.get("ANTHROPIC_API_KEY"):
        return {}
    try:
        import anthropic
    except ImportError:
        print("  anthropic SDK not installed -> skipping summaries",
              file=sys.stderr)
        return {}

    lines = []
    for i, it in enumerate(items):
        excerpt = fetch_body_excerpt(it["link"])
        entry = f'{i}. [{it["source"]}] {it["title"]}'
        if excerpt:
            entry += f"\n   본문: {excerpt[:600]}"
        lines.append(entry)
    print(f"  body excerpts fetched for {len(items)} article(s)")

    prompt = (
        "다음은 ATSC 3.0 / NextGen TV, 브라질 TV 3.0(DTV+), Broadcast RTK·eGPS, "
        "BPS(방송 측위), EdgeBeam 관련 뉴스 헤드라인과 본문 발췌다. 방송기술 "
        "엔지니어가 훑어볼 알림용으로, 각 기사를 한국어 한 문장으로 요약하라.\n\n"
        f"{chr(10).join(lines)}\n\n"
        "규칙:\n"
        "- 기사마다 정확히 한 문장, 40자~70자 내외. 핵심 사실(누가 무엇을) 위주.\n"
        "- 제목을 그대로 번역하지 말고 본문 발췌가 있으면 그 내용을 반영하라.\n"
        "- 본문 발췌가 없으면 제목에서 확실히 알 수 있는 사실만 쓰고 추측하지 마라.\n"
        "- 회사·기관·표준 이름은 원문 표기를 유지하라 (ATSC 3.0, Sinclair, TV 3.0 등).\n"
        "- index는 위 목록의 번호를 그대로 쓴다."
    )

    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            output_config={
                "format": {"type": "json_schema", "schema": SUMMARY_SCHEMA},
                "effort": "low",
            },
            messages=[{"role": "user", "content": prompt}],
        )
        text = next(b.text for b in resp.content if b.type == "text")
        data = json.loads(text)
        return {
            s["index"]: s["summary"].strip()
            for s in data["summaries"]
            if 0 <= s["index"] < len(items)
        }
    except Exception as exc:
        print(f"  summary generation failed: {exc}", file=sys.stderr)
        return {}


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def build_messages(added: list[dict], summaries: dict[int, str],
                   total: int) -> list[str]:
    """Render the Telegram payload, split to stay under the length limit."""
    if not added:
        return [f"📡 <b>Broadcast RTK 뉴스</b>\n\n신규 기사 없음 "
                f"(수집 {total}건 유지)."]

    header = (f"📡 <b>Broadcast RTK 뉴스 — 신규 {len(added)}건</b> "
              f"(전체 {total}건)")
    blocks = []
    for i, it in enumerate(added):
        parts = [f'• <a href="{esc(it["link"])}">{esc(it["title"])}</a>']
        summary = summaries.get(i)
        if summary:
            parts.append(f"  {esc(summary)}")
        parts.append(f'  <i>{esc(it["source"])} · {esc(it["date"])}</i>')
        blocks.append("\n".join(parts))

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

    seen = {it["link"] for it in old_items}
    added = [it for it in new_items if it["link"] not in seen]
    changed = {it["link"] for it in new_items} != seen

    print(f"articles: {len(old_items)} -> {len(new_items)} "
          f"({len(added)} new, changed={changed})")

    to_summarize = added[:SUMMARY_MAX]
    if len(added) > SUMMARY_MAX:
        print(f"  summarizing the {SUMMARY_MAX} newest of {len(added)} new "
              f"articles; the rest are listed without a summary")
    summaries = summarize_korean(to_summarize)

    send_telegram(build_messages(added, summaries, len(new_items)))

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
            f.write(f"added={len(added)}\n")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
