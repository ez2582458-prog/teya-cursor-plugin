#!/usr/bin/env python3
"""Reset teya-memory before starting a new site."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


KEEP_BY_DEFAULT = {
    "site.inv.example",
    "teya.env.example",
}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_clean_memory(memory_dir: Path, *, preserved: dict[str, bool], archived_to: str | None) -> None:
    memory_dir.mkdir(parents=True, exist_ok=True)
    for name in ("fragments", "research", "semantic-core", "design", "wp", "blog"):
        (memory_dir / name).mkdir(parents=True, exist_ok=True)

    (memory_dir / "00-brief.md").write_text(
        "# Teya brief\n\nНовая сессия. Заполнить brief перед запуском агентов.\n",
        encoding="utf-8",
    )
    (memory_dir / "01-handoff.md").write_text(
        "# Teya — новая сессия\n\nПамять очищена перед созданием нового сайта.\n",
        encoding="utf-8",
    )
    manifest = {
        "reset_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "archived_previous_memory_to": archived_to,
        "preserved": preserved,
        "status": "clean",
    }
    (memory_dir / "memory-reset.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def reset_memory(project_root: Path, *, keep_secrets: bool, archive: bool) -> Path | None:
    memory_dir = project_root / "teya-memory"
    archive_dir: Path | None = None
    preserved_dir = project_root / ".teya-memory-preserve"

    if preserved_dir.exists():
        shutil.rmtree(preserved_dir)
    preserved_dir.mkdir(parents=True, exist_ok=True)

    preserved: dict[str, bool] = {}
    if memory_dir.exists():
        for name in KEEP_BY_DEFAULT:
            src = memory_dir / name
            preserved[name] = src.is_file()
            copy_if_exists(src, preserved_dir / name)

        if keep_secrets:
            for name in ("site.inv", "teya.env.local"):
                src = memory_dir / name
                preserved[name] = src.is_file()
                copy_if_exists(src, preserved_dir / name)

        if archive:
            archive_root = project_root / "teya-memory-archive"
            archive_root.mkdir(parents=True, exist_ok=True)
            archive_dir = archive_root / f"teya-memory-{utc_stamp()}"
            memory_dir.rename(archive_dir)
        else:
            shutil.rmtree(memory_dir)

    memory_dir.mkdir(parents=True, exist_ok=True)
    for item in preserved_dir.iterdir():
        copy_if_exists(item, memory_dir / item.name)
    write_clean_memory(
        memory_dir,
        preserved=preserved,
        archived_to=str(archive_dir.relative_to(project_root)).replace("\\", "/") if archive_dir else None,
    )
    shutil.rmtree(preserved_dir)
    return archive_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset teya-memory before a new Teya site run.")
    parser.add_argument("--project-root", default=".", help="Workspace/project root containing teya-memory/")
    parser.add_argument(
        "--keep-secrets",
        action="store_true",
        help="Preserve site.inv and teya.env.local. Default removes old-site intake and secrets from active memory.",
    )
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Delete old teya-memory instead of moving it into teya-memory-archive/.",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    archive_dir = reset_memory(root, keep_secrets=args.keep_secrets, archive=not args.no_archive)
    if archive_dir:
        print(f"TEYA_MEMORY_RESET: archived previous memory to {archive_dir}")
    else:
        print("TEYA_MEMORY_RESET: created clean memory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
