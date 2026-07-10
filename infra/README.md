# infra — 派上服務定義（F17）

新機器重建服務層：裝好 Docker 與 Tailscale 後——

```bash
cd infra
cp .env.example .env   # 填入帳密與 BIND_IP（Tailscale IP）
docker compose up -d
```

## 服務

| 服務 | 用途 | 資料 |
|---|---|---|
| couchdb | Obsidian Self-hosted LiveSync 同步中樞（F14） | `data/couchdb/`（不進 git；F16 備份對象） |
| livesync-bridge | CouchDB ⇄ 派上 vault 資料夾雙向橋（發佈管線的輸入端） | 設定 `livesync-bridge-dat/config.json`（含機密不進 git） |

livesync-bridge 需先手動 clone（含 submodule）：

```bash
cd infra
git clone --recursive https://github.com/vrtmrz/livesync-bridge
```

規劃中：code-server（容器化遷移）、vault 轉換排程、M4 FastAPI、M5 Perlite。

## 安全原則

- 所有服務只綁 Tailscale IP（`.env` 的 `BIND_IP`），公網不存在
- 機密只在 `.env`（gitignore），範本見 `.env.example`
