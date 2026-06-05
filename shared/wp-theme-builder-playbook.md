# Teya Aurora WordPress Theme Playbook

This playbook distills the useful production rules from the Desktop reference project `WP Teamplate`.

Aurora (`aurora`) must treat this as a hard contract when creating a WordPress theme from Teya outputs.

Aurora must also read `teya/shared/quality-anti-haltura.md`. Thin pages, missing blocks, placeholders, fake reviews, broken hero, broken sitemap/robots or staging-domain leakage are release blockers, not warnings.

Aurora is a subagent and must not launch nested subagents. The Director runs `aurora-team-lead`, `aurora-team-content`, `aurora-team-navigation`, `aurora-team-schema`, `aurora-team-indexing`, `aurora-team-local-entity`, `aurora-team-performance-a11y`, `aurora-team-conversion`, `aurora-team-security-release`, `aurora`, and `aurora-team-qa` as peer tasks.

## Input Order

Read inputs in this order:

1. `<PROJECT_ROOT>/teya-memory/site.inv` — structured user intake.
2. `<PROJECT_ROOT>/teya-memory/00-brief.md` — natural-language brief.
3. `<PROJECT_ROOT>/teya-memory/research/site-research-dossier.md`.
4. `<PROJECT_ROOT>/teya-memory/research/competitors.csv`.
5. `<PROJECT_ROOT>/teya-memory/research/offers-map.md`.
6. `<PROJECT_ROOT>/teya-memory/research/audience-map.md`.
7. `<PROJECT_ROOT>/teya-memory/research/fact-bank.md`.
8. Latest `<PROJECT_ROOT>/teya-memory/semantic-core/<run>/`.
9. `<PROJECT_ROOT>/teya-memory/design/AURADESIGN.md`.
10. `<PROJECT_ROOT>/teya-memory/design/AURA_PAGE_PLAN.md`.
11. `<PROJECT_ROOT>/teya-memory/design/AURA_VISUAL_INVENTORY.json`.
12. `<PROJECT_ROOT>/teya-memory/design/AURA_SHAPE_MAP.json`.
13. `<PROJECT_ROOT>/teya-memory/design/AURA_SECTION_TRANSITIONS.json`.
14. `<PROJECT_ROOT>/teya-memory/design/AURA_ASSET_REGISTRY.json`.
15. `<PROJECT_ROOT>/teya/shared/visual-assets-mcp-policy.md`.
16. `<PROJECT_ROOT>/teya/shared/wp-media-upload-contract.md`.
17. `<PROJECT_ROOT>/teya/shared/reference-visual-fidelity-gate.md`.
18. `<PROJECT_ROOT>/teya-memory/wp/aurora-team-blueprint.md`.
18. `<PROJECT_ROOT>/teya-memory/wp/page-content-pack.md`.
19. `<PROJECT_ROOT>/teya/shared/quality-anti-haltura.md`.
20. `<PROJECT_ROOT>/teya-memory/wp/navigation-linking-map.md`.
21. `<PROJECT_ROOT>/teya-memory/wp/schema-technical-seo-map.md`.
22. `<PROJECT_ROOT>/teya-memory/wp/indexing-crawl-map.md`.
23. `<PROJECT_ROOT>/teya-memory/wp/local-entity-map.md`.
24. `<PROJECT_ROOT>/teya-memory/wp/performance-accessibility-map.md`.
25. `<PROJECT_ROOT>/teya-memory/wp/conversion-tracking-map.md`.
26. `<PROJECT_ROOT>/teya-memory/wp/security-release-map.md`.
27. `<PROJECT_ROOT>/teya-memory/01-handoff.md`.

If `site.inv` is missing, create `teya-memory/site.inv` from `teya/shared/site.inv.example`, fill what is known from `00-brief.md`, and stop with a clear list of missing required fields before deployment.

If `teya-memory/research/site-research-dossier.md` is missing, Aurora must stop and return a blocker to the Director. Aurora must not build from brief alone.

## Aurora Test Page Scope

In the current test phase Aurora creates **maximum 5 pages total**:

1. Front page / homepage.
2. Up to 4 most important inner pages.

Page selection rules:

