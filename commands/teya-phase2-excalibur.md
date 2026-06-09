---
description: Teya Excalibur repair/rerun — ручной повтор статей/обложек, если Phase 1 Excalibur был deferred.
---

# Teya — Excalibur Repair/Rerun

Это не основной путь. В нормальном прогоне Excalibur пишет статьи и готовит covers в Phase 1 сразу после Core + AURA. Используй эту команду только для ручного ремонта, дописывания или повторной публикации.

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
5. Publish repair — `commands/teya-phase2-excalibur-publish.md` + skill `excalibur-wp-publish`, если Phase 1 publish был deferred.

**Передай:** `topic_id` (`B01`…`B06`, `all`, `P0-only`), `publish: yes/no`.

## Как держится единый стиль

| Fixed (концепт) | Variable (тема) |
|-----------------|------------------|
| cover_family, палитра, layout, grain, свет | объект/метафора статьи |
| prefix/suffix промпта | `topic_scene_descriptor` |

6 обложек в grid должны читаться как **одна серия бренда**.
