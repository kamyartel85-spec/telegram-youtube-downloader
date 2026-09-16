"""Telegram event handlers for the YouTube downloader bot."""

import asyncio
import uuid
import os
import logging
from datetime import datetime, timezone

from telethon import events, Button
from telethon.errors import FloodWaitError

from config import (
    DOWNLOAD_DIR,
    MAX_FILE_SIZE,
    MAX_CONCURRENT_DOWNLOADS,
    DOWNLOAD_TIMEOUT,
    UPLOAD_TIMEOUT,
    OWNER_ID,
)
from utils import is_valid_youtube_url, format_size, format_duration, cleanup_files
from youtube import extract_info, download_video, download_audio
from progress import DownloadProgressTracker, UploadProgressTracker
from i18n import t, menu_labels, LANG_LABELS, SUPPORTED_LANGS
import db

logger = logging.getLogger(__name__)

# download_id → {url, title, user_id, lang}
_pending: dict = {}
# user_id → number of active downloads
_active_counts: dict = {}


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
async def _get_user_lang(event):
    """Return the user's saved language, creating the user if needed."""
    user_id = event.sender_id
    user = await asyncio.to_thread(db.get_user, user_id)
    if user is None:
        username = None
        try:
            sender = await event.get_sender()
            username = getattr(sender, "username", None)
        except Exception:
            pass
        user = await asyncio.to_thread(db.create_user, user_id, username)
    return user.get("language", "fa") if user else "fa"


def _main_menu(lang):
    """Build the reply-keyboard for *lang*."""
    labels = menu_labels(lang)
    return [
        [labels[0], labels[1]],
        [labels[2], labels[3]],
        [labels[4], labels[5]],
        [labels[6]],
    ]


def _lang_buttons():
    """Inline buttons for the language picker."""
    return [
        [Button.inline(LANG_LABELS[lang], data=f"lang:{lang}")]
        for lang in SUPPORTED_LANGS
    ]


# ----------------------------------------------------------------------
# Handler registration
# ----------------------------------------------------------------------
def register_handlers(client):
    """Attach all command, message, and callback handlers to *client*."""

    # ── /start ────────────────────────────────────────────────────────
    @client.on(events.NewMessage(pattern=r"^/start(@\w+)?$"))
    async def _start(event):
        user_id = event.sender_id
        user = await asyncio.to_thread(db.get_user, user_id)

        if user is None:
            # First-time user: ask for language
            await event.respond(
                t("select_language", "fa"),
                buttons=_lang_buttons(),
            )
            return

        lang = user.get("language", "fa")
        await event.respond(
            t("welcome", lang),
            buttons=_main_menu(lang),
        )

    # ── /help ────────────────────────────────────────────────────────
    @client.on(events.NewMessage(pattern=r"^/help(@\w+)?$"))
    async def _help(event):
        lang = await _get_user_lang(event)
        labels = menu_labels(lang)
        await event.respond(
            t("guide_text", lang),
            buttons=_main_menu(lang),
        )

    # ── Reply-keyboard messages ───────────────────────────────────────
    @client.on(events.NewMessage(incoming=True))
    async def _menu_or_url(event):
        text = (event.raw_text or "").strip()
        user_id = event.sender_id

        # If it's a valid YouTube URL, handle download flow
        if is_valid_youtube_url(text):
            await _handle_url(event)
            return

        # Otherwise, check if it matches a menu button label
        lang = await _get_user_lang(event)
        labels = menu_labels(lang)

        if text == labels[0]:  # Search YouTube
            await event.respond(t("search_prompt", lang))

        elif text == labels[1]:  # My Account
            await _show_account(event, lang)

        elif text == labels[2]:  # Free Traffic
            await event.respond(t("free_traffic_placeholder", lang))

        elif text == labels[3]:  # Support
            await _show_support(event, lang)

        elif text == labels[4]:  # Change Language
            await event.respond(
                t("select_language", lang),
                buttons=_lang_buttons(),
            )

        elif text == labels[5]:  # YouTube Download Guide
            await event.respond(t("guide_text", lang))

        elif text == labels[6]:  # Information Channel
            await _show_channel(event, lang)

    # ── Callback queries ─────────────────────────────────────────────
    @client.on(events.CallbackQuery())
    async def _callback(event):
        try:
            data = event.data.decode("utf-8")
            parts = data.split(":")
            action = parts[0]
        except (UnicodeDecodeError, IndexError):
            return

        # ── Language selection ─────────────────────────────────────────
        if action == "lang":
            lang = parts[1] if len(parts) > 1 else "fa"
            if lang not in SUPPORTED_LANGS:
                lang = "fa"
            user = await asyncio.to_thread(db.get_user, event.sender_id)
            if user is None:
                username = None
                try:
                    sender = await event.get_sender()
                    username = getattr(sender, "username", None)
                except Exception:
                    pass
                await asyncio.to_thread(db.create_user, event.sender_id, username, language=lang)
            else:
                await asyncio.to_thread(db.update_user, event.sender_id, language=lang)
            await event.answer()
            await event.edit(t("lang_changed", lang))
            # Send fresh welcome with main menu
            await event.respond(
                t("welcome", lang),
                buttons=_main_menu(lang),
            )
            return

        # ── Download flow callbacks ────────────────────────────────────
        try:
            download_id = parts[1]
        except IndexError:
            return

        entry = _pending.get(download_id)
        if entry is None:
            await event.answer(t("expired", entry.get("lang", "fa") if entry else "fa"))
            return

        if entry["user_id"] != event.sender_id:
            await event.answer(t("not_yours", entry.get("lang", "fa")))
            return

        lang = entry.get("lang", "fa")

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
            await event.edit(t("select_quality", lang), buttons=buttons)

        elif action == "a":
            await event.answer()
            await _process_download(event, download_id, "audio", None)

        elif action == "q":
            quality = parts[2]
            await event.answer()
            await _process_download(event, download_id, "video", quality)


