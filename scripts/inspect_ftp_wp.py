#!/usr/bin/env python3
"""Inspect WordPress on Beget FTP."""
from __future__ import annotations

import ftplib
import io
import re
import sys
from pathlib import Path


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
    root = Path(__file__).resolve().parents[2]
    env = load_env(root / "teya-memory" / "teya.env.local")
    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=60)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)

    print("ROOT:", sorted(ftp.nlst())[:25])

    ftp.cwd("/wp-content/themes")
    themes = ftp.nlst()
    print("THEMES:", themes)

    if "teya-kovcheg" in themes:
        ftp.cwd("teya-kovcheg")
        files = ftp.nlst()
        print("TEYA-KOVcheg count:", len(files))
        print("TEYA sample:", sorted(files)[:12])
    else:
        print("MISSING: teya-kovcheg theme")

    ftp.cwd("/")
    bio = io.BytesIO()
    ftp.retrbinary("RETR wp-config.php", bio.write)
    text = bio.getvalue().decode("utf-8", errors="replace")
    for key in [
        "DB_PASSWORD",
        "AUTH_KEY",
        "SECURE_AUTH_KEY",
        "LOGGED_IN_KEY",
        "NONCE_KEY",
        "SECURE_AUTH_SALT",
        "LOGGED_IN_SALT",
        "NONCE_SALT",
    ]:
        text = re.sub(
            rf"define\s*\(\s*'{key}'\s*,\s*'[^']*'",
            f"define( '{key}', '[REDACTED]'",
            text,
        )
    print("--- wp-config.php (redacted) ---")
    print("\n".join(text.splitlines()[:35]))

    ftp.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
