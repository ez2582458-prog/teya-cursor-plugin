# Teya Design Source Decomposition Gate

Этот gate нужен до сборки темы. Он заставляет AURA разобрать визуальный референс как дизайнер, а не как список цветов.

## Обязательные Артефакты AURA

AURA обязана создать:

```text
teya-memory/design/AURA_SOURCE_DECOMPOSITION.json
teya-memory/design/AURA_VISUAL_BUDGET.json
teya-memory/design/AURA_SECTION_BLUEPRINTS.json
teya-memory/design/AURA_STYLE_MATCH_SCORECARD.md
```

Если есть сильный screenshot/reference, без этих файлов AURA не может дать `✅`.

## `AURA_SOURCE_DECOMPOSITION.json`

Файл описывает источник по слоям:

```json
{
  "reference": "...",
  "overall_vibe": "hot pink 3D gaming kids / playful / dense / toy-like",
  "global_motifs": ["clouds", "planet doodles", "3d mascot", "yellow pills"],
  "sections": [
    {
      "source_section": "hero",
      "target_section": "front-page:hero",
      "background": "hot pink gradient + doodles",
      "layout": "left text, right 3D mascot, dense top navigation",
      "visual_objects": ["3D mascot", "clouds", "planet doodles"],
      "cards_or_panels": [],
      "section_transition": "overlap into white trial card",
      "must_match": ["pink fill", "yellow CTA", "large mascot", "playful display font"],
      "must_not": ["plain white hero", "single text column", "generic SaaS layout"]
    }
  ]
}
```

## `AURA_VISUAL_BUDGET.json`

Файл задаёт минимальную визуальную плотность **для каждой страницы в test build / production build**, а не только для главной:

```json
{
  "pages": [
    {
      "slug": "/",
      "template": "front-page.php",
      "minimum_colored_sections": 2,
      "minimum_meaningful_image_assets": 5,
      "minimum_decorative_motifs": 8,
      "minimum_overlap_compositions": 2,
      "minimum_custom_cards": 6,
      "minimum_non_rectangular_transitions": 2,
      "forbidden_simplifications": [
        "white hero only",
        "one mascot only",
        "plain text cards",
        "generic flat sections"
      ]
    },
    {
      "slug": "/programma/",
      "template": "page-programma.php",
      "minimum_colored_sections": 1,
      "minimum_meaningful_image_assets": 2,
      "minimum_decorative_motifs": 4,
      "minimum_overlap_compositions": 1,
      "minimum_custom_cards": 4,
      "minimum_non_rectangular_transitions": 1,
      "forbidden_simplifications": [
        "default page.php look",
        "text-only longread",
        "plain white content stack"
      ]
    }
  ]
}
```

CSS gradients, cards, blobs and icon dots do not count as meaningful images. They may count as colored sections or decorative motifs only.

Каждая страница, которую Aurora собирает в test build, должна иметь запись в `pages[]`. Если страница не имеет visual budget, она не может быть `production-ready`.

## `AURA_SECTION_BLUEPRINTS.json`

Каждый target section должен иметь implementation checklist:

```json
{
  "sections": [
    {
      "id": "front-page:services",
      "required_background": "white",
      "required_visuals": ["3 unique 3D/object icons"],
      "required_cards": 3,
      "required_motion": "card hover lift",
      "required_transition_in": "white overlap after hero/trial",
      "required_transition_out": "pink block starts with curved/overlap cap",
      "fidelity_blockers": ["text-only cards", "missing object icons"]
    }
  ]
}
```

## `AURA_STYLE_MATCH_SCORECARD.md`

AURA должна поставить ожидаемые баллы до передачи Aurora:

```markdown
# AURA Style Match Scorecard

| Category | Minimum | Planned |
|---|---:|---:|
| Color identity | 90 | ... |
| Visual density | 90 | ... |
| Section composition | 90 | ... |
| Asset fidelity | 90 | ... |
| Typography mood | 85 | ... |
| Motion/transition | 80 | ... |

Status: ✅ READY | ❌ BLOCKER
Blockers:
- ...
```

Если любой ключевой балл ниже minimum, AURA не отдаёт `✅`; она пишет blocker/fix plan.

## Абсолютные Блокеры

Ставь `❌ DESIGN SOURCE BLOCKER`, если:

- reference screenshot dense/playful/visual, а план AURA допускает mostly white/text layout;
- visual budget не задан или заполнен нулями для любой build page при сильном визуальном reference;
- section blueprint отсутствует для любой key section выбранных страниц;
- внутренняя страница получает generic/default text page вместо собственной visual treatment;
- forbidden simplification присутствует в Aurora output или разрешена в AURA;
- `AURA_STYLE_MATCH_SCORECARD.md` пишет pass без чисел и evidence.
