"""Telegram event handlers for the YouTube downloader bot."""

import asyncio
import uuid
import os
import logging

from telethon import events, Button
from telethon.errors import FloodWaitError

from config import (
    DOWNLOAD_DIR,
    MAX_FILE_SIZE,
    MAX_CONCURRENT_DOWNLOADS,
    DOWNLOAD_TIMEOUT,
    UPLOAD_TIMEOUT,
)
from utils import is_valid_youtube_url, format_size, format_duration, cleanup_files
from youtube import extract_info, download_video, download_audio
from progress import DownloadProgressTracker, UploadProgressTracker

logger = logging.getLogger(__name__)

# download_id → {url, title, user_id}
_pending: dict = {}
# user_id → number of active downloads
_active_counts: dict = {}


def register_handlers(client):
    """Attach all command, message, and callback handlers to *client*."""

    @client.on(events.NewMessage(pattern=r"^/start(@\w+)?$"))
    async def _start(event):
        await event.respond(
            "**YouTube Downloader Bot**\n\n"
            "Send me a YouTube video link and I'll download it for you.\n\n"
            "Use /help for detailed instructions."
        )

    @client.on(events.NewMessage(pattern=r"^/help(@\w+)?$"))
    async def _help(event):
        await event.respond(
            "**How to use this bot**\n\n"
            "1. Send a YouTube video URL\n"
            "2. Choose **Video** or **Audio**\n"
            "3. For video, pick a quality (360p – 1080p)\n"
            "4. Wait for the download and upload to finish\n"
            "5. The file is sent directly in this chat\n\n"
            "**Commands**\n"
            "/start — welcome message\n"
            "/help — this help text\n\n"
            "**Notes**\n"
            "- Only public YouTube videos are supported\n"
            "- Files are sent via MTProto, so large files work too\n"
            "- Downloaded files are deleted immediately after sending"
        )

    @client.on(
        events.NewMessage(
            incoming=True,
            func=lambda e: is_valid_youtube_url(e.raw_text.strip()),
        )
    )
    async def _url(event):
        url = event.raw_text.strip()

        if _active_counts.get(event.sender_id, 0) >= MAX_CONCURRENT_DOWNLOADS:
            await event.respond(
                "You already have a download in progress. "
                "Please wait for it to finish before sending another URL."
            )
            return

        status = await event.respond("Fetching video info…")

        try:
            info = await asyncio.wait_for(
                asyncio.to_thread(extract_info, url),
                timeout=30,
            )
        except asyncio.TimeoutError:
            await status.edit("Fetching video info timed out. Please try again.")
            return
        except Exception:
            logger.exception("extract_info failed for %s", url)
            await status.edit(
                "Could not fetch video info. The video might be private, "
                "age-restricted, or unavailable."
            )
            return

        title = info.get("title", "Unknown")
        duration = info.get("duration", 0)
        uploader = info.get("uploader", "Unknown")

        download_id = uuid.uuid4().hex[:8]
        _pending[download_id] = {
            "url": url,
            "title": title,
            "user_id": event.sender_id,
        }

        text = (
            f"**{title}**\n\n"
            f"Channel: {uploader}\n"
            f"Duration: {format_duration(duration)}\n\n"
            f"Choose a format:"
        )
        buttons = [
            [
                Button.inline("Video", data=f"v:{download_id}"),
                Button.inline("Audio", data=f"a:{download_id}"),
            ]
        ]
        await status.edit(text, buttons=buttons)

    @client.on(events.CallbackQuery())
    async def _callback(event):
        try:
            data = event.data.decode("utf-8")
            parts = data.split(":")
            action = parts[0]
            download_id = parts[1]
        except (UnicodeDecodeError, IndexError):
            return

        entry = _pending.get(download_id)
        if entry is None:
            await event.answer("This selection has expired. Send the URL again.")
            return

        if entry["user_id"] != event.sender_id:
            await event.answer("This isn't your request.")
            return

        if action == "v":
            await event.answer()
            buttons = [
                [
                    Button.inline("360p", data=f"q:{download_id}:360"),
                    Button.inline("480p", data=f"q:{download_id}:480"),
                    Button.inline("720p", data=f"q:{download_id}:720"),
                    Button.inline("1080p", data=f"q:{download_id}:1080"),
                ]
            ]
            await event.edit("Select video quality:", buttons=buttons)

        elif action == "a":
            await event.answer()
            await _process_download(event, download_id, "audio", None)

        elif action == "q":
            quality = parts[2]
            await event.answer()
            await _process_download(event, download_id, "video", quality)


# ----------------------------------------------------------------------
# Core download + upload flow
# ----------------------------------------------------------------------
async def _process_download(event, download_id, media_type, quality):
    entry = _pending.pop(download_id, {})
    url = entry.get("url", "")
    title = entry.get("title", "Unknown")
    user_id = event.sender_id

    if _active_counts.get(user_id, 0) >= MAX_CONCURRENT_DOWNLOADS:
        await event.edit("You already have a download in progress. Please wait.")
        return

    _active_counts[user_id] = _active_counts.get(user_id, 0) + 1
    session_id = uuid.uuid4().hex[:8]
    status = None

    try:
        status = await event.get_message()
        loop = asyncio.get_running_loop()
        tracker = DownloadProgressTracker(status, loop)

        if media_type == "video":
            await status.edit(f"Downloading video ({quality}p)…")
            file_path = await asyncio.wait_for(
                asyncio.to_thread(
                    download_video, url, quality, session_id, DOWNLOAD_DIR, tracker.hook
                ),
                timeout=DOWNLOAD_TIMEOUT,
            )
        else:
            await status.edit("Downloading audio…")
            file_path = await asyncio.wait_for(
                asyncio.to_thread(
                    download_audio, url, session_id, DOWNLOAD_DIR, tracker.hook
                ),
                timeout=DOWNLOAD_TIMEOUT,
            )

        file_size = os.path.getsize(file_path)

        if file_size == 0:
            await status.edit("The downloaded file is empty. The video may be unavailable.")
            return

        if file_size > MAX_FILE_SIZE:
            await status.edit(
                f"File is too large ({format_size(file_size)}).\n"
                f"Maximum supported size: {format_size(MAX_FILE_SIZE)}."
            )
            return

        await status.edit(f"Uploading {format_size(file_size)}…")
        upload_tracker = UploadProgressTracker(status, file_size)

        await asyncio.wait_for(
            event.client.send_file(
                event.chat_id,
                file_path,
                caption=title,
                progress_callback=upload_tracker.callback,
                supports_streaming=(media_type == "video"),
            ),
            timeout=UPLOAD_TIMEOUT,
        )

        await status.edit("Done! Your file has been sent.")

    except FloodWaitError as exc:
        if status:
            await status.edit(
                f"Telegram asked us to wait {exc.seconds}s. Please try again later."
            )
    except asyncio.TimeoutError:
        if status:
            await status.edit("The operation timed out. Please try again.")
    except FileNotFoundError:
        if status:
            await status.edit("Download failed — no output file was produced.")
    except Exception:
        logger.exception("Download/upload failed")
        if status:
            await status.edit("Something went wrong. Please try again later.")
    finally:
        _active_counts[user_id] = max(0, _active_counts.get(user_id, 1) - 1)
        if _active_counts.get(user_id, 0) == 0:
            _active_counts.pop(user_id, None)
        cleanup_files(DOWNLOAD_DIR, session_id)
