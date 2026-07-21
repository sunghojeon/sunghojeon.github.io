#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report newly-collected Broadcast RTK / ATSC 3.0 news to Telegram.

Reads the NEWS-TIMELINE block that fetch_rtk_news.py just wrote (the
scripts/news_timeline.html data store — there is no public page any more),
works out which articles are genuinely new, reads each one's body, has
Claude vet it, group duplicate coverage, and write a one-line Korean
summary, then posts the digest and folds the results back into the store.

The digest hides nothing: every article that was collected but not
reported appears in it with the reason — low relevance score (from the
fetch run report), vetted out as junk/off-topic, stale re-index, or
folded under earlier coverage (♻️). Query evolution (added / disabled
keywords) is reported with reasons the same way.

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
    python scripts/news_notify.py OLD_TIMELINE NEW_TIMELINE
    (before/after copies of scripts/news_timeline.html)

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
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from datetime import datetime, timezone  # noqa: E402

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
# Written by fetch_rtk_news.py in the same run: low-relevance drops,
# per-region counts, query additions/disablings.
REPORT_FILE = Path(tempfile.gettempdir()) / "rtk_news_run_report.json"
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
                    "sibling_query": {
                        "type": "string",
                        "description": "For representatives only: a 2-4 word "
                                       "Google News query, in the article's "
                                       "own language, to find other outlets' "
                                       "coverage of the same story. '' "
                                       "otherwise.",
                    },
                    "has_figures": {
                        "type": "boolean",
                        "description": "True if the article carries official "
                                       "presentation slides, maps, charts, or "
                                       "technical figures (not stock photos).",
                    },
                    "drop_reason": {
                        "type": "string",
                        "description": "Why it was dropped. Empty when kept.",
                    },
                },
                "required": ["index", "keep", "duplicate_of", "summary",
                             "sibling_query", "has_figures", "drop_reason"],
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


def load_report() -> dict:
    """fetch_rtk_news.py's run report; {} when absent or stale."""
    try:
        report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
        gen = report.get("generated", "")
        if gen:  # a report left over from an unrelated earlier run
            age = datetime.now(timezone.utc) - datetime.fromisoformat(gen)
            if age.total_seconds() > 6 * 3600:
                return {}
        return report
    except Exception:
        return {}


