#!/usr/bin/env python3
"""Hard release gate for Teya/Aurora WordPress builds.

This script exists because text reports are not evidence. A run can only be
marked successful when local artifacts, media maps, browser/live URL signals
and the gate's OWN browser checks agree with each other.

The verdict is computed only from what this script checks and from the scripts
it runs itself (teya_visual_lint, teya_content_lint, teya_page_weight,
teya_site_fact_check, teya_image_optimize --check, teya_favicon --check).
It never reads its own previous release-gate-report.md and never trusts an
agent-written "pass" verdict (paint-evidence, DESIGN OK, QA OK).

Modes:
  --project-root P                      live: checks PUBLIC_SITE_URL (HTTPS)
  --project-root P --local-url URL      local/preview WordPress (http://127.0.0.1:8080/ or static mirror)
  --project-root P --no-live            FAILS unless --local-url is given (no site = no checks = no pass)
  --final                               also requires fresh ✅ DESIGN OK and ✅ QA OK with current theme_hash
  --theme-hash                          prints the theme hash that guardian/QA must write into their reports
Exit: 0 PASS, 1 FAIL.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BEGET_STUB_MARKERS = (
    "Домен не прилинкован",
    "не прилинкован к директории",
    "not linked to any directory",
)

SUCCESS_STATUSES = {
    "success",
    "published",
    "published_and_configured",
    "ok",
    "pass",
}

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")
FONT_EXTENSIONS = (".woff2", ".woff", ".ttf", ".otf")


def sniff_image_format(data: bytes) -> str:
    stripped = data.lstrip()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if stripped[:128].lower().startswith((b"<svg", b"<?xml")) and b"<svg" in stripped[:512].lower():
        return "svg"
    return ""


def validate_image_file(path: Path) -> list[str]:
    errors: list[str] = []
    suffix = path.suffix.lower().lstrip(".")
    if suffix == "jpg":
        suffix = "jpeg"

    try:
        data = path.read_bytes()
    except OSError as exc:
        return [f"cannot read image asset {path}: {exc}"]

    if not data:
        return [f"empty image asset: {path}"]

    detected = sniff_image_format(data)
    if not detected:
        return [f"image asset has unknown/corrupt signature: {path}"]
    if suffix and suffix != detected:
        errors.append(f"image extension/content mismatch: {path} is .{suffix} but bytes are {detected}")

    if detected == "svg":
        return errors

    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
    except ImportError:
        errors.append(f"Pillow is not installed; cannot decode-verify raster image: {path}")
    except Exception as exc:  # noqa: BLE001 - release gate must catch decoder failures.
        errors.append(f"image asset is not decodable by Pillow: {path}: {exc}")

    return errors


def read_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing required json: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json {path}: {exc}")
        return {}


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def fetch_url_details(url: str, timeout: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TeyaReleaseGate/1.0 (+https://cursor.local)",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("content-type", "")
            data = response.read(700_000)
            body = data.decode("utf-8", errors="replace")
            return {
                "status": response.status,
                "content_type": content_type,
                "body": body,
                "final_url": response.geturl(),
                "body_length": len(body),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(200_000).decode("utf-8", errors="replace")
        return {
            "status": exc.code,
            "content_type": exc.headers.get("content-type", ""),
            "body": body,
            "final_url": url,
            "body_length": len(body),
        }
    except Exception as exc:  # noqa: BLE001 - release gate must report any connectivity failure.
        body = f"FETCH_ERROR: {exc}"
        return {
            "status": 0,
            "content_type": "",
            "body": body,
            "final_url": url,
            "body_length": len(body),
        }


def fetch_url(url: str, timeout: int = 20) -> tuple[int, str, str]:
    details = fetch_url_details(url, timeout=timeout)
    return int(details["status"]), str(details["content_type"]), str(details["body"])


def normalize_assets(media_map: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(media_map.get("assets"), list):
        return [item for item in media_map["assets"] if isinstance(item, dict)]

    if isinstance(media_map.get("assets"), dict):
        assets: list[dict[str, Any]] = []
        for registry_id, item in media_map["assets"].items():
            if isinstance(item, dict):
                copied = dict(item)
                copied.setdefault("registry_id", registry_id)
                assets.append(copied)
        return assets

    metadata_keys = {
        "theme_slug",
        "generated_at",
        "source",
        "status",
        "import_status",
        "attachments",
        "project",
        "public_site_url",
        "note",
    }
    assets: list[dict[str, Any]] = []
    for registry_id, item in media_map.items():
        if registry_id in metadata_keys:
            continue
        if isinstance(item, dict):
            copied = dict(item)
            copied.setdefault("registry_id", registry_id)
            assets.append(copied)
    return assets


def is_success(value: Any) -> bool:
    return str(value or "").strip().lower() in SUCCESS_STATUSES


def public_url_from_reports(site_spec: dict[str, Any], build_report: dict[str, Any]) -> str:
    project = site_spec.get("project") if isinstance(site_spec.get("project"), dict) else {}
    return str(
        project.get("public_site_url")
        or site_spec.get("public_site_url")
        or build_report.get("public_site_url")
        or ""
    ).strip()


def theme_slug_from_reports(site_spec: dict[str, Any], build_report: dict[str, Any]) -> str:
    project = site_spec.get("project") if isinstance(site_spec.get("project"), dict) else {}
    return str(
        project.get("theme_slug")
        or site_spec.get("theme_slug")
        or build_report.get("theme_slug")
        or ""
    ).strip()


def resolve_local_path(project_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return project_root / path


def check_report_consistency(site_spec: dict[str, Any], build_report: dict[str, Any], errors: list[str]) -> None:
    report_statuses = [
        ("site-spec project.status", (site_spec.get("project") or {}).get("status") if isinstance(site_spec.get("project"), dict) else None),
        ("build-report status", build_report.get("status")),
        ("build-report deploy status", (build_report.get("deploy") or {}).get("status") if isinstance(build_report.get("deploy"), dict) else None),
    ]

    success_claims = [name for name, value in report_statuses if is_success(value)]
    if success_claims:
        for field in (
            "local_asset_files_status",
            "browser_subresources_status",
            "animation_motion_status",
            "animation_dependency_status",
            "reduced_motion_status",
            "unstyled_live_paint_status",
            "wp_media_import_status",
            "paint_evidence_status",
        ):
            value = build_report.get(field) or site_spec.get(field)
            if not value:
                errors.append(f"success claim without required data-flow field: {field}")


def check_split_reports(wp_dir: Path, build_report: dict[str, Any], errors: list[str]) -> None:
    final_reports_exist = any(
        (wp_dir / file_name).is_file()
        for file_name in ("site-spec.json", "build-report.json", "content-completeness-report.md", "verification.md")
    )
    if not final_reports_exist and not is_success(build_report.get("status")):
        return

    for file_name in (
        "theme-base-report.md",
        "asset-packaging-report.md",
        "asset-transport-report.md",
        "animation-motion-map.md",
        "animation-implementation-report.md",
        "page-build-report.md",
        "artifact-readiness-report.md",
    ):
        path = wp_dir / file_name
        if not path.is_file():
            errors.append(f"final Aurora reports without split report: teya-memory/wp/{file_name}")


def check_report_identity(wp_dir: Path, theme_slug: str, errors: list[str]) -> None:
    if not theme_slug:
        return

    report_names = (
        "theme-base-report.md",
        "asset-packaging-report.md",
        "asset-transport-report.md",
        "page-build-report.md",
        "artifact-readiness-report.md",
        "design-integrity-report.md",
        "seo-geo-verification.md",
    )
    slug_pattern = re.compile(r"\bteya-[a-z0-9][a-z0-9-]+\b")
    for name in report_names:
        path = wp_dir / name
        if not path.is_file():
            continue
        text = read_text(path)
        slugs = sorted(set(slug_pattern.findall(text)))
        stale_slugs = [slug for slug in slugs if slug not in {theme_slug, "teya-memory"}]
        if stale_slugs and theme_slug not in slugs:
            errors.append(f"stale report identity in teya-memory/wp/{name}: found {stale_slugs}, expected {theme_slug}")


def check_media_maps(project_root: Path, wp_dir: Path, theme_dir: Path, errors: list[str]) -> None:
    wp_media_map = read_json(wp_dir / "wp-media-map.json", errors)
    theme_media_map = read_json(theme_dir / "media-map.json", errors)

    for label, media_map in (("wp-media-map.json", wp_media_map), ("theme media-map.json", theme_media_map)):
        if label == "theme media-map.json" and media_map.get("transport_status") != "pass":
            errors.append("theme media-map.json transport_status is not pass; asset transport did not complete")
        assets = normalize_assets(media_map)
        if not assets:
            errors.append(f"{label} has no assets array/object")
            continue

        for item in assets:
            registry_id = str(item.get("registry_id") or item.get("id") or "").strip()
            asset_id = str(item.get("id") or item.get("registry_id") or "").strip()
            file_name = str(item.get("file") or item.get("path") or "").strip()
            local_source = str(item.get("local_source_path") or "").strip()
            attachment_url = str(item.get("attachment_url") or "").strip()
            alt_text = str(item.get("alt_text") or item.get("alt") or "").strip()

            if not registry_id:
                errors.append(f"{label}: asset without id/registry_id")
            if registry_id and asset_id and registry_id != asset_id:
                errors.append(f"{label}: id/registry_id mismatch for {registry_id}: id={asset_id}")
            if not file_name:
                errors.append(f"{label}: {registry_id} has no file")
            if not alt_text or alt_text.lower() in {"image", "photo", "placeholder", "asset"}:
                errors.append(f"{label}: {registry_id} has missing/generic alt_text")

            if local_source:
                resolved_source = resolve_local_path(project_root, local_source)
                if not resolved_source.is_file():
                    errors.append(f"{label}: local_source_path missing for {registry_id}: {local_source}")
                elif resolved_source.suffix.lower() in IMAGE_EXTENSIONS:
                    errors.extend(f"{label}: {registry_id}: {error}" for error in validate_image_file(resolved_source))
                    item["_resolved_asset_path"] = str(resolved_source)
            elif file_name:
                relative = Path(file_name)
                candidate = theme_dir / relative if str(file_name).replace("\\", "/").startswith("assets/") else theme_dir / "assets" / "images" / relative
                if not candidate.is_file():
                    errors.append(f"{label}: theme asset file missing for {registry_id}: {candidate.relative_to(theme_dir)}")
                elif candidate.suffix.lower() in IMAGE_EXTENSIONS:
                    errors.extend(f"{label}: {registry_id}: {error}" for error in validate_image_file(candidate))
                    item["_resolved_asset_path"] = str(candidate)

            if attachment_url:
                parsed = urllib.parse.urlparse(attachment_url)
                path = parsed.path.lower()
                if "/wp-content/uploads/" not in path:
                    errors.append(f"{label}: {registry_id} attachment_url is not WP uploads: {attachment_url}")
                if not path.endswith(IMAGE_EXTENSIONS):
                    errors.append(f"{label}: {registry_id} attachment_url is not a direct image file: {attachment_url}")

    if wp_media_map.get("import_status") == "pending":
        errors.append("wp-media-map.json import_status is pending; WP Media import is not complete")

    for label, media_map in (("wp-media-map.json", wp_media_map), ("theme media-map.json", theme_media_map)):
        hashes: dict[str, list[str]] = {}
        for item in normalize_assets(media_map):
            registry_id = str(item.get("registry_id") or item.get("id") or "").strip()
            raw_path = str(item.get("_resolved_asset_path") or "").strip()
            if not registry_id or not raw_path:
                continue
            path = Path(raw_path)
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                hashes.setdefault(digest, []).append(registry_id)
        for digest, ids in hashes.items():
            unique_ids = sorted(set(ids))
            if len(unique_ids) > 1:
                errors.append(f"{label}: duplicate image bytes for distinct assets {unique_ids}: sha256={digest}")


def check_aura_asset_registry(project_root: Path, errors: list[str]) -> None:
    registry_path = project_root / "teya-memory" / "design" / "AURA_ASSET_REGISTRY.json"
    registry = read_json(registry_path, errors)
    assets = registry.get("assets") if isinstance(registry.get("assets"), list) else []

    if not assets:
        errors.append("AURA_ASSET_REGISTRY.json has no assets array")
        return

    for item in assets:
        if not isinstance(item, dict):
            continue

        asset_id = str(item.get("id") or item.get("registry_id") or "").strip()
        requires_bg = bool(item.get("requires_background_removal"))
        transparent_url = str(item.get("transparent_url") or "").strip()
        packaged_url = str(item.get("packaged_url") or "").strip()
        bg_tool = str(item.get("background_removal_tool") or "").strip()
        bg_status = str(item.get("background_removal_status") or "").strip().lower()
        tools_pipeline = item.get("tools_pipeline") if isinstance(item.get("tools_pipeline"), list) else []

        if requires_bg:
            if "recraft_remove_background" not in tools_pipeline and bg_tool != "recraft_remove_background":
                errors.append(f"AURA asset {asset_id}: cutout requires recraft_remove_background pipeline")
            if not transparent_url:
                errors.append(f"AURA asset {asset_id}: requires_background_removal but transparent_url is empty")
            if bg_status != "ready":
                errors.append(f"AURA asset {asset_id}: background_removal_status is not ready")
            if not packaged_url:
                errors.append(f"AURA asset {asset_id}: packaged_url is empty")
            if transparent_url and packaged_url.startswith(("http://", "https://")) and packaged_url != transparent_url:
                errors.append(f"AURA asset {asset_id}: packaged_url must equal transparent_url for cutout assets")
            if packaged_url and not packaged_url.startswith(("http://", "https://")) and not packaged_url.startswith("assets/"):
                errors.append(f"AURA asset {asset_id}: local packaged_url must start with assets/: {packaged_url}")

        if item.get("status") == "ready" and requires_bg and not transparent_url:
            errors.append(f"AURA asset {asset_id}: status ready contradicts missing transparent_url")


def check_excalibur_blog_ownership(project_root: Path, wp_dir: Path, errors: list[str]) -> None:
    blog_dir = project_root / "teya-memory" / "blog"
    articles_dir = blog_dir / "articles"
    fragment = project_root / "teya-memory" / "fragments" / "excalibur.md"
    run_log = blog_dir / "excalibur-run-log.md"

    article_dirs = [path for path in articles_dir.iterdir() if path.is_dir()] if articles_dir.is_dir() else []
    article_like_reports = ""
    for name in ("page-content-pack.md", "page-build-report.md", "content-completeness-report.md", "build-report.json"):
        path = wp_dir / name
        if path.is_file():
            article_like_reports += "\n" + read_text(path)

    claims_articles = bool(re.search(r"\b(article\.html|BlogPosting|wp-publish-result|article-qa\.md)\b", article_like_reports))
    if claims_articles and not article_dirs:
        errors.append("reports claim blog articles/schema, but teya-memory/blog/articles has no Excalibur article dirs")

    if article_dirs and not fragment.is_file():
        errors.append("blog articles exist without teya-memory/fragments/excalibur.md; articles must be owned by Excalibur")
    if article_dirs and not run_log.is_file():
        errors.append("blog articles exist without teya-memory/blog/excalibur-run-log.md")

    for article_dir in article_dirs:
        for required in ("article.html", "article.meta.json", "article-qa.md", "schema.jsonld"):
            if not (article_dir / required).is_file():
                errors.append(f"Excalibur article missing {required}: {article_dir.relative_to(project_root)}")
        qa_text = read_text(article_dir / "article-qa.md")
        if qa_text and "PASS" not in qa_text.upper() and "✅" not in qa_text:
            errors.append(f"Excalibur article QA is not PASS: {article_dir.relative_to(project_root)}")


def css_urls(css: str) -> list[str]:
    return re.findall(r"url\((?:'|\")?([^'\"\)]+)(?:'|\")?\)", css)


def js_dynamic_imports(js: str) -> list[str]:
    return re.findall(r"import\(\s*['\"]([^'\"]+)['\"]\s*\)", js)


def check_theme_assets(theme_dir: Path, errors: list[str]) -> None:
    for css_path in [theme_dir / "style.css", theme_dir / "assets" / "dist" / "style.css"]:
        if not css_path.is_file():
            errors.append(f"missing css file: {css_path}")
            continue
        for raw_url in css_urls(read_text(css_path)):
            if raw_url.startswith(("data:", "http://", "https://", "#")):
                continue
            asset_path = (css_path.parent / raw_url).resolve()
            if raw_url.lower().endswith(IMAGE_EXTENSIONS + FONT_EXTENSIONS) and not asset_path.is_file():
                errors.append(f"css references missing asset: {css_path} -> {raw_url}")
            elif raw_url.lower().endswith(IMAGE_EXTENSIONS) and asset_path.is_file():
                errors.extend(validate_image_file(asset_path))

    header = read_text(theme_dir / "header.php")
    for raw_url in re.findall(r"/assets/[^'\"\s>]+", header):
        relative = raw_url.lstrip("/")
        if relative.lower().endswith(IMAGE_EXTENSIONS + FONT_EXTENSIONS) and not (theme_dir / relative).is_file():
            errors.append(f"header preload/reference missing asset: {relative}")

    images_dir = theme_dir / "assets" / "images"
    if images_dir.is_dir():
        for image_path in sorted(images_dir.rglob("*")):
            if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
                errors.extend(validate_image_file(image_path))

    main_js_path = theme_dir / "assets" / "dist" / "main.js"
    if main_js_path.is_file():
        for rel_import in js_dynamic_imports(read_text(main_js_path)):
            import_path = (main_js_path.parent / rel_import).resolve()
            if not import_path.is_file():
                errors.append(f"main.js dynamic import references missing local chunk: {rel_import}")


def check_paint_evidence(wp_dir: Path, public_url: str, require_live: bool, errors: list[str]) -> None:
    paint_dir = wp_dir / "paint-qa"
    evidence_path = paint_dir / "paint-evidence.json"

    if not evidence_path.is_file():
        if require_live:
            errors.append("missing paint evidence: teya-memory/wp/paint-qa/paint-evidence.json")
        return

    evidence = read_json(evidence_path, errors)
    if public_url and evidence.get("public_site_url") and str(evidence["public_site_url"]).rstrip("/") != public_url.rstrip("/"):
        errors.append("paint evidence public_site_url does not match release public URL")

    screenshots = evidence.get("screenshots") if isinstance(evidence.get("screenshots"), dict) else {}
    screenshot_paths: list[str] = []
    for key in ("home_1440", "home_375"):
        if screenshots.get(key):
            screenshot_paths.append(str(screenshots[key]))
    for page in screenshots.get("pages") or []:
        if isinstance(page, dict):
            screenshot_paths.extend(str(page[key]) for key in ("desktop", "mobile") if page.get(key))

    if require_live and not screenshot_paths:
        errors.append("paint evidence has no screenshot paths")

    for path in screenshot_paths:
        if not resolve_local_path(wp_dir.parent.parent, path).is_file():
            errors.append(f"paint evidence screenshot file missing: {path}")

    # An agent-written "pass" is NOT evidence: the gate runs teya_visual_lint.py itself.
    # An agent-written "fail" still blocks (the agent saw a problem).
    verdict = str(evidence.get("verdict") or "").lower()
    if verdict and verdict != "pass":
        errors.append(f"paint evidence verdict is {verdict!r} (agent saw a problem)")


def check_live(public_url: str, theme_slug: str, theme_dir: Path, errors: list[str], require_https: bool = True) -> None:
    if not public_url:
        return

    parsed = urllib.parse.urlparse(public_url)
    if require_https and parsed.scheme != "https":
        errors.append(f"public_site_url must be HTTPS for published success: {public_url}")

    details = fetch_url_details(public_url)
    status = int(details["status"])
    content_type = str(details["content_type"])
    html = str(details["body"])
    final_url = str(details["final_url"])
    body_length = int(details["body_length"])
    if status != 200:
        errors.append(f"public_site_url is not HTTP 200: {public_url} -> {status}, final_url={final_url}, body_length={body_length}")
        return

    if body_length == 0:
        errors.append(f"public_site_url returned empty body: {public_url} -> 200, final_url={final_url}")
        return

    if any(marker.lower() in html.lower() for marker in BEGET_STUB_MARKERS):
        errors.append(f"public_site_url returns Beget/domain stub instead of site: {public_url}")

    if theme_slug and theme_slug not in html:
        errors.append(f"public HTML does not contain current theme slug {theme_slug}")

    if "text/html" not in content_type.lower():
        errors.append(f"public_site_url content-type is not HTML: {content_type}")

    if theme_slug:
        theme_css_url = urllib.parse.urljoin(public_url, f"/wp-content/themes/{theme_slug}/style.css")
        css_details = fetch_url_details(theme_css_url, timeout=15)
        if int(css_details["status"]) != 200:
            errors.append(
                f"theme stylesheet is not reachable: {theme_css_url} -> {css_details['status']}, "
                f"final_url={css_details['final_url']}, body_length={css_details['body_length']}"
            )

        main_js_url = urllib.parse.urljoin(public_url, f"/wp-content/themes/{theme_slug}/assets/dist/main.js")
        main_js_details = fetch_url_details(main_js_url, timeout=15)
        if int(main_js_details["status"]) != 200:
            errors.append(
                f"theme main.js is not reachable: {main_js_url} -> {main_js_details['status']}, "
                f"final_url={main_js_details['final_url']}, body_length={main_js_details['body_length']}"
            )
        else:
            live_main_js = str(main_js_details["body"])
            local_imports: list[str] = []
            local_main_js = theme_dir / "assets" / "dist" / "main.js"
            if local_main_js.is_file():
                local_imports = js_dynamic_imports(read_text(local_main_js))
                for rel_import in local_imports:
                    if rel_import not in live_main_js:
                        errors.append(f"live main.js is stale/missing dynamic import reference: {rel_import}")

            dynamic_imports = sorted(set(js_dynamic_imports(live_main_js) + local_imports))
            for rel_import in dynamic_imports:
                dynamic_url = urllib.parse.urljoin(main_js_url, rel_import)
                dynamic_details = fetch_url_details(dynamic_url, timeout=15)
                if int(dynamic_details["status"]) != 200:
                    errors.append(
                        f"theme dynamic import is not reachable: {dynamic_url} -> {dynamic_details['status']}, "
                        f"final_url={dynamic_details['final_url']}, body_length={dynamic_details['body_length']}"
                    )

    wp_json_url = urllib.parse.urljoin(public_url, "/wp-json/")
    wp_json_details = fetch_url_details(wp_json_url, timeout=15)
    if int(wp_json_details["status"]) >= 400 or int(wp_json_details["status"]) == 0:
        errors.append(
            f"wp-json endpoint is not reachable: {wp_json_url} -> {wp_json_details['status']}, "
            f"final_url={wp_json_details['final_url']}, body_length={wp_json_details['body_length']}"
        )

    image_sources = re.findall(r"<img[^>]+src=[\"']([^\"']+)[\"']", html, flags=re.I)
    if not image_sources:
        errors.append("public HTML has no img[src] elements")

    for src in image_sources[:40]:
        absolute = urllib.parse.urljoin(public_url, src)
        code, _, _ = fetch_url(absolute, timeout=15)
        if code >= 400 or code == 0:
            errors.append(f"live image request failed: {absolute} -> {code}")


def check_https_canonical(wp_dir: Path, public_url: str, errors: list[str]) -> None:
    if public_url and not public_url.startswith("https://"):
        errors.append(f"canonical public URL must be HTTPS: {public_url}")

    deploy_log = read_text(wp_dir / "deploy-log.md")
    for match in re.findall(r"home_url:\s*(https?://\S+)|home=([^\s]+)|siteurl=([^\s]+)", deploy_log):
        observed = next((part for part in match if part), "")
        if observed.startswith("http://"):
            errors.append(f"WordPress canonical URL is HTTP, expected HTTPS: {observed}")


# --------------------------------------------------------------------------------------
# Gate-owned checks: scripts, report scan, theme hash, favicon.
# --------------------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parent
GATE_REPORT = "release-gate-report.md"
# Status words are matched case-sensitively (BLOCKER / FAIL in caps = a verdict, "blocker" in prose = a rule).
NEGATIVE_LINE = re.compile(
    r"(❌\s*\**\s*(?:[A-ZА-ЯЁ-]+\s+){0,2}(?:BLOCKER|BLOCKED|FAIL|НЕ\s*ГОТОВ)"
    r"|\bFAIL(?:ED)?\b"
    r"|\*\*\s*(?:[A-ZА-ЯЁ-]+\s+){0,2}BLOCKER\b"
    r"|(?i:(?:Статус|Status|Verdict|Вердикт|Итог)\s*\**\s*:\s*\**\s*❌)"
    r"|(?i:Ready[^\n|]{0,40}\|\s*\**\s*(?:no|нет)\b))"
)
NOT_A_FINDING = re.compile(
    r"((?i:\b(?:no|not|нет|без|none|никаких)\b)\W{0,4}`?\s*❌|BLOCKER\**\s*:\s*\**\s*(?i:none|нет)\b|(?i:\bno\s+`?\S*\s*BLOCKER)"
    r"|(?i:\b(?:если|if|when|любой|any|должен|должна|must|ставь|запрещено|иначе|otherwise|например|e\.g\.)\b))"
)
RESOLVED_LINE = re.compile(r"(исправлен|устранен|устранён|fixed|resolved|закрыт|было\s*:|до\s+исправления|history|история)", re.I)
POSITIVE_STATUS = re.compile(
    r"((?:Статус|Status|Verdict|Вердикт|Итог)\s*\**\s*:?\s*\**\s*(?:✅\s*(?:[A-Z]+\s+)?OK|PASS\b|READY\b|published_and_configured))"
    r"|^#+\s*✅\s*(?:DESIGN|QA)\s+OK",
    re.I | re.M,
)
SCANNED_REPORT_DIRS = ("wp", "fragments")
SKIP_REPORTS = {GATE_REPORT, "aurora-team-release-gate.md"}


def theme_hash(theme_dir: Path) -> str:
    """Short hash of the theme files: guardian/QA reports must quote it (`theme_hash: xxxx`)."""
    digest = hashlib.sha256()
    if theme_dir.is_dir():
        for path in sorted(p for p in theme_dir.rglob("*") if p.is_file()):
            rel = path.relative_to(theme_dir).as_posix()
            if rel.startswith((".git/", "node_modules/")):
                continue
            digest.update(rel.encode())
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()[:12]


def report_hash(text: str) -> str:
    match = re.search(r"theme_hash\s*[:=]\s*`?([0-9a-f]{8,64})", text)
    return match.group(1)[:12] if match else ""


def scan_reports(project_root: Path, current_hash: str, errors: list[str], warnings: list[str]) -> None:
    """❌ / BLOCKER / FAIL status lines and contradictions in agent reports block the release.

    Reports stamped with an older theme_hash are stale: only a warning (the gate's own checks decide),
    but they cannot be used as DESIGN OK / QA OK.
    """
    mem = project_root / "teya-memory"
    files: list[Path] = []
    for sub in SCANNED_REPORT_DIRS:
        d = mem / sub
        if d.is_dir():
            files += sorted(p for p in d.glob("*.md") if p.name not in SKIP_REPORTS)
    if (mem / "01-handoff.md").is_file():
        files.append(mem / "01-handoff.md")
    for path in files:
        text = read_text(path)
        rel = path.relative_to(project_root).as_posix()
        stamped = report_hash(text)
        stale = bool(stamped and current_hash and stamped != current_hash)
        bad_lines = []
        in_code = False
        for line in text.splitlines():
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if NEGATIVE_LINE.search(line) and not RESOLVED_LINE.search(line) and not NOT_A_FINDING.search(line):
                # rule/template lines like "Статус: ✅ DESIGN OK | ⚠️ ... | ❌ DESIGN BLOCKER" are not findings
                if line.count("|") >= 2 and "✅" in line and "❌" in line and "DESIGN" in line.upper():
                    continue
                bad_lines.append(line.strip()[:160])
        if not bad_lines:
            continue
        msg = f"{rel}: {len(bad_lines)} строк(и) с ❌/BLOCKER/FAIL, например «{bad_lines[0]}»"
        if stale:
            warnings.append(f"(устаревший отчёт, theme_hash {stamped} ≠ {current_hash}) {msg}")
            continue
        errors.append(msg)
        if POSITIVE_STATUS.search(text):
            errors.append(f"{rel}: противоречие — в отчёте одновременно успех (OK/PASS/READY) и ❌/BLOCKER")


def check_final_signoff(project_root: Path, current_hash: str, errors: list[str]) -> None:
    wp_dir = project_root / "teya-memory" / "wp"
    for name, marker in (("design-integrity-report.md", r"✅\s*DESIGN OK"), ("seo-geo-verification.md", r"✅\s*(QA\s*)?OK")):
        text = read_text(wp_dir / name)
        if not text:
            errors.append(f"--final: нет teya-memory/wp/{name}")
            continue
        if not re.search(marker, text):
            errors.append(f"--final: teya-memory/wp/{name} не содержит {marker.replace(chr(92) + 's*', ' ')}")
        stamped = report_hash(text)
        if not stamped:
            errors.append(f"--final: teya-memory/wp/{name} без `theme_hash:` — нельзя понять, к какой версии темы относится")
        elif stamped != current_hash:
            errors.append(f"--final: teya-memory/wp/{name} устарел (theme_hash {stamped} ≠ текущий {current_hash}); после правок проверку надо повторить")
    shots_note = read_text(wp_dir / "design-integrity-report.md")
    if shots_note and not re.search(r"(скриншот|screenshot)[^\n]{0,80}(описан|описание|description|вижу)", shots_note, re.I):
        errors.append("--final: design-integrity-report.md не содержит описаний скриншотов (guardian обязан описать каждый)")


def run_tool(name: str, cli: list[str], out_json: Path, results: list[dict[str, Any]], errors: list[str], timeout: int = 900) -> dict[str, Any]:
    import subprocess

    cmd = [sys.executable, str(SCRIPTS_DIR / name)] + cli
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        code, tail = proc.returncode, (proc.stdout + proc.stderr).strip().splitlines()[-3:]
    except subprocess.TimeoutExpired:
        code, tail = 2, [f"timeout after {timeout}s"]
    data: dict[str, Any] = {}
    if out_json.is_file():
        try:
            data = json.loads(out_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    verdict = str(data.get("verdict") or ("pass" if code == 0 else "fail"))
    row = {"tool": name, "exit": code, "verdict": verdict, "report": str(out_json), "tail": tail}
    results.append(row)
    if code == 2:
        errors.append(f"{name}: не удалось запустить ({' / '.join(tail)}) — без проверки нет PASS")
    elif code != 0 or verdict == "fail":
        errors.append(f"{name}: FAIL — см. {out_json.with_suffix('.md')} ({' / '.join(tail)})")
    return row


def run_site_checks(project_root: Path, theme_dir: Path, url: str, pages_limit: int, errors: list[str],
                    warnings: list[str], results: list[dict[str, Any]], lighthouse: bool) -> None:
    qa = project_root / "teya-memory" / "wp" / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    root = ["--project-root", str(project_root)]
    lim = ["--limit", str(pages_limit)]
    run_tool("teya_visual_lint.py", ["--url", url, *lim, *root, "--out", str(qa / "visual-lint.json")], qa / "visual-lint.json", results, errors)
    content_cli = ["--url", url, *lim, *root, "--out", str(qa / "content-lint.json")]
    if theme_dir.is_dir():
        content_cli += ["--paths", str(theme_dir)]
    run_tool("teya_content_lint.py", content_cli, qa / "content-lint.json", results, errors)
    pw_cli = ["--url", url, *lim, *root, "--out", str(qa / "page-weight.json")]
    if lighthouse:
        pw_cli.append("--lighthouse")
    run_tool("teya_page_weight.py", pw_cli, qa / "page-weight.json", results, errors)
    fact_cli = ["--url", url, *lim, *root, "--out", str(qa / "site-fact-check.json")]
    if theme_dir.is_dir():
        fact_cli += ["--paths", str(theme_dir)]
    row = run_tool("teya_site_fact_check.py", fact_cli, qa / "site-fact-check.json", results, errors)
    if row["verdict"] == "no_claims":
        warnings.append("site fact check: 0 утверждений найдено — это НЕ «факты проверены», а «проверять нечего»")
    if theme_dir.is_dir():
        run_tool("teya_image_optimize.py", ["--theme", str(theme_dir), "--out", str(qa / "image-optimize.json")], qa / "image-optimize.json", results, errors)


def check_favicon(theme_dir: Path, url: str, errors: list[str]) -> None:
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from teya_favicon import check as favicon_check
    except Exception as exc:  # noqa: BLE001
        errors.append(f"favicon check unavailable: {exc}")
        return
    http_url = url if url.startswith(("http://", "https://")) else None
    for err in favicon_check(theme_dir if theme_dir.is_dir() else None, http_url):
        errors.append(err)


def write_gate_report(project_root: Path, mode: str, target: str, current_hash: str, errors: list[str],
                      warnings: list[str], results: list[dict[str, Any]]) -> None:
    from datetime import datetime, timezone

    wp_dir = project_root / "teya-memory" / "wp"
    wp_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Release gate report (written by teya_release_gate.py — do not edit by hand)",
        "",
        f"**Verdict:** {'PASS' if not errors else 'FAIL'}  ",
        f"**Mode:** {mode}  ",
        f"**Target:** {target or '—'}  ",
        f"**theme_hash:** {current_hash}  ",
        f"**Checked at:** {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}",
        "",
        "## Script checks (run by the gate itself)",
        "",
        "| script | exit | verdict | report |",
        "| --- | ---: | --- | --- |",
    ]
    for row in results:
        lines.append(f"| {row['tool']} | {row['exit']} | {row['verdict']} | `{row['report']}` |")
    if errors:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in errors]
    if warnings:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in warnings]
    (wp_dir / GATE_REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Teya/Aurora release evidence.")
    parser.add_argument("--project-root", default=".", help="Project root containing teya-memory/")
    parser.add_argument("--no-live", action="store_true", help="Do not check PUBLIC_SITE_URL. Requires --local-url, otherwise FAIL.")
    parser.add_argument("--local-url", help="Local WordPress / preview URL (http://127.0.0.1:8080/, file:// or static mirror dir)")
    parser.add_argument("--final", action="store_true", help="Final release: require fresh ✅ DESIGN OK and ✅ QA OK with current theme_hash")
    parser.add_argument("--theme-hash", action="store_true", help="Print current theme_hash and exit")
    parser.add_argument("--pages-limit", type=int, default=40)
    parser.add_argument("--lighthouse", action="store_true", help="Also run Lighthouse via teya_page_weight.py")
    parser.add_argument("--skip-site-scripts", action="store_true", help="Debug only: never gives PASS")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    wp_dir = project_root / "teya-memory" / "wp"

    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    site_spec = read_json(wp_dir / "site-spec.json", errors)
    build_report = read_json(wp_dir / "build-report.json", errors)
    theme_slug = theme_slug_from_reports(site_spec, build_report)
    public_url = public_url_from_reports(site_spec, build_report)
    theme_dir = project_root / "teya-memory" / "wp" / "theme" / theme_slug if theme_slug else Path()
    current_hash = theme_hash(theme_dir) if theme_slug else ""

    if args.theme_hash:
        print(current_hash or "no-theme")
        return 0 if current_hash else 1

    if not theme_slug:
        errors.append("cannot determine theme_slug from reports")
    elif not theme_dir.is_dir():
        errors.append(f"theme directory missing: {theme_dir}")

    check_report_consistency(site_spec, build_report, errors)
    check_split_reports(wp_dir, build_report, errors)
    check_report_identity(wp_dir, theme_slug, errors)
    check_aura_asset_registry(project_root, errors)
    check_excalibur_blog_ownership(project_root, wp_dir, errors)
    check_https_canonical(wp_dir, public_url, errors)

    if theme_dir.is_dir():
        check_media_maps(project_root, wp_dir, theme_dir, errors)
        check_theme_assets(theme_dir, errors)

    if args.local_url:
        mode, target = "local", args.local_url
    elif args.no_live:
        mode, target = "no-live", ""
        errors.append("--no-live без --local-url: сайт не проверен браузером → PASS невозможен (подними локальный WordPress и передай --local-url)")
    elif public_url:
        mode, target = "live", public_url
    else:
        mode, target = "none", ""
        errors.append("нет ни PUBLIC_SITE_URL, ни --local-url: проверять нечего → FAIL")

    check_paint_evidence(wp_dir, public_url, mode == "live", errors)
    if mode == "live":
        check_live(public_url, theme_slug, theme_dir, errors, require_https=True)
    elif mode == "local" and target.startswith(("http://", "https://")):
        check_live(target, theme_slug, theme_dir, errors, require_https=False)

    if target:
        if args.skip_site_scripts:
            errors.append("--skip-site-scripts: браузерные проверки пропущены → PASS невозможен")
        else:
            run_site_checks(project_root, theme_dir, target, args.pages_limit, errors, warnings, results, args.lighthouse)
        check_favicon(theme_dir, target, errors)
    elif theme_dir.is_dir():
        check_favicon(theme_dir, "", errors)

    scan_reports(project_root, current_hash, errors, warnings)
    if args.final:
        check_final_signoff(project_root, current_hash, errors)

    errors = list(dict.fromkeys(errors))
    warnings = list(dict.fromkeys(warnings))
    write_gate_report(project_root, mode + (" final" if args.final else ""), target, current_hash, errors, warnings, results)

    if errors:
        print("TEYA RELEASE GATE FAILED")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"! {warning}")
        print(f"theme_hash: {current_hash}")
        return 1

    for warning in warnings:
        print(f"! {warning}")
    print(f"TEYA RELEASE GATE PASS (theme_hash: {current_hash})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
