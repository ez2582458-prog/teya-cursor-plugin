---
name: excalibur-wp-publish
description: Excalibur WP Publish — Phase 1 публикация готовой статьи Excalibur в WordPress (post, featured image, schema meta).
---

# Excalibur WP Publish

## Когда

После `✅ ARTICLE OK` от Excalibur и готового deploy context (`allow_publish=yes` в `site.inv`). Это Phase 1 blog publish step: если WP/deploy доступен, не откладывать в Phase 2b. Publish failure не должен ломать готовность базового сайта, но обязан стать явным `EXCALIBUR PUBLISH DEFERRED/BLOCKER`.

## Контракт

`teya/shared/excalibur-wp-publish-contract.md`

## Preconditions

- `article-qa.md` → PASS
- `link-verify.json` → pass (или fix links)
- `cover/cover.png`, `cover-registry.json` с alt; cover должен быть настоящим декодируемым PNG после byte-signature/Pillow verification
- `teya.env.local` — FTP_*, PUBLIC_SITE_URL

## Шаги

1. Запусти link verify:

```bash
python teya/scripts/excalibur_link_verify.py <article.html> -o link-verify.json --site-base $PUBLIC_SITE_URL
```

2. Dry-run publish:

```bash
python teya/scripts/teya_excalibur_wp_publish.py --article-dir teya-memory/blog/articles/<topic_id>-<slug> --dry-run
```

3. Publish:

```bash
python teya/scripts/teya_excalibur_wp_publish.py --article-dir teya-memory/blog/articles/<topic_id>-<slug>
```

4. Проверь live URL: title, featured image, FAQ visible, schema in page source (если theme wired).

5. Запиши `teya-memory/blog/wp-publish-log.md` + обнови fragment excalibur `Ready for WP publish: yes`.

## Aurora responsibility

Если `_teya_schema_jsonld` ещё не выводится в `single.php` — Aurora добавляет hook при следующем deploy темы.

## Blockers

- `❌ PUBLISH BLOCKER` — QA / links / credentials / allow_publish
- `❌ PUBLISH BLOCKER` — cover без alt, не проходит decode verification или не может быть нормализован в настоящий PNG
