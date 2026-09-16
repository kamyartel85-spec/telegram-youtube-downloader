"""Telegram event handlers for the YouTube downloader bot."""

import asyncio
import uuid
import os
import json
import time
import logging
from datetime import datetime, timezone

from telethon import events, Button, utils as telethon_utils
from telethon.errors import FloodWaitError
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeAudio, InputDocument

from config import (
    DOWNLOAD_DIR,
    MAX_FILE_SIZE,
    MAX_CONCURRENT_DOWNLOADS,
    DOWNLOAD_TIMEOUT,
    UPLOAD_TIMEOUT,
    MAX_PLAYLIST_ITEMS,
    RATE_LIMIT_PER_MINUTE,
    OWNER_ID,
)
from utils import (
    is_valid_youtube_url,
    is_playlist_url,
    format_size,
    format_duration,
    format_duration_persian,
    format_system_status,
    cleanup_files,
)
from youtube import (
    extract_info,
    extract_playlist_info,
    download_video,
    download_audio,
    prepare_thumbnail,
    get_quality_dimensions,
)
from progress import SimpleStatusTracker, SimpleUploadTracker
from i18n import t, menu_labels, LANG_LABELS, SUPPORTED_LANGS
from keyboards import (
    main_menu_keyboard,
    lang_inline_keyboard,
    force_join_keyboard,
    quality_and_format_keyboard,
    file_action_keyboard,
    retry_keyboard,
)
import db

logger = logging.getLogger(__name__)

# State tracking
# download_id → metadata dict
_pending_downloads: dict = {}
# user_id → active downloads count
_active_user_downloads: dict = {}
# user_id → list of message timestamps (for rate limiting)
_user_rate_limits: dict = {}


# ----------------------------------------------------------------------
# Middleware / Pre-flight checks
# ----------------------------------------------------------------------
def _is_rate_limited(user_id: int) -> bool:
    """Return True if user exceeded rate limit."""
    now = time.time()
    times = _user_rate_limits.setdefault(user_id, [])
    # Remove timestamps older than 60s
    _user_rate_limits[user_id] = [ts for ts in times if now - ts < 60]
    if len(_user_rate_limits[user_id]) >= RATE_LIMIT_PER_MINUTE:
        return True
    _user_rate_limits[user_id].append(now)
    return False


async def _check_maintenance(event, user_id: int) -> bool:
    """Return True if maintenance is active and user is not admin."""
    admin = await asyncio.to_thread(db.get_admin, user_id)
    if admin or (OWNER_ID and user_id == OWNER_ID):
        return False
    val = await asyncio.to_thread(db.get_setting, "maintenance_mode", "0")
    if val == "1":
        u = await asyncio.to_thread(db.get_user, user_id)
        lang = u.get("language", "fa") if u else "fa"
        await event.respond(t("maintenance_message", lang))
        return True
    return False


async def _check_force_join(client, event, user_id: int, lang: str = "fa") -> bool:
    """Check if user joined all required channels. Returns True if passed, False if blocked."""
    admin = await asyncio.to_thread(db.get_admin, user_id)
    if admin or (OWNER_ID and user_id == OWNER_ID):
        return True

    enabled = await asyncio.to_thread(db.get_setting, "force_join_enabled", "0")
    if enabled != "1":
        return True

    raw_channels = await asyncio.to_thread(db.get_setting, "force_join_channels", "[]")
    try:
        channels = json.loads(raw_channels)
    except Exception:
        channels = []

    if not channels:
        return True

    not_joined = []
    for ch in channels:
        channel_ref = ch.get("url") or ch.get("name")
        if not channel_ref:
            continue
        try:
            # Extract username or handle
            handle = channel_ref.rstrip("/").split("/")[-1]
            if not handle.startswith("@") and not handle.startswith("+"):
                handle = f"@{handle}"
            perms = await client.get_permissions(handle, user_id)
            if perms is None:
                not_joined.append(ch)
        except Exception:
            # If checking permissions fails or is private link, keep listed
            not_joined.append(ch)

    if not_joined:
        await event.respond(
            t("force_join_prompt", lang),
            buttons=force_join_keyboard(channels, lang),
        )
        return False

    return True


