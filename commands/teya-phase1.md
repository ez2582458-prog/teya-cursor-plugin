---
description: Teya фаза 1 — Research, затем Ядрышko + AURA, Aurora Team, Aurora, Design Guardian и QA.
---

# Teya — фаза 1

Перед первым запуском нового сайта Директор обязан очистить память старого проекта:

```bash
python teya/scripts/reset_teya_memory.py --project-root <PROJECT_ROOT>
```

Скрипт архивирует старую `teya-memory/` в `teya-memory-archive/` и создаёт чистую память. Используй `--keep-secrets` только если пользователь явно просит сохранить `site.inv` и `teya.env.local`.

После reset пользователь заполняет:

- `teya-memory/site.inv` — данные бизнеса, дизайна, контента и разрешения
- `teya-memory/teya.env.local` — приватные доступы к WP/хостингу/SMTP/аналитике, если нужен деплой

1. Директор сбрасывает `teya-memory/01-handoff.md`
2. Brief → `teya-memory/00-brief.md`
3. Task(teya-researcher) — глубокий research темы, продукта/личности, оферов, аудитории, конкурентов и фактов → `teya-memory/research/`.
4. Директор проверяет `site-research-dossier.md`, `competitors.csv`, `offers-map.md`, `audience-map.md`, `fact-bank.md`; без research gate не запускает Ядрышко/AURA.
5. **Параллельно:** Task(core) + Task(aura-designer), оба читают research dossier.
6. Директор склеивает fragments → handoff.
7. Директор проверяет research-файлы, `06-url-map.csv`, `07-content-briefs.md`, `11-blog-topics.md`, `AURADESIGN.md`, `AURA_PAGE_PLAN.md`, `AURA_SOURCE_DECOMPOSITION.json`, `AURA_VISUAL_BUDGET.json`, `AURA_SECTION_BLUEPRINTS.json`, `AURA_VISUAL_INVENTORY.json`, `AURA_SECTION_TRANSITIONS.json`, `AURA_STYLE_MATCH_SCORECARD.md`, `AURA_SHAPE_MAP.json`, `AURA_ASSET_REGISTRY.json`, `AURA_VISUAL_DIFF.md`, `AURA_REVIEWER_PASS.md`, `AURA_VISUAL_QA.md`, `AURA_LINT_REPORT.md`.
8. **Excalibur в Phase 1:** сразу после `11-blog-topics.md`, research/fact-bank и `AURA_BLOG_COVER_CONCEPT.*` Директор запускает Task(`excalibur`). Только Excalibur пишет финальные blog articles, `article.html`, longread excerpts, BlogPosting/FAQ schema, covers и publish handoff. Aurora/Aurora Team не пишут статьи вместо него.
9. Task(aurora-team-lead) — раскладывает структуру сайта по research + semantic-core + AURA: страницы, обязательный blog slot, меню, футер, SEO/GEO, schema, linking, no-visible-top-breadcrumbs policy, source decomposition, per-page visual budget, per-page section blueprints, visual inventory requirements, required assets, section transitions.
10. **Параллельно:** Task(aurora-team-content) + Task(aurora-team-navigation) + Task(aurora-team-schema) + Task(aurora-team-indexing) + Task(aurora-team-local-entity) + Task(aurora-team-performance-a11y) + Task(aurora-team-conversion) + Task(aurora-team-security-release) + Task(aurora-team-asset-packager) + Task(aurora-team-motion) mode `MOTION PLAN`. Teya default motion contract: GSAP + meaningful Three.js/WebGL/canvas wow-scene, unless user explicitly forbids 3D or performance/a11y map blocks it.
11. Директор проверяет `page-content-pack.md`, `navigation-linking-map.md`, `schema-technical-seo-map.md`, `indexing-crawl-map.md`, `local-entity-map.md`, `performance-accessibility-map.md`, `conversion-tracking-map.md`, `security-release-map.md`, `asset-packaging-report.md`, `animation-motion-map.md`, theme `media-map.json` и реальные files в `theme/<theme-slug>/assets/images/`. Реальный raster asset = file exists + byte signature matches extension + Pillow `verify()`/`load()` OK + `decode_verified: true`; `.png` URL/content-type от MCP не является доказательством PNG. Если content pack тонкий, без готовых текстов/block inventory или с placeholders — дозапускает Content. Если asset packager дал blocker, нет fragment, нет файлов или есть binary/decode mismatch — не запускает Aurora Page Builder. Если motion map missing/blocker — дозапускает Motion.
12. **Artifact readiness gate:** Task(aurora-team-artifact-auditor) проверяет все входы перед Aurora Page Builder и пишет `artifact-readiness-report.md`. Если `BLOCKED`, дозапускается только недостающий агент. До `READY` нельзя писать `AURORA (WP + DEPLOY) — in progress`.
13. **Aurora split build, не один жирный контекст:** Директор запускает Aurora последовательно в малых режимах:
   - `AURORA THEME BASE` — каркас темы, tokens, header/footer, layout components, legal/cookie/menu contracts.
   - `AURORA PAGE BUILDER` — только после `theme-base-report.md` + `asset-packaging-report.md` с binary/decode verification + `animation-motion-map.md` + `artifact-readiness-report.md READY` + theme `media-map.json` + реальных local assets. Главная + до 4 внутренних страниц по AURA/Aurora Team artifacts. Homepage blog slot использует Excalibur `article.meta.json`/covers при PASS; если Excalibur deferred, разрешены только topic cards из `11-blog-topics.md` без article body, fake excerpt, `article.html` или “готовится/placeholder”.
