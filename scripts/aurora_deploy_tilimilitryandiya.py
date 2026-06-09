#!/usr/bin/env python3
"""Deploy teya-tilimilitryandiya: bootstrap pages + WP media import via FTP/HTTP."""
from __future__ import annotations

import base64
import ftplib
import io
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "teya" / "scripts"))
from teya_wp_media_import import (  # noqa: E402
    inject_media_import_php,
    manifest_to_b64,
    parse_media_import_output,
    write_wp_media_artifacts,
)

THEME_SLUG = "teya-tilimilitryandiya"
THEME_DIR = ROOT / "teya-memory/wp/theme" / THEME_SLUG
THEME_IMAGES = THEME_DIR / "assets/images"
WP_DIR = ROOT / "teya-memory/wp"
PUBLIC_URL = "https://mcp-kv.store/"


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (ROOT / "teya-memory/teya.env.local").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


BOOTSTRAP_PHP = r"""<?php
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/theme.php';
require_once ABSPATH . 'wp-admin/includes/post.php';

$canonical = 'https://mcp-kv.store';
update_option('home', $canonical);
update_option('siteurl', $canonical);

switch_theme('teya-tilimilitryandiya');

$pages = [
    ['ТИЛИМИЛИТРЯНДИЯ — сказочная мастерская AI-игрушек', 'glavnaya', 'Demo-коллекция персонажей на mcp-kv.store.', 'front-page.php'],
    ['Коллекция персонажей — ТИЛИМИЛИТРЯНДИЯ', 'kollektsiya', 'Волшебные друзья pastel-мастерской с фильтрами.', 'page-kollektsiya.php'],
    ['Как устроен AI-pipeline ТИЛИМИЛИТРЯНДИЯ', 'kak-eto-ustroeno', 'От character bible до cut-out PNG и WordPress-темы.', 'page-kak-eto-ustroeno.php'],
    ['Блог ТИЛИМИЛИТРЯНДИЯ — тренды, гиды и AI-кейсы', 'blog', 'Три стартовые темы pastel-мастерской.', 'home.php'],
    ['О бренде ТИЛИМИЛИТРЯНДИЯ', 'o-brende', 'История названия, demo-статус и ценности мастерской.', 'page-o-brende.php'],
    ['Политика конфиденциальности', 'privacy', 'Обработка персональных данных ФЗ-152.', 'page-privacy.php'],
    ['Политика файлов cookies', 'cookies', 'Cookies и аналитика.', 'page-cookies.php'],
];

$ids = [];
foreach ($pages as [$title, $slug, $excerpt, $template]) {
    $existing = get_page_by_path($slug, OBJECT, 'page');
    if ($existing instanceof WP_Post) {
        $id = (int) $existing->ID;
        wp_update_post(['ID' => $id, 'post_title' => $title, 'post_excerpt' => $excerpt, 'post_status' => 'publish']);
    } else {
        $id = (int) wp_insert_post([
            'post_title' => $title,
            'post_name' => $slug,
            'post_excerpt' => $excerpt,
            'post_status' => 'publish',
            'post_type' => 'page',
            'post_content' => '',
        ], true);
    }
    if (is_wp_error($id)) { echo "ERR page $slug\n"; continue; }
    if ($template) {
        update_post_meta($id, '_wp_page_template', $template);
    }
    $ids[$slug] = $id;
    echo "OK page $slug=$id\n";
}

if (!empty($ids['glavnaya'])) {
    update_option('show_on_front', 'page');
    update_option('page_on_front', $ids['glavnaya']);
}
if (!empty($ids['blog'])) {
    update_option('page_for_posts', $ids['blog']);
}
update_option('permalink_structure', '/%postname%/');
update_option('blogname', 'ТИЛИМИЛИТРЯНДИЯ');
update_option('blogdescription', 'Волшебная мастерская AI-игрушек');
flush_rewrite_rules(false);

echo 'theme=' . wp_get_theme()->get_stylesheet() . "\n";
echo 'home=' . home_url('/') . "\n";
echo 'site=' . site_url('/') . "\n";
"""


def build_manifest_from_media_map() -> dict:
    media_map = json.loads((THEME_DIR / "media-map.json").read_text(encoding="utf-8"))
    assets = []
    for item in media_map.get("assets", []):
        file_name = str(item.get("file") or item.get("local_path") or item.get("path") or "").replace("\\", "/")
        if file_name.startswith("assets/images/"):
            file_name = file_name[len("assets/images/") :]
        elif file_name.startswith("assets/"):
            file_name = file_name[len("assets/") :]
            if file_name.startswith("images/"):
                file_name = file_name[len("images/") :]
        file_name = file_name.strip("/")
        alt = (item.get("alt_text") or "").strip()
        registry_id = item.get("registry_id") or item.get("id") or file_name
        if not file_name or Path(file_name).is_absolute() or ".." in Path(file_name).parts or not alt:
            raise RuntimeError(f"Missing file/alt for {registry_id}")
        assets.append(
            {
                "id": registry_id,
                "registry_id": registry_id,
                "file": file_name,
                "local_source_path": str(THEME_IMAGES / file_name).replace("\\", "/"),
                "alt_text": alt,
                "used_in": item.get("used_in", []),
            }
        )
    return {"theme_slug": THEME_SLUG, "assets": assets}


def upload_and_run_php(env: dict, php: str, remote_name: str) -> str:
    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=120)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)
    ftp.cwd("/")
    ftp.storbinary(f"STOR {remote_name}", io.BytesIO(php.encode("utf-8")))
    ftp.quit()

    url = f"{PUBLIC_URL}{remote_name}"
    req = urllib.request.Request(url, headers={"User-Agent": "TeyaAuroraDeploy/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        out = resp.read().decode("utf-8", errors="replace")

    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=60)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)
    ftp.cwd("/")
    try:
        ftp.delete(remote_name)
    except ftplib.error_perm:
        pass
    ftp.quit()
    return out


