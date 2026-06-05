---
name: excalibur-research
description: Excalibur Research — topic research перед статьёй блога Teya (конкуренты, SERP intent, факты, угол). Обязательный gate до article.html.
---

# Excalibur Research

## Когда

Перед написанием **каждой** статьи Excalibur. Без `research-notes.md` с источниками нельзя утверждать цены, даты, версии, статистику.

## Вход

- Карточка темы из `11-blog-topics.md` (`topic_id`, H1, queries, H2/H3, FAQ hints, internal links)
- `teya-memory/research/fact-bank.md`, `site-research-dossier.md`, `audience-map.md`, `competitors.csv`
- `teya/shared/quality-anti-haltura.md`

## Выход

`teya-memory/blog/articles/<topic_id>-<slug>/research-notes.md`

## Шаблон research-notes.md

```markdown
# Research: [H1]
topic_id: B01
date: YYYY-MM-DD
primary_query: ...
search_intent: informational | how_to | comparison | commercial_investigation

## SERP / конкуренты (3–5 URL)
| URL | Угол | Что закрывают | Пробел (наш угол) |
|-----|------|---------------|-------------------|

## Факты (только с источником)
| Факт | Источник | Дата доступа | Можно в текст |
|------|----------|--------------|---------------|

## Уникальный угол Excalibur
1–3 предложения: чем статья отличается от топа, без выдуманного «я сделал».

## Риски и запреты
- что нельзя утверждать (нет источника)
- чувствительные темы (дети, медицина, VPN и т.д.)

## Рекомендуемый режим статьи
A (новость/разбор) | B (инструкция/гайд)

## GEO hooks
- direct answer (1 предложение для первого абзаца)
- 3 quotable тезиса (25–50 слов каждый)
- FAQ кандидаты из PAA / queries темы
```

## Правила

1. Web research — **кратко**, 15–25 мин на тему; приоритет fact-bank.
2. Минимум **3** конкурента или аналога в SERP; если ниша пустая — явно напиши.
3. Каждая цифра/дата/цена → строка в таблице фактов или **не использовать** в тексте.
4. Не копировать структуру конкурента 1:1 — адаптируй под `11-blog-topics.md`.
5. Для local/детских/edtech ниш — отметь compliance (без stock-детей, без мед.гарантий).

## Blockers

- `❌ RESEARCH BLOCKER` — тема не найдена в `11-blog-topics.md`
- `❌ RESEARCH BLOCKER` — нет ни fact-bank, ни web sources для ключевых утверждений
