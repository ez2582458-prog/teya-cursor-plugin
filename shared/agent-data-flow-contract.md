# Teya Agent Data Flow Contract

Этот файл фиксирует передачу данных между агентами Teya. Он нужен, чтобы артефакты не терялись между AURA, Aurora Team, Aurora, Design Guardian и QA.

## Главная Цепочка (Сквозной E2E Пайплайн)

```text
00-brief.md + site.inv
  -> teya-researcher (Исследование темы)
  -> core/yadryshko (Ядрышко: семантика и 11-blog-topics.md) || aura-designer (Дизайн и обложки блога)
  -> excalibur (Phase 1 blog articles + covers; единственный владелец статей)
  -> aurora-team-lead (Проектирование структуры)
  -> aurora-team-* maps || aurora-team-asset-packager || aurora-team-motion (MOTION PLAN)
  -> aurora-team-artifact-auditor (input go/no-go)
  -> aurora: THEME BASE -> PAGE BUILDER
  -> aurora-team-motion (MOTION IMPLEMENT)
  -> aurora-team-paint-evidence
  -> aurora-team-release-gate / teya_release_gate.py
  -> aurora: BLOG INTEGRATOR (Phase 1, only if Excalibur PASS; then repeat deploy/report/paint/release for enriched site)
  -> aurora-team-design-guardian (Дизайн-контроль)
  -> aurora-team-qa (Финальная проверка)
```

## Research Передаётся Всем

Каждый агент после `teya-researcher` обязан учитывать:

```text
teya-memory/research/site-research-dossier.md
teya-memory/research/competitors.csv
teya-memory/research/offers-map.md
teya-memory/research/audience-map.md
teya-memory/research/fact-bank.md
```

Факты, оферы, цены, отзывы, кейсы, NAP, лицензии и гарантии нельзя брать вне `fact-bank.md`, `site.inv` или явного brief.

## Semantic Core Передаётся Структуре и Контенту

После `core/yadryshko` обязательны:

```text
teya-memory/semantic-core/<latest-run>/06-url-map.csv
teya-memory/semantic-core/<latest-run>/07-content-briefs.md
teya-memory/semantic-core/<latest-run>/11-blog-topics.md
```

`11-blog-topics.md` обязателен для homepage blog section, `/blog/` и будущего `single.php`.

## AURA Передаётся Всем Визуальным и WP Этапам

После `aura-designer` обязательны:

```text
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
teya-memory/design/AURA_BLOG_COVER_CONCEPT.md
teya-memory/design/AURA_BLOG_COVER_CONCEPT.json
teya-memory/design/AURA_BLOG_COVER_SYSTEM.md
teya-memory/design/AURA_BLOG_COVER_PROMPTS.json
```

`AURA_BLOG_COVER_CONCEPT.*` — один primary `cover_family` из `blog-cover-family-registry.json` (33 типа); Excalibur меняет только scene per topic.

## Excalibur → blog articles (Phase 1)

```text
teya-memory/blog/excalibur-run-log.md
teya-memory/blog/articles/<topic_id>-<slug>/research-notes.md
teya-memory/blog/articles/<topic_id>-<slug>/article.html
teya-memory/blog/articles/<topic_id>-<slug>/article.meta.json
teya-memory/blog/articles/<topic_id>-<slug>/article-qa.md
teya-memory/blog/articles/<topic_id>-<slug>/link-verify.json
teya-memory/blog/articles/<topic_id>-<slug>/fact-check-report.json
teya-memory/blog/articles/<topic_id>-<slug>/schema.jsonld
teya-memory/blog/articles/<topic_id>-<slug>/promotion-checklist.md
teya-memory/blog/articles/<topic_id>-<slug>/cover/cover.png
teya-memory/blog/wp-publish-log.md                    # Phase 1 publish/integration when deploy is available
teya-memory/blog/articles/<topic_id>-<slug>/wp-publish-result.json
llms.txt
llms-full.txt
teya-memory/fragments/excalibur.md
```

Scripts: `teya/scripts/excalibur_link_verify.py`, `teya/scripts/teya_excalibur_wp_publish.py`, `teya/scripts/teya_excalibur_fact_checker.py`, `teya/scripts/teya_excalibur_interlinker.py`, `teya/scripts/teya_excalibur_llms_generator.py`.

