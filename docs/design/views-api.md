# 瀏覽統計 API 設計（M4，關閉 spec §9 最後一個缺口）

定案日：2026-07-11

## 目標與邊界

- 每篇文章顯示瀏覽次數（spec M4 DoD）；只統計「次數」，**不儲存 IP、UA 或任何個資**
- 網站本體仍是純靜態：計數顯示為前端漸進增強，API 掛掉時只是不顯示數字，頁面完全不受影響
- 位置：網站 repo `api/`（單一 repo 原則）

## Endpoints

| Method | Path | 行為 | 回應 |
|---|---|---|---|
| POST | `/views/{slug}` | 計數 +1 並回傳新值 | `{"slug": "...", "views": N}` |
| GET | `/views/{slug}` | 只讀，不計數 | 同上（不存在回 0） |
| GET | `/healthz` | 健康檢查（容器 HEALTHCHECK 用） | `{"ok": true}` |

- `slug` 驗證：`^[a-z0-9]+(-[a-z0-9]+)*$` 且 ≤100 字元（與發佈 slug 規則一致），不符回 400——垃圾請求進不了資料庫
- CORS：只允許 `https://shaoyong.dev`

## 前端行為（Fuwari 端）

- 文章頁載入時 POST 一次；`sessionStorage` 去重（同分頁重看不重複計數）
- fetch 失敗即靜默隱藏數字（不 console 噪音、不影響版面）

## 儲存

- SQLite 單表：`views(slug TEXT PK, count INT, updated TEXT)`，WAL 模式
- 資料檔在 `infra/views-data/`（volume 掛載、不進 git、納入每日備份）

## 部署鏈（spec §5）

```
api/ 原始碼 → GitHub Actions 建 arm64 image → ghcr.io
→ 派上 Watchtower 自動拉新版 → cloudflared（Tunnel）→ api.shaoyong.dev 公網
```

- 容器以 uid 1000 執行；port 只綁 Tailscale IP（公網流量一律走 Tunnel 進來）
- 濫用防護 v1：slug 驗證 + Cloudflare 免費層（proxy/快取/基本防護）；進階 rate limit 留待觀察後開卡

## 測試

- unittest + FastAPI TestClient：計數遞增、GET 不計數、非法 slug 擋 400、健康檢查
