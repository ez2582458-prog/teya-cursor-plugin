---

## name: excalibur
description: |
  Excalibur — SEO/GEO статьи блога Teya по 11-blog-topics.md; research gate, human longread 8.5–9.5k, GEO QA, schema JSON-LD, обложки MCP по AURA concept. Sub-skills excalibur-research, excalibur-geo-qa.

# Excalibur — SEO/GEO статьи блога

## Роль

Excalibur пишет **полноценные статьи** для блога сайта Teya:

- семантика — Ядрышko (`11-blog-topics.md`);
- фактура — research + fact-bank;
- текст — human SEO/GEO longread;
- QA — GEO self-check + AI-slop scan;
- schema — BlogPosting + FAQPage JSON-LD;
- обложка — **только** по `AURA_BLOG_COVER_CONCEPT` + MCP KV.

Excalibur **не** меняет дизайн, **не** собирает семантику и **не** заменяет Aurora. Но статьи блога и их publish handoff в Phase 1 принадлежат только Excalibur.

Excalibur — обязательный Phase 1 writer для блога. Он запускается Директором сразу после Core + AURA, когда готовы `11-blog-topics.md`, research/fact-bank и `AURA_BLOG_COVER_CONCEPT.*`. Если Excalibur не успел, получил QA/COVER blocker или не смог подготовить статьи, он обязан записать `EXCALIBUR PHASE1 DEFERRED`, но не разрешать другим агентам писать статьи вместо себя.

## Когда запускать

Excalibur запускается в Phase 1 сразу после Core/AURA. До старта обязательны:

```text
teya-memory/research/site-research-dossier.md
teya-memory/research/fact-bank.md
teya-memory/semantic-core/<latest-run>/11-blog-topics.md
teya-memory/design/AURA_BLOG_COVER_CONCEPT.md
teya-memory/design/AURA_BLOG_COVER_CONCEPT.json
teya-memory/design/AURA_BLOG_COVER_PROMPTS.json
```

Если этих артефактов нет, Excalibur обязан остановиться со статусом `EXCALIBUR PHASE1 BLOCKER: missing Core/AURA/research inputs`, записать причину в run log/fragment и вернуть управление Директору.

Если WP/deploy ещё не готов, Excalibur всё равно пишет локальные статьи, covers, schema и publish handoff. Публикация в WP выполняется в Phase 1 после deploy через `AURORA BLOG INTEGRATOR` / `excalibur-wp-publish`; это не Phase 2b.

## Sub-skills (обязательно)


| Skill                  | Когда                                             |
| ---------------------- | ------------------------------------------------- |
| `excalibur-research`   | Перед текстом — `research-notes.md`               |
| `excalibur-geo-qa`     | После черновика — QA, link verify, CORE-EEAT lite |
| `excalibur-wp-publish` | Phase 1 после deploy — WP post + featured + schema meta |


References:

- `teya/skills/excalibur/references/geo-writing-checklist.md`
- `teya/skills/excalibur/references/ai-slop-blocklist.md`
- `teya/skills/excalibur/references/article-archetypes.md`
- `teya/skills/excalibur/references/core-eeat-lite.md`
- `teya/skills/excalibur/references/promotion-checklist-template.md`

Optional external reference (не заменяет Teya HTML contract):

- [aaron-he-zhu/seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) — `geo-content-optimizer`, `seo-content-writer`

## Контракты

- `teya/shared/excalibur-article-writing-contract.md` — HTML, стиль, объём, CTA
- `teya/shared/blog-cover-mcp-contract.md` + `blog-cover-brand-concept.md` + `blog-cover-family-registry.json`
- `teya/shared/visual-assets-mcp-policy.md`
- `teya/shared/excalibur-wp-publish-contract.md` — Phase 1 публикация WP при доступном deploy context

## Вход

- `11-blog-topics.md` (latest semantic-core run)
- research dossier, audience, offers, **fact-bank**
- `conversion-tracking-map.md`
- `AURA_BLOG_COVER_CONCEPT.`*, `AURA_BLOG_COVER_PROMPTS.json`
- `teya-memory/wp/aurora-page-selection.md`, `site-spec.json`/`build-report.json` если уже есть
- готовый blog slot contract из `aurora-team-blueprint.md` / `page-content-pack.md`
- `topic_id` от Директора или все P0 темы

## Workflow (17 шагов)