Только Excalibur имеет право создавать `article.html`, longread excerpts, article schema, covers and article QA. `aurora-team-content`, `aurora-team-lead`, `aurora` and `AURORA PAGE BUILDER` may reference Excalibur metadata/cards, but must not write substitute blog articles.

`AURA_VISUAL_INVENTORY.json` является мостом между дизайном и сборкой. Если он содержит required zones, они должны появиться в:

- `aurora-team-blueprint.md`;
- `page-content-pack.md` block inventory;
- `performance-accessibility-map.md` image policy;
- `security-release-map.md` site-spec/build-report contract;
- `site-spec.json`;
- `build-report.json`;
- `content-completeness-report.md`;
- `design-integrity-report.md`;
- `seo-geo-verification.md`.

`AURA_SOURCE_DECOMPOSITION.json`, `AURA_VISUAL_BUDGET.json`, `AURA_SECTION_BLUEPRINTS.json` и `AURA_STYLE_MATCH_SCORECARD.md` являются мостом между reference и реальным paint. Они должны появиться в:

- `aurora-team-blueprint.md`;
- `security-release-map.md`;
- `site-spec.json`;
- `build-report.json`;
- `content-completeness-report.md`;
- `design-integrity-report.md`;
- `paint-qa-report.md`;
- `seo-geo-verification.md`.

Если в `site.inv` или `AURA_VISUAL_INVENTORY.json` указано `minimum_homepage_visual_assets`, это число должно перейти в Aurora reports как minimum meaningful image assets. Если `AURA_VISUAL_BUDGET.json` содержит `pages[]`, per-page minimums должны перейти в Aurora reports как `per_page_meaningful_image_counts` and `per_page_visual_gaps`. CSS cards, gradients and decorative shapes do not count as meaningful image assets.

## Aurora Team Artifacts Передаются Aurora

Перед Aurora должны существовать:

```text
teya-memory/wp/aurora-team-blueprint.md
teya-memory/wp/page-content-pack.md
teya-memory/wp/navigation-linking-map.md
teya-memory/wp/schema-technical-seo-map.md
teya-memory/wp/indexing-crawl-map.md
teya-memory/wp/local-entity-map.md
teya-memory/wp/performance-accessibility-map.md
teya-memory/wp/conversion-tracking-map.md
teya-memory/wp/security-release-map.md
teya-memory/wp/asset-packaging-report.md
teya-memory/wp/artifact-readiness-report.md
```

Если любого файла нет, Director дозапускает только соответствующего агента.

## Parallelization Contract

Можно запускать параллельно после Core + AURA + Aurora Team Lead:

```text
aurora-team-content
aurora-team-navigation
aurora-team-schema
aurora-team-indexing
aurora-team-local-entity
aurora-team-performance-a11y
aurora-team-conversion
aurora-team-security-release
aurora-team-asset-packager
aurora-team-motion
excalibur
```

Строго последовательно:

```text
aurora-team-artifact-auditor
  -> aurora: THEME BASE
  -> aurora: PAGE BUILDER
  -> aurora-team-motion: MOTION IMPLEMENT
  -> aurora-team-wp-deploy-media
  -> aurora-team-paint-evidence
  -> aurora-team-release-gate
  -> aurora: BLOG INTEGRATOR (only if Phase 1 Excalibur PASS)
  -> aurora-team-design-guardian
  -> aurora-team-qa
```

`AURORA THEME BASE` можно параллелить с `aurora-team-asset-packager`, если оба работают по read-only входам и не пишут один файл.

Excalibur запускается в Phase 1 сразу после Core + AURA. `EXCALIBUR PHASE1 DEFERRED` не блокирует Design Guardian / QA базового сайта, но чужие article bodies запрещены; blog integration выполняется только при Excalibur PASS.

## Aurora Reports Передаются Design Guardian и QA

После Aurora обязательны:

```text
teya-memory/wp/aurora-page-selection.md
teya-memory/wp/theme-base-report.md
teya-memory/wp/asset-packaging-report.md
teya-memory/wp/page-build-report.md
teya-memory/wp/animation-motion-map.md
teya-memory/wp/animation-implementation-report.md
teya-memory/wp/artifact-readiness-report.md
teya-memory/wp/site-spec.json
teya-memory/wp/build-report.json
teya-memory/wp/content-completeness-report.md
teya-memory/wp/verification.md
teya-memory/wp/deploy-log.md
teya-memory/wp/theme/<theme-slug>/
```

