# 個人網站：需求規格與開發計畫

版本：v2（2026-07-08 重整）｜開發模式：單人敏捷

## 1. 專案概述

- 開發者：一人。技能：Python/C/C++/PHP/SQL、Git/GitHub、Linux 日常使用、Docker 用過現成 image、前端基礎；修過軟工/演算法/資料庫。
- 目標：建立個人網站（門面 + 筆記發佈），同時作為後端與 DevOps 練習場。
- 硬體：Raspberry Pi 4 4GB + SSD（Debian 13，已運行 code-server、Tailscale、Docker）。
- 年度現金成本上限：約 NT$500（僅網域，其餘全免費）。

## 2. 功能需求

### A. 網站（靜態層，GitHub Pages + Fuwari）

| 編號 | 需求 | 優先級 |
|---|---|---|
| F1 | 技術筆記/部落格：Markdown、分類、標籤 | P0 |
| F2 | 作品集：`projects.json` 單一資料源（name/desc/tech/github/demo/localPath），build 時抓 GitHub API 補星數與更新時間 | P0 |
| F3 | 自我介紹頁 + 社群連結 | P0 |
| F4 | 實驗性專案展示區（可掛派上服務的 demo） | P1 |
| F5 | 中英雙語：介面雙語、文章依性質擇一語言（文章 front matter 標 `lang`） | P0 |
| F6 | 程式碼高亮（Expressive Code 內建）+ 數學公式（KaTeX 需自加） | P0 |
| F7 | 深色/淺色模式（Fuwari 內建） | P0 |
| F8 | `/lab` 私人入口頁：讀 `projects.json` 的 `localPath` 生成 code-server `?folder=` 直開連結 + 內部工具連結（Fauxton、監控） | P1 |
| F9 | RSS、全文搜尋（Pagefind）、TOC——Fuwari 內建，隨主題免費取得 | P0 |

### B. 筆記發佈 pipeline（Obsidian → 網站）

| 編號 | 需求 | 優先級 |
|---|---|---|
| F10 | front matter 標 `publish: true` 才發佈（預設私密），轉換時映射為 Fuwari 的 `draft: false` | P0 |
| F11 | 格式轉換：wiki link `[[...]]` → 標準連結、附件圖片搬移 | P0 |
| F12 | 筆記更新 → 網站自動重建部署，全程零手動 | P0 |
| F13 | 轉換失敗擋 CI 並通知（紅燈即不上線） | P1 |

### C. 多裝置同步（iPad / Android / Windows / Linux(派)）

| 編號 | 需求 | 優先級 |
|---|---|---|
| F14 | 四平台 Obsidian 經 Self-hosted LiveSync + CouchDB（派上 Docker）即時同步，走 Tailscale，開 E2E 加密 | P0 |
| F15 | 派上 systemd timer 自動 commit + push vault 到 GitHub（裝置端免 Git 操作） | P0 |
| F16 | CouchDB 每日備份 + 已演練過還原 | P0 |

### D. 未來功能（架構已預留，不排入 M1–M4）

- **即時筆記牆（M5，Perlite）**：`garden/` 資料夾由派上 Perlite 容器即時渲染，與精選發佈並存（精選＝門面、CDN；筆記牆＝即時、動態）。先僅 Tailscale，視需求再公開。
- 公私筆記分流（需認證）、留言、瀏覽統計以外的 API（搜尋等）。

## 3. 非功能需求

- 網站本體可用性不依賴派/家用網路（靜態層在 CDN）。
- 派不開任何對公網的 port：私人服務走 Tailscale，公開服務（M4 起）走 Cloudflare Tunnel。
- 所有內容與設定進 Git；機密用 GitHub Secrets / 環境變數，不進 repo。
- 管理介面（Fauxton、code-server）永不對公網暴露。

## 4. 系統架構

```
[iPad / Android / Windows / Linux(派) — Obsidian]
        ⇅ Tailscale 私網（同步、IDE、SSH——僅自己的裝置）
[Raspberry Pi 4（Docker + UFW）]
   - CouchDB（M3）＝LiveSync 同步中樞
   - code-server（既有）＝瀏覽器 IDE，綁 Tailscale IP
   - systemd timer（M3）＝vault 自動 commit + push
   - FastAPI（M4）＝統計 API ◄─ Cloudflare Tunnel（M4 才建）◄─ 訪客
   - Perlite（M5）＝garden/ 即時筆記牆
        │ git push
        ▼
[筆記 repo] ─► [GitHub Actions] ─► [GitHub Pages（Fuwari）]
              篩選 publish、wiki link         ▲
              轉換、lint、建置          訪客瀏覽（CDN）
```

