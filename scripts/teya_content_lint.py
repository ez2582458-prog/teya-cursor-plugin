#!/usr/bin/env python3
"""Teya content lint: no service markup, markdown or stray Latin on the site.

Checks the text people actually see (rendered in Chromium: innerText + img alt +
title) on every page, and optionally raw source files (theme PHP/HTML seeds,
SVG) for service markers.

Findings (each one = BLOCKER):
- service/draft markers: «Секция:», «Intro», «answer-block», «cards-grid»,
  «H2:», «Абзац:», «CTA», «Related», «Visual», «E-E-A-T», «placeholder»,
  «required_blocks», «Прямой ответ», «Hello world», «Welcome to WordPress»,
  «{{…}}», «TODO», «lorem», «заглушка» …;
- markdown left in text: «**», «# Заголовок», «[текст](ссылка)»;
- Latin words in visible text that are not in the allowlist
  (default list + teya-memory/content-allowlist.txt + --allow);
- SVG <text> without letters (broken Cyrillic encoding).

Exit code: 0 = PASS, 1 = FAIL, 2 = cannot run.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from teya_browser_common import (
    default_out,
    normalize_start,
    now_iso,
    page_label,
    require_playwright,
    resolve_pages,
    write_json,
)

MARKERS = [
    (r"Секция\s*:", "service_marker"),
    (r"\bIntro\b", "service_marker"),
    (r"answer[\s_-]?block", "service_marker"),
    (r"cards?[\s_-]grid", "service_marker"),
    (r"\((?:steps|cards|text-image|faq|spec-table)\)", "service_marker"),
    (r"(?<![\w-])H[1-6]\s*:", "service_marker"),
    (r"Абзац\s*:", "service_marker"),
    (r"Карточки\s*:", "service_marker"),
    (r"\bCTA\b", "service_marker"),
    (r"\bRelated\b", "service_marker"),
    (r"\bVisual\b", "service_marker"),
    (r"E-E-A-T", "service_marker"),
    (r"placeholder", "service_marker"),
    (r"required_blocks|text_length|placeholder_scan|block_inventory", "service_marker"),
    (r"Прямой ответ", "service_marker"),
    (r"Дисклеймер\s*\(", "service_marker"),
    (r"\(\d+\s*[–-]\s*\d+\s*слов\)", "service_marker"),
    (r"Hello world|Welcome to WordPress|Just another WordPress site|Ещё один сайт на WordPress|Sample Page|Пример страницы", "wp_default_content"),
    (r"\{\{[^}]{1,60}\}\}", "template_placeholder"),
    (r"\bTODO\b|\bFIXME\b|lorem ipsum", "service_marker"),
    (r"заглушк|в разработке", "service_marker"),
    (r"\*\*", "markdown"),
    (r"(?m)^\s{0,3}#{1,6}\s+\S", "markdown"),
    (r"\[[^\]\n]{1,80}\]\((?:https?:|/)[^)\s]+\)", "markdown"),
]
# subset that is safe to search in raw PHP/HTML source after stripping tags
SOURCE_MARKER_CODES = {"Секция\\s*:", "Абзац\\s*:", "Карточки\\s*:", "Прямой ответ", "\\*\\*", "\\{\\{[^}]{1,60}\\}\\}",
                       "(?<![\\w-])H[1-6]\\s*:", "Дисклеймер\\s*\\(", "\\bIntro\\b", "E-E-A-T"}

DEFAULT_ALLOW = {
    "telegram", "whatsapp", "viber", "vk", "max", "cookie", "cookies", "wi-fi", "wifi", "led", "pdf", "gps",
    "rehau", "veka", "kbe", "salamander", "deceuninck", "schuco", "brusbox", "kaleva", "proplex", "montblanc",
    "knauf", "ceresit", "tikkurila", "technonicol", "rockwool", "isover", "grundfos", "pvc", "ii", "iii", "iv",
    "ok", "online", "id", "seo", "faq", "ip", "google", "analytics", "yandex", "android", "ios",
}
LATIN_WORD = re.compile(r"(?<![\w@./-])[A-Za-z][A-Za-z'’-]{1,}(?![\w@/])")
URLISH = re.compile(r"(?:https?://|www\.)\S+|[\w.+-]+@[\w-]+\.[\w.]+|\b[\w-]+\.(?:ru|com|рф|net|org|su|me|io)\b(?:/\S*)?", re.I)

TEXT_JS = r"""
() => {
  const parts = [document.body ? document.body.innerText : ''];
  document.querySelectorAll('body img[alt]').forEach(i => { const a = (i.getAttribute('alt') || '').trim(); if (a) parts.push('〔подпись картинки〕 ' + a); });
  document.querySelectorAll('body [title]').forEach(e => { const t = (e.getAttribute('title') || '').trim(); if (t) parts.push('〔всплывающая подсказка〕 ' + t); });
  parts.push('〔заголовок вкладки〕 ' + document.title);
  const md = document.querySelector('meta[name="description"]');
  if (md) parts.push('〔описание для поиска〕 ' + md.getAttribute('content'));
  return parts.join('\n');
}
"""


def load_allow(project_root: str | None, extra: list[str] | None) -> set[str]:
    allow = set(DEFAULT_ALLOW)
    if project_root:
        p = Path(project_root) / "teya-memory" / "content-allowlist.txt"
        if p.is_file():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    allow.add(line.lower())
    for item in extra or []:
        allow.update(x.strip().lower() for x in item.split(",") if x.strip())
    return allow


def context(text: str, start: int, end: int) -> str:
    return text[max(0, start - 40):min(len(text), end + 40)].replace("\n", " ⏎ ").strip()


def scan_text(text: str, allow: set[str], latin: bool, marker_filter: set[str] | None = None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for pattern, code in MARKERS:
        if marker_filter is not None and pattern not in marker_filter:
            continue
        for m in re.finditer(pattern, text, flags=re.I if code != "markdown" and "CTA" not in pattern and "Intro" not in pattern and "Visual" not in pattern and "Related" not in pattern else 0):
            findings.append({"code": code, "match": m.group(0), "context": context(text, m.start(), m.end())})
    if latin:
        cleaned = URLISH.sub(" ", text)
        for m in LATIN_WORD.finditer(cleaned):
            word = m.group(0).strip("'’-")
            if len(word) < 2 or word.lower() in allow:
                continue
            findings.append({"code": "latin_text", "match": word, "context": context(cleaned, m.start(), m.end())})
    uniq: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for f in findings:
        key = (f["code"], f["match"].lower())
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


def strip_source(raw: str, suffix: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", raw, flags=re.S)
    text = re.sub(r"(?m)^\s*(//|#(?!\s*\S*\s*\{)).*$", " ", text) if suffix == ".php" else text
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def svg_garbled(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    out = []
    for m in re.finditer(r"<text[^>]*>(.*?)</text>", raw, flags=re.S):
        inner = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        letters = re.findall(r"[A-Za-zА-Яа-яЁё]", inner)
        if inner and (len(letters) < max(1, len(inner.replace(" ", "")) // 2) or "\ufffd" in inner):
            out.append({"code": "svg_text_garbled", "match": inner[:40], "context": f"{path.name}: <text>{inner[:60]}</text>"})
    return out


def scan_sources(paths: list[str]) -> list[dict[str, Any]]:
    results = []
    files: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files += [f for f in p.rglob("*") if f.suffix.lower() in {".php", ".html", ".svg", ".json"} and "node_modules" not in f.parts and "vendor" not in f.parts]
        elif p.is_file():
            files.append(p)
    for f in files:
        if f.suffix.lower() == ".svg":
            found = svg_garbled(f)
        elif f.suffix.lower() == ".json":
            continue
        else:
            text = strip_source(f.read_text(encoding="utf-8", errors="replace"), f.suffix.lower())
            found = scan_text(text, set(), latin=False, marker_filter=SOURCE_MARKER_CODES)
        if found:
            results.append({"source": str(f), "findings": found})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Teya content lint (service markup, markdown, Latin).")
    parser.add_argument("--url", help="Site start URL / file:// / static mirror dir (rendered text check)")
    parser.add_argument("--pages", nargs="*")
    parser.add_argument("--urls-file")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--paths", nargs="*", help="Source files/dirs to scan (theme, mu-plugins, seeds, svg)")
    parser.add_argument("--allow", action="append", help="Comma-separated extra allowed Latin words")
    parser.add_argument("--no-latin", action="store_true")
    parser.add_argument("--project-root")
    parser.add_argument("--out")
    args = parser.parse_args()
    if not args.url and not args.paths:
        parser.error("give --url and/or --paths")

    out = Path(args.out) if args.out else default_out(args.project_root, "content-lint.json")
    allow = load_allow(args.project_root, args.allow)
    page_results: list[dict[str, Any]] = []
    if args.url:
        start = normalize_start(args.url)
        sync_playwright = require_playwright()
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            pages = resolve_pages(browser, start, args.pages, args.urls_file, args.limit)
            ctx = browser.new_context()
            page = ctx.new_page()
            for url in pages:
                label = page_label(url, start)
                try:
                    page.goto(url, wait_until="load", timeout=60000)
                    text = page.evaluate(TEXT_JS)
                    found = scan_text(text, allow, latin=not args.no_latin)
                except Exception as exc:  # noqa: BLE001
                    found = [{"code": "page_error", "match": "", "context": str(exc)[:200]}]
                page_results.append({"page": label, "url": url, "findings": found})
                print(f"{label}: {len(found)} finding(s)")
            ctx.close()
            browser.close()
    source_results = scan_sources(args.paths) if args.paths else []
    count = sum(len(r["findings"]) for r in page_results) + sum(len(r["findings"]) for r in source_results)
    checked = len(page_results) + (1 if args.paths else 0)
    report = {
        "tool": "teya_content_lint",
        "checked_at": now_iso(),
        "start_url": args.url,
        "finding_count": count,
        "verdict": "pass" if checked and count == 0 else "fail",
        "pages": page_results,
        "sources": source_results,
    }
    write_json(out, report)
    lines = ["# Content lint (служебная разметка, markdown, латиница)", "",
             f"**Verdict:** {'PASS' if report['verdict'] == 'pass' else '❌ FAIL'}  ", f"**Findings:** {count}", ""]
    for r in page_results:
        for f in r["findings"]:
            lines.append(f"- `{r['page']}` **{f['code']}** «{f['match']}» — …{f['context']}…")
    for r in source_results:
        for f in r["findings"]:
            lines.append(f"- `{r['source']}` **{f['code']}** «{f['match']}» — …{f['context'][:120]}…")
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"CONTENT LINT {'PASS' if report['verdict'] == 'pass' else 'FAIL'}: {count} finding(s) → {out}")
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
