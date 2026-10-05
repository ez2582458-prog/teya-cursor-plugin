# Shared Inner-Page Template Contract

> RU: Одна общая (shared) раскладка для всех типовых внутренних страниц — услуги, гео, FAQ, цены, портфолио, «о нас»; страницы отличаются контентом, а не дизайном. Уникальный макет — только главная/лендинг или по прямой просьбе пользователя.

Decision by the user (Sergey) on 2026-10-05. Applies to AURA, Aurora Team Lead, Aurora Team Content, Aurora, WP Theme Builder, Design Guardian and QA. Rule entry point: `rules/shared-inner-page-template.mdc`.

## Why

A site with 40 similar inner pages must not get 40 different designs. Designing and coding every inner page separately wastes budget, drifts visually, and does not scale. Typical inner pages share **one designed template**; each page is a **content variant** of it.

## Page roles

| Role | Layout | WordPress file |
|------|--------|----------------|
| `home` / front page | unique, rich, may follow the full reference | `front-page.php` |
| `landing` (only when the user explicitly asks for a standalone promo landing) | unique | `page-{slug}.php` |
| `inner` — service, sub-service, geo/city, FAQ, prices, portfolio/cases, about, team, contacts-style info pages | **shared template `inner-shared`** | one `page-inner.php` (Template Name: «Внутренняя страница») or the default `page.php` |
| `blog` archive / `single` post | own system templates (unchanged) | `home.php`/`page-blog.php`, `single.php` |
| `legal` (privacy, cookies) | simple text variant of `inner-shared` (no hero image required) | same shared template or `page.php` |

A unique layout for an `inner` page is allowed **only** when:

1. the user explicitly asks for a unique design of that specific page, or
2. the page is the home page or an explicitly requested standalone landing, or
3. the page needs a genuinely different technical structure (calculator, configurator, canvas/3D scene, booking widget) that cannot be expressed as a content block — document the reason as `unique_template_reason` in `AURA_PAGE_PLAN.md` and `aurora-team-blueprint.md`.

"Looks nicer" or "SEO landing page" is not a reason. Without a recorded reason a `page-{slug}.php` for an inner page is a planning error.

## Anatomy of `inner-shared`

Fixed order of slots (each slot is designed once by AURA and styled once by Aurora):

1. **Hero + H1** — colored band / AURA motif background, H1 = page title, short lead, optional hero image (featured image), primary CTA button.
2. **Breadcrumbs slot** — BreadcrumbList JSON-LD always. Visible crumbs stay off by default (existing no-visible-top-breadcrumbs policy); if AURA defines a safe in-hero position below the H1 that never overlaps header/menu/CTA, the slot may render them there for every inner page at once.
3. **Intro** — 1-3 paragraphs answering the page intent directly (GEO/AEO 40-60-word answer first).
4. **Content sections (variable)** — ordered list of blocks from the shared block library (below), chosen per page from research, URL map and content briefs.
5. **FAQ** — visible accordion; feeds FAQPage JSON-LD.
6. **CTA / form** — shared CTA band + lead form (`wp_mail`, nonce, honeypot, consent); text can be overridden per page.
7. **Related links** — 3-8 contextual internal links (hub/spoke) from `navigation-linking-map.md`.

Only slots 4 (which blocks, in which order) and the texts/images of every slot change between pages. Slots 1-3, 5-7 keep the same structure, spacing, motifs and transitions on every inner page.

## Shared block library (content sections)

AURA designs, and Aurora implements once, a small library of section blocks that pages combine. Typical set (AURA adapts to the reference, 6-10 blocks is enough):

- `text-image` — text + image (left/right variants)
- `cards-grid` — services / benefits / features with icons or images
- `steps` — process / how it works
- `prices` — price table or price cards (real prices only, from fact bank)
- `gallery` — portfolio / cases / photos
- `geo-facts` — local facts, service area, address/map, NAP (for geo pages)
- `stats-proof` — numbers, licenses, guarantees (verified facts only)
- `quote` / `team` — people, expertise (real data only)
- `cta-band` — mid-page CTA

Each block has the same AURA treatment (tokens, motifs, card style, transitions) wherever it appears. New block types are added to the library, never designed ad hoc for one page.

## WordPress implementation (WordPress-by-default rule still applies)

