---
title: SAMS 獎助學金申請與管理系統
published: 2026-08-19
description: 軟體工程課程期末專題 —— 六人團隊、PHP MVC、五種角色的完整申請審核流程。
tags:
- 作品集
- PHP
- 團隊專案
category: 作品集
lang: zh_TW
---
<!-- generated from vault; do not edit -->

## 專案說明

軟體工程課程的期末專題，六人團隊開發的獎助學金申請與管理系統（Scholarship Application and Management System）。把公告、申請、文件上傳、導師推薦、單位審核到後台維運，整合成一套系統。

系統有五種角色，各自有獨立的操作介面與權限：

- **學生**：瀏覽公告、線上申請、上傳證明文件
- **導師**：撰寫與管理推薦信
- **獎助單位**：檢視申請者、審核決定
- **管理員**：維護獎學金項目、公告與獎助單位
- **共通**：帳號註冊登入、個人資料維護、通知

## 技術構成

- **後端**：PHP 8.2，不套框架、自建 MVC——`Router` 解析 `/{controller}/{action}` 分派到對應 Controller，Model 層用 PDO 單例管理連線
- **資料庫**：MySQL 8.0，12 張表涵蓋使用者、申請、文件、推薦、審核紀錄等
- **前端**：Bootstrap 5 + 原生 JS
- **部署**：Docker Compose 一鍵起 PHP-Apache、MySQL、phpMyAdmin 三個容器
- **安全處理**：路由白名單擋非預期的 Controller 呼叫；上傳文件放在 web root 之外，一律經 Controller 驗證權限後才回傳

## 我負責的部分

主要做**獎助單位端的審核模組**和**重構原本網頁架構成MVC**——申請者列表、審核流程的 Controller 與 Model、以及對應的畫面。另外也參與了路由分派、獎學金資料層，和各角色 Dashboard 的實作。全案 60 個 commit 中我提交了 35 個。

## 現況

課程已結束，專案封存。原始碼為六人團隊共同著作。

**GitHub**：[scholarship](https://github.com/ShaoYong-0921/scholarship)
