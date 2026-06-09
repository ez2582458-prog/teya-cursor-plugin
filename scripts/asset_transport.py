#!/usr/bin/env python3
"""Asset transport preflight: remote MCP/CDN URLs -> verified local theme files."""
from __future__ import annotations

import argparse
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from asset_download import download_url_bytes
from teya_release_gate import sniff_image_format, validate_image_file


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def is_http_url(value: Any) -> bool:
    text = str(value or "").strip()
    return text.startswith(("http://", "https://"))


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_media_assets(media_map: dict[str, Any]) -> list[dict[str, Any]]:
    assets = media_map.get("assets")
    if isinstance(assets, list):
        return [item for item in assets if isinstance(item, dict)]
    if isinstance(assets, dict):
        normalized: list[dict[str, Any]] = []
        for registry_id, item in assets.items():
            if isinstance(item, dict):
                item.setdefault("registry_id", registry_id)
                normalized.append(item)
        return normalized
    return []


def registry_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assets = registry.get("assets") if isinstance(registry.get("assets"), list) else []
    return {
        str(item.get("id") or item.get("registry_id")): item
        for item in assets
        if isinstance(item, dict) and (item.get("id") or item.get("registry_id"))
    }


def pick_remote_url(item: dict[str, Any]) -> str:
    if item.get("requires_background_removal"):
        for key in ("transparent_url", "packaged_url", "remote_packaged_url"):
            if is_http_url(item.get(key)):
                return str(item[key]).strip()
        return ""
    for key in ("packaged_url", "remote_packaged_url", "transparent_url", "url"):
        if is_http_url(item.get(key)):
            return str(item[key]).strip()
    return ""


def target_path(theme_dir: Path, media_item: dict[str, Any], registry_item: dict[str, Any]) -> Path | None:
    raw = str(
        media_item.get("path")
        or media_item.get("file")
        or registry_item.get("planned_theme_path")
        or ""
    ).strip()
    if not raw:
        return None

    raw = raw.replace("\\", "/")
    if raw.startswith("teya-memory/"):
        return Path(raw)
    if raw.startswith("assets/"):
        return theme_dir / raw
    return theme_dir / "assets" / "images" / raw


def save_as_target_format(data: bytes, dest: Path) -> str:
    detected = sniff_image_format(data)
    if not detected:
        raise RuntimeError("downloaded bytes are not a known image format")

    suffix = dest.suffix.lower().lstrip(".")
    if suffix == "jpg":
        suffix = "jpeg"

    tmp = dest.with_name(f"{dest.stem}.transport-tmp{dest.suffix}")
    try:
        if suffix == detected:
            tmp.write_bytes(data)
        elif suffix == "png" and detected in {"webp", "jpeg", "gif"}:
            from PIL import Image

            with Image.open(io.BytesIO(data)) as image:
                image.save(tmp, format="PNG")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and verify theme assets before deploy.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--theme-slug", required=True)
    parser.add_argument("--force", action="store_true", help="Re-download even if local file is valid.")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    wp_dir = root / "teya-memory" / "wp"
    theme_dir = wp_dir / "theme" / args.theme_slug
    registry = read_json(root / "teya-memory" / "design" / "AURA_ASSET_REGISTRY.json")
    media_map_path = theme_dir / "media-map.json"
    media_map = read_json(media_map_path)
    registry_map = registry_by_id(registry)
    rows: list[dict[str, Any]] = []
    errors: list[str] = []

    for media_item in normalize_media_assets(media_map):
        registry_id = str(media_item.get("registry_id") or media_item.get("id") or "").strip()
        registry_item = registry_map.get(registry_id, {})
        dest = target_path(theme_dir, media_item, registry_item)
        if dest is None:
            errors.append(f"{registry_id or '?'}: no target path in media-map/registry")
            continue
        if dest.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        remote_url = pick_remote_url(registry_item)
        local_errors = validate_image_file(dest) if dest.is_file() else [f"missing local file: {dest}"]
        needs_download = args.force or bool(local_errors)

        row: dict[str, Any] = {
            "registry_id": registry_id,
            "path": str(dest.relative_to(theme_dir)).replace("\\", "/"),
            "remote_url": remote_url,
            "source": "existing_file",
        }

        try:
            if needs_download:
                if not remote_url:
                    raise RuntimeError("; ".join(local_errors) + "; no remote URL for repair")
                data, evidence = download_url_bytes(remote_url, timeout=20, retries=5, chunk_size=8 * 1024)
                dest.parent.mkdir(parents=True, exist_ok=True)
                detected = save_as_target_format(data, dest)
                row.update(
                    {
                        "source": "range_download",
                        "remote_content_type": evidence.get("content_type"),
                        "remote_content_range": evidence.get("content_range"),
                        "remote_signature_hex": evidence.get("signature_hex"),
                        "downloaded_bytes": len(data),
                        "detected_remote_format": detected,
                    }
                )

            post_errors = validate_image_file(dest)
            if post_errors:
                raise RuntimeError("; ".join(post_errors))

            row.update(
                {
                    "bytes": dest.stat().st_size,
                    "detected_local_format": sniff_image_format(dest.read_bytes()),
                    "decode_verified": True,
                    "status": "ok",
                }
            )
            media_item["local_source_path"] = str(dest.relative_to(root)).replace("\\", "/")
            media_item["id"] = registry_id
            media_item["registry_id"] = registry_id
            media_item["bytes"] = row["bytes"]
            media_item["detected_format"] = row["detected_local_format"]
            media_item["decode_verified"] = True
        except Exception as exc:  # noqa: BLE001 - report per-asset blockers.
            row.update({"status": "blocker", "error": str(exc)})
            errors.append(f"{registry_id or dest.name}: {exc}")

        rows.append(row)

    media_map["transport_checked_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    media_map["transport_status"] = "pass" if not errors else "blocker"
    write_json(media_map_path, media_map)

    report_lines = [
        "# Asset Transport Report",
        "",
        f"**Theme slug:** {args.theme_slug}",
        f"**Status:** {'PASS' if not errors else 'BLOCKER'}",
        f"**Generated at:** {media_map['transport_checked_at']}",
        "",
        "| registry_id | status | source | local format | bytes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        report_lines.append(
            f"| {row.get('registry_id', '')} | {row.get('status', '')} | {row.get('source', '')} | "
            f"{row.get('detected_local_format', '')} | {row.get('bytes', '')} |"
        )
    if errors:
        report_lines.extend(["", "## Blockers", ""])
        report_lines.extend(f"- {error}" for error in errors)
    (wp_dir / "asset-transport-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    if errors:
        print("ASSET_TRANSPORT_BLOCKER")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"ASSET_TRANSPORT_PASS: {len(rows)} assets verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

