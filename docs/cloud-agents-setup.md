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
- `.cursor/environment.json` (только если его не было): `bash teya/scripts/teya_cloud_setup.sh` — Python-зависимости (paramiko, pillow, playwright), Chromium для Playwright и подготовка `teya-memory/`. Если `environment.json` уже был, скрипт inject печатает, что добавить в его `install`.

Повторный запуск скрипта = обновление Teya в этом репо до текущего форка (rev пишется в `teya/.teya-fork-rev`).
Если тот же репо открыт локально, где ещё стоит плагин — правила будут дублироваться; это не ломает, но лучше держать один источник.

**Секреты** (FTP/SFTP/WP-пароли и т.п.) — только в cursor.com/dashboard → Cloud Agents → **Secrets**, не в репо.

### Длинный промпт от сайтостроителя

Пока путь A не подтверждён, сайтостроитель (бот, который запускает облачных агентов) должен в каждом запуске:

1. Запускать агента на репо сайта, в который уже сделан inject (или первым шагом попросить: «склонируй https://github.com/ez2582458-prog/teya-cursor-plugin в `teya/` и следуй `teya/rules/*.mdc` и `teya/agents/director.md`»).
2. В промпте явно писать: «Работай по пайплайну Teya: начни с `.cursor/rules/teya-orchestrator.mdc` и `/teya-start`. `site.inv` заполняешь сам из данных ниже. Ядрышко/Wordstat не использовать, ключи — по `manual-keywords-url-map`. WordPress по умолчанию.» и прикладывать все данные брифа (домен, компания, ИНН, услуги, ключи, гео, доступы — через Secrets).

## Облачное окружение: WordPress + Playwright (для проверок)

Проверки Teya (`teya_visual_lint.py`, `teya_page_weight.py`, `teya_content_lint.py`, `teya_site_fact_check.py`) и release gate открывают сайт в настоящем браузере. В облаке для этого нужны **Playwright + Chromium**, а чтобы проверить тему **до деплоя** — **локальный WordPress**. Без них gate выходит с ошибкой (код 2 у скриптов = «не могу проверить» = FAIL), а не с PASS.

### 1. `.cursor/environment.json` в репо сайта

```json
{
  "install": "bash teya/scripts/teya_cloud_setup.sh || true"
}
```

`teya_cloud_setup.sh` ставит `paramiko pillow playwright` (с обходом PEP 668), `python3 -m playwright install --with-deps chromium` (если есть sudo; иначе только Chromium) и проверяет, что Chromium запускается.

### 2. Локальный WordPress в облаке (PHP + SQLite, без MySQL и Docker)

Когда тема собрана в `teya-memory/wp/theme/<slug>/`:

```bash
bash teya/scripts/teya_cloud_setup.sh --no-python --wordpress --theme <slug>
```

Что делает (проверено 09.10.2026 на Debian 13, PHP 8.4, тема ek-servis):

1. ставит `php-cli php-sqlite3 php-gd php-mbstring php-xml php-curl php-zip` через apt (нужен sudo — в облачных агентах Cursor он есть);
2. качает WP-CLI и WordPress (ru_RU) в `/tmp/teya-wp/site`, подключает плагин `sqlite-database-integration` как `db.php` (база — файл SQLite, MySQL не нужен);
3. `wp core install` с **одноразовым случайным** паролем администратора (`/tmp/teya-wp/.admin-pass`, в репо не попадает), ЧПУ `/%postname%/`, `home`/`siteurl` = `http://127.0.0.1:8080`;
4. подключает тему симлинком из `teya-memory/wp/theme/<slug>`, копирует `teya-memory/wp/mu-plugins/*.php` (создание страниц/меню), активирует тему;
5. запускает `php -S 127.0.0.1:8080` в фоне (лог `/tmp/teya-wp/server.log`, ошибки PHP — `wp-content/debug.log`, `WP_DEBUG` включён).

Альтернатива, если в окружении есть Docker: образы `wordpress` + `mariadb` (или `wp-env`) — тогда передавай их URL в `--local-url`.

### 3. Проверка и gate против локального сайта

```bash
python3 teya/scripts/teya_visual_lint.py   --url http://127.0.0.1:8080/ --project-root .
python3 teya/scripts/teya_content_lint.py  --url http://127.0.0.1:8080/ --paths teya-memory/wp/theme/<slug> --project-root .
python3 teya/scripts/teya_page_weight.py   --url http://127.0.0.1:8080/ --project-root .
python3 teya/scripts/teya_site_fact_check.py --url http://127.0.0.1:8080/ --paths teya-memory/wp/theme/<slug> --project-root .
python3 teya/scripts/teya_release_gate.py  --project-root . --local-url http://127.0.0.1:8080/
```

Результаты — `teya-memory/wp/qa/*.md|json` и `teya-memory/wp/release-gate-report.md`. Лимиты и смысл проверок — `teya/shared/site-quality-scripts.md`. Статическая копия сайта тоже подходит: `--url /путь/к/папке` (папка с `index.html`) или `file://…`.

После деплоя тот же gate без `--local-url` проверяет живой `PUBLIC_SITE_URL` (HTTPS).

## Ветка `cloud-marketplace`

Содержит `.cursor-plugin/marketplace.json`, который объявляет этот же репозиторий единственным плагином `teya` (`"source": "./"`). Нужна для импорта «From GitHub Repository». Формат с `source: "./"` для корневого плагина **не проверен** — если Cursor его не примет, вариант: перенести плагин в подпапку `plugins/teya/` только в этой ветке.
