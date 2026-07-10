#!/usr/bin/env python3
"""Vault → 網站發佈轉換器。

掃描 vault 的 notes/ 與 garden/ 中標 publish: true 的筆記，驗證後轉換為
Fuwari 文章（src/content/posts/<slug>/index.md + 同資料夾附件）。
任一錯誤即整批不寫入（紅燈即不上線）；錯誤一次全部列出。
規則定義：網站 repo docs/design/ 下的三份設計文件。
"""

import argparse
import datetime
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

MARKER = "<!-- generated from vault; do not edit -->"
MANIFEST_NAME = ".vault-manifest.json"
SCAN_DIRS = ("notes", "garden")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}
FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.DOTALL)
WIKI_RE = re.compile(r"(!?)\[\[([^\[\]]+)\]\]")
CHUNK_RE = re.compile(r"(```.*?(?:```|$)|`[^`\n]*`)", re.DOTALL)
ATTACHMENT_WARN_BYTES = 2 * 1024 * 1024


class Note:
    def __init__(self, path: Path, rel: str, fm: dict, body: str):
        self.path = path
        self.rel = rel
        self.fm = fm
        self.body = body
        self.slug = fm.get("slug")
        self.assets: list[tuple[Path, str]] = []  # (來源檔, 目的檔名)


class Result:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.actions: list[str] = []

    def error(self, rel: str, kind: str, msg: str):
        self.errors.append(f"{rel}: {kind}: {msg}")

    def warn(self, rel: str, msg: str):
        self.warnings.append(f"{rel}: {msg}")


def parse_front_matter(text: str):
    m = FM_RE.match(text)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return e, m.group(2)
    if not isinstance(fm, dict):
        fm = {}
    return fm, m.group(2)


def collect_notes(vault: Path, res: Result) -> list[Note]:
    notes = []
    for d in SCAN_DIRS:
        base = vault / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            rel = p.relative_to(vault).as_posix()
            fm, body = parse_front_matter(p.read_text(encoding="utf-8"))
            if isinstance(fm, yaml.YAMLError):
                res.error(rel, "front-matter", f"YAML 解析失敗：{fm}")
                continue
            if fm is None or fm.get("publish") is not True:
                continue
            notes.append(Note(p, rel, fm, body))
    return notes


def coerce_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        return datetime.date.fromisoformat(value)
    raise ValueError(str(value))


def validate(notes: list[Note], site: Path, manifest: dict, res: Result):
    posts_dir = site / "src" / "content" / "posts"
    managed = set(manifest.get("slugs", []))
    seen_slugs: dict[str, str] = {}
    seen_names: dict[str, str] = {}
    for n in notes:
        name = n.path.stem
        if name in seen_names:
            res.error(n.rel, "duplicate-name", f"筆記名與 {seen_names[name]} 重複，wiki link 無法解析")
        else:
            seen_names[name] = n.rel

        if not n.slug or not isinstance(n.slug, str):
            res.error(n.rel, "slug", "發佈筆記必須指定 slug")
            continue
        if not SLUG_RE.match(n.slug):
            res.error(n.rel, "slug", f"格式不符 kebab-case：{n.slug!r}")
            continue
        if n.slug in seen_slugs:
            res.error(n.rel, "slug", f"與 {seen_slugs[n.slug]} 的 slug 重複")
            continue
        seen_slugs[n.slug] = n.rel

        if n.slug not in managed:
            if (posts_dir / n.slug).exists() or (posts_dir / f"{n.slug}.md").exists():
                res.error(n.rel, "slug", f"與網站既有（非轉換器管理的）文章衝突：{n.slug}")

        try:
            n.fm["published"] = coerce_date(n.fm.get("published"))
        except (ValueError, TypeError):
            res.error(n.rel, "published", "缺少或非法的發佈日期（需 ISO 格式）")

        if not n.fm.get("description"):
            res.warn(n.rel, "缺 description（將以內文摘要代替）")
        if not n.fm.get("category"):
            res.warn(n.rel, "缺 category")


def find_attachment(vault: Path, filename: str):
    hits = sorted((vault / "attachments").rglob(filename)) if (vault / "attachments").is_dir() else []
    return hits


def resolve_embed(note: Note, inner: str, vault: Path, res: Result) -> str:
    target = inner.split("|")[0].strip()
    ext = Path(target).suffix.lower()
    if ext not in IMAGE_EXTS:
        res.error(note.rel, "unsupported", f"不支援的嵌入（僅支援圖片附件）：![[{inner}]]")
        return f"![[{inner}]]"
    hits = find_attachment(vault, Path(target).name)
    if not hits:
        res.error(note.rel, "attachment", f"attachments/ 中找不到：{target}")
        return f"![[{inner}]]"
    if len(hits) > 1:
        res.error(note.rel, "attachment", f"attachments/ 中有多個同名檔案：{target}")
        return f"![[{inner}]]"
    src = hits[0]
    if src.stat().st_size > ATTACHMENT_WARN_BYTES:
        res.warn(note.rel, f"附件超過 2MB：{target}")
    note.assets.append((src, src.name))
    return f"![]({'./' + src.name})"


