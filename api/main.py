"""shaoyong.dev 瀏覽統計 API。

設計文件：docs/design/views-api.md。只存 slug 與次數，不碰任何個資。
"""

import os
import re
import sqlite3
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = os.environ.get("VIEWS_DB", "/data/views.db")
ALLOWED_ORIGIN = os.environ.get("VIEWS_ORIGIN", "https://shaoyong.dev")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

_write_lock = threading.Lock()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@asynccontextmanager
async def lifespan(_app: FastAPI):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS views ("
            "slug TEXT PRIMARY KEY,"
            "count INTEGER NOT NULL DEFAULT 0,"
            "updated TEXT)"
        )
    yield


app = FastAPI(title="shaoyong.dev views API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "POST"],
    allow_headers=[],
)


def validate_slug(slug: str) -> None:
    if len(slug) > 100 or not SLUG_RE.match(slug):
        raise HTTPException(status_code=400, detail="invalid slug")


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/views/{slug}")
def get_views(slug: str):
    validate_slug(slug)
    with connect() as conn:
        row = conn.execute("SELECT count FROM views WHERE slug = ?", (slug,)).fetchone()
    return {"slug": slug, "views": row[0] if row else 0}


@app.post("/views/{slug}")
def add_view(slug: str):
    validate_slug(slug)
    with _write_lock, connect() as conn:
        conn.execute(
            "INSERT INTO views (slug, count, updated) VALUES (?, 1, datetime('now')) "
            "ON CONFLICT(slug) DO UPDATE SET count = count + 1, updated = datetime('now')",
            (slug,),
        )
        row = conn.execute("SELECT count FROM views WHERE slug = ?", (slug,)).fetchone()
    return {"slug": slug, "views": row[0]}
