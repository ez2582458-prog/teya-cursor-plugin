# Teya WordPress Media Upload Contract

Этот контракт обязателен для Aurora, Design Guardian и QA.

## Главный Закон

Production-сайт **не может** показывать MCP/tempfile/remote image URLs в публичном HTML.

Правильный путь:

1. MCP KV генерирует asset (`gpt-image-2` → `recraft_remove_background` для cutout).
2. Aurora скачивает финальный файл локально в theme package (staging).
3. При деплое Aurora **загружает файл в медиатеку WordPress** (`wp-content/uploads/`).
4. В шаблонах используются **WP attachment** + **осмысленный `alt`**, а не прямой URL.

Theme path (`/wp-content/themes/.../assets/images/...`) допустим только как staging/preview до импорта. На live public HTML для MCP-generated images обязателен WP Media Library URL или `wp_get_attachment_image()`.

## Обязательные Артефакты

После деплоя Aurora создаёт:

```text
teya-memory/wp/wp-media-map.json
teya-memory/wp/wp-media-import-log.md
```

### `wp-media-map.json`

```json
{
  "theme_slug": "teya-kovcheg-kids",
  "public_site_url": "https://example.com/",
  "imported_at": "2026-06-04T00:00:00Z",
  "assets": [
    {
      "registry_id": "hero-mascot-kovcheg",
      "file": "hero-mascot-kovcheg.png",
      "local_source_path": "teya-memory/wp/theme/teya-kovcheg-kids/assets/images/hero-mascot-kovcheg.png",
      "attachment_id": 123,
      "attachment_url": "https://example.com/wp-content/uploads/2026/06/hero-mascot-kovcheg.png",
      "alt_text": "Робот Ковчег — маскот школы вайбкодинга",
      "used_in": ["front-page:hero"]
    }
  ],
  "verdict": "pass | fail"
}
```

## ALT Text

Каждый meaningful image обязан иметь `alt_text`:

- в `AURA_ASSET_REGISTRY.json` — поле `alt_text` (источник истины для theme visuals);
- в `page-content-pack.md` / `visual_alt_requirements` — для page-specific wording;
- в `wp-media-map.json` после импорта;
- в attachment meta `_wp_attachment_image_alt` на WordPress;
- в финальном HTML через `wp_get_attachment_image()` или `<img alt="...">`.

Запрещено:

- пустой `alt=""` для смысловых изображений;
- generic alt вроде `image`, `photo`, `mascot`, `placeholder`;
- alt не на языке страницы без причины.

## Как Импортировать В WordPress

Aurora обязана использовать один из допустимых способов:

### A. Bootstrap PHP на сервере (предпочтительно при FTP-only)

```php
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';
require_once ABSPATH . 'wp-admin/includes/image.php';

$attachment_id = media_handle_sideload($file_array, 0, null, [
    'post_title' => 'hero-mascot-kovcheg',
    'post_content' => '',
    'post_excerpt' => '',
]);
if (!is_wp_error($attachment_id)) {
    update_post_meta($attachment_id, '_wp_attachment_image_alt', $alt_text);
}
```

### B. WP-CLI (если SSH доступен)

```bash
wp media import /path/to/hero-mascot-kovcheg.png --title="hero-mascot-kovcheg" --alt="..." --porcelain
```

### C. WordPress REST API / MCP WordPress tools (если доступны в среде)

Импорт должен создавать real attachment с alt meta.

## Theme Integration

Aurora создаёт helper, например `inc/media.php`:

```php
function teya_get_media_map() {
    static $map = null;
    if ($map === null) {
        $path = get_template_directory() . '/media-map.json';
        $map = file_exists($path) ? json_decode(file_get_contents($path), true) : [];
    }
    return $map['assets'] ?? [];
}

function teya_media_img($registry_id, $attrs = []) {
    foreach (teya_get_media_map() as $item) {
        $item_id = $item['id'] ?? ($item['registry_id'] ?? '');
        if ($item_id !== $registry_id && ($item['registry_id'] ?? '') !== $registry_id) {
            continue;
        }
        $id = (int) ($item['attachment_id'] ?? 0);
        if ($id > 0) {
            $attrs['alt'] = $attrs['alt'] ?? ($item['alt_text'] ?? '');
            return wp_get_attachment_image($id, 'full', false, $attrs);
        }
        if (! empty($item['attachment_url'])) {
            $alt = esc_attr($attrs['alt'] ?? ($item['alt_text'] ?? ''));
            $class = isset($attrs['class']) ? ' class="' . esc_attr($attrs['class']) . '"' : '';
            return '<img src="' . esc_url($item['attachment_url']) . '" alt="' . $alt . '"' . $class . '>';
        }
    }
    return '';
}
```

В шаблонах для production visuals используй `teya_media_img('hero-mascot-kovcheg', [...])`, а не hardcoded theme URI и не remote URL.

`media-map.json` в теме заполняется при деплое из `teya-memory/wp/wp-media-map.json`.

## Blockers

`❌ CONTENT BLOCKER` / `❌ DESIGN BLOCKER`, если:

- public HTML содержит `tempfile.aiquickdraw.com`, MCP URL или другой remote asset URL вместо WP uploads;
- `wp-media-map.json` отсутствует после deploy;
- `media-map.json`/`wp-media-map.json` не содержат одновременно `id` и `registry_id` для каждого asset;
- `attachment_id` отсутствует для required asset;
- `alt_text` пустой или generic для meaningful image;
- attachment alt meta не совпадает с registry/content pack;
- theme template hardcodes external URL;
- deploy оставил images только в `/themes/.../assets/images/` без WP media import на production.

## QA Checks

Design Guardian и QA проверяют:

- live HTML `img[src]` для MCP assets → домен сайта `/wp-content/uploads/`;
- нет remote MCP/tempfile URLs в public HTML;
- каждый meaningful `<img>` имеет непустой осмысленный `alt`;
- `wp-media-map.json` существует и совпадает с текущим theme/project/public URL.
