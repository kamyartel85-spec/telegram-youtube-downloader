# YouTube Downloader Telegram Bot

A production-ready Telegram bot that downloads YouTube videos and audio using
**yt-dlp** and sends them via **Telethon (MTProto)**, which supports files far
larger than the standard 50 MB Bot API limit.

## Features

- `/start` welcome message and `/help` usage guide
- Accepts YouTube URLs (`watch`, `youtu.be`, `shorts`, `embed`)
- Choose **Video** or **Audio** via inline buttons
- Video quality options: 360p, 480p, 720p, 1080p (MP4 when possible)
- Audio extracted to MP3 192 kbps via FFmpeg
- Large file support via MTProto upload (up to 2 GB)
- Live download progress (percentage, size, speed, ETA)
- Live upload progress
- Automatic cleanup of temporary files
- Per-user concurrent-download limiting
- Graceful error handling (private videos, age-restriction, timeouts, FloodWait, etc.)
- Health-check HTTP server for Railway
- No secrets hardcoded — everything via environment variables

## Prerequisites

- Python 3.12+
- FFmpeg (included in the Docker image)
- A Telegram bot token, API ID, and API hash

### Getting Telegram credentials

1. Go to <https://my.telegram.org> → **API Development Tools**
2. Create an application to get your **API ID** and **API Hash**.
3. Talk to [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`,
   and copy the **Bot Token**.

## Local development

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Make sure FFmpeg is installed
#    macOS:  brew install ffmpeg
#    Ubuntu: sudo apt install ffmpeg

# 3. Create your .env file
cp .env.example .env
# Edit .env and fill in BOT_TOKEN, API_ID, API_HASH

# 4. Run the bot
python main.py
```

## Deploy on Railway

1. **Push this project to a GitHub repository.**

2. Go to [Railway](https://railway.app) and click **New Project → Deploy from
   GitHub repo**. Select your repository.

3. Railway will detect the `Dockerfile` automatically and build the image
   (FFmpeg is installed inside).

4. Go to the **Variables** tab and add:
   | Variable     | Value                  |
   |--------------|------------------------|
   | `BOT_TOKEN`  | your bot token         |
   | `API_ID`     | your API ID (numbers)  |
   | `API_HASH`   | your API hash          |

   Optional variables (`DOWNLOAD_DIR`, `MAX_FILE_SIZE`, etc.) can be added
   but have sensible defaults.

5. Click **Deploy**. The bot will start automatically with `python main.py`.

6. Check the **Logs** tab to confirm the bot started. You should see:
   ```
   Bot started as @YourBotUsername
   ```

7. Open Telegram, find your bot, send `/start`, then send a YouTube URL.

## Environment variables

| Variable                  | Required | Default            | Description                         |
|---------------------------|----------|--------------------|-------------------------------------|
| `BOT_TOKEN`               | Yes      | —                  | Telegram bot token from BotFather   |
| `API_ID`                  | Yes      | —                  | Telegram API ID from my.telegram.org|
| `API_HASH`                | Yes      | —                  | Telegram API hash                   |
| `DOWNLOAD_DIR`            | No       | `/tmp/ytdl_downloads` | Temp download directory          |
| `MAX_FILE_SIZE`           | No       | `2147483648` (2 GB)| Max upload size in bytes             |
| `MAX_CONCURRENT_DOWNLOADS`| No       | `1`                | Per-user concurrent downloads        |
| `DOWNLOAD_TIMEOUT`        | No       | `600`              | Download timeout in seconds          |
| `UPLOAD_TIMEOUT`          | No       | `1800`             | Upload timeout in seconds            |
| `HEALTH_CHECK_PORT`       | No       | `8000`             | Health-check HTTP port               |
| `SESSION_NAME`            | No       | `bot_session`      | Telethon session file name           |
| `LOG_LEVEL`               | No       | `INFO`             | Logging verbosity                    |

## How it works

1. User sends a YouTube URL → bot validates it and fetches video info.
2. Bot shows the title, channel, duration, and **Video / Audio** buttons.
3. For video, the user picks a quality (360p–1080p).
4. The bot downloads via yt-dlp (FFmpeg merges streams when needed).
5. Progress is shown live by editing a single message (no spam).
6. The file is uploaded via Telethon's MTProto `send_file`, bypassing the
   50 MB Bot API limit.
7. The temporary file is deleted immediately after sending.

## Project structure

```
├── main.py          # Entry point: logging, health server, bot startup
├── config.py        # Environment variable loading
├── handlers.py      # Telegram event handlers (commands, URLs, callbacks)
├── youtube.py       # yt-dlp wrapper (info extraction, download)
├── progress.py      # Download & upload progress trackers
├── utils.py         # URL validation, formatting, file cleanup
├── requirements.txt # Python dependencies
├── Dockerfile       # Docker image with FFmpeg
├── railway.json     # Railway deployment config
├── .env.example     # Example environment variables
├── .gitignore       # Ignores .env, sessions, downloads, cache
└── .dockerignore    # Excludes non-essential files from Docker build
```

## Notes

- Only public YouTube videos are supported. Private, age-restricted, or
  removed videos will produce a friendly error message.
- The bot uses a Telethon session file (`bot_session.session`) to persist
  its auth key. On Railway this file is ephemeral and is recreated on each
  deploy — this is normal and harmless.
- Files are sent via MTProto, not the HTTP Bot API, so the 50 MB limit does
  not apply. The practical limit is 2 GB (Telegram's MTProto cap for bots).
