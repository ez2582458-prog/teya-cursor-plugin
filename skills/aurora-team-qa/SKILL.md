---
name: aurora-team-qa
description: Aurora Team QA — проверка готовой темы и страниц: WP, SEO/GEO, schema, меню, перелинковка, дизайн, live/deploy.
---

# Aurora Team QA

## Выход

`teya-memory/wp/seo-geo-verification.md`

## Проверить

- Перед финальным статусом обязательно запустить:

```text
python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>
```

- Ненулевой код = `❌ BLOCKER`, даже если `build-report.json`, `verification.md`, `design-integrity-report.md` или handoff пишут `✅`.
- Сохрани вывод команды в `teya-memory/wp/release-gate-report.md`.
- Final QA не имеет права ставить `✅ OK`, если hard release gate не прошёл кодом 0.

- Соответствие `teya-memory/research/site-research-dossier.md`, `offers-map.md`, `audience-map.md`, `fact-bank.md`.
- WordPress theme contract.
- AURA design match.
- `teya/shared/agent-data-flow-contract.md`.
- `teya/shared/visual-paint-qa-gate.md`.
- `teya/shared/design-source-decomposition-gate.md`.
- `teya/shared/visual-assets-mcp-policy.md`.
- `AURA_VISUAL_INVENTORY.json`, `AURA_SHAPE_MAP.json`, `AURA_SECTION_TRANSITIONS.json`, `AURA_ASSET_REGISTRY.json`.
- Visual assets: MCP-required images/cutouts exist and are not stock/fallback/CSS placeholders.
- Visual density: source image-bearing cards/sections are preserved; one hero image is not enough when the source has multiple visual cards.
- WP Media import contract: `teya/shared/wp-media-upload-contract.md`; after deploy create `wp-media-map.json`, import attachments with alt, no MCP/tempfile URLs in public HTML.
- Source decomposition / visual budget / section blueprints are implemented and not contradicted by live paint.
- Section transitions: source/AURA wave/blob/mask/overlap transitions are preserved.
- Test limit: максимум 5 страниц.
- H1, title, description, FAQ, content depth.
- Main menu, footer menu, legal links.
- 3-8 contextual internal links per SEO page.
- JSON-LD matches visible content.
- Yandex/Google verification and robots/canonical.
- robots.txt, sitemap, redirects, `llms.txt`, AI crawler policy.
- Yandex Business, Google Business Profile, 2GIS, NAP consistency.
- Core Web Vitals, image/font optimization, keyboard/focus accessibility.
- Forms, consent, anti-spam, Metrika/GA4 goals.
- Security/release map, deployignore, backup/rollback, PHP lint/theme checks.
- `site-spec.json` and `build-report.json`.
- Data-flow report fields in `site-spec.json`, `build-report.json`, `content-completeness-report.md`: `visual_inventory_status`, `required_visual_zones_count`, `ready_visual_zones_count`, `meaningful_image_count`, `section_transitions_status`, `asset_registry_status`, `visual_budget_status`, `section_blueprints_status`, `style_match_scorecard_status`, `per_page_visual_budget_status`, `per_page_section_blueprints_status`, `per_page_meaningful_image_counts`, `per_page_visual_gaps`, `local_asset_files_status`, `missing_local_asset_files`, `browser_subresources_status`, `unstyled_live_paint_status`, `theme_slug`, `project/site_name`, `public_site_url`.
- `design-integrity-report.md` from Aurora Team Design Guardian. If it is not `✅ DESIGN OK`, final QA cannot be `✅ OK`.
- `teya-memory/wp/paint-qa/paint-evidence.json` and screenshots for homepage plus every selected/build page. If public URL exists and paint evidence is missing or covers only homepage, final QA must be `❌ BLOCKER`.
- Screenshot files referenced in `paint-evidence.json` must exist on disk. Browser network evidence must show theme CSS/JS/images after fresh navigation/cache-bust.
- `content-completeness-report.md`. If it contains `❌ CONTENT BLOCKER`, final QA cannot be `✅ OK`.
- Live verification when public URL exists.
- No claims that contradict `fact-bank.md`.

## Anti-Haltura Blockers

Следуй `teya/shared/quality-anti-haltura.md`.

Final QA must be `❌ BLOCKER` if:

- public HTML contains `пример отзыва`, `пример участника`, `в разработке`, `скоро`, `TODO`, `placeholder`, `lorem`, `заглушка`;
- sitemap.xml is not 200 XML;
- robots.txt references staging/test/wrong host;
- canonical/schema/sitemap use a technical domain instead of public URL;
- visible page content is thin or missing required blocks;
- honeypot field is visible to users;
- visible top breadcrumbs overlap menu, hero or CTA;
- homepage has no real blog section from `11-blog-topics.md`;
- `/blog/` route/archive or `single.php` is missing;
- blog cards contain `скоро`, `готовится`, `пример`, `placeholder`, `lorem`;
- privacy policy page is missing;
- cookies policy page is missing;
- cookie banner or accept button is missing;
- cookie banner does not link to privacy and cookies policies;
- source/AURA has non-standard section transitions but the theme replaced them with generic straight blocks;
- MCP-required visual asset is missing, fake, stock/fallback, or absent from `AURA_ASSET_REGISTRY.json`;
- `AURA_VISUAL_INVENTORY.json` has required visual zones with `status != ready`;
- reference/source has image-bearing cards or a form-side image, but the final page keeps only one hero image;
- `meaningful_image_count` is below `minimum_homepage_visual_assets` / `minimum_meaningful_image_assets_homepage`;
- per-page `meaningful_image_count` is below per-page `minimum_meaningful_image_assets`;
- browser paint evidence is missing or contradicts `design-integrity-report.md`;
- browser paint evidence covers homepage only while selected/build inner pages exist;
- screenshot files referenced in `paint-evidence.json` are missing from `teya-memory/wp/paint-qa/`;
- live browser paint looks like unstyled/default HTML, even if reports say `pink hero` or `DESIGN OK`;
- browser network does not request theme CSS/JS/images after fresh navigation/cache-bust;
- public HTML contains MCP/tempfile/remote image URLs instead of WordPress Media Library uploads;
- `wp-media-map.json` missing, attachment_id empty, or alt missing/generic for meaningful images;
- visual budget or section blueprints are missing, ignored, or contradicted by live paint;
- source decomposition forbids generic/mostly-white/text-heavy layout, but live page looks generic/mostly-white/text-heavy;
- any selected/build inner page looks like a generic/default text template instead of inheriting AURA visual language;
- transparent cutout/background removal is required but no real `recraft_remove_background` result exists;
- hero/person/object asset is visibly clipped at a section boundary;
- `design-integrity-report.md` belongs to a different theme/project/slug than the deployed site.
- `site-spec.json`, `build-report.json` or `content-completeness-report.md` do not include required data-flow visual fields.

## Итог

Статус: `✅ OK`, `⚠️ FIXES NEEDED` или `❌ BLOCKER`.