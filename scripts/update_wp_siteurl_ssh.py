#!/usr/bin/env python3
"""Update WordPress site URL on Beget via SSH."""
from __future__ import annotations

from pathlib import Path

import paramiko

NEW_URL = "https://mcp-kv.store"


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
    return (stdout.read().decode("utf-8", errors="replace") + stderr.read().decode("utf-8", errors="replace")).strip()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    env = load_env(root / "teya-memory" / "teya.env.local")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(env["SSH_HOST"], username=env["SSH_USER"], password=env["SSH_PASS"], timeout=30)

    php = "/usr/local/bin/php8.3"
    script = f"""<?php
require __DIR__ . '/wp-load.php';
$new = '{NEW_URL}';
update_option('siteurl', $new);
update_option('home', $new);
flush_rewrite_rules(false);
echo 'siteurl=' . get_option('siteurl') . PHP_EOL;
echo 'home=' . get_option('home') . PHP_EOL;
echo 'theme=' . get_option('stylesheet') . PHP_EOL;
"""

    local = root / "teya-memory" / "wp" / "teya-update-url.php"
    local.write_text(script, encoding="utf-8")
    sftp = client.open_sftp()
    sftp.put(str(local), "teya-update-url.php")
    sftp.close()

    print(run(client, f"cd ~ && {php} teya-update-url.php"))
    print(run(client, "cd ~ && rm -f teya-update-url.php"))
    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
