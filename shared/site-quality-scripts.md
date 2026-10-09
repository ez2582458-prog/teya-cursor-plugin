# Site quality scripts and limits (single source of truth)

Этот файл — единый источник правил «проверено скриптом, а не словами». Агенты ссылаются сюда, а не переписывают лимиты у себя.
Все скрипты лежат в `teya/scripts/`. Они работают одинаково на живом сайте (`https://…`), на локальном WordPress (`http://127.0.0.1:8080/`) и на статической копии (`file://…` или папка с `index.html`).

Требования окружения: `python3 -m pip install playwright pillow` и `python3 -m playwright install --with-deps chromium` (в облаке — см. `docs/cloud-agents-setup.md`).
Если Playwright нет — скрипт выходит с кодом `2` («не могу проверить»). Это **не** PASS.

## Скрипты

| Скрипт | Что делает | Выход (по умолчанию `teya-memory/wp/qa/`) |
| --- | --- | --- |
| `teya_visual_lint.py --url URL` | Открывает каждую страницу в Chromium на 1440 / 768 / 375 px, **прокручивает до низа** (запускаются scroll-анимации), делает полностраничные скриншоты, проверяет вычисленные стили; отдельно открывает страницы **без JS** | `visual-lint.json/.md`, `visual-lint-screens/*.png` |
| `teya_content_lint.py --url URL [--paths THEME]` | Видимый текст, alt, title, meta description: служебная разметка («Секция:», «H2:», «answer-block», «(40–60 слов)», `{{…}}`, TODO/lorem, «в разработке»), markdown (`**`, `[текст](ссылка)`, `# `), латиница в русском тексте, «битый» текст в SVG | `content-lint.json/.md` |
| `teya_page_weight.py --url URL [--lighthouse]` | Холодная загрузка каждой страницы: вес, CSS, каждая картинка; формат, `loading="lazy"`, `width/height` | `page-weight.json/.md` |
| `teya_site_fact_check.py --url URL [--paths THEME]` | Все фактические утверждения сайта (годы, «с 20XX», «более N лет», N объектов, %, цены, гарантии, лицензии/СРО, рейтинги; текст + alt + SVG + JSON-LD) сверяет с `00-brief.md`, `site.inv`, `research/fact-bank.md` | `site-fact-check.json/.md` |
| `teya_image_optimize.py --theme DIR [--fix]` | Проверка/исправление картинок темы: WebP, размеры, бюджеты, варианты для `srcset`; `--fix` переписывает ссылки в php/css/js/json и `media-map.json` | `image-optimize.json/.md` |
| `teya_favicon.py --theme DIR …` | Генерирует набор фавиконов и подключает в тему; `--check [--url]` проверяет | `assets/favicon/*`, `inc/favicon.php` |
| `teya_release_gate.py` | Запускает **всё перечисленное само**, сканирует отчёты, считает вердикт | `teya-memory/wp/release-gate-report.md` |

## Лимиты (FAIL, если нарушено)

**Вёрстка и текст** (`teya_visual_lint.py`):
- нет горизонтального скролла (`horizontal_overflow`) ни на одной ширине;
- основной текст ≥ **16 px** (`body_font_small`, `content_font_small` — абзацы/списки/таблицы в `main`); любой текст ≥ 12 px (`text_too_small`);
- заголовки: **без переноса внутри слова** (`heading_word_split`) и **с полями от края экрана** ≥ 8 px (`heading_edge`); H1 не перекрыт другими элементами (`h1_overlap`);
- после прокрутки весь контент видим (`hidden_content` — opacity 0 / visibility hidden после анимаций); подменю закрыты (`submenu_open`); картинки загрузились (`broken_image`);
- без JS контент тоже видим (`hidden_without_js`): анимации не имеют права прятать контент, если JS не выполнился (начальное скрытие — только под классом, который ставит JS, например `.js .reveal`);
- нет пустых полос в высоту экрана (`empty_band`).

**Вес** (`teya_page_weight.py`):
- главная ≤ **1,5 MB**, внутренняя ≤ **1 MB** (холодная загрузка, все запросы);
- CSS ≤ **60 KB** на страницу;
- любая картинка ≤ **300 KB**; PNG/JPEG > 30 KB = ошибка (`image_not_webp`);
- `<img>` ниже первого экрана — `loading="lazy"`; у каждой `<img>` есть `width` и `height`;
- Lighthouse Performance ≥ 70 (если запускали с `--lighthouse`).

