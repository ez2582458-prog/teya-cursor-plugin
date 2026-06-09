#!/usr/bin/env python3
"""Deploy teya-kovcheg-kids: FTP theme + bootstrap pages/posts + menus."""
from __future__ import annotations

import base64
import ftplib
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "teya" / "scripts"))
from md_to_wp_html import md_block_to_html  # noqa: E402
from teya_wp_media_import import (  # noqa: E402
    build_manifest,
    inject_media_import_php,
    manifest_to_b64,
    parse_media_import_output,
    write_wp_media_artifacts,
)

PACK = ROOT / "teya-memory/wp/page-content-pack.md"
REGISTRY = ROOT / "teya-memory/design/AURA_ASSET_REGISTRY.json"
THEME_SLUG = "teya-kovcheg-kids"
THEME_DIR = ROOT / "teya-memory/wp/theme" / THEME_SLUG
THEME_IMAGES = THEME_DIR / "assets/images"
WP_DIR = ROOT / "teya-memory/wp"


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (ROOT / "teya-memory/teya.env.local").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def extract_section(pack: str, start_marker: str, end_markers: list[str]) -> str:
    start = pack.index(start_marker)
    end = len(pack)
    for em in end_markers:
        pos = pack.find(em, start + len(start_marker))
        if pos != -1:
            end = min(end, pos)
    block = pack[start:end]
    for skip in ("| Поле |", "**H1:**", "**Title:**", "**Description:**"):
        pass
    # Remove metadata table at top
    m = re.search(r"(?:^## .+|^### .+)", block, re.MULTILINE)
    if m and m.start() > 0:
        block = block[m.start() :]
    # Skip first H1 line if duplicated
    lines = block.strip().splitlines()
    out: list[str] = []
    skipped_h1 = False
    for line in lines:
        if not skipped_h1 and line.startswith("## ") and "GEO" not in line:
            skipped_h1 = True
            continue
        if line.startswith("| **") and "** |" in line:
            continue
        if line.startswith("```"):
            break
        out.append(line)
    return "\n".join(out).strip()


def blog_posts() -> list[dict]:
    if os.environ.get("TEYA_ALLOW_LEGACY_BLOG_PUBLISH") != "yes":
        return []
    pack = PACK.read_text(encoding="utf-8")
    specs = [
        {
            "slug": "vajbkoding-dlya-detey",
            "marker": "# B01 —",
            "title": "Что такое вайбкодинг для детей простыми словами",
            "excerpt": "Объясняем вайбкодинг без жаргона: чем отличается от Scratch и Python и когда имеет смысл записаться на курс.",
            "thumb": "blog-thumb-b01.png",
        },
        {
            "slug": "bezopasnost-chatgpt-cursor",
            "marker": "# B02 —",
            "title": "Безопасно ли ребёнку ChatGPT и Cursor: правила для родителей",
            "excerpt": "Чек-лист для родителей: личные данные, списывание, контроль экрана. Как мы учим этике на курсе.",
            "thumb": "blog-thumb-ai-safety.png",
        },
        {
            "slug": "5-proektov-s-ai",
            "marker": "# B03 —",
            "title": "5 проектов, которые подросток может собрать с AI",
            "excerpt": "От промпт-квеста до Telegram-сценария — и как довести идею до Demo Day за 12 недель.",
            "thumb": "blog-thumb-b03.png",
        },
    ]
    posts = []
    for i, spec in enumerate(specs):
        end = ["# B0", "# `/", "## Legal", "---\n\n# `/"]
        body_md = extract_section(pack, spec["marker"], [e for e in end if e != spec["marker"]])
        posts.append(
            {
                "slug": spec["slug"],
                "title": spec["title"],
                "excerpt": spec["excerpt"],
                "content": md_block_to_html(body_md),
                "thumb_file": spec["thumb"],
            }
        )
    return posts