- Use `AURA_PAGE_PLAN.md` as the **design** source of truth.
- Use Yadryshko/Core outputs (`06-url-map.csv`, `07-content-briefs.md`, `05-clusters.csv`) as the **semantic** source of truth.
- Aurora must combine both. AURA does not own SEO structure; Yadryshko does not own visual composition.
- Cross-check selected pages against `06-url-map.csv` and `07-content-briefs.md`.
- Prefer pages marked `build_in_test: yes`.
- If AURA marks more than 5 pages, keep the homepage and the four inner pages with the strongest Yadryshko SEO priority; use AURA design priority only as a tie-breaker.
- If AURA marks fewer pages, add P0 pages from semantic-core until the limit is reached.
- Write the final selection to `teya-memory/wp/aurora-page-selection.md`.

If a page exists only in AURA, do not treat it as an SEO landing page unless Yadryshko confirms it. It may become a service/UX page only when required by the brief.

If a page exists only in Yadryshko, use the closest AURA template and document the design assumption in `aurora-page-selection.md`.

## Aurora Team Artifacts

Aurora must integrate these files:

- `aurora-team-blueprint.md` — sitemap, selected pages, templates, menu/footer, SEO/GEO requirements.
- `page-content-pack.md` — page copy, headings, meta, FAQ, CTA, answer blocks, target text length.
- `navigation-linking-map.md` — primary menu, footer menu, breadcrumbs, internal links, anchors.
- `schema-technical-seo-map.md` — JSON-LD, canonical, robots, Yandex/Google technical requirements.
- `indexing-crawl-map.md` — robots.txt, sitemap.xml, canonical, noindex, redirects, `llms.txt`, AI crawlers.
- `local-entity-map.md` — NAP, Yandex Business, Google Business Profile, 2GIS, maps, reviews, LocalBusiness.
- `performance-accessibility-map.md` — Core Web Vitals, images, fonts, JS/CSS, WCAG, keyboard/focus.
- `conversion-tracking-map.md` — forms, CTA, consent, anti-spam, SMTP/delivery, Metrika/GA4 events.
- `security-release-map.md` — SiteSpec, build report, deployignore, backup, rollback, security checks, release gates.

If one of these files is missing, Aurora must stop with `❌ БЛОКЕР` instead of silently inventing the missing layer.

## Deterministic Build Artifacts

Before writing theme files, Aurora must synthesize:

```text
teya-memory/wp/site-spec.json
```

This file should describe selected pages, slugs, templates, menus, schema types, forms, assets, analytics, indexing policy, and deploy mode in a deterministic machine-readable format.

After writing theme files, Aurora must write:

```text
teya-memory/wp/build-report.json
```

This report should include generated files, pages, templates, menus, forms, schema, indexing outputs, checks run, skipped checks with reasons, package path, deploy status, and rollback data.

## Required WordPress Theme Structure

The generated theme must be self-contained and must work without page builders or required premium plugins.

Minimum required theme root:

```text
style.css
index.php
functions.php
header.php
footer.php
front-page.php
page.php
single.php
archive.php
search.php
searchform.php
404.php
comments.php
screenshot.png or screenshot.jpg
theme.json
inc/setup.php
inc/enqueues.php
inc/seo.php
inc/customizer.php
inc/breadcrumbs.php
inc/security.php
template-parts/content/content.php
template-parts/content/content-none.php
assets/dist/style.css
assets/dist/main.js
assets/src/scss/main.scss
assets/src/js/main.js
```

For each selected page from `AURA_PAGE_PLAN.md` + `06-url-map.csv`, create either:

- `page-{slug}.php` with a Template Name header, or
- a robust `page.php` + `_wp_page_template` assignment strategy.

Prefer explicit `page-{slug}.php` for landing/service pages with custom design, scripts, canvas, or complex sections.

## style.css Header

`style.css` must begin with a valid WordPress header:

```css
/*
Theme Name: Teya Generated Site
Theme URI: https://example.com
Author: Teya
Author URI: https://example.com
Description: Production WordPress theme generated by Teya.
Version: 1.0.0
License: GNU General Public License v2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html
Text Domain: teya-generated-site
Tags: custom-logo, custom-menu, featured-images, threaded-comments, translation-ready
*/
```

Rules:

