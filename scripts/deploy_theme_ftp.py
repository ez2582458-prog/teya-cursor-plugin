#!/usr/bin/env python3
"""Deploy WordPress theme via FTP."""
from __future__ import annotations

import argparse
import ftplib
import sys
from pathlib import Path

from teya_release_gate import IMAGE_EXTENSIONS, validate_image_file


def load_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        data[k.strip()] = v.strip()
    return data


def ftp_root_entries(ftp: ftplib.FTP) -> set[str]:
    try:
        entries = ftp.nlst("/")
    except ftplib.error_perm:
        entries = ftp.nlst()
    return {Path(entry.rstrip("/")).name for entry in entries}


def theme_suffix(remote_path: str, theme_slug: str) -> str:
    normalized = remote_path.replace("\\", "/").strip()
    if not normalized:
        return f"wp-content/themes/{theme_slug}"

    marker = "/wp-content/themes/"
    lowered = normalized.lower()
    marker_index = lowered.find(marker)
    if marker_index >= 0:
        return normalized[marker_index + 1 :].strip("/")

    if lowered.startswith("wp-content/themes/"):
        return normalized.strip("/")

    return f"wp-content/themes/{theme_slug}"


def normalize_remote_theme_path(raw_path: str, theme_slug: str, root_entries: set[str]) -> str:
    suffix = theme_suffix(raw_path, theme_slug)

    # Some hosts chroot FTP users directly into public_html. In that case a
    # configured /avrora/public_html/... path creates public_html inside itself.
    if "wp-content" in root_entries:
        return "/" + suffix

    if "public_html" in root_entries:
        return "/public_html/" + suffix

    cleaned = raw_path.replace("\\", "/").strip().rstrip("/")
    if not cleaned:
        return "/" + suffix
    if not cleaned.startswith("/"):
        cleaned = "/" + cleaned
    return cleaned


def has_duplicate_docroot(remote_path: str) -> bool:
    compact = remote_path.replace("\\", "/").lower().strip("/")
    return "public_html/avrora/public_html" in compact or "public_html/public_html" in compact


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
    parser.add_argument(
        "--remote",
        default="",
        help="Override remote theme path (e.g. /wp-content/themes/slug for docroot WP)",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    env = load_env(root / "teya-memory" / "teya.env.local")
    host = env.get("FTP_HOST", "")
    port = int(env.get("FTP_PORT", "21"))
    user = env.get("FTP_USER", "")
    password = env.get("FTP_PASS", "")
    raw_remote_base = args.remote or env.get("FTP_REMOTE_THEME_PATH", "").rstrip("/")

    theme_local = root / "teya-memory" / "wp" / "theme" / args.theme_slug
    ignore = {".git", "node_modules", ".DS_Store", ".deployignore"}

    if env.get("TEYA_ALLOW_PUBLISH", "").strip().lower() != "yes":
        print("BLOCKER: TEYA_ALLOW_PUBLISH != yes")
        return 1

    if not theme_local.is_dir():
        print(f"BLOCKER: theme not found: {theme_local}")
        return 1

    image_errors = validate_theme_images(theme_local)
    if image_errors:
        print("ASSET_VERIFY_BLOCKER: theme contains invalid image files")
        for error in image_errors:
            print(f"- {error}")
        return 1

    ftp = ftplib.FTP()
    try:
        ftp.connect(host, port, timeout=60)
        ftp.login(user, password)
        ftp.set_pasv(True)

        root_entries = ftp_root_entries(ftp)
        remote_base = normalize_remote_theme_path(raw_remote_base, args.theme_slug, root_entries)
        if has_duplicate_docroot(remote_base):
            print(f"FTP_PATH_BLOCKER: duplicated public_html/docroot in remote path: {remote_base}")
            ftp.quit()
            return 1

        def cwd_mk(remote_dir: str) -> None:
            ftp.cwd("/")
            parts = [p for p in remote_dir.split("/") if p]
            for p in parts:
                try:
                    ftp.cwd(p)
                except ftplib.error_perm:
                    ftp.mkd(p)
                    ftp.cwd(p)

        cwd_mk(remote_base)
        uploaded = 0

        for path in sorted(theme_local.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(theme_local).as_posix()
            if any(part in ignore for part in Path(rel).parts):
                continue
            remote_dir = "/".join([remote_base] + rel.split("/")[:-1])
            ftp.cwd("/")
            cwd_mk(remote_dir)
            with path.open("rb") as f:
                ftp.storbinary(f"STOR {path.name}", f)
            uploaded += 1

        ftp.cwd("/")
        cwd_mk(remote_base)
        deployed_names = {Path(name.rstrip("/")).name for name in ftp.nlst()}
        missing_required = sorted({"style.css", "functions.php"} - deployed_names)
        if missing_required:
            print(f"FTP_VERIFY_FAIL: missing required theme files at {remote_base}: {', '.join(missing_required)}")
            ftp.quit()
            return 1

        ftp.quit()
        if raw_remote_base.rstrip("/") != remote_base:
            print(f"FTP_PATH_NORMALIZED: {raw_remote_base or '(empty)'} -> {remote_base}")
        print(f"OK: FTP uploaded {uploaded} files to {remote_base}")
        return 0
    except Exception as e:
        print(f"FTP_FAIL: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
