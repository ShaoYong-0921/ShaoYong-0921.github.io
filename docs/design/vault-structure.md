# Vault 結構設計（M2 設計文件 1/3）

定案日：2026-07-09｜對應 spec §9 缺口「Vault 結構」

## 決策前提

- 全新專用 vault（不遷就舊筆記；舊筆記之後挑著搬入）
- 公私之分由 front matter `publish: true` 決定（F10），**不用資料夾區分**
- 附件集中一個資料夾
- 同步：Self-hosted LiveSync（M3）
- **vault 不上 GitHub**（2026-07-09 需求變更）：原始筆記只存在於派與各同步裝置；派上以本地 git（無 remote）保留版本歷史，systemd timer 自動 commit（F15 修訂版）

## 資料夾結構

```
vault/
├── notes/          一般筆記（中文檔名 OK；預設私密，publish: true 才發佈）
├── garden/         M5 即時筆記牆的公開範圍；M5 之前當一般資料夾用
├── attachments/    全 vault 附件集中地（Obsidian「預設附件位置」指到這）
├── templates/      Obsidian 模板；「發佈用 front matter 模板」放這
└── .obsidian/      Obsidian 設定
```

## 規則

1. **發佈掃描範圍**：轉換腳本掃 `notes/` 與 `garden/` 兩個資料夾中 `publish: true` 的筆記。
2. **檔名**：筆記檔名自由（中文為主）；發佈的網址一律來自 front matter 的 `slug`（見對應表文件）。
3. **附件**：一律進 `attachments/`；筆記內用 Obsidian 預設的 `![[檔名]]` 嵌入。單檔 > 2MB 轉換時警告（spec 風險表：vault 附件肥大）。
4. **`.obsidian/` 進 git**，但 `.gitignore` 排除 `workspace.json`、`workspace-mobile.json` 與快取——這些是各裝置的視窗狀態，同步會互相打架。
5. **機密紀律**：憑證、token 一律不進筆記（spec §8）；vault repo 的 CI 掛 gitleaks 把關。

## 待 M3 銜接

- vault 位於派 `~/Desktop/vault`，本地 git（無 remote）；LiveSync/CouchDB 負責裝置間同步
- 備份策略：各裝置持有完整 vault 副本（LiveSync 天然多副本）+ CouchDB 每日備份（F16）；異地加密備份另開 Issue 評估
- 發佈觸發：派上 systemd 排程跑轉換腳本（見 conversion-rules.md）
