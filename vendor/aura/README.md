# AURA Designer для Teya

Источник: `https://github.com/Horosheff/aura-designer`

Локальный reference-пакет был сверены с `C:/Users/mrrut/Desktop/disMD/auradesign-agent`.

## Роль

AURA Designer создаёт дизайн-контракт и дизайн-артефакты для Aurora. В Teya AURA не занимается семантикой, URL-картой и поисковыми приоритетами: это зона Ядрышка/Core.

## Skill

Главный skill:

```text
teya/skills/aura-designer/SKILL.md
```

Вспомогательные skills:

```text
teya/skills/aura-cyrillic-google-fonts/SKILL.md
teya/skills/aura-shape-replication/SKILL.md
```

## Output Root

```text
teya-memory/design/
```

## Обязательные Deliverables

```text
AURADESIGN.md
AURA_PAGE_PLAN.md
AURA_REPLICATION_TODO.md
AURA_SOURCE_ANALYSIS.md
AURA_SOURCE_MAP.json
AURA_COMPOSITION_LOCK.json
AURA_COMPONENT_MAP.json
AURA_VISUAL_INVENTORY.json
AURA_SECTION_TRANSITIONS.json
AURA_SHAPE_MAP.json
AURA_FONT_MATCH.md
AURA_BRAND_KIT_IMAGE_PROMPT.md
AURA_COLOR_PSYCHOLOGY.md
AURA_ASSET_REGISTRY.json
AURA_VISUAL_DIFF.md
AURA_REVIEWER_PASS.md
AURA_VISUAL_QA.md
AURA_LINT_REPORT.md
index.html
```

Если файл неприменим для конкретного brief, AURA создаёт его с честным статусом `not_applicable` и причиной.

## Source Runtime Reference

Исходный локальный пакет содержит Python-модули:

```text
aura.py
aura_scanner.py
aura_source_analyzer.py
aura_generator.py
aura_replicator.py
aura_deliverables.py
aura_asset_manager.py
aura_visual_qa.py
aura_linter.py
```

В Teya основной runtime — Cursor subagent + skills. Python-модули источника используются как reference-архитектура и могут быть перенесены в `teya/vendor/aura/runtime/`, если будет нужен CLI-режим AURA внутри плагина.

## Законы

- Source-first: источник является законом.
- Кириллица: Google Fonts только с поддержкой Cyrillic/Cyrillic Extended для русского текста.
- Shapes: копировать форму источника, не подмешивать старые стили.
- Visual inventory: если source содержит image cards / form-side image / callouts, они обязательны как visual zones, не заменять одним hero image.
- Meaningful image density: `minimum_meaningful_image_assets_homepage` считает только реальные image/illustration/cutout scenes; CSS cards/gradients/blobs не считаются.
- No scene collapse: разные появления персонажа/объекта в разных секциях нельзя закрывать одним hero asset без явного `reuse_reason`.
- Section transitions: копировать нестандартные стыки блоков, masks, waves, overlaps, diagonal cuts и cutout-композиции.
- Assets: новые hero/person/object/case-study изображения только через MCP KV `gpt-image-2` и `recraft_remove_background`.
- Visual gates обязательны: lint, visual diff, reviewer pass, visual QA.
