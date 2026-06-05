#!/usr/bin/env python3
"""Validate the Teya site.inv intake file.

The validator checks only required orchestration inputs and does not validate
secret values. It is dependency-free for local and cloud agent runs.
"""

from __future__ import annotations

import argparse
import configparser
from pathlib import Path


REQUIRED_FIELDS = {
    "project": ("site_name", "theme_slug", "language", "primary_goal"),
    "business": ("company_name", "short_description"),
    "contacts": ("phone", "email"),
    "content": ("niche", "services", "target_audience"),
    "seo": ("wordstat_region", "priority_search"),
    "wordpress": ("target_theme_slug", "permalink_structure"),
    "hosting": ("deploy_mode", "credentials_file"),
    "automation": (
        "allow_publish",
        "allow_activate_theme",
        "allow_create_pages",
        "allow_create_posts",
    ),
}


def is_filled(value: str | None) -> bool:
    return bool(value and value.strip())


def validate(path: Path) -> list[str]:
    if not path.exists():
        return [f"Missing intake file: {path}"]

    parser = configparser.RawConfigParser()
    parser.read(path, encoding="utf-8")

    errors: list[str] = []
    for section, fields in REQUIRED_FIELDS.items():
        if not parser.has_section(section):
            errors.append(f"Missing section [{section}]")
            continue

        for field in fields:
            if not is_filled(parser.get(section, field, fallback="")):
                errors.append(f"Missing required field: [{section}] {field}")

    deploy_mode = parser.get("hosting", "deploy_mode", fallback="").strip().lower()
    allow_publish = parser.get("automation", "allow_publish", fallback="no").strip().lower()

    if not parser.has_section("design"):
        errors.append("Missing section [design]")
    else:
        design_reference_fields = ("reference_url", "reference_screenshot", "style_notes")
        if not any(is_filled(parser.get("design", field, fallback="")) for field in design_reference_fields):
            errors.append(
                "Missing design reference: fill at least one of [design] reference_url, reference_screenshot, style_notes"
            )

        visual_guidance_fields = ("visual_must_keep", "required_visual_zones", "must_keep")
        if not any(is_filled(parser.get("design", field, fallback="")) for field in visual_guidance_fields):
            errors.append(
                "Missing visual guidance: fill [design] visual_must_keep, required_visual_zones, or must_keep"
            )

    if allow_publish in {"yes", "true", "1"} and deploy_mode == "local-only":
        errors.append("[automation] allow_publish=yes requires [hosting] deploy_mode other than local-only")

    if deploy_mode in {"ftp", "sftp", "ssh"}:
        public_url = parser.get("project", "public_site_url", fallback="")
        if not is_filled(public_url):
            errors.append("[project] public_site_url is required for remote deployment")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Teya site.inv.")
    parser.add_argument(
        "--path",
        default="teya-memory/site.inv",
        help="Path to the Teya site.inv file.",
    )
    args = parser.parse_args()

    errors = validate(Path(args.path).resolve())
    if errors:
        print("Teya intake validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Teya intake validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