**通道原則**：私人服務（IDE、SSH、DB 管理）一律走 Tailscale，公網上不存在；只有「訪客瀏覽器要呼叫」的服務（M4 統計 API）才經 Cloudflare Tunnel 對外。

## 5. 技術選型

| 層 | 工具 | 選用理由 |
|---|---|---|
| 筆記 | Obsidian（既有） | 本地 Markdown、資料自主 |
| SSG | Astro | Markdown 支援最佳、零 JS 預設輸出 |
| 主題 | Fuwari（template 模式） | Obsidian 風格、深色/搜尋/RSS 內建、MIT、程式碼歸自己所有 |
| 同步 | Self-hosted LiveSync + CouchDB | 四平台全支援、免月費、E2E 加密 |
| 版控/CI/CD | Git + GitHub + Actions | 已會；repo、CI、託管零整合成本 |
| 靜態託管 | GitHub Pages | 免費 CDN、不依賴家中網路 |
| 容器 | Docker + compose | 服務隔離、compose 檔即文件（已裝） |
| 私人通道 | Tailscale（既有） | SSH/IDE/管理介面全走私網 |
| 公開通道 | Cloudflare Tunnel（M4） | 免開 port、免固定 IP、自帶 HTTPS |
| 開發環境 | code-server（既有） | 全裝置瀏覽器 IDE，`/lab` 頁整合入口 |
| 後端 | FastAPI + SQLite/PostgreSQL（M4） | Python 最熟、自動 API 文件、銜接資料庫課 |
| 部署 | ghcr.io + Watchtower（M4） | Actions 建 arm64 image、派自動拉新版 |
| 排程 | systemd timer | 比 cron 好除錯（journalctl） |
| 監控 | UptimeRobot（或 Uptime Kuma） | 免費、掛了通知 |

## 6. 開發計畫

### 單人敏捷運作規則

- **Backlog**：GitHub Projects 看板（Backlog / Todo / Doing / Done），里程碑拆 Issue。
- **Sprint = 1 週**：週日 15 分鐘回顧 + 挑下週 2–4 張，記錄寫開發日誌。
- **WIP = 1**：Doing 同時只有一張。
- **每週收尾**：main 保持可部署，網站隨時是可用版本。
- 不採用：站會、故事點、burndown。

### Roadmap

**M1 網站骨架（週 1–2）**
Fuwari template 建站：config 客製、中英路由、KaTeX、作品集（projects.json）、`/lab` 頁；Actions 自動部署 Pages；買網域接 Cloudflare DNS。
DoD：網址可訪問、中英切換、深色模式、push 即自動更新。

**M2 筆記 pipeline（週 3–4）**
先補三份設計文件（見 §9）；vault repo + Python 轉換腳本 + Actions 串接；gitleaks 掃描進 CI。
DoD：標 `publish: true` 的筆記從存檔到上線全程零手動；轉換錯誤擋 CI。

**M3 派同步中樞（週 5–7，全走 Tailscale，不需 Tunnel）**
派加固（SSH 金鑰、ufw、fail2ban、關 lightdm/rpcbind 等閒置服務、DHCP 保留、散熱）；code-server 改綁 Tailscale IP；CouchDB compose + 四平台 LiveSync；systemd timer 自動 push；備份 + 還原演練。
DoD：任一裝置寫筆記 → 四平台同步 → 自動進 Git → 網站更新，零手動；備份可還原。

**M4 第一個公開 API（週 8+）**
建 Cloudflare Tunnel（api. 子網域）；FastAPI 瀏覽統計：Dockerfile → Actions 建 arm64 image → ghcr.io → Watchtower 自動部署。
DoD：每頁顯示瀏覽次數；公網可呼叫；CI/CD 全自動。

**M5 即時筆記牆（選做）**
Perlite 容器唯讀掛載 `garden/`，先僅 Tailscale。
DoD：garden/ 筆記存檔數秒內可在筆記牆看到；私密筆記不可達。

### M1 初始 Backlog

