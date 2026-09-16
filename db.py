"""SQLite database layer for the YouTube downloader bot.

All functions are synchronous — call them from async code via
``asyncio.to_thread(...)``.
"""

import os
import sqlite3
import logging
from datetime import datetime, timezone

from config import DB_PATH, OWNER_ID

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Connection helper
# ----------------------------------------------------------------------
def _connect():
    """Return a sqlite3 connection with row objects enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ----------------------------------------------------------------------
# Schema
# ----------------------------------------------------------------------
_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id            INTEGER PRIMARY KEY,
    username           TEXT,
    language           TEXT DEFAULT 'fa',
    joined_at          TEXT,
    is_banned          INTEGER DEFAULT 0,
    referred_by        INTEGER,
    bonus_downloads    INTEGER DEFAULT 0,
    custom_daily_limit INTEGER
);

CREATE TABLE IF NOT EXISTS downloads (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    url        TEXT,
    title      TEXT,
    media_type TEXT,
    quality    TEXT,
    file_size  INTEGER,
    status     TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS cache (
    video_id        TEXT,
    quality         TEXT,
    media_type      TEXT,
    telegram_file_id TEXT,
    file_size       INTEGER,
    created_at      TEXT,
    PRIMARY KEY (video_id, quality, media_type)
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY,
    role    TEXT
);

CREATE TABLE IF NOT EXISTS error_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER,
    url           TEXT,
    error_message TEXT,
    created_at    TEXT
);
"""


def initialize_database():
    """Create all tables and seed the owner admin if OWNER_ID is set."""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = _connect()
    try:
        conn.executescript(_SCHEMA)
        conn.commit()

        if OWNER_ID:
            existing = conn.execute(
                "SELECT 1 FROM admins WHERE user_id = ?", (OWNER_ID,)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO admins (user_id, role) VALUES (?, 'owner')",
                    (OWNER_ID,),
                )
                conn.commit()
                logger.info("Owner admin seeded: user_id=%s", OWNER_ID)
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Users
# ----------------------------------------------------------------------
def get_user(user_id):
    """Return a dict for the given user or None."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_user(user_id, username=None, referred_by=None, language="fa"):
    """Insert a new user and return the row as a dict."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO users (user_id, username, language, joined_at, referred_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, username, language, now, referred_by),
        )
        conn.commit()
    finally:
        conn.close()
    return get_user(user_id)


def update_user(user_id, **fields):
    """Update one or more columns on an existing user.

    Example: ``update_user(123, language='en', is_banned=1)``
    """
    if not fields:
        return
    allowed = {
        "username", "language", "is_banned", "referred_by",
        "bonus_downloads", "custom_daily_limit",
    }
    columns = []
    values = []
    for key, value in fields.items():
        if key in allowed:
            columns.append(f"{key} = ?")
            values.append(value)
    if not columns:
        return
    values.append(user_id)
    conn = _connect()
    try:
        conn.execute(
            f"UPDATE users SET {', '.join(columns)} WHERE user_id = ?",
            values,
        )
        conn.commit()
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Settings (key-value)
# ----------------------------------------------------------------------
def get_setting(key, default=None):
    """Return the value for *key* or *default*."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()


def set_setting(key, value):
    """Insert or update a setting."""
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value)),
        )
        conn.commit()
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Downloads
# ----------------------------------------------------------------------
def add_download(user_id, url, title, media_type, quality, file_size=None, status="pending"):
    """Insert a download record and return its id."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO downloads
                (user_id, url, title, media_type, quality, file_size, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, url, title, media_type, quality, file_size, status, now),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_downloads(user_id, limit=20):
    """Return the most recent downloads for *user_id* as a list of dicts."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM downloads WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Cache (Telegram file-id reuse)
# ----------------------------------------------------------------------
def get_cache(video_id, quality, media_type):
    """Return a cached file record or None."""
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT * FROM cache
            WHERE video_id = ? AND quality = ? AND media_type = ?
            """,
            (video_id, quality, media_type),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def set_cache(video_id, quality, media_type, telegram_file_id, file_size=None):
    """Insert or replace a cache entry."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO cache (video_id, quality, media_type, telegram_file_id, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(video_id, quality, media_type) DO UPDATE SET
                telegram_file_id = excluded.telegram_file_id,
                file_size       = excluded.file_size,
                created_at      = excluded.created_at
            """,
            (video_id, quality, media_type, telegram_file_id, file_size, now),
        )
        conn.commit()
    finally:
        conn.close()


def clear_cache():
    """Delete every row in the cache table."""
    conn = _connect()
    try:
        conn.execute("DELETE FROM cache")
        conn.commit()
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Error logs
# ----------------------------------------------------------------------
def add_error_log(user_id, url, error_message):
    """Record an error in the error_logs table."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO error_logs (user_id, url, error_message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, url, error_message, now),
        )
        conn.commit()
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Admins
# ----------------------------------------------------------------------
def get_admin(user_id):
    """Return {'user_id': …, 'role': …} or None."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM admins WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def add_admin(user_id, role):
    """Insert or update an admin role."""
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO admins (user_id, role) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET role = excluded.role",
            (user_id, role),
        )
        conn.commit()
    finally:
        conn.close()


def remove_admin(user_id):
    """Remove an admin.  The owner cannot be removed."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT role FROM admins WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row and row["role"] == "owner":
            return False
        conn.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    finally:
        conn.close()
