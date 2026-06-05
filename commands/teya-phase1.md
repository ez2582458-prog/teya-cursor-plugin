---
description: Teya фаза 1 — Research, затем Ядрышko + AURA, Aurora Team, Aurora, Design Guardian и QA.
---

# Teya — фаза 1

Перед первым запуском пользователь заполняет:

- `teya-memory/site.inv` — данные бизнеса, дизайна, контента и разрешения
- `teya-memory/teya.env.local` — приватные доступы к WP/хостингу/SMTP/аналитике, если нужен деплой

1. Директор сбрасывает `teya-memory/01-handoff.md`
2. Brief → `teya-memory/00-brief.md`
3. Task(teya-researcher) — глубокий research темы, продукта/личности, оферов, аудитории, конкурентов и фактов → `teya-memory/research/`.
4. Директор проверяет `site-research-dossier.md`, `competitors.csv`, `offers-map.md`, `audience-map.md`, `fact-bank.md`; без research gate не запускает Ядрышко/AURA.
5. **Параллельно:** Task(core) + Task(aura-designer), оба читают research dossier.
6. Директор склеивает fragments → handoff.
7. Директор проверяет research-файлы, `06-url-map.csv`, `07-content-briefs.md`, `11-blog-topics.md`, `AURADESIGN.md`, `AURA_PAGE_PLAN.md`, `AURA_SOURCE_DECOMPOSITION.json`, `AURA_VISUAL_BUDGET.json`, `AURA_SECTION_BLUEPRINTS.json`, `AURA_VISUAL_INVENTORY.json`, `AURA_SECTION_TRANSITIONS.json`, `AURA_STYLE_MATCH_SCORECARD.md`, `AURA_SHAPE_MAP.json`, `AURA_ASSET_REGISTRY.json`, `AURA_VISUAL_DIFF.md`, `AURA_REVIEWER_PASS.md`, `AURA_VISUAL_QA.md`, `AURA_LINT_REPORT.md`.
8. **Blog slot planning, без Excalibur:** AURA фиксирует только cover system/concept, а Aurora Team Lead планирует `/blog/`, homepage blog slot и `single.php` по темам из `11-blog-topics.md`. Excalibur на этом этапе не запускается.
9. Task(aurora-team-lead) — раскладывает структуру сайта по research + semantic-core + AURA: страницы, обязательный blog slot, меню, футер, SEO/GEO, schema, linking, no-visible-top-breadcrumbs policy, source decomposition, per-page visual budget, per-page section blueprints, visual inventory requirements, required assets, section transitions.
10. **Параллельно:** Task(aurora-team-content) + Task(aurora-team-navigation) + Task(aurora-team-schema) + Task(aurora-team-indexing) + Task(aurora-team-local-entity) + Task(aurora-team-performance-a11y) + Task(aurora-team-conversion) + Task(aurora-team-security-release) + Task(aurora-team-asset-packager).
11. Директор проверяет `page-content-pack.md`, `navigation-linking-map.md`, `schema-technical-seo-map.md`, `indexing-crawl-map.md`, `local-entity-map.md`, `performance-accessibility-map.md`, `conversion-tracking-map.md`, `security-release-map.md`, `asset-packaging-report.md`, theme `media-map.json` и реальные files в `theme/<theme-slug>/assets/images/`. Если content pack тонкий, без готовых текстов/block inventory или с placeholders — дозапускает Content. Если asset packager дал blocker, нет fragment или нет файлов — не запускает Aurora Page Builder.
12. **Artifact readiness gate:** Task(aurora-team-artifact-auditor) проверяет все входы перед Aurora Page Builder и пишет `artifact-readiness-report.md`. Если `BLOCKED`, дозапускается только недостающий агент. До `READY` нельзя писать `AURORA (WP + DEPLOY) — in progress`.
13. **Aurora split build, не один жирный контекст:** Директор запускает Aurora последовательно в малых режимах:
   - `AURORA THEME BASE` — каркас темы, tokens, header/footer, layout components, legal/cookie/menu contracts.
   - `AURORA PAGE BUILDER` — только после `theme-base-report.md` + `asset-packaging-report.md` + `artifact-readiness-report.md READY` + theme `media-map.json` + реальных local assets. Главная + до 4 внутренних страниц по AURA/Aurora Team artifacts, без финальных статей Excalibur; homepage blog slot использует только темы/карточки-заготовки без “готовится/placeholder”.
