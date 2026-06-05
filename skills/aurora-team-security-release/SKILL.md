---
name: aurora-team-security-release
description: Aurora Team Security Release — SiteSpec, build report, deployignore, backup, rollback, PHP lint, Theme Check, secrets policy.
---

# Aurora Team Security Release

## Выход

`teya-memory/wp/security-release-map.md`

## Обязательно

- `site-spec.json` contract for deterministic build.
- `build-report.json` contract for final reporting.
- Both reports must include visual data fields: `visual_inventory_status`, `required_visual_zones_count`, `ready_visual_zones_count`, `meaningful_image_count`, `minimum_meaningful_image_assets_homepage`, `meaningful_image_gap`, `section_transitions_status`, `asset_registry_status`, `paint_evidence_status`, `visual_budget_status`, `section_blueprints_status`, `style_match_scorecard_status`, `per_page_visual_budget_status`, `per_page_section_blueprints_status`, `per_page_meaningful_image_counts`, `per_page_visual_gaps`, `local_asset_files_status`, `missing_local_asset_files`, `browser_subresources_status`, `unstyled_live_paint_status`, `wp_media_map_status`, `wp_media_import_status`, `missing_wp_media_attachments`, `theme_slug`, `project/site_name`, `public_site_url`.
- WP Media release contract: `teya-memory/wp/wp-media-map.json`, `wp-media-import-log.md`, theme `media-map.json`; no MCP/tempfile URLs in public HTML (`wp-media-upload-contract.md`).
- Paint QA release contract: Design Guardian must create `teya-memory/wp/paint-qa/paint-evidence.json`, `paint-qa-report.md`, `home-1440-fullpage.png`, `home-375-fullpage.png`, plus `page-<slug>-1440-fullpage.png` and `page-<slug>-375-fullpage.png` for every selected/build page. JSON pass is invalid without real screenshot files, browser CSS/JS/images subresources, and no unstyled/default HTML paint.
- Safe file extension allowlist.
- `.deployignore` / `.distignore` policy.
- Never package credentials, `.env`, local secrets, logs, or `teya-memory`.
- Backup/snapshot before remote deploy.
- Rollback plan for theme activation and files.
- PHP lint and basic Theme Check guidance.
- Escaping/sanitization/nonces/security checks.
- Preview/sandbox guidance when available.
- Release blockers list.
- Release blockers must include missing visual inventory, missing/unimplemented visual budget or section blueprints on any selected/build page, required visual zones not implemented, meaningful image count below per-page minimum, missing per-page paint evidence, missing screenshot files, unstyled live paint, browser subresources missing theme CSS/JS/images, missing local asset files, missing WP media import or MCP/tempfile URLs in public HTML, generic/default inner pages, one hero image when source requires multiple visual zones, and stale report identity mismatch.
