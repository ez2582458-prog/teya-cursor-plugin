# Teya — протокол общей памяти

Все субагенты читают и пишут артефакты в **`<PROJECT_ROOT>/teya-memory/`**. Это единый источник правды между этапами.

Подробная карта передачи данных между агентами: `teya/shared/agent-data-flow-contract.md`.

## Новый сайт = новая память

Перед созданием нового сайта активная память должна быть очищена машинно:

```bash
python teya/scripts/reset_teya_memory.py --project-root <PROJECT_ROOT>
```

Контракт reset:

- старая `teya-memory/` переносится в `teya-memory-archive/teya-memory-<timestamp>/`;
- новая `teya-memory/` создаётся пустой;
- создаётся `teya-memory/memory-reset.json` со статусом `clean`;
- `site.inv` и `teya.env.local` не сохраняются по умолчанию, чтобы доступы и данные предыдущего сайта не попали в новый проект;
- `--keep-secrets` допустим только по явному запросу пользователя.

Агенты не читают `teya-memory-archive/` во время нового прогона, если пользователь явно не попросил восстановить старый сайт.

## Структура

```text
teya-memory/
├── site.inv                    # Structured intake from user (local/private)
├── site.inv.example            # Safe template
├── teya.env.local              # Private secrets: WP, hosting, SMTP, analytics (do not commit)
├── teya.env.example            # Safe env template
├── 00-brief.md                 # Вход пользователя (контакты, референс, контент)
├── 01-handoff.md               # Склейка Директором (маркеры этапов)
├── fragments/                  # Параллельные записи (без гонок)
│   ├── core.md                  # Ядрышко/Core, основной файл
│   ├── yadryshko.md             # alias для совместимости
│   ├── teya-researcher.md
│   ├── aura.md
│   ├── aurora-team-lead.md
│   ├── aurora-team-content.md
│   ├── aurora-team-navigation.md
│   ├── aurora-team-schema.md
│   ├── aurora-team-indexing.md
│   ├── aurora-team-local-entity.md
│   ├── aurora-team-performance-a11y.md
│   ├── aurora-team-conversion.md
│   ├── aurora-team-security-release.md
│   ├── aurora-team-design-guardian.md
│   ├── aurora-team-qa.md
│   └── excalibur.md
├── research/                    # Pre-start research для всей команды
│   ├── site-research-dossier.md
│   ├── competitors.csv
│   ├── offers-map.md
│   ├── audience-map.md
│   └── fact-bank.md
├── semantic-core/               # Ядрышко: полный пакет исследования
│   └── <run-folder>/           # index.html, csv, xlsx, briefs...
├── design/                     # AURA: DESIGN.md и deliverables
│   ├── AURADESIGN.md
│   ├── AURA_PAGE_PLAN.md
│   ├── AURA_REPLICATION_TODO.md
│   ├── AURA_SOURCE_ANALYSIS.md
│   ├── AURA_SOURCE_DECOMPOSITION.json
│   ├── AURA_SOURCE_MAP.json
│   ├── AURA_COMPOSITION_LOCK.json
│   ├── AURA_COMPONENT_MAP.json
│   ├── AURA_VISUAL_BUDGET.json
│   ├── AURA_SECTION_BLUEPRINTS.json
│   ├── AURA_VISUAL_INVENTORY.json
│   ├── AURA_SECTION_TRANSITIONS.json
│   ├── AURA_STYLE_MATCH_SCORECARD.md
│   ├── AURA_SHAPE_MAP.json
│   ├── AURA_FONT_MATCH.md
│   ├── AURA_BRAND_KIT_IMAGE_PROMPT.md
│   ├── AURA_COLOR_PSYCHOLOGY.md
│   ├── AURA_ASSET_REGISTRY.json
│   ├── AURA_VISUAL_DIFF.md
│   ├── AURA_REVIEWER_PASS.md
│   ├── AURA_VISUAL_QA.md
│   ├── AURA_LINT_REPORT.md
│   ├── AURA_BLOG_COVER_CONCEPT.md
│   ├── AURA_BLOG_COVER_CONCEPT.json
│   ├── AURA_BLOG_COVER_SYSTEM.md
│   ├── AURA_BLOG_COVER_PROMPTS.json
│   ├── assets/blog-cover-style-anchor.png   # опционально, эталон серии
│   ├── index.html              # референс-страница
│   └── ...
├── blog/                       # Excalibur: SEO/GEO статьи + covers
│   ├── excalibur-run-log.md
│   ├── wp-publish-log.md            # Phase 1 publish/integration log if deploy is available
│   └── articles/<topic_id>-<slug>/
│       ├── research-notes.md
│       ├── article.html
│       ├── article.meta.json
│       ├── article-qa.md
│       ├── link-verify.json
│       ├── html-linter-report.json
│       ├── slop-detector-report.json
│       ├── fact-check-report.json
│       ├── cannibalization-report.json
│       ├── schema.jsonld
│       ├── promotion-checklist.md
│       ├── wp-publish-result.json   # Phase 1 publish result if deploy is available
│       └── cover/cover.png
└── wp/                         # Aurora Team + Aurora
    ├── aurora-team-blueprint.md
    ├── page-content-pack.md
    ├── navigation-linking-map.md
    ├── schema-technical-seo-map.md
    ├── indexing-crawl-map.md
    ├── local-entity-map.md
    ├── performance-accessibility-map.md
    ├── conversion-tracking-map.md
    ├── security-release-map.md
    ├── site-spec.json
    ├── build-report.json
    ├── content-completeness-report.md
    ├── design-integrity-report.md
    ├── paint-qa/
    │   ├── paint-evidence.json
    │   ├── paint-qa-report.md
    │   ├── home-1440-fullpage.png
    │   ├── home-375-fullpage.png
    │   ├── page-<slug>-1440-fullpage.png
    │   └── page-<slug>-375-fullpage.png
    ├── aurora-page-selection.md
    ├── seo-geo-verification.md
    ├── theme/                  # исходники темы локально
    ├── deploy-log.md
    └── verification.md
```

