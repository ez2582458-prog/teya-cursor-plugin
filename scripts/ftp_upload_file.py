#!/usr/bin/env python3
"""Upload a single file to WordPress FTP root."""
from __future__ import annotations

import argparse
import ftplib
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--local-file", required=True)
    parser.add_argument("--remote-name", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    env = load_env(root / "teya-memory" / "teya.env.local")
    local = Path(args.local_file)
    if not local.is_file():
        print(f"BLOCKER: missing {local}")
        return 1

    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=60)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)
    ftp.cwd("/")
    with local.open("rb") as fh:
        ftp.storbinary(f"STOR {args.remote_name}", fh)
    ftp.quit()
    print(f"OK: uploaded {args.remote_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
