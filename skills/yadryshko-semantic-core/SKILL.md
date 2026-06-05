---
name: yadryshko-semantic-core
description: Ядрышко/Core для Teya — Wordstat, SEO/GEO семантика, кластеры, URL map, content briefs, HTML/XLSX отчёты. Используй для subagent core/yadryshko перед AURA Team и Aurora.
---

# Ядрышко / Core Semantic Core

## Роль

Ядрышко/Core собирает полноценное семантическое ядро для Teya и отдаёт результат в общую память.

Это **длинный sub-agent workflow**, не короткая SEO-подсказка. Skill фиксирует методологию и Teya-адаптацию, а работу выполняет агент `core` или fallback `yadryshko`.

## Источники

Перед работой прочитай:

- `teya/vendor/yadryshko/docs/core-agent-playbook.md`
- `teya/vendor/yadryshko/docs/semantic-core-methodology.md`
- `teya/vendor/yadryshko/docs/mcp-kv-wordstat-setup.md`
- `teya/vendor/yadryshko/templates/run-files.md`

Если Teya установлена как плагин, пути могут быть внутри plugin root: `vendor/yadryshko/...`.

## Teya Output Root

Для Teya основной путь:

```text
teya-memory/semantic-core/<domain-or-topic>-<YYYY-MM-DD>/
```

Не используй `research/semantic-core-runs/` как основной выход внутри Teya.

## Вход

- `teya-memory/00-brief.md`
- `teya-memory/site.inv`
- `teya-memory/research/site-research-dossier.md`
- `teya-memory/research/competitors.csv`
- `teya-memory/research/offers-map.md`
- `teya-memory/research/audience-map.md`
- `teya-memory/research/fact-bank.md`
- при наличии: `teya-memory/01-handoff.md`

Из `site.inv` бери:

- `project.region`
- `project.language`
- `project.primary_goal`
- `content.niche`
- `content.services`
- `content.products`
- `content.target_audience`
- `content.competitors`
- `content.exclude_topics`
- `seo.wordstat_region`
- `seo.priority_search`

## Wordstat

MCP server: `user-mcp-kv`.

Ожидаемые tools:

- `wordstat_get_user_info`
- `wordstat_get_top_requests`

Правила:

- сначала проверь доступность Wordstat, если tool есть;
- минимум 10 осмысленных Wordstat-вызовов для нормального проекта;
- регион указывать явно;
- не выдумывать частотности;
- если Wordstat недоступен, продолжай на seed/intent уровне, но пометь `frequency_value=not_available`, `WORDSTAT DEGRADED`, `0 successful calls`, запиши блокер в `09-quality-report.md` и fragment. Не представляй такие частотности как подтверждённый спрос.

## Обязательные Файлы

В run-folder должны быть:

```text
index.html
semantic-core.xlsx
README.md
00-brief.md
01-site-inventory.md
02-seed-map.md
03-wordstat-raw.csv
04-keywords-clean.csv
05-clusters.csv
06-url-map.csv
07-content-briefs.md
08-serp-geo-notes.md
09-quality-report.md
10-todo.md
11-blog-topics.md
12-implementation-roadmap.md
```

## CSV Контракт

Минимальные схемы:

```csv
03-wordstat-raw.csv:
date_collected,seed_phrase,query,raw_frequency,region,device,source,source_call,notes

04-keywords-clean.csv:
query,canonical_query,source_sources,frequency_region,frequency_value,intent_initial,intent_confidence,cluster_candidate,include_status,exclude_reason,notes

05-clusters.csv:
cluster_id,cluster_name,primary_query,secondary_queries,intent,frequency_total,region_note,page_type,priority,business_value,target_url,url_status,serp_engine,serp_check_status,top_competitors,geo_questions,content_status,last_review,notes

06-url-map.csv:
target_url,url_status,page_type,cluster_ids,primary_queries,recommended_h1,title_draft,description_draft,internal_links_from,internal_links_to,implementation_task,owner_hint,notes
```

## GEO/AI Layer

В `07-content-briefs.md` и `08-serp-geo-notes.md` добавляй:

- FAQ;
- question-style H2/H3;
- короткие определения;
- блоки сравнения;
- trust-сигналы;
- источники/обновляемость;
- рекомендации для answer blocks и AI-выдачи.

## Blog Topics

Помимо страниц и URL-карты, обязательно дай **6 тем для блога** в файле:

```text
11-blog-topics.md
```

Каждая тема должна быть основана на семантике, а не придумана отдельно от ядра.

Для каждой из 6 тем укажи:

- `topic_id`;
- рабочий H1;
- title draft;
- description draft;
- primary query;
- secondary queries;
- intent;
- связанный cluster_id из `05-clusters.csv`;
- linked landing URL из `06-url-map.csv`;
- зачем тема нужна бизнесу;
- рекомендуемый объём;
- H2/H3 план;
- FAQ/GEO answer blocks;
- internal links to/from;
- priority `P0/P1/P2`.

В `07-content-briefs.md` можно кратко упомянуть эти blog topics, но полная версия должна быть в `11-blog-topics.md`.

## Scripts

Если доступны:

```text
python teya/vendor/yadryshko/scripts/build_core_html_report.py <run-folder>
python teya/vendor/yadryshko/scripts/build_semantic_core_xlsx.py <run-folder>
```

Если путь другой, используй `vendor/yadryshko/scripts/...`.

Если скрипты недоступны, создай HTML/XLSX fallback или зафиксируй причину в `09-quality-report.md`.

## HTML Report Safety

- Не делай глобальные string-replace по всему HTML/CSV/MD для статусов вроде `ok -> готово`, `pending -> ...`.
- Запрещено заменять подстроки внутри слов: `token`, `storybook`, `cookies`, slug/path/URL.
- Если локализуешь статусы, меняй только отдельные значения ячеек/полей через структурированные данные.
- Перед финалом проверь `index.html` на повреждения:

```text
tготово
storyboготово
coготово
risunготово
podarготово
```

Если найдено — исправь генератор/HTML и запиши проблему в `09-quality-report.md`.

## Fragment для Директора

Пиши canonical fragment только в:

```text
teya-memory/fragments/core.md
```

Для alias `yadryshko` можно продублировать только если Директор умеет дедупликацию. Если дублируешь:

```text
teya-memory/fragments/yadryshko.md
```

Оба файла должны содержать одинаковый `fragment_id: semantic-core:<run-folder>`, чтобы Директор склеил их один раз.

Формат:

```markdown
=== ЯДРЫШКО (СЕМАНТИКА) ===
## Статус: ✅ | ❌
Run path: teya-memory/semantic-core/...
Wordstat calls: N
Keywords raw/clean: N / N
Clusters: N
P0 pages: ...
P0 URLs: ...
Blog topics: 6
Files:
- 06-url-map.csv: ...
- 07-content-briefs.md: ...
- 11-blog-topics.md: ...
Ограничения: ...
```

Не пиши в `teya-memory/01-handoff.md`.

## Quality Gates

- Не заявляй файл создан без проверки на диске.
- Не выдумывай Wordstat, GSC, Яндекс.Вебмастер или SERP-факты.
- Отделяй факты от допущений.
- `10-todo.md` должен быть понятен владельцу: `done/check/next/backlog`, роли `SEO/редактор/разработчик/владелец/аналитик`.
- В конце `index.html` должны быть рекомендации: что хорошо, что мешает росту, что улучшить первым, какие страницы создать/обновить, что проверить в SERP/GSC/Яндекс.Вебмастере, план 7/30/90.

