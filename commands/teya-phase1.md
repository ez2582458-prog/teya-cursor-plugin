---
description: Teya фаза 1 — Research, затем ручные ключи + URL-карта + AURA, Aurora Team, Aurora, Design Guardian и QA.
---

# Teya — фаза 1

Перед первым запуском нового сайта Директор обязан очистить память старого проекта:

```bash
python teya/scripts/reset_teya_memory.py --project-root <PROJECT_ROOT>
```

Скрипт архивирует старую `teya-memory/` в `teya-memory-archive/` и создаёт чистую память. Используй `--keep-secrets` только если пользователь явно просит сохранить `site.inv` и `teya.env.local`.

После reset:

- Директор / сайтостроитель **сам** заполняет `teya-memory/site.inv` из данных брифа в чате (пользователь файл руками не правит).
- `teya-memory/teya.env.local` — приватные доступы к WP/хостингу/SMTP/аналитике, если нужен деплой (можно принять из чата и записать в файл).

1. Директор сбрасывает `teya-memory/01-handoff.md`
2. Brief → `teya-memory/00-brief.md` + бот заполняет `site.inv` из чата
3. Task(teya-researcher) — глубокий research темы, продукта/личности, оферов, аудитории, конкурентов и фактов → `teya-memory/research/`.
4. Директор проверяет `site-research-dossier.md`, `competitors.csv`, `offers-map.md`, `audience-map.md`, `fact-bank.md`; без research gate не запускает keywords/URL map и AURA.
5. **Keywords + URL map (без Ядрышко):** Директор (skill `manual-keywords-url-map`) принимает ручной список ключей от пользователя/сайтостроителя **или** выбирает ключи из brief/research и пишет `teya-memory/semantic-core/manual/` (`04-keywords-clean.csv`, `06-url-map.csv`, `07-content-briefs.md`, `11-blog-topics.md`) + fragment `keywords-url-map.md`. **Не** вызывать `Task(core)` / `Task(yadryshko)`, **не** Wordstat, **не** MCP-KV для ключей.
6. **Параллельно или сразу после keywords:** Task(aura-designer) — читает research dossier (не зависит от Wordstat).
7. Директор склеивает fragments → handoff.
8. Директор проверяет research-файлы, `06-url-map.csv`, `07-content-briefs.md`, `11-blog-topics.md`, `AURADESIGN.md`, `AURA_PAGE_PLAN.md`, `AURA_SOURCE_DECOMPOSITION.json`, `AURA_VISUAL_BUDGET.json`, `AURA_SECTION_BLUEPRINTS.json`, `AURA_VISUAL_INVENTORY.json`, `AURA_SECTION_TRANSITIONS.json`, `AURA_STYLE_MATCH_SCORECARD.md`, `AURA_SHAPE_MAP.json`, `AURA_ASSET_REGISTRY.json`, `AURA_VISUAL_DIFF.md`, `AURA_REVIEWER_PASS.md`, `AURA_VISUAL_QA.md`, `AURA_LINT_REPORT.md`.
9. **Excalibur в Phase 1:** сразу после `11-blog-topics.md`, research/fact-bank и `AURA_BLOG_COVER_CONCEPT.*` Директор запускает Task(`excalibur`). Только Excalibur пишет финальные blog articles, `article.html`, longread excerpts, BlogPosting/FAQ schema, covers и publish handoff. Aurora/Aurora Team не пишут статьи вместо него.
10. Task(aurora-team-lead) — раскладывает структуру сайта по research + **manual keywords/URL map** + AURA: страницы, обязательный blog slot, меню, футер, SEO/GEO, schema, linking, no-visible-top-breadcrumbs policy, source decomposition, per-page visual budget, per-page section blueprints, visual inventory requirements, required assets, section transitions.
11. **Параллельно:** Task(aurora-team-content) + Task(aurora-team-navigation) + Task(aurora-team-schema) + Task(aurora-team-indexing) + Task(aurora-team-local-entity) + Task(aurora-team-performance-a11y) + Task(aurora-team-conversion) + Task(aurora-team-security-release) + Task(aurora-team-asset-packager) + Task(aurora-team-motion) mode `MOTION PLAN`. Teya default motion contract: GSAP/CSS motion по AURA; Three.js/WebGL/canvas — только где оправдано (brief/дизайн явно просит 3D/wow-сцену, есть смысловая сцена и бюджет performance/a11y). Для типового сайта услуг Three.js не обязателен; `threejs_scene_status: not_used` с причиной — нормальный статус.
12. Директор проверяет `page-content-pack.md`, `navigation-linking-map.md`, `schema-technical-seo-map.md`, `indexing-crawl-map.md`, `local-entity-map.md`, `performance-accessibility-map.md`, `conversion-tracking-map.md`, `security-release-map.md`, `asset-packaging-report.md`, `animation-motion-map.md`, theme `media-map.json` и реальные files в `theme/<theme-slug>/assets/images/`. Реальный raster asset = file exists + byte signature matches extension + Pillow `verify()`/`load()` OK + `decode_verified: true`; `.png` URL/content-type от MCP не является доказательством PNG. Если content pack тонкий, без готовых текстов/block inventory или с placeholders — дозапускает Content. Если asset packager дал blocker, нет fragment, нет файлов или есть binary/decode mismatch — не запускает Aurora Page Builder. Если motion map missing/blocker — дозапускает Motion.
13. **Artifact readiness gate:** Task(aurora-team-artifact-auditor) проверяет все входы перед Aurora Page Builder и пишет `artifact-readiness-report.md`. Если `BLOCKED`, дозапускается только недостающий агент. До `READY` нельзя писать `AURORA (WP + DEPLOY) — in progress`.
14. **Aurora split build, не один жирный контекст:** Директор запускает Aurora последовательно в малых режимах:
   - `AURORA THEME BASE` — каркас темы, tokens, header/footer, layout components, legal/cookie/menu contracts и **обязательный фавикон** (`teya_favicon.py … --wire`: favicon.ico, favicon.svg, 32/180/192/512 PNG, site.webmanifest из логотипа или инициалов + фирменного цвета; подключение в теме или через `site_icon`).
   - `AURORA PAGE BUILDER` — только после `theme-base-report.md` + `asset-packaging-report.md` с binary/decode verification + `animation-motion-map.md` + `artifact-readiness-report.md READY` + theme `media-map.json` + реальных local assets. Главная + все внутренние из брифа / `06-url-map.csv` (N из брифа = N; без потолка «главная+4»). Homepage blog slot использует Excalibur `article.meta.json`/covers при PASS; если Excalibur deferred, разрешены только topic cards из `11-blog-topics.md` без article body, fake excerpt, `article.html` или “готовится/placeholder”.
