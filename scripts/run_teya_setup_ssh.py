#!/usr/bin/env python3
"""Run teya-setup.php on Beget via SSH."""
from __future__ import annotations

import sys
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

    base = "cd ~"
    print("PWD:", run(client, f"{base} && pwd"))
    print("PHP bins:", run(client, "ls /usr/local/bin/php* 2>/dev/null || true"))

    php = run(client, "command -v php8.3 || command -v php8.2 || command -v php8.1 || command -v php")
    php = php.splitlines()[0].strip() if php else "php"
    print("Using PHP:", php)

    setup_cmd = (
        f"{base} && {php} -r "
        "\"$_GET['key']='teya-kovcheg-setup-2026'; include 'teya-setup.php';\""
    )
    print("--- setup output ---")
    print(run(client, setup_cmd))

    verify = f"""{base} && {php} -r '
require "wp-load.php";
echo "theme=" . get_option("stylesheet") . PHP_EOL;
echo "front=" . get_option("show_on_front") . "|" . get_option("page_on_front") . PHP_EOL;
foreach (array("home","obuchenie","make-com","mcp-server","klub") as $s) {{
  $p = get_page_by_path($s);
  echo $s . "=" . ($p ? $p->ID : "missing") . PHP_EOL;
}}
'"""
    print("--- verify ---")
    print(run(client, verify))

    print("--- wp core check ---")
    print(run(client, f"{base} && {php} -r \"require 'wp-load.php'; echo is_blog_installed() ? 'installed' : 'not_installed';\""))

    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
