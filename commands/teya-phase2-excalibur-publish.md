---
description: Teya фаза 2b — публикация Excalibur статьи в WordPress.
---

# Teya — фаза 2b (Excalibur WP Publish)

**Prerequisites:** `✅ ARTICLE OK`, `article-qa.md` PASS, `link-verify.json` pass, `cover/cover.png`, `site.inv` + `allow_publish=yes`.

## Шаги

1. Проверь `teya-memory/blog/articles/<topic_id>-<slug>/` — полный комплект артефактов.
2. Link verify (если ещё нет):

```bash
python teya/scripts/excalibur_link_verify.py \
  teya-memory/blog/articles/<dir>/article.html \
  -o teya-memory/blog/articles/<dir>/link-verify.json \
  --site-base $PUBLIC_SITE_URL
```

3. Dry-run:

```bash
python teya/scripts/teya_excalibur_wp_publish.py --article-dir teya-memory/blog/articles/<dir> --dry-run
```

4. **Task(excalibur-wp-publish)** или Aurora — publish + live check.
5. Запиши `teya-memory/blog/wp-publish-log.md`, обнови fragment `Ready for WP publish: yes`.

Контракт: `teya/shared/excalibur-wp-publish-contract.md`  
Skill: `skills/excalibur-wp-publish/SKILL.md`

## Aurora follow-up

Если `single.php` не выводит `_teya_schema_jsonld` — добавить при следующем deploy темы.
