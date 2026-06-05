#!/usr/bin/env python3
"""Activate teya-wondertoylab and create WP pages on Beget via SSH."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[2]

BOOTSTRAP_PHP = r"""<?php
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/theme.php';
require_once ABSPATH . 'wp-admin/includes/post.php';

$public_site_url = getenv('TEYA_PUBLIC_SITE_URL');
if (!$public_site_url) {
    $public_site_url = 'https://mcp-kv.store/';
}
$public_site_url = rtrim($public_site_url, '/') . '/';
if (0 !== strpos($public_site_url, 'https://')) {
    echo "ERR public_site_url_must_be_https=$public_site_url" . PHP_EOL;
    exit(2);
}
update_option('home', $public_site_url);
update_option('siteurl', $public_site_url);
$_SERVER['HTTPS'] = 'on';
$_SERVER['HTTP_HOST'] = parse_url($public_site_url, PHP_URL_HOST);

switch_theme('teya-wondertoylab');

$pages = [
    ['Главная', 'glavnaya', 'Волшебная мастерская игрушек из нейросети. Плюш, дерево, ткань.', ''],
    ['Создать свою игрушку', 'zayavka', 'Заявка на AI-эскиз игрушки.', 'page-zayavka.php'],
    ['Плюшевые игрушки', 'plushevye-igrushki', 'Плюшевые игрушки на заказ с AI-эскизом.', 'page-plushevye-igrushki.php'],
    ['Деревянные игрушки', 'derevyannye-igrushki', 'Деревянные сказочные игрушки на заказ.', 'page-derevyannye-igrushki.php'],
    ['Тканевые игрушки', 'tkanevye-igrushki', 'Тканевые игрушки и куклы на заказ.', 'page-tkanevye-igrushki.php'],
    ['Как это работает', 'kak-eto-rabotaet', 'От идеи до игрушки — 4 шага.', 'page-kak-eto-rabotaet.php'],
    ['По рисунку ребёнка', 'po-risunku-rebenka', 'Игрушка по рисунку ребёнка.', 'page-po-risunku-rebenka.php'],
    ['FAQ', 'faq', 'Частые вопросы о игрушках из нейросети.', 'page-faq.php'],
    ['Блог', 'blog', 'Блог WonderToy Lab.', ''],
    ['Политика конфиденциальности', 'politika-konfidentsialnosti', 'Обработка персональных данных.', 'page-politika-konfidentsialnosti.php'],
    ['Политика cookies', 'politika-cookies', 'Информация о cookies.', 'page-politika-cookies.php'],
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
        if (is_wp_error($id)) {
            echo "ERR $slug: " . $id->get_error_message() . PHP_EOL;
            continue;
        }
    }
    if ($template !== '') {
        update_post_meta($id, '_wp_page_template', $template);
    }
    $ids[$slug] = $id;
    echo "OK page $slug=$id" . PHP_EOL;
}

if (!empty($ids['glavnaya'])) {
    update_option('show_on_front', 'page');
    update_option('page_on_front', $ids['glavnaya']);
}
if (!empty($ids['blog'])) {
    update_option('page_for_posts', $ids['blog']);
}
update_option('permalink_structure', '/%postname%/');
update_option('blogname', 'WonderToy Lab');
update_option('blogdescription', 'Волшебные игрушки из нейросети');
update_option('WPLANG', 'ru_RU');
flush_rewrite_rules(false);
echo 'theme=' . wp_get_theme()->get_stylesheet() . PHP_EOL;
echo 'home=' . home_url('/') . PHP_EOL;
echo 'siteurl=' . site_url('/') . PHP_EOL;
"""


def load_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        data[k.strip()] = v.strip()
    return data


def main() -> int:
    env = load_env(ROOT / "teya-memory" / "teya.env.local")
    host = env.get("SSH_HOST", "")
    user = env.get("SSH_USER", "")
    password = env.get("SSH_PASS", "")
    wp_path = env.get("SSH_WP_PATH", "").rstrip("/")
    if not wp_path:
        docroot = (env.get("SSH_DOCROOT", "").strip() or "/home/m/mrrutrnc/avrora/public_html").rstrip("/")
        if docroot.startswith("/avrora/"):
            wp_path = "/home/m/mrrutrnc" + docroot
        else:
            wp_path = docroot

    if not all([host, user, password]):
        print("BLOCKER: SSH credentials missing")
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    port = int(env.get("SSH_PORT", "22") or "22")
    client.connect(host, port=port, username=user, password=password, timeout=30)

    remote_php = f"{wp_path}/wtl-bootstrap-{int(time.time())}.php"
    sftp = client.open_sftp()
    with sftp.file(remote_php, "w") as f:
        f.write(BOOTSTRAP_PHP)
    sftp.close()

    php_bin = env.get("SSH_PHP_BIN", "php8.2")
    public_site_url = env.get("PUBLIC_SITE_URL", "https://mcp-kv.store/").strip() or "https://mcp-kv.store/"
    if not public_site_url.startswith("https://"):
        print(f"BLOCKER: PUBLIC_SITE_URL must be HTTPS, got {public_site_url}")
        return 1

    cmd = f"cd {wp_path} && TEYA_PUBLIC_SITE_URL='{public_site_url}' {php_bin} {remote_php} && rm -f {remote_php}"
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    print(out or "(empty stdout)")
    if err:
        print("STDERR:", err, file=sys.stderr)
    client.close()
    ok = "theme=teya-wondertoylab" in out and f"home={public_site_url.rstrip('/')}/" in out
    if not ok:
        print("BOOTSTRAP_FAIL: expected theme=teya-wondertoylab and HTTPS home URL in output")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
