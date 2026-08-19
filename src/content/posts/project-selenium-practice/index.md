---
title: Selenium 網頁自動化
published: 2026-08-19
description: 2021 年疫情時期的第一個自動化專案——用 Python + Selenium 把每天重複的網頁操作變成一行指令。
tags:
- 作品集
- Python
- 自動化
category: 作品集
lang: zh_TW
---
<!-- generated from vault; do not edit -->

## 專案說明

高中時期寫的網頁自動化練習：用 Python + Selenium 操作瀏覽器，自動完成每天都要做的校園網頁回報流程——登入、填表、送出，然後用 SMTP 寄一封確認信通知完成。

## 技術構成

- **Selenium WebDriver**：XPath 定位表單元素、模擬輸入與送出
- **pandas**：執行紀錄寫進 CSV（什麼時候跑過、跑了誰）
- **smtplib**：跑完自動寄信回報，不用自己檢查
- **設定與程式分離**：帳號資料放 `data.txt`、密碼放 `setting.py`，不寫死在主程式

## 現況

已封存。當年的網站已下線，留著當紀念。

**GitHub**：[selenium-practice](https://github.com/ShaoYong-0921/selenium-practice)
