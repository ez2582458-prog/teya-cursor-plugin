---
name: aurora-team-schema
description: Aurora Team Schema — schema.org, technical SEO, robots/sitemap guidance, Google/Yandex/GEO requirements.
---

# Aurora Team Schema

## Выход

`teya-memory/wp/schema-technical-seo-map.md`

## Research Input

Читай `teya-memory/research/site-research-dossier.md` и `teya-memory/research/fact-bank.md`.

Schema.org, Organization/LocalBusiness, authors, facts, claims and sameAs must use only confirmed facts from `fact-bank.md`, `site.inv` or visible content.

## Schema

- Organization.
- LocalBusiness при наличии NAP/адреса/часов.
- WebSite + SearchAction.
- WebPage.
- BreadcrumbList JSON-LD без обязательного visible breadcrumb UI.
- FAQPage только когда FAQ видим на странице.
- Article только для статей.

## Google/Yandex

- JSON-LD должен совпадать с видимым контентом.
- Yandex: verification, Metrika defer, Organization/LocalBusiness fields.
- Google: canonical, robots, BreadcrumbList JSON-LD, mobile, Core Web Vitals basics.
- Не выдумывать ratings, prices, reviews, authors, address, geo.
