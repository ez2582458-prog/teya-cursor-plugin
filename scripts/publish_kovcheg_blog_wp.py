#!/usr/bin/env python3
"""Publish BT01–BT03, trash Hello World, via FTP+HTTP bootstrap on docroot WP."""
from __future__ import annotations

import ftplib
import io
import os
import re
import urllib.request
from pathlib import Path

from md_to_wp_html import md_block_to_html

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "teya-memory/wp/page-content-pack.md"


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (ROOT / "teya-memory/teya.env.local").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def extract_post(pack: str, marker: str) -> str:
    start = pack.index(marker)
    end = pack.find("\n---\n", start + 10)
    if end == -1:
        end = pack.find("\n## Legal", start)
    block = pack[start:end]
    # body after H1 line
    m = re.search(r"\*\*H1:\*\*[^\n]+\n\n", block)
    if m:
        return block[m.end() :].strip()
    return block


def parse_meta(block_prefix: str, pack: str) -> dict[str, str]:
    chunk = pack[pack.index(block_prefix) : pack.index(block_prefix) + 800]
    def grab(label: str) -> str:
        m = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", chunk)
        return m.group(1).strip() if m else ""

    return {
        "title": grab("Title").split("|")[0].strip(),
        "description": grab("Description"),
        "h1": grab("H1"),
    }


def posts_data() -> list[dict]:
    pack = PACK.read_text(encoding="utf-8")
    specs = [
        ("## BT01", "chatgpt-dlya-detey-bezopasno", "## BT01 —"),
        ("## BT02", "vajbkoding-vs-scratch", "## BT02 —"),
        ("## BT03", "programmirovanie-dlya-detey-s-nulya", "## BT03 —"),
    ]
    posts = []
    for marker, slug, block_start in specs:
        meta = parse_meta(block_start, pack)
        body_md = extract_post(pack, block_start)
        body_html = md_block_to_html(body_md)
        posts.append(
            {
                "slug": slug,
                "title": meta["h1"] or meta["title"],
                "excerpt": meta["description"],
                "content": body_html,
            }
        )
    return posts


def build_php(posts: list[dict]) -> str:
    import base64
    import json

    b64 = base64.b64encode(json.dumps(posts, ensure_ascii=False).encode("utf-8")).decode("ascii")
    return f"""<?php
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/post.php';

$posts = json_decode(base64_decode('{b64}'), true);

foreach ($posts as $p) {{
    $existing = get_page_by_path($p['slug'], OBJECT, 'post');
    if ($existing instanceof WP_Post) {{
        $id = (int) $existing->ID;
        wp_update_post([
            'ID' => $id,
            'post_title' => $p['title'],
            'post_name' => $p['slug'],
            'post_content' => $p['content'],
            'post_excerpt' => $p['excerpt'],
            'post_status' => 'publish',
        ]);
    }} else {{
        $id = (int) wp_insert_post([
            'post_title' => $p['title'],
            'post_name' => $p['slug'],
            'post_content' => $p['content'],
            'post_excerpt' => $p['excerpt'],
            'post_status' => 'publish',
            'post_type' => 'post',
        ], true);
    }}
    if (is_wp_error($id)) {{
        echo 'ERR ' . $p['slug'] . ': ' . $id->get_error_message() . PHP_EOL;
        continue;
    }}
    echo 'OK post ' . $p['slug'] . '=' . $id . PHP_EOL;
}}

$hello = get_posts(['name' => 'hello-world', 'post_type' => 'post', 'post_status' => 'any', 'numberposts' => 1]);
if (!empty($hello[0])) {{
    wp_trash_post((int) $hello[0]->ID);
    echo 'TRASH hello-world=' . $hello[0]->ID . PHP_EOL;
}}
$sample = get_posts(['title' => 'Привет, мир!', 'post_type' => 'post', 'post_status' => 'any', 'numberposts' => 1]);
if (!empty($sample[0])) {{
    wp_trash_post((int) $sample[0]->ID);
    echo 'TRASH privet-mir=' . $sample[0]->ID . PHP_EOL;
}}
echo 'posts_count=' . wp_count_posts()->publish . PHP_EOL;
"""


def main() -> int:
    if os.environ.get("TEYA_ALLOW_LEGACY_BLOG_PUBLISH") != "yes":
        print(
            "BLOCKED: legacy page-content-pack blog publisher is disabled. "
            "Blog articles must be created/published by Excalibur Phase 1."
        )
        return 2

    posts = posts_data()
    php = build_php(posts)
    env = load_env()
    remote = "kk-publish-blog-once.php"

    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=60)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)
    ftp.cwd("/")
    ftp.storbinary(f"STOR {remote}", io.BytesIO(php.encode("utf-8")))
    ftp.quit()

    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "TeyaAuroraBlog/1.0")]
    urllib.request.install_opener(opener)
    out = urllib.request.urlopen(f"https://mcp-kv.store/{remote}", timeout=180).read().decode(
        "utf-8", errors="replace"
    )
    print(out)

    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=60)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)
    try:
        ftp.delete(remote)
    except ftplib.error_perm:
        pass
    ftp.quit()

    ok = all(f"OK post {s}" in out for s in ["chatgpt", "vajbkoding", "programmirovanie"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
