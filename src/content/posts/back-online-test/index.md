---
title: 重灌後的全鏈路測試
published: 2026-08-19
description: Windows 重灌後的第一篇實彈測試：Obsidian（新機）→ LiveSync → CouchDB → 派 → convert.py
  → GitHub Actions → 上線。如果你看得到這篇，整條管線已完全復活。
tags:
- 網站建置
- pipeline
category: 網站建置
lang: zh_TW
---
<!-- generated from vault; do not edit -->

這篇筆記誕生於重灌後的 Windows 新機（vault 已搬到 `D:\Obsidin test`）。

它的旅程比七月那篇更曲折：中間經歷了 Windows 重灌、派離線又復活、LiveSync 升級 1.0、CouchDB 資料庫重建、bridge 升級重建映像——但此刻它仍然只需要「存檔」，剩下的交給管線。

如果你看得到這篇文章，代表：

1. 新機的 Obsidian ⇄ CouchDB 同步正常
2. 派上的 livesync-bridge（升級後）正常落地檔案
3. `vault-publish.timer` 的 gitleaks → convert.py → push 全程綠燈
4. GitHub Actions 品質門檻放行並部署

歡迎回來。
