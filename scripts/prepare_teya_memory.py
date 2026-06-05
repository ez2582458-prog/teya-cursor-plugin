#!/usr/bin/env python3
"""Prepare Teya shared memory for a new orchestrator run.

This script is intentionally dependency-free so it can run in local Cursor,
Cloud Agent, and worker environments.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


MEMORY_DIRS = (
    "fragments",
    "research",
    "semantic-core",
    "design",
    "wp",
    "wp/theme",
)


def prepare_memory(project_root: Path, reset: bool) -> Path:
    memory_root = project_root / "teya-memory"
    memory_root.mkdir(parents=True, exist_ok=True)

    for relative in MEMORY_DIRS:
        (memory_root / relative).mkdir(parents=True, exist_ok=True)

    if reset:
        handoff = memory_root / "01-handoff.md"
        handoff.write_text("# Teya — новая сессия\n", encoding="utf-8")

        fragments = memory_root / "fragments"
        for child in fragments.iterdir():
            if child.name == ".gitkeep":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    example_target = memory_root / "site.inv.example"
    if not example_target.exists():
        plugin_root = Path(__file__).resolve().parents[1]
        example_source = plugin_root / "shared" / "site.inv.example"
        if example_source.exists():
            shutil.copyfile(example_source, example_target)

    env_example_target = memory_root / "teya.env.example"
    if not env_example_target.exists():
        plugin_root = Path(__file__).resolve().parents[1]
        env_example_source = plugin_root / "shared" / "teya.env.example"
        if env_example_source.exists():
            shutil.copyfile(env_example_source, env_example_target)

    return memory_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Teya shared memory.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Workspace root that contains or should contain teya-memory.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset 01-handoff.md and clear fragments.",
    )
    args = parser.parse_args()

    memory_root = prepare_memory(Path(args.project_root).resolve(), args.reset)
    print(f"Teya memory ready: {memory_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
