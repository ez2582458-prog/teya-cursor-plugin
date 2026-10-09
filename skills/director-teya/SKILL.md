---
name: director-teya
description: "Директор Teya — фаза 1: Research → manual keywords/URL map || AURA → Aurora Team Lead → 8 parallel Aurora Team agents → Aurora → Design Guardian → QA."
---

# Директор Teya — фаза 1

Протокол памяти: `shared/memory-protocol.md`
Карта передачи данных: `shared/agent-data-flow-contract.md`

## Стек сайта

По умолчанию **любой сайт делается на WordPress** (своя тема, контент/меню/контакты редактируются в админке, SEO и JSON-LD в теме без платных плагинов, форма через `wp_mail`, zip-пакет в структуре корня сайта + опциональный mu-plugin автонастройки, проверка на локальном WordPress перед сдачей). Статичный HTML — только если пользователь прямо попросил. Полный контракт: `rules/wordpress-by-default.mdc`.

## Один шаблон для внутренних страниц

По умолчанию главная — уникальная, а все типовые внутренние страницы (услуги, гео, FAQ, цены, портфолио, о нас) — **один общий шаблон** `inner-shared` с переменными content-блоками; 40 похожих страниц = 40 контент-вариантов, не 40 дизайнов. Уникальный макет — только главная/лендинг или по прямой просьбе пользователя (`unique_template_reason`). В WordPress шаблон делается один раз (`page-inner.php` + block patterns), контент страниц редактируется в админке через `the_content`. Передавай это в задачи AURA, Aurora Team Lead, Content и Aurora. Полный контракт: `rules/shared-inner-page-template.mdc`, `shared/shared-inner-page-template.md`.

## AUTO-BRIEF (решение пользователя)

Когда пользователь просит бриф / новый сайт — команда `/teya-brief`: выдай пустой `shared/site-brief-template.md`, дождись заполнения, перенеси в `00-brief.md` + `site.inv` + manual keywords/URL map.

- **Число и список страниц** — только из заполненного брифа. Если бриф задаёт N страниц — строй N; **старый потолок «max 5» снят для брифа**. Если бриф молчит — спроси, не дефолть 5.
- **Число статей блога** — из брифа; не раздувай.
- **Ключи** — из брифа / чата; без Ядрышко/Wordstat; slug можно слегка нормализовать.
- Не выдумывай страницы, статьи и ключи сверх брифа.

## Цепочка

```text
/teya-brief (empty template → filled brief) → 00-brief.md + bot fills site.inv → teya-researcher → research gate → [manual keywords/URL map from brief ║ aura-designer] → merge → aurora-team-lead → [content ║ navigation ║ schema ║ indexing ║ local-entity ║ performance-a11y ║ conversion ║ security-release] → content gate → aurora (N pages from brief) → content-completeness gate → aurora-team-design-guardian → aurora-team-qa → URL
```

## Параллель (безопасно)

| Пара | Почему |
|------|--------|
| **manual keywords/URL map || AURA** | Ключи вручную или выбор Директора; AURA независима; общий brief + research |
| **aurora-team-content \|\| aurora-team-navigation \|\| aurora-team-schema \|\| aurora-team-indexing \|\| aurora-team-local-entity \|\| aurora-team-performance-a11y \|\| aurora-team-conversion \|\| aurora-team-security-release** | Все читают blueprint и готовят разные WP-артефакты |

Пишут в **разные** fragments. Директор склеивает.

Aurora Team Lead и Aurora не запускают вложенные subagents. Все Task запускает только Директор.

## Алгоритм

См. `agents/director.md` — полный пошаговый контракт.

Перед Aurora и финальным QA обязательно применяй:

- `teya/shared/quality-anti-haltura.md`;
- `teya/shared/visual-assets-mcp-policy.md`;
- `teya/shared/reference-visual-fidelity-gate.md`;
- `teya/shared/visual-paint-qa-gate.md`;
- `teya/shared/design-source-decomposition-gate.md`;
- `teya/shared/agent-data-flow-contract.md`.

Запрещено продолжать pipeline, если:

