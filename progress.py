"""Progress trackers for yt-dlp downloads and Telethon uploads."""

import time
import asyncio

from utils import format_size, format_duration


class DownloadProgressTracker:
    """Receives yt-dlp progress hooks (called from a worker thread) and
    edits a Telegram status message with download progress."""

    def __init__(self, message, loop, prefix="Downloading"):
        self.message = message
        self.loop = loop
        self.prefix = prefix
        self._last_update = 0.0
        self._last_text = ""

    # ------------------------------------------------------------------
    # yt-dlp calls this synchronously from a background thread
    # ------------------------------------------------------------------
    def hook(self, d):
        if d.get("status") != "downloading":
            return

        downloaded = d.get("downloaded_bytes", 0) or 0
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        speed = d.get("speed") or 0
        eta = d.get("eta") or 0

        now = time.time()
        if now - self._last_update < 3:
            return
        self._last_update = now

        text = self._format(downloaded, total, speed, eta)
        if text == self._last_text:
            return
        self._last_text = text
        asyncio.run_coroutine_threadsafe(self._edit(text), self.loop)

    # ------------------------------------------------------------------
    def _format(self, downloaded, total, speed, eta):
        if total > 0:
            pct = (downloaded / total) * 100
            bar = _progress_bar(pct)
            return (
                f"{self.prefix}\n"
                f"{bar} {pct:.1f}%\n"
                f"Size: {format_size(downloaded)} / {format_size(total)}\n"
                f"Speed: {format_size(speed)}/s\n"
                f"ETA: {format_duration(eta)}"
            )
        return f"{self.prefix}\nReceived: {format_size(downloaded)}"

    async def _edit(self, text):
        try:
            await self.message.edit(text)
        except Exception:
            pass


class UploadProgressTracker:
    """Receives Telethon upload progress callbacks (called on the event
    loop) and edits a Telegram status message with upload progress."""

    def __init__(self, message, total_size):
        self.message = message
        self.total = total_size
        self._last_update = 0.0

    def callback(self, sent, total):
        now = time.time()
        if now - self._last_update < 3:
            return
        self._last_update = now

        pct = (sent / total) * 100 if total > 0 else 0
        bar = _progress_bar(pct)
        text = (
            f"Uploading\n"
            f"{bar} {pct:.1f}%\n"
            f"Sent: {format_size(sent)} / {format_size(total)}"
        )
        asyncio.ensure_future(self._edit(text))

    async def _edit(self, text):
        try:
            await self.message.edit(text)
        except Exception:
            pass


def _progress_bar(pct):
    filled = int(pct / 5)
    return "[" + "\u2588" * filled + "\u2591" * (20 - filled) + "]"
