---
description: Teya фаза 2 — AURA blog cover brand concept + Excalibur SEO/GEO статьи.
---

# Teya — фаза 2 (Excalibur)

**Prerequisites:** research + `11-blog-topics.md` + `AURA_BLOG_COVER_CONCEPT.json`.

## Пайплайн

1. Директор проверяет `11-blog-topics.md`, `AURA_BLOG_COVER_CONCEPT.md`, `.json`.
2. **Task(aura-designer)** — blog covers:
   - один **cover_family** из реестра `blog-cover-family-registry.json` (**33** типа)
   - `global_prompt_prefix` + `global_prompt_suffix` + `color_lock`
   - per-topic: только `topic_scene_descriptor` + alt
   - опционально: `blog-cover-style-anchor.png`
   - см. `teya/shared/blog-cover-brand-concept.md`
3. **Task(excalibur)** — статьи + MCP covers: **prefix + scene + suffix**, не freestyle.
4. Проверь: research-notes, article-qa, link-verify, schema, promotion-checklist, cover.
5. (Опц.) **Фаза 2b** — `commands/teya-phase2-excalibur-publish.md` + skill `excalibur-wp-publish`.

**Передай:** `topic_id` (`B01`…`B06`, `all`, `P0-only`), `publish: yes/no`.

## Как держится единый стиль

| Fixed (концепт) | Variable (тема) |
|-----------------|------------------|
| cover_family, палитра, layout, grain, свет | объект/метафора статьи |
| prefix/suffix промпта | `topic_scene_descriptor` |

6 обложек в grid должны читаться как **одна серия бренда**.
