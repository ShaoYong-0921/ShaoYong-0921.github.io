---
title: 個人網站與筆記
published: 2026-08-19
description: 不只是一個部落格——從 Obsidian 筆記到自動上線的完整 pipeline，跑在一台樹梅派上。
tags:
- 作品集
- Astro
- DevOps
category: 作品集
lang: zh_TW
---
<!-- generated from vault; do not edit -->

## 專案說明

網站基於 [Fuwari](https://github.com/saicaca/fuwari) 主題開發， Astro 靜態部落格，筆記在 Obsidian 寫、存檔和發佈，中間的同步、驗證、轉換、部署由樹梅派自動處理。

## 架構

- **前端**：Fuwari 主題，自行移植到 Astro 7（上游綁 Astro 5），含 content collections 新 API、expressive-code 升級等一系列相容性改動
- **筆記層**：Obsidian + Self-hosted LiveSync，多裝置（Windows、iPad）經自架 CouchDB 端到端加密同步
- **中樞**：一台樹梅派跑 8 個 Docker 容器——CouchDB、同步橋接、code-server、瀏覽數 API（FastAPI + SQLite）、Cloudflare Tunnel、Watchtower 自動部署等
- **發佈管線**：systemd timer 每 5 分鐘執行——vault 快照 → gitleaks 機密掃描 → 轉換腳本（front matter 驗證、slug 檢查、附件搬運）→ 推送 GitHub
- **部署**：GitHub Actions 品質門檻→ GitHub Pages + Cloudflare DNS

## 亮點

- **存檔即發佈**：從 Obsidian 按下 Ctrl+S 到文章上線，全程零手動，實測約 5–8 分鐘
- **原始筆記不進 GitHub**：公開的只有轉換後的產物，私人筆記物理隔離
- **門檻式部署**：每一關（機密掃描、格式驗證、lint、型別檢查）紅燈都會擋下發佈
- **瀏覽數 API**：派上的 FastAPI 服務經 Cloudflare Tunnel 出公網，派本身零公網 port

## 目前狀態

持續開發中

**GitHub**：[ShaoYong-0921.github.io](https://github.com/ShaoYong-0921/ShaoYong-0921.github.io)
