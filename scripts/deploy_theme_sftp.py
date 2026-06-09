#!/usr/bin/env python3
"""Deploy WordPress theme via SFTP (reads teya.env.local)."""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from teya_release_gate import IMAGE_EXTENSIONS, validate_image_file

try:
    import paramiko
except ImportError:
    print("ERROR: pip install paramiko", file=sys.stderr)
    sys.exit(2)


def load_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.is_file():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        data[k.strip()] = v.strip()
    return data


def should_skip(rel: str, ignore_names: set[str]) -> bool:
    parts = Path(rel).parts
    if any(p in ignore_names for p in parts):
        return True
    if rel.endswith(".deployignore"):
        return True
    return False


def validate_theme_images(theme_local: Path) -> list[str]:
    images_dir = theme_local / "assets" / "images"
    if not images_dir.is_dir():
        return []

    errors: list[str] = []
    for image_path in sorted(images_dir.rglob("*")):
        if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
            errors.extend(validate_image_file(image_path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--theme-slug", default="teya-kovcheg")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    # Note: theme lives under <project>/teya-memory/wp/theme/
    env = load_env(root / "teya-memory" / "teya.env.local")
    host = env.get("SSH_HOST", "")
    port = int(env.get("SSH_PORT", "22"))
    user = env.get("SSH_USER", "")
    password = env.get("SSH_PASS", "")
    remote_base = env.get("SSH_THEME_PATH", "").rstrip("/")

    if not all([host, user, remote_base]):
        print("BLOCKER: missing SSH_HOST, SSH_USER, or SSH_THEME_PATH")
        return 1

    if env.get("TEYA_ALLOW_PUBLISH", "").strip().lower() != "yes":
        print("BLOCKER: TEYA_ALLOW_PUBLISH != yes")
        return 1

    theme_local = root / "teya-memory" / "wp" / "theme" / args.theme_slug
    if not theme_local.is_dir():
        print(f"BLOCKER: theme not found: {theme_local}")
        return 1

    image_errors = validate_theme_images(theme_local)
    if image_errors:
        print("ASSET_VERIFY_BLOCKER: theme contains invalid image files")
        for error in image_errors:
            print(f"- {error}")
        return 1

    ignore = {".git", "node_modules", ".DS_Store"}
    ignore_file = theme_local / ".deployignore"
    if ignore_file.is_file():
        for line in ignore_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                ignore.add(line)

    transport = paramiko.Transport((host, port))
    try:
        if password:
            transport.connect(username=user, password=password)
        else:
            key_path = env.get("SSH_KEY_PATH", "")
            if not key_path:
                print("BLOCKER: no SSH_PASS or SSH_KEY_PATH")
                return 1
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
            transport.connect(username=user, pkey=pkey)
        sftp = paramiko.SFTPClient.from_transport(transport)

        def mkdir_p(remote_dir: str) -> None:
            parts = remote_dir.strip("/").split("/")
            cur = ""
            for p in parts:
                cur += "/" + p
                try:
                    sftp.stat(cur)
                except OSError:
                    try:
                        sftp.mkdir(cur)
                    except OSError:
                        pass

        uploaded = 0
        for path in theme_local.rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(theme_local).as_posix()
            if should_skip(rel, ignore):
                continue
            remote = f"{remote_base}/{rel}".replace("\\", "/")
            mkdir_p(os.path.dirname(remote))
            sftp.put(str(path), remote)
            uploaded += 1

        sftp.close()
        print(f"OK: uploaded {uploaded} files to {remote_base}")
        return 0
    except Exception as e:
        print(f"DEPLOY_FAIL: {e}")
        return 1
    finally:
        transport.close()


if __name__ == "__main__":
    raise SystemExit(main())