- Text Domain must match every translation function.
- Version must be used for cache busting or bumped before packaging.
- The theme folder slug should match `project.theme_slug` from `site.inv`.

## PHP Safety

Every PHP file except `style.css` must include:

```php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
```

Escaping rules:

- Text: `esc_html()`, `esc_html_e()`
- Attributes: `esc_attr()`, `esc_attr_e()`
- URLs: `esc_url()`
- Rich editor HTML: `wp_kses_post()`
- JSON-LD: `wp_json_encode( ..., JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES )`

Never raw-echo user input, database values, contact fields, titles, excerpts, URLs, or schema values.

## Header Contract

`header.php` must include:

- `<!DOCTYPE html>`
- `<html <?php language_attributes(); ?>>`
- `<meta charset="<?php bloginfo( 'charset' ); ?>">`
- `<meta name="viewport" content="width=device-width, initial-scale=1">`
- `wp_head()` before `</head>`
- `<body <?php body_class(); ?>>`
- `wp_body_open()` immediately after body
- skip link to `#primary`
- accessible logo link to `home_url( '/' )`
- responsive logo with explicit `width`/`height`
- `loading="eager"` and `fetchpriority="high"` for the logo or LCP hero image when appropriate

Every custom template must include:

```html
<main id="primary" class="site-main">
```

If a page template is generated from raw HTML, wrap it in `main#primary` before deployment.

## Theme Setup

`inc/setup.php` must include:

- `add_theme_support( 'title-tag' )`
- `add_theme_support( 'post-thumbnails' )`
- `add_theme_support( 'html5', ... )`
- `add_theme_support( 'custom-logo', ... )`
- `add_theme_support( 'responsive-embeds' )`
- `add_theme_support( 'align-wide' )`
- `register_nav_menus()` for `primary` and `footer`
- `register_sidebar()` for footer/widget areas

If the generated theme owns the full layout, it may dequeue Gutenberg block styles, but only if this does not break posts/pages.

## Enqueues and Performance

`inc/enqueues.php` must:

- enqueue one main CSS file and one main JS file;
- use theme version or `filemtime()` for cache busting;
- defer JS (`strategy => defer`, `in_footer => true`) where supported;
- preload critical CSS with the same version as the enqueue URL;
- add `dns-prefetch`/`preconnect` for fonts only when external fonts are used;
- not enqueue jQuery unless the design explicitly needs it;
- add `defer` for analytics scripts containing `mc.yandex.ru` or `metrika`.

Performance rules from the reference theme:

- Avoid keyframe animation of `box-shadow`; prefer `transform` and `opacity`.
- Touch targets for interactive controls should be at least 44-48px.
- Use explicit image dimensions to reduce CLS.
- Do not lazy-load the logo or primary LCP image.
- Lazy-load below-the-fold images.

## SEO and GEO

`inc/seo.php` must output in one central place:

- unique title logic via `pre_get_document_title`;
- meta description per front page, generated service pages, blog posts, archive, search, 404;
- canonical URL, while removing default duplicate `rel_canonical` if printing a custom canonical;
- Open Graph: title, description, image, url, type, site_name, locale;
- Twitter Card;
- robots meta: `index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1` for indexable pages; `noindex, follow` for search/404;
- JSON-LD where applicable:
  - Organization
  - Person or LocalBusiness if contact/business data supports it
  - WebSite + SearchAction
  - WebPage
  - Article for posts
  - FAQPage when visible FAQ exists
  - BreadcrumbList
  - Course/Offer only if the business is actually a course/product with real price/rating data
  - Speakable selectors for GEO/AI search when content has clear answer sections

Schema must match visible page content. Do not invent ratings, prices, authors, addresses, or legal organization data.

## Content Depth and GEO/AEO

Use `page-content-pack.md` as the content source. Recommended minimums:

- Homepage: 5,000-9,000 characters.
- Commercial P0/P1 service page: 4,000-8,000 characters.
- Local/geo landing page: 3,500-7,000 characters plus visible NAP/regional signals when available.
- Expert article or guide: 8,000-15,000+ characters when intent requires depth.

Rules:

