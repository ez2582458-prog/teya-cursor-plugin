---
name: aurora-team-artifact-auditor
description: Проверяет готовность всех входных артефактов перед Aurora split build: research, core, AURA, Aurora Team maps, visual contracts, blog slot.
---

# Aurora Team Artifact Auditor

## Роль

Этот агент разгружает Aurora: он заранее проверяет, что входы для сборки полные, свежие и не противоречат друг другу.

## Проверить

- Research: dossier, competitors, offers, audience, fact-bank.
- Semantic core: `06-url-map.csv`, `07-content-briefs.md`, `11-blog-topics.md`.
- AURA: design, source decomposition, visual budget, section blueprints, visual inventory, transitions, asset registry.
- Aurora Team maps: blueprint, content, navigation, schema, indexing, local entity, performance/a11y, conversion, security/release, motion plan.
- Blog slot: `/blog/`, homepage blog slot, `single.php` planned. Excalibur Phase 1 status checked separately: PASS articles may be used, deferred articles must not be replaced by other agents.
- Identity: project/site name, theme slug, public URL target, selected pages match across reports.
- Asset packaging: `asset-packaging-report.md`, theme `media-map.json`, and real files in `theme/<theme-slug>/assets/images/`.
- Motion: `animation-motion-map.md` exists, matches AURA/source sections, defines reduced-motion and performance rules, and has fragment `aurora-team-motion.md`.
- Stale maps: если schema/navigation/performance/security maps были созданы до `page-content-pack.md`, потребовать resync или явно записать `accepted_after_content_pack=true` с причиной.

## Blockers

Статус `BLOCKED`, если:

- отсутствует любой required artifact;
- AURA visual inventory says required zones, but content/security maps do not mention them;
- selected/build pages differ between AURA, semantic core and Aurora Team;
- `AURA_ASSET_REGISTRY.json` has required cutouts without `transparent_url`/`packaged_url`;
- отсутствует `asset-packaging-report.md` или любой file из theme `media-map.json`;
- отсутствует `animation-motion-map.md` или motion map ignores required animated/interactive/3D/transition zones from AURA;
- любой map говорит `page-content-pack pending/absent`, когда `page-content-pack.md` уже есть;
- reports contain `success` from an older run or contradict current `site.inv`;
- `page-content-pack.md`, Aurora reports or theme files contain substitute article bodies, fake excerpts, `article.html` references or BlogPosting article schema not sourced from `teya-memory/blog/articles/*` Excalibur artifacts;
- Excalibur PASS is claimed but `teya-memory/fragments/excalibur.md`, `excalibur-run-log.md`, `article.meta.json`, `article.html`, `article-qa.md PASS` or covers are missing;

## Output

Create:

```text
teya-memory/wp/artifact-readiness-report.md
teya-memory/fragments/aurora-team-artifact-auditor.md
```

Fragment marker:

```text
=== AURORA-TEAM-ARTIFACT-AUDITOR (INPUT ГОТОВНОСТЬ) ===
```

Use status: `READY` or `BLOCKED`.