15. **Motion implementation отдельно от Aurora:** Task(aurora-team-motion) mode `MOTION IMPLEMENT` после Page Builder и до deploy/media внедряет GSAP/Three.js/CSS animations в тему и пишет `animation-implementation-report.md`. `MOTION THREEJS BLOCKER` — только если brief/motion map требует Three.js, а сцены нет; `threejs_scene_status: not_used` с причиной — не блокер. Если dynamic imports из `main.js` не существуют локально или не отдаются 200 на live после deploy — это `MOTION DEPLOY BLOCKER`. Если любой `MOTION BLOCKER` — не деплоить.
16. **Asset transport + deploy/media отдельно от Aurora:** Task(aurora-team-wp-deploy-media) является единым владельцем remote MCP/CDN → verified local files → server upload → WP Media. Перед FTP/SFTP он запускает `python teya/scripts/asset_transport.py --project-root <PROJECT_ROOT> --theme-slug <theme-slug>` и пишет `asset-transport-report.md`; затем делает deploy, WP Media import, `wp-media-map.json`, `deploy-log.md`.
   - Если transport дал `ASSET_TRANSPORT_BLOCKER`, не деплоить, не активировать тему и не запускать live QA.
   - FTP path обязан быть нормализован относительно FTP root: если `/` уже содержит `wp-content`, грузить в `/wp-content/themes/<theme-slug>`, не в `/avrora/public_html/wp-content/...`.
   - После FTP upload обязательно проверить, что `style.css` и `functions.php` лежат в normalized theme path. Иначе `FTP PATH BLOCKER`.
   - Production `PUBLIC_SITE_URL` обязан быть HTTPS.
   - После bootstrap WordPress `home` и `siteurl` обязаны совпадать с HTTPS canonical URL.
   - Если `home_url('/')` возвращает `http://`, это `❌ HTTPS CANONICAL BLOCKER`; не писать пользователю “домен не прилинкован” без доказанного Beget stub.
   - Live-check обязан писать raw evidence: HTTP/HTTPS status, final URL, body length/title, theme CSS status, `/wp-json/` status.
   - Пустой body, 404 theme CSS или недоступный `/wp-json/` = `PUBLIC URL DOES NOT SERVE DEPLOYED WP/THEME`, не “домен не прилинкован”.
