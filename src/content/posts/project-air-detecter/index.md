---
title: 作品介紹：Air-detecter 即時空氣品質儀表板
published: 2026-08-19
description: 感測器資料上雲、即時圖表、離線偵測——2023 年的 IoT 全端練習。
tags:
- 作品集
- Python
- IoT
category: 作品集
lang: zh_TW
---
<!-- generated from vault; do not edit -->

## 這是什麼

2023 年底跟著線上課程做的即時空氣品質監測儀表板：感測端把量測資料寫進雲端資料庫，網頁端用 Python Dash 做即時視覺化——打開網頁就能看到最新的空氣品質曲線，感測器斷線了頁面也會直接顯示離線狀態。

【待補：感測端硬體與量測項目——用什麼板子、什麼感測器（PM2.5？CO₂？溫濕度？）、放在哪裡量】

## 技術構成

- **前端 / 服務**：Python Dash（Flask 基底）+ Plotly 圖表，`dcc.Interval` 每 3 秒輪詢刷新曲線、30 秒刷新主圖
- **資料層**：MongoDB Atlas 雲端資料庫，自寫 `DbWrapper` 封裝查詢
- **狀態偵測**：比對最新一筆資料的時間戳，超過門檻即判定感測器離線，儀表板即時顯示
- **部署**：gunicorn + Procfile，當年部署在 Heroku 型平台

## 現況

已封存（2023 年後未更新）。

**GitHub**：[air-detecter](https://github.com/ShaoYong-0921/air-detecter)
