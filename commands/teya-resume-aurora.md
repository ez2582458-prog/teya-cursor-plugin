---
description: Teya recovery — продолжить сборку Aurora без перезапуска upstream и без фальшивого SUCCESS.
---

# Teya — resume Aurora

Используй, если после Excalibur/Aurora Team есть частичная тема в `teya-memory/wp/theme/<theme-slug>/`, но нет финального рабочего сайта или hard release gate не проходит.

## Главное правило

Recovery не имеет права писать `published_and_configured`, `success`, `✅ DESIGN OK`, `✅ QA OK` или “готово”, пока не прошёл:

```text
python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>
```

Если команда вернула ненулевой код:

1. Запиши полный вывод в `teya-memory/wp/release-gate-report.md`.
2. Поставь статус `❌ RELEASE BLOCKER`.
3. Исправляй только перечисленные gate-проблемы.
4. Не запускай Excalibur publish, Design Guardian или QA.

## Что нельзя перезапускать

Не перезапускай upstream-агентов, если их артефакты уже есть:

- `teya-researcher`
- `core` / `yadryshko`
- `aura-designer`
- `excalibur`
- Aurora Team agents

## Проверить перед recovery

Обязательные входы:

- `teya-memory/fragments/excalibur.md`
- `teya-memory/wp/page-content-pack.md`
- `teya-memory/wp/navigation-linking-map.md`
- `teya-memory/wp/schema-technical-seo-map.md`
- `teya-memory/wp/indexing-crawl-map.md`
- `teya-memory/wp/local-entity-map.md`
- `teya-memory/wp/performance-accessibility-map.md`
- `teya-memory/wp/conversion-tracking-map.md`
- `teya-memory/wp/security-release-map.md`
- `teya-memory/design/AURA_ASSET_REGISTRY.json`
- `teya-memory/wp/theme/<theme-slug>/`

## Запустить только Aurora recovery

```text
Режим AURORA RECOVERY. Не запускай upstream-агентов заново. Прочитай готовые артефакты research, semantic-core, design, blog/articles, все карты wp/*.md и частичную тему teya-memory/wp/theme/<theme-slug>/. Исправь только недостающие/сломанные части темы, deploy/media map/live evidence. Особое внимание: media-map schema assets[], локальные files из local_source_path, реальные WP uploads attachment_url, отсутствие Beget domain stub на HTTPS public URL, browser network без 4xx/5xx по CSS/JS/images/fonts, paint-evidence screenshots по главной и selected/build pages. После исправления обязательно запусти python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>. Если gate не прошёл — статус RELEASE BLOCKER и вывод в release-gate-report.md. Если deploy нельзя выполнить из-за credentials/allow_publish — статус ГОТОВО К ДЕПЛОЮ, запускай gate с --no-live и не выдумывай URL.
```

После успешного `teya_release_gate.py` можно запускать обычные gates: Design Guardian → QA.
