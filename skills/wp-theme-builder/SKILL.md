---
name: wp-theme-builder
description: Deprecated alias for Aurora. Сборка WordPress-темы по semantic-core, AURA и Aurora Team artifacts.
---

# WP Theme Builder (Teya)

## Источники истины (строго)


| Источник                | Путь                                              | Что брать                                                                                                                             |
| ----------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Intake                  | `teya-memory/site.inv`                            | Контакты, hosting mode, permissions, WP target                                                                                        |
| Brief                   | `teya-memory/00-brief.md`                         | Контакты, бренд, пожелания                                                                                                            |
| Research dossier        | `teya-memory/research/site-research-dossier.md`   | Тема, продукт, аудитория, оферы, конкуренты                                                                                           |
| Fact bank               | `teya-memory/research/fact-bank.md`               | Подтверждённые факты и ограничения                                                                                                    |
| Семантика               | `teya-memory/semantic-core/<run>/`                | `06-url-map.csv`, `07-content-briefs.md`, `05-clusters.csv`                                                                           |
| Дизайн                  | `teya-memory/design/`                             | `AURADESIGN.md`, `AURA_VISUAL_INVENTORY.json`, `AURA_SECTION_TRANSITIONS.json`, `AURA_ASSET_REGISTRY.json`, fonts, colors, components |
| Team blueprint          | `teya-memory/wp/aurora-team-blueprint.md`         | sitemap, page map, menu/footer, SEO/GEO requirements                                                                                  |
| Content pack            | `teya-memory/wp/page-content-pack.md`             | texts, FAQ, CTA, content length                                                                                                       |
| Navigation/linking      | `teya-memory/wp/navigation-linking-map.md`        | menu, footer, breadcrumbs, internal links                                                                                             |
| Schema map              | `teya-memory/wp/schema-technical-seo-map.md`      | schema.org, canonical, robots, Yandex/Google                                                                                          |
| Indexing/crawl          | `teya-memory/wp/indexing-crawl-map.md`            | robots, sitemap, canonical, noindex, redirects, llms.txt                                                                              |
| Local entity            | `teya-memory/wp/local-entity-map.md`              | NAP, business profiles, maps, LocalBusiness                                                                                           |
| Performance/a11y        | `teya-memory/wp/performance-accessibility-map.md` | CWV, images, fonts, accessibility                                                                                                     |
| Conversion/tracking     | `teya-memory/wp/conversion-tracking-map.md`       | forms, CTA, consent, goals                                                                                                            |
| Security/release        | `teya-memory/wp/security-release-map.md`          | SiteSpec, build report, backup, rollback, secrets policy                                                                              |
| Handoff                 | `teya-memory/01-handoff.md`                       | Статусы этапов                                                                                                                        |
| Data flow               | `teya/shared/agent-data-flow-contract.md`         | Required report fields and identity checks                                                                                            |
| Playbook                | `teya/shared/wp-theme-builder-playbook.md`        | WP structure, SEO, deploy, QA rules                                                                                                   |
| Anti-haltura            | `teya/shared/quality-anti-haltura.md`             | Content/block/placeholder/fake-proof/indexing blockers                                                                                |
| Visual assets policy    | `teya/shared/visual-assets-mcp-policy.md`         | MCP assets, cutouts, asset blockers                                                                                                   |
| Reference fidelity gate | `teya/shared/reference-visual-fidelity-gate.md`   | Required visual zones, image density blockers                                                                                         |


## Структура темы

```text
teya-memory/wp/theme/<slug>/
  style.css
  functions.php
  header.php / footer.php
  front-page.php
  page.php / single.php / archive.php / search.php / 404.php
  inc/setup.php / enqueues.php / seo.php / customizer.php / breadcrumbs.php / security.php
  template-parts/content/content.php
  template-parts/content/content-none.php
  page-{slug}.php   # P0 из url-map
  assets/css/
  assets/js/
  theme.json
  screenshot.png
```

## Деплой

1. Validate `site.inv`: `python teya/scripts/validate_teya_inv.py --path <PROJECT_ROOT>/teya-memory/site.inv`
2. If `allow_publish != yes` or credentials are missing: local build only, status `⚠️ ГОТОВО К ДЕПЛОЮ`
3. Credentials: `hosting.credentials.local` или env (`FTP_*`, `SSH_*`, `PUBLIC_SITE_URL`, `WP_THEME_SLUG`)
4. Prefer SSH/SFTP; FTP only if SSH/SFTP is unavailable
5. Upload theme → activate
6. Create pages from url-map
7. Set `_wp_page_template` and `post_excerpt` for generated pages
8. Verify → `wp/verification.md`

## Проверка успеха

- Не только HTTP 200
- HTML содержит маркеры кастомной темы
- `main#primary` есть
- P0 URL открываются
- Контакты из brief на месте
- Assets CSS/JS/images return 200
- `AURA_VISUAL_INVENTORY.json` exists and all required visual zones are implemented
- Meaningful image count matches source visual density; one hero image is not enough when source has image-bearing cards/form-side visuals
- Meaningful image count is not below `minimum_homepage_visual_assets` / `minimum_meaningful_image_assets_homepage`
- CSS cards, gradients, blobs and section backgrounds are not counted as meaningful image assets
- `AURA_ASSET_REGISTRY.json` has no required `pending` assets
- `site-spec.json`, `build-report.json`, `content-completeness-report.md` include visual data fields from `agent-data-flow-contract.md`, including minimum/gap and `paint_evidence_status`
- Reports match current `theme_slug`, project/site name and public URL
- Homepage blog section, `/blog/` archive and single post template work
- No visible top breadcrumbs overlap menu/hero/CTA
- Standard privacy policy and cookies policy pages exist
- Cookie banner has accept button and links to both policies
- No fake public URL when deployment did not happen
- `content-completeness-report.md` exists and has no `❌ CONTENT BLOCKER`
- Research dossier and fact bank exist; public claims do not contradict them
- No placeholders, fake reviews, sitemap non-200, wrong robots Host/Sitemap or staging domain leakage

## Запреты

- Своя структура сайта вместо url-map
- Игнорировать research dossier/fact bank
- Игнорировать Aurora Team artifacts
- Запускать nested subagents
- Свой дизайн вместо AURADESIGN
- Деплой при ❌ семантике или дизайне
- Деплой при `❌ CONTENT BLOCKER`
- Деплой без `AURA_VISUAL_INVENTORY.json`
- Деплой, если source image-bearing cards/form-side visuals заменены plain text blocks
- Деплой, если meaningful image count below minimum
- Деплой, если reports do not include visual data fields or identify another theme/project/public URL
- Публичные placeholders, фейковые отзывы, sitemap 500, wrong robots Host/Sitemap
- Production без `/blog/`, homepage blog section или `single.php`
- Видимые top breadcrumbs поверх меню/hero/CTA
- Production без “Политика конфиденциальности”, “Политика cookies” или cookie accept button
- Публикация без `allow_publish=yes`
- Публикация без live verification