## Маркеры handoff

```text
=== BRIEF (ВХОД) ===
=== TEYA-RESEARCHER (ГЛУБОКИЙ РЕСЁРЧ) ===
=== ЯДРЫШКО (СЕМАНТИКА) ===
=== AURA (ДИЗАЙН) ===
=== AURORA-TEAM-LEAD (СТРУКТУРА) ===
=== AURORA-TEAM-CONTENT (SEO/GEO ТЕКСТЫ) ===
=== AURORA-TEAM-NAVIGATION (МЕНЮ И ПЕРЕЛИНКОВКА) ===
=== AURORA-TEAM-SCHEMA (TECH SEO/GEO) ===
=== AURORA-TEAM-INDEXING (CRAWL/INDEX) ===
=== AURORA-TEAM-LOCAL-ENTITY (БИЗНЕС-СУЩНОСТЬ) ===
=== AURORA-TEAM-PERFORMANCE-A11Y (CWV/A11Y) ===
=== AURORA-TEAM-CONVERSION (ФОРМЫ И ЦЕЛИ) ===
=== AURORA-TEAM-SECURITY-RELEASE (БЕЗОПАСНЫЙ РЕЛИЗ) ===
=== AURORA (WP-ТЕМА И СТРАНИЦЫ) ===
=== AURORA-TEAM-DESIGN-GUARDIAN (ДИЗАЙН-КОНТРОЛЬ) ===
=== AURORA-TEAM-QA (ПРОВЕРКА) ===
```

Параллельные агенты пишут **только** в свои файлы и `fragments/`. Директор переносит fragments в `01-handoff.md`.

Важно: Aurora и Aurora Team Lead — тоже subagents. Они **не запускают вложенные Task**. Все Task запускает только Директор.

## Gate-файлы перед Aurora

Директор не запускает `aurora`, пока не проверит наличие:

```text
teya-memory/site.inv
teya-memory/research/site-research-dossier.md
teya-memory/research/competitors.csv
teya-memory/research/offers-map.md
teya-memory/research/audience-map.md
teya-memory/research/fact-bank.md
teya-memory/semantic-core/<latest-run>/06-url-map.csv
teya-memory/semantic-core/<latest-run>/07-content-briefs.md
teya-memory/semantic-core/<latest-run>/11-blog-topics.md
teya-memory/design/AURADESIGN.md
teya-memory/design/AURA_PAGE_PLAN.md
teya-memory/design/AURA_SOURCE_DECOMPOSITION.json
teya-memory/design/AURA_VISUAL_BUDGET.json
teya-memory/design/AURA_SECTION_BLUEPRINTS.json
teya-memory/design/AURA_STYLE_MATCH_SCORECARD.md
teya-memory/design/AURA_VISUAL_INVENTORY.json
teya-memory/design/AURA_SECTION_TRANSITIONS.json
teya-memory/design/AURA_SHAPE_MAP.json
teya-memory/design/AURA_ASSET_REGISTRY.json
teya-memory/design/AURA_FONT_MATCH.md
teya-memory/design/AURA_COMPONENT_MAP.json
teya-memory/design/AURA_COMPOSITION_LOCK.json
teya-memory/design/AURA_VISUAL_DIFF.md
teya-memory/design/AURA_REVIEWER_PASS.md
teya-memory/design/AURA_VISUAL_QA.md
teya-memory/design/AURA_LINT_REPORT.md
teya-memory/fragments/core.md или teya-memory/fragments/yadryshko.md
teya-memory/fragments/aura.md
teya-memory/wp/aurora-team-blueprint.md
teya-memory/wp/page-content-pack.md
teya-memory/wp/navigation-linking-map.md
teya-memory/wp/schema-technical-seo-map.md
teya-memory/wp/indexing-crawl-map.md
teya-memory/wp/local-entity-map.md
teya-memory/wp/performance-accessibility-map.md
teya-memory/wp/conversion-tracking-map.md
teya-memory/wp/security-release-map.md
```