async def _get_or_create_user(event, referral_id=None):
    """Retrieve user from database or create new record."""
    user_id = event.sender_id
    user = await asyncio.to_thread(db.get_user, user_id)
    if user is None:
        username = None
        try:
            sender = await event.get_sender()
            username = getattr(sender, "username", None)
        except Exception:
            pass
        user = await asyncio.to_thread(
            db.create_user,
            user_id=user_id,
            username=username,
            referred_by=referral_id,
            language="fa",
        )
        # Give bonus to inviter if valid referral
        if referral_id and referral_id != user_id:
            inviter = await asyncio.to_thread(db.get_user, referral_id)
            if inviter:
                bonus_str = await asyncio.to_thread(db.get_setting, "referral_bonus", "3")
                try:
                    bonus = int(bonus_str)
                except ValueError:
                    bonus = 3
                cur_bonus = inviter.get("bonus_downloads") or 0
                await asyncio.to_thread(
                    db.update_user,
                    referral_id,
                    bonus_downloads=cur_bonus + bonus,
                )
    return user


async def _has_download_allowance(user_id: int) -> bool:
    """Verify if user has available download quota for today."""
    daily_enabled = await asyncio.to_thread(db.get_setting, "daily_limit_enabled", "1")
    if daily_enabled != "1":
        return True

    user = await asyncio.to_thread(db.get_user, user_id)
    if not user:
        return True

    custom_limit = user.get("custom_daily_limit")
    if custom_limit is not None:
        daily_limit = custom_limit
    else:
        limit_str = await asyncio.to_thread(db.get_setting, "daily_limit_count", "10")
        try:
            daily_limit = int(limit_str)
        except ValueError:
            daily_limit = 10

    bonus = user.get("bonus_downloads") or 0
    total_allowed = daily_limit + bonus

    # Count downloads today
    today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    recent = await asyncio.to_thread(db.get_user_downloads, user_id, 100)
    today_count = sum(1 for d in recent if (d.get("created_at") or "").startswith(today_prefix) and d.get("status") == "success")

    return today_count < total_allowed


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------
def register_handlers(client):
    """Attach all event listeners to Telethon client."""

    # ------------------------------------------------------------------
    # /start
    # ------------------------------------------------------------------
    @client.on(events.NewMessage(pattern=r"^/start(?:\s+(ref_\d+))?"))
    async def handle_start(event):
        user_id = event.sender_id
        if await _check_maintenance(event, user_id):
            return

        ref_param = event.pattern_match.group(1)
        ref_id = None
        if ref_param and ref_param.startswith("ref_"):
            try:
                ref_id = int(ref_param.replace("ref_", ""))
            except ValueError:
                ref_id = None

        existing = await asyncio.to_thread(db.get_user, user_id)
        user = await _get_or_create_user(event, referral_id=ref_id)
        lang = user.get("language", "fa")

        # Check forced join first
        if not await _check_force_join(client, event, user_id, lang):
            return

        # If user was not yet created before or has not chosen language, show language picker
        if existing is None:
            await event.respond(
                t("select_language", lang),
                buttons=lang_inline_keyboard(),
            )
            return

        # Send welcome message with reply keyboard
        await event.respond(
            t("welcome", lang),
            buttons=main_menu_keyboard(lang),
        )

    # ------------------------------------------------------------------
    # /status (Real-time system health and resource metrics)
    # ------------------------------------------------------------------
    @client.on(events.NewMessage(pattern=r"^/status\b"))
    async def handle_status_command(event):
        active = sum(_active_user_downloads.values())
        status_text = format_system_status(active_downloads=active)
        await event.respond(status_text, parse_mode="html")

    # ------------------------------------------------------------------
    # Language change callback
    # ------------------------------------------------------------------
    @client.on(events.CallbackQuery(pattern=r"^lang:(fa|en|ru)$"))
    async def handle_lang_callback(event):
        lang = event.pattern_match.group(1).decode("utf-8")
        user_id = event.sender_id
        await asyncio.to_thread(db.update_user, user_id, language=lang)
        await event.answer()

        await event.respond(
            t("lang_changed", lang),
        )
        await event.respond(
            t("welcome", lang),
            buttons=main_menu_keyboard(lang),
        )

    # ------------------------------------------------------------------
    # Forced join verification callback
    # ------------------------------------------------------------------
    @client.on(events.CallbackQuery(pattern=r"^check_join$"))
    async def handle_check_join(event):
        user_id = event.sender_id
        u = await asyncio.to_thread(db.get_user, user_id)
        lang = u.get("language", "fa") if u else "fa"

        passed = await _check_force_join(client, event, user_id, lang)
        if passed:
            await event.answer("✅", alert=False)
            await event.respond(
                t("welcome", lang),
                buttons=main_menu_keyboard(lang),
            )
        else:
            await event.answer(t("force_join_not_yet", lang), alert=True)

    # ------------------------------------------------------------------
    # Reply Keyboard Menu Clicks
    # ------------------------------------------------------------------
    @client.on(events.NewMessage)
    async def handle_menu_text(event):
        text = (event.raw_text or "").strip()
        if not text or text.startswith("/"):
            return

        user_id = event.sender_id
        if await _check_maintenance(event, user_id):
            return

        if _is_rate_limited(user_id):
            u = await asyncio.to_thread(db.get_user, user_id)
            lang = u.get("language", "fa") if u else "fa"
            await event.respond(t("rate_limit_exceeded", lang))
            return

        user = await _get_or_create_user(event)
        if user.get("is_banned"):
            await event.respond(t("banned_message", user.get("language", "fa")))
            return

        lang = user.get("language", "fa")

        # 🔍 جست‌وجو در یوتیوب
        if any(text == t("btn_search", l) for l in SUPPORTED_LANGS):
            await event.respond(t("search_prompt", lang))
            return

        # 👤 حساب من
        if any(text == t("btn_account", l) for l in SUPPORTED_LANGS):
            recent = await asyncio.to_thread(db.get_user_downloads, user_id, 200)
            total_dl = len([d for d in recent if d.get("status") == "success"])
            today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            today_dl = len([d for d in recent if (d.get("created_at") or "").startswith(today_prefix) and d.get("status") == "success"])

            daily_enabled = await asyncio.to_thread(db.get_setting, "daily_limit_enabled", "1")
            if daily_enabled != "1":
                rem_str = "بی‌نهایت" if lang == "fa" else "Unlimited"
            else:
                c_lim = user.get("custom_daily_limit")
                if c_lim is not None:
                    max_allowed = c_lim + (user.get("bonus_downloads") or 0)
                else:
                    lim_str = await asyncio.to_thread(db.get_setting, "daily_limit_count", "10")
                    try:
                        max_allowed = int(lim_str) + (user.get("bonus_downloads") or 0)
                    except ValueError:
                        max_allowed = 10 + (user.get("bonus_downloads") or 0)
                remaining = max(0, max_allowed - today_dl)
                rem_str = str(remaining)

            await event.respond(
                t(
                    "account_text",
                    lang,
                    user_id=user_id,
                    total_downloads=total_dl,
                    today_downloads=today_dl,
                    remaining_downloads=rem_str,
                )
            )
            return

        # 🚀 ترافیک رایگان
        if any(text == t("btn_free_traffic", l) for l in SUPPORTED_LANGS):
            me = await client.get_me()
            bot_user = me.username or "Bot"
            ref_link = f"https://t.me/{bot_user}?start=ref_{user_id}"
            bonus_str = await asyncio.to_thread(db.get_setting, "referral_bonus", "3")
            await event.respond(
                t(
                    "free_traffic_text",
                    lang,
                    bonus_count=bonus_str,
                    referral_link=ref_link,
                )
            )
            return

        # ☎️ پشتیبانی
        if any(text == t("btn_support", l) for l in SUPPORTED_LANGS):
            supp = await asyncio.to_thread(db.get_setting, "support_id", "@SupportBot")
            await event.respond(t("support_text", lang, support_id=supp))
            return

        # 🌐 تغییر زبان
        if any(text == t("btn_change_lang", l) for l in SUPPORTED_LANGS):
            await event.respond(
                t("select_language", lang),
                buttons=lang_inline_keyboard(),
            )
            return

        # 🍿 راهنمای دانلود از یوتیوب
        if any(text == t("btn_guide", l) for l in SUPPORTED_LANGS):
            await event.respond(t("guide_text", lang))
            return

        # 📢 کانال اطلاع‌رسانی
        if any(text == t("btn_channel", l) for l in SUPPORTED_LANGS):
            ch_link = await asyncio.to_thread(db.get_setting, "channel_link", "https://t.me")
            await event.respond(t("channel_text", lang, channel_link=ch_link))
            return

    # ------------------------------------------------------------------
    # YouTube Link Detection (Single Video or Playlist)
    # ------------------------------------------------------------------
    @client.on(events.NewMessage)
    async def handle_youtube_link(event):
        url = (event.raw_text or "").strip()
        if not is_valid_youtube_url(url):
            return

        user_id = event.sender_id
        if await _check_maintenance(event, user_id):
            return

        if _is_rate_limited(user_id):
            u = await asyncio.to_thread(db.get_user, user_id)
            lang = u.get("language", "fa") if u else "fa"
            await event.respond(t("rate_limit_exceeded", lang))
            return

        user = await _get_or_create_user(event)
        if user.get("is_banned"):
            await event.respond(t("banned_message", user.get("language", "fa")))
            return

        lang = user.get("language", "fa")

        if not await _check_force_join(client, event, user_id, lang):
            return

        status_msg = await event.respond(t("status_waiting", lang))

        # Check if playlist
        if is_playlist_url(url):
            try:
                max_pl_str = await asyncio.to_thread(db.get_setting, "max_playlist_items", str(MAX_PLAYLIST_ITEMS))
                try:
                    max_pl = int(max_pl_str)
                except ValueError:
                    max_pl = MAX_PLAYLIST_ITEMS

                info = await asyncio.to_thread(extract_playlist_info, url, max_pl)
                dl_id = str(uuid.uuid4())[:8]
                _pending_downloads[dl_id] = {
                    "is_playlist": True,
                    "url": url,
                    "title": info["title"],
                    "items": info["items"],
                    "user_id": user_id,
                    "lang": lang,
                }
                caption = t(
                    "playlist_info_caption",
                    lang,
                    title=info["title"],
                    count=info["total_count"],
                    max_items=len(info["items"]),
                )
                await status_msg.delete()
                await event.respond(
                    caption,
                    buttons=quality_and_format_keyboard(dl_id, {}, lang),
                )
            except Exception as exc:
                logger.error("Playlist extract error: %s", exc)
                await status_msg.edit(t("fetch_error", lang))
                await asyncio.to_thread(db.add_error_log, user_id, url, str(exc))
            return

        # Single video
        try:
            info = await asyncio.to_thread(extract_info, url)
            dl_id = str(uuid.uuid4())[:8]
            _pending_downloads[dl_id] = {
                "is_playlist": False,
                "url": url,
                "video_id": info["id"],
                "title": info["title"],
                "uploader": info["uploader"],
                "duration": info["duration"],
                "raw_duration": info.get("raw_duration") or 0,
                "thumbnail": info.get("thumbnail"),
                "user_id": user_id,
                "lang": lang,
            }

            dur_display = info["duration"]
            if info.get("duration_persian") and lang == "fa":
                dur_display = f"{info['duration']} ({info['duration_persian']})"

            caption = t(
                "video_info_caption",
                lang,
                title=info["title"],
                duration=dur_display,
                uploader=info["uploader"],
                views=info["view_count"],
                comments=info["comment_count"],
                upload_date=info["upload_date"],
            )

            await status_msg.delete()
            if info.get("thumbnail"):
                await client.send_file(
                    event.chat_id,
                    info["thumbnail"],
                    caption=caption,
                    parse_mode="html",
                    buttons=quality_and_format_keyboard(dl_id, info.get("format_sizes"), lang),
                )
            else:
                await event.respond(
                    caption,
                    parse_mode="html",
                    buttons=quality_and_format_keyboard(dl_id, info.get("format_sizes"), lang),
                )
        except Exception as exc:
            logger.error("Extract video info error: %s", exc)
            await status_msg.edit(t("fetch_error", lang))
            await asyncio.to_thread(db.add_error_log, user_id, url, str(exc))

    # ------------------------------------------------------------------
    # Quality / Format Callback (Download Execution)
    # ------------------------------------------------------------------
    @client.on(events.CallbackQuery(pattern=r"^dl:([a-zA-Z0-9_-]+):(a_med|a_best|v_\d+)$"))
    async def handle_download_callback(event):
        dl_id = event.pattern_match.group(1).decode("utf-8")
        choice = event.pattern_match.group(2).decode("utf-8")
        user_id = event.sender_id

        entry = _pending_downloads.get(dl_id)
        if not entry:
            await event.answer("⚠️ این درخواست منقضی شده است.", alert=True)
            return

        lang = entry.get("lang", "fa")

        # Check quota
        allowed = await _has_download_allowance(user_id)
        if not allowed:
            await event.answer()
            await event.respond(t("daily_limit_reached", lang))
            return

        # Check concurrent
        active = _active_user_downloads.get(user_id, 0)
        if active >= MAX_CONCURRENT_DOWNLOADS:
            await event.answer("⚠️ دانلود دیگری در حال اجراست.", alert=True)
            return

        _active_user_downloads[user_id] = active + 1
        await event.answer()

        status_msg = await event.respond(t("status_waiting", lang))

        # Playlist batch execution
        if entry.get("is_playlist"):
            items = entry.get("items", [])
            total = len(items)
            success_count = 0
            for idx, item in enumerate(items, 1):
                await status_msg.edit(f"⏳ در حال دانلود ویدیو {idx} از {total}...")
                try:
                    ok = await _process_single_media(
                        client=client,
                        event=event,
                        status_msg=status_msg,
                        user_id=user_id,
                        url=item["url"],
                        video_id=item.get("id"),
                        title=item.get("title", f"Video {idx}"),
                        choice=choice,
                        lang=lang,
                        send_status=False,
                    )
                    if ok:
                        success_count += 1
                except Exception as e:
                    logger.error("Playlist item download failed: %s", e)
            await status_msg.edit(f"✅ {success_count} از {total} ویدیو با موفقیت ارسال شد.")
            _active_user_downloads[user_id] = max(0, _active_user_downloads.get(user_id, 1) - 1)
            return

        # Single video execution
        try:
            await _process_single_media(
                client=client,
                event=event,
                status_msg=status_msg,
                user_id=user_id,
                url=entry["url"],
                video_id=entry.get("video_id"),
                title=entry.get("title"),
                choice=choice,
                raw_duration=entry.get("raw_duration", 0),
                thumbnail_url=entry.get("thumbnail"),
                uploader=entry.get("uploader"),
                lang=lang,
                send_status=True,
            )
        finally:
            _active_user_downloads[user_id] = max(0, _active_user_downloads.get(user_id, 1) - 1)

    # ------------------------------------------------------------------
    # Report problem callback
    # ------------------------------------------------------------------
    @client.on(events.CallbackQuery(pattern=r"^report:(\d+)$"))
    async def handle_report(event):
        dl_record_id = event.pattern_match.group(1).decode("utf-8")
        user_id = event.sender_id
        u = await asyncio.to_thread(db.get_user, user_id)
        lang = u.get("language", "fa") if u else "fa"

        # Log problem
        await asyncio.to_thread(
            db.add_error_log,
            user_id,
            f"dl_id:{dl_record_id}",
            "User reported problem with downloaded file",
        )

        # Notify error log channel if configured
        err_ch = await asyncio.to_thread(db.get_setting, "error_log_channel_id", "")
        if err_ch:
            try:
                await client.send_message(
                    int(err_ch) if err_ch.startswith("-") else err_ch,
                    f"⚠️ <b>گزارش مشکل دانلود:</b>\n"
                    f"👤 کاربر: <code>{user_id}</code>\n"
                    f"📁 شناسه دانلود: <code>{dl_record_id}</code>",
                    parse_mode="html",
                )
            except Exception as exc:
                logger.error("Could not forward report to error channel: %s", exc)

        await event.answer(t("issue_reported", lang), alert=True)

    # ------------------------------------------------------------------
    # Retry callback
    # ------------------------------------------------------------------
    @client.on(events.CallbackQuery(pattern=r"^retry:([a-zA-Z0-9_-]+)$"))
    async def handle_retry(event):
        dl_id = event.pattern_match.group(1).decode("utf-8")
        entry = _pending_downloads.get(dl_id)
        if not entry:
            await event.answer("⚠️ منقضی شده است.", alert=True)
            return
        await event.answer()
        # Prompt quality again
        lang = entry.get("lang", "fa")
        await event.respond(
            "لطفاً کیفیت مورد نظر را مجدداً انتخاب کنید:",
            buttons=quality_and_format_keyboard(dl_id, {}, lang),
        )

    @client.on(events.CallbackQuery(pattern=r"^cancel_retry:([a-zA-Z0-9_-]+)$"))
    async def handle_cancel_retry(event):
        await event.delete()


