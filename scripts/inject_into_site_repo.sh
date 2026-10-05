#!/usr/bin/env bash
# Inject the Teya fork into a SITE repository so Cursor Cloud Agents get
# the same rules/skills/subagents/commands without a plugin install.
#
# Usage:
#   bash scripts/inject_into_site_repo.sh /path/to/site-repo
#   (run from the fork root, or set TEYA_SRC=/path/to/teya-cursor-plugin)
#
# Result inside the site repo (all committed, idempotent re-run = update):
#   teya/                      full copy of the fork (paths teya/shared, teya/scripts resolve)
#   .cursor/rules/teya-*.mdc   copies of rules/*.mdc   (project rules)
#   .cursor/skills/<skill>/    copies of skills/*       (project skills)
#   .cursor/agents/*.md        copies of agents/*       (project subagents)
#   .cursor/commands/*.md      copies of commands/*     (project commands)
#   AGENTS.md                  block "Cursor Cloud specific instructions (Teya)"
#   .cursor/environment.json   only if absent: pip deps for teya scripts
set -euo pipefail

SITE="${1:?usage: inject_into_site_repo.sh /path/to/site-repo}"
SRC="${TEYA_SRC:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
[[ -f "$SRC/.cursor-plugin/plugin.json" ]] || { echo "not a Teya plugin root: $SRC" >&2; exit 1; }
[[ -d "$SITE" ]] || { echo "site repo not found: $SITE" >&2; exit 1; }
SITE="$(cd "$SITE" && pwd)"
REV="$(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo unknown)"

echo "Teya src: $SRC @ $REV"
echo "Site repo: $SITE"

# 1) full copy of the fork into teya/ (no .git, no runtime memory/secrets)
rm -rf "$SITE/teya" && mkdir -p "$SITE/teya"
tar -C "$SRC" \
  --exclude './.git' --exclude './teya-memory' --exclude '__pycache__' \
  --exclude '.env' --exclude '.env.*' --exclude '*.local' --exclude '*.credentials*' \
  -cf - . | tar -C "$SITE/teya" -xf -
echo "$REV" > "$SITE/teya/.teya-fork-rev"

# 2) project-level Cursor components (copies, not symlinks)
mkdir -p "$SITE/.cursor/rules" "$SITE/.cursor/skills" "$SITE/.cursor/agents" "$SITE/.cursor/commands"
for f in "$SRC"/rules/*.mdc; do
  b="$(basename "$f")"; case "$b" in teya-*) dst="$b";; *) dst="teya-$b";; esac
  cp "$f" "$SITE/.cursor/rules/$dst"
done
for d in "$SRC"/skills/*/; do
  n="$(basename "$d")"
  rm -rf "$SITE/.cursor/skills/$n" && cp -R "${d%/}" "$SITE/.cursor/skills/$n"
done
cp "$SRC"/agents/*.md "$SITE/.cursor/agents/"
cp "$SRC"/commands/*.md "$SITE/.cursor/commands/"

# 3) AGENTS.md block (replace between markers, keep the rest of the file)
BEGIN='<!-- TEYA-CLOUD:BEGIN -->'; END='<!-- TEYA-CLOUD:END -->'
BLOCK="$(cat <<MD
$BEGIN
## Cursor Cloud specific instructions (Teya)

Этот репозиторий собирается пайплайном **Teya** (форк ez2582458-prog/teya-cursor-plugin, rev \`$REV\`).
В облаке плагин НЕ устанавливается — всё лежит прямо в репо:

- \`.cursor/rules/teya-*.mdc\` — правила оркестратора (главное: \`teya-orchestrator.mdc\`, \`teya-manual-keywords.mdc\`, \`teya-wordpress-by-default.mdc\`).
- \`.cursor/skills/\` — skills Teya (\`director-teya\`, \`manual-keywords-url-map\`, \`aurora-*\`, \`excalibur*\` …).
- \`.cursor/agents/\` — субагенты (director, aurora-team-*, excalibur …), \`.cursor/commands/\` — \`/teya-start\`, \`/teya-phase1\` …
- \`teya/\` — полная копия плагина. Пути вида \`teya/shared/...\`, \`teya/scripts/...\` считаются от корня репо.
- Рабочие данные: \`teya-memory/\` (site.inv заполняет бот/Директор из чата, пользователь руками не правит).
- Ядрышко / Wordstat / MCP-KV для ключей **не используются**: ключи + URL-карта — skill \`manual-keywords-url-map\`.
- Секреты (FTP/SFTP/WP) — только из Cloud Agent Secrets (cursor.com/dashboard → Cloud Agents → Secrets), не коммитить.

Старт: \`/teya-start\` (или «запусти Teya для этого сайта» — Директор читает \`.cursor/rules/teya-*\`).
Обновить Teya в этом репо: из форка \`bash scripts/inject_into_site_repo.sh <путь к этому репо>\` и закоммитить.
$END
MD
)"
AG="$SITE/AGENTS.md"
if [[ -f "$AG" ]] && grep -qF "$BEGIN" "$AG"; then
  python3 - "$AG" "$BEGIN" "$END" "$BLOCK" <<'PY'
import sys,re
p,b,e,blk=sys.argv[1:]
s=open(p,encoding='utf-8').read()
s=re.sub(re.escape(b)+r'.*?'+re.escape(e), lambda m: blk, s, flags=re.S)
open(p,'w',encoding='utf-8').write(s)
PY
else
  { [[ -f "$AG" ]] && { cat "$AG"; echo; }; printf '%s\n' "$BLOCK"; } > "$AG.tmp" && mv "$AG.tmp" "$AG"
fi

# 4) environment.json only if the site repo has none
ENVJ="$SITE/.cursor/environment.json"
if [[ ! -f "$ENVJ" ]]; then
  cat > "$ENVJ" <<'JSON'
{
  "install": "python3 -m pip install --user --no-cache-dir paramiko pillow || true; python3 teya/scripts/prepare_teya_memory.py --project-root \"$PWD\" || true"
}
JSON
  echo "created .cursor/environment.json"
fi

# 5) keep runtime memory/secrets out of git
GI="$SITE/.gitignore"; touch "$GI"
for pat in 'teya-memory/*.local' 'teya-memory/teya.env.local' '*.credentials.local' '.env.local'; do
  grep -qxF "$pat" "$GI" || echo "$pat" >> "$GI"
done

echo "Done. Review and commit in $SITE:"
echo "  git add teya .cursor AGENTS.md .gitignore && git commit -m 'Inject Teya fork ($REV) for Cursor Cloud' && git push"
