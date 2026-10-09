---
name: aurora-team-performance-a11y
description: Aurora Team Performance A11y — Core Web Vitals, images, fonts, JS/CSS, WCAG, keyboard/focus, semantic HTML.
---

# Aurora Team Performance A11y

## Выход

`teya-memory/wp/performance-accessibility-map.md`

## Research Input

Читай `teya-memory/research/site-research-dossier.md`, `teya-memory/research/audience-map.md`, `teya-memory/design/AURA_VISUAL_INVENTORY.json` и `teya-memory/design/AURA_ASSET_REGISTRY.json`. Accessibility priorities must reflect audience needs and usage scenarios from research.

## Цели

- LCP < 2.5s.
- INP < 200ms.
- CLS < 0.1.
- **WebP обязательно** (PNG — только фавиконы / `keep_png`); hero ≤ 250 KB, остальные ≤ 150 KB, потолок 300 KB; `srcset`/`sizes` из `-480w/-800w/-1200w.webp`.
- Вес холодной загрузки: главная ≤ 1,5 MB, внутренняя ≤ 1 MB, CSS ≤ 60 KB (`teya_page_weight.py`, лимиты — `teya/shared/site-quality-scripts.md`).
- Основной текст ≥ 16 px, любой текст ≥ 12 px; заголовки без переноса внутри слова, с полями от края экрана (`teya_visual_lint.py`).
- Explicit image dimensions (`width`/`height` у каждой `<img>`).
- Per required visual zone: dimensions, format, alt policy, LCP/below-fold loading strategy.
- No lazy-load for LCP image.
- Lazy-load below-fold images.
- `font-display: swap`.
- Defer non-critical JS.
- Respect `prefers-reduced-motion`.
- Required MCP/temp assets should be self-hosted or cached for production when possible; do not leave broken/temporary image dependencies unreported.
- Skip link, keyboard navigation, visible focus states.
- Labels for forms, sufficient contrast, 44-48px touch targets.