def _build_media_caption(title, media_type, quality, file_size, raw_duration, uploader, bot_username=None):
    """Build a polished, 100% Persian delivery caption for downloaded media."""
    tag = f"\n\n🤖 @{bot_username}" if bot_username else ""
    size_str = format_size(file_size) if file_size else "استاندارد"
    dur_str = format_duration(raw_duration) if raw_duration else "نامشخص"
    up_str = uploader or "یوتیوب (YouTube)"

    if media_type == "video":
        return (
            f"🎬 <b>{title}</b>\n\n"
            f"🎥 <b>کیفیت:</b> {quality}p\n"
            f"💾 <b>حجم:</b> {size_str}\n"
            f"⏱ <b>مدت زمان:</b> {dur_str}\n"
            f"📢 <b>کانال:</b> {up_str}"
            f"{tag}"
        )
    else:
        q_label = "320 kbps (حداکثر کیفیت)" if quality in ("a_best", "320") else "128 kbps (کیفیت استاندارد)"
        return (
            f"🎧 <b>{title}</b>\n\n"
            f"🎵 <b>کیفیت:</b> {q_label}\n"
            f"💾 <b>حجم:</b> {size_str}\n"
            f"⏱ <b>مدت زمان:</b> {dur_str}\n"
            f"🎙 <b>هنرمند / کانال:</b> {up_str}"
            f"{tag}"
        )