# ----------------------------------------------------------------------
# Menu helper functions
# ----------------------------------------------------------------------
async def _show_account(event, lang):
    """Show the user's account info."""
    user_id = event.sender_id
    user = await asyncio.to_thread(db.get_user, user_id)

    username = "—"
    if user:
        username = user.get("username") or "—"

    # Total downloads
    all_downloads = await asyncio.to_thread(db.get_user_downloads, user_id, limit=10000)
    total = len(all_downloads)

    # Today's downloads
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_count = sum(
        1 for d in all_downloads
        if d.get("created_at", "").startswith(today_str)
    )

    # Daily limit
    custom_limit = user.get("custom_daily_limit") if user else None
    if custom_limit:
        remaining = max(0, custom_limit - today_count)
        limit_text = f"{remaining} / {custom_limit}"
    else:
        limit_text = t("account_unlimited", lang)

    text = (
        f"**{t('account_title', lang)}**\n\n"
        f"{t('account_user_id', lang)}: `{user_id}`\n"
        f"{t('account_username', lang)}: @{username}\n"
        f"{t('account_total_downloads', lang)}: {total}\n"
        f"{t('account_today_downloads', lang)}: {today_count}\n"
        f"{t('account_daily_limit', lang)}: {limit_text}"
    )
    await event.respond(text, buttons=_main_menu(lang))


async def _show_support(event, lang):
    """Show support contact info from settings."""
    support_id = await asyncio.to_thread(db.get_setting, "support_id")
    if support_id:
        await event.respond(
            t("support_text", lang, support_id=support_id),
            buttons=_main_menu(lang),
        )
    else:
        await event.respond(
            t("support_not_set", lang),
            buttons=_main_menu(lang),
        )


async def _show_channel(event, lang):
    """Show the information channel link from settings."""
    channel_link = await asyncio.to_thread(db.get_setting, "channel_link")
    if channel_link:
        await event.respond(
            t("channel_text", lang, channel_link=channel_link),
            buttons=_main_menu(lang),
        )
    else:
        await event.respond(
            t("channel_not_set", lang),
            buttons=_main_menu(lang),
        )


