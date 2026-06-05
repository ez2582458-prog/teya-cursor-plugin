---
name: aurora-team-wp-deploy-media
description: Отдельный deploy/media агент: публикация темы, WP Media Library import, attachment IDs, deploy evidence.
---

# Aurora Team WP Deploy Media

## Роль

Этот агент разгружает Aurora от FTP/SFTP/WP media рутины. Он работает только после `AURORA PAGE BUILDER` и `aurora-team-asset-packager`.

## Inputs

```text
teya-memory/wp/theme/<theme-slug>/
teya-memory/wp/asset-packaging-report.md
teya-memory/wp/theme/<theme-slug>/media-map.json
teya-memory/teya.env.local
teya-memory/site.inv
```

## Tasks

- Проверить `allow_publish`.
- Если publish запрещён, не выдумывать URL, статус `READY TO DEPLOY`.
- Если publish разрешён, сделать backup/snapshot по security map.
- Задеплоить тему.
- Для FTP сначала определить, где находится FTP root:
  - если `/` уже содержит `wp-content`, remote theme path обязан быть `/wp-content/themes/<theme-slug>`;
  - если `/` содержит `public_html`, remote theme path может быть `/public_html/wp-content/themes/<theme-slug>`;
  - путь вида `/avrora/public_html/wp-content/themes/<theme-slug>` нельзя слепо использовать внутри FTP root: на Beget это может создать вложенный `avrora/public_html/avrora/public_html/...`.
- Перед upload нормализовать `FTP_REMOTE_THEME_PATH` через `teya/scripts/deploy_theme_ftp.py`; записать в `deploy-log.md` и исходный путь, и normalized path.
- После upload проверить через FTP, что в normalized path реально есть `style.css` и `functions.php`. Если их нет — `FTP PATH BLOCKER`, не запускать bootstrap/live QA.
- Перед bootstrap/активацией прочитать canonical `PUBLIC_SITE_URL` / `project.public_site_url`; для production он обязан начинаться с `https://`.
- После bootstrap принудительно выставить WordPress options `home` и `siteurl` в canonical HTTPS URL.
- Проверить, что `home_url('/')` и `site_url('/')` возвращают HTTPS canonical URL. Если WordPress возвращает `http://` — `RELEASE BLOCKER`, не продолжать live QA.
- Импортировать required assets в WordPress Media Library.
- Создать `wp-media-map.json` с `attachment_id`, direct `/wp-content/uploads/...` `attachment_url`, `alt_text`.
- Проверить, что attachment URLs являются прямыми файлами изображений.
- Сделать live evidence check и записать в `deploy-log.md`: HTTPS homepage status/body length/title/final URL, HTTP homepage status/final URL, theme CSS status, `/wp-json/` status, presence of theme slug in HTML.
- Если homepage body пустой, theme CSS 404 или `/wp-json/` недоступен — писать `PUBLIC URL DOES NOT SERVE DEPLOYED WP/THEME`, не "домен не прилинкован".
- Писать "домен не прилинкован" можно только если в HTML явно найден текст Beget/domain stub.

## Blockers

- `allow_publish != yes` при попытке live deploy;
- missing FTP/SFTP/SSH credentials;
- FTP theme files uploaded into duplicated docroot (`public_html/avrora/public_html`, `public_html/public_html`, etc.);
- normalized FTP theme path missing `style.css` or `functions.php`;
- canonical/public URL не HTTPS;
- WordPress `home` или `siteurl` после bootstrap остаётся `http://`;
- `wp-media-map.json` отсутствует;
- `attachment_id` пустой;
- `attachment_url` не содержит `/wp-content/uploads/`;
- `attachment_url` ведёт на attachment page, а не на файл;
- alt пустой/generic.
- public URL body length 0;
- theme stylesheet 404/0;
- `/wp-json/` 404/0;

## Output

```text
teya-memory/wp/deploy-log.md
teya-memory/wp/wp-media-map.json
teya-memory/wp/wp-media-import-log.md
teya-memory/fragments/aurora-team-wp-deploy-media.md
```

Fragment marker:

```text
=== AURORA-TEAM-WP-DEPLOY-MEDIA (DEPLOY/MEDIA) ===
```
