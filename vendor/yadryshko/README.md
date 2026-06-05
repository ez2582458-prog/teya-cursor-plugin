# ЯДрышко / Core для Teya

Источник: `https://github.com/Horosheff/yadryshko-semantic-core-subagent`

`ЯДрышко` (`Core`) — Cursor sub-agent для полного исследования семантического ядра сайта: Wordstat, очищенные запросы, кластеры, URL-карта, контент-брифы, GEO/AI-рекомендации, roadmap, HTML-отчёт и Excel-книга.

В Teya агент адаптирован под общую память:

```text
teya-memory/semantic-core/<domain-or-topic>-<YYYY-MM-DD>/
```

## Что важно

- Основной subagent: `core`.
- Alias: `yadryshko`.
- Skill Teya: `skills/yadryshko-semantic-core/SKILL.md`.
- Для реальных частотностей нужен MCP `user-mcp-kv` и Wordstat tools.
- Если Wordstat недоступен, Core не выдумывает частотности и фиксирует ограничение в `09-quality-report.md`.

## Основные файлы результата

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

## Скрипты

```text
python teya/vendor/yadryshko/scripts/build_core_html_report.py <run-folder>
python teya/vendor/yadryshko/scripts/build_semantic_core_xlsx.py <run-folder>
```

## Reference

- `docs/core-agent-playbook.md`
- `docs/semantic-core-methodology.md`
- `docs/mcp-kv-wordstat-setup.md`
- `docs/repository-map.md`
- `templates/run-files.md`
- `examples/prompt.md`