- helpful, people-first content beats artificial length;
- one H1 per page;
- Title should usually be 50-60 characters;
- meta description should usually be 150-160 characters;
- use clear H2/H3 hierarchy;
- add question-style H2 where it matches search intent;
- after important question headings, include a direct 40-60 word answer block for GEO/AEO;
- visible FAQ must match FAQPage schema;
- no invented prices, ratings, reviews, licenses, addresses, guarantees, or case studies.

Yandex-specific:

- support `yandex-verification` from `site.inv`;
- include Host in generated `robots.txt` guidance when the domain is known;
- do not block YandexBot, Googlebot, Bingbot, or major AI search crawlers in security filters.
- if LocalBusiness/Organization schema is used, include visible matching name, phone, address/city, URL, and opening hours when available;
- pages with organization/location markup must be reachable from the home page through visible internal links.

Google-specific:

- use JSON-LD for structured data;
- keep content helpful, readable, and organized;
- links must be crawlable and descriptive;
- do not render visible top breadcrumbs; use BreadcrumbList JSON-LD only, unless the Director explicitly requests visible breadcrumbs in a design-safe position;
- schema must be eligible by content type and must match visible page content.

## Indexing, Crawl, and AI Retrieval

Use `indexing-crawl-map.md`.

Required:

- create or document `robots.txt` with `Sitemap:` reference;
- do not block critical CSS, JS, images, Googlebot, YandexBot, Bingbot, or approved AI crawlers;
- AI crawler policy should explicitly consider GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, PerplexityBot, Google-Extended, and CCBot;
- create or document `sitemap.xml` with only canonical, indexable URLs;
- include accurate `lastmod` dates when they are known;
- add self-referencing canonical on every indexable page;
- set `noindex, follow` for search, 404, thank-you, and utility pages;
- create redirect guidance for old URLs if `site.inv` or brief indicates an existing website;
- keep important pages within three clicks of the homepage;
- generate `llms.txt` when requested by the indexing map, listing site purpose, key pages, and content usage notes.

Never invent old URLs, migration redirects, or canonical domains. Mark missing migration data clearly.

## Local Entity and Business Profiles

Use `local-entity-map.md`.

Required:

- use one canonical NAP: name, address, phone, email, opening hours;
- render NAP consistently in footer/contact blocks when data exists;
- implement Organization or the most specific LocalBusiness subtype when business data supports it;
- use `sameAs`, `areaServed`, `geo`, and `openingHoursSpecification` only when real data exists;
- include Yandex Business, Google Business Profile, and 2GIS checklist links/status when available;
- embed Yandex Maps or Google Maps only when a real address/service area exists;
- add reviews CTA/strategy, but never output fake AggregateRating, Review, or rating values;
- create location pages only with unique local facts, local services, NAP, landmarks/service area, and visible value beyond a city-name swap.

## Performance and Accessibility

Use `performance-accessibility-map.md`.

Targets:

- LCP under 2.5s;
- INP under 200ms;
- CLS under 0.1.

Required:

- do not lazy-load the primary LCP image;
- use explicit image dimensions and responsive `srcset`/`sizes` where possible;
- prefer WebP/AVIF when assets are available;
- lazy-load below-the-fold images;
- use `font-display: swap`;
- preload only critical fonts/assets;
- defer non-critical JS;
- respect `prefers-reduced-motion`;
- keep animations on `transform` and `opacity`;
- provide visible focus states, keyboard-accessible menus, labels for form controls, sufficient contrast, and 44-48px touch targets;
- include skip link and semantic landmarks.

## Conversion, Forms, and Tracking

Use `conversion-tracking-map.md`.

Required:

- CTA links in header, hero, service sections, and footer;
- lead forms with validation, success state, error state, and privacy consent;
- cookie notice when analytics/cookies are used;
- anti-spam basics: nonce, honeypot, and rate-limit recommendation;
- SMTP/delivery requirements documented, never hardcode secrets;
- click tracking hooks for phone, email, messengers, and CTA;
- Yandex Metrika and GA4 event names when IDs exist;
- thank-you pages should usually be `noindex, follow`;
- if CRM/webhook credentials are missing, build the form UI safely and document missing integration data.

## Security, Release, and Rollback

Use `security-release-map.md`.

Required:

