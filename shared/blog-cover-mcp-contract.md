# Teya Blog Cover Contract — AURA + Excalibur + MCP KV

## Кто за что отвечает

| Роль | Задача |
|------|--------|
| **Ядрышко / Core** | `11-blog-topics.md` — темы, queries, H2/H3, FAQ |
| **AURA** | **Фирменный концепт** + per-topic сцены: `AURA_BLOG_COVER_CONCEPT.*`, `AURA_BLOG_COVER_SYSTEM.md`, `AURA_BLOG_COVER_PROMPTS.json` |
| **Excalibur** | Статья + MCP обложка **строго по концепту** (prefix + scene + suffix) |
| **Aurora** (опц.) | WP Media Library для featured image |

Excalibur **не придумывает** стиль и **не меняет** `cover_family`, prefix/suffix, palette lock.

Методология концепта: `teya/shared/blog-cover-brand-concept.md`.  
Реестр slug: `teya/shared/blog-cover-family-registry.json` (**33** типа).

## Обязательные артефакты AURA

```text
teya-memory/design/AURA_BLOG_COVER_CONCEPT.md      # фирменный концепт (human-readable)
teya-memory/design/AURA_BLOG_COVER_CONCEPT.json    # machine lock: family, prefix, suffix, layout
teya-memory/design/AURA_BLOG_COVER_SYSTEM.md       # техника: 16:9, MCP, cutout, QA
teya-memory/design/AURA_BLOG_COVER_PROMPTS.json     # per-topic scene + alt (+ optional full prompt)
teya-memory/design/assets/blog-cover-style-anchor.png   # рекомендуется: эталон серии
```

### `AURA_BLOG_COVER_CONCEPT.md`

- выбранный `cover_family` из реестра `blog-cover-brand-concept.md` (22+ типов: collage, photo, illustration, mixed, mockup, mascot, infographic…) и **почему**;
- `allowed_cover_families_considered[]` — 3 shortlist + отказ от остальных;
- visual lock: палитра, композиция, текстура, формы, свет;
- что **fixed** vs **variable** per topic;
- связь с `AURADESIGN.md`, mascot/assets сайта;
- do/don't (no text in image, no stock slop, no style drift);
- ссылка на style anchor, если сгенерирован.

### `AURA_BLOG_COVER_CONCEPT.json`

```json
{
  "concept_version": "1",
  "cover_family": "brand_collage",
  "cover_family_label_ru": "Фирменный коллаж",
  "allowed_cover_families_considered": ["brand_collage", "mascot_series", "sticker_scrapbook"],
  "cover_family_selection_rationale": "Playful EdTech site with mascot; collage matches hero cards",
  "secondary_cover_families": [],
  "prompt_assembly_mode": "prefix_scene_suffix",
  "global_prompt_prefix": "English, detailed, no text in image...",
  "global_prompt_suffix": "16:9, thumbnail-safe, consistent brand series...",
  "global_negative_prompt": "text, watermark, logo, blurry...",
  "composition_lock": {
    "aspect_ratio": "16:9",
    "target_size": "1200x675",
    "layout_description": "main subject right 55%, brand color band left",
    "thumbnail_safe_zone": "center-right"
  },
  "color_lock": {
    "background": "#FAFAF7",
    "primary_accent": "#B8FF3C",
    "secondary_accent": "#FF3CAC"
  },
  "fixed_elements": ["soft grain", "rounded sticker frames", "same lighting direction"],
  "variable_per_topic": ["hero object", "secondary prop", "topic_archetype mood"],
  "topic_archetypes": {
    "informational": { "scene_bias": "single hero object, calm background" },
    "how_to": { "scene_bias": "tool or hands metaphor" }
  },
  "style_anchor": {
    "status": "ready | skipped | pending",
    "local_path": "teya-memory/design/assets/blog-cover-style-anchor.png",
    "prompt_used": "..."
  }
}
```

### `AURA_BLOG_COVER_PROMPTS.json`

Per topic — **сцена внутри концепта**, не новый стиль:

```json
{
  "topic_id": "B01",
  "slug": "vajbkoding-dlya-detey",
  "topic_archetype": "informational",
  "topic_scene_descriptor": "robot mascot beside laptop, playful learning props, lime blob accent",
  "cover_alt_text": "Робот и ноутбук — вайбкодинг для детей",
  "use_concept_assembly": true,
  "gpt_image_2_prompt": null,
  "assembled_prompt_preview": "optional full string for QA",
  "requires_background_removal": false,
  "status": "prompt_ready"
}
```

**Сборка промпта:**

```text
gpt_image_2_prompt =
  AURA_BLOG_COVER_CONCEPT.json → global_prompt_prefix
  + topic.topic_scene_descriptor
  + global_prompt_suffix
```

Если `gpt_image_2_prompt` уже заполнен AURA — Excalibur использует его, но **обязан** прочитать concept и убедиться, что family/prefix не нарушены.

### `AURA_BLOG_COVER_SYSTEM.md`

Технический слой: MCP tools, cutout rules, 16:9, WP import, grid QA, style-anchor workflow.

## MCP Pipeline

1. Собрать prompt из concept + topic (или взять pre-assembled).
2. `user-mcp-kv` / `gpt-image-2`.
3. `recraft_remove_background` только если `requires_background_removal: true` или family требует cutout collage.
4. Сохранить `teya-memory/blog/articles/<topic_id>-<slug>/cover/cover.png`.
5. `cover-registry.json` + update prompts JSON (`url`, `local_path`, `generated_at`).

## Blockers

- нет `AURA_BLOG_COVER_CONCEPT.md` / `.json` → `❌ COVER CONCEPT BLOCKER`;
- `cover_family` не задан, slug **не из** `blog-cover-family-registry.json`, или per-topic промпт ломает family lock;
- нет `topic_scene_descriptor` / `cover_alt_text`;
- Excalibur freestyle prompt без concept;
- style series QA: 2+ covers выглядят как разные бренды → вернуть AURA.