- `teya-memory/research/site-research-dossier.md`, `competitors.csv`, `offers-map.md`, `audience-map.md` или `fact-bank.md` отсутствуют;
- `page-content-pack.md` не содержит готовых текстов, block inventory и минимумов;
- `content-completeness-report.md` отсутствует или содержит `❌ CONTENT BLOCKER`;
- публичный HTML содержит placeholders или фейковые отзывы;
- sitemap/robots/canonical используют неправильный домен;
- нет `/blog/`, homepage blog section или `single.php`;
- нет “Политика конфиденциальности”, “Политика cookies” или cookie banner с кнопкой принятия;
- есть visible top breadcrumbs, перекрывающие menu/hero/CTA;
- MCP-required visual assets отсутствуют, заменены заглушками или не записаны в `AURA_ASSET_REGISTRY.json`;
- cutout/overlap assets используют raw MCP `url` вместо `packaged_url`/`transparent_url`, или `requires_background_removal: true` без `recraft_remove_background`;
- после deploy images не импортированы в WordPress Media Library, `wp-media-map.json` отсутствует или `attachment_id` пуст;
- public HTML содержит MCP/tempfile/remote image URLs вместо `/wp-content/uploads/`;
- meaningful images без осмысленного `alt_text` в registry, WP attachment meta или HTML;
- `AURA_VISUAL_INVENTORY.json` отсутствует или required visual zones не реализованы;
- `AURA_SOURCE_DECOMPOSITION.json`, `AURA_VISUAL_BUDGET.json`, `AURA_SECTION_BLUEPRINTS.json` или `AURA_STYLE_MATCH_SCORECARD.md` отсутствуют при сильном visual reference;
- source имеет несколько image-bearing зон, а тема оставила только один hero image;
- source decomposition, visual budget или section blueprints проигнорированы;
- плотный visual reference превращён в generic/mostly-white/text-heavy layout;
- `meaningful_image_count` меньше `minimum_homepage_visual_assets` / `minimum_meaningful_image_assets_homepage`;
- per-page `meaningful_image_count` меньше per-page `minimum_meaningful_image_assets`;
- внутренняя selected/build page выглядит как generic/default text template;
- `site-spec.json`, `build-report.json` или `content-completeness-report.md` не содержат visual data fields из `agent-data-flow-contract.md`;
- `paint-qa/paint-evidence.json`, `paint-qa-report.md` или screenshots 1440/375 по главной и каждой selected/build page отсутствуют при наличии public URL;
- `paint-evidence.json` ссылается на screenshot path, которого нет на диске;
- browser network после fresh navigation/cache-bust не содержит theme CSS/JS/images или live screenshot выглядит как unstyled/default HTML;
- required visual asset отсутствует локально в `teya-memory/wp/theme/<theme-slug>/`;
- screenshot/computed style evidence противоречит `design-integrity-report.md`;
- QA/design отчёты относятся к другому `theme_slug`, проекту или public URL;
- нестандартные шейпы/переходы секций из AURA/source заменены generic прямыми блоками;
- Design Guardian не дал `✅ DESIGN OK`.

Перед первым запуском используй `/teya-brief` (или `/teya-start`): выдай шаблон брифа, прими заполненный бриф в чате и сам заполни `site.inv` (не жди ручного редактирования файла).

Обязательные файлы (бот пишет сам из чата):

- `teya-memory/site.inv` — данные бизнеса, дизайна, контента и разрешения. **Пользователь не правит файл руками** — Директор заполняет из заполненного брифа в чате (`/teya-brief`, `rules/manual-keywords.mdc`). Поля `pages_count` / `pages_list` / `blog_articles_count` — из брифа.
- `teya-memory/teya.env.local` — приватные доступы к WordPress, FTP/SFTP/SSH, SMTP, аналитике и webhook. Не коммитить.

## Правила честной проверки (обязательны, источник лимитов — `teya/shared/site-quality-scripts.md`)

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

## Skills

- `teya-researcher` — обязательный pre-start research перед keywords/URL map и `aura-designer`.
- `manual-keywords-url-map` — вместо Ядрышко: ручные ключи + URL-карта без Wordstat/MCP-KV.
- `aura-designer` — обязательно для `aura-designer`.
- `yadryshko-semantic-core` / `core` / `yadryshko` — **сняты с пайплайна**; не вызывать.
- `aura-shape-replication`, `aura-cyrillic-google-fonts` — вспомогательные skills AURA для дизайн-референсов, шейпов, переходов секций и кириллицы.
- `aurora` и `wp-theme-builder` — для WP-интеграции.
- `aurora-team-design-guardian` — обязательный дизайн-gate после Aurora и до финального QA.
- `excalibur`, `excalibur-research`, `excalibur-geo-qa` — Phase 1 статьи блога; `excalibur-wp-publish` — Phase 1 publish step после deploy context.

## Маркеры

- `=== BRIEF (ВХОД) ===`
- `=== TEYA-RESEARCHER (ГЛУБОКИЙ РЕСЁРЧ) ===`
- `=== KEYWORDS + URL MAP (MANUAL) ===`
- `=== AURA (ДИЗАЙН) ===`
- `=== AURORA-TEAM-LEAD (СТРУКТУРА) ===`
- `=== AURORA-TEAM-CONTENT (SEO/GEO ТЕКСТЫ) ===`
- `=== AURORA-TEAM-NAVIGATION (МЕНЮ И ПЕРЕЛИНКОВКА) ===`
- `=== AURORA-TEAM-SCHEMA (TECH SEO/GEO) ===`
- `=== AURORA-TEAM-INDEXING (CRAWL/INDEX) ===`
- `=== AURORA-TEAM-LOCAL-ENTITY (БИЗНЕС-СУЩНОСТЬ) ===`
- `=== AURORA-TEAM-PERFORMANCE-A11Y (CWV/A11Y) ===`
- `=== AURORA-TEAM-CONVERSION (ФОРМЫ И ЦЕЛИ) ===`
- `=== AURORA-TEAM-SECURITY-RELEASE (БЕЗОПАСНЫЙ РЕЛИЗ) ===`
- `=== AURORA (WP-ТЕМА И СТРАНИЦЫ) ===`
- `=== AURORA-TEAM-DESIGN-GUARDIAN (ДИЗАЙН-КОНТРОЛЬ) ===`
- `=== AURORA-TEAM-QA (ПРОВЕРКА) ===`
- `=== EXCALIBUR (SEO/GEO СТАТЬИ БЛОГА) ===`
