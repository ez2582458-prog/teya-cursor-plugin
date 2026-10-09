#!/usr/bin/env python3
"""Teya visual lint: automatic layout checks on real browser renders.

For every page and viewport (1440 / 768 / 375 by default) the script opens the
page in Chromium, scrolls it top-to-bottom (fires lazy-load and scroll-reveal
animations), takes a full-page screenshot and checks:

- horizontal overflow (page wider than the viewport);
- H1 overlapping images / text / buttons;
- headings touching the viewport edge or breaking a word across lines;
- content left invisible (opacity 0 / visibility hidden) after scrolling;
- content invisible with JavaScript disabled (motion must not hide content);
- dropdown sub-menus rendered open without hover;
- body text < 16px, any content text < 12px;
- broken images;
- large empty bands on the full-page screenshot.

The verdict is computed by the script. Agents must not edit it.

Usage:
  python3 teya/scripts/teya_visual_lint.py --url https://example.ru/ --project-root .
  python3 teya/scripts/teya_visual_lint.py --url http://127.0.0.1:8080/ --pages / /uslugi/
  python3 teya/scripts/teya_visual_lint.py --url /tmp/preview   # static mirror (index.html)
Exit code: 0 = PASS, 1 = FAIL, 2 = cannot run.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from teya_browser_common import (
    VIEWPORTS,
    default_out,
    normalize_start,
    now_iso,
    page_label,
    require_playwright,
    resolve_pages,
    scroll_through,
    write_json,
)

CHECK_JS = r"""
() => {
  const vw = document.documentElement.clientWidth;
  const vh = window.innerHeight;
  const out = {issues: [], warnings: [], metrics: {}};
  const add = (code, message, samples) => out.issues.push({code, message, samples: (samples || []).slice(0, 5)});
  const warn = (code, message, samples) => out.warnings.push({code, message, samples: (samples || []).slice(0, 5)});
  const CHROME = 'header, nav, footer, dialog, [role=dialog], [aria-hidden="true"], [hidden], details:not([open]) > :not(summary), [class*="cookie"], [id*="cookie"], .screen-reader-text, .sr-only, noscript, template, [class*="skip-link"]';
  const desc = el => {
    if (!el || !el.tagName) return '';
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const cls = (typeof el.className === 'string' ? el.className : '').trim().split(/\s+/).filter(Boolean).slice(0, 2);
    if (cls.length) s += '.' + cls.join('.');
    const t = (el.innerText || el.getAttribute('alt') || '').trim().replace(/\s+/g, ' ').slice(0, 60);
    return t ? s + ' «' + t + '»' : s;
  };
  const effOpacity = el => {
    let o = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || cs.contentVisibility === 'hidden') return 0;
      o *= parseFloat(cs.opacity || '1');
    }
    return o;
  };
  const isRendered = el => { const r = el.getBoundingClientRect(); return r.width > 1 && r.height > 1; };
  const inChrome = el => !!el.closest(CHROME);
  const textRect = el => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const rects = Array.from(range.getClientRects()).filter(r => r.width > 0 && r.height > 0);
    if (!rects.length) return el.getBoundingClientRect();
    const left = Math.min(...rects.map(r => r.left)), right = Math.max(...rects.map(r => r.right));
    const top = Math.min(...rects.map(r => r.top)), bottom = Math.max(...rects.map(r => r.bottom));
    return {left, right, top, bottom, width: right - left, height: bottom - top};
  };
  const scrollW = Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0);
  out.metrics.viewport_width = vw;
  out.metrics.scroll_width = scrollW;

  // 1. horizontal overflow
  if (scrollW > vw + 2) {
    const offenders = [];
    document.querySelectorAll('body *').forEach(el => {
      if (offenders.length > 8) return;
      const r = el.getBoundingClientRect();
      if (r.right > vw + 2 && r.width > 0 && effOpacity(el) > 0.05) {
        const parent = el.parentElement && el.parentElement.getBoundingClientRect();
        if (!parent || parent.right <= vw + 2) offenders.push(desc(el) + ' right=' + Math.round(r.right));
      }
    });
    add('horizontal_overflow', `Страница шире экрана: ${scrollW}px при ширине ${vw}px`, offenders);
  }

  // 2. hidden content after scroll (opacity 0 / visibility hidden)
  const main = document.querySelector('main') || document.body;
  const hidden = [];
  main.querySelectorAll('h1, h2, h3, p, li, img, figure, blockquote, table').forEach(el => {
    if (inChrome(el)) return;
    const own = el.tagName === 'IMG' ? 'img' : (el.innerText || '').trim();
    if (el.tagName !== 'IMG' && own.length < 15) return;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    if (effOpacity(el) < 0.05) hidden.push(desc(el));
  });
  out.metrics.hidden_blocks = hidden.length;
  if (hidden.length) add('hidden_content', `${hidden.length} блок(ов) контента невидимы после прокрутки (opacity 0 / visibility hidden)`, hidden);

  // 3. open dropdown sub-menus without hover
  const openMenus = [];
  document.querySelectorAll('.sub-menu, .children, nav ul ul, [class*="dropdown-menu"], [class*="submenu"], [class*="sub-menu"]').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.height < 4 || r.width < 4) return;
    if (r.right < 0 || r.left > vw || r.bottom < 0) return;
    if (effOpacity(el) < 0.05) return;
    if (getComputedStyle(el).clipPath && getComputedStyle(el).clipPath.includes('inset(50%')) return;
    const toggle = el.closest('[aria-expanded="true"], .is-open, .open, .toggled, [class*="menu-open"]');
    if (toggle) return;
    openMenus.push(desc(el));
  });
  if (openMenus.length) add('submenu_open', 'Выпадающее подменю показано раскрытым без наведения', openMenus);

  // 4. font sizes
  const bodyFs = parseFloat(getComputedStyle(document.body).fontSize);
  out.metrics.body_font_px = bodyFs;
  if (bodyFs < 16) add('body_font_small', `Основной шрифт body ${bodyFs}px (нужно ≥16px)`, []);
  const smallMain = [], tiny = [];
  main.querySelectorAll('p, li, td, dd, blockquote').forEach(el => {
    if (inChrome(el) || !isRendered(el) || effOpacity(el) < 0.05) return;
    if (el.closest('figcaption, small, .caption, [class*="caption"], [class*="meta"], [class*="label"], [class*="eyebrow"], [class*="kicker"], [class*="breadcrumb"]')) return;
    if ((el.innerText || '').trim().length < 40) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 16) smallMain.push(desc(el) + ' ' + fs + 'px');
  });
  if (smallMain.length) add('content_font_small', `${smallMain.length} абзац(ев) основного текста мельче 16px`, smallMain);
  document.querySelectorAll('body *').forEach(el => {
    if (tiny.length > 10) return;
    if (!el.firstChild || ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2)) return;
    if (!isRendered(el) || effOpacity(el) < 0.05 || el.closest('.screen-reader-text, .sr-only, [aria-hidden="true"]')) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 12) tiny.push(desc(el) + ' ' + fs + 'px');
  });
  if (tiny.length) add('text_too_small', `Текст мельче 12px`, tiny);

  // 5. broken images
  const broken = [];
  document.querySelectorAll('img').forEach(img => {
    if (!isRendered(img) || effOpacity(img) < 0.05) return;
    if (img.complete && img.naturalWidth === 0) broken.push(desc(img) + ' src=' + (img.currentSrc || img.src).slice(-80));
  });
  if (broken.length) add('broken_image', `${broken.length} картинок не загрузилось`, broken);

  // 6. headings: edges, split words
  const edge = [], split = [];
  document.querySelectorAll('h1, h2').forEach(h => {
    if (!isRendered(h) || effOpacity(h) < 0.05 || inChrome(h)) return;
    const tr = textRect(h);
    if (tr.left < 8 || tr.right > vw - 8) edge.push(desc(h) + ` left=${Math.round(tr.left)} right=${Math.round(tr.right)}`);
    const walker = document.createTreeWalker(h, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const re = /[^\s\u00a0\u00ad-]{4,}/g;
      let m;
      while ((m = re.exec(node.textContent))) {
        const range = document.createRange();
        range.setStart(node, m.index);
        range.setEnd(node, m.index + m[0].length);
        const tops = new Set(Array.from(range.getClientRects()).filter(r => r.width > 0).map(r => Math.round(r.top)));
        if (tops.size > 1) split.push(`${h.tagName.toLowerCase()} «${m[0]}»`);
      }
    }
  });
  if (edge.length) add('heading_edge', 'Заголовок прижат к краю экрана или выходит за него (нужен отступ ≥8px)', edge);
  if (split.length) add('heading_word_split', 'Слово в заголовке разорвано переносом на две строки', split);

  // 7. H1 overlaps other content
  const overlaps = [];
  document.querySelectorAll('h1').forEach(h => {
    if (!isRendered(h) || effOpacity(h) < 0.05) return;
    const a = textRect(h);
    document.querySelectorAll('img, picture, video, p, figure, button, a[class*="btn"], a[class*="button"], table, h2, [class*="card"]').forEach(el => {
      if (el === h || h.contains(el) || el.contains(h) || !isRendered(el) || effOpacity(el) < 0.05 || inChrome(el)) return;
      const b = el.getBoundingClientRect();
      const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const hh = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (w <= 0 || hh <= 0) return;
      const area = w * hh, smaller = Math.min(a.width * a.height, b.width * b.height) || 1;
      if (area / smaller > 0.04 && area > 400) overlaps.push(desc(el));
    });
  });
  if (overlaps.length) add('h1_overlap', 'H1 наезжает на другие элементы', overlaps);
  return out;
}
"""

NOJS_JS = r"""
() => {
  const effOpacity = el => {
    let o = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      o *= parseFloat(cs.opacity || '1');
    }
    return o;
  };
  const main = document.querySelector('main') || document.body;
  const hidden = [];
  main.querySelectorAll('h1, h2, h3, p, li, img, figure').forEach(el => {
    if (el.closest('header, nav, footer, dialog, [aria-hidden="true"], [hidden], details:not([open]), noscript, [class*="cookie"]')) return;
    if (el.tagName !== 'IMG' && (el.innerText || el.textContent || '').trim().length < 15) return;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    if (effOpacity(el) < 0.05) hidden.push(el.tagName.toLowerCase() + ' «' + (el.textContent || '').trim().slice(0, 50) + '»');
  });
  return hidden;
}
"""


def blank_bands(png_path: Path, viewport_h: int) -> list[dict[str, int]]:
    """Find tall uniform horizontal bands on a full-page screenshot."""
    try:
        from PIL import Image
    except ImportError:
        return []
    with Image.open(png_path) as im:
        gray = im.convert("L")
        w, h = gray.size
        small = gray.resize((max(1, min(240, w)), h))
        px = small.load()
        sw = small.size[0]
        bands: list[dict[str, int]] = []
        run_start = None
        for y in range(h):
            row = [px[x, y] for x in range(0, sw, 2)]
            uniform = (max(row) - min(row)) <= 6
            if uniform and run_start is None:
                run_start = y
            if (not uniform or y == h - 1) and run_start is not None:
                length = y - run_start
                if length >= int(viewport_h * 1.1):
                    bands.append({"top": run_start, "height": length})
                run_start = None
        return bands


def lint_page(browser, url: str, label: str, vp_name: str, size: tuple[int, int], shots_dir: Path, nojs: bool) -> dict[str, Any]:
    width, height = size
    context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
    page = context.new_page()
    result: dict[str, Any] = {"page": label, "url": url, "viewport": vp_name, "width": width}
    try:
        page.goto(url, wait_until="load", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:  # noqa: BLE001
            pass
        scroll_through(page)
        data = page.evaluate(CHECK_JS)
        shot = shots_dir / f"{label.replace('/', '__')}-{width}.png"
        shot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(shot), full_page=True)
        result["screenshot"] = str(shot)
        bands = blank_bands(shot, height)
        if bands:
            data["issues"].append(
                {
                    "code": "empty_band",
                    "message": f"Пустая полоса на скриншоте высотой ≥{bands[0]['height']}px (контент не показался?)",
                    "samples": [f"y={b['top']} h={b['height']}" for b in bands[:5]],
                }
            )
        result.update(data)
    except Exception as exc:  # noqa: BLE001
        result["issues"] = [{"code": "page_error", "message": f"Страница не открылась: {exc}", "samples": []}]
        result["warnings"] = []
    finally:
        context.close()

    if nojs and not result.get("issues", [{}])[0:1] == [{"code": "page_error"}]:
        ctx = browser.new_context(viewport={"width": width, "height": height}, java_script_enabled=False)
        p2 = ctx.new_page()
        try:
            p2.goto(url, wait_until="load", timeout=60000)
            hidden = p2.evaluate(NOJS_JS)
            if hidden:
                result.setdefault("issues", []).append(
                    {
                        "code": "hidden_without_js",
                        "message": f"Без JavaScript скрыто {len(hidden)} блок(ов) контента (анимация прячет контент)",
                        "samples": hidden[:5],
                    }
                )
        except Exception as exc:  # noqa: BLE001
            result.setdefault("warnings", []).append({"code": "nojs_error", "message": str(exc), "samples": []})
        finally:
            ctx.close()
    return result


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Visual lint (автоматическая проверка вёрстки)",
        "",
        f"**Verdict:** {'PASS' if report['verdict'] == 'pass' else '❌ FAIL'}  ",
        f"**Start:** {report['start_url']}  ",
        f"**Checked at:** {report['checked_at']}  ",
        f"**Pages × viewports:** {len(report['results'])}  ",
        f"**Issues:** {report['issue_count']}",
        "",
        "## Найдено",
        "",
    ]
    for res in report["results"]:
        for issue in res.get("issues", []):
            sample = "; ".join(issue.get("samples", [])[:3])
            lines.append(f"- `{res['page']}` @{res['width']}: **{issue['code']}** — {issue['message']}" + (f" ({sample})" if sample else ""))
    if not report["issue_count"]:
        lines.append("- проблем не найдено")
    lines += [
        "",
        "## Скриншоты для визуального описания",
        "",
        "Контролёр дизайна обязан открыть КАЖДЫЙ скриншот и описать 1–2 фразами, что на нём видно (в design-integrity-report.md).",
        "",
    ]
    for res in report["results"]:
        if res.get("screenshot"):
            lines.append(f"- `{res['page']}` @{res['width']}: `{res['screenshot']}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Teya visual lint (Playwright).")
    parser.add_argument("--url", required=True, help="Site start URL, file:// URL or static mirror directory")
    parser.add_argument("--pages", nargs="*", help="Explicit page paths/URLs (default: crawl same-site links)")
    parser.add_argument("--urls-file")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--viewports", default="desktop,tablet,mobile", help="Comma list of desktop,tablet,mobile")
    parser.add_argument("--no-nojs", action="store_true", help="Skip JavaScript-disabled check")
    parser.add_argument("--project-root", help="Write results into <root>/teya-memory/wp/qa/")
    parser.add_argument("--out", help="JSON output path")
    args = parser.parse_args()

    start = normalize_start(args.url)
    out = Path(args.out) if args.out else default_out(args.project_root, "visual-lint.json")
    shots_dir = out.parent / "visual-lint-screens"
    sync_playwright = require_playwright()
    results: list[dict[str, Any]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pages = resolve_pages(browser, start, args.pages, args.urls_file, args.limit)
        for url in pages:
            label = page_label(url, start)
            for vp_name in [v.strip() for v in args.viewports.split(",") if v.strip()]:
                size = VIEWPORTS[vp_name]
                results.append(lint_page(browser, url, label, vp_name, size, shots_dir, not args.no_nojs))
                print(f"{label} @{size[0]}: {len(results[-1].get('issues', []))} issue(s)")
        browser.close()

    issue_count = sum(len(r.get("issues", [])) for r in results)
    report = {
        "tool": "teya_visual_lint",
        "start_url": start,
        "checked_at": now_iso(),
        "pages": sorted({r["page"] for r in results}),
        "issue_count": issue_count,
        "verdict": "pass" if results and issue_count == 0 else "fail",
        "results": results,
    }
    write_json(out, report)
    out.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
    print(f"VISUAL LINT {'PASS' if report['verdict'] == 'pass' else 'FAIL'}: {issue_count} issue(s) on {len(results)} render(s) → {out}")
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
