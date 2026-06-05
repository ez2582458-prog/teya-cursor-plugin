# Teya Visual Paint QA Gate

Этот gate закрывает провал, когда отчёт пишет `✅ DESIGN OK`, но реальный сайт в браузере выглядит иначе.

## Главный Закон

Design Guardian и финальный QA не имеют права ставить `✅`, если не проверили реальный paint страницы.

DOM, HTML, CSS-файл, `site-spec.json`, `build-report.json` и утверждения Aurora не являются достаточным доказательством. Нужны браузерные evidence.

`paint-evidence.json` со словом `pass` тоже не является доказательством сам по себе. PASS действителен только если все screenshot-файлы реально существуют в `teya-memory/wp/paint-qa/`, browser network показывает загрузку CSS/JS/images, а screenshot/computed styles подтверждают применённый дизайн.

## Обязательные Evidence

Если есть public URL, Design Guardian обязан создать:

```text
teya-memory/wp/paint-qa/
```

И записать туда:

```text
home-1440-fullpage.png
home-375-fullpage.png
page-<slug>-1440-fullpage.png
page-<slug>-375-fullpage.png
paint-evidence.json
paint-qa-report.md
```

Если public URL недоступен, проверяй локальный preview/HTML. Если нет ни live, ни preview — статус не может быть `✅ DESIGN OK`.

## Что Должно Быть В `paint-evidence.json`

```json
{
  "public_site_url": "...",
  "theme_slug": "...",
  "checked_at": "...",
  "screenshots": {
    "home_1440": "teya-memory/wp/paint-qa/home-1440-fullpage.png",
    "home_375": "teya-memory/wp/paint-qa/home-375-fullpage.png",
    "pages": [
      {
        "slug": "/programma/",
        "desktop": "teya-memory/wp/paint-qa/page-programma-1440-fullpage.png",
        "mobile": "teya-memory/wp/paint-qa/page-programma-375-fullpage.png"
      }
    ]
  },
  "computed_styles": {
    "hero_background": "...",
    "primary_cta_background": "...",
    "body_font_family": "...",
    "h1_font_family": "..."
  },
  "asset_counts": {
    "meaningful_image_elements_home": 0,
    "meaningful_image_elements_by_page": {
      "/": 0,
      "/programma/": 0
    },
    "mcp_required_assets_rendered": 0,
    "broken_images": 0
  },
  "css_network": {
    "theme_css_url": "...",
    "theme_css_status": 200,
    "theme_css_contains_required_tokens": true,
    "browser_requested_theme_css": true,
    "browser_requested_theme_js": true,
    "browser_requested_required_images": true,
    "subresource_request_count": 0
  },
  "paint_application": {
    "body_has_theme_class": true,
    "hero_has_expected_class": true,
    "hero_background_matches_aura": true,
    "primary_cta_matches_aura": true,
    "unstyled_html_detected": false
  },
  "verdict": "pass | fail"
}
```

## Paint Blockers

Ставь `❌ DESIGN BLOCKER`, если:

- screenshot показывает не тот визуальный язык, который описан в `AURADESIGN.md`;
- computed style противоречит AURA tokens (например, AURA требует hot pink hero, а реальный hero белый);
- browser network не загрузил theme CSS/JS или CSS не применился;
- browser network после fresh navigation/cache-bust содержит только main document и не содержит theme CSS/JS/images;
- live screenshot выглядит как unstyled HTML: bullet navigation, plain links/buttons, white hero, default spacing, missing AURA background/cards;
- screenshot-файлы, указанные в `paint-evidence.json`, отсутствуют на диске;
- `screenshots.pages` пустой при наличии selected/build pages;
- report утверждает `pink hero`, `yellow CTA`, `trial overlap`, `visual zones live`, но screenshot/computed style этого не подтверждают;
- meaningful image count в screenshot/DOM любой выбранной страницы меньше её budget/minimum из `AURA_VISUAL_BUDGET.json` или `AURA_VISUAL_INVENTORY.json`;
- required image-bearing zones закрыты CSS-card/gradient-placeholder, хотя source требует реальные изображения/3D/иллюстрации;
- внутренняя страница выглядит как generic/default text page при visual reference, где каждая страница должна наследовать визуальный язык;
- screenshots есть только для главной, но build содержит внутренние страницы;
- Design Guardian проверил только локальные файлы при наличии public URL.

## Запрет На Ложный PASS

Фразы вроде `CSS bundle валиден`, `tokens match`, `live DOM verified`, `paint not used as sole source` не могут заменить screenshot evidence.

Если screenshot не создан и не указан в отчёте, Design Guardian обязан поставить:

```text
❌ DESIGN BLOCKER: missing browser paint evidence
```

Финальный QA обязан блокировать публикацию, если `paint-qa-report.md` или screenshot evidence отсутствуют.

Если live browser screenshot показывает unstyled/default HTML, Design Guardian обязан поставить:

```text
❌ DESIGN BLOCKER: live paint is unstyled or theme CSS is not applied
```
