"""Configuration loaded from environment variables."""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

try:
    API_ID = int(os.environ.get("API_ID", "0"))
except ValueError:
    API_ID = 0

API_HASH = os.environ.get("API_HASH", "")

DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "/tmp/ytdl_downloads")

try:
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", str(2 * 1024 * 1024 * 1024)))
except ValueError:
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024

try:
    MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", "1"))
except ValueError:
    MAX_CONCURRENT_DOWNLOADS = 1

try:
    DOWNLOAD_TIMEOUT = int(os.environ.get("DOWNLOAD_TIMEOUT", "600"))
except ValueError:
    DOWNLOAD_TIMEOUT = 600

try:
    UPLOAD_TIMEOUT = int(os.environ.get("UPLOAD_TIMEOUT", "1800"))
except ValueError:
    UPLOAD_TIMEOUT = 1800

HEALTH_CHECK_PORT = int(os.environ.get("PORT", os.environ.get("HEALTH_CHECK_PORT", "8000")))

SESSION_NAME = os.environ.get("SESSION_NAME", "bot_session")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Persistent database path (prevents data reset on restarts/updates)
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.getcwd(), "data", "bot.db"))

def _parse_id(val: str) -> int:
    clean = val.strip().strip('"').strip("'").lstrip("@")
    try:
        return int(clean)
    except (ValueError, TypeError):
        return 0

raw_owner = os.environ.get("OWNER_ID", "")
OWNER_ID = _parse_id(raw_owner)

# Support comma-separated extra admins if defined: ADMIN_IDS="123,456"
ADMIN_IDS = set()
if OWNER_ID:
    ADMIN_IDS.add(OWNER_ID)
raw_admins = os.environ.get("ADMIN_IDS", "")
if raw_admins:
    for item in raw_admins.split(","):
        parsed = _parse_id(item)
        if parsed:
            ADMIN_IDS.add(parsed)

try:
    MAX_PLAYLIST_ITEMS = int(os.environ.get("MAX_PLAYLIST_ITEMS", "25"))
except ValueError:
    MAX_PLAYLIST_ITEMS = 25

try:
    RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "5"))
except ValueError:
    RATE_LIMIT_PER_MINUTE = 5

try:
    DEFAULT_DAILY_LIMIT = int(os.environ.get("DEFAULT_DAILY_LIMIT", "10"))
except ValueError:
    DEFAULT_DAILY_LIMIT = 10

try:
    DEFAULT_REFERRAL_BONUS = int(os.environ.get("DEFAULT_REFERRAL_BONUS", "3"))
except ValueError:
    DEFAULT_REFERRAL_BONUS = 3