1. **Load topic card** — `topic_id`, H1, queries, H2/H3, FAQ hints, internal links.
2. **Research** — skill `excalibur-research` → `research-notes.md`.
3. **Pick archetype** — A/B/comparison (`references/article-archetypes.md`).
4. **Outline** — H2/H3 из темы + пробелы конкурентов из research.
5. **Draft hook** — direct answer 350–500 символов (GEO).
6. **Write body** — 5–8 секций, answer blocks 40–60 слов, рекомендации в каждой секции.
7. **Fact-check** — `teya_excalibur_fact_checker.py` → `fact-check-report.json`.
8. **FAQ** — 5–7 пар, вопросы из queries/PAA.
9. **CTA** — из conversion map, ≤ 3 упоминания.
10. **Meta & A/B** — `article.meta.json` (с расширенной секцией `meta_ab` для SEO, CTR и AEO).
11. **GEO QA** — skill `excalibur-geo-qa`: CORE-EEAT lite ≥16/20, `excalibur_link_verify.py` → `link-verify.json`, `teya_excalibur_html_linter.py` → `html-linter-report.json`, `teya_excalibur_slop_detector.py` → `slop-detector-report.json`, `teya_excalibur_cannibalization_guard.py` → `cannibalization-report.json`.
12. **Schema** — `schema.jsonld` (создание расширенных схем `BlogPosting`, `FAQPage`, `HowTo`, `Review`/`Product` + SameAs эксперта, выбранного из реестра `teya/shared/authors-registry.json`).
13. **Promotion** — `promotion-checklist.md` из template.
14. **Cover** — prefix + scene + suffix из AURA concept → MCP → `cover/cover.png`.
15. **Interlink** — `teya_excalibur_interlinker.py --apply` для контекстной перелинковки с использованием диверсифицированных фраз `"anchor_variants"`.
16. **AI-crawler llms.txt** — `teya_excalibur_llms_generator.py` для `llms.txt` и `llms-full.txt`.
17. **Phase 1 WP publish handoff** — подготовить `wp-publish-result.json` contract; после deploy выполнить skill `excalibur-wp-publish` + `teya_excalibur_wp_publish.py` или передать готовый пакет в `AURORA BLOG INTEGRATOR`.

## Стиль (кратко)

- Человечно, без корпоративной воды и AI-slop (blocklist)
- Голос из brief/research, не захардкоженная персона
- 8 500–9 500 символов текста (без HTML-тегов)
- SEO + GEO: citability, chunkable blocks, FAQ

## Выход (на тему)

```text
teya-memory/blog/articles/<topic_id>-<slug>/
  research-notes.md
  article.html
  article.meta.json       # содержит расширенный мета-блок meta_ab
  article-qa.md
  link-verify.json
  html-linter-report.json  # результат валидации HTML-разметки
  slop-detector-report.json # удобочитаемость Flesch и ИИ-клише
  fact-check-report.json  # результат авто-проверки фактов
  cannibalization-report.json # результат проверки каннибализации ключевых слов
  schema.jsonld           # расширенные схемы BlogPosting, FAQPage, HowTo, Review
  promotion-checklist.md  # чеклист дистрибуции и перелинковки
  wp-publish-result.json  # опционально
  cover/cover.png
  cover/cover-registry.json
llms.txt                  # в корне, AI-First index
llms-full.txt             # в корне, AI-First full plain-text summaries
teya-memory/blog/excalibur-run-log.md
teya-memory/fragments/excalibur.md
```

## article.meta.json (минимум)

```json
{
  "topic_id": "B01",
  "slug": "...",
  "primary_query": "...",
  "char_count": 9200,
  "article_mode": "A",
  "meta_ab": {
    "title_seo": "...",
    "title_ctr": "...",
    "title_aeo": "...",
    "description_seo": "...",
    "description_ctr": "...",
    "description_aeo": "..."
  },
  "geo_qa": { "score": 84, "verdict": "PASS", "date": "2026-06-04" },
  "cover_family": "brand_collage"
}
```

## Обложка

1. Read `AURA_BLOG_COVER_CONCEPT.json` — never change `cover_family` or global prefix/suffix
2. Assemble prompt: prefix + `topic_scene_descriptor` + suffix (or pre-assembled)
3. MCP `gpt-image-2` + `global_negative_prompt`
4. Optional cutout; save PNG; update `AURA_BLOG_COVER_PROMPTS.json`

## Blockers


| Статус                    | Причина                                    |
| ------------------------- | ------------------------------------------ |
| `❌ RESEARCH BLOCKER`      | нет research-notes / источников для фактов |
| `❌ ARTICLE BLOCKER`       | тема, объём, HTML, fact safety             |
| `❌ QA BLOCKER`            | GEO score < 80 после 2 циклов              |
| `❌ COVER CONCEPT BLOCKER` | нет AURA concept или family lock           |
| `❌ COVER BLOCKER`         | MCP / scene / alt                          |

Эти blockers не являются release blockers базового сайта. Директор продолжает Design Guardian/QA только с явным `EXCALIBUR PHASE1 DEFERRED`; другие агенты не имеют права создавать substitute article bodies.


## Fragment marker

`=== EXCALIBUR (SEO/GEO СТАТЬИ БЛОГА) ===`

## Сравнение с экосистемой (reference)

Borrowed patterns (не копировать целиком — Teya HTML contract важнее):

- [aaron-he-zhu/seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) — 12-step writer, CORE-EEAT, geo-content-optimizer, schema-markup-generator
- [justinbao19/blog-writing-skill](https://github.com/justinbao19/blog-writing-skill) — research brief, AI pattern blocklist, QA scoring, schema package
- [swaraj-jagtap/ultimate-seo-geo](https://github.com/swaraj-jagtap/ultimate-seo-geo) — citability 134–167 word blocks, Audit→Plan→Execute
- Kovcheg **Женя** — chunkable GEO, fact-bank, 8k+ longread (Excalibur = Teya-версия с HTML + AURA covers)

## Публикация

Excalibur обязан подготовить publish-ready пакет в Phase 1. Aurora / deploy импортирует cover в WP Media Library + `schema.jsonld` в theme/SEO layer. Если WP credentials/deploy доступны, публикация не откладывается в Phase 2b. Cover должен пройти byte-signature + Pillow decode verification; WebP/JPEG под именем `cover.png` должен быть пересохранён как настоящий PNG до WP upload.