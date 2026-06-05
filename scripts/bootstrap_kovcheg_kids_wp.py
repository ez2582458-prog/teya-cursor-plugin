#!/usr/bin/env python3
"""Activate teya-kovcheg-kids and create WP pages on Beget via SSH."""
from __future__ import annotations

import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[2]

BOOTSTRAP_PHP = r"""<?php
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/theme.php';
require_once ABSPATH . 'wp-admin/includes/post.php';

switch_theme('teya-kovcheg-kids');

$pages = [
    ['Главная', 'glavnaya', 'Онлайн-курс вайбкодинга для детей: Cursor AI, Telegram-боты и наставником. 12 недель, Demo Day, пробное 0 ₽.', ''],
    ['Программа вайбкодинга', 'programma', 'План занятий по неделям: Cursor, Telegram-боты, промпты, автоматизация и Demo Day.', 'page-programma.php'],
    ['Пробное занятие 0 ₽', 'probnoe', '60–75 мин онлайн: диагностика, мини-проект в Cursor, разбор программы для родителя.', 'page-probnoe.php'],
    ['Тарифы Kids Group и Pro', 'tarify', 'Сравнение форматов без публикации цен до согласования. Запись через пробное 0 ₽.', 'page-tarify.php'],
    ['Формат и расписание', 'format-raspisanie', 'Онлайн 2×/нед по MSK, домашние мини-проекты.', 'page-format-raspisanie.php'],
    ['Политика конфиденциальности', 'politika-konfidencialnosti', 'Обработка персональных данных по ФЗ-152.', 'page-politika-konfidencialnosti.php'],
    ['Политика cookies', 'politika-cookies', 'Информация о cookies и аналитике.', 'page-cookies.php'],
    ['Блог', 'blog', 'Статьи о вайбкодинге и IT для детей.', ''],
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
    $front_id = $ids['glavnaya'];
    update_option('show_on_front', 'page');
    update_option('page_on_front', $front_id);
}
if (!empty($ids['blog'])) {
    update_option('page_for_posts', $ids['blog']);
}
update_option('permalink_structure', '/%postname%/');
update_option('blogname', 'Ковчег Kids');
update_option('blogdescription', 'Вайбкодинг для детей 10–16');
update_option('WPLANG', 'ru_RU');
flush_rewrite_rules(false);
echo 'theme=' . wp_get_theme()->get_stylesheet() . PHP_EOL;
echo 'home=' . home_url('/') . PHP_EOL;
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
    wp_path = env.get(
        "SSH_WP_PATH",
        env.get("WP_PATH", "/home/m/mrrutrnc/avrora/public_html"),
    ).rstrip("/")

    if not all([host, user, password]):
        print("BLOCKER: SSH credentials missing")
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)

    remote_php = f"{wp_path}/kk-bootstrap-{__import__('time').time():.0f}.php"
    sftp = client.open_sftp()
    with sftp.file(remote_php, "w") as f:
        f.write(BOOTSTRAP_PHP)
    sftp.close()

    php_bin = env.get("SSH_PHP_BIN", "php8.2")
    cmd = f"cd {wp_path} && {php_bin} {remote_php} && rm -f {remote_php}"
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    print(out or "(empty stdout)")
    if err:
        print("STDERR:", err, file=sys.stderr)
    client.close()
    ok = "theme=teya-kovcheg-kids" in out
    if not ok:
        print("BOOTSTRAP_FAIL: expected theme=teya-kovcheg-kids in output")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
