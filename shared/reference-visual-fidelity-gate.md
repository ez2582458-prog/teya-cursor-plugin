# Teya Reference Visual Fidelity Gate

Этот gate нужен, чтобы AURA и Aurora не превращали сильный визуальный референс в текстовый шаблон с одной картинкой.

Работает вместе с `teya/shared/design-source-decomposition-gate.md`: visual inventory считает зоны и assets, а source decomposition/visual budget фиксируют композиционную плотность секций.

## Обязательный Артефакт

AURA обязана создать:

```text
teya-memory/design/AURA_VISUAL_INVENTORY.json
```

Файл описывает все визуальные зоны референса и будущего сайта.

## Что Считать Визуальной Зоной

Фиксируй не только hero:

- hero photo / cutout / product object;
- изображения внутри карточек;
- form-side image / person / object;
- decorative stickers, arrows, labels, badges, callouts;
- section background shapes;
- thumbnails in blog/material cards, if reference cards use images;
- mockups, screenshots, UI panels, case visuals;
- icon systems, if icons are meaningful visual elements;
- repeated motifs that define the visual language.

## Формат

```json
{
  "source_reference": "...",
  "visual_zones": [
    {
      "id": "feature-card-1-image",
      "source_zone": "three pastel cards / card 1",
      "page": "/",
      "section": "features",
      "type": "photo | cutout | thumbnail | illustration | icon | sticker | callout | shape | mockup | form-side-image",
      "source_has_image": true,
      "required_for_fidelity": true,
      "implementation": "mcp-image | mcp-remove-bg | inline-svg | css-shape | existing-confirmed-asset | omitted-with-blocker",
      "asset_registry_id": "feature-card-1-image",
      "status": "ready | not_applicable | blocker",
      "reason": "..."
    }
  ],
  "minimum_ready_assets_for_homepage": 0,
  "minimum_meaningful_image_assets_homepage": 0,
  "asset_instance_count_homepage": 0,
  "pages": [
    {
      "slug": "/",
      "minimum_meaningful_image_assets": 0,
      "asset_instance_count": 0
    },
    {
      "slug": "/programma/",
      "minimum_meaningful_image_assets": 0,
      "asset_instance_count": 0
    }
  ],
  "blockers": []
}
```

## Правило Минимальной Плотности

Если референс содержит несколько фото/визуальных карточек, AURA не может пройти gate с одним hero image.

Для каждой build page:

- если source имеет hero image + 3 image cards + form-side image, минимум: hero image + 3 card visuals + form-side visual или честный `❌ VISUAL FIDELITY BLOCKER`;
- если source имеет image-bearing cards, карточки нельзя превращать в plain text cards без blocker;
- если source имеет form-side person/object, lead form нельзя оставлять только white card без visual side;
- если точные фото нельзя копировать, нужно сгенерировать тематические аналоги через MCP KV или заменить на равноценные inline SVG/mockup visuals, явно отмеченные как `ready`.
- внутренние страницы не могут быть generic text templates: каждая выбранная страница должна наследовать visual motifs, section rhythm, cards, colored bands, illustrations or equivalent visual treatment from AURA.

CSS-компонент, белая карточка, gradient placeholder, цветная плашка, background shape или декоративный blob **не считаются meaningful image asset**. Они могут быть visual zone, но не закрывают минимум изображений.

## Запрет На Схлопывание Зон

Нельзя закрывать несколько разных image-bearing сцен одним asset:

- hero mascot не закрывает mascot/card image в trial card;
- hero mascot не закрывает персонажа в how-it-works section;
- один services strip не закрывает отдельные крупные image cards, если в референсе каждая карточка имеет собственный объект;
- footer/newsletter visual нельзя считать готовым, если это только input/card без персонажа или иллюстрации, а source имеет footer mascot/object.

Для каждой image-bearing зоны в `AURA_VISUAL_INVENTORY.json` укажи:

```json
{
  "source_has_image": true,
  "counts_as_meaningful_image": true,
  "asset_instance_id": "unique-id",
  "can_reuse_asset_id": null,
  "reuse_reason": null
}
```

`can_reuse_asset_id` допустим только когда source действительно повторяет тот же объект без новой композиционной роли. Если роль другая, нужен отдельный asset или `❌ VISUAL FIDELITY BLOCKER`.

## Pending Не Равно Ready

`pending` допустим только для optional/backlog assets, которые не участвуют в текущих build pages.

Если asset нужен для страницы, которая идёт в test build или production, `pending` является blocker.

## Blockers

Ставь `❌ VISUAL FIDELITY BLOCKER`, если:

- `AURA_VISUAL_INVENTORY.json` отсутствует;
- `AURA_VISUAL_BUDGET.json` или `AURA_SECTION_BLUEPRINTS.json` отсутствуют при сильном visual reference;
- в референсе есть image-bearing cards, а в теме карточки только текстовые;
- в референсе есть form-side image, а форма собрана без равноценного visual;
- homepage содержит только один смысловой image asset при source, где visuals распределены по нескольким секциям;
- любая внутренняя build page содержит только текстовые блоки при source/AURA, где visual language должен продолжаться на всех страницах;
- `minimum_homepage_visual_assets` или `minimum_meaningful_image_assets_homepage` больше фактического количества meaningful image assets;
- per-page `minimum_meaningful_image_assets` больше фактического количества meaningful image assets на этой странице;
- несколько image-bearing зон закрыты одним hero asset или одним strip без отдельной композиции;
- required visual zone имеет `status: pending`, `not_applicable` без причины или пустой `asset_registry_id`;
- Design Guardian/QA проверили только наличие hero image, но не visual density по секциям.