14. **Motion implementation отдельно от Aurora:** Task(aurora-team-motion) mode `MOTION IMPLEMENT` после Page Builder и до deploy/media внедряет GSAP/Three.js/CSS animations в тему и пишет `animation-implementation-report.md`. Если `threejs_scene_status: not_used` без явного запрета/блокера — это `MOTION THREEJS BLOCKER`. Если dynamic imports из `main.js` не существуют локально или не отдаются 200 на live после deploy — это `MOTION DEPLOY BLOCKER`. Если любой `MOTION BLOCKER` — не деплоить.
15. **Asset transport + deploy/media отдельно от Aurora:** Task(aurora-team-wp-deploy-media) является единым владельцем remote MCP/CDN → verified local files → server upload → WP Media. Перед FTP/SFTP он запускает `python teya/scripts/asset_transport.py --project-root <PROJECT_ROOT> --theme-slug <theme-slug>` и пишет `asset-transport-report.md`; затем делает deploy, WP Media import, `wp-media-map.json`, `deploy-log.md`.
   - Если transport дал `ASSET_TRANSPORT_BLOCKER`, не деплоить, не активировать тему и не запускать live QA.
   - FTP path обязан быть нормализован относительно FTP root: если `/` уже содержит `wp-content`, грузить в `/wp-content/themes/<theme-slug>`, не в `/avrora/public_html/wp-content/...`.
   - После FTP upload обязательно проверить, что `style.css` и `functions.php` лежат в normalized theme path. Иначе `FTP PATH BLOCKER`.
   - Production `PUBLIC_SITE_URL` обязан быть HTTPS.
   - После bootstrap WordPress `home` и `siteurl` обязаны совпадать с HTTPS canonical URL.
   - Если `home_url('/')` возвращает `http://`, это `❌ HTTPS CANONICAL BLOCKER`; не писать пользователю “домен не прилинкован” без доказанного Beget stub.
   - Live-check обязан писать raw evidence: HTTP/HTTPS status, final URL, body length/title, theme CSS status, `/wp-json/` status.
   - Пустой body, 404 theme CSS или недоступный `/wp-json/` = `PUBLIC URL DOES NOT SERVE DEPLOYED WP/THEME`, не “домен не прилинкован”.
16. **Reports отдельно от Aurora:** Task(aurora-team-report-compiler) собирает `site-spec.json`, `build-report.json`, `content-completeness-report.md` только из split reports/evidence.
17. **Paint evidence отдельно:** Task(aurora-team-paint-evidence) собирает browser screenshots/network/computed styles в `paint-qa/`, включая animation evidence: `main.js`, dynamic motion chunks, GSAP/Three.js bundles, console errors/warnings, reduced-motion branch.
18. **Hard Release Gate — readiness базового сайта:**
   - Task(aurora-team-release-gate) запускает `python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>` и пишет `release-gate-report.md`.
   - Если gate вернул ненулевой код, статус фазы: `❌ RELEASE BLOCKER`; вывод сохранить в `teya-memory/wp/release-gate-report.md`; не запускать Design Guardian, QA и не писать пользователю “готово”.
19. **AURORA BLOG INTEGRATOR — Phase 1, только если Excalibur PASS:** если Excalibur создал готовые `article.html`, `article.meta.json`, `article-qa.md PASS`, covers и schema, отдельный Task(`aurora`) mode `AURORA BLOG INTEGRATOR` встраивает статьи в homepage blog block, `/blog/`, `single.php`, WP posts/covers/schema. После blog integration обязательно повторить deploy/media → report compiler → paint evidence → release gate для enriched-сайта. Если Blog Integrator падает, записать `BLOG INTEGRATION BLOCKER/DEFERRED` и не поручать статьи Aurora.
20. Если Excalibur Phase 1 не успел или упал, записать `EXCALIBUR PHASE1 DEFERRED` в `teya-memory/blog/excalibur-run-log.md` и handoff; базовый QA можно продолжить только без чужих article bodies.
21. Task(aurora-team-design-guardian) — строгий дизайн-gate. Использует готовый `paint-evidence.json`, сам evidence не собирает. Запускать только если нет content blocker и hard release gate прошёл.
22. Если дизайн не `✅ DESIGN OK` — вернуть только нужный Aurora split-mode/asset/motion/deploy agent на исправление, максимум 2 цикла.
23. Task(aurora-team-qa) — SEO/GEO/WP/live/research/fact-bank/design-identity/data-flow-fields/per-page paint-evidence/screenshot files/browser subresources/no unstyled paint/local assets/WP media import + alt/report identity/visual-inventory/animation reduced-motion проверка только после no content blocker + design OK + paint evidence pass + `teya_release_gate.py` code 0. Excalibur deferred не блокирует QA базового сайта, но должен быть явно указан в финальном handoff.

Что можно запускать синхронно/параллельно:
- После Team Lead: content, navigation, schema, indexing, local entity, performance/a11y, conversion, security/release, asset-packager, motion plan.
- После этих карт: artifact-auditor строго один.
- `AURORA THEME BASE` можно запускать параллельно с `aurora-team-asset-packager`, если оба получают только read-only artifacts и не пишут один и тот же файл.
- Page Builder строго после Theme Base + Asset Packager + Artifact Auditor.
- Motion Implement строго после Page Builder.
- WP Deploy/Media строго после Motion Implement.
- Report Compiler строго после Deploy/Media.
- Paint Evidence строго после live/deploy базового сайта.
- Release Gate строго после reports + paint evidence.
- Excalibur запускается в Phase 1 сразу после Core + AURA; статьи блога не пишет никто кроме него.
- Blog Integrator в Phase 1 только если Excalibur PASS; после него повторить deploy/report/paint/release для enriched-сайта.

**Передай:** контакты, референс дизайна, нишу/контент. Для деплоя заполни `teya-memory/teya.env.local`.

Если Task(`core`) недоступен, используй Task(`yadryshko`) как alias.