17. **Reports отдельно от Aurora:** Task(aurora-team-report-compiler) собирает `site-spec.json`, `build-report.json`, `content-completeness-report.md` только из split reports/evidence.
18. **Paint evidence отдельно:** Task(aurora-team-paint-evidence) собирает browser screenshots/network/computed styles в `paint-qa/`, включая animation evidence: `main.js`, dynamic motion chunks, GSAP/Three.js bundles, console errors/warnings, reduced-motion branch.
19. **Hard Release Gate — readiness базового сайта:**
   - Task(aurora-team-release-gate) запускает `python3 teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>` (live) или `--local-url http://127.0.0.1:8080/` (локальный WordPress); gate сам запускает `teya_visual_lint.py`, `teya_content_lint.py`, `teya_page_weight.py`, `teya_site_fact_check.py`, `teya_image_optimize.py --check`, проверку фавикона и сам пишет `release-gate-report.md`. `--no-live` без `--local-url` = FAIL.
   - Если gate вернул ненулевой код, статус фазы: `❌ RELEASE BLOCKER`; вывод сохранить в `teya-memory/wp/release-gate-report.md`; не запускать Design Guardian, QA и не писать пользователю “готово”.
20. **AURORA BLOG INTEGRATOR — Phase 1, только если Excalibur PASS:** если Excalibur создал готовые `article.html`, `article.meta.json`, `article-qa.md PASS`, covers и schema, отдельный Task(`aurora`) mode `AURORA BLOG INTEGRATOR` встраивает статьи в homepage blog block, `/blog/`, `single.php`, WP posts/covers/schema. После blog integration обязательно повторить deploy/media → report compiler → paint evidence → release gate для enriched-сайта. Если Blog Integrator падает, записать `BLOG INTEGRATION BLOCKER/DEFERRED` и не поручать статьи Aurora.
21. Если Excalibur Phase 1 не успел или упал, записать `EXCALIBUR PHASE1 DEFERRED` в `teya-memory/blog/excalibur-run-log.md` и handoff; базовый QA можно продолжить только без чужих article bodies.
22. Task(aurora-team-design-guardian) — строгий дизайн-gate. Использует готовый `paint-evidence.json`, сам evidence не собирает. Запускать только если нет content blocker и hard release gate прошёл.
23. Если дизайн не `✅ DESIGN OK` — вернуть только нужный Aurora split-mode/asset/motion/deploy agent на исправление, максимум 2 цикла. После каждого исправления — заново gate и Design Guardian (новый `theme_hash`).
24. Task(aurora-team-qa) — SEO/GEO/WP/live/research/fact-bank/design-identity/data-flow-fields/per-page paint-evidence/screenshot files/browser subresources/no unstyled paint/local assets/WP media import + alt/report identity/visual-inventory/animation reduced-motion проверка только после no content blocker + design OK + paint evidence pass + `teya_release_gate.py` code 0. Excalibur deferred не блокирует QA базового сайта, но должен быть явно указан в финальном handoff.

