# ShaoYong-0921 個人網站

技術筆記與作品集：**https://shaoyong-0921.github.io/**

基於 [Fuwari](https://github.com/saicaca/fuwari) 主題（MIT）的 Astro 靜態網站。
主題已自行移植到 **Astro 7**（上游為 Astro 5）——**請勿**直接套用上游更新或執行 `@astrojs/upgrade`，移植細節見 [docs/devlog/2026-07-08.md](docs/devlog/2026-07-08.md)。

## 架構

```
[派上開發：VS Code Remote-SSH / code-server]
        │ git push（main）
        ▼
[GitHub Actions — deploy.yml]
   quality（Biome lint + Astro check）
        │ 全綠才繼續（紅燈即不上線）
        ▼
   build（withastro/action，含 Pagefind 索引）
        ▼
   deploy ──► GitHub Pages（CDN）──► 訪客
```

- 網站本體是純靜態檔案，可用性不依賴任何自有主機
- 作品集資料源：`src/data/projects.json`（單一資料源，build 時抓 GitHub API 補星數）
- 完整需求規格與里程碑：[docs/devlog/spec.md](docs/devlog/spec.md)

## 本機啟動

需求：Node.js ≥ 20、pnpm ≥ 9

```bash
pnpm install
pnpm dev        # 開發伺服器 http://localhost:4321
pnpm build      # 靜態建置到 dist/（含 Pagefind 搜尋索引）
pnpm preview    # 預覽 build 結果
```

品質檢查（CI 跑的是同一套，push 前可先本地驗）：

```bash
pnpm exec biome ci ./src   # lint + 格式
pnpm run check             # Astro 型別檢查
```

## 寫文章

- 新文章放 `src/content/posts/`，檔名即 slug，**英文 kebab-case**（如 `merge-sort-notes.md` → `/posts/merge-sort-notes/`）
- front matter 依 `src/content.config.ts` 的 schema：`title`、`published` 必填；分類與標籤以中文為主；`lang` 標 `zh_TW` 或 `en`
- 附圖的文章可用資料夾形式：`my-post/index.md` + 同資料夾圖片
- push 到 main 即自動部署，約兩分鐘上線

## 主要技術

Astro 7・Fuwari（自維護移植）・Tailwind CSS・Svelte（互動元件）・Expressive Code・KaTeX・Pagefind・GitHub Actions / Pages

## 授權

主題原始碼依上游 Fuwari 之 [MIT License](LICENSE)；文章內容 © ShaoYong，採 CC BY-NC-SA 4.0。
