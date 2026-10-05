# Teya (этот форк) в Cursor Cloud Agents

Форк: https://github.com/ez2582458-prog/teya-cursor-plugin (публичный, ветка `main`).
Локально на MacBook плагин лежит в `~/.cursor/plugins/local/teya` и работает. Ниже — как получить то же самое в **облачных** агентах (cursor.com/agents, Agents Window → Cloud, Slack, API).

> Статус на 05.10.2026: облачная загрузка форка **как плагина ещё не проверена**. Проверен только отрицательный результат: папка `~/.cursor/plugins/local/teya` (симлинк из `.cursor/environment.json`) в облаке **не загружается** — диагностический облачный прогон от 25.09.2026 показал, что в `~/.cursor/plugins/cache/.cloud-plugin-manifest.json` были только `gmail` и `google-drive`, а skills Teya агенту не выдавались.

## Как облако подхватывает инструкции (по документации Cursor)

| Источник | Работает в Cloud Agent? |
|---|---|
| `~/.cursor/plugins/local/*` (локальные плагины) | **Нет** (проверено 25.09.2026). |
| Плагины из marketplace (официальный / командный / импорт из GitHub) | Ставятся при старте каждого облачного агента через `.cloud-plugin-manifest.json`. Сотрудники Cursor пишут, что плагины с GitHub ставятся; на форуме есть баг-репорт, где skills из team marketplace в облаке не появились. Для нашего форка — **не проверено**. |
| `.cursor/rules/*.mdc`, `AGENTS.md`, `.cursor/skills/`, `.cursor/agents/`, `.cursor/commands/` **в репозитории сайта** | **Да.** Облачный агент клонирует репо и читает их. Именно это Cursor советует как самый надёжный вариант. |
| `~/.cursor/skills/` + «Sync Skills for Cloud Agents» | Да, но только skills (без rules/agents/commands), и они видны только тебе. |
| Team Rules (Dashboard) | Да, но нужен тариф Teams/Enterprise. |

## Путь A — подключить форк как плагин (нужен клик в Cursor)

1. **Если тариф Teams/Enterprise:** cursor.com → Dashboard → **Plugins & MCPs** → Team Marketplaces → **Add Marketplace** → **Import from Repo** → вставить `https://github.com/ez2582458-prog/teya-cursor-plugin` → проверить, что распознан плагин `teya` → Marketplace Settings: доступ — вся команда, плагин `teya` — **Required** (или Default On), включить **Auto Refresh** (нужна GitHub App Cursor на этом репо) → Save.
   Если Import from Repo ругается, что нет marketplace-манифеста: открыть маркетплейс → **Add to Marketplace → Plugin** → вставить URL форка.
2. **Если обычный личный тариф (Pro/Ultra):** Cursor desktop → **Customize** → добавить плагин **From GitHub Repository** → URL форка → Install, scope **user**. Для этого импорта в корне репо нужен `.cursor-plugin/marketplace.json`; он подготовлен в ветке `cloud-marketplace` (см. ниже). Если импорт берёт только ветку `main` — смерджить эту ветку в `main`.
3. Убрать дубликат: после установки из marketplace локальная копия `~/.cursor/plugins/local/teya` не нужна (установка из marketplace и так имеет приоритет).
4. **Проверка (обязательно, пока не сделано):** запустить облачного агента на любом репо с промптом:
   «Только чтение. Выведи `cat ~/.cursor/plugins/cache/.cloud-plugin-manifest.json`, `ls ~/.cursor/plugins/cache`, и перечисли доступные тебе skills и rules. Есть ли `director-teya`, `manual-keywords-url-map`, правило `teya-orchestrator`?»
   Если `teya` есть в manifest и skills видны — путь A работает. Если нет — путь B.

## Путь B — надёжный фоллбэк: Teya внутри каждого репо сайта

Скрипт из форка копирует всё нужное в репозиторий сайта (Origin или GitHub):

```bash
git clone https://github.com/ez2582458-prog/teya-cursor-plugin
cd teya-cursor-plugin
bash scripts/inject_into_site_repo.sh /путь/к/репо-сайта
cd /путь/к/репо-сайта && git add teya .cursor AGENTS.md .gitignore && git commit -m "Inject Teya" && git push
```

Что появится в репо сайта:

- `teya/` — полная копия форка (пути `teya/shared/...`, `teya/scripts/...` из правил начинают резолвиться от корня репо);
- `.cursor/rules/teya-*.mdc` — правила (оркестратор, ручные ключи без Ядрышко/Wordstat, WordPress по умолчанию);
- `.cursor/skills/*`, `.cursor/agents/*`, `.cursor/commands/*` — skills, субагенты, команды `/teya-start`, `/teya-phase1`…;
- блок `Cursor Cloud specific instructions (Teya)` в `AGENTS.md` (между маркерами, повторный запуск обновляет блок);
- `.cursor/environment.json` (только если его не было): `pip install paramiko pillow` + подготовка `teya-memory/`.

Повторный запуск скрипта = обновление Teya в этом репо до текущего форка (rev пишется в `teya/.teya-fork-rev`).
Если тот же репо открыт локально, где ещё стоит плагин — правила будут дублироваться; это не ломает, но лучше держать один источник.

**Секреты** (FTP/SFTP/WP-пароли и т.п.) — только в cursor.com/dashboard → Cloud Agents → **Secrets**, не в репо.

### Длинный промпт от сайтостроителя

Пока путь A не подтверждён, сайтостроитель (бот, который запускает облачных агентов) должен в каждом запуске:

1. Запускать агента на репо сайта, в который уже сделан inject (или первым шагом попросить: «склонируй https://github.com/ez2582458-prog/teya-cursor-plugin в `teya/` и следуй `teya/rules/*.mdc` и `teya/agents/director.md`»).
2. В промпте явно писать: «Работай по пайплайну Teya: начни с `.cursor/rules/teya-orchestrator.mdc` и `/teya-start`. `site.inv` заполняешь сам из данных ниже. Ядрышко/Wordstat не использовать, ключи — по `manual-keywords-url-map`. WordPress по умолчанию.» и прикладывать все данные брифа (домен, компания, ИНН, услуги, ключи, гео, доступы — через Secrets).

## Ветка `cloud-marketplace`

Содержит `.cursor-plugin/marketplace.json`, который объявляет этот же репозиторий единственным плагином `teya` (`"source": "./"`). Нужна для импорта «From GitHub Repository». Формат с `source: "./"` для корневого плагина **не проверен** — если Cursor его не примет, вариант: перенести плагин в подпапку `plugins/teya/` только в этой ветке.
