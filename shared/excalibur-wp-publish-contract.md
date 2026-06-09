# Excalibur — WordPress publish contract

Excalibur готовит артефакты локально в Phase 1; публикация в WP — Phase 1 blog publish step после готового deploy context (Aurora Blog Integrator или скрипт). Failure/deferred публикации не блокирует готовность базового сайта, но не может быть скрыта или отложена как “фаза 2b”.

## Prerequisites

- `article.html`, `article.meta.json`, `article-qa.md` (verdict PASS)
- `schema.jsonld`
- `cover/cover.png` + `cover-registry.json` (alt); cover должен быть настоящим PNG после byte-signature/Pillow decode verification
- `link-verify.json` (verdict pass или documented skips)
- `site.inv` / `teya.env.local` — FTP + `PUBLIC_SITE_URL`
- Тема с `/blog/` и `single.php` (Phase 1 Aurora)

## Скрипт

```bash
python teya/scripts/excalibur_link_verify.py \
  teya-memory/blog/articles/B01-slug/article.html \
  -o teya-memory/blog/articles/B01-slug/link-verify.json \
  --site-base https://example.com

python teya/scripts/teya_excalibur_wp_publish.py \
  --article-dir teya-memory/blog/articles/B01-slug
```

`--dry-run` — проверка payload без FTP.

## Что делает publish

1. `wp_insert_post` / `wp_update_post` — title, slug, content, excerpt
2. Featured image из `cover/cover.png` + alt в attachment meta. Перед upload скрипт нормализует WebP/JPEG/GIF под именем `cover.png` в настоящий PNG или ставит publish blocker.
3. Post meta `_teya_schema_jsonld` — JSON-LD для вывода в `single.php` (Aurora)

## Артефакты после publish

```text
teya-memory/blog/articles/<topic_id>-<slug>/wp-publish-result.json
teya-memory/blog/wp-publish-log.md
```

### wp-publish-result.json

```json
{
  "slug": "...",
  "topic_id": "B01",
  "permalink": "https://example.com/blog/.../",
  "verdict": "pass"
}
```

## Schema в теме

Aurora в `single.php` (или `inc/schema.php`):

```php
$schema = get_post_meta(get_the_ID(), '_teya_schema_jsonld', true);
if ($schema) {
    echo '<script type="application/ld+json">' . wp_kses_post($schema) . '</script>';
}
```

## Blockers

- `❌ PUBLISH BLOCKER` — QA не PASS, link-verify fail, нет credentials
- `❌ PUBLISH BLOCKER` — cover без alt
- `❌ PUBLISH BLOCKER` — cover missing/corrupt, не декодируется Pillow или не может быть нормализован в PNG
- Production HTML не должен содержать MCP URLs — только WP media для featured image

## Skill

`skills/excalibur-wp-publish/SKILL.md`
