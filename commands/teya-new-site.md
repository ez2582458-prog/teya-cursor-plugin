---
description: Teya new site — очистить память предыдущего сайта и стартовать новую сборку.
---

# Teya — новый сайт

Перед любыми Task для нового сайта обязательно очисти активную память:

```bash
python teya/scripts/reset_teya_memory.py --project-root <PROJECT_ROOT>
```

Правила:

- По умолчанию старый `teya-memory/` архивируется в `teya-memory-archive/teya-memory-<timestamp>/`.
- Активная `teya-memory/` становится чистой.
- Старые `site.inv` и `teya.env.local` не переносятся, чтобы данные прошлого сайта не смешались с новым.
- Если пользователь явно просит сохранить доступы/интейк, используй:

```bash
python teya/scripts/reset_teya_memory.py --project-root <PROJECT_ROOT> --keep-secrets
```

После reset:

1. Проверь `teya-memory/memory-reset.json` → `status: clean`.
2. Запиши новый brief в `teya-memory/00-brief.md`.
3. Попроси пользователя заполнить новый `site.inv` / `teya.env.local`, если нужны публикация, SMTP, аналитика или WordPress.
4. Продолжай по `commands/teya-phase1.md`.

Без fresh `memory-reset.json` не запускай subagents.
