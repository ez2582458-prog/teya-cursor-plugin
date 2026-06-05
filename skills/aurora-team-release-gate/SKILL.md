---
name: aurora-team-release-gate
description: Запускает машинный release gate, сохраняет stdout/stderr и финальный PASS/BLOCKER.
---

# Aurora Team Release Gate

## Роль

Финальная машинная проверка перед Design Guardian/QA. Этот агент не доверяет markdown/json self-report.

## Command

```text
python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>
```

Для local-only build без public URL:

```text
python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT> --no-live
```

## Rules

- Exit code 0 = `PASS`.
- Non-zero exit = `RELEASE BLOCKER`.
- Сохрани полный вывод команды.
- Не исправляй ошибки сам; верни их Директору для нужного split-mode/agent.
- Запускать до Design Guardian/QA. Если gate failed, Design Guardian может делать только local/design fix-pack, но не `DESIGN OK`.
- Gate обязан падать при отсутствии split reports, пустом live body, HTTP canonical, 404 theme CSS, missing paint evidence, pending WP Media import, missing background removal evidence.
- Не используй `--no-live` для production `PUBLIC_SITE_URL=https://...`, кроме явного user/developer request.

## Output

```text
teya-memory/wp/release-gate-report.md
teya-memory/fragments/aurora-team-release-gate.md
```

Fragment marker:

```text
=== AURORA-TEAM-RELEASE-GATE (MACHINE GATE) ===
```