- generate `site-spec.json` before building;
- generate `build-report.json` after building;
- use a strict file allowlist for generated theme/package files;
- never include credentials, `.env`, local secret files, logs, or `teya-memory` in packages;
- create `.deployignore` or `.distignore` when packaging/deploying;
- run PHP syntax checks when PHP is available;
- run Theme Check or document why unavailable;
- verify escaping, sanitization, nonces, and allowed HTML for user-facing forms/settings;
- create backup/snapshot guidance before remote deploy;
- record rollback path: previous active theme, backup artifact, restoration steps;
- remote deployment must stop on release blockers.

## Breadcrumbs

`inc/breadcrumbs.php` should:

- skip breadcrumbs on the front page;
- support posts, pages with parents, categories, tags, archives, search, 404;
- escape HTML output;
- emit BreadcrumbList JSON-LD;
- not render a visible top breadcrumb block by default;
- never place visible breadcrumbs above/inside the header area, over the menu, or before the hero when that breaks the design.

## Navigation and Internal Linking

Use `navigation-linking-map.md`.

Required:

- primary menu with 4-7 clear items;
- primary menu must include blog unless the test page limit explicitly moves it to footer-only, but the site still needs a blog route;
- footer menu with services, company, contacts, legal pages, and blog;
- header/hero/footer CTA links;
- no visible top breadcrumbs on inner pages; use JSON-LD BreadcrumbList for SEO instead;
- 3-8 contextual internal links on each SEO page;
- descriptive anchors, never generic `click here` / `подробнее` without context;
- homepage links to priority P0/P1 pages;
- supporting pages link back to pillar pages;
- no orphan pages among generated pages.

## Customizer / Theme Mods

`inc/customizer.php` should expose user-editable settings:

- social links
- CTA URL/text
- footer copyright
- Google verification
- Yandex verification
- optional Metrika counter ID

Use proper sanitizers:

- URL: `esc_url_raw`
- text: `sanitize_text_field`
- textarea/code snippets: avoid raw code if possible; otherwise sanitize tightly.

## Footer, Legal, and Forms

The footer must use data from `site.inv`:

- brand name and description;
- contacts;
- social links;
- legal links;
- CTA.

Standard legal pages are mandatory for production:

- `privacy` / `privacy-policy`: “Политика конфиденциальности”.
- `cookies` / `cookie-policy`: “Политика cookies”.
- Both pages must use real business/site data from `site.inv` where available.
- If exact legal entity data is incomplete, write a standard neutral policy with placeholders replaced by site name, public URL, contact email/phone, and mark missing legal facts in `verification.md`; do not publish raw placeholders.
- Footer must link to both pages.

For forms that collect personal data:

- add a required privacy/consent checkbox;
- link to privacy policy and data processing consent;
- do not inject consent into search forms.

Cookie banner:

- include a visible cookie notice on production sites;
- include a clear accept button: “Принять cookies” / “Принять”;
- store consent in a first-party cookie or localStorage;
- do not load optional analytics until consent when consent mode is required by the project;
- link to cookie policy and privacy policy;
- banner must be accessible, keyboard reachable, and not cover primary CTA/menu in a way that blocks navigation.

## Visual Assets and Section Transitions

Aurora must implement AURA visuals as production UI, not as generic placeholders.

Required:

- shapes/decor follow `AURA_SHAPE_MAP.json`;
- visual zones follow `AURA_VISUAL_INVENTORY.json`;
- section joins follow `AURA_SECTION_TRANSITIONS.json`;
- generated/cutout assets follow `AURA_ASSET_REGISTRY.json`;
- MCP-required images use `gpt-image-2` and `recraft_remove_background` according to `visual-assets-mcp-policy.md`;
- complex transitions may use inline SVG, CSS `clip-path`, `mask-image`, gradients, pseudo-elements, negative margins, z-index layers, or generated visual assets;
- mobile 375px must preserve the transition without covering H1, CTA, menu, forms, or legal/cookie UI.
- `site-spec.json` and `build-report.json` must include `visual_inventory_status`, `required_visual_zones_count`, `ready_visual_zones_count`, `meaningful_image_count`, `minimum_meaningful_image_assets_homepage`, `meaningful_image_gap`, `section_transitions_status`, `asset_registry_status`, `paint_evidence_status`, `visual_budget_status`, `section_blueprints_status`, `style_match_scorecard_status`, `per_page_visual_budget_status`, `per_page_section_blueprints_status`, `per_page_meaningful_image_counts`, `per_page_visual_gaps`, `local_asset_files_status`, `missing_local_asset_files`, `browser_subresources_status`, `unstyled_live_paint_status` per selected page.
- `meaningful_image_count` must count only real image/illustration/cutout/mockup assets. CSS cards, gradients, blobs and section backgrounds do not count.

