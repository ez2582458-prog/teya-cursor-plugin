---
name: aurora-team-paint-evidence
description: Собирает browser paint evidence: screenshots 1440/375, network CSS/JS/images, broken assets, computed styles.
---

# Aurora Team Paint Evidence

## Роль

Этот агент разгружает Design Guardian и QA от сбора evidence. Он не оценивает красоту, он фиксирует факты браузера.

## Tasks

- Открыть public URL с cache-bust.
- Проверить HTTPS и отсутствие Beget/domain stub.
- Записать raw live evidence: HTTP status, HTTPS status, final URL, body length, `<title>`, theme CSS status, `/wp-json/` status, theme slug present in HTML.
- Снять screenshots 1440/375 для home и каждой selected/build page.
- Собрать network evidence: theme CSS, theme JS, images, fonts, 4xx/5xx.
- Если `main.js` содержит dynamic imports (`import('./motion/...')`), проверить каждый imported chunk: URL должен быть в network или HTTP probe со статусом 200. Missing `motion-home.js`/`motion-lite.js` = blocker.
- Для motion evidence проверить console warnings/errors; `motion-home unavailable`, failed dynamic import, missing GSAP/Three.js chunk, module 404 = blocker.
- Если `animation-implementation-report.md` заявляет GSAP/Three.js, browser evidence должен подтвердить reachable bundles and no module load errors.
- Проверить broken images и alt text.
- Снять базовые computed styles: body font, H1 font, hero background, CTA color.
- Записать `paint-evidence.json` строго по `visual-paint-qa-gate.md`.

## Blockers

- screenshot отсутствует;
- network не содержит theme CSS/JS/images;
- live page выглядит как Beget stub/unstyled/default HTML;
- any selected page missing;
- broken image/font requests;
- broken JS dynamic imports / missing motion chunks;
- animation report claims GSAP/Three.js but browser evidence does not show reachable bundles;
- public URL mismatch with reports.
- body length `0`;
- theme CSS 404/0;
- `/wp-json/` 404/0;
- HTTP canonical вместо HTTPS.

Не писать пользователю "домен не прилинкован", если нет явного текста Beget/domain stub. Для пустого body/404 assets писать: `public URL does not serve deployed WP/theme files` + raw evidence.

## Output

```text
teya-memory/wp/paint-qa/paint-evidence.json
teya-memory/wp/paint-qa/paint-qa-report.md
teya-memory/wp/paint-qa/home-1440-fullpage.png
teya-memory/wp/paint-qa/home-375-fullpage.png
teya-memory/wp/paint-qa/page-<slug>-1440-fullpage.png
teya-memory/wp/paint-qa/page-<slug>-375-fullpage.png
teya-memory/fragments/aurora-team-paint-evidence.md
```

Fragment marker:

```text
=== AURORA-TEAM-PAINT-EVIDENCE (BROWSER EVIDENCE) ===
```
