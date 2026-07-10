"""convert.py 單元測試——每條轉換規則對應至少一個測項（docs/design/conversion-rules.md）。"""

import json
import tempfile
import unittest
from pathlib import Path

import convert

PUBLISH_FM = """---
publish: true
slug: {slug}
title: 測試文
published: 2026-07-09
---
"""


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.vault = root / "vault"
        self.site = root / "site"
        for d in ("notes", "garden", "attachments"):
            (self.vault / d).mkdir(parents=True)
        (self.site / "src" / "content" / "posts").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def note(self, name: str, content: str, folder: str = "notes"):
        p = self.vault / folder / f"{name}.md"
        p.write_text(content, encoding="utf-8")
        return p

    def published(self, name: str, slug: str, body: str = "內文。", folder: str = "notes"):
        return self.note(name, PUBLISH_FM.format(slug=slug) + body, folder)

    def run_conv(self, dry_run: bool = False):
        return convert.run(self.vault, self.site, dry_run)

    def out(self, slug: str) -> str:
        return (self.site / "src" / "content" / "posts" / slug / "index.md").read_text(encoding="utf-8")

    def assert_error(self, res, kind: str):
        self.assertTrue(any(f": {kind}:" in e for e in res.errors), res.errors)


class TestFiltering(Base):
    def test_no_front_matter_skipped(self):
        self.note("日記", "今天很累。")
        res = self.run_conv()
        self.assertEqual(res.errors, [])
        self.assertEqual(res.actions, [])

    def test_publish_false_skipped(self):
        self.note("草稿", "---\npublish: false\n---\n內容")
        res = self.run_conv()
        self.assertEqual(res.actions, [])

    def test_garden_folder_scanned(self):
        self.published("園子", "garden-note", folder="garden")
        res = self.run_conv()
        self.assertEqual(res.errors, [])
        self.assertIn("測試文", self.out("garden-note"))


class TestValidation(Base):
    def test_missing_slug_blocks(self):
        self.note("沒slug", "---\npublish: true\npublished: 2026-07-09\n---\nx")
        self.assert_error(self.run_conv(), "slug")

    def test_bad_slug_format_blocks(self):
        self.note("壞slug", "---\npublish: true\nslug: Bad_Slug\npublished: 2026-07-09\n---\nx")
        self.assert_error(self.run_conv(), "slug")

    def test_duplicate_slug_blocks(self):
        self.published("甲", "same-slug")
        self.published("乙", "same-slug")
        self.assert_error(self.run_conv(), "slug")

    def test_missing_published_blocks(self):
        self.note("沒日期", "---\npublish: true\nslug: no-date\n---\nx")
        self.assert_error(self.run_conv(), "published")

    def test_collision_with_manual_post_blocks(self):
        (self.site / "src" / "content" / "posts" / "manual.md").write_text("手寫文章", encoding="utf-8")
        self.published("撞名", "manual")
        self.assert_error(self.run_conv(), "slug")

    def test_error_blocks_all_writes(self):
        self.published("好筆記", "good-note")
        self.note("壞筆記", "---\npublish: true\npublished: 2026-07-09\n---\nx")
        res = self.run_conv()
        self.assertTrue(res.errors)
        self.assertFalse((self.site / "src" / "content" / "posts" / "good-note").exists())


class TestWikiLinks(Base):
    def test_link_to_published(self):
        self.published("目標", "target-post")
        self.published("來源", "src-post", body="見 [[目標]]。")
        res = self.run_conv()
        self.assertEqual(res.errors, [])
        self.assertIn("[目標](/posts/target-post/)", self.out("src-post"))

    def test_link_with_alias(self):
        self.published("目標", "target-post")
        self.published("來源", "src-post", body="見 [[目標|這篇]]。")
        self.run_conv()
        self.assertIn("[這篇](/posts/target-post/)", self.out("src-post"))

    def test_link_to_unpublished_blocks(self):
        self.note("私密", "私密內容")
        self.published("來源", "src-post", body="見 [[私密]]。")
        self.assert_error(self.run_conv(), "wiki-link")

    def test_heading_link_blocks(self):
        self.published("目標", "target-post")
        self.published("來源", "src-post", body="見 [[目標#小節]]。")
        self.assert_error(self.run_conv(), "unsupported")

    def test_code_fence_untouched(self):
        self.published("來源", "src-post", body="```\n[[不是連結]]\n```\n以及 `[[也不是]]`。")
        res = self.run_conv()
        self.assertEqual(res.errors, [])
        self.assertIn("[[不是連結]]", self.out("src-post"))
        self.assertIn("`[[也不是]]`", self.out("src-post"))

    def test_dataview_blocks(self):
        self.published("來源", "src-post", body="```dataview\nlist\n```")
        self.assert_error(self.run_conv(), "unsupported")


class TestEmbeds(Base):
    def test_image_embed_copied(self):
        (self.vault / "attachments" / "圖.png").write_bytes(b"png")
        self.published("來源", "src-post", body="看圖 ![[圖.png]]")
        res = self.run_conv()
        self.assertEqual(res.errors, [])
        self.assertIn("![](./圖.png)", self.out("src-post"))
        self.assertTrue((self.site / "src" / "content" / "posts" / "src-post" / "圖.png").exists())

    def test_missing_attachment_blocks(self):
        self.published("來源", "src-post", body="![[不存在.png]]")
        self.assert_error(self.run_conv(), "attachment")

    def test_note_embed_blocks(self):
        self.published("目標", "target-post")
        self.published("來源", "src-post", body="![[目標]]")
        self.assert_error(self.run_conv(), "unsupported")

    def test_image_front_matter_field(self):
        (self.vault / "attachments" / "cover.png").write_bytes(b"png")
        self.note(
            "封面文",
            "---\npublish: true\nslug: cover-post\npublished: 2026-07-09\nimage: \"[[cover.png]]\"\n---\n內文",
        )
        res = self.run_conv()
        self.assertEqual(res.errors, [])
        self.assertIn("image: ./cover.png", self.out("cover-post"))


class TestLifecycle(Base):
    def test_unpublish_deletes_managed_post(self):
        self.published("甲", "post-a")
        self.run_conv()
        self.assertTrue((self.site / "src" / "content" / "posts" / "post-a").exists())
        (self.vault / "notes" / "甲.md").unlink()
        res = self.run_conv()
        self.assertEqual(res.errors, [])
        self.assertFalse((self.site / "src" / "content" / "posts" / "post-a").exists())
        manifest = json.loads((self.site / convert.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertEqual(manifest["slugs"], [])

    def test_manual_post_never_deleted(self):
        manual = self.site / "src" / "content" / "posts" / "hand" / "index.md"
        manual.parent.mkdir(parents=True)
        manual.write_text("手寫，無標記", encoding="utf-8")
        (self.site / convert.MANIFEST_NAME).write_text('{"slugs": ["hand"]}', encoding="utf-8")
        res = self.run_conv()
        self.assertEqual(res.errors, [])
        self.assertTrue(manual.exists())

    def test_dry_run_writes_nothing(self):
        self.published("甲", "post-a")
        res = self.run_conv(dry_run=True)
        self.assertTrue(res.actions)
        self.assertFalse((self.site / "src" / "content" / "posts" / "post-a").exists())

    def test_output_contains_marker_and_defaults(self):
        self.published("甲", "post-a")
        self.run_conv()
        out = self.out("post-a")
        self.assertIn(convert.MARKER, out)
        self.assertIn("lang: zh_TW", out)
        self.assertIn("published: 2026-07-09", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
