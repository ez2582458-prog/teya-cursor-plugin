#!/usr/bin/env python3
"""Bootstrap WordPress theme and MVP pages on Beget via SSH."""
from __future__ import annotations

from pathlib import Path

import paramiko


def load_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        data[k.strip()] = v.strip()
    return data


def run(client: paramiko.SSHClient, cmd: str) -> str:
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    return (out + err).strip()


BOOTSTRAP_PHP = r"""<?php
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/theme.php';
require_once ABSPATH . 'wp-admin/includes/post.php';

switch_theme('teya-kovcheg');

$pages = [
    ['Главная', 'home', 'Курсы и клуб автоматизаторов от Артура Хорошева. Make.com, Cursor AI, MCP-сервер, OpenClaw.', ''],
    ['Обучение', 'obuchenie', 'Обучение автоматизации бизнес-процессов на Make.com, Cursor AI и MCP.', 'page-obuchenie.php'],
    ['Make.com', 'make-com', 'Курс Make.com с нуля: сценарии, интеграции CRM и маркетплейсов без программирования.', 'page-make-com.php'],
    ['MCP-сервер', 'mcp-server', 'MCP-сервер KV-AI: подключение Cursor AI и нейросетей к вашим данным.', 'page-mcp-server.php'],
    ['Клуб', 'klub', 'Закрытый клуб автоматизаторов Ковчег: шаблоны Make.com и поддержка сообщества.', 'page-klub.php'],
];

$ids = [];
foreach ($pages as [$title, $slug, $excerpt, $template]) {
    $existing = get_page_by_path($slug, OBJECT, 'page');
    if ($existing instanceof WP_Post) {
        $id = (int) $existing->ID;
    } else {
        $id = (int) wp_insert_post([
            'post_title' => $title,
            'post_name' => $slug,
            'post_excerpt' => $excerpt,
            'post_status' => 'publish',
            'post_type' => 'page',
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
    echo "OK $slug=$id" . PHP_EOL;
}

if (!empty($ids['home'])) {
    update_option('show_on_front', 'page');
    update_option('page_on_front', $ids['home']);
}
update_option('permalink_structure', '/%postname%/');
update_option('blogname', 'Ковчег — KV-AI');
update_option('blogdescription', 'Автоматизация бизнес-процессов с Make.com, Cursor AI и MCP');
update_option('WPLANG', 'ru_RU');
flush_rewrite_rules(false);
echo 'theme=' . get_option('stylesheet') . PHP_EOL;
echo 'siteurl=' . get_option('siteurl') . PHP_EOL;
echo 'home=' . get_option('home') . PHP_EOL;
"""


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    env = load_env(root / "teya-memory" / "teya.env.local")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        env["SSH_HOST"],
        username=env["SSH_USER"],
        password=env["SSH_PASS"],
        timeout=30,
    )

    php = "/usr/local/bin/php8.3"
    local_bootstrap = root / "teya-memory" / "wp" / "teya-bootstrap.php"
    local_bootstrap.write_text(BOOTSTRAP_PHP, encoding="utf-8")

    sftp = client.open_sftp()
    sftp.put(str(local_bootstrap), "teya-bootstrap.php")
    sftp.close()

    print(run(client, f"cd ~ && {php} teya-bootstrap.php"))
    print(run(client, f"cd ~ && rm -f teya-bootstrap.php teya-setup.php"))

    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