| # | Issue | 備註 |
|---|---|---|
| 1 | Fuwari template 建 repo，本機 `pnpm dev` 跑起來 | `npm create fuwari@latest` |
| 2 | `src/config.ts`：站名、簡介、社群連結、主題色 | |
| 3 | KaTeX 支援（remark-math + rehype-katex），寫含公式測試文驗證 | |
| 4 | GitHub Pages 部署 workflow，push 自動上線 | 改 `astro.config.mjs` 的 site |
| 5 | 買網域、DNS 接 Cloudflare、指到 Pages | 子網域 api. 留到 M4 |
| 6 | 資訊架構：導覽列頁面、筆記 slug 規則（英文 slug 手動指定） | 設計缺口 |
| 7 | `projects.json` + 作品集頁（build 時抓 GitHub API） | 設計缺口 |
| 8 | `/lab` 頁：讀 projects.json 生成 code-server `?folder=` 連結 + 內部工具連結 | F8 |
| 9 | README：架構圖、本機啟動方式 | DoD 一部分 |

## 7. 教科書對應（Pressman & Maxim 9e）

採**演化式/增量過程模型 + 敏捷實務**。做到哪個里程碑讀對應章節，拿專案當習題：

| 專案活動 | 章節 |
|---|---|
| 迭代方式、單人敏捷 | Ch 2–4 |
| 本規格書（§2–3 需求工程） | Ch 7–8 |
| 架構與分層（§4） | Ch 9–10 |
| API 分層（router/service/repository，M4） | Ch 11 |
| 主題微調、雙語、深色模式 | Ch 12 |
| CI 品質門檻、自我 code review | Ch 15–16 |
| API 測試（happy path + 錯誤 case） | Ch 19–20 |
| 加固、Tunnel、secrets、defense in depth | Ch 18 |
| Git、分支、CI/CD、環境設定 | Ch 22（SCM） |
| 里程碑、DoD、Issue 驅動 | Ch 24–25 |
| 風險表（§8） | Ch 26 |
| 監控、備份、維運 | Ch 27 |

## 8. 風險

| 風險 | 對策 |
|---|---|
| 轉換 edge case 多（巢狀 wiki link、嵌入） | 先支援常用語法，其餘擋 CI 逐步補 |
| 範圍膨脹做不完 | 嚴守 DoD 與 WIP=1，新想法一律先開 Issue |
| 派或家網掛掉 | 靜態層在 CDN，網站本體不受影響 |
| 溫度過高降頻（實測 70°C） | 加散熱片 + 風扇殼 |
| CouchDB 掛掉 | 各裝置本地有完整 vault，不丟資料；監控 + 還原演練 |
| vault 附件肥大 | 附件大小上限，必要時分離同步 |
| Fuwari 上游停更 | template 模式程式碼歸自己；內容為 Markdown 可攜，換主題只搬 front matter |
| 即時牆誤公開私密筆記（M5） | 公開以資料夾為界；容器唯讀且只掛 `garden/`；上線前抽查 |
| Perlite 成為攻擊面（M5） | 先僅 Tailscale；非 root + 唯讀 + 資源上限；公開才加 WAF/rate limit |
| 筆記意外含機密 | gitleaks 進 CI（M2 起）；憑證不進筆記的紀律 |

## 9. 設計缺口追蹤

| 缺口 | 需要時點 | 狀態 |
|---|---|---|
| 資訊架構 / URL / slug 規則 | M1（Issue #6） | 已定案（見 §10） |
| projects.json 欄位定案 | M1（Issue #7） | 草案已定（§2 F2） |
| front matter 對應表（Obsidian → Fuwari） | M2 開工前 | 未完成 |
| Vault 結構（資料夾、附件、公私共存、`garden/` 預留） | M2 開工前 | 未完成 |
| 轉換錯誤處理規則（何者擋 CI） | M2 開工前 | 未完成 |
| API 詳細設計（endpoint、schema） | M4 開工前 | 刻意延遲 |

## 10. 資訊架構定案（M1 Issue #6，2026-07-09）

- **Slug / 檔名**：文章檔名即 slug，純英文 kebab-case（如 `merge-sort-notes.md` → `/posts/merge-sort-notes/`），不加日期前綴；日期由 front matter 的 `published` 承載。
- **分類與標籤**：以中文為主（如「網站建置」）；英文文章的標籤可用英文。分類保持少而穩定，標籤自由增長。
- **雙語呈現（F5）**：每篇文章依性質擇一語言撰寫，front matter 標 `lang`（`zh_TW` / `en`）。
- **導覽列**：首頁、彙整、關於、GitHub；「作品集」隨 Issue #7 頁面完成時加入；Lab（F8）完成後視需要加入。
