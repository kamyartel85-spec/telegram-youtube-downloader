"""Simplified progress notification tracker for the YouTube downloader bot.

Rotates simple friendly status messages without cluttered percentages (Section 6.3).
"""

import time
import asyncio
from i18n import t


class SimpleStatusTracker:
    """Cycle through friendly status messages every few seconds to inform the user."""

    def __init__(self, message, loop, lang="fa"):
        self.message = message
        self.loop = loop
        self.lang = lang
        self._last_update = 0.0
        self._stage_idx = 0
        self._stages = [
            "status_downloading",
            "status_processing",
            "status_waiting",
        ]

    def hook(self, d):
        """Called by yt-dlp synchronously from a background thread."""
        now = time.time()
        if now - self._last_update < 3.5:
            return
        self._last_update = now

        key = self._stages[self._stage_idx % len(self._stages)]
        self._stage_idx += 1
        text = t(key, self.lang)

        asyncio.run_coroutine_threadsafe(self._edit(text), self.loop)

    async def _edit(self, text):
        try:
            await self.message.edit(text)
        except Exception:
            pass


class SimpleUploadTracker:
    """Sends simple upload status during Telethon file transmission."""

    def __init__(self, message, lang="fa"):
        self.message = message
        self.lang = lang
        self._last_update = 0.0

    def callback(self, sent, total):
        now = time.time()
        if now - self._last_update < 4:
            return
        self._last_update = now

        text = t("status_uploading", self.lang)
        asyncio.ensure_future(self._edit(text))

    async def _edit(self, text):
        try:
            await self.message.edit(text)
        except Exception:
            pass