# ----------------------------------------------------------------------
# YouTube URL handling
# ----------------------------------------------------------------------
async def _handle_url(event):
    """Process a YouTube URL sent by the user."""
    url = event.raw_text.strip()
    user_id = event.sender_id

    lang = await _get_user_lang(event)

    if _active_counts.get(user_id, 0) >= MAX_CONCURRENT_DOWNLOADS:
        await event.respond(t("already_downloading", lang))
        return

    status = await event.respond(t("fetching_info", lang))

    try:
        info = await asyncio.wait_for(
            asyncio.to_thread(extract_info, url),
            timeout=30,
        )
    except asyncio.TimeoutError:
        await status.edit(t("fetch_timeout", lang))
        return
    except Exception:
        logger.exception("extract_info failed for %s", url)
        await status.edit(t("fetch_error", lang))
        return

    title = info.get("title", "Unknown")
    duration = info.get("duration", 0)
    uploader = info.get("uploader", "Unknown")

    download_id = uuid.uuid4().hex[:8]
    _pending[download_id] = {
        "url": url,
        "title": title,
        "user_id": user_id,
        "lang": lang,
    }

    text = (
        f"**{title}**\n\n"
        f"{t('channel', lang)}: {uploader}\n"
        f"{t('duration', lang)}: {format_duration(duration)}\n\n"
        f"{t('choose_format', lang)}"
    )
    buttons = [
        [
            Button.inline(t("video", lang), data=f"v:{download_id}"),
            Button.inline(t("audio", lang), data=f"a:{download_id}"),
        ]
    ]
    await status.edit(text, buttons=buttons)


# ----------------------------------------------------------------------
# Core download + upload flow
# ----------------------------------------------------------------------
async def _process_download(event, download_id, media_type, quality):
    entry = _pending.pop(download_id, {})
    url = entry.get("url", "")
    title = entry.get("title", "Unknown")
    user_id = event.sender_id
    lang = entry.get("lang", "fa")

    if _active_counts.get(user_id, 0) >= MAX_CONCURRENT_DOWNLOADS:
        await event.edit(t("already_downloading", lang))
        return

    _active_counts[user_id] = _active_counts.get(user_id, 0) + 1
    session_id = uuid.uuid4().hex[:8]
    status = None

    try:
        status = await event.get_message()
        loop = asyncio.get_running_loop()
        tracker = DownloadProgressTracker(status, loop)

        if media_type == "video":
            await status.edit(t("downloading_video", lang, quality=quality))
            file_path = await asyncio.wait_for(
                asyncio.to_thread(
                    download_video, url, quality, session_id, DOWNLOAD_DIR, tracker.hook
                ),
                timeout=DOWNLOAD_TIMEOUT,
            )
        else:
            await status.edit(t("downloading_audio", lang))
            file_path = await asyncio.wait_for(
                asyncio.to_thread(
                    download_audio, url, session_id, DOWNLOAD_DIR, tracker.hook
                ),
                timeout=DOWNLOAD_TIMEOUT,
            )

        file_size = os.path.getsize(file_path)

        if file_size == 0:
            await status.edit(t("file_empty", lang))
            return

        if file_size > MAX_FILE_SIZE:
            await status.edit(
                t("file_too_large", lang, size=format_size(file_size),
                  max_size=format_size(MAX_FILE_SIZE))
            )
            return

        await status.edit(t("uploading", lang, size=format_size(file_size)))
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

        await status.edit(t("done", lang))

    except FloodWaitError as exc:
        if status:
            await status.edit(t("flood_wait", lang, seconds=exc.seconds))
    except asyncio.TimeoutError:
        if status:
            await status.edit(t("timeout", lang))
    except FileNotFoundError:
        if status:
            await status.edit(t("no_file", lang))
    except Exception:
        logger.exception("Download/upload failed")
        if status:
            await status.edit(t("generic_error", lang))
    finally:
        _active_counts[user_id] = max(0, _active_counts.get(user_id, 1) - 1)
        if _active_counts.get(user_id, 0) == 0:
            _active_counts.pop(user_id, None)
        cleanup_files(DOWNLOAD_DIR, session_id)