def load_seen() -> dict:
    seen = {"titles": [], "summaries": {}, "dropped": [], "low_reported": [],
            "reps": {}, "related": {}, "related_members": {}, "outlets": {},
            "tags": {}}
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
    seen["low_reported"] = seen["low_reported"][-SEEN_KEEP:]
    for k in ("summaries", "reps", "related", "related_members", "outlets",
              "tags"):
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
            '"summary": "...", "sibling_query": "...", '
            '"has_figures": false, "drop_reason": ""}]}',
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
                      outlets: dict | None = None,
                      tag_stats: dict | None = None) -> dict[int, dict]:
    """Vet each article, group duplicates, summarize keepers in Korean.

    recent_reps: representatives from earlier runs, offered as R0..Rn dup
    targets so a late-arriving outlet's copy folds under the original story.
    outlets: optional {domain: count} tally, incremented for kept articles.
    tag_stats: optional {tag_lower: {t, n}} tally of article tags, ditto.
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
                              [infos[i] for i in idxs],
                              recent_reps, idxs))

    # Outlet + tag tracking, for kept articles only. Outlets feed
    # evolve_outlets() (direct-RSS promotion); tags feed --evolve's query
    # proposals — an editor-assigned tag recurring across kept articles is
    # the strongest evolution signal there is (this is how entities like
    # Anatel should surface without anyone noticing them by hand).
    for i, info in enumerate(infos):
        v = out.get(i)
        if v is None or not v["keep"]:
            continue
        if outlets is not None and info["domain"]:
            outlets[info["domain"]] = outlets.get(info["domain"], 0) + 1
        if tag_stats is not None:
            for tag in info.get("tags", []):
                key = tag.lower()
                e = tag_stats.get(key, {"t": tag, "n": 0})
                e["n"] += 1
                tag_stats[key] = e

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


def _vet_chunk(items: list[dict], infos: list[dict],
               recent_reps: list[dict],
               numbers: list[int]) -> dict[int, dict]:
    """numbers: the global index shown for (and returned with) each item, so
    duplicate_of references stay valid across chunks."""
    lines = []
    for i, it in enumerate(items):
        entry = f'{numbers[i]}. [{it["source"]} · {it["date"]}] {it["title"]}'
        if infos[i]["text"]:
            entry += f"\n   본문: {infos[i]['text'][:700]}"
        else:
            entry += "\n   본문: (본문을 가져오지 못함)"
        if infos[i].get("images"):
            entry += f"\n   이미지: {'; '.join(infos[i]['images'])}"
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
        "Tolka(수신기), Merkhet·Cerinet, ETRI·IEEE BMSB 학술 성과 등,\n"
        "  (라) 학회·표준화 기관(KIBME 한국방송·미디어공학회, TTA, "
        "미래방송미디어표준포럼, ATSC 등)의 ATSC 3.0·UHD·방송기술 관련 공지, "
        "워크숍, 학술대회, 표준화 행사 — 뉴스 기사가 아니어도 keep. "
        "방송사업자 협회·단체(ABERT, NAB, Pearl TV 등)의 조직 개편·정책 "
        "대응·성명도 차세대 TV·측위·규제기술 전환과 닿아 있으면 keep (예: "
        "ABERT의 규제·기술 이사회 신설). 단 라디오 전용 소식(Rádio 3.0, "
        "라디오 광고·편성·시상)은 제외,\n"
        "  (마) 규제기관(Anatel, FCC, 과기정통부 등)의 방송·주파수·측위·"
        "차세대미디어·AI 규제 정책, 공공 자문(consulta/consultation), 제도 "
        "개편 — 단, 개별 통신사 요금·개별 기업 인허가 같은 통신 실무 잡보는 "
        "제외.\n\n"
        f"{chr(10).join(lines)}{rep_block}\n\n"
        "각 기사(번호별)에 대해 판단하라.\n\n"
        "1) keep — 위 (가)(나)(다) 중 하나에 해당하는 실제 기사면 true.\n"
        "   다음만 keep=false: 실제 기사가 아닌 것(사진 라이브러리, 아카이브 "
        "색인, 행사 안내 스텁, 경품 응모, 주가·공시 단신), 또는 위 주제와 "
        "무관한 것(단어만 우연히 겹친 경우).\n\n"
        "2) duplicate_of — 같은 사건·발표를 다룬 기사가 목록이나 R목록에 있으면 "
        "그 번호를 문자열로 적는다 (목록 내 기사면 '3'처럼 번호, 이미 보도된 "
        "대표기사면 'R2'처럼). 스스로가 대표가 될 기사는 ''로 둔다. 대표 선정 "
        "기준: ① 공식 발표자료 슬라이드·지도·차트 등 기술 자료 이미지를 실은 "
        "기사 우선(이미지 목록으로 판단), ② 그다음 가장 상세하거나 원 출처에 "
        "가까운 것. 같은 회사의 서로 다른 소식은 중복이 아니다.\n\n"
        "2.7) has_figures — 이미지 목록의 파일명·캡션으로 판단해, 공식 발표 "
        "슬라이드·지도·차트·표 등 기술 자료가 실렸으면 true (기자 스케치·"
        "인물사진·스톡이미지는 false).\n\n"
        "2.5) sibling_query — 대표기사(keep=true, duplicate_of='')마다, 다른 "
        "매체의 같은 사건 보도를 찾을 구글뉴스 검색어를 기사 언어로 2~4단어 "
        "제안하라 (예: 'KBS 적자 지상파', 'Anatel TV 3.0 250 MHz'). 중복·"
        "junk면 ''.\n\n"
        "3) summary — duplicate_of가 ''이고 keep=true인 기사만, 한국어 한 문장"
        "(40~80자). 읽는 사람은 포르투갈어·영어를 편하게 읽지 못한다 — 요약만 "
        "읽고 내용을 파악할 수 있어야 한다. 본문을 반영하고 제목 직역은 "
        "피하라. 회사·기관·표준 이름은 원문 표기 유지 (ATSC 3.0, Anatel, "
        "Globo, Sinclair, NAB 등). 본문이 없으면 제목의 확실한 사실만 쓰라.\n\n"
        "index는 위 목록의 번호를 그대로 쓴다."
    )

    # CLI first: locally and in CI (CLAUDE_CODE_OAUTH_TOKEN) it runs on the
    # Claude subscription at no extra cost; the metered API key is the fallback.
    text = _via_cli(prompt) or _via_api(prompt)
    if not text:
        print("  no LLM available (claude CLI / ANTHROPIC_API_KEY) "
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
                   seen: dict, recent_reps: list[dict]
                   ) -> tuple[list, list, list]:
    """Fold verdicts into the ledger. Returns (kept, excluded, folded).

    kept: [(item, summary, [related_meta...])] — new representatives;
    related articles from the same batch ride along under them.
    excluded: [{title, link, source, reason}] — vetted out, with the reason.
    folded: [{title, link, source, rep_title}] — grouped under a rep that is
    NOT in this batch (usually an already-reported story), so they would
    otherwise vanish from the digest without a trace.
    """
    kept: dict[str, tuple[dict, str, list]] = {}   # rep_key -> entry
    excluded: list[dict] = []
    folded: list[dict] = []

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
            excluded.append({**item_meta(it),
                             "reason": v.get("drop_reason", "") or "기준 미달"})
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
            else:                         # rep already reported — show as ♻️
                rep_meta = seen["reps"].get(rep_key, {})
                folded.append({**item_meta(it),
                               "rep_title": rep_meta.get("title", "")})
        else:
            summary = v["summary"].strip()
            # 📊 = carries official slides/figures — the articles worth
            # opening, per the reader.
            if v.get("has_figures") and summary and "📊" not in summary:
                summary = "📊 " + summary
            seen["reps"][key] = item_meta(it)
            if summary:
                seen["summaries"][key] = summary
            kept[key] = (it, summary, [])
    return list(kept.values()), excluded, folded


# ---------------------------------------------------------------------------
# Rendering: Telegram + the page itself
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def outlet(source: str) -> str:
    """'와우테일 · KR' -> '와우테일' (for the compact related-articles line)."""
    return source.split(" · ")[0]


def related_line_html(rels: list[dict]) -> str:
    rows = "<br>".join(
        f'· <a href="{esc(m["link"])}" target="_blank" rel="noopener">'
        f'{esc(m["title"])}</a> ({esc(outlet(m["source"]))})'
        for m in rels)
    return f'<div class="tl-related">관련기사 {len(rels)}<br>{rows}</div>'


def keyword_digest(report: dict) -> str:
    """This run's query-evolution changes (with reasons), plus totals.

    The full query list is in scripts/rtk_news_queries.json — the digest
    reports what CHANGED, the way a human editor would."""
    try:
        store = json.loads(QUERIES_FILE.read_text(encoding="utf-8"))
    except Exception:
        store = {}
    seeds = store.get("seeds", [])
    learned = [q for q in store.get("learned", []) if q.get("enabled", True)]
    feeds = [f for f in store.get("feeds", []) if f.get("enabled", True)]
    boards = [w for w in store.get("watch_pages", [])
              if w.get("enabled", True)]
    head = f"🔎 <b>검색 키워드</b> — 시드 {len(seeds)} · 학습 {len(learned)}"
    if feeds:
        head += f" · 매체 {len(feeds)}"
    if boards:
        head += f" · 게시판 {len(boards)}"

    lines = []
    for q in report.get("queries_added", []):
        lines.append(f'➕ 추가: <code>[{q["region"]}] {esc(q["q"])}</code>')
        if q.get("why"):
            lines.append(f'   이유: {esc(q["why"])}')
    for q in report.get("queries_disabled", []):
        lines.append(f'➖ 비활성화: <code>[{q["region"]}] {esc(q["q"])}</code>'
                     f' — {q.get("misses", "?")}회 연속 무수확')
    if report.get("evolve_note"):
        lines.append(f'⚠️ {esc(report["evolve_note"])}')
    if not lines:
        lines.append("변경 없음")
    out = head + "\n" + "\n".join(lines)

    # 누적 태그 — 기사들이 스스로 말해주는 다음 진화 후보
    try:
        tags = json.loads(SEEN_FILE.read_text(encoding="utf-8")).get("tags", {})
        top = sorted(tags.values(), key=lambda e: -e["n"])[:8]
        top = [e for e in top if e["n"] >= 2]
        if top:
            out += ("\n\n🏷 <b>누적 태그</b>: "
                    + " · ".join(f'{esc(e["t"])}({e["n"]})' for e in top))
    except Exception:
        pass
    return out


def _short(title: str, n: int = 70) -> str:
    return title if len(title) <= n else title[: n - 1] + "…"


def _section_blocks(head: str, lines: list[str],
                    chunk: int = 1600) -> list[str]:
    """A section as one or more <=chunk-char blocks (long lists must not
    produce a single block over the Telegram message cap); the header is
    repeated with '계속' on continuation blocks."""
    blocks, cur = [], head
    for ln in lines:
        if cur != head and len(cur) + len(ln) + 1 > chunk:
            blocks.append(cur)
            cur = head.replace("</b>", " — 계속</b>", 1)
        cur += "\n" + ln
    blocks.append(cur)
    return blocks


def build_messages(kept: list[tuple[dict, str, list]], excluded: list[dict],
                   folded: list[dict], grouped: int, total: int,
                   report: dict) -> list[str]:
    header = f"📡 <b>Broadcast RTK 뉴스 — 신규 {len(kept)}건</b> (수집 {total}건)"
    region_counts = report.get("region_counts", {})
    if region_counts:
        header += ("\n<i>국가별 수집: "
                   + " · ".join(f"{r} {n}"
                                for r, n in sorted(region_counts.items()))
                   + "</i>")
    extras = []
    if grouped:
        extras.append(f"관련기사 묶음 {grouped}건")
    if excluded:
        extras.append(f"제외 {len(excluded)}건")
    if extras:
        header += f"\n<i>{' · '.join(extras)}</i>"
    if not kept:
        header += "\n\n새로 보낼 기사 없음."

    blocks = []
    for it, summary, rels in kept:
        parts = [f'• <a href="{esc(it["link"])}">{esc(it["title"])}</a>']
        if summary:
            parts.append(f"  {esc(summary)}")
        parts.append(f'  <i>{esc(it["source"])} · {esc(it["date"])}</i>')
        for m in rels:
            parts.append(f'  ↳ <a href="{esc(m["link"])}">'
                         f'{esc(_short(m["title"], 60))}</a> '
                         f'({esc(outlet(m["source"]))})')
        blocks.append("\n".join(parts))

    # ♻️ — an outlet re-running an already-reported story. Listed, never
    # silently swallowed (사용자 요청: 재게시도 표시해서 다시 알릴 것).
    if folded:
        lines = []
        for m in folded:
            line = (f'· <a href="{esc(m["link"])}">{esc(_short(m["title"]))}'
                    f'</a> ({esc(outlet(m["source"]))})')
            if m.get("rep_title"):
                line += f' → 기존 보도 “{esc(_short(m["rep_title"], 45))}”'
            lines.append(line)
        blocks += _section_blocks(
            f"♻️ <b>기존 보도로 묶음 {len(folded)}건</b>", lines)

    # 🚫 — every article collected but not reported, with the reason.
    if excluded:
        lines = [f'· <a href="{esc(m["link"])}">{esc(_short(m["title"]))}</a>'
                 f' ({esc(outlet(m["source"]))}) — {esc(m["reason"])}'
                 for m in excluded]
        blocks += _section_blocks(f"🚫 <b>제외 {len(excluded)}건</b>", lines)

    blocks.append(keyword_digest(report))

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
    """Rebuild the timeline data store from the ledger: drop vetted-out junk,
    fold related coverage under its representative, attach summaries."""
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


def _bigrams(s: str) -> set:
    s = norm_title(s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


SIBLING_MAX_SEARCHES = 10   # reverse lookups per run
SIBLING_MAX_HITS = 4        # related articles adopted per representative


def sibling_search(rep: dict, query: str, seen: dict) -> list[dict]:
    """유사 기사 역검색 — 대표기사의 검색어로 구글 뉴스를 되짚어, 같은 사건을
    다룬 타 매체 보도를 관련기사로 가져온다.

    Articles arriving via an outlet feed or a notice board have no query
    siblings in the collection (nothing else searched for that topic), so
    without this, coverage that every other outlet also ran would look like a
    single-outlet story. Title-bigram similarity + a date window guard
    against grouping a different story that merely matched the query.
    """
    from fetch_rtk_news import REGION_LOCALE, fetch_rss
    region = rep["source"].rsplit(" · ", 1)[-1].strip()
    # Brazilian stories are also covered by Spanish-language LatAm outlets —
    # search both locales for them.
    regions = {"BR": ["BR", "MX"]}.get(region, [region])
    items = []
    for rg in regions:
        loc = REGION_LOCALE.get(rg, REGION_LOCALE["US"])
        try:
            items += fetch_rss({"q": query, **loc, "region": rg})
        except Exception:
            continue
    if not items:
        return []
    rep_key = norm_title(rep["title"])
    rep_bg = _bigrams(rep["title"])
    try:
        rep_date = datetime.strptime(rep["date"], "%Y.%m.%d")
    except Exception:
        rep_date = None
    known = (set(seen["titles"]) | set(seen["related_members"])
             | set(seen["dropped"]) | {rep_key})
    out = []
    for it in sorted(items, key=lambda x: x["date"], reverse=True):
        key = norm_title(it["title"])
        if key in known:
            continue
        if rep_date and abs((it["date"].replace(tzinfo=None)
                             - rep_date).days) > 6:
            continue
        bg = _bigrams(it["title"])
        if len(rep_bg & bg) / max(1, len(rep_bg | bg)) < 0.18:
            continue
        out.append({"title": it["title"], "link": it["link"],
                    "source": f'{it["source"]} · {it["region"]}',
                    "date": it["date"].strftime("%Y.%m.%d")})
        known.add(key)
        if len(out) >= SIBLING_MAX_HITS:
            break
    return out


def enrich_with_siblings(kept: list, verdicts: dict[int, dict],
                         fresh: list[dict], seen: dict) -> int:
    """Reverse-search siblings for this run's new representatives."""
    sib_q = {}
    for i, v in verdicts.items():
        if v.get("keep") and not v.get("duplicate_of") \
                and v.get("sibling_query"):
            sib_q[norm_title(fresh[i]["title"])] = v["sibling_query"]
    searches = found = 0
    for it, _summary, rels in kept:
        if searches >= SIBLING_MAX_SEARCHES:
            break
        key = norm_title(it["title"])
        q = sib_q.get(key)
        if not q or len(rels) >= 2:     # already well-connected
            continue
        searches += 1
        sibs = sibling_search(it, q, seen)
        for m in sibs:
            mkey = norm_title(m["title"])
            seen["related_members"][mkey] = key
            seen["related"].setdefault(key, []).append(m)
            seen["titles"].append(mkey)
            rels.append(m)
            found += 1
    if searches:
        print(f"  sibling search: {searches} queries -> {found} related "
              f"article(s) adopted")
    return found


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

    report = load_report()
    verdicts = vet_and_summarize(fresh, recent_rep_list(seen),
                                 seen["outlets"], seen["tags"])
    kept, excluded, folded = apply_verdicts(fresh, verdicts, seen,
                                            recent_rep_list(seen))
    grouped = (len(folded) + sum(len(rels) for _, _, rels in kept)
               + enrich_with_siblings(kept, verdicts, fresh, seen))

    # Fetch-stage relevance drops — collected but never shown to the vetting
    # LLM. Listed too: the digest accounts for every collected article.
    # Each one is announced ONCE (low_reported ledger) — stock-note junk that
    # re-fetches daily must not re-clutter every digest — and drops that
    # sibling-search later adopted as related coverage are not "excluded".
    known = (set(seen["titles"]) | set(seen["related_members"])
             | set(seen["low_reported"]))
    for it in report.get("low_relevance", []):
        key = norm_title(it["title"])
        if key in known:
            continue
        known.add(key)
        seen["low_reported"].append(key)
        excluded.append({"title": it["title"], "link": it["link"],
                         "source": f'{it["source"]} · {it["region"]}',
                         "reason": "관련성 점수 미달(키워드 필터)"})

    send_telegram(build_messages(kept, excluded, folded, grouped,
                                 len(new_items), report))
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
                                              seen["outlets"], seen["tags"])
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
