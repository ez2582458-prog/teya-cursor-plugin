---
name: excalibur-geo-qa
description: Excalibur GEO QA — self-check SEO/GEO статьи, CORE-EEAT lite, link verify, AI-slop, schema handoff.
---

# Excalibur GEO QA

## Когда

После `article.html` + `article.meta.json`, **до** обложки MCP и финального статуса.

## Вход

- `article.html`, `article.meta.json`, `research-notes.md`
- `teya/shared/excalibur-article-writing-contract.md`
- `teya/skills/excalibur/references/geo-writing-checklist.md`
- `teya/skills/excalibur/references/ai-slop-blocklist.md`
- `teya/skills/excalibur/references/core-eeat-lite.md`

## Выход

- `article-qa.md`
- `link-verify.json` (скрипт битых ссылок)
- `html-linter-report.json` (результат проверки валидности HTML)
- `slop-detector-report.json` (метрики удобочитаемости и ИИ-клише)
- обновлённый `article.meta.json` с `geo_qa`
- `promotion-checklist.md` (из template, после PASS)

## Валидаторы и скрипты качества (Обязательно)

1. **Link verify:**
```bash
python teya/scripts/excalibur_link_verify.py \
  teya-memory/blog/articles/<topic_id>-<slug>/article.html \
  -o teya-memory/blog/articles/<topic_id>-<slug>/link-verify.json \
  --site-base https://YOUR_SITE
```
- `verdict: pass` — OK
- **fail** → fix URLs или замени на актуальные, max 2 цикла.

2. **Strict HTML Whitelist Linter:**
```bash
python teya/scripts/teya_excalibur_html_linter.py \
  teya-memory/blog/articles/<topic_id>-<slug>/article.html \
  -o teya-memory/blog/articles/<topic_id>-<slug>/html-linter-report.json
```
- **Правило:** Если вердикт FAIL (использование запрещенных тегов или незакрытый тег), публикация блокируется (`❌ HTML LINTER BLOCKER`).

3. **AI-Slop & Readability Analyzer:**
```bash
python teya/scripts/teya_excalibur_slop_detector.py \
  teya-memory/blog/articles/<topic_id>-<slug>/article.html \
  -o teya-memory/blog/articles/<topic_id>-<slug>/slop-detector-report.json
```
- **Правило:** Если индекс читаемости Flesch RU < 40 или обнаружено более 3 ИИ-клише/длинных предложений (>25 слов), текст отправляется на рерайтинг.

## Scoring (0–100)

| Блок | Вес | Критерии |
|------|-----|----------|
| SEO structure | 20 | H2/H3, primary query, internal links |
| GEO / citability | 25 | direct answer, answer blocks (схемы/списки/таблицы по архетипу), FAQ |
| CORE-EEAT lite | 15 | ≥16/20 (`references/core-eeat-lite.md`) |
| Human voice | 15 | AI-slop blocklist |
| Fact safety | 15 | research-notes / fact-bank |
| Contract HTML | 10 | разрешенные теги (включая `<table>` для сравнений), 1-3 `<img>` с подписями `<i>`, объём, CTA, запреты |

**Pass:** ≥ 80, CORE-EEAT ≥16/20, link-verify pass, нет veto.

**Veto:** выдуманные факты, эмодзи, VPN, объём вне диапазона, нет FAQ, link-verify fail после 2 fixes.

## article-qa.md формат

```markdown
# QA: [topic_id] [slug]
date: YYYY-MM-DD
score_total: 84/100
core_eeat_lite: 18/20
link_verify: pass
verdict: PASS | FIX_REQUIRED | BLOCKER

## Scores
...

## CORE-EEAT lite
C01 ✓ ... (18/20)

## Link verify
- total: N, failed: 0
- see link-verify.json

## AI-slop scan
...

## Schema ready
BlogPosting: yes | FAQPage: yes (N) | HowTo: yes/no | Review: yes/no | E-E-A-T SameAs Author: yes (N links)
```

## После QA PASS

1. `schema.jsonld`
2. `promotion-checklist.md` — по `references/promotion-checklist-template.md`
3. Обложка MCP
4. (Опц.) WP publish — skill `excalibur-wp-publish`

## Blockers

- `❌ QA BLOCKER` — score < 80 или CORE-EEAT < 16/20 после 2 циклов
- `❌ LINK BLOCKER` — link-verify fail после 2 циклов