Если `core.md` и `yadryshko.md` существуют одновременно, актуальным считается более новый файл; при склейке в handoff оставь один блок `=== ЯДРЫШКО (СЕМАНТИКА) ===`.

## Gate-файлы перед Ядрышком/AURA

Директор не запускает `core`/`yadryshko` и `aura-designer`, пока не создан pre-start research:

```text
teya-memory/research/site-research-dossier.md
teya-memory/research/competitors.csv
teya-memory/research/offers-map.md
teya-memory/research/audience-map.md
teya-memory/research/fact-bank.md
teya-memory/fragments/teya-researcher.md
```

Research dossier читает вся команда. Если dossier отсутствует, содержит placeholders, не имеет competitors/offers/audience/fact bank или не содержит источники, Директор дозапускает `teya-researcher`.

## Gate-файлы после Aurora, перед финальным QA

Директор не запускает `aurora-team-qa`, пока `aurora-team-design-guardian` не проверит готовую тему:

```text
teya-memory/wp/content-completeness-report.md
teya-memory/wp/design-integrity-report.md
teya-memory/wp/paint-qa/paint-evidence.json
teya-memory/wp/paint-qa/paint-qa-report.md
teya-memory/wp/paint-qa/home-1440-fullpage.png
teya-memory/wp/paint-qa/home-375-fullpage.png
teya-memory/wp/paint-qa/page-<slug>-1440-fullpage.png
teya-memory/wp/paint-qa/page-<slug>-375-fullpage.png
teya-memory/wp/wp-media-map.json
teya-memory/wp/wp-media-import-log.md
teya-memory/fragments/aurora-team-design-guardian.md
```

В отчётах должны быть статусы:

```text
нет ❌ CONTENT BLOCKER
✅ DESIGN OK
```

Если статус `⚠️ DESIGN FIXES NEEDED` или `❌ DESIGN BLOCKER`, Директор возвращает задачу Aurora на исправление дизайна и повторяет Design Guardian. Максимум 2 цикла.

## Intake `.inv`

`site.inv` is the structured source of truth for user-provided data:

- business and contacts;
- design reference;
- content/niche;
- SEO region and verification codes;
- WordPress and hosting mode;
- publishing permissions.

Template: `teya/shared/site.inv.example` or `teya-memory/site.inv.example`.

Secrets and connection data live in:

```text
teya-memory/teya.env.local
```

Template: `teya/shared/teya.env.example` or `teya-memory/teya.env.example`.

Do not write passwords, tokens, SSH keys or hosting panel credentials into `site.inv`.

Before remote deployment, validate:

```text
python teya/scripts/validate_teya_inv.py --path <PROJECT_ROOT>/teya-memory/site.inv
```

If validation fails, the Director must ask the user to fill the missing fields or continue only in local build mode.

## Сброс новой сессии

1. **Write** → `01-handoff.md` одной строкой: `# Teya — новая сессия`
2. Очистить `fragments/`
3. Создать, если отсутствуют: `semantic-core/`, `design/`, `wp/`, `wp/theme/`
4. Не запускать Task до сброса

Если папка плагина доступна в workspace, можно использовать скрипт:

```text
python teya/scripts/prepare_teya_memory.py --project-root <PROJECT_ROOT> --reset
```

## Пути

- `<PROJECT_ROOT>` — корень workspace, не абсолютные `C:\Users\...`
- Ядрышко/Core: основной Task name `core`; alias `yadryshko`
- Ядрышко: методология в `vendor/yadryshko/docs/` внутри плагина или `<PROJECT_ROOT>/teya/vendor/yadryshko/docs/`
- AURA skills: `skills/aura-cyrillic-google-fonts`, `skills/aura-shape-replication`

## Секреты

- `teya-memory/hosting.credentials.local` — не в git
- `teya-memory/site.inv` — не в git, потому что там могут быть приватные бизнес-данные и пути хостинга
- Шаблон: `shared/hosting.credentials.example`

## Деплой без credentials

Если FTP/SFTP/SSH credentials отсутствуют:

- `aurora` всё равно должна собрать локальную тему в `teya-memory/wp/theme/<theme-slug>/`
- не должен выдумывать публичный URL;
- должен записать статус `⚠️ ГОТОВО К ДЕПЛОЮ` в `01-handoff.md`;
- должен перечислить, каких переменных/полей не хватает для публикации.
