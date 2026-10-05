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
- Заполненный бриф (`00-brief.md`) с списком страниц, числом статей и ключами
- Список ключей из чата / файла пользователя / сайтостроителя; если в брифе «подобрать вместе» — предложи в чате на утверждение (без Wordstat)

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
- **Набор страниц = список из заполненного брифа.** Если бриф задаёт N страниц — все N в `06-url-map.csv`. Старый потолок «5 страниц» **не применять**, когда бриф задаёт набор. Если бриф молчит о страницах — статус `⚠️ NEEDS PAGES`, спроси в чате; не подставляй 5.
- Число строк/тем в `11-blog-topics.md` = `blog_articles_count` из брифа (не раздувать).
- Ключи в `04-keywords-clean.csv` — только из брифа/чата; не выдумывать сверх списка.
- Служебные: `/blog/` (если блог нужен), privacy, cookies — по политике Teya (не вычитать из пользовательского N, если пользователь их не считал).
- URL и приоритеты — из брифа + research, **не** из Wordstat. Slug можно слегка нормализовать.

## `07-content-briefs.md`

Краткий бриф на каждую URL-строку: цель страницы, primary/secondary keys, обязательные блоки, CTA, FAQ-кандидаты из research. Без выдуманных частотностей.

## `11-blog-topics.md`

Число тем = **число статей из брифа** (не фиксированные «6»). Формат: title, slug, primary query, priority P0/P1, Phase 1 note. Темы — из брифа; недостающие до указанного числа можно предложить по нише **в пределах count**. Источник — бриф + ключи + research, не Wordstat. Если блог не нужен — файл с пометкой `blog_required: no` и нулём тем.

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

- Нет списка ключей и в брифе не сказано «подобрать вместе» — статус `⚠️ NEEDS KEYWORDS`, спроси в чате, **не** вызывай Wordstat.
- Нет числа/списка страниц в брифе — `⚠️ NEEDS PAGES`, спроси; не дефолть 5.
- Пустой `06-url-map.csv` или нет главной — `❌ BLOCKER`.
- Число URL контент-страниц меньше списка брифа (обрезали «для теста») — `❌ BLOCKER`.
- Не блокировать из‑за отсутствия MCP-KV / Wordstat.
