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
- WebP/AVIF where possible.
- Explicit image dimensions.
- Per required visual zone: dimensions, format, alt policy, LCP/below-fold loading strategy.
- No lazy-load for LCP image.
- Lazy-load below-fold images.
- `font-display: swap`.
- Defer non-critical JS.
- Respect `prefers-reduced-motion`.
- Required MCP/temp assets should be self-hosted or cached for production when possible; do not leave broken/temporary image dependencies unreported.
- Skip link, keyboard navigation, visible focus states.
- Labels for forms, sufficient contrast, 44-48px touch targets.
