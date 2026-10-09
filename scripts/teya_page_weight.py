#!/usr/bin/env python3
"""Teya page weight / image policy check (real browser, cold cache).

For every page the script loads it in a fresh Chromium context (no cache),
scrolls to the bottom (so lazy images load too) and sums all downloaded bytes.

Budgets (override with flags):
- home page total ≤ 1.5 MB, inner page total ≤ 1.0 MB;
- any single image ≤ 300 KB;
- CSS total ≤ 60 KB (transfer size);
- raster images must be WebP/AVIF (PNG/JPEG over 30 KB = issue; SVG/ICO ok);
- images below the first screen must have loading="lazy";
- every <img> must have width and height attributes.

Optional: --lighthouse runs the `lighthouse` CLI (if installed) for the home page
(mobile) and records performance score and LCP.

Exit code: 0 = PASS, 1 = FAIL, 2 = cannot run.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from teya_browser_common import (
    default_out,
    is_home,
    normalize_start,
    now_iso,
    page_label,
    require_playwright,
    resolve_pages,
    scroll_through,
    write_json,
)

KB = 1024

IMG_JS = r"""
() => Array.from(document.images).map(img => {
  const r = img.getBoundingClientRect();
  return {
    src: img.currentSrc || img.src,
    loading: img.getAttribute('loading') || '',
    has_wh: img.hasAttribute('width') && img.hasAttribute('height'),
    srcset: !!img.getAttribute('srcset'),
    top: r.top + window.scrollY,
    display_w: Math.round(r.width),
    natural_w: img.naturalWidth,
    visible: r.width > 1 && r.height > 1,
  };
})
"""


def resource_type(url: str, rtype: str, ctype: str) -> str:
    path = urlparse(url).path.lower()
    if rtype == "image" or ctype.startswith("image/") or path.endswith((".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg", ".ico")):
        return "image"
    if rtype == "stylesheet" or path.endswith(".css") or "text/css" in ctype:
        return "css"
    if rtype == "script" or path.endswith((".js", ".mjs")) or "javascript" in ctype:
        return "js"
    if rtype == "font" or path.endswith((".woff", ".woff2", ".ttf", ".otf")):
        return "font"
    if rtype == "document":
        return "document"
    return "other"


def image_format(url: str, ctype: str) -> str:
    ctype = (ctype or "").split(";")[0].strip().lower()
    if ctype.startswith("image/"):
        return ctype.split("/", 1)[1].replace("svg+xml", "svg").replace("x-icon", "ico").replace("vnd.microsoft.icon", "ico")
    ext = Path(urlparse(url).path).suffix.lower().lstrip(".")
    return {"jpg": "jpeg"}.get(ext, ext)


def file_size(url: str) -> int:
    if urlparse(url).scheme != "file":
        return 0
    p = Path(unquote(urlparse(url).path))
    return p.stat().st_size if p.is_file() else 0


def measure(browser, url: str, label: str, home: bool, limits: dict[str, int]) -> dict[str, Any]:
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    records: dict[str, dict[str, Any]] = {}

    def on_finished(request):
        try:
            resp = request.response()
            ctype = (resp.headers.get("content-type", "") if resp else "")
            status = resp.status if resp else 0
            sizes = request.sizes()
            size = int(sizes.get("responseBodySize") or 0)
            if size <= 0 and resp is not None:
                size = int(resp.headers.get("content-length") or 0)
            if size <= 0:
                size = file_size(request.url)
            if size <= 0 and resp is not None:
                try:
                    size = len(resp.body())
                except Exception:  # noqa: BLE001
                    size = 0
            records[request.url] = {
                "url": request.url,
                "type": resource_type(request.url, request.resource_type, ctype),
                "content_type": ctype,
                "status": status,
                "bytes": size,
            }
        except Exception:  # noqa: BLE001
            pass

    page.on("requestfinished", on_finished)
    result: dict[str, Any] = {"page": label, "url": url, "issues": [], "warnings": []}
    try:
        page.goto(url, wait_until="load", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:  # noqa: BLE001
            pass
        initial_bytes = sum(r["bytes"] for r in records.values())
        imgs_initial = page.evaluate(IMG_JS)
        scroll_through(page)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:  # noqa: BLE001
            pass
        imgs = page.evaluate(IMG_JS)
    except Exception as exc:  # noqa: BLE001
        result["issues"].append({"code": "page_error", "message": f"Страница не открылась: {exc}"})
        context.close()
        return result
    context.close()

    resources = list(records.values())
    total = sum(r["bytes"] for r in resources)
    by_type: dict[str, int] = {}
    for r in resources:
        by_type[r["type"]] = by_type.get(r["type"], 0) + r["bytes"]
    budget = limits["home"] if home else limits["inner"]
    result.update(
        {
            "total_bytes": total,
            "initial_bytes": initial_bytes,
            "budget_bytes": budget,
            "by_type": by_type,
            "requests": len(resources),
            "largest": sorted(resources, key=lambda r: -r["bytes"])[:10],
        }
    )
    if total > budget:
        result["issues"].append({"code": "page_over_budget", "message": f"Страница весит {total / KB / KB:.2f} МБ при лимите {budget / KB / KB:.2f} МБ"})
    css = by_type.get("css", 0)
    if css > limits["css"]:
        result["issues"].append({"code": "css_over_budget", "message": f"CSS {css // KB} КБ при лимите {limits['css'] // KB} КБ"})
    for r in resources:
        if r["type"] != "image":
            continue
        fmt = image_format(r["url"], r["content_type"])
        name = Path(urlparse(r["url"]).path).name
        if r["bytes"] > limits["image"]:
            result["issues"].append({"code": "image_over_budget", "message": f"Картинка {name}: {r['bytes'] // KB} КБ (лимит {limits['image'] // KB} КБ)"})
        if fmt in ("png", "jpeg", "jpg", "gif", "bmp") and r["bytes"] > 30 * KB:
            result["issues"].append({"code": "image_not_webp", "message": f"Картинка {name} в формате {fmt.upper()} ({r['bytes'] // KB} КБ) — нужен WebP/AVIF"})
    seen_src: set[str] = set()
    for img in imgs_initial:
        if not img["visible"]:
            continue
        if img["top"] > 900 * 1.2 and img["loading"] != "lazy" and img["src"] not in seen_src:
            seen_src.add(img["src"])
            result["issues"].append({"code": "missing_lazy", "message": f"Картинка ниже первого экрана без loading=\"lazy\": {Path(urlparse(img['src']).path).name}"})
    for img in imgs:
        name = Path(urlparse(img["src"]).path).name
        if img["visible"] and not img["has_wh"]:
            result["issues"].append({"code": "missing_dimensions", "message": f"У картинки {name} нет атрибутов width/height"})
        if img["visible"] and img["natural_w"] and img["display_w"] and img["natural_w"] > img["display_w"] * 2.5 and not img["srcset"]:
            result["warnings"].append({"code": "oversized_image", "message": f"{name}: файл {img['natural_w']}px при показе {img['display_w']}px и без srcset"})
    # de-duplicate messages
    for key in ("issues", "warnings"):
        uniq = []
        for item in result[key]:
            if item not in uniq:
                uniq.append(item)
        result[key] = uniq
    return result


def run_lighthouse(url: str, out_dir: Path) -> dict[str, Any]:
    exe = shutil.which("lighthouse")
    if not exe:
        return {"status": "not_installed", "hint": "npm i -g lighthouse"}
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "lighthouse-home.json"
    cmd = [exe, url, "--quiet", "--output=json", f"--output-path={out}", "--only-categories=performance",
           "--chrome-flags=--headless=new --no-sandbox"]
    try:
        subprocess.run(cmd, check=True, timeout=240, capture_output=True)
        data = json.loads(out.read_text(encoding="utf-8"))
        audits = data.get("audits", {})
        return {
            "status": "ok",
            "performance_score": round((data["categories"]["performance"]["score"] or 0) * 100),
            "lcp_ms": audits.get("largest-contentful-paint", {}).get("numericValue"),
            "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
            "total_byte_weight": audits.get("total-byte-weight", {}).get("numericValue"),
            "report": str(out),
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)[:300]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Teya page weight and image policy check.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--pages", nargs="*")
    parser.add_argument("--urls-file")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--home-budget-kb", type=int, default=1536)
    parser.add_argument("--inner-budget-kb", type=int, default=1024)
    parser.add_argument("--image-budget-kb", type=int, default=300)
    parser.add_argument("--css-budget-kb", type=int, default=60)
    parser.add_argument("--lighthouse", action="store_true", help="Also run lighthouse CLI for the home page")
    parser.add_argument("--min-lighthouse", type=int, default=70, help="Fail when Lighthouse performance < this")
    parser.add_argument("--project-root")
    parser.add_argument("--out")
    args = parser.parse_args()

    start = normalize_start(args.url)
    out = Path(args.out) if args.out else default_out(args.project_root, "page-weight.json")
    limits = {
        "home": args.home_budget_kb * KB,
        "inner": args.inner_budget_kb * KB,
        "image": args.image_budget_kb * KB,
        "css": args.css_budget_kb * KB,
    }
    sync_playwright = require_playwright()
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pages = resolve_pages(browser, start, args.pages, args.urls_file, args.limit)
        for url in pages:
            label = page_label(url, start)
            res = measure(browser, url, label, is_home(url, start), limits)
            results.append(res)
            print(f"{label}: {res.get('total_bytes', 0) / KB / KB:.2f} MB, {len(res['issues'])} issue(s)")
        browser.close()

    lighthouse = None
    if args.lighthouse and start.startswith("http"):
        lighthouse = run_lighthouse(start, out.parent)
        if lighthouse.get("status") == "ok" and lighthouse["performance_score"] < args.min_lighthouse:
            results[0]["issues"].append({"code": "lighthouse_low", "message": f"Lighthouse mobile performance {lighthouse['performance_score']} < {args.min_lighthouse}"})

    issue_count = sum(len(r["issues"]) for r in results)
    report = {
        "tool": "teya_page_weight",
        "start_url": start,
        "checked_at": now_iso(),
        "limits_bytes": limits,
        "issue_count": issue_count,
        "verdict": "pass" if results and issue_count == 0 else "fail",
        "lighthouse": lighthouse,
        "results": results,
    }
    write_json(out, report)
    lines = [
        "# Page weight (вес страниц и политика картинок)", "",
        f"**Verdict:** {'PASS' if report['verdict'] == 'pass' else '❌ FAIL'}  ",
        f"**Start:** {start}  ", f"**Checked at:** {report['checked_at']}", "",
        "| Страница | Вес, МБ | Лимит, МБ | Картинки, МБ | Проблем |", "| --- | ---: | ---: | ---: | ---: |",
    ]
    for r in results:
        lines.append(f"| {r['page']} | {r.get('total_bytes', 0) / KB / KB:.2f} | {r.get('budget_bytes', 0) / KB / KB:.2f} | {r.get('by_type', {}).get('image', 0) / KB / KB:.2f} | {len(r['issues'])} |")
    lines += ["", "## Проблемы", ""]
    for r in results:
        for i in r["issues"]:
            lines.append(f"- `{r['page']}`: **{i['code']}** — {i['message']}")
    if lighthouse:
        lines += ["", f"Lighthouse: `{json.dumps(lighthouse, ensure_ascii=False)}`"]
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"PAGE WEIGHT {'PASS' if report['verdict'] == 'pass' else 'FAIL'}: {issue_count} issue(s) → {out}")
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
