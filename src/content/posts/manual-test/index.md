---
title: 從 Obsidian vault 發佈的第二篇筆記
published: 2026-07-09
description: 這篇文章不是在網站 repo 裡寫的——它誕生於 Obsidian vault，由派上的轉換腳本驗證、轉換、推送上線。筆記 pipeline
  的第一次實彈測試。
tags:
- 網站建置
- pipeline
category: 網站建置
lang: zh_TW
---
<!-- generated from vault; do not edit -->

這篇筆記寫在樹梅派上的 Obsidian vault（`notes/從vault發佈的第二篇.md`，中文檔名），你現在看到它的網址卻是英文的 `/posts/hello-from-vault/`——因為 front matter 裡指定了 `slug`。

它的旅程：

1. 筆記存檔在 vault（原始檔**不會**出現在 GitHub 上）
2. 派上的 `convert.py` 掃描到 `publish: true`，跑完整驗證（slug 格式、日期、連結、附件）
3. 轉換成 Fuwari 格式、附件一併搬運，推送到網站 repo
4. GitHub Actions 的品質門檻放行後，部署到 CDN

附件嵌入測試（這張圖原本放在 vault 的 `attachments/`）：

![](./pipeline-demo.png)

這是人工測試的第二篇
