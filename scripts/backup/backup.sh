#!/bin/bash
# F16 每日備份：CouchDB 資料 + vault 資料夾 + infra 機密設定，保留最近 7 份
# 還原演練步驟見 scripts/backup/README.md
set -euo pipefail

BACKUP_DIR="$HOME/backups"
INFRA="$HOME/Desktop/fuwari/infra"
VAULT="$HOME/Desktop/vault"
STAMP=$(date +%F_%H%M)
OUT="$BACKUP_DIR/homepi-$STAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

# 暫停 CouchDB 確保檔案一致性（幾秒鐘；LiveSync 客戶端會自動重試）
docker pause couchdb >/dev/null
trap 'docker unpause couchdb >/dev/null 2>&1 || true' EXIT

tar czf "$OUT" \
    -C "$INFRA" data/couchdb .env livesync-bridge-dat/config.json \
    -C "$HOME/Desktop" vault \
    -C "$HOME" .vault-git

docker unpause couchdb >/dev/null
trap - EXIT

# 保留最近 7 份
ls -1t "$BACKUP_DIR"/homepi-*.tar.gz | tail -n +8 | xargs -r rm --

echo "backup done: $OUT ($(du -h "$OUT" | cut -f1))"
