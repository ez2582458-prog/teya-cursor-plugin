---
name: aurora-team-indexing
description: Aurora Team Indexing — robots.txt, sitemap.xml, canonical, noindex, redirects, llms.txt, AI crawler policy.
---

# Aurora Team Indexing

## Выход

`teya-memory/wp/indexing-crawl-map.md`

## Research Input

Читай `teya-memory/research/site-research-dossier.md`: учитывай текущий/старый сайт, публичный домен, конкурентный контекст и важные страницы.

## Обязательно

- `robots.txt` accessible, no blocking CSS/JS/images.
- Sitemap with canonical/indexable URLs and accurate `lastmod`.
- Self-referencing canonical on every indexable page.
- `noindex, follow` for search, 404, thank-you, utility pages.
- Redirect map for old URLs when existing site exists.
- Important pages within 3 clicks.
- AI crawler policy: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, PerplexityBot, Google-Extended, CCBot.
- `llms.txt` plan for AI retrieval.

Do not invent old URLs or redirects; mark missing migration data.

## Blockers

Final indexing status cannot be `✅` if:

- `project.public_site_url` is missing for remote deploy;
- `robots.txt` Host is not the public domain;
- `robots.txt` Sitemap is not the public domain;
- `/sitemap.xml` returns non-200 or non-XML;
- staging/test/technical hosting domain appears in canonical, robots, sitemap or schema;
- sitemap includes admin/search/thank-you/noindex URLs.