Blockers:

- missing `AURA_VISUAL_INVENTORY.json`;
- required visual zones not implemented;
- meaningful image count below `minimum_homepage_visual_assets` / `minimum_meaningful_image_assets_homepage`;
- per-page meaningful image count below `minimum_meaningful_image_assets`;
- required local asset files missing from `teya-memory/wp/theme/<theme-slug>/`;
- `paint-evidence.json` references screenshot files that do not exist;
- browser network does not request theme CSS/JS/images or live screenshot looks like unstyled/default HTML;
- source image-bearing cards/form-side images collapsed into plain text blocks;
- multiple source image scenes collapsed into one hero image or one strip;
- homepage or inner selected/build page has only one meaningful image when source distributes visuals across cards/forms;
- inner selected/build page is a generic/default text template instead of inheriting AURA visual language;
- replacing a source wave/blob/mask/overlap with a plain straight section;
- using stock/fallback URLs for AURA-required assets;
- claiming background removal without a real transparent asset URL/path;
- leaving hero/person/object cutouts visibly chopped at the section edge;
- creating CSS-only fake assets when AURA required MCP generation.

## Page and Post Creation

For each selected page in `AURA_PAGE_PLAN.md` and `06-url-map.csv`:

- create a page with the requested slug;
- set `_wp_page_template` when using custom templates;
- set `post_excerpt` from meta description, because themes and SEO modules may use it;
- keep H1, title, description, FAQ, and URL aligned with semantic-core briefs;
- create internal links according to URL map.
- create content and sections according to `page-content-pack.md`.
- create menus and contextual links according to `navigation-linking-map.md`.
- create schema/meta according to `schema-technical-seo-map.md`.
- create robots/sitemap/canonical/noindex/llms guidance according to `indexing-crawl-map.md`.
- create NAP/local entity/profile/map elements according to `local-entity-map.md`.
- create performance and accessibility implementation according to `performance-accessibility-map.md`.
- create forms, CTA, consent, and tracking hooks according to `conversion-tracking-map.md`.
- create deterministic spec, build report, deployignore, backup/rollback, and security checks according to `security-release-map.md`.
- do not create more than 5 pages total in test mode unless the Director explicitly removes the limit.

For blog:

- blog is required for every production Teya site;
- homepage must include a real “Блог” / insights section with 3-6 topics from `11-blog-topics.md`;
- create `home.php` or `page-blog.php`;
- create or reserve the `/blog/` route in menus and internal linking without placeholder copy;
- render card layout with thumbnail, title, excerpt, date, category;
- include pagination;
- `single.php` should include author/date/modified date, reading time, article schema support, related/internal links, and content;
- do not publish fake starter posts, lorem, “скоро”, “статья готовится” or placeholder blog cards.

## Deployment

Credentials come from:

1. Environment variables (`FTP_*`, `SSH_*`, `PUBLIC_SITE_URL`, `WP_*`).
2. `<PROJECT_ROOT>/teya-memory/hosting.credentials.local`.
3. `site.inv` may reference the host and deployment mode, but committed templates must not contain real secrets.

If credentials are missing, build locally and stop with status `⚠️ ГОТОВО К ДЕПЛОЮ`.

If credentials are present:

1. Prefer SSH/SFTP when available; FTP is acceptable when only FTP exists.
2. Upload into the real active theme path.
3. Import all required images into WordPress Media Library with alt meta per `wp-media-upload-contract.md`. Reuse `teya/scripts/teya_wp_media_import.py` (`build_manifest`, `inject_media_import_php`, `write_wp_media_artifacts`) or project deploy script that embeds the same bootstrap PHP.
4. Create `teya-memory/wp/wp-media-map.json`, `wp-media-import-log.md` and theme `media-map.json`.
5. If WP-CLI is available, verify:
   - active stylesheet/template;
   - created page IDs;
   - `_wp_page_template`;
   - `post_excerpt`;
   - permalink structure.
