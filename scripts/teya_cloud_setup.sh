#!/usr/bin/env bash
# Teya cloud/local environment setup.
#
#   bash teya/scripts/teya_cloud_setup.sh                 # python deps + Playwright Chromium
#   bash teya/scripts/teya_cloud_setup.sh --wordpress     # + local WordPress on http://127.0.0.1:8080/ (PHP + SQLite, no MySQL)
#   bash teya/scripts/teya_cloud_setup.sh --wordpress --theme <slug>   # + link teya-memory/wp/theme/<slug>, mu-plugins, activate
#   --no-python   skip pip/Playwright (already installed)
#
# Env: TEYA_WP_DIR (default /tmp/teya-wp), TEYA_WP_PORT (default 8080), TEYA_PROJECT_ROOT (default $PWD).
# The local WordPress is a throwaway test site: random admin password stored in $TEYA_WP_DIR/.admin-pass (never commit it).
set -uo pipefail

WITH_WP=0
WITH_PY=1
THEME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --wordpress) WITH_WP=1 ;;
    --theme) THEME="${2:-}"; shift ;;
    --no-python) WITH_PY=0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

ROOT="${TEYA_PROJECT_ROOT:-$PWD}"
WP_DIR="${TEYA_WP_DIR:-/tmp/teya-wp}"
PORT="${TEYA_WP_PORT:-8080}"
SUDO=""
if [[ $EUID -ne 0 ]] && command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then SUDO="sudo -n"; fi

pip_install() {
  python3 -m pip install --user --no-cache-dir "$@" 2>/dev/null \
    || python3 -m pip install --user --no-cache-dir --break-system-packages "$@" \
    || python3 -m pip install --no-cache-dir "$@"
}

if [[ $WITH_PY -eq 1 ]]; then
echo "== python deps (paramiko, pillow, playwright)"
pip_install paramiko pillow playwright || echo "WARN: pip install failed"

echo "== Playwright Chromium"
if [[ -n "$SUDO" || $EUID -eq 0 ]]; then
  python3 -m playwright install --with-deps chromium || python3 -m playwright install chromium || echo "WARN: playwright chromium install failed"
else
  python3 -m playwright install chromium || echo "WARN: playwright chromium install failed (no sudo for system deps)"
fi
python3 - <<'PY' || echo "WARN: Chromium does not start — teya_visual_lint / release gate will exit 2 (FAIL)"
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); b.close()
print("chromium OK")
PY
fi

[[ -f "$ROOT/teya/scripts/prepare_teya_memory.py" ]] && python3 "$ROOT/teya/scripts/prepare_teya_memory.py" --project-root "$ROOT" >/dev/null 2>&1 || true

[[ $WITH_WP -eq 1 ]] || exit 0

echo "== local WordPress (PHP + SQLite) in $WP_DIR on :$PORT"
if ! command -v php >/dev/null 2>&1 || ! php -m 2>/dev/null | grep -qi pdo_sqlite; then
  if [[ -n "$SUDO" || $EUID -eq 0 ]]; then
    $SUDO apt-get update -qq && $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
      php-cli php-sqlite3 php-gd php-mbstring php-xml php-curl php-zip php-intl unzip curl >/dev/null
  else
    echo "ERROR: php + pdo_sqlite missing and no sudo to install them" >&2; exit 1
  fi
fi
WP="$WP_DIR/wp-cli.phar"
mkdir -p "$WP_DIR"
[[ -f "$WP" ]] || curl -fsSL -o "$WP" https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
wp() { php "$WP" --path="$WP_DIR/site" --allow-root "$@"; }

if [[ ! -f "$WP_DIR/site/wp-config.php" ]]; then
  mkdir -p "$WP_DIR/site"
  wp core download --locale=ru_RU --quiet || wp core download --quiet
  curl -fsSL -o "$WP_DIR/sqlite.zip" https://downloads.wordpress.org/plugin/sqlite-database-integration.latest-stable.zip
  unzip -q -o "$WP_DIR/sqlite.zip" -d "$WP_DIR/site/wp-content/plugins/"
  PLUG="$WP_DIR/site/wp-content/plugins/sqlite-database-integration"
  sed -e "s#{SQLITE_IMPLEMENTATION_FOLDER_PATH}#$PLUG#" -e "s#{SQLITE_PLUGIN}#sqlite-database-integration/load.php#" \
    "$PLUG/db.copy" > "$WP_DIR/site/wp-content/db.php"
  wp config create --dbname=wp --dbuser=wp --dbpass=wp --skip-check --quiet
  wp config set WP_DEBUG true --raw --quiet
  wp config set WP_DEBUG_LOG true --raw --quiet
  wp config set WP_DEBUG_DISPLAY false --raw --quiet
  PASS="$(head -c 18 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 20)"
  echo "$PASS" > "$WP_DIR/.admin-pass"; chmod 600 "$WP_DIR/.admin-pass"
  wp core install --url="http://127.0.0.1:$PORT" --title="Teya local" --admin_user=admin \
    --admin_password="$PASS" --admin_email=admin@example.com --skip-email --quiet
  wp rewrite structure '/%postname%/' --quiet
fi
# wp-cli may store the sub-path of --path as home/siteurl; pin both to the server root.
wp option update home "http://127.0.0.1:$PORT" --quiet
wp option update siteurl "http://127.0.0.1:$PORT" --quiet

if [[ -n "$THEME" ]]; then
  SRC="$ROOT/teya-memory/wp/theme/$THEME"
  [[ -d "$SRC" ]] || { echo "ERROR: theme not found: $SRC" >&2; exit 1; }
  ln -sfn "$SRC" "$WP_DIR/site/wp-content/themes/$THEME"
  if [[ -d "$ROOT/teya-memory/wp/mu-plugins" ]]; then
    mkdir -p "$WP_DIR/site/wp-content/mu-plugins"
    cp -f "$ROOT"/teya-memory/wp/mu-plugins/*.php "$WP_DIR/site/wp-content/mu-plugins/" 2>/dev/null || true
  fi
  wp theme activate "$THEME" --quiet
fi

if ! curl -fsS -o /dev/null "http://127.0.0.1:$PORT/" 2>/dev/null; then
  # PHP built-in server: unknown paths fall back to index.php, so pretty permalinks work.
  nohup php -S "127.0.0.1:$PORT" -t "$WP_DIR/site" > "$WP_DIR/server.log" 2>&1 &
  sleep 2
fi
curl -fsS -o /dev/null -w "WordPress: http://127.0.0.1:$PORT/ -> %{http_code}\n" "http://127.0.0.1:$PORT/" || echo "WARN: WordPress did not answer"
echo "Release gate: python3 teya/scripts/teya_release_gate.py --project-root . --local-url http://127.0.0.1:$PORT/"
