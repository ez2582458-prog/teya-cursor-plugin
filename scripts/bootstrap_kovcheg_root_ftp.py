#!/usr/bin/env python3
"""Bootstrap root docroot WP via FTP-uploaded PHP + HTTP trigger."""
from __future__ import annotations

import ftplib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = (Path(__file__).parent / "bootstrap_kovcheg_kids_wp.py").read_text(encoding="utf-8")
# Extract PHP body from bootstrap script
start = BOOTSTRAP.find('BOOTSTRAP_PHP = r"""') + len('BOOTSTRAP_PHP = r"""')
end = BOOTSTRAP.find('"""', start)
php = BOOTSTRAP[start:end]


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (ROOT / "teya-memory/teya.env.local").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def main() -> int:
    env = load_env()
    remote_name = "kk-bootstrap-root-once.php"
    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=60)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)
    ftp.cwd("/")
    bio = php.encode("utf-8")
    ftp.storbinary(f"STOR {remote_name}", __import__("io").BytesIO(bio))
    ftp.quit()

    url = f"https://mcp-kv.store/{remote_name}"
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "TeyaAuroraBootstrap/1.0")]
    urllib.request.install_opener(opener)
    out = urllib.request.urlopen(url, timeout=120).read().decode("utf-8", errors="replace")
    print(out)
    # cleanup
    ftp = ftplib.FTP()
    ftp.connect(env["FTP_HOST"], int(env.get("FTP_PORT", "21")), timeout=60)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.set_pasv(True)
    try:
        ftp.delete(remote_name)
    except ftplib.error_perm:
        pass
    ftp.quit()
    return 0 if "theme=teya-kovcheg-kids" in out else 1


if __name__ == "__main__":
    raise SystemExit(main())
