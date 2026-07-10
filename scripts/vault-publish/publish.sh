#!/bin/bash
# Vault 自動發佈管線（systemd timer 每 5 分鐘觸發）
# 快照 → gitleaks → 轉換驗證 → 推送。任一步失敗即中止，錯誤見 journalctl --user -u vault-publish
set -euo pipefail

VAULT="$HOME/Desktop/vault"
SITE="$HOME/Desktop/fuwari"
VGIT=(git --git-dir="$HOME/.vault-git" --work-tree="$VAULT")

exec 200>/tmp/vault-publish.lock
flock -n 200 || { echo "previous run still in progress, skip"; exit 0; }

if [ -n "$("${VGIT[@]}" status --porcelain)" ]; then
    "${VGIT[@]}" add -A
    "${VGIT[@]}" commit -q -m "auto: vault snapshot $(date +%F_%H%M)"
    echo "vault snapshot committed"
fi

if ! docker run --rm -v "$VAULT:/scan:ro" ghcr.io/gitleaks/gitleaks:latest \
        detect --source /scan --no-git --exit-code 9 --no-banner -v; then
    echo "gitleaks 偵測到疑似機密，發佈中止" >&2
    exit 1
fi

python3 "$SITE/scripts/vault-publish/convert.py" --vault "$VAULT" --site "$SITE"

cd "$SITE"
if [ -n "$(git status --porcelain -- src/content/posts .vault-manifest.json)" ]; then
    git add -- src/content/posts .vault-manifest.json
    git commit -q -m "Publish from vault (auto)"
    git push -q
    echo "published to site repo"
else
    echo "no publish changes"
fi
