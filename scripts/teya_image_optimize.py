#!/usr/bin/env python3
"""Teya image optimizer: WebP + resize + size budgets + responsive variants.

Default mode is --check (read-only report). --fix converts PNG/JPEG photos to WebP,
downsizes, writes -480w/-800w/-1200w variants for srcset, rewrites references
(theme php/css/js/json/html + extra --rewrite paths) and updates media-map.json.

Budgets (bytes of the main file):
  hero (id/name contains hero/lcp, or --hero NAME)  ≤ 250 KB, max side 1600 px
  normal content image                              ≤ 150 KB, max side 1200 px
  thumbs / cards / covers in lists (thumb, card)    ≤ 150 KB, max side 800 px
  hard limit for ANY raster image                    ≤ 300 KB
  PNG/JPEG over 30 KB = issue (must be WebP; PNG only for favicon / tiny UI icons).
Skipped: assets/favicon/**, theme-root screenshot.png, svg.
Exit: 0 ok, 1 issues remain, 2 cannot run.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

HERO_KB, NORMAL_KB, HARD_KB, LEGACY_KB = 250, 150, 300, 30
MAX_SIDE = {"hero": 1600, "normal": 1200, "thumb": 800}
VARIANT_WIDTHS = (480, 800, 1200)
RASTER = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
TEXT_EXT = {".php", ".css", ".js", ".json", ".html", ".htm", ".md", ".txt", ".xml"}
VARIANT_RE = re.compile(r"-(\d{3,4})w$")


def require_pil():
    try:
        from PIL import Image, ImageOps  # noqa: F401
    except ImportError:
        print("Pillow is required: pip install pillow", file=sys.stderr)
        raise SystemExit(2)


def role_for(name: str, hero_names: set[str], explicit: str | None = None) -> str:
    if explicit in MAX_SIDE:
        return explicit  # type: ignore[return-value]
    low = name.lower()
    if low in hero_names or Path(low).stem in hero_names or re.search(r"(hero|lcp|first-screen|banner)", low):
        return "hero"
    if re.search(r"(thumb|card|teaser|icon|avatar|logo-sm|cover-sm)", low):
        return "thumb"
    return "normal"


def budget_kb(role: str) -> int:
    return HERO_KB if role == "hero" else NORMAL_KB


def _prepare(img):
    from PIL import ImageOps

    img = ImageOps.exif_transpose(img)
    if img.mode in ("P", "LA", "L"):
        img = img.convert("RGBA" if "A" in img.mode or img.info.get("transparency") is not None else "RGB")
    elif img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    if img.mode == "RGBA" and img.getchannel("A").getextrema() == (255, 255):
        img = img.convert("RGB")
    return img


def _resize(img, max_side: int):
    from PIL import Image

    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        img = img.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    return img


def encode_webp(img, max_side: int, limit_kb: int) -> tuple[bytes, Any]:
    """Return (bytes, resized image) with size ≤ limit_kb, lowering quality, then size."""
    side = max_side
    while True:
        cur = _resize(img, side)
        for q in (82, 76, 70, 64, 58, 52, 46):
            buf = io.BytesIO()
            cur.save(buf, format="WEBP", quality=q, method=6)
            data = buf.getvalue()
            if len(data) <= limit_kb * 1024:
                return data, cur
        if max(cur.size) <= 480:
            return data, cur
        side = int(max(cur.size) * 0.85)


def optimize_bytes(data: bytes, dest: Path, role: str = "normal", variants: bool = True) -> dict[str, Any]:
    """Encode image bytes to dest (.webp) within budget; write srcset variants. Returns info."""
    from PIL import Image

    with Image.open(io.BytesIO(data)) as src:
        src.load()
        img = _prepare(src)
    main, resized = encode_webp(img, MAX_SIDE[role], budget_kb(role))
    dest = dest.with_suffix(".webp")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(main)
    w, h = resized.size
    info: dict[str, Any] = {"path": str(dest), "width": w, "height": h, "bytes": len(main), "role": role,
                            "format": "webp", "srcset": []}
    if variants:
        for vw in VARIANT_WIDTHS:
            if vw >= w:
                continue
            vdata, vimg = encode_webp(img, vw if img.size[0] >= img.size[1] else int(vw * img.size[1] / img.size[0]),
                                      min(budget_kb(role), 120))
            vpath = dest.with_name(f"{dest.stem}-{vw}w.webp")
            vpath.write_bytes(vdata)
            info["srcset"].append({"path": str(vpath), "width": vimg.size[0], "height": vimg.size[1], "bytes": len(vdata)})
        info["srcset"].append({"path": str(dest), "width": w, "height": h, "bytes": len(main)})
    return info


def skip(path: Path, theme: Path | None) -> bool:
    parts = [p.lower() for p in path.parts]
    if "favicon" in parts or re.search(r"(favicon|apple-touch|android-chrome|mstile)", path.name.lower()):
        return True
    if theme and path.parent == theme and path.name.lower().startswith("screenshot."):
        return True
    if "node_modules" in parts or "vendor" in parts:
        return True
    return bool(VARIANT_RE.search(path.stem))


def inspect(path: Path, role: str) -> list[dict[str, Any]]:
    from PIL import Image

    issues = []
    size = path.stat().st_size
    kb = size / 1024
    ext = path.suffix.lower()
    try:
        with Image.open(path) as im:
            w, h = im.size
    except Exception as exc:  # noqa: BLE001
        return [{"code": "broken_image", "detail": str(exc)[:120]}]
    if ext in {".png", ".jpg", ".jpeg", ".gif"} and size > LEGACY_KB * 1024:
        issues.append({"code": "not_webp", "detail": f"{ext} {kb:.0f} KB — нужен WebP"})
    if size > HARD_KB * 1024:
        issues.append({"code": "over_hard_limit", "detail": f"{kb:.0f} KB > {HARD_KB} KB"})
    elif size > budget_kb(role) * 1024 and ext == ".webp":
        issues.append({"code": "over_budget", "detail": f"{kb:.0f} KB > {budget_kb(role)} KB ({role})"})
    if max(w, h) > MAX_SIDE[role] * 1.05:
        issues.append({"code": "too_large_dimensions", "detail": f"{w}×{h} > {MAX_SIDE[role]} px ({role})"})
    if ext == ".webp" and w > 800 and not any((path.with_name(f"{path.stem}-{vw}w.webp")).is_file() for vw in VARIANT_WIDTHS):
        issues.append({"code": "no_srcset_variants", "detail": "нет вариантов -480w/-800w для srcset"})
    return issues


def rewrite_refs(files: list[Path], renames: dict[str, str]) -> list[str]:
    changed = []
    if not renames:
        return changed
    pattern = re.compile(r"(?<![\w.-])(" + "|".join(re.escape(k) for k in sorted(renames, key=len, reverse=True)) + r")(?![\w.-])")
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new = pattern.sub(lambda m: renames[m.group(1)], text)
        if new != text:
            f.write_text(new, encoding="utf-8")
            changed.append(str(f))
    return changed


def text_files(roots: list[Path]) -> list[Path]:
    out = []
    for r in roots:
        if r.is_file():
            out.append(r)
        elif r.is_dir():
            out += [f for f in r.rglob("*") if f.is_file() and f.suffix.lower() in TEXT_EXT
                    and "node_modules" not in f.parts and "vendor" not in f.parts and ".git" not in f.parts]
    return out


def update_media_map(theme: Path, converted: dict[str, dict[str, Any]]) -> bool:
    mm = theme / "media-map.json"
    if not mm.is_file() or not converted:
        return False
    data = json.loads(mm.read_text(encoding="utf-8"))
    by_old = {Path(k).name: v for k, v in converted.items()}
    touched = False
    for item in data.get("assets", []) if isinstance(data.get("assets"), list) else []:
        for key in ("local_path", "path"):
            name = Path(str(item.get(key) or "")).name
            if name in by_old:
                info = by_old[name]
                rel = str(Path(str(item[key])).with_name(Path(info["path"]).name)).replace("\\", "/")
                item[key] = rel
                item.update({"detected_format": "webp", "expected_extension": ".webp", "content_type": "image/webp",
                             "bytes": info["bytes"], "width": info["width"], "height": info["height"],
                             "srcset": [{"path": str(Path(rel).with_name(Path(v["path"]).name)).replace("\\", "/"),
                                         "width": v["width"]} for v in info["srcset"]]})
                item.pop("sha256", None)
                touched = True
    if touched:
        mm.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return touched


def main() -> int:
    ap = argparse.ArgumentParser(description="Teya image optimizer (WebP, resize, budgets, srcset variants).")
    ap.add_argument("--theme", required=True, help="Theme directory (scans assets/ by default)")
    ap.add_argument("--dirs", nargs="*", help="Image dirs to scan (default: <theme>/assets)")
    ap.add_argument("--fix", action="store_true", help="Convert / resize / write variants / rewrite references")
    ap.add_argument("--keep", nargs="*", default=[], help="File names to keep as-is (e.g. logo.png with exact pixels)")
    ap.add_argument("--hero", nargs="*", default=[], help="File names that are hero/LCP images")
    ap.add_argument("--rewrite", nargs="*", default=[], help="Extra files/dirs where references must be rewritten (mu-plugins, seeds)")
    ap.add_argument("--delete-originals", action="store_true", help="Remove converted PNG/JPEG originals after rewrite")
    ap.add_argument("--out", help="Report json path (default <root>/teya-memory/wp/qa/image-optimize.json or ./image-optimize.json)")
    args = ap.parse_args()
    require_pil()

    theme = Path(args.theme).resolve()
    if not theme.is_dir():
        print(f"theme dir not found: {theme}", file=sys.stderr)
        return 2
    dirs = [Path(d).resolve() for d in (args.dirs or [str(theme / "assets")])]
    hero = {h.lower() for h in args.hero} | {Path(h).stem.lower() for h in args.hero}
    keep = {k.lower() for k in args.keep}
    images = sorted({p for d in dirs if d.is_dir() for p in d.rglob("*") if p.suffix.lower() in RASTER})
    images = [p for p in images if not skip(p, theme)]

    rows, converted, renames = [], {}, {}
    for p in images:
        role = role_for(p.name, hero)
        if p.suffix.lower() != ".webp" and p.with_suffix(".webp").is_file() and not args.fix:
            rows.append({"file": str(p.relative_to(theme)) if p.is_relative_to(theme) else str(p), "bytes": p.stat().st_size,
                         "role": role, "issues": [], "note": "оригинал оставлен, рядом есть .webp (ссылки проверяет teya_page_weight.py)"})
            continue
        issues = inspect(p, role)
        row: dict[str, Any] = {"file": str(p.relative_to(theme)) if p.is_relative_to(theme) else str(p),
                               "bytes": p.stat().st_size, "role": role, "issues": issues}
        if args.fix and issues and p.name.lower() not in keep:
            try:
                info = optimize_bytes(p.read_bytes(), p.with_suffix(".webp"), role)
                row["fixed"] = {"to": Path(info["path"]).name, "bytes": info["bytes"], "width": info["width"],
                                "height": info["height"], "variants": [Path(v["path"]).name for v in info["srcset"]]}
                if p.suffix.lower() != ".webp":
                    converted[str(p)] = info
                    renames[p.name] = Path(info["path"]).name
                row["issues_after"] = inspect(Path(info["path"]), role)
            except Exception as exc:  # noqa: BLE001
                row["fix_error"] = str(exc)[:200]
        rows.append(row)

    changed_files: list[str] = []
    if args.fix and renames:
        update_media_map(theme, converted)
        changed_files = rewrite_refs(text_files([theme] + [Path(r) for r in args.rewrite]), renames)
        if args.delete_originals:
            for old in converted:
                Path(old).unlink(missing_ok=True)

    remaining = [r for r in rows if (r.get("issues_after") if "issues_after" in r else r["issues"])]
    root = next((c for c in [theme, *theme.parents] if (c / "teya-memory").is_dir()), None)
    out = Path(args.out) if args.out else ((root / "teya-memory/wp/qa/image-optimize.json") if root else Path("image-optimize.json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {"tool": "teya_image_optimize", "mode": "fix" if args.fix else "check", "theme": str(theme),
              "images": len(rows), "with_issues": len(remaining), "verdict": "pass" if not remaining else "fail",
              "renamed": renames, "rewritten_files": changed_files, "rows": rows}
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# Image optimize", "", f"**Verdict:** {'PASS' if not remaining else '❌ FAIL'} · images: {len(rows)} · with issues: {len(remaining)} · mode: {report['mode']}", ""]
    for r in rows:
        iss = r.get("issues_after") if "issues_after" in r else r["issues"]
        mark = "✅" if not iss else "❌"
        fx = f" → {r['fixed']['to']} {r['fixed']['bytes'] // 1024} KB {r['fixed']['width']}×{r['fixed']['height']}" if r.get("fixed") else ""
        md.append(f"- {mark} `{r['file']}` {r['bytes'] // 1024} KB ({r['role']}){fx} {'; '.join(i['code'] + ': ' + i['detail'] for i in iss)}")
    if changed_files:
        md += ["", "## Ссылки переписаны в", ""] + [f"- `{f}`" for f in changed_files]
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"IMAGE OPTIMIZE {report['verdict'].upper()}: {len(rows)} image(s), {len(remaining)} with issues → {out}")
    return 0 if not remaining else 1


if __name__ == "__main__":
    raise SystemExit(main())