14. **Deploy/media отдельно от Aurora:** Task(aurora-team-wp-deploy-media) делает deploy, WP Media import, `wp-media-map.json`, `deploy-log.md`.
   - FTP path обязан быть нормализован относительно FTP root: если `/` уже содержит `wp-content`, грузить в `/wp-content/themes/<theme-slug>`, не в `/avrora/public_html/wp-content/...`.
   - После FTP upload обязательно проверить, что `style.css` и `functions.php` лежат в normalized theme path. Иначе `FTP PATH BLOCKER`.
   - Production `PUBLIC_SITE_URL` обязан быть HTTPS.
   - После bootstrap WordPress `home` и `siteurl` обязаны совпадать с HTTPS canonical URL.
   - Если `home_url('/')` возвращает `http://`, это `❌ HTTPS CANONICAL BLOCKER`; не писать пользователю “домен не прилинкован” без доказанного Beget stub.
   - Live-check обязан писать raw evidence: HTTP/HTTPS status, final URL, body length/title, theme CSS status, `/wp-json/` status.
   - Пустой body, 404 theme CSS или недоступный `/wp-json/` = `PUBLIC URL DOES NOT SERVE DEPLOYED WP/THEME`, не “домен не прилинкован”.
15. **Reports отдельно от Aurora:** Task(aurora-team-report-compiler) собирает `site-spec.json`, `build-report.json`, `content-completeness-report.md` только из split reports/evidence.
16. **Excalibur после готовой базовой сборки сайта:** только после Aurora base/deploy-media без content blocker запускается Task(`excalibur`) для реальных статей и blog covers под готовый сайт/визуальную систему. Excalibur отвечает за наполнение blog block и статьи, а не за раннюю сборку до сайта.
17. **AURORA BLOG INTEGRATOR:** после Excalibur отдельный Task(`aurora`) в режиме blog integration встраивает реальные статьи в homepage blog block, `/blog/`, `single.php`, WP posts/covers/schema. Не трогает базовый дизайн/семантику без необходимости.
18. **Paint evidence отдельно:** Task(aurora-team-paint-evidence) собирает browser screenshots/network/computed styles в `paint-qa/`.
19. **Hard Release Gate перед любым SUCCESS:**
   - Task(aurora-team-release-gate) запускает `python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>` и пишет `release-gate-report.md`.
   - Если gate вернул ненулевой код, статус фазы: `❌ RELEASE BLOCKER`; вывод сохранить в `teya-memory/wp/release-gate-report.md`; не запускать Excalibur publish, Design Guardian, QA и не писать пользователю “готово”.
20. Task(aurora-team-design-guardian) — строгий дизайн-gate. Использует готовый `paint-evidence.json`, сам evidence не собирает. Запускать только если нет content blocker и hard release gate прошёл.
21. Если дизайн не `✅ DESIGN OK` — вернуть только нужный Aurora split-mode/asset/deploy agent на исправление, максимум 2 цикла.
22. Task(aurora-team-qa) — SEO/GEO/WP/live/research/fact-bank/design-identity/data-flow-fields/per-page paint-evidence/screenshot files/browser subresources/no unstyled paint/local assets/WP media import + alt/report identity/visual-inventory проверка только после no content blocker + design OK + paint evidence pass + `teya_release_gate.py` code 0.

Что можно запускать синхронно/параллельно:
- После Team Lead: content, navigation, schema, indexing, local entity, performance/a11y, conversion, security/release, asset-packager.
- После этих карт: artifact-auditor строго один.
- `AURORA THEME BASE` можно запускать параллельно с `aurora-team-asset-packager`, если оба получают только read-only artifacts и не пишут один и тот же файл.
- Page Builder строго после Theme Base + Asset Packager + Artifact Auditor.
- WP Deploy/Media строго после Page Builder.
- Report Compiler строго после Deploy/Media.
- Excalibur строго после базового сайта/blog slot.
- Blog Integrator строго после Excalibur.
- Paint Evidence строго после live/deploy/blog integration.
- Release Gate строго после reports + paint evidence.

**Передай:** контакты, референс дизайна, нишу/контент. Для деплоя заполни `teya-memory/teya.env.local`.

Если Task(`core`) недоступен, используй Task(`yadryshko`) как alias.
