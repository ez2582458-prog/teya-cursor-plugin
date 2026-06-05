#!/usr/bin/env python3
"""Validate the local Teya env file without printing secrets."""

from __future__ import annotations

import argparse
from pathlib import Path


TRUTHY = {"yes", "true", "1", "on"}


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def is_filled(values: dict[str, str], key: str) -> bool:
    return bool(values.get(key, "").strip())


def require(errors: list[str], values: dict[str, str], keys: tuple[str, ...], context: str) -> None:
    for key in keys:
        if not is_filled(values, key):
            errors.append(f"Missing {key} for {context}")


def has_duplicate_ftp_docroot(path: str) -> bool:
    compact = path.replace("\\", "/").lower().strip("/")
    return "public_html/avrora/public_html" in compact or "public_html/public_html" in compact


def validate(path: Path) -> list[str]:
    if not path.exists():
        return [
            f"Missing env file: {path}",
            "Copy teya-memory/teya.env.example to teya-memory/teya.env.local",
        ]

    values = load_env(path)
    errors: list[str] = []

    deploy_mode = values.get("TEYA_DEPLOY_MODE", "local-only").strip().lower()
    allow_publish = values.get("TEYA_ALLOW_PUBLISH", "no").strip().lower() in TRUTHY

    if deploy_mode not in {"local-only", "ftp", "sftp", "ssh"}:
        errors.append("TEYA_DEPLOY_MODE must be one of: local-only, ftp, sftp, ssh")

    if deploy_mode == "local-only":
        return errors

    require(errors, values, ("PUBLIC_SITE_URL",), "remote deployment")

    if deploy_mode == "ftp":
        require(
            errors,
            values,
            ("FTP_HOST", "FTP_USER", "FTP_PASS", "FTP_REMOTE_THEME_PATH"),
            "FTP deployment",
        )
        ftp_theme_path = values.get("FTP_REMOTE_THEME_PATH", "")
        if has_duplicate_ftp_docroot(ftp_theme_path):
            errors.append(f"FTP_REMOTE_THEME_PATH contains duplicated public_html/docroot: {ftp_theme_path}")

    if deploy_mode in {"sftp", "ssh"}:
        require(errors, values, ("SSH_HOST", "SSH_USER", "SSH_THEME_PATH"), "SFTP/SSH deployment")
        if not is_filled(values, "SSH_PASS") and not is_filled(values, "SSH_KEY_PATH"):
            errors.append("SFTP/SSH deployment requires SSH_PASS or SSH_KEY_PATH")

    if allow_publish:
        require(errors, values, ("WP_ADMIN_URL", "WP_ADMIN_USER"), "publishing")
        if not is_filled(values, "WP_APP_PASSWORD") and not is_filled(values, "WP_ADMIN_PASSWORD"):
            errors.append("Publishing requires WP_APP_PASSWORD or WP_ADMIN_PASSWORD")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate teya.env.local without printing secrets.")
    parser.add_argument(
        "--path",
        default="teya-memory/teya.env.local",
        help="Path to the local Teya env file.",
    )
    args = parser.parse_args()

    errors = validate(Path(args.path).resolve())
    if errors:
        print("Teya env validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Teya env validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