Что можно запускать синхронно/параллельно:
- Keywords/URL map и AURA — AURA может идти параллельно с записью manual keywords, если research gate уже пройден.
- После Team Lead: content, navigation, schema, indexing, local entity, performance/a11y, conversion, security/release, asset-packager, motion plan.
- После этих карт: artifact-auditor строго один.
- `AURORA THEME BASE` можно запускать параллельно с `aurora-team-asset-packager`, если оба получают только read-only artifacts и не пишут один и тот же файл.
- Page Builder строго после Theme Base + Asset Packager + Artifact Auditor.
- Motion Implement строго после Page Builder.
- WP Deploy/Media строго после Motion Implement.
- Report Compiler строго после Deploy/Media.
- Paint Evidence строго после live/deploy базового сайта.
- Release Gate строго после reports + paint evidence.
- Excalibur запускается в Phase 1 сразу после keywords/URL map + AURA; статьи блога не пишет никто кроме него.
- Blog Integrator в Phase 1 только если Excalibur PASS; после него повторить deploy/report/paint/release для enriched-сайта.

**Передай:** контакты, референс дизайна, нишу/контент — в чат; бот сам заполнит `site.inv`. Для деплоя заполни `teya-memory/teya.env.local` (можно через чат).

**Запрещено:** запускать Ядрышко (`core` / `yadryshko`), Wordstat или MCP-KV для расширения ключей. См. `rules/manual-keywords.mdc`.

**Правила честной проверки (обязательны, источник лимитов — `teya/shared/site-quality-scripts.md`):**

1. **Чужие вердикты не трогать.** Директор и любой агент не редактируют и не «уточняют» `design-integrity-report.md`, `seo-geo-verification.md`, `paint-qa/paint-evidence.json`, `release-gate-report.md` и fragments других агентов. Не согласен — перезапусти того агента с конкретным fix pack.
2. **Не подменять paint-evidence и release gate.** Директор не пишет `paint-evidence.json` и не составляет вывод gate руками. `release-gate-report.md` пишет только `teya_release_gate.py`; вердикт gate считается из его собственных проверок и скриптов, а не из текстов агентов.
3. **QA — только после `✅ DESIGN OK`**, выданного Design Guardian для текущего `theme_hash` (`python3 teya/scripts/teya_release_gate.py --project-root . --theme-hash`). Нет OK или хэш старый — QA не запускать.
4. **После любого исправления — повторная проверка.** Правка темы меняет `theme_hash`: заново gate (`--local-url` или live), заново Design Guardian, потом QA. Старые OK после правок недействительны.
5. **Design Guardian описывает каждый скриншот**: страница, ширина, что видно сверху вниз и что не так. Скриншот без описания не считается просмотренным; «скриншоты сделаны» ≠ «дизайн проверен».
6. **Анимации не прячут контент без JS.** Начальное скрытие (opacity 0, translate) — только под классом, который ставит JS (`.js .reveal`), плюс `prefers-reduced-motion`. `teya_visual_lint.py` проверяет страницу без JS (`hidden_without_js`).
7. **Стоковые/внешние фото** (если политика проекта их вообще разрешает) — только после того, как агент открыл картинку, посмотрел и описал, что на ней, и проверил, что это про услугу клиента. Непросмотренная картинка на сайт не идёт.
8. **Тексты без служебной разметки**: никаких «Секция:», «H2:», «answer-block», «(40–60 слов)», `**`, `[текст](ссылка)`, TODO, «в разработке» и английских слов в русском тексте (`teya_content_lint.py`).
9. **Основной текст ≥ 16 px**, мелкий служебный ≥ 12 px.
10. **Заголовки без переноса внутри слова и с полями от края экрана** на 375/768/1440 (`heading_word_split`, `heading_edge`).
11. **Факты по всему сайту** сверяются с брифом и fact-bank (`teya_site_fact_check.py`): годы, «с 20XX», «N лет», число объектов, лицензии/СРО. 0 найденных фактов — не PASS проверки фактов, а «0 фактов проверено».
12. **Картинки** — WebP, hero ≤ 250 KB, остальные ≤ 150 KB, `srcset` + `width/height` + `loading="lazy"` (кроме hero). **Фавикон обязателен** (`teya_favicon.py`), без него gate = FAIL.