BOOTSTRAP_PHP = r"""<?php
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/theme.php';
require_once ABSPATH . 'wp-admin/includes/post.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';
require_once ABSPATH . 'wp-admin/includes/image.php';

switch_theme('teya-kovcheg-kids');

$pages = [
    ['Главная', 'glavnaya', '12 недель онлайн: нейросети, Cursor, 2–4 проекта и Demo Day.', ''],
    ['Программа 12 недель', 'programma', '4 модуля: AI, творчество, Cursor, Demo Day.', 'page-programma.php'],
    ['Пробное занятие', 'probnoe', 'Познакомим ребёнка 10–16 с AI и вайбкодингом.', 'page-probnoe.php'],
    ['Формат и расписание', 'format', 'Онлайн, 1 занятие в неделю, группа 6–10.', 'page-format.php'],
    ['Тарифы Kids', 'tarify', 'Сравнение форматов без публикации цен.', 'page-tarify.php'],
    ['Политика конфиденциальности', 'politika-konfidencialnosti', 'Обработка ПДн ФЗ-152.', 'page-politika-konfidencialnosti.php'],
    ['Политика cookies', 'politika-cookies', 'Cookies и аналитика.', 'page-politika-cookies.php'],
    ['Блог', 'blog', 'Статьи о вайбкодинге для родителей.', ''],
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
    if ($template) update_post_meta($id, '_wp_page_template', $template);
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
update_option('blogname', 'Ковчег Kids');
update_option('blogdescription', 'Вайбкодинг для детей 10–16');
flush_rewrite_rules(false);

// Primary menu
$menu_name = 'Primary Kids';
$menu = wp_get_nav_menu_object($menu_name);
if (!$menu) {
    $menu_id = wp_create_nav_menu($menu_name);
} else {
    $menu_id = (int) $menu->term_id;
}
$locs = get_theme_mod('nav_menu_locations', []);
$locs['primary'] = $menu_id;
set_theme_mod('nav_menu_locations', $locs);

$menu_items = [
    ['Программа', '/programma/'],
    ['Формат', '/format/'],
    ['Тарифы', '/tarify/'],
    ['Блог', '/blog/'],
    ['Записаться', '/probnoe/'],
];
foreach ($menu_items as [$label, $path]) {
    $slug = trim($path, '/');
    $page = get_page_by_path($slug);
    if ($page) {
        wp_update_nav_menu_item($menu_id, 0, [
            'menu-item-title' => $label,
            'menu-item-object' => 'page',
            'menu-item-object-id' => $page->ID,
            'menu-item-type' => 'post_type',
            'menu-item-status' => 'publish',
        ]);
    }
}

$posts_json = base64_decode('__POSTS_B64__');
$posts = json_decode($posts_json, true);
$theme_uri = get_template_directory_uri();
foreach ($posts as $p) {
    $existing = get_page_by_path($p['slug'], OBJECT, 'post');
    if ($existing instanceof WP_Post) {
        $pid = (int) $existing->ID;
        wp_update_post([
            'ID' => $pid,
            'post_title' => $p['title'],
            'post_name' => $p['slug'],
            'post_content' => $p['content'],
            'post_excerpt' => $p['excerpt'],
            'post_status' => 'publish',
        ]);
    } else {
        $pid = (int) wp_insert_post([
            'post_title' => $p['title'],
            'post_name' => $p['slug'],
            'post_content' => $p['content'],
            'post_excerpt' => $p['excerpt'],
            'post_status' => 'publish',
            'post_type' => 'post',
        ], true);
    }
    if (is_wp_error($pid)) { echo 'ERR post '.$p['slug']."\n"; continue; }
    echo 'OK post '.$p['slug'].'='.$pid."\n";
}

$hello = get_posts(['name' => 'hello-world', 'post_type' => 'post', 'post_status' => 'any', 'numberposts' => 1]);
if (!empty($hello[0])) { wp_trash_post((int) $hello[0]->ID); echo 'TRASH hello-world'."\n"; }

echo 'theme=' . wp_get_theme()->get_stylesheet() . "\n";
echo 'home=' . home_url('/') . "\n";
echo 'posts=' . wp_count_posts()->publish . "\n";
"""


def deploy_ftp_theme(env: dict) -> int:
    cmd = [
        sys.executable,
        str(ROOT / "teya/scripts/deploy_theme_ftp.py"),
        "--project-root",
        str(ROOT),
        "--theme-slug",
        "teya-kovcheg-kids",
        "--remote",
        "/wp-content/themes/teya-kovcheg-kids",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout or r.stderr)
    return r.returncode


def upload_and_run_php(env: dict, php: str, remote_name: str) -> str:
    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=120)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)
    ftp.cwd("/")
    ftp.storbinary(f"STOR {remote_name}", io.BytesIO(php.encode("utf-8")))
    ftp.quit()
    url = f"https://mcp-kv.store/{remote_name}"
    req = urllib.request.Request(url, headers={"User-Agent": "TeyaAuroraDeploy/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        out = resp.read().decode("utf-8", errors="replace")
    # cleanup
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


def main() -> int:
    env = load_env()
    if env.get("TEYA_ALLOW_PUBLISH", "").lower() != "yes":
        print("BLOCKER: TEYA_ALLOW_PUBLISH != yes")
        return 1

    print("=== FTP theme upload ===")
    if deploy_ftp_theme(env) != 0:
        return 1
    print("=== WP bootstrap + media import ===")
    posts = blog_posts()
    b64 = base64.b64encode(json.dumps(posts, ensure_ascii=False).encode("utf-8")).decode("ascii")
    php = BOOTSTRAP_PHP.replace("__POSTS_B64__", b64)
    extra_files = [
        {
            "registry_id": "blog-thumb-b01",
            "file": "blog-thumb-b01.png",
            "alt_text": "Иллюстрация ребёнка и AI-редактора",
            "used_in": ["front-page:blog-teaser", "archive:blog-card"],
        },
        {
            "registry_id": "blog-thumb-b03",
            "file": "blog-thumb-b03.png",
            "alt_text": "Коллаж детских проектов",
            "used_in": ["front-page:blog-teaser", "archive:blog-card"],
        },
    ]
    manifest = build_manifest(REGISTRY, THEME_SLUG, THEME_IMAGES, extra_files=extra_files)
    php = inject_media_import_php(php, manifest_to_b64(manifest))
    out = upload_and_run_php(env, php, "kk-aurora-bootstrap-once.php")
    print(out)
    ok = "theme=teya-kovcheg-kids" in out and "MEDIA_IMPORT_DONE" in out
    media_map = parse_media_import_output(out)
    if media_map:
        write_wp_media_artifacts(WP_DIR, media_map, theme_dir=THEME_DIR)
        print(f"=== wp-media-map.json: {len(media_map.get('assets', []))} assets, verdict={media_map.get('verdict')} ===")
    else:
        print("WARN: MEDIA_MAP_JSON missing from bootstrap output")
    log = ROOT / "teya-memory/wp/deploy-log.md"
    log.write_text(
        f"""# Deploy Log — Ковчег Kids

**Date:** 2026-06-04  
**Method:** FTP  
**Host:** mrrutrnc.beget.tech  
**Remote theme:** /avrora/public_html/wp-content/themes/teya-kovcheg-kids/  
**Public URL:** https://mcp-kv.store/  
**Status:** {"✅ SUCCESS" if ok else "❌ FAILED"}

## Bootstrap output

```
{out.strip()}
```
""",
        encoding="utf-8",
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
