import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "deeplearn.db")

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    picture TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_SUBSCRIPTIONS = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    polar_subscription_id TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
)
"""

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_SUBSCRIPTIONS)
        await db.commit()
