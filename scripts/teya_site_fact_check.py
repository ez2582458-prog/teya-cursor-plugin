#!/usr/bin/env python3
"""Teya site-wide fact check.

Collects factual claims from the rendered site (visible text, alt, title, SVG <text>)
and optionally from theme/source files (--paths), then verifies each claim against
the project's sources of truth: teya-memory/00-brief.md, teya-memory/site.inv
(non-secret lines only), teya-memory/research/fact-bank.md (sections marked as
"not confirmed" are ignored) and any extra --sources.

Claims: years («с 2015», «основана в 2010», «2019 г.»), experience («более 15 лет»),
counts («500 объектов», «20 специалистов»), percentages, prices, guarantees,
licences / СРО / certificates / awards / ratings.

Verdicts:
  pass       — claims found and every claim is confirmed by a source;
  no_claims  — nothing factual found (NOT a pass: report says "0 facts checked");
  fail       — at least one claim is not confirmed, or there are no sources at all.
Exit: 0 pass/no_claims, 1 fail, 2 cannot run.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from teya_browser_common import (  # noqa: E402
    default_out,
    normalize_start,
    now_iso,
    page_label,
    require_playwright,
    resolve_pages,
    write_json,
)

CURRENT_YEAR = _dt.date.today().year
MONTHS = r"(?:январ|феврал|март|апрел|ма[йя]|июн|июл|август|сентябр|октябр|ноябр|декабр)\w*"

TEXT_JS = r"""
() => {
  const parts = [document.body ? document.body.innerText : ''];
  document.querySelectorAll('body img[alt]').forEach(i => { const a=(i.getAttribute('alt')||'').trim(); if (a) parts.push(a); });
  document.querySelectorAll('body [title]').forEach(e => { const t=(e.getAttribute('title')||'').trim(); if (t) parts.push(t); });
  document.querySelectorAll('svg text, svg textPath').forEach(t => { const s=(t.textContent||'').trim(); if (s) parts.push(s); });
  document.querySelectorAll('[aria-label]').forEach(e => { const s=(e.getAttribute('aria-label')||'').trim(); if (/\d/.test(s)) parts.push(s); });
  parts.push(document.title || '');
  const md = document.querySelector('meta[name="description"]');
  if (md) parts.push(md.getAttribute('content') || '');
  document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
    const t = s.textContent || '';
    const fd = t.match(/"foundingDate"\s*:\s*"(\d{4})/); if (fd) parts.push('Основана в ' + fd[1] + ' году (JSON-LD foundingDate)');
    const ne = t.match(/"numberOfEmployees"[^0-9]{0,60}(\d+)/); if (ne) parts.push(ne[1] + ' сотрудников (JSON-LD numberOfEmployees)');
    const rv = t.match(/"ratingValue"\s*:\s*"?([\d.]+)/); if (rv) parts.push('рейтинг ' + rv[1] + ' из 5 (JSON-LD aggregateRating)');
  });
  return parts.join('\n');
}
"""

SVG_IMG_JS = r"""
() => Array.from(new Set(Array.from(document.querySelectorAll('img, object, use, image'))
  .map(e => e.currentSrc || e.src || e.data || e.getAttribute('href') || e.getAttribute('xlink:href') || '')
  .filter(u => /\.svg(\?|#|$)/i.test(u)).map(u => new URL(u, location.href).href.split('#')[0])))
"""

SECRET_KEY = re.compile(r"(pass|pwd|token|secret|key|login|user|credential|ftp|ssh|api)", re.I)
UNCONFIRMED_HEADING = re.compile(r"(не\s*подтвержд|not[_ ]confirmed|needs[_ ]user[_ ]fact|нельзя|запрещ|не\s*использовать|гипотез)", re.I)

# Things that look like numbers but are not claims.
NOISE = [
    re.compile(r"\+?[78][\s\-(]*\d{3}[\s\-)]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}"),       # phones
    re.compile(r"\b(?:ИНН|КПП|ОГРН|ОКПО|БИК|р/с|к/с|ОКВЭД)\s*:?\s*[\d\s.]+", re.I),  # requisites
    re.compile(r"\b\d{6},?\s*(?:г\.\s*)?(?=[А-ЯЁ])"),                               # postal index
    re.compile(r"\b\d{1,2}[:.]\d{2}\s*[–—-]\s*\d{1,2}[:.]\d{2}"),                   # hours
    re.compile(r"\b\d{1,2}\s+" + MONTHS + r"\s+\d{4}", re.I),                        # dates
    re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b"),                                    # dd.mm.yyyy
    re.compile(r"©\s*(?:\d{4}\s*[–—-]\s*)?\d{4}"),                                   # copyright
    re.compile(r"\b\d+\s*-?\s*ФЗ\b|№\s*\d[\d\-/]*|\bст\.\s*\d+|\bп\.\s*\d+|\bч\.\s*\d+", re.I),  # laws
    re.compile(r"\b(?:СП|СНиП|ГОСТ|ТР ТС)\s*[\d.\-–]+", re.I),                     # norms (checked separately? no)
    re.compile(r"\bшаг\s*\d+|\b\d+\.\s(?=[А-ЯЁ])", re.I),                             # list numbering
]

CLAIMS: list[tuple[str, re.Pattern[str]]] = [
    ("since_year", re.compile(r"(?:\bс|\bсо|основан\w*\s+в|работаем\s+с|на\s+рынке\s+с|since|с\s+момента\s+основания\s+в)\s+(19[5-9]\d|20[0-4]\d)\s*(?:г\.?|года?)?", re.I)),
    ("experience", re.compile(r"(?:более|свыше|больше|около|почти|уже)?\s*(\d{1,3})\s*\+?\s*(?:лет|года?)\s+(?:опыт\w*|на\s+рынке|работ\w*|в\s+(?:ремонт|строител|отрасл|професс)\w*|практик\w*|успешн\w*)", re.I)),
    ("experience", re.compile(r"(?:опыт\w*|стаж\w*)\s+(?:работы\s+)?(?:более|свыше|от|больше)?\s*(\d{1,3})\s*\+?\s*(?:лет|года?)", re.I)),
    ("count", re.compile(r"(?:более|свыше|больше|около|уже)?\s*(\d[\d\s\u00a0]{0,7}\d|\d)\s*\+?\s*(объект\w*|проект\w*|клиент\w*|заказчик\w*|сотрудник\w*|специалист\w*|мастер\w*|бригад\w*|квартир\w*|дом\w*|фасад\w*|кровл\w*|отзыв\w*|м²|м2|кв\.?\s?м)", re.I)),
    ("percent", re.compile(r"(\d{1,3}(?:[.,]\d+)?)\s*%")),
    ("price", re.compile(r"(?:от|до)?\s*(\d[\d\s\u00a0]{0,9}\d|\d)\s*(?:₽|руб\w*|р\.(?!\s*ф)|\$|usd|€|евро)", re.I)),
    ("guarantee", re.compile(r"гаранти\w*\s+(?:качества\s+)?(?:до|на|от)?\s*(\d{1,3})\s*(?:лет|года?|мес\w*)", re.I)),
    ("guarantee", re.compile(r"(\d{1,3})\s*(?:лет|года?|мес\w*)\s+гаранти\w*", re.I)),
    ("year", re.compile(r"\b(19[5-9]\d|20[0-4]\d)\s*(?:г\.|год\w*)", re.I)),
    ("rating", re.compile(r"(?:рейтинг\w*|оценк\w*)\s*(\d(?:[.,]\d)?)\s*(?:/|из)\s*5", re.I)),
]
KEYWORD_CLAIMS = [
    ("licence", re.compile(r"\b(СРО\b|лицензи\w+|допуск\w* СРО|сертифика\w+|аккредитац\w+|ISO\s*\d+)", re.I)),
    ("award", re.compile(r"\b(наград\w+|лауреат\w*|победител\w+|премия\w*|диплом\w*|top[-\s]?\d+|топ[-\s]?\d+)", re.I)),
    ("partner", re.compile(r"\b(официальн\w+\s+(?:дилер|партн[её]р|представител)\w*)", re.I)),
]
FIRST_PERSON = re.compile(r"\b(мы|нас|наш\w*|имеем|облада\w*|состоим|являемся|входим|член\w*|компания\s+имеет)\b", re.I)
NEGATION = re.compile(r"\b(не|нет|без|ни)\b[^.!?\n]{0,40}$", re.I)


def project_root(arg: str | None) -> Path:
    if arg:
        return Path(arg).resolve()
    here = Path(__file__).resolve()
    for cand in [Path.cwd(), *Path.cwd().parents, *here.parents]:
        if (cand / "teya-memory").is_dir():
            return cand
    return Path.cwd()


def strip_unconfirmed(md: str) -> str:
    out, skip_level = [], None
    for line in md.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and UNCONFIRMED_HEADING.search(m.group(2)):
                skip_level = level
                continue
        if skip_level is None:
            # single lines/table rows that explicitly say "not confirmed" do not count
            if UNCONFIRMED_HEADING.search(line) and "|" in line:
                continue
            out.append(line)
    return "\n".join(out)


def load_sources(root: Path, extra: list[str] | None) -> tuple[str, list[str]]:
    mem = root / "teya-memory"
    cands = [mem / "00-brief.md", mem / "site.inv", mem / "research" / "fact-bank.md",
             mem / "research" / "fact-bank.json", mem / "brief.md"]
    cands += [Path(p) for p in (extra or [])]
    texts, used = [], []
    for p in cands:
        if not p.is_file():
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        if p.name.startswith("site.inv"):
            raw = "\n".join(l for l in raw.splitlines() if not SECRET_KEY.search(l.split("=", 1)[0].split(":", 1)[0]))
        elif p.suffix == ".md":
            raw = strip_unconfirmed(raw)
        texts.append(raw)
        used.append(str(p))
    return "\n".join(texts), used


def norm(s: str) -> str:
    s = s.lower().replace("\u00a0", " ").replace("ё", "е")
    s = re.sub(r"(?<=\d)[\s\u202f](?=\d{3}\b)", "", s)
    return re.sub(r"\s+", " ", s)


def clean_noise(text: str) -> str:
    for rx in NOISE:
        text = rx.sub(" ", text)
    return text


def context(text: str, start: int, end: int, width: int = 60) -> str:
    return text[max(0, start - width):end + width].replace("\n", " ⏎ ").strip()


BARE_YEAR = re.compile(r"(?<![\d.])(19[5-9]\d|20[0-4]\d)(?![\d.])")


def extract_claims(text: str, strict: bool = False) -> list[dict[str, Any]]:
    """strict=True for SVG / badge / seal text: any year there is a claim («с 2008» on a seal)."""
    text = clean_noise(text.replace("\u00a0", " "))
    found: list[dict[str, Any]] = []
    taken: list[tuple[int, int]] = []
    claims = CLAIMS + ([("year", BARE_YEAR)] if strict else [])
    for kind, rx in claims:
        for m in rx.finditer(text):
            s, e = m.span()
            if any(a <= s < b or a < e <= b for a, b in taken):
                continue
            value = re.sub(r"\s+", "", m.group(1))
            if kind in ("count", "price") and value in {"0", "1"}:
                continue
            if kind == "year" and not strict and int(value) >= CURRENT_YEAR - 1 and not re.search(r"\b(?:с|основан)", text[max(0, s - 20):s], re.I):
                # current/previous year in plain text (e.g. "цены 2026 г.") is not a company claim
                continue
            taken.append((s, e))
            found.append({"kind": kind, "value": value, "claim": m.group(0).strip(), "context": context(text, s, e)})
    for kind, rx in KEYWORD_CLAIMS:
        for m in rx.finditer(text):
            before = text[max(0, m.start() - 60):m.start()]
            if NEGATION.search(before.split("\n")[-1]):
                continue  # «без выдуманных лицензий», «нет СРО» — not a claim
            sent_start = max(text.rfind(".", 0, m.start()), text.rfind("\n", 0, m.start()), text.rfind("?", 0, m.start())) + 1
            ends = [i for i in (text.find(".", m.end()), text.find("\n", m.end()), text.find("?", m.end())) if i != -1]
            sentence = text[sent_start:min(ends) if ends else len(text)]
            if not FIRST_PERSON.search(sentence):
                continue  # general mention («лицензия Минкультуры нужна подрядчику»), not a claim about the company
            found.append({"kind": kind, "value": m.group(1).lower(), "claim": m.group(0).strip(),
                          "context": context(text, m.start(), m.end())})
    return found


def verify(claim: dict[str, Any], src: str) -> tuple[bool, str]:
    if not src:
        return False, "нет источников (бриф / fact-bank) для сверки"
    value = norm(claim["value"])
    if claim["kind"] in ("licence", "award", "partner"):
        stem = value[:6]
        if stem and stem in src and not re.search(r"(без|не|нет|запрещ)[^.\n]{0,160}" + re.escape(stem), src):
            return True, f"«{stem}…» есть в источниках"
        return False, "упоминание лицензии/СРО/наград/партнёрства не подтверждено брифом или fact-bank"
    claim_n = norm(claim["claim"])
    if claim_n in src:
        return True, "формулировка найдена в источниках"
    if value and re.search(r"(?<![\d])" + re.escape(value) + r"(?![\d])", src):
        if claim["kind"] in ("since_year", "year", "experience", "guarantee", "percent", "rating"):
            # number must appear near a related word in the sources
            near = {"since_year": r"(с|основ|год|г\.|работ|рынк)", "year": r"(год|г\.|основ|с )",
                    "experience": r"(лет|год|опыт|стаж)", "guarantee": r"(гарант|лет|год|мес)",
                    "percent": r"%|процент", "rating": r"(рейтинг|оценк|/5|из 5)"}[claim["kind"]]
            for m in re.finditer(r"(?<![\d])" + re.escape(value) + r"(?![\d])", src):
                win = src[max(0, m.start() - 40):m.end() + 40]
                if re.search(near, win):
                    return True, f"число {value} есть в источниках рядом с подходящим словом"
            return False, f"число {value} в источниках есть, но не в этом смысле"
        return True, f"число {value} есть в источниках"
    return False, f"«{claim['claim']}» нет ни в брифе, ни в fact-bank"


def svg_text(svg: str) -> str:
    parts = re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S | re.I)
    parts += re.findall(r"<(?:title|desc)[^>]*>(.*?)</(?:title|desc)>", svg, re.S | re.I)
    return "\n".join(re.sub(r"<[^>]+>", " ", p) for p in parts)


def fetch_text(ctx, url: str) -> str:
    try:
        if url.startswith("file://"):
            from urllib.parse import unquote, urlparse
            return Path(unquote(urlparse(url).path)).read_text(encoding="utf-8", errors="replace")
        resp = ctx.request.get(url, timeout=20000)
        return resp.text() if resp.ok else ""
    except Exception:  # noqa: BLE001
        return ""


def scan_paths(paths: list[str]) -> list[dict[str, Any]]:
    res = []
    for raw in paths:
        p = Path(raw)
        files = [f for f in p.rglob("*") if f.suffix.lower() in {".svg", ".php", ".html"}
                 and "vendor" not in f.parts and "node_modules" not in f.parts] if p.is_dir() else [p]
        for f in files:
            if not f.is_file():
                continue
            t = f.read_text(encoding="utf-8", errors="replace")
            if f.suffix.lower() == ".svg":
                t = svg_text(t)
            else:
                t = re.sub(r"<\?php.*?\?>", " ", t, flags=re.S)
                t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
                t = re.sub(r"<[^>]+>", " ", t)
                t = re.sub(r"\b(?:width|height|viewBox|x|y|r|cx|cy)=\S+", " ", t)
            if t.strip():
                res.append((str(f), t))
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Site-wide fact check against brief / site.inv / fact-bank.")
    ap.add_argument("--url", help="Site URL, file:// or static mirror dir")
    ap.add_argument("--pages", nargs="*")
    ap.add_argument("--urls-file")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--paths", nargs="*", help="Theme / SVG / seed files to scan as well")
    ap.add_argument("--sources", nargs="*", help="Extra source-of-truth files")
    ap.add_argument("--project-root")
    ap.add_argument("--out")
    args = ap.parse_args()
    if not args.url and not args.paths:
        ap.error("give --url and/or --paths")

    root = project_root(args.project_root)
    src_raw, used = load_sources(root, args.sources)
    src = norm(src_raw)
    out = Path(args.out) if args.out else default_out(str(root), "site-fact-check.json")

    units: list[tuple[str, str, str, bool]] = []  # (where, url, text, strict)
    svg_seen: set[str] = set()
    if args.url:
        start = normalize_start(args.url)
        sync_playwright = require_playwright()
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            pages = resolve_pages(browser, start, args.pages, args.urls_file, args.limit)
            ctx = browser.new_context()
            page = ctx.new_page()
            for url in pages:
                try:
                    page.goto(url, wait_until="load", timeout=60000)
                    units.append((page_label(url, start), url, page.evaluate(TEXT_JS), False))
                    for svg_url in page.evaluate(SVG_IMG_JS):
                        if svg_url in svg_seen:
                            continue
                        svg_seen.add(svg_url)
                        body = fetch_text(ctx, svg_url)
                        if body:
                            units.append((f"svg:{svg_url.rsplit('/', 1)[-1]}", svg_url, svg_text(body), True))
                except Exception as exc:  # noqa: BLE001
                    print(f"page error {url}: {exc}", file=sys.stderr)
            ctx.close()
            browser.close()
    for f, t in scan_paths(args.paths or []):
        units.append((f, "", t, f.lower().endswith(".svg")))

    claims_all: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for where, url, text, strict in units:
        for c in extract_claims(text, strict=strict):
            key = (c["kind"], norm(c["claim"]))
            ok, why = verify(c, src)
            c.update({"where": where, "url": url, "verified": ok, "reason": why})
            if key in seen:
                c["duplicate"] = True
            seen.add(key)
            claims_all.append(c)

    uniq = [c for c in claims_all if not c.get("duplicate")]
    unverified = [c for c in uniq if not c["verified"]]
    if not used:
        verdict = "fail"
    elif not uniq:
        verdict = "no_claims"
    else:
        verdict = "fail" if unverified else "pass"
    report = {
        "tool": "teya_site_fact_check",
        "checked_at": now_iso(),
        "start_url": args.url,
        "sources": used,
        "units_checked": len(units),
        "claims_total": len(uniq),
        "claims_verified": len(uniq) - len(unverified),
        "claims_unverified": len(unverified),
        "verdict": verdict,
        "claims": claims_all,
    }
    write_json(out, report)
    lines = ["# Сверка фактов по всему сайту", "",
             f"**Verdict:** {'PASS' if verdict == 'pass' else ('NO_CLAIMS (фактов не найдено — это не PASS)' if verdict == 'no_claims' else '❌ FAIL')}  ",
             f"**Источники:** {', '.join(used) if used else '❌ нет (бриф/fact-bank не найдены)'}  ",
             f"**Проверено страниц/файлов:** {len(units)} · **утверждений:** {len(uniq)} · **не подтверждено:** {len(unverified)}", ""]
    if unverified:
        lines += ["## Не подтверждено (убрать с сайта или внести источник в fact-bank)", ""]
        for c in unverified:
            where = sorted({x["where"] for x in claims_all if x["kind"] == c["kind"] and norm(x["claim"]) == norm(c["claim"])})
            lines.append(f"- **{c['kind']}** «{c['claim']}» — {c['reason']}; где: {', '.join(where)}; …{c['context']}…")
    ok = [c for c in uniq if c["verified"]]
    if ok:
        lines += ["", "## Подтверждено", ""] + [f"- {c['kind']} «{c['claim']}» — {c['reason']}" for c in ok]
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"SITE FACT CHECK {verdict.upper()}: {len(uniq)} claim(s), {len(unverified)} unverified → {out}")
    return 1 if verdict == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
