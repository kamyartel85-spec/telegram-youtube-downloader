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

        # Seed default settings if not present
        default_settings = {
            "force_join_enabled": "0",
            "force_join_channels": "[]",
            "daily_limit_enabled": "1",
            "daily_limit_count": "10",
            "referral_bonus": "3",
            "support_id": "@SupportBot",
            "channel_link": "https://t.me/MyChannel",
            "download_log_channel_id": "",
            "error_log_channel_id": "",
            "max_playlist_items": "25",
            "maintenance_mode": "0",
        }
        for k, v in default_settings.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (k, v),
            )
        conn.commit()
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


def delete_cache(video_id, quality, media_type):
    """Delete a specific cache record."""
    conn = _connect()
    try:
        conn.execute(
            "DELETE FROM cache WHERE video_id = ? AND quality = ? AND media_type = ?",
            (video_id, quality, media_type),
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


def get_all_admins():
    """Return all admins as a list of dicts."""
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM admins ORDER BY role DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Extended Settings & Text Customization
# ----------------------------------------------------------------------
def get_all_settings():
    """Return all settings as a dict."""
    conn = _connect()
    try:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        return {r["key"]: r["value"] for r in rows}
    finally:
        conn.close()


def get_custom_text(key, lang):
    """Return overridden text for (key, lang) or None."""
    return get_setting(f"text_{lang}_{key}", None)


def set_custom_text(key, lang, text):
    """Override a localized text string."""
    set_setting(f"text_{lang}_{key}", text)


# ----------------------------------------------------------------------
# Statistics & Analytics
# ----------------------------------------------------------------------
def get_user_count():
    """Total registered users."""
    conn = _connect()
    try:
        row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def get_active_users_today():
    """Count of users who downloaded something today (UTC)."""
    today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT COUNT(DISTINCT user_id) AS count FROM downloads WHERE created_at LIKE ?",
            (f"{today_prefix}%",),
        ).fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def get_active_users_month():
    """Count of users who downloaded something this month (UTC)."""
    month_prefix = datetime.now(timezone.utc).strftime("%Y-%m")
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT COUNT(DISTINCT user_id) AS count FROM downloads WHERE created_at LIKE ?",
            (f"{month_prefix}%",),
        ).fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def get_growth_stats():
    """Calculate comparisons and statistics."""
    conn = _connect()
    try:
        total_users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
        total_downloads = conn.execute("SELECT COUNT(*) as c FROM downloads").fetchone()["c"]
        total_failed = conn.execute("SELECT COUNT(*) as c FROM downloads WHERE status = 'failed'").fetchone()["c"]
        
        # Today vs Yesterday
        today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        dl_today = conn.execute("SELECT COUNT(*) as c FROM downloads WHERE created_at LIKE ?", (f"{today_prefix}%",)).fetchone()["c"]
        
        # Total size downloaded (bytes)
        size_row = conn.execute("SELECT SUM(file_size) as s FROM downloads WHERE file_size IS NOT NULL").fetchone()
        total_bytes = size_row["s"] if size_row and size_row["s"] else 0

        return {
            "total_users": total_users,
            "total_downloads": total_downloads,
            "failed_downloads": total_failed,
            "downloads_today": dl_today,
            "active_users_today": get_active_users_today(),
            "active_users_month": get_active_users_month(),
            "total_bytes": total_bytes,
        }
    finally:
        conn.close()


# ----------------------------------------------------------------------
# User Management Helpers
# ----------------------------------------------------------------------
def search_users(query, limit=20):
    """Search users by user_id or username."""
    conn = _connect()
    try:
        q = f"%{query}%"
        rows = conn.execute(
            """
            SELECT * FROM users
            WHERE CAST(user_id AS TEXT) LIKE ? OR username LIKE ?
            ORDER BY user_id DESC LIMIT ?
            """,
            (q, q, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def export_users_csv():
    """Generate CSV string of all users."""
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM users ORDER BY user_id DESC").fetchall()
        lines = [
            "user_id,username,language,joined_at,is_banned,referred_by,bonus_downloads,custom_daily_limit"
        ]
        for r in rows:
            u = dict(r)
            line = f"{u.get('user_id')},{u.get('username') or ''},{u.get('language') or 'fa'},{u.get('joined_at') or ''},{u.get('is_banned') or 0},{u.get('referred_by') or ''},{u.get('bonus_downloads') or 0},{u.get('custom_daily_limit') or ''}"
            lines.append(line)
        return "\n".join(lines)
    finally:
        conn.close()


def get_active_users_since(months=3):
    """Return list of distinct user_ids active within the last *months* months."""
    conn = _connect()
    try:
        # Approximate 30 days per month
        rows = conn.execute(
            """
            SELECT DISTINCT user_id FROM downloads
            WHERE created_at >= datetime('now', '-' || ? || ' month')
            UNION
            SELECT user_id FROM users
            WHERE joined_at >= datetime('now', '-' || ? || ' month')
            """,
            (months, months),
        ).fetchall()
        return [r["user_id"] for r in rows if r["user_id"]]
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Cache Stats & Error Log Inspection
# ----------------------------------------------------------------------
def get_cache_stats():
    """Return count of cached items and sum of file sizes."""
    conn = _connect()
    try:
        count_row = conn.execute("SELECT COUNT(*) AS c FROM cache").fetchone()
        size_row = conn.execute("SELECT SUM(file_size) AS s FROM cache WHERE file_size IS NOT NULL").fetchone()
        count = count_row["c"] if count_row else 0
        total_size = size_row["s"] if size_row and size_row["s"] else 0
        return {"count": count, "total_size": total_size}
    finally:
        conn.close()


def get_recent_errors(limit=20):
    """Return the most recent error logs."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM error_logs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
