---
name: aurora-team-navigation
description: Aurora Team Navigation — меню, футер, breadcrumbs, CTA и внутренняя перелинковка сайта.
---

# Aurora Team Navigation

## Выход

`teya-memory/wp/navigation-linking-map.md`

## Research Input

Читай `teya-memory/research/site-research-dossier.md`, `offers-map.md` и `audience-map.md`. Меню, CTA, блог-ссылки и anchors должны соответствовать аудитории и оферам из dossier.

## Обязательные решения

- Primary menu: 4-7 пунктов.
- Blog route `/blog/` обязателен.
- Homepage blog links: 3-6 тем из `11-blog-topics.md`.
- Footer menu: услуги, компания, контакты, legal, блог.
- Legal links are mandatory: “Политика конфиденциальности” and “Политика cookies”.
- CTA links.
- Breadcrumbs policy: no visible top breadcrumbs; JSON-LD BreadcrumbList only by default.
- 3-8 внутренних ссылок на SEO-страницу.
- Hub-and-spoke: pillar pages ↔ supporting pages.
- No orphan pages.

## Запреты

- Не использовать generic anchors без контекста.
- Не ссылаться как на готовые страницы на backlog-only URL.
- Не противоречить `06-url-map.csv`.
- Не размещать видимые breadcrumbs под header/над hero, если они перекрывают меню или ломают дизайн.
- Не делать blog placeholders: `скоро`, `готовится`, `пример`, `placeholder`, `lorem`.
- Не выпускать navigation map без privacy/cookies links.
