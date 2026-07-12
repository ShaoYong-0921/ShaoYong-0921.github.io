"""views API 單元測試（docs/design/views-api.md 的每條規則對應一測項）。"""

import os
import tempfile
import unittest

os.environ["VIEWS_DB"] = os.path.join(tempfile.mkdtemp(), "test-views.db")

from fastapi.testclient import TestClient

import main


class TestViewsApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def test_healthz(self):
        r = self.client.get("/healthz")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True})

    def test_unknown_slug_reads_zero(self):
        r = self.client.get("/views/never-seen")
        self.assertEqual(r.json()["views"], 0)

    def test_post_increments(self):
        first = self.client.post("/views/post-test").json()["views"]
        second = self.client.post("/views/post-test").json()["views"]
        self.assertEqual(second, first + 1)

    def test_get_does_not_increment(self):
        n = self.client.post("/views/read-only").json()["views"]
        self.client.get("/views/read-only")
        self.client.get("/views/read-only")
        self.assertEqual(self.client.get("/views/read-only").json()["views"], n)

    def test_invalid_slug_rejected(self):
        for bad in ("UPPER", "中文", "has_underscore", "a--b", "-lead", "x" * 101):
            r = self.client.post(f"/views/{bad}")
            self.assertEqual(r.status_code, 400, bad)

    def test_counts_isolated_per_slug(self):
        self.client.post("/views/alpha")
        self.assertEqual(self.client.get("/views/beta").json()["views"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
