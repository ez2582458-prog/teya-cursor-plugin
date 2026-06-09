---
name: aurora-team-content
description: Aurora Team Content — SEO/GEO контент-пакет страниц: H1, title, description, секции, FAQ, answer-блоки, CTA и объёмы.
---

# Aurora Team Content

## Выход

`teya-memory/wp/page-content-pack.md`

## Research Input

Обязательно читай:

- `teya-memory/research/site-research-dossier.md`
- `teya-memory/research/offers-map.md`
- `teya-memory/research/audience-map.md`
- `teya-memory/research/fact-bank.md`
- `teya-memory/design/AURA_VISUAL_INVENTORY.json`
- `teya-memory/design/AURA_ASSET_REGISTRY.json`

Тексты, FAQ, CTA, E-E-A-T и ограничения должны опираться на research. Не выдумывать факты вне `fact-bank.md`/brief.

## На каждую страницу

- slug и intent;
- main query / cluster;
- H1, Title, Description;
- рекомендуемый объём текста;
- H2/H3 структура;
- готовый hero copy;
- готовые тексты секций, а не только названия блоков;
- homepage blog section copy с 3-6 темами из `11-blog-topics.md` или Excalibur `article.meta.json`;
- blog archive intro copy без заглушек;
- FAQ с готовыми ответами;
- answer-блоки 40-60 слов;
- CTA;
- E-E-A-T сигналы;
- alt requirements.
- visual requirements from AURA: image-bearing cards, form-side visuals, callouts, mockups, thumbnails;
- alt drafts for each required visual zone.

## Block Inventory

Для каждой страницы обязательно:

```text
required_blocks:
implemented_blocks:
missing_blocks:
text_length_target:
text_length_planned:
placeholder_scan:
internal_links_required:
blog_section_status:
visible_top_breadcrumbs_policy:
visual_inventory_status:
required_visual_zones:
visual_alt_requirements:
verdict:
```

`missing_blocks` должен быть пустым для статуса `✅`.

## Объём

- Главная: 5 000-9 000 знаков.
- Коммерческая P0/P1: 4 000-8 000 знаков.
- Гео/локальная: 3 500-7 000 знаков.
- Экспертная статья: 8 000-15 000+ знаков.

Не выдумывать цены, рейтинги, кейсы, лицензии, адреса или гарантии.

## Анти-халтура

Следуй `teya/shared/quality-anti-haltura.md`.

Запрещено:

- `пример отзыва`, `пример участника`, `в разработке`, `скоро`, `TODO`, `placeholder`, `lorem`;
- фейковые отзывы;
- страницы без готового текста;
- страницы без FAQ, CTA и внутренних ссылок.
- главная без раздела “Блог”/“Материалы”;
- blog cards `скоро`, `готовится`, `пример`, `placeholder`, `lorem`.
- писать финальные статьи блога, `article.html`, SEO longreads, BlogPosting schema или fake article excerpts. Статьями занимается только Excalibur в Phase 1. Content может дать только section copy, archive intro и card copy из `11-blog-topics.md`/Excalibur meta.