4. Set file permissions: 644 files, 755 directories.
5. Clear object/page cache when possible.
6. Verify live HTML, not just HTTP 200.

Live verification must check:

- public URL resolves;
- `body_class` includes the generated theme slug or page markers;
- `main#primary` exists;
- no default `page.php` symptom when a custom template was expected;
- CSS/JS assets return 200;
- meaningful images load from `/wp-content/uploads/`, not MCP/tempfile/remote URLs;
- every meaningful `<img>` has non-empty descriptive `alt`;
- `wp-media-map.json` exists and matches current deploy;
- no fatal PHP output;
- contacts and CTA are visible;
- generated P0 pages open;
- primary menu and footer menu are visible;
- 3-8 contextual internal links exist on SEO pages;
- schema matches `schema-technical-seo-map.md`;
- robots/sitemap/canonical/noindex/llms output matches `indexing-crawl-map.md`;
- NAP/local entity output matches `local-entity-map.md`;
- performance/accessibility output matches `performance-accessibility-map.md`;
- forms/CTA/tracking output matches `conversion-tracking-map.md`;
- security/release output matches `security-release-map.md`;
- `site-spec.json` exists and matches selected pages/artifacts;
- `build-report.json` exists and lists generated files/checks/deploy status;
- content depth matches `page-content-pack.md` or missing facts are documented;
- homepage blog section exists and uses real topics from `11-blog-topics.md`;
- blog archive and a single post template work.

## Packaging

Create a zip only with runtime files:

- include theme PHP, `inc/`, `template-parts/`, `assets/`, `screenshot`, `theme.json`;
- exclude `node_modules`, temporary scripts, raw credentials, logs, and `teya-memory`;
- zip root must be exactly one folder named `<theme-slug>/`.

## Final Aurora Output

Write:

- `teya-memory/wp/deploy-log.md`
- `teya-memory/wp/verification.md`
- `teya-memory/wp/theme/<theme-slug>/`
- `teya-memory/wp/aurora-page-selection.md`
- read-only integration of `aurora-team-blueprint.md`, `page-content-pack.md`, `navigation-linking-map.md`, `schema-technical-seo-map.md`, `indexing-crawl-map.md`, `local-entity-map.md`, `performance-accessibility-map.md`, `conversion-tracking-map.md`, `security-release-map.md`
- `teya-memory/wp/site-spec.json`
- `teya-memory/wp/build-report.json`
- optional `teya-memory/wp/<theme-slug>.zip`

Append one block to `teya-memory/01-handoff.md`:

```markdown
=== AURORA (WP-ТЕМА И СТРАНИЦЫ) ===
## Статус: ✅ ОПУБЛИКОВАНО | ⚠️ ГОТОВО К ДЕПЛОЮ | ❌ БЛОКЕР
Theme slug: ...
Local theme: teya-memory/wp/theme/...
Zip: ...
Test page limit: 5
Public URL: ...
Pages created: ...
Blog created: ...
Deploy method: SSH/SFTP/FTP/local-only
Page selection: teya-memory/wp/aurora-page-selection.md
Team blueprint: teya-memory/wp/aurora-team-blueprint.md
Content pack: teya-memory/wp/page-content-pack.md
Navigation/linking: teya-memory/wp/navigation-linking-map.md
Schema map: teya-memory/wp/schema-technical-seo-map.md
Indexing/crawl: teya-memory/wp/indexing-crawl-map.md
Local entity: teya-memory/wp/local-entity-map.md
Performance/a11y: teya-memory/wp/performance-accessibility-map.md
Conversion/tracking: teya-memory/wp/conversion-tracking-map.md
Security/release: teya-memory/wp/security-release-map.md
SiteSpec: teya-memory/wp/site-spec.json
Build report: teya-memory/wp/build-report.json
Verification: teya-memory/wp/verification.md
Deploy log: teya-memory/wp/deploy-log.md
Missing data: ...
```
