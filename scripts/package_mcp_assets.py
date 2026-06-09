#!/usr/bin/env python3
"""Package MCP/CDN visual assets into a WordPress theme safely.

This is the canonical asset-packager script for Teya agents. It exists so
agents do not invent ad-hoc downloaders that corrupt Range responses.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from asset_download import download_url_bytes, probe_url
from teya_release_gate import sniff_image_format, validate_image_file


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_http_url(value: Any) -> bool:
    text = str(value or "").strip()
    return text.startswith(("http://", "https://"))


def is_local_asset_path(value: Any) -> bool:
    text = str(value or "").replace("\\", "/").strip()
    return text.startswith("assets/")


def registry_assets(registry: dict[str, Any]) -> list[dict[str, Any]]:
    assets = registry.get("assets")
    return [item for item in assets if isinstance(item, dict)] if isinstance(assets, list) else []


def asset_id(item: dict[str, Any]) -> str:
    return str(item.get("id") or item.get("registry_id") or "").strip()


def pick_remote_url(item: dict[str, Any]) -> str:
    """Pick the correct remote URL without trusting local packaged_url values."""
    if item.get("requires_background_removal"):
        for key in ("transparent_url", "packaged_url", "remote_packaged_url"):
            if is_http_url(item.get(key)):
                return str(item[key]).strip()
        return ""

    for key in ("packaged_url", "remote_packaged_url", "url", "transparent_url"):
        if is_http_url(item.get(key)):
            return str(item[key]).strip()
    return ""


def pick_target_path(theme_dir: Path, item: dict[str, Any]) -> Path:
    raw = str(
        item.get("planned_theme_path")
        or item.get("local_path")
        or item.get("path")
        or item.get("file")
        or ""
    ).replace("\\", "/").strip()

    if not raw and is_local_asset_path(item.get("packaged_url")):
        raw = str(item["packaged_url"]).replace("\\", "/").strip()

    ident = asset_id(item)
    if not raw:
        raw = f"assets/images/{ident}.png"
    if raw.startswith("teya-memory/"):
        return Path(raw)
    if raw.startswith("assets/"):
        return theme_dir / raw
    return theme_dir / "assets" / "images" / raw


def save_as_target_format(data: bytes, dest: Path) -> str:
    detected = sniff_image_format(data)
    if not detected:
        raise RuntimeError("downloaded bytes have unknown/corrupt image signature")

    suffix = dest.suffix.lower().lstrip(".")
    if suffix == "jpg":
        suffix = "jpeg"

    tmp = dest.with_name(f"{dest.stem}.package-tmp{dest.suffix}")
    tmp.unlink(missing_ok=True)
    try:
        if suffix == detected:
            tmp.write_bytes(data)
        elif suffix == "png" and detected in {"webp", "jpeg", "gif"}:
            from PIL import Image

            with Image.open(io.BytesIO(data)) as image:
                image.save(tmp, format="PNG", optimize=True)
        else:
            raise RuntimeError(f"refusing to save {detected} bytes as .{suffix}")

        errors = validate_image_file(tmp)
        if errors:
            raise RuntimeError("; ".join(errors))
        tmp.replace(dest)
        return detected
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    if path.suffix.lower() == ".svg":
        return None, None
    try:
        from PIL import Image

        with Image.open(path) as image:
            return image.size
    except Exception:
        return None, None


def update_registry_summary(registry: dict[str, Any], ready_count: int, total: int) -> None:
    summary = registry.get("summary")
    if not isinstance(summary, dict):
        summary = {}
        registry["summary"] = summary
    summary["generated"] = ready_count
    summary["ready"] = ready_count
    summary["pending"] = max(0, total - ready_count)


def main() -> int:
    parser = argparse.ArgumentParser(description="Package MCP assets into verified local theme files.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--theme-slug", required=True)
    parser.add_argument("--force", action="store_true", help="Re-download assets even when local files validate.")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    wp_dir = root / "teya-memory" / "wp"
    theme_dir = wp_dir / "theme" / args.theme_slug
    registry_path = root / "teya-memory" / "design" / "AURA_ASSET_REGISTRY.json"
    registry = read_json(registry_path)
    assets = registry_assets(registry)

    if not assets:
        print("ASSET_PACKAGING_BLOCKER")
        print(f"- no assets array in {registry_path}")
        return 1

    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    media_assets: list[dict[str, Any]] = []

    for item in assets:
        ident = asset_id(item)
        if not ident:
            errors.append("asset without id/registry_id")
            continue

        dest = pick_target_path(theme_dir, item)
        remote_url = pick_remote_url(item)
        existing_errors = validate_image_file(dest) if dest.is_file() else [f"missing local file: {dest}"]
        needs_download = args.force or bool(existing_errors)
        row: dict[str, Any] = {
            "id": ident,
            "local_path": str(dest.relative_to(theme_dir)).replace("\\", "/") if dest.is_relative_to(theme_dir) else str(dest),
            "remote_url": remote_url,
            "requires_background_removal": bool(item.get("requires_background_removal")),
            "source": "existing_file",
        }

        try:
            if needs_download:
                if not remote_url:
                    raise RuntimeError("; ".join(existing_errors) + "; no remote MCP/CDN URL for repair")

                evidence = probe_url(remote_url, timeout=15)
                if not evidence.get("content_range") and str(evidence.get("content_length") or "") == "16":
                    raise RuntimeError("range probe returned Content-Length: 16 without Content-Range total")

                data, evidence = download_url_bytes(remote_url, timeout=20, retries=6, chunk_size=8 * 1024)
                dest.parent.mkdir(parents=True, exist_ok=True)
                remote_format = save_as_target_format(data, dest)
                row.update(
                    {
                        "source": "range_chunks_8192",
                        "remote_content_type": evidence.get("content_type"),
                        "remote_content_range": evidence.get("content_range"),
                        "remote_content_length": evidence.get("content_length"),
                        "remote_signature_hex": evidence.get("signature_hex"),
                        "downloaded_bytes": len(data),
                        "detected_remote_format": remote_format,
                    }
                )

            post_errors = validate_image_file(dest)
            if post_errors:
                dest.unlink(missing_ok=True)
                raise RuntimeError("; ".join(post_errors))

            local_bytes = dest.read_bytes()
            local_format = sniff_image_format(local_bytes)
            width, height = image_dimensions(dest)
            row.update(
                {
                    "status": "ok",
                    "bytes": len(local_bytes),
                    "sha256": hashlib.sha256(local_bytes).hexdigest(),
                    "detected_format": local_format,
                    "width": width,
                    "height": height,
                    "decode_verified": True,
                }
            )

            rel_path = row["local_path"]
            item.setdefault("remote_packaged_url", remote_url)
            item["packaged_url"] = rel_path
            item["local_path"] = rel_path
            item["status"] = "ready"
            item["detected_format"] = local_format
            item["decode_verified"] = True
            item["bytes"] = len(local_bytes)
            media_assets.append(
                {
                    "id": ident,
                    "registry_id": ident,
                    "local_path": rel_path,
                    "path": rel_path,
                    "remote_url": remote_url,
                    "source_url": item.get("url"),
                    "transparent_url": item.get("transparent_url"),
                    "requires_background_removal": bool(item.get("requires_background_removal")),
                    "alt_text": item.get("alt_text") or item.get("alt") or "",
                    "detected_format": local_format,
                    "expected_extension": dest.suffix.lower(),
                    "content_type": f"image/{'jpeg' if local_format == 'jpeg' else local_format}",
                    "bytes": len(local_bytes),
                    "sha256": row["sha256"],
                    "width": width,
                    "height": height,
                    "download_method": "range_chunks_8192" if row["source"].startswith("range") else "existing_file",
                    "decode_verified": True,
                }
            )
        except Exception as exc:  # noqa: BLE001 - convert every asset failure into report evidence.
            row.update({"status": "blocker", "error": str(exc), "decode_verified": False})
            item["status"] = "blocker"
            item["decode_verified"] = False
            errors.append(f"{ident}: {exc}")

        rows.append(row)

    hashes: dict[str, list[str]] = {}
    for row in rows:
        if row.get("status") == "ok" and row.get("sha256"):
            hashes.setdefault(str(row["sha256"]), []).append(str(row.get("id") or ""))
    for digest, ids in sorted(hashes.items()):
        unique_ids = sorted(set(ids))
        if len(unique_ids) > 1:
            allowed = {
                str(item.get("allow_duplicate_of") or "")
                for item in assets
                if asset_id(item) in unique_ids and item.get("allow_duplicate_of")
            }
            if not allowed:
                for row in rows:
                    if row.get("id") in unique_ids:
                        row["status"] = "blocker"
                        row["error"] = "duplicate bytes with another distinct asset id"
                for item in assets:
                    if asset_id(item) in unique_ids:
                        item["status"] = "blocker"
                        item["decode_verified"] = False
                for media_item in media_assets:
                    if media_item.get("id") in unique_ids or media_item.get("registry_id") in unique_ids:
                        media_item["status"] = "blocker"
                        media_item["decode_verified"] = False
                        media_item["duplicate_asset_blocker"] = True
                errors.append(f"duplicate asset bytes detected for distinct ids {unique_ids}: sha256={digest}")

    packaged_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ready_count = sum(1 for row in rows if row.get("status") == "ok")
    update_registry_summary(registry, ready_count, len(assets))
    registry["packaged_at"] = packaged_at
    write_json(registry_path, registry)

    media_map = {
        "theme_slug": args.theme_slug,
        "generated_at": packaged_at,
        "source": "teya/scripts/package_mcp_assets.py",
        "transport_status": "pass" if not errors else "blocker",
        "assets": media_assets,
    }
    write_json(theme_dir / "media-map.json", media_map)

    report_lines = [
        f"# Asset Packaging Report — {args.theme_slug}",
        "",
        f"**Theme slug:** `{args.theme_slug}`",
        f"**Generated at:** {packaged_at}",
        "**Script:** `teya/scripts/package_mcp_assets.py`",
        f"**Verdict:** {'READY' if not errors else 'BLOCKER'}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Registry assets | {len(assets)} |",
        f"| Ready assets | {ready_count} |",
        f"| Blockers | {len(errors)} |",
        "",
        "## Download Contract",
        "",
        "- Probe: `Range: bytes=0-15`.",
        "- File size: only `Content-Range */total` is authoritative for range responses.",
        "- Chunks: 8192-byte Range requests with retries.",
        "- Verification: byte signature + Pillow `verify()` + second `load()`.",
        "- Format mismatch: WebP/JPEG/GIF to `.png` is re-encoded, never renamed.",
        "",
        "## Per Asset",
        "",
        "| id | status | source | format | bytes | WxH | local_path |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        wh = f"{row.get('width') or '?'}x{row.get('height') or '?'}"
        report_lines.append(
            f"| {row.get('id', '')} | {row.get('status', '')} | {row.get('source', '')} | "
            f"{row.get('detected_format', row.get('detected_remote_format', ''))} | {row.get('bytes', '')} | "
            f"{wh} | `{row.get('local_path', '')}` |"
        )
    if errors:
        report_lines.extend(["", "## Blockers", ""])
        report_lines.extend(f"- {error}" for error in errors)
    (wp_dir / "asset-packaging-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    fragment = [
        "=== AURORA-TEAM-ASSET-PACKAGER (ASSETS/CUTOUTS) ===",
        "",
        f"**Theme slug:** `{args.theme_slug}`  ",
        f"**Verdict:** {'READY' if not errors else 'BLOCKER'}  ",
        f"**Generated at:** {packaged_at}",
        "",
        "## Deliverables",
        "",
        f"- `teya-memory/wp/theme/{args.theme_slug}/media-map.json`",
        "- `teya-memory/wp/asset-packaging-report.md`",
        "- `teya-memory/design/AURA_ASSET_REGISTRY.json`",
        "",
        "## Contract",
        "",
        "Used canonical script `teya/scripts/package_mcp_assets.py`; no ad-hoc downloader.",
        f"Ready assets: {ready_count}/{len(assets)}.",
    ]
    if errors:
        fragment.extend(["", "## Blockers", ""])
        fragment.extend(f"- {error}" for error in errors)
    fragment_path = root / "teya-memory" / "fragments" / "aurora-team-asset-packager.md"
    fragment_path.parent.mkdir(parents=True, exist_ok=True)
    fragment_path.write_text("\n".join(fragment) + "\n", encoding="utf-8")

    if errors:
        print("ASSET_PACKAGING_BLOCKER")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"ASSET_PACKAGING_READY: {ready_count}/{len(assets)} assets verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