`site-spec.json` и `build-report.json` должны содержать:

```text
visual_inventory_status
required_visual_zones_count
ready_visual_zones_count
meaningful_image_count
minimum_meaningful_image_assets_homepage
meaningful_image_gap
section_transitions_status
asset_registry_status
paint_evidence_status
visual_budget_status
section_blueprints_status
style_match_scorecard_status
per_page_visual_budget_status
per_page_section_blueprints_status
per_page_meaningful_image_counts
per_page_visual_gaps
local_asset_files_status
missing_local_asset_files
browser_subresources_status
animation_motion_status
animation_dependency_status
reduced_motion_status
threejs_scene_status
unstyled_live_paint_status
wp_media_map_status
wp_media_import_status
missing_wp_media_attachments
theme_slug
project/site_name
public_site_url
```

После Aurora deploy обязательны:

```text
teya-memory/wp/wp-media-map.json
teya-memory/wp/wp-media-import-log.md
teya-memory/wp/release-gate-report.md
teya-memory/wp/deploy-log.md
```

`release-gate-report.md` создаётся выводом:

```text
python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>
```

Перед `excalibur-publish`, Design Guardian, QA и финальным ответом пользователя gate обязан завершиться с кодом 0. Если код ненулевой, любые `success` / `published_and_configured` / `✅ DESIGN OK` / `✅ QA OK` в markdown или JSON считаются недействительными.

После Paint Evidence обязательны:

```text
teya-memory/wp/paint-qa/home-1440-fullpage.png
teya-memory/wp/paint-qa/home-375-fullpage.png
teya-memory/wp/paint-qa/page-<slug>-1440-fullpage.png
teya-memory/wp/paint-qa/page-<slug>-375-fullpage.png
teya-memory/wp/paint-qa/paint-evidence.json
teya-memory/wp/paint-qa/paint-qa-report.md
```

После Design Guardian обязательны:

```text
teya-memory/wp/design-integrity-report.md
```

## QA Identity Check

Design Guardian и QA обязаны проверять, что отчёты относятся к текущей сборке:

- `theme_slug` совпадает с темой;
- `project/site_name` совпадает с `site.inv`;
- `public_site_url` совпадает с deploy target;
- `build-report.json` свежее или относится к текущему прогону;
- `design-integrity-report.md` не от другого проекта/темы.
- screenshot evidence относится к текущему public URL, а не к старой вкладке/старому deploy.
- screenshot paths из `paint-evidence.json` реально существуют на диске;
- browser network evidence относится к fresh navigation/cache-bust и содержит CSS/JS/image subresources текущей темы;

## Blockers

Остановить pipeline, если:

- отсутствует любой gate-файл текущего этапа;
- fragment пишет `✅`, но обязательный artifact отсутствует;
- AURA visual inventory required zones не дошли до Aurora reports;
- source имеет image-bearing zones, а final theme имеет только hero image;
- meaningful image count меньше minimum homepage visual assets;
- per-page meaningful image count меньше per-page visual budget minimum;
- visual budget или section blueprints отсутствуют/не реализованы;
- paint evidence отсутствует для любой selected/build page;
- внутренняя selected/build page выглядит как generic/default text template вместо AURA visual language;
- live browser paint выглядит как unstyled/default HTML или theme CSS не применился;
- browser network не содержит theme CSS/JS/images после fresh navigation/cache-bust;
- screenshot files referenced in `paint-evidence.json` do not exist;
- required local asset files are missing from `teya-memory/wp/theme/<theme-slug>/`;
- public HTML uses MCP/tempfile/remote image URLs instead of WP Media Library;
- `wp-media-map.json` missing or attachment_id empty for required asset;
- meaningful image alt missing or generic;
- source decomposition forbids generic/mostly-white layout, but final theme is generic/mostly-white/text-heavy;
- `paint-qa` screenshots/evidence отсутствуют при наличии public URL;
- `teya_release_gate.py` вернул ненулевой код или `release-gate-report.md` отсутствует при заявленном deploy success;
- Design Guardian пишет `✅ DESIGN OK`, но `paint-evidence.json` отсутствует, `verdict != pass`, screenshot files отсутствуют, browser subresources не содержат theme CSS/JS/images или live paint unstyled/default;
- QA использует старый `design-integrity-report.md` от другой темы;
- `01-handoff.md` содержит противоречивые статусы по одному этапу.