# ----------------------------------------------------------------------
# Single Media Download & Upload Workflow
# ----------------------------------------------------------------------
async def _process_single_media(
    client,
    event,
    status_msg,
    user_id,
    url,
    video_id,
    title,
    choice,
    raw_duration=0,
    thumbnail_url=None,
    uploader="YouTube",
    lang="fa",
    send_status=True,
) -> bool:
    """Download or retrieve from cache and deliver to user."""
    is_audio = choice.startswith("a_")
    media_type = "audio" if is_audio else "video"
    quality = choice.replace("v_", "") if not is_audio else choice

    bot_username = getattr(client, "_bot_username", None)
    if not bot_username:
        try:
            me = await client.get_me()
            bot_username = me.username or ""
            client._bot_username = bot_username
        except Exception:
            bot_username = ""

    # 1. Check Cache (Section 6.1)
    if video_id:
        cached = await asyncio.to_thread(db.get_cache, video_id, quality, media_type)
        if cached and cached.get("telegram_file_id"):
            file_id = cached["telegram_file_id"]
            if send_status:
                await status_msg.edit("⚡ در حال بازیابی و ارسال از آرشیو تلگرام...")

            sent_msg = None
            cached_caption = _build_media_caption(
                title=title,
                media_type=media_type,
                quality=quality,
                file_size=cached.get("file_size"),
                raw_duration=raw_duration,
                uploader=uploader,
                bot_username=bot_username,
            )

            try:
                if file_id.startswith("doc:"):
                    parts = file_id.split(":")
                    if len(parts) >= 4:
                        doc = InputDocument(
                            id=int(parts[1]),
                            access_hash=int(parts[2]),
                            file_reference=bytes.fromhex(parts[3]),
                        )
                        sent_msg = await client.send_file(
                            event.chat_id,
                            doc,
                            caption=cached_caption,
                            parse_mode="html",
                            supports_streaming=True,
                        )
                else:
                    sent_msg = await client.send_file(
                        event.chat_id,
                        file_id,
                        caption=cached_caption,
                        parse_mode="html",
                        supports_streaming=True,
                    )

                if sent_msg:
                    rec_id = await asyncio.to_thread(
                        db.add_download,
                        user_id=user_id,
                        url=url,
                        title=title,
                        media_type=media_type,
                        quality=quality,
                        file_size=cached.get("file_size"),
                        status="success",
                    )
                    try:
                        await sent_msg.edit(buttons=file_action_keyboard(rec_id, lang))
                    except Exception:
                        pass

                    if send_status:
                        await status_msg.edit(t("status_done", lang) + " ⚡ (تحویل فوری از آرشیو)")

                    # Forward to download log channel (Section 8)
                    await _forward_to_download_log(client, sent_msg, title, event.sender)
                    return True

            except Exception as cache_err:
                logger.warning("Cache send failed (%s), invalidating cache and falling back to fresh download", cache_err)
                await asyncio.to_thread(db.delete_cache, video_id, quality, media_type)
                if send_status:
                    await status_msg.edit(t("status_downloading", lang))

    # 2. Cache miss: download from YouTube
    session_id = f"{user_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    loop = asyncio.get_running_loop()

    tracker = SimpleStatusTracker(status_msg, loop, lang=lang)

    try:
        if send_status:
            await status_msg.edit(t("status_downloading", lang))

        if is_audio:
            file_path = await asyncio.wait_for(
                asyncio.to_thread(
                    download_audio,
                    url=url,
                    preset="mp3_best" if choice == "a_best" else "mp3_medium",
                    session_id=session_id,
                    download_dir=DOWNLOAD_DIR,
                    progress_hook=tracker.hook,
                ),
                timeout=DOWNLOAD_TIMEOUT,
            )
        else:
            file_path = await asyncio.wait_for(
                asyncio.to_thread(
                    download_video,
                    url=url,
                    quality=quality,
                    session_id=session_id,
                    download_dir=DOWNLOAD_DIR,
                    progress_hook=tracker.hook,
                ),
                timeout=DOWNLOAD_TIMEOUT,
            )

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            await status_msg.edit(
                f"❌ حجم فایل ({format_size(file_size)}) بیشتر از سقف مجاز تلگرام است."
            )
            cleanup_files(DOWNLOAD_DIR, session_id)
            return False

        # 3. Upload to Telegram
        if send_status:
            await status_msg.edit(t("status_uploading", lang))

        upload_tracker = SimpleUploadTracker(status_msg, lang=lang)
        caption = _build_media_caption(
            title=title,
            media_type=media_type,
            quality=quality,
            file_size=file_size,
            raw_duration=raw_duration,
            uploader=uploader,
            bot_username=bot_username,
        )

        # Prepare thumbnail to fix black/white blank previews in Telegram
        thumb_path = None
        if thumbnail_url:
            thumb_path = await asyncio.to_thread(
                prepare_thumbnail,
                thumb_url=thumbnail_url,
                session_id=session_id,
                download_dir=DOWNLOAD_DIR,
            )

        # Set explicit document attributes:
        # Prevents the "00:00" duration bug and configures correct player dimensions & metadata
        attributes = []
        if media_type == "video":
            width, height = get_quality_dimensions(quality)
            attributes.append(
                DocumentAttributeVideo(
                    duration=int(raw_duration or 0),
                    w=width,
                    h=height,
                    supports_streaming=True,
                )
            )
        else:
            attributes.append(
                DocumentAttributeAudio(
                    duration=int(raw_duration or 0),
                    title=title or "Audio Track",
                    performer=uploader or "YouTube",
                    voice=False,  # Explicitly standard music track for Telegram music player
                )
            )

        sent_msg = await asyncio.wait_for(
            client.send_file(
                event.chat_id,
                file_path,
                caption=caption,
                parse_mode="html",
                thumb=thumb_path,
                attributes=attributes,
                progress_callback=upload_tracker.callback,
                supports_streaming=True,  # Enables instant progressive streaming for both audio & video
            ),
            timeout=UPLOAD_TIMEOUT,
        )

        # 4. Save to Cache & Record in DB
        telegram_file_id = None
        if sent_msg and getattr(sent_msg, "media", None):
            media = sent_msg.media
            doc = getattr(media, "document", None)
            if doc and hasattr(doc, "id") and hasattr(doc, "access_hash") and hasattr(doc, "file_reference"):
                telegram_file_id = f"doc:{doc.id}:{doc.access_hash}:{doc.file_reference.hex()}"
            else:
                try:
                    telegram_file_id = telethon_utils.pack_bot_file_id(media)
                except Exception:
                    telegram_file_id = str(getattr(getattr(sent_msg, "file", None), "id", "")) or None

        if video_id and telegram_file_id:
            await asyncio.to_thread(
                db.set_cache,
                video_id=video_id,
                quality=quality,
                media_type=media_type,
                telegram_file_id=telegram_file_id,
                file_size=file_size,
            )

        rec_id = await asyncio.to_thread(
            db.add_download,
            user_id=user_id,
            url=url,
            title=title,
            media_type=media_type,
            quality=quality,
            file_size=file_size,
            status="success",
        )

        # Attach report issue button
        try:
            await sent_msg.edit(buttons=file_action_keyboard(rec_id, lang))
        except Exception:
            pass

        if send_status:
            await status_msg.edit(t("status_done", lang))

        # Forward to download log channel (Section 8)
        await _forward_to_download_log(client, sent_msg, title, event.sender)
        return True

    except asyncio.TimeoutError:
        logger.error("Download or upload timed out for url=%s", url)
        await asyncio.to_thread(db.add_error_log, user_id, url, "Operation timed out")
        dl_retry_id = str(uuid.uuid4())[:8]
        _pending_downloads[dl_retry_id] = {
            "is_playlist": False,
            "url": url,
            "video_id": video_id,
            "title": title,
            "user_id": user_id,
            "lang": lang,
        }
        await status_msg.edit(
            t("download_incomplete", lang),
            buttons=retry_keyboard(dl_retry_id, lang),
        )
        return False
    except Exception as exc:
        logger.exception("Error processing download: %s", exc)
        await asyncio.to_thread(db.add_error_log, user_id, url, str(exc))
        # Forward to error channel if configured
        err_ch = await asyncio.to_thread(db.get_setting, "error_log_channel_id", "")
        if err_ch:
            try:
                await client.send_message(
                    int(err_ch) if err_ch.startswith("-") else err_ch,
                    f"⚠️ <b>خطای غیرمنتظره در دانلود:</b>\n"
                    f"👤 کاربر: <code>{user_id}</code>\n"
                    f"🔗 لینک: {url}\n"
                    f"❌ خطا: <code>{str(exc)[:200]}</code>",
                    parse_mode="html",
                )
            except Exception:
                pass

        dl_retry_id = str(uuid.uuid4())[:8]
        _pending_downloads[dl_retry_id] = {
            "is_playlist": False,
            "url": url,
            "video_id": video_id,
            "title": title,
            "user_id": user_id,
            "lang": lang,
        }
        await status_msg.edit(
            t("download_incomplete", lang),
            buttons=retry_keyboard(dl_retry_id, lang),
        )
        return False
    finally:
        cleanup_files(DOWNLOAD_DIR, session_id)


async def _forward_to_download_log(client, sent_msg, title, sender):
    """Forward sent media file to configured download log channel (Section 8)."""
    log_ch = await asyncio.to_thread(db.get_setting, "download_log_channel_id", "")
    if not log_ch:
        return
    try:
        user_label = getattr(sender, "username", None) or getattr(sender, "id", "Unknown")
        caption = f"{title}\n\n👤 دانلود شده توسط: @{user_label}" if str(user_label).isalnum() else f"{title}\n\n👤 دانلود شده توسط: {user_label}"
        target = int(log_ch) if log_ch.startswith("-") else log_ch
        await client.send_file(
            target,
            sent_msg.media,
            caption=caption,
        )
    except Exception as exc:
        logger.error("Could not forward download to log channel: %s", exc)
