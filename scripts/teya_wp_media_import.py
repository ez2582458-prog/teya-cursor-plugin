#!/usr/bin/env python3
"""WordPress Media Library import helpers for Teya Aurora deploy."""
from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from teya_release_gate import IMAGE_EXTENSIONS, validate_image_file

# Fallback alts when registry omits alt_text (kovcheg-kids defaults).
DEFAULT_ALT_BY_FILE: dict[str, str] = {
    "hero-mascot-kovcheg.png": "Робот Ковчег — маскот школы вайбкодинга",
    "benefit-yellow-ai-safe.png": "Ребёнок за ноутбуком с иконками безопасного AI",
    "benefit-green-projects.png": "Скриншоты детских мини-игр и приложений",
    "benefit-pink-demo-day.png": "Demo Day — презентация проекта",
    "form-robot-wave.png": "Робот Ковчег приглашает на пробное занятие",
    "blog-thumb-ai-safety.png": "Щит и детский ноутбук",
    "program-roadmap-12w.png": "Инфографика 12 недель и 4 модулей",
    "blog-thumb-b01.png": "Иллюстрация ребёнка и AI-редактора",
    "blog-thumb-b03.png": "Коллаж детских проектов",
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_manifest(
    registry_path: Path,
    theme_slug: str,
    theme_images_dir: Path,
    *,
    extra_files: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build import manifest from AURA_ASSET_REGISTRY.json + optional extra theme images."""
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    assets: list[dict[str, Any]] = []
    seen_files: set[str] = set()

    for item in data.get("assets", []):
        raw_path = str(item.get("local_path") or item.get("planned_theme_path") or item.get("path") or "").replace("\\", "/")
        if raw_path.startswith("assets/images/"):
            file_name = raw_path[len("assets/images/") :]
        elif raw_path.startswith("assets/"):
            file_name = raw_path[len("assets/") :]
            if file_name.startswith("images/"):
                file_name = file_name[len("images/") :]
        else:
            file_name = raw_path
        file_name = file_name.strip("/")
        if not file_name or Path(file_name).is_absolute() or ".." in Path(file_name).parts:
            continue
        seen_files.add(file_name)
        alt = (item.get("alt_text") or DEFAULT_ALT_BY_FILE.get(Path(file_name).name) or "").strip()
        if not alt:
            raise RuntimeError(f"Missing alt_text for asset {item.get('id')} ({file_name})")
        local_path = theme_images_dir / file_name
        if local_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_errors = validate_image_file(local_path)
            if image_errors:
                raise RuntimeError(f"Invalid image asset {local_path}: {'; '.join(image_errors)}")
        assets.append(
            {
                "id": item.get("id", Path(file_name).stem),
                "registry_id": item.get("id", file_name),
                "file": file_name,
                "local_source_path": str(local_path).replace("\\", "/"),
                "alt_text": alt,
                "used_in": item.get("used_in", []),
                "requires_background_removal": bool(
                    item.get("requires_background_removal", item.get("transparent_url"))
                ),
            }
        )

    for extra in extra_files or []:
        file_name = str(extra.get("file", "")).replace("\\", "/").strip("/")
        if not file_name or Path(file_name).is_absolute() or ".." in Path(file_name).parts or file_name in seen_files:
            continue
        seen_files.add(file_name)
        alt = (extra.get("alt_text") or DEFAULT_ALT_BY_FILE.get(Path(file_name).name) or "").strip()
        if not alt:
            raise RuntimeError(f"Missing alt_text for extra file {file_name}")
        local_path = theme_images_dir / file_name
        if local_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_errors = validate_image_file(local_path)
            if image_errors:
                raise RuntimeError(f"Invalid image asset {local_path}: {'; '.join(image_errors)}")
        assets.append(
            {
                "id": extra.get("registry_id", Path(file_name).stem),
                "registry_id": extra.get("registry_id", Path(file_name).stem),
                "file": file_name,
                "local_source_path": str(local_path).replace("\\", "/"),
                "alt_text": alt,
                "used_in": extra.get("used_in", []),
                "requires_background_removal": False,
            }
        )

    return {
        "theme_slug": theme_slug,
        "assets": assets,
    }


def manifest_to_b64(manifest: dict[str, Any]) -> str:
    return base64.b64encode(json.dumps(manifest, ensure_ascii=False).encode("utf-8")).decode("ascii")


MEDIA_IMPORT_PHP = r"""
// --- Teya WP Media Import (wp-media-upload-contract.md) ---
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';
require_once ABSPATH . 'wp-admin/includes/image.php';

function teya_import_theme_image( $abs_path, $registry_id, $alt_text ) {
	if ( ! file_exists( $abs_path ) ) {
		return new WP_Error( 'missing_file', 'File not found: ' . $abs_path );
	}
	$existing = get_posts(
		array(
			'post_type'      => 'attachment',
			'posts_per_page' => 1,
			'fields'         => 'ids',
			'meta_query'     => array(
				array(
					'key'   => 'teya_registry_id',
					'value' => $registry_id,
				),
			),
		)
	);
	if ( ! empty( $existing[0] ) ) {
		$aid = (int) $existing[0];
		update_post_meta( $aid, '_wp_attachment_image_alt', $alt_text );
		return $aid;
	}
	$filename = basename( $abs_path );
	$contents = file_get_contents( $abs_path );
	if ( false === $contents ) {
		return new WP_Error( 'read_fail', 'Cannot read: ' . $abs_path );
	}
	$upload = wp_upload_bits( $filename, null, $contents );
	if ( ! empty( $upload['error'] ) ) {
		return new WP_Error( 'upload_fail', $upload['error'] );
	}
	$filetype   = wp_check_filetype( $filename, null );
	$attachment = array(
		'post_mime_type' => $filetype['type'],
		'post_title'     => sanitize_file_name( pathinfo( $filename, PATHINFO_FILENAME ) ),
		'post_content'   => '',
		'post_status'    => 'inherit',
	);
	$aid = wp_insert_attachment( $attachment, $upload['file'] );
	if ( is_wp_error( $aid ) ) {
		return $aid;
	}
	$attach_data = wp_generate_attachment_metadata( $aid, $upload['file'] );
	wp_update_attachment_metadata( $aid, $attach_data );
	update_post_meta( $aid, '_wp_attachment_image_alt', $alt_text );
	update_post_meta( $aid, 'teya_registry_id', $registry_id );
	return (int) $aid;
}

$teya_manifest = json_decode( base64_decode( '__MEDIA_MANIFEST_B64__' ), true );
$teya_theme_dir = get_template_directory();
$teya_map = array(
	'theme_slug'      => $teya_manifest['theme_slug'] ?? wp_get_theme()->get_stylesheet(),
	'public_site_url' => home_url( '/' ),
	'imported_at'     => gmdate( 'c' ),
	'assets'          => array(),
	'verdict'         => 'pass',
);
foreach ( $teya_manifest['assets'] as $teya_asset ) {
	$file = $teya_asset['file'] ?? '';
	$registry_id = $teya_asset['registry_id'] ?? ( $teya_asset['id'] ?? $file );
	$alt = $teya_asset['alt_text'] ?? '';
	$path = $teya_theme_dir . '/assets/images/' . ltrim( $file, '/' );
	$aid = teya_import_theme_image( $path, $registry_id, $alt );
	if ( is_wp_error( $aid ) ) {
		echo 'MEDIA_ERR|' . $registry_id . '|' . $aid->get_error_message() . "\n";
		$teya_map['verdict'] = 'fail';
		continue;
	}
	$url = wp_get_attachment_url( $aid );
	$teya_map['assets'][] = array(
		'id'                => $registry_id,
		'registry_id'       => $registry_id,
		'file'              => $file,
		'local_source_path' => 'teya-memory/wp/theme/' . $teya_map['theme_slug'] . '/assets/images/' . $file,
		'attachment_id'     => $aid,
		'attachment_url'    => $url,
		'alt_text'          => $alt,
		'used_in'           => $teya_asset['used_in'] ?? array(),
	);
	echo 'MEDIA_OK|' . $registry_id . '|' . $aid . '|' . $url . "\n";
}
file_put_contents(
	$teya_theme_dir . '/media-map.json',
	wp_json_encode( $teya_map, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT )
);
echo 'MEDIA_MAP_JSON=' . base64_encode( wp_json_encode( $teya_map, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) ) . "\n";
echo "MEDIA_IMPORT_DONE\n";
"""


def inject_media_import_php(bootstrap_php: str, manifest_b64: str) -> str:
    snippet = MEDIA_IMPORT_PHP.replace("__MEDIA_MANIFEST_B64__", manifest_b64)
    return bootstrap_php.rstrip() + "\n" + snippet


def parse_media_import_output(output: str) -> dict[str, Any] | None:
    match = re.search(r"^MEDIA_MAP_JSON=(.+)$", output, re.MULTILINE)
    if not match:
        return None
    raw = base64.b64decode(match.group(1).strip())
    return json.loads(raw.decode("utf-8"))


def write_wp_media_artifacts(
    wp_dir: Path,
    media_map: dict[str, Any],
    *,
    theme_dir: Path | None = None,
) -> None:
    wp_dir.mkdir(parents=True, exist_ok=True)
    if media_map.get("verdict") == "pass":
        media_map.setdefault("transport_status", "pass")
        media_map.setdefault("import_status", "pass")
    map_path = wp_dir / "wp-media-map.json"
    map_path.write_text(json.dumps(media_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# WP Media Import Log",
        "",
        f"**Imported at:** {media_map.get('imported_at', _iso_now())}",
        f"**Theme slug:** {media_map.get('theme_slug', '')}",
        f"**Public URL:** {media_map.get('public_site_url', '')}",
        f"**Verdict:** {media_map.get('verdict', 'unknown')}",
        "",
        "| registry_id | file | attachment_id | alt_text |",
        "| --- | --- | --- | --- |",
    ]
    for asset in media_map.get("assets", []):
        lines.append(
            f"| {asset.get('registry_id', '')} | {asset.get('file', '')} | "
            f"{asset.get('attachment_id', '')} | {asset.get('alt_text', '')} |"
        )
    (wp_dir / "wp-media-import-log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if theme_dir is not None:
        theme_dir.mkdir(parents=True, exist_ok=True)
        (theme_dir / "media-map.json").write_text(
            json.dumps(media_map, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def media_import_status(media_map: dict[str, Any] | None) -> tuple[str, str, list[str]]:
    if media_map is None:
        return "fail", "fail", ["wp-media-map.json not created"]
    missing: list[str] = []
    for asset in media_map.get("assets", []):
        if not asset.get("attachment_id"):
            missing.append(asset.get("registry_id", asset.get("file", "?")))
        alt = (asset.get("alt_text") or "").strip()
        if len(alt) < 8 or alt.lower() in {"image", "photo", "mascot", "placeholder"}:
            missing.append(f"bad_alt:{asset.get('registry_id', '?')}")
    verdict = media_map.get("verdict", "fail")
    map_status = "pass" if verdict == "pass" and not missing else "fail"
    import_status = "pass" if media_map.get("assets") and map_status == "pass" else "fail"
    return map_status, import_status, missing