- The template is coded **once**: `page-inner.php` (`Template Name: Внутренняя страница`) or `page.php`, plus `template-parts/inner/hero.php`, `faq.php`, `cta.php`, `related.php`.
- Page content lives in **WP admin**, inside `the_content()`: H1 = page title, hero lead = excerpt or a registered post meta field, hero image = featured image, content sections and FAQ = Gutenberg **block patterns** registered by the theme (`register_block_pattern()` with category `teya-inner`), e.g. `teya/text-image`, `teya/cards-grid`, `teya/steps`, `teya/prices`, `teya/gallery`, `teya/geo-facts`, `teya/faq`, `teya/cta-band`. Patterns use core blocks (group, columns, image, heading, paragraph, list, details, buttons) + theme CSS classes, so the editor can add, reorder or remove sections without code.
- Alternative allowed when the editor is disabled or patterns are impractical: the template renders the same slots and the variable blocks come from `the_content` HTML with the same CSS classes. Never hard-code page texts in PHP.
- `meta description` stays in `post_excerpt` per playbook; if the excerpt is used for SEO, the hero lead comes from a registered meta field (`register_post_meta`, sanitized, shown in a small meta box) — no ACF Pro / paid builders.
- FAQPage JSON-LD is built from the visible FAQ pattern (`core/details` blocks inside `.teya-faq`), so schema always matches visible content.
- Per-page CTA override: optional post meta (`teya_cta_title`, `teya_cta_text`), defaulting to Customizer CTA settings.
- The mu-plugin setup (if used) creates every inner page with `_wp_page_template = page-inner.php` (or default) and fills `post_content` with pattern markup from `page-content-pack.md`.
- Adding page N+1 later = create a page in admin, pick «Внутренняя страница», insert patterns. No theme change, no new design.

## Scaling and the test page limit

The current Aurora test limit (home + up to 4 inner pages) is **unchanged**. The template is built so that, once the Director lifts the limit, any number of inner pages (10, 40, 100) reuse it with no extra design or theme work — only content.

## Artifacts — how to specify

### `AURA_PAGE_PLAN.md`

Add a `## Templates` section before `## Pages`:

```markdown
## Templates

### home
- file: front-page.php
- layout: unique (full reference fidelity)

### inner-shared
- file: page-inner.php (Template Name: Внутренняя страница)
- slots: hero+H1, breadcrumbs (JSON-LD; visible only in safe in-hero spot), intro, content-blocks, FAQ, CTA/form, related links
- block_library: text-image, cards-grid, steps, prices, gallery, geo-facts, stats-proof, cta-band
- visual_treatment: colored hero band + motif X, card style Y, transition Z (from AURADESIGN.md)
- min_meaningful_images: hero image + >=1 image-bearing block
```

Each inner page in `## Pages` then lists only `template: inner-shared`, `content_variant` (ordered blocks) and page-specific images — no separate composition, no separate `key_sections` design.

### `AURA_VISUAL_BUDGET.json` / `AURA_SECTION_BLUEPRINTS.json` / `AURA_VISUAL_INVENTORY.json`

- Add `templates[]` with one entry for `inner-shared` (budget, blueprints per slot and per library block, visual zones).
- `pages[]` entries for inner pages set `"template": "inner-shared"` and `"inherits_template_budget": true`; they may add page-specific asset instances (e.g. hero image of that service) but do not redefine layout.
- The home page keeps its own full per-page entry.

### `aurora-team-blueprint.md`

- `page template map`: home → `front-page.php`; every typical inner page → `page-inner.php`; exceptions listed with `unique_template_reason`.
- `content variants` table: slug × ordered blocks × required images × FAQ count × CTA override.

### `page-content-pack.md`

Per inner page, texts are grouped by slot: hero (H1, lead, CTA), intro, blocks in order (block type + copy + images/alt), FAQ, CTA override, related links.

## Gates — how to read existing rules

- "Inner page must not be a generic/default text template" means: no **unstyled/default WP look**. A shared template that is fully designed by AURA (colored hero, motifs, custom cards, transitions, real images) satisfies the rule; the same template on many pages is the intended result, not a violation.
- Per-page visual budget / meaningful image minimums for inner pages are checked against the `inner-shared` template budget plus the page's own asset instances.
- Design Guardian / QA flag as a planning defect: N different custom layouts for similar inner pages without `unique_template_reason`, or hard-coded page texts in PHP templates.
