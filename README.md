# YouTube Downloader Telegram Bot with Complete Admin Panel & SQLite

A production-ready Telegram bot that downloads YouTube videos and audio playlists using
**yt-dlp** and delivers them via **Telethon (MTProto)**, bypassing the standard 50 MB Bot API limit (up to 2 GB).

Includes a complete in-bot Telegram Admin Panel with reply-keyboards, SQLite storage, fast Telegram-file caching, forced channel join, multi-language support (FA / EN / RU), referral system, rate limiting, and error logging.

## Core Features

- **Multi-Language Support (i18n):** Persian (فارسی), English, and Russian (Русский).
- **Interactive Onboarding:**
  - Forced Channel Join verification (configurable from admin panel).
  - Language selection dialog.
  - Welcoming onboarding flow and rich reply keyboard.
- **Main Menu (Reply Keyboard):**
  - 🔍 **YouTube Search / Link Input**
  - 👤 **My Account:** Real-time statistics (user ID, total downloads, downloads today, remaining quota).
  - 🚀 **Free Traffic:** Referral link generator (`https://t.me/BOT?start=ref_<id>`) granting bonus downloads.
  - ☎️ **Support:** Dynamic support username contact.
  - 🌐 **Change Language:** Instant switch between FA, EN, and RU.
  - 🍿 **Download Guide:** Comprehensive walkthrough on copying and downloading links.
  - 📢 **Information Channel:** Direct channel link.
- **Rich Media Extraction & Formats:**
  - Thumbnail preview with title, duration, channel, views, comments, and release date.
  - Formats: MP3 Medium (128k), MP3 Best (320k), and video resolutions (144p, 240p, 360p, 480p, 720p, 1080p) with approximate file sizes.
  - Sequential Playlist download & delivery with progress status.
- **Fast Telegram File Caching:** Instant delivery for previously downloaded media via Telegram `file_id`.
- **Download Quotas & Limits:** Daily limits, custom user overrides, and referral bonuses.
- **Channels Integration:** Automatic forwarding of completed media to Download Log channel and unexpected errors to Error Log channel.
- **Failure Recovery & Problem Reporting:** Under every file, users can click `⚠️ گزارش مشکل` or retry interrupted downloads.
- **Rate Limiting:** Protects against flooding and spam (default: 5 requests/min).
- **Maintenance Mode:** Instant global maintenance switch for user-facing maintenance.
- **Full In-Bot Admin Panel (`/admin`):**
  - 📊 **Bot Analytics:** Total users, active users today/month, total traffic, and download metrics.
  - 👥 **User Management:** Search user, ban/unban, adjust custom limits, grant bonus downloads, export CSV.
  - 📢 **Targeted Broadcast:** Broadcast message to users active within the last N months.
  - ⚙️ **Bot Settings:** Toggle forced join, set daily limits, edit referral rewards, channels, and logs.
  - 💬 **Live Text Customization:** Edit and override bot text strings in any language live from Telegram.
  - 🗂 **Cache Management:** View cache size and clear cache.
  - 🧾 **Error Logs:** View recent system error logs.
  - 👮 **Admin Roles:** Manage admin users (`owner`, `full`, `viewer`).
  - 🔧 **Maintenance Toggle:** Turn maintenance mode on/off.

---

## Project Structure

```
├── main.py             # Entry point: logging, health-check server, startup
├── config.py           # Configuration loaded from environment variables
├── db.py               # SQLite layer: users, downloads, cache, settings, admins, errors
├── i18n.py             # Translations bundle (FA, EN, RU) & dynamic database overrides
├── keyboards.py        # Reply and inline keyboards for user menus & admin panel
├── handlers.py         # Main user workflows, links, callbacks, caching & download flows
├── admin_handlers.py   # Admin commands, reply keyboard navigation, and settings
├── youtube.py          # yt-dlp wrapper (info, playlist extraction, format sizing, downloading)
├── progress.py         # Alternating friendly status messages (no cluttered percentages)
├── utils.py            # URL validation, formatting, duration, and file cleanup
├── requirements.txt    # Python dependencies
├── Dockerfile          # Production Docker container with FFmpeg
├── railway.json        # Railway deployment configuration
└── .env.example        # Environment variables documentation
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | Yes | — | Telegram Bot token from @BotFather |
| `API_ID` | Yes | — | Telegram API ID from my.telegram.org |
| `API_HASH` | Yes | — | Telegram API Hash from my.telegram.org |
| `OWNER_ID` | Yes/Recommended | `0` | Telegram numeric user ID of owner (auto-seeded with owner role) |
| `DB_PATH` | No | `/tmp/ytdl_bot/bot.db` | Path to SQLite database file |
| `DOWNLOAD_DIR` | No | `/tmp/ytdl_downloads` | Temporary download directory |
| `MAX_FILE_SIZE` | No | `2147483648` (2 GB) | Maximum file size allowed for upload |
| `MAX_PLAYLIST_ITEMS` | No | `25` | Max playlist videos processed per request |
| `RATE_LIMIT_PER_MINUTE` | No | `5` | Max messages/requests allowed per user per minute |
| `DEFAULT_DAILY_LIMIT` | No | `10` | Default daily downloads limit per user |
| `DEFAULT_REFERRAL_BONUS` | No | `3` | Default bonus downloads per successful referral |
| `DOWNLOAD_LOG_CHANNEL_ID` | No | `""` | Telegram Channel ID to forward completed media to |
| `ERROR_LOG_CHANNEL_ID` | No | `""` | Telegram Channel ID to forward error logs to |
| `HEALTH_CHECK_PORT` | No | `8000` | HTTP health-check port for deployment |
| `SESSION_NAME` | No | `bot_session` | Telethon session name |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Quick Start (Local & Container)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Fill in BOT_TOKEN, API_ID, API_HASH, OWNER_ID

# 3. Start bot
python main.py
```
