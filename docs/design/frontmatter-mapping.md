# Front matter 對應表：Obsidian → Fuwari（M2 設計文件 2/3）

定案日：2026-07-09｜對應 spec §9 缺口「front matter 對應表」

## 對應表

| Obsidian 欄位 | 發佈時必填 | Fuwari 欄位 | 轉換規則 |
|---|---|---|---|
| `publish` | —（開關） | `draft` | `true` → `draft: false` 並納入轉換；缺欄或非 true → 跳過（預設私密） |
| `slug` | **必填** | 檔名（`<slug>/index.md`） | 格式 `^[a-z0-9]+(-[a-z0-9]+)*$`；缺、格式錯、與既有文章重複 → 擋 CI |
| `title` | 選填 | `title` | 缺 → 用筆記檔名（可中文） |
| `published` | **必填** | `published` | ISO 日期；缺或格式錯 → 擋 CI |
| `updated` | 選填 | `updated` | 原樣 |
| `description` | 建議 | `description` | 缺 → 警告不擋（Fuwari 會用內文摘要） |
| `tags` | 選填 | `tags` | 屬性面板的 tags 直接映射；內文 `#tag` v1 不轉 |
| `category` | 選填 | `category` | 原樣（中文為主，見 spec §10） |
| `lang` | 選填 | `lang` | 缺 → 預設 `zh_TW` |
| `image` | 選填 | `image` | 值為 `[[附件]]` 或路徑；轉換時複製附件並改為 `./檔名` 相對路徑 |
| 其他（aliases、cssclasses…） | — | — | 忽略，不輸出 |

## 發佈用模板（放 vault `templates/`）

```yaml
---
publish: false
slug:
title:
published: {{date}}
description:
tags: []
category:
lang: zh_TW
image:
---
```

## 輸出形式

- 每篇轉成網站 repo 的 `src/content/posts/<slug>/index.md`，引用到的附件複製到同資料夾（沿用 Fuwari 的相對路徑機制）
- 生成檔案開頭加註 `<!-- generated from vault; do not edit -->`；轉換器維護 manifest（`.vault-manifest.json`），**只增刪改自己管理的文章**，與手寫文章（如 katex-test）共存互不干擾
