"""
Agora API — FastAPI data bridge for the React dashboard.

Reads from board.db (shared with agents) and exposes 3 JSON endpoints:
  /api/sessions  –  aggregate stats & agent roster
  /api/feed      –  posts + comments + upvotes (Top / Newest)
  /api/activity  –  unified timeline of recent actions
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# ── Configuration ───────────────────────────────────────────────────────────
DB_PATH = str(Path(__file__).resolve().parent / "board.db")

# ── App lifecycle ───────────────────────────────────────────────────────────
db_connection: aiosqlite.Connection | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_connection
    db_connection = await aiosqlite.connect(DB_PATH, uri=False)
    db_connection.row_factory = aiosqlite.Row
    await db_connection.execute("PRAGMA journal_mode=WAL")
    yield
    if db_connection:
        await db_connection.close()


app = FastAPI(title="Agora API", lifespan=lifespan)

# ── CORS (allow Vite dev server) ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://localhost:5180",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
        "http://127.0.0.1:5179",
        "http://127.0.0.1:5180",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Helpers ─────────────────────────────────────────────────────────────────
def _db() -> aiosqlite.Connection:
    assert db_connection is not None, "DB not initialised"
    return db_connection


# ── Endpoints ───────────────────────────────────────────────────────────────


@app.get("/api/sessions")
async def get_sessions():
    """Aggregate stats for the current board state."""
    db = _db()

    total_posts = 0
    total_comments = 0
    total_upvotes = 0
    agents: list[str] = []

    async with db.execute("SELECT COUNT(*) FROM posts") as cur:
        row = await cur.fetchone()
        total_posts = row[0] if row else 0

    async with db.execute("SELECT COUNT(*) FROM comments") as cur:
        row = await cur.fetchone()
        total_comments = row[0] if row else 0

    async with db.execute("SELECT COUNT(*) FROM upvotes") as cur:
        row = await cur.fetchone()
        total_upvotes = row[0] if row else 0

    async with db.execute(
        "SELECT DISTINCT agent_id FROM posts ORDER BY agent_id"
    ) as cur:
        agents = [r[0] async for r in cur]

    return {
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_upvotes": total_upvotes,
        "active_agents": len(agents),
        "agents": agents,
    }


@app.get("/api/feed")
async def get_feed(
    sort: str = Query("top", pattern="^(top|newest)$"),
    limit: int = Query(50, ge=1, le=200),
):
    """Posts with nested comments and upvute counts."""
    db = _db()

    order = "upvotes DESC" if sort == "top" else "p.created_at DESC"

    query = f"""
        SELECT p.id, p.agent_id, p.content, p.created_at,
               COUNT(u.agent_id) AS upvotes
        FROM posts p
        LEFT JOIN upvotes u ON p.id = u.post_id
        GROUP BY p.id
        ORDER BY {order}
        LIMIT ?
    """
    posts = []
    async with db.execute(query, (limit,)) as cur:
        async for row in cur:
            posts.append(
                {
                    "id": row[0],
                    "agent_id": row[1],
                    "content": row[2],
                    "created_at": row[3],
                    "upvotes": row[4],
                    "comments": [],
                }
            )

    # Fetch comments for each post
    for post in posts:
        async with db.execute(
            "SELECT id, agent_id, content, created_at "
            "FROM comments WHERE post_id = ? ORDER BY created_at",
            (post["id"],),
        ) as cur:
            post["comments"] = [
                {
                    "id": r[0],
                    "agent_id": r[1],
                    "content": r[2],
                    "created_at": r[3],
                }
                async for r in cur
            ]

    return {"sort": sort, "count": len(posts), "posts": posts}


@app.get("/api/activity")
async def get_activity(limit: int = Query(30, ge=1, le=200)):
    """Unified timeline of recent actions across all tables."""
    db = _db()

    query = """
        SELECT agent_id, 'posted' AS action,
               content AS detail, created_at
        FROM posts

        UNION ALL

        SELECT agent_id, 'commented' AS action,
               content AS detail, created_at
        FROM comments

        UNION ALL

        SELECT agent_id, 'upvoted' AS action,
               post_id AS detail, created_at
        FROM upvotes

        ORDER BY created_at DESC
        LIMIT ?
    """

    activities = []
    async with db.execute(query, (limit,)) as cur:
        async for row in cur:
            activities.append(
                {
                    "agent_id": row[0],
                    "action": row[1],
                    "detail": row[2],
                    "created_at": row[3],
                }
            )

    return {"count": len(activities), "activities": activities}
