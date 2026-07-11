# ShaoYong-0921 個人網站與筆記系統

技術筆記與作品集：**https://shaoyong.dev/**

基於 [Fuwari](https://github.com/saicaca/fuwari) 主題（MIT）的 Astro 靜態網站，加上以樹梅派為中樞的
Obsidian 同步與自動發佈管線。主題已自行移植到 **Astro 7**（上游為 Astro 5）——**請勿**直接套用上游更新或
執行 `@astrojs/upgrade`，移植細節見 [docs/devlog/2026-07-08.md](docs/devlog/2026-07-08.md)。

## 架構

```
[各裝置 Obsidian] ◄─LiveSync（E2E 加密）─► [派：CouchDB] ◄─橋─► [派：vault 資料夾]
                                                                    │ systemd 每 5 分鐘
                                                       快照 → gitleaks → 轉換驗證
                                                                    │ 全綠才推（紅燈即不上線）
[shaoyong.dev] ◄─CDN─ [GitHub Pages] ◄─門檻 CI─ [本 repo] ◄─產物 push─┘
      ▲                （lint→型別→建置→部署）
   訪客瀏覽
```

- 網站本體是純靜態檔案，可用性不依賴任何自有主機；原始筆記**不上 GitHub**，只存在於派與同步裝置
- 派上服務（CouchDB、livesync-bridge、code-server）以 docker compose 定義於 [`infra/`](infra/)，
  新機器 `compose up` 即可重建（F17）；私人服務只在 Tailscale 私網可達，公網不存在
- 每日備份 + 已演練還原：[`scripts/backup/`](scripts/backup/)
- 私人入口頁 `/lab`：code-server 直開連結與內部工具（連結僅私網有效）

## 本機啟動（網站部分）

需求：Node.js ≥ 20、pnpm ≥ 9

```bash
pnpm install
pnpm dev        # 開發伺服器 http://localhost:4321
pnpm build      # 靜態建置到 dist/（含 Pagefind 搜尋索引）
```

品質檢查（CI 跑的是同一套，push 前可先本地驗）：

```bash
pnpm exec biome ci ./src   # lint + 格式
pnpm run check             # Astro 型別檢查
```

## 寫文章

**主要方式（Obsidian，全自動）**：在 vault 的筆記插入 `publish-post` 模板 → 填 `slug`（英文
kebab-case，即網址）→ `publish: true` → 存檔。五分鐘內自動驗證、轉換、部署上線。單一換行即
換行（remark-breaks），與 Obsidian 所見一致；`![[圖片]]`、`[[已發佈筆記]]` 皆自動轉換。
規則全文：[docs/design/](docs/design/)。

**手動方式**：新文章放 `src/content/posts/`，front matter 依 `src/content.config.ts` schema，
push 即部署。轉換器生成的文章帶有標記與 manifest 管理，與手寫文章互不干擾。

## 主要技術

Astro 7・Fuwari（自維護移植）・Tailwind・Svelte・Expressive Code・KaTeX・Pagefind・
GitHub Actions / Pages・Obsidian + Self-hosted LiveSync・CouchDB・Docker Compose・Tailscale

## 授權

主題原始碼依上游 Fuwari 之 [MIT License](LICENSE)；文章內容 © ShaoYong，採 CC BY-NC-SA 4.0。
