#!/bin/bash
# 每月自動續期 Tailscale TLS 憑證（效期 90 天）並重載使用它的服務
# 前置：tailscale operator 已設為本使用者（sudo tailscale set --operator=homepi）
set -euo pipefail

CERT_DIR="$HOME/.config/code-server"
NAME="homepi.tail890983.ts.net"

tailscale cert --cert-file "$CERT_DIR/$NAME.crt" --key-file "$CERT_DIR/$NAME.key" "$NAME"
docker restart code-server >/dev/null
echo "cert renewed: $(openssl x509 -enddate -noout -in "$CERT_DIR/$NAME.crt")"
