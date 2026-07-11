# 備份與還原（F16）

## 備份

- `backup.sh`：CouchDB 資料（暫停容器數秒確保一致）+ vault 資料夾 + `~/.vault-git` + infra 機密設定，打包到 `~/backups/`，保留最近 7 份
- 排程：`vault-backup.timer`（每日 03:30，Persistent）
- 已知限制：備份與本體在同一顆 SSD——防誤刪/損毀，不防碟亡。異地加密備份另開 Issue

## 還原演練 SOP（每季跑一次；上次通過：2026-07-11）

```bash
DRILL=/tmp/restore-drill && mkdir -p $DRILL
tar xzf ~/backups/homepi-<日期>.tar.gz -C $DRILL
source <(grep -E "COUCHDB_(USER|PASSWORD)" ~/Desktop/fuwari/infra/.env | sed "s/^/export /")
docker run -d --rm --name couchdb-drill -p 127.0.0.1:5985:5984 \
  -e COUCHDB_USER -e COUCHDB_PASSWORD \
  -v $DRILL/data/couchdb:/opt/couchdb/data couchdb:3
sleep 15
curl -s -u "$COUCHDB_USER:$COUCHDB_PASSWORD" http://127.0.0.1:5985/vault | grep -o '"doc_count":[0-9]*'
# ↑ 與正式庫（:5984）的 doc_count 比對，一致即通過
docker stop couchdb-drill
# 清理：容器會 chown 資料檔，需借 root 容器刪除
docker run --rm -v $DRILL:/x alpine sh -c "rm -rf /x/data /x/vault /x/.vault-git /x/livesync-bridge-dat /x/.env"
rmdir $DRILL
```

## 完整災難還原（新派）

1. 裝 Docker + Tailscale，clone 網站 repo
2. 解開最新備份：`.env`、`livesync-bridge-dat/` 放回 `infra/`，`data/couchdb` 放回 `infra/data/`，`vault`、`.vault-git` 放回家目錄
3. `infra/` 內 `git clone --recursive https://github.com/vrtmrz/livesync-bridge`
4. `docker compose up -d` → 服務層重建完成（F17）
5. 依 infra/README 重掛 systemd timers
