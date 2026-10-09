#!/usr/bin/env python3
"""Shared helpers for Teya browser-based quality scripts.

Used by teya_visual_lint.py, teya_page_weight.py, teya_content_lint.py and
teya_site_fact_check.py. Works with live/local http(s) sites and with static
mirrors opened via file:// (for example an unpacked preview zip).

Install once (cloud/local):
    python3 -m pip install --user playwright pillow
    python3 -m playwright install --with-deps chromium   # or: install chromium
"""
from __future__ import annotations

import json
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urldefrag, urljoin, urlparse

SKIP_PATH_PARTS = (
    "/wp-admin", "/wp-login", "/wp-json", "/feed", "/xmlrpc", "/comments/feed",
    "/wp-content/", "/wp-includes/", "/cart", "/checkout", "/my-account",
)
SKIP_EXTENSIONS = (
    ".xml", ".pdf", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".ico",
    ".zip", ".txt", ".css", ".js", ".json", ".mp4", ".webmanifest",
)
VIEWPORTS = {"desktop": (1440, 900), "tablet": (768, 1024), "mobile": (375, 812)}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def require_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print(
            "TEYA BROWSER BLOCKER: Playwright is not installed.\n"
            "  python3 -m pip install --user playwright pillow\n"
            "  python3 -m playwright install --with-deps chromium",
            file=sys.stderr,
        )
        raise SystemExit(2)
    from playwright.sync_api import sync_playwright

    return sync_playwright


def normalize_start(value: str) -> str:
    """Accept http(s) URL, file:// URL, a directory or an index.html path."""
    if value.startswith(("http://", "https://", "file://")):
        return value
    path = Path(value).expanduser().resolve()
    if path.is_dir():
        path = path / "index.html"
    if not path.is_file():
        raise SystemExit(f"start path not found: {value}")
    return path.as_uri()


def same_site(url: str, start: str) -> bool:
    a, b = urlparse(url), urlparse(start)
    if b.scheme == "file":
        root = str(Path(urlparse(start).path).parent)
        return a.scheme == "file" and urlparse(url).path.startswith(root)
    return a.scheme in ("http", "https") and a.netloc == b.netloc


def clean_url(url: str) -> str:
    url, _frag = urldefrag(url)
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.query:
        url = url.split("?", 1)[0]
    return url


def is_page_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    if any(part in path for part in SKIP_PATH_PARTS):
        return False
    if path.endswith(SKIP_EXTENSIONS):
        return False
    if "/page/" in path or "/tag/" in path or "/author/" in path:
        return False
    return True


def collect_links(page, base: str) -> list[str]:
    hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
    out: list[str] = []
    for href in hrefs or []:
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = clean_url(urljoin(base, href))
        if urlparse(absolute).scheme == "file" and absolute.endswith("/"):
            absolute += "index.html"
        out.append(absolute)
    return out


def discover_pages(page, start: str, limit: int = 40, depth: int = 2) -> list[str]:
    """Breadth-first crawl of same-site links (works for file:// mirrors too)."""
    start = clean_url(start)
    seen: list[str] = [start]
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    while queue and len(seen) < limit:
        url, level = queue.popleft()
        if level >= depth:
            continue
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
        except Exception:  # noqa: BLE001 - unreachable page just stops this branch
            continue
        for link in collect_links(page, page.url):
            if link in seen or not same_site(link, start) or not is_page_url(link):
                continue
            seen.append(link)
            queue.append((link, level + 1))
            if len(seen) >= limit:
                break
    return seen


def read_url_list(start: str, pages: Iterable[str] | None, urls_file: str | None) -> list[str]:
    items: list[str] = []
    for raw in pages or []:
        items.append(clean_url(urljoin(start, raw)))
    if urls_file:
        for line in Path(urls_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                items.append(clean_url(urljoin(start, line)))
    return items


def resolve_pages(browser, start: str, pages: Iterable[str] | None, urls_file: str | None, limit: int) -> list[str]:
    explicit = read_url_list(start, pages, urls_file)
    if explicit:
        return list(dict.fromkeys(explicit))[:limit]
    context = browser.new_context()
    page = context.new_page()
    try:
        return discover_pages(page, start, limit=limit)
    finally:
        context.close()


def scroll_through(page, step_ratio: float = 0.8, pause_ms: int = 120, max_steps: int = 80) -> None:
    """Scroll to the bottom in steps (fires lazy-load and scroll reveals), then back to top."""
    page.evaluate(
        """async ([ratio, pause, maxSteps]) => {
            const sleep = ms => new Promise(r => setTimeout(r, ms));
            const step = Math.max(200, Math.floor(window.innerHeight * ratio));
            for (let i = 0; i < maxSteps; i++) {
                const before = window.scrollY;
                window.scrollBy(0, step);
                await sleep(pause);
                if (window.scrollY === before) break;
            }
            await sleep(400);
            window.scrollTo(0, 0);
            await sleep(300);
        }""",
        [step_ratio, pause_ms, max_steps],
    )
    page.wait_for_timeout(700)


def page_label(url: str, start: str) -> str:
    path = urlparse(url).path
    root = urlparse(start).path
    if urlparse(start).scheme == "file":
        root = str(Path(root).parent) + "/"
        path = path.replace("index.html", "")
    rel = path[len(root):] if path.startswith(root) else path
    rel = rel.strip("/")
    return rel or "home"


def is_home(url: str, start: str) -> bool:
    return page_label(url, start) == "home"


def visible_text(page) -> str:
    return page.evaluate("() => document.body ? document.body.innerText : ''") or ""


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def default_out(project_root: str | None, name: str) -> Path:
    if project_root:
        return Path(project_root).resolve() / "teya-memory" / "wp" / "qa" / name
    return Path.cwd() / name
