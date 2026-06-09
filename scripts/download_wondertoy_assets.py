#!/usr/bin/env python3
"""Download AURA_ASSET_REGISTRY assets into teya-wondertoylab theme."""
from __future__ import annotations

import json
from pathlib import Path

from asset_download import download_url_bytes
from teya_release_gate import sniff_image_format, validate_image_file

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "teya-memory" / "design" / "AURA_ASSET_REGISTRY.json"
THEME_IMG = ROOT / "teya-memory" / "wp" / "theme" / "teya-wondertoylab" / "assets" / "images"

MAP = {
    "hero-sky-scene": "hero-sky-scene.png",
    "hero-01-cloud-bunny": "heroes/hero-01-cloud-bunny.png",
    "hero-02-birch-deer": "heroes/hero-02-birch-deer.png",
    "hero-03-linen-doll": "heroes/hero-03-linen-doll.png",
    "hero-04-sailor-cat": "heroes/hero-04-sailor-cat.png",
    "hero-05-firefly": "heroes/hero-05-firefly.png",
    "hero-06-bear-postman": "heroes/hero-06-bear-postman.png",
    "hero-07-velvet-fox": "heroes/hero-07-velvet-fox.png",
    "hero-08-moon-fawn": "heroes/hero-08-moon-fawn.png",
    "category-plush": "categories/category-plush.png",
    "category-wood": "categories/category-wood.png",
    "category-fabric": "categories/category-fabric.png",
    "icon-moon": "icons/icon-moon.png",
    "icon-plane-dog": "icons/icon-plane-dog.png",
}


def write_valid_image(data: bytes, dest: Path) -> None:
    detected = sniff_image_format(data)
    if not detected:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"Downloaded bytes are not a known image: {dest}")

    suffix = dest.suffix.lower().lstrip(".")
    if suffix == "jpg":
        suffix = "jpeg"

    tmp = dest.with_name(f"{dest.stem}.tmp{dest.suffix}")
    try:
        if suffix == detected:
            tmp.write_bytes(data)
        elif suffix == "png" and detected in {"webp", "jpeg", "gif"}:
            import io

            from PIL import Image

            with Image.open(io.BytesIO(data)) as image:
                image.save(tmp, format="PNG")
        else:
            raise RuntimeError(f"Refusing to save {detected} bytes as .{suffix}: {dest}")

        errors = validate_image_file(tmp)
        if errors:
            raise RuntimeError("; ".join(errors))
        tmp.replace(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        dest.unlink(missing_ok=True)
        raise


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    THEME_IMG.mkdir(parents=True, exist_ok=True)
    ok = 0
    for asset in data["assets"]:
        aid = asset["id"]
        rel = MAP.get(aid)
        if not rel:
            print(f"SKIP unknown id {aid}")
            continue
        url = ""
        for key in ("transparent_url", "remote_packaged_url", "packaged_url", "url"):
            value = str(asset.get(key) or "").strip()
            if value.startswith(("http://", "https://")):
                url = value
                break
        if not url:
            print(f"FAIL no url {aid}")
            continue
        dest = THEME_IMG / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        data, evidence = download_url_bytes(url, timeout=20, retries=6, chunk_size=8 * 1024)
        write_valid_image(data, dest)
        print(
            f"OK {aid} -> {rel} ({dest.stat().st_size} bytes, "
            f"remote_type={evidence.get('content_type')}, range={evidence.get('content_range')}, "
            f"sig={evidence.get('signature_hex')})"
        )
        ok += 1
    print(f"Downloaded {ok}/{len(MAP)}")
    return 0 if ok == len(MAP) else 1


if __name__ == "__main__":
    raise SystemExit(main())