def resolve_link(note: Note, inner: str, slug_by_name: dict, res: Result) -> str:
    parts = inner.split("|", 1)
    target = parts[0].strip()
    label = parts[1].strip() if len(parts) > 1 else target
    if "#" in target:
        res.error(note.rel, "unsupported", f"暫不支援標題/區塊連結：[[{inner}]]")
        return f"[[{inner}]]"
    name = Path(target).stem
    slug = slug_by_name.get(name)
    if slug is None:
        res.error(note.rel, "wiki-link", f"連到不存在或未發佈的筆記：[[{target}]]")
        return f"[[{inner}]]"
    return f"[{label}](/posts/{slug}/)"


def convert_body(note: Note, slug_by_name: dict, vault: Path, res: Result) -> str:
    def transform(text: str) -> str:
        def sub(m):
            embed, inner = m.group(1), m.group(2)
            if embed:
                return resolve_embed(note, inner, vault, res)
            return resolve_link(note, inner, slug_by_name, res)

        return WIKI_RE.sub(sub, text)

    out = []
    for chunk in CHUNK_RE.split(note.body):
        if chunk.startswith("```"):
            info = chunk[3:].split("\n", 1)[0].strip().lower()
            if info == "dataview":
                res.error(note.rel, "unsupported", "dataview 區塊無法轉換")
            out.append(chunk)
        elif chunk.startswith("`"):
            out.append(chunk)
        else:
            out.append(transform(chunk))
    return "".join(out)


def resolve_image_field(note: Note, vault: Path, res: Result):
    raw = note.fm.get("image")
    if not raw:
        return None
    raw = str(raw).strip()
    m = re.fullmatch(r"!?\[\[([^\[\]]+)\]\]", raw)
    if m:
        converted = resolve_embed(note, m.group(1), vault, res)
        return converted[4:-1] if converted.startswith("![](") else None
    return raw


def render(note: Note, body: str, image) -> str:
    fm: dict = {
        "title": note.fm.get("title") or note.path.stem,
        "published": note.fm["published"],
    }
    if note.fm.get("updated"):
        fm["updated"] = coerce_date(note.fm["updated"])
    fm["description"] = note.fm.get("description") or ""
    fm["tags"] = note.fm.get("tags") or []
    fm["category"] = note.fm.get("category") or ""
    fm["lang"] = note.fm.get("lang") or "zh_TW"
    if image:
        fm["image"] = image
    dumped = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{dumped}---\n{MARKER}\n\n{body.strip()}\n"


def load_manifest(site: Path) -> dict:
    p = site / MANIFEST_NAME
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"slugs": []}


def run(vault: Path, site: Path, dry_run: bool = False) -> Result:
    res = Result()
    posts_dir = site / "src" / "content" / "posts"
    manifest = load_manifest(site)
    notes = collect_notes(vault, res)
    validate(notes, site, manifest, res)

    slug_by_name = {n.path.stem: n.slug for n in notes if n.slug}
    rendered: dict[str, tuple[Note, str]] = {}
    for n in notes:
        if not n.slug or not isinstance(n.fm.get("published"), datetime.date):
            continue
        body = convert_body(n, slug_by_name, vault, res)
        image = resolve_image_field(n, vault, res)
        rendered[n.slug] = (n, render(n, body, image))

    if res.errors:
        return res

    new_slugs = sorted(rendered.keys())
    stale = [s for s in manifest.get("slugs", []) if s not in rendered]
    for slug, (n, content) in sorted(rendered.items()):
        res.actions.append(f"write posts/{slug}/ （來源 {n.rel}，附件 {len(n.assets)}）")
    for s in stale:
        res.actions.append(f"delete posts/{s}/ （來源筆記已取消發佈）")

    if dry_run:
        return res

    for slug, (n, content) in rendered.items():
        out_dir = posts_dir / slug
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)
        (out_dir / "index.md").write_text(content, encoding="utf-8")
        for src, name in n.assets:
            shutil.copy2(src, out_dir / name)

    for s in stale:
        out_dir = posts_dir / s
        idx = out_dir / "index.md"
        if idx.exists() and MARKER in idx.read_text(encoding="utf-8"):
            shutil.rmtree(out_dir)

    (site / MANIFEST_NAME).write_text(
        json.dumps({"slugs": new_slugs}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Vault → Fuwari 發佈轉換器")
    ap.add_argument("--vault", required=True, type=Path)
    ap.add_argument("--site", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    res = run(args.vault, args.site, args.dry_run)
    for w in res.warnings:
        print(f"[warn] {w}")
    if res.errors:
        for e in res.errors:
            print(f"[error] {e}", file=sys.stderr)
        print(f"\n{len(res.errors)} 個錯誤，未寫入任何檔案。", file=sys.stderr)
        return 1
    for a in res.actions:
        print(f"[{'plan' if args.dry_run else 'done'}] {a}")
    if not res.actions:
        print("沒有需要發佈或更新的筆記。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