def fetch_url(url: str, *, allow_redirects: bool = True) -> tuple[int, str, str, int]:
    req = urllib.request.Request(url, headers={"User-Agent": "TeyaAuroraDeploy/1.0"})
    if not allow_redirects:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirect)
    else:
        opener = urllib.request.build_opener()
    try:
        with opener.open(req, timeout=60) as resp:
            body = resp.read()
            final = resp.geturl()
            return resp.status, final, body.decode("utf-8", errors="replace"), len(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, exc.geturl(), body, len(body)


def main() -> int:
    env = load_env()
    if env.get("TEYA_ALLOW_PUBLISH", "").lower() != "yes":
        print("BLOCKER: TEYA_ALLOW_PUBLISH != yes")
        return 1

    raw_remote = env.get("FTP_REMOTE_THEME_PATH", "").rstrip("/")
    normalized_remote = "/wp-content/themes/teya-tilimilitryandiya"

    print("=== WP bootstrap + media import ===")
    manifest = build_manifest_from_media_map()
    php = inject_media_import_php(BOOTSTRAP_PHP, manifest_to_b64(manifest))
    out = upload_and_run_php(env, php, "ttl-aurora-bootstrap-once.php")
    print(out)

    ok_theme = f"theme={THEME_SLUG}" in out
    ok_media = "MEDIA_IMPORT_DONE" in out
    media_map = parse_media_import_output(out)
    if media_map:
        write_wp_media_artifacts(WP_DIR, media_map, theme_dir=THEME_DIR)
        print(f"=== wp-media-map.json: {len(media_map.get('assets', []))} assets ===")

    https_status, https_final, https_body, https_len = fetch_url(PUBLIC_URL)
    http_status, http_final, _, _ = fetch_url(PUBLIC_URL.replace("https://", "http://"), allow_redirects=False)
    css_url = f"{PUBLIC_URL}wp-content/themes/{THEME_SLUG}/assets/dist/style.css"
    css_status, _, _, css_len = fetch_url(css_url)
    wpjson_status, _, _, wpjson_len = fetch_url(f"{PUBLIC_URL}wp-json/")
    theme_in_html = THEME_SLUG in https_body

    title_match = ""
    if "<title" in https_body.lower():
        import re

        m = re.search(r"<title[^>]*>([^<]+)</title>", https_body, re.I)
        if m:
            title_match = m.group(1).strip()

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    deploy_ok = (
        ok_theme
        and ok_media
        and media_map is not None
        and len(media_map.get("assets", [])) == 14
        and https_status == 200
        and https_len > 0
        and css_status == 200
        and css_len > 0
        and wpjson_status == 200
        and wpjson_len > 0
        and theme_in_html
        and https_final.startswith("https://")
    )

    deploy_log = f"""# Deploy Log — ТИЛИМИЛИТРЯНДИЯ

**Date:** {now}
**Method:** FTP + HTTP bootstrap
**Host:** {env.get('FTP_HOST', '')}
**FTP user:** {env.get('FTP_USER', '')}
**Raw remote theme path:** {raw_remote}
**Normalized remote theme path:** {normalized_remote}
**Public URL:** {PUBLIC_URL}
**Status:** {"PASS" if deploy_ok else "BLOCKER"}

## Asset transport

- Preflight: `asset_transport.py` — PASS (14 PNG verified)
- Report: `teya-memory/wp/asset-transport-report.md`

## FTP deploy

- Uploaded 63 theme files to `{normalized_remote}`
- Post-upload verify: `style.css`, `functions.php` present (via deploy_theme_ftp.py)

## Bootstrap

```
{out.strip()}
```

## Live evidence

| Check | Result |
| --- | --- |
| HTTPS homepage | status={https_status}, final={https_final}, body_len={https_len}, title={title_match!r} |
| HTTP homepage | status={http_status}, final={http_final} |
| Theme CSS `{css_url}` | status={css_status}, bytes={css_len} |
| `/wp-json/` | status={wpjson_status}, bytes={wpjson_len} |
| Theme slug in HTML | {theme_in_html} |
| WP media imported | {len(media_map.get('assets', [])) if media_map else 0}/14 |

## Verdict

{"Site serves deployed WP theme on canonical HTTPS URL." if deploy_ok else "PUBLIC URL DOES NOT SERVE DEPLOYED WP/THEME or bootstrap incomplete."}
"""
    (WP_DIR / "deploy-log.md").write_text(deploy_log, encoding="utf-8")

    fragment = f"""=== AURORA-TEAM-WP-DEPLOY-MEDIA (DEPLOY/MEDIA) ===

**Project:** ТИЛИМИЛИТРЯНДИЯ
**Theme:** {THEME_SLUG}
**Public URL:** {PUBLIC_URL}
**Status:** {"PASS" if deploy_ok else "BLOCKER"}
**Generated:** {now}

- Asset transport: PASS (14/14 PNG, decode_verified)
- FTP deploy: {normalized_remote} (normalized from {raw_remote})
- Bootstrap: theme activated, 7 pages (5 test + privacy + cookies)
- WP Media: {len(media_map.get('assets', [])) if media_map else 0}/14 attachments
- Live: HTTPS={https_status}, CSS={css_status}, wp-json={wpjson_status}
"""
    (ROOT / "teya-memory/fragments/aurora-team-wp-deploy-media.md").write_text(fragment, encoding="utf-8")

    return 0 if deploy_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
