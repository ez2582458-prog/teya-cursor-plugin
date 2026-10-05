---
name: manual-keywords-url-map
description: Вместо Ядрышко — принять ручной список ключей и построить URL-карту/брифы без Wordstat и MCP-KV. Использует Директор или сайтостроитель.
---

# Manual keywords + URL map

Замена пайплайна Ядрышко/Core. **Не** вызывай Wordstat, **не** используй MCP-KV для ключей, **не** запускай `core` / `yadryshko`.

## Вход

- `teya-memory/00-brief.md`
- `teya-memory/site.inv` (уже заполнен ботом из чата)
- `teya-memory/research/*` (после research gate)
- Список ключей из чата / файла пользователя / сайтостроителя **или** выбор Директора из услуг/ниши/оферов research

## Выход

Каталог: `teya-memory/semantic-core/manual/` (предпочтительно) или `teya-memory/semantic-core/<run-id>/` с `00-brief.md` пометкой `source: manual-keywords`.

```text
04-keywords-clean.csv
06-url-map.csv
07-content-briefs.md
11-blog-topics.md
teya-memory/fragments/keywords-url-map.md
```

Опционально (без Wordstat): `05-clusters.csv` — простая группировка ключей по интенту вручную.

**Не создавать и не требовать:** `03-wordstat-raw.csv`, HTML/XLSX отчёты Ядрышко, минимальное число Wordstat-вызовов.

## `04-keywords-clean.csv`

Минимум колонок:

```csv
keyword,intent,cluster,priority,source_note
```

`source_note`: `user` | `saitostroitel` | `director-from-research`.

## `06-url-map.csv`

Минимум колонок:

```csv
url,page_type,primary_keyword,intent,priority,h1_draft,title_draft
```

Правила:

- Главная `/` всегда есть.
- Тестовый лимит страниц не менять здесь (лимит 5 страниц сборки — отдельно у Aurora).
- Служебные: `/blog/`, privacy, cookies — по политике Teya.
- URL и приоритеты — из ручного списка + research, **не** из Wordstat.

## `07-content-briefs.md`

Краткий бриф на каждую URL-строку: цель страницы, primary/secondary keys, обязательные блоки, CTA, FAQ-кандидаты из research. Без выдуманных частотностей.

## `11-blog-topics.md`

6 тем для блога (как раньше по контракту Excalibur): title, slug, primary query, priority P0/P1, Phase 1 note. Источник — ключи + research + услуги, не Wordstat.

## Fragment

```markdown
=== KEYWORDS + URL MAP (MANUAL) ===
## Статус: ✅ | ⚠️ NEEDS KEYWORDS | ❌ BLOCKER
Source: user | saitostroitel | director-from-research
Keywords: teya-memory/semantic-core/manual/04-keywords-clean.csv
URL map: teya-memory/semantic-core/manual/06-url-map.csv
Briefs: teya-memory/semantic-core/manual/07-content-briefs.md
Blog topics: teya-memory/semantic-core/manual/11-blog-topics.md
Wordstat: not used
MCP-KV keywords: not used
Blockers: ...
```

## Quality gate

- Нет списка ключей и Директор не смог собрать даже минимальный из services/niche — статус `⚠️ NEEDS KEYWORDS`, спроси в чате, **не** вызывай Wordstat.
- Пустой `06-url-map.csv` или нет главной — `❌ BLOCKER`.
- Не блокировать из‑за отсутствия MCP-KV / Wordstat.