**Картинки** (`teya_image_optimize.py`, `package_mcp_assets.py`, `asset_transport.py`):
- формат **WebP** (PNG — только фавиконы и картинки с `keep_png: true`, например пиксельный логотип);
- hero/LCP: длинная сторона ≤ 1600 px, ≤ **250 KB**; остальные: ≤ 1200 px, ≤ **150 KB**; карточки/миниатюры ≤ 800 px; жёсткий потолок 300 KB;
- для картинок шире 800 px есть варианты `-480w/-800w/-1200w.webp`, в разметке `srcset` + `sizes` + `width/height` + `loading="lazy"` (hero: `fetchpriority="high"`, без lazy). Готовый PHP-хелпер: `teya/shared/snippets/teya-responsive-image.php` (`teya_img()`); для картинок из медиатеки — `wp_get_attachment_image()`.

**Тексты** (`teya_content_lint.py`): ни одной служебной пометки, markdown или английского слова в русском тексте (кроме брендов и общепринятых слов из allowlist; свои — `teya-memory/content-allowlist.txt`).

**Факты** (`teya_site_fact_check.py`):
- каждое утверждение должно подтверждаться брифом / site.inv / fact-bank (раздел «не подтверждено» в fact-bank не считается);
- `no_claims` (0 утверждений найдено) — это **не** PASS проверки фактов, в отчётах так и писать: «0 фактов проверено»;
- год основания, «с 20XX», «N лет опыта», число объектов, лицензии/СРО **без источника — убрать**, а не «смягчить».

**Фавикон** (`teya_favicon.py`, шаг обязателен): `favicon.ico` (16/32/48), `favicon.svg`, `favicon-32x32.png`, `apple-touch-icon.png` (180), `android-chrome-192x192.png`, `android-chrome-512x512.png`, `site.webmanifest` в `assets/favicon/` темы + `inc/favicon.php`, подключённый в `functions.php` (или Site Icon через `site_icon`). На странице есть `<link rel="icon">` (200 OK) и `apple-touch-icon`. Нет фавикона — release gate FAIL.

```bash
# из логотипа (SVG/PNG) или из инициалов и фирменного цвета
python3 teya/scripts/teya_favicon.py --theme teya-memory/wp/theme/<slug> --initials "ЭС" --color "#B3261E" --name "Эксперт Сервис" --wire
python3 teya/scripts/teya_favicon.py --theme teya-memory/wp/theme/<slug> --logo assets/images/logo-mark.svg --color "#B3261E" --name "…" --wire
```

## Release gate

```bash
# локальный WordPress / превью (обязательно перед Design Guardian)
python3 teya/scripts/teya_release_gate.py --project-root . --local-url http://127.0.0.1:8080/
# живой сайт
python3 teya/scripts/teya_release_gate.py --project-root .
# финальный выпуск: + свежие ✅ DESIGN OK и ✅ QA OK с текущим theme_hash
python3 teya/scripts/teya_release_gate.py --project-root . --final
# хэш темы, который guardian/QA пишут в свои отчёты строкой `theme_hash: <hash>`
python3 teya/scripts/teya_release_gate.py --project-root . --theme-hash
```

Правила gate:
- вердикт считается **только** из проверок самого gate и запущенных им скриптов; свой старый `release-gate-report.md` он не читает; `verdict: pass` из paint-evidence или «DESIGN OK» в тексте — не доказательство;
- `--no-live` без `--local-url` = FAIL (нет сайта — нет проверки — нет PASS);
- любой отчёт агента со строкой статуса ❌ / `BLOCKER` / `FAIL` или с противоречием («✅ OK» и «❌ BLOCKER» в одном отчёте) = FAIL. Отчёты со старым `theme_hash` считаются устаревшими (предупреждение) и не годятся как OK;
- `--final`: `design-integrity-report.md` с `✅ DESIGN OK`, `seo-geo-verification.md` с `✅ QA OK`, оба с текущим `theme_hash`, в отчёте guardian есть описания скриншотов.
- `release-gate-report.md` пишет только скрипт. Агентам запрещено редактировать его, чужие вердикты и `paint-evidence.json`.

## После любого исправления

Исправил тему → перезапусти скрипты, которые это проверяют (или весь gate) → новый `theme_hash` → guardian/QA перепроверяют и пишут отчёт заново. Старый OK после правок недействителен.
