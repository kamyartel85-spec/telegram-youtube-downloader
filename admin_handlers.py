"""Admin panel handlers and commands (Reply Keyboard & Direct Admin Actions)."""

import asyncio
import io
import json
import logging
from telethon import events, Button

import db
from config import OWNER_ID
from keyboards import ADMIN_BUTTONS, admin_main_keyboard, main_menu_keyboard
from utils import format_size

logger = logging.getLogger(__name__)


async def _is_admin(user_id):
    """Check if user_id has admin rights."""
    if OWNER_ID and user_id == OWNER_ID:
        return {"user_id": user_id, "role": "owner"}
    return await asyncio.to_thread(db.get_admin, user_id)


def register_admin_handlers(client):
    """Register all admin-related event handlers."""

    # ------------------------------------------------------------------
    # /admin command
    # ------------------------------------------------------------------
    @client.on(events.NewMessage(pattern=r"^/admin\b"))
    async def admin_entry(event):
        admin = await _is_admin(event.sender_id)
        if not admin:
            return

        role = admin.get("role", "viewer")
        await event.respond(
            f"🛠 به پنل مدیریت خوش آمدید.\n"
            f"👤 سطح دسترسی شما: <b>{role}</b>\n\n"
            f"برای انجام امور، یکی از دکمه‌های زیر را انتخاب کنید:",
            parse_mode="html",
            buttons=admin_main_keyboard(role),
        )

    # ------------------------------------------------------------------
    # Reply Keyboard Menu Navigation
    # ------------------------------------------------------------------
    @client.on(events.NewMessage)
    async def admin_buttons_router(event):
        # Filter only if message text matches an admin button
        text = (event.raw_text or "").strip()
        if text not in ADMIN_BUTTONS.values():
            return

        admin = await _is_admin(event.sender_id)
        if not admin:
            return

        role = admin.get("role", "viewer")

        # ⬅️ خروج از پنل ادمین
        if text == ADMIN_BUTTONS["exit"]:
            u = await asyncio.to_thread(db.get_user, event.sender_id)
            lang = u.get("language", "fa") if u else "fa"
            await event.respond(
                "✅ از پنل ادمین خارج شدید و به منوی اصلی بازگشتید.",
                buttons=main_menu_keyboard(lang),
            )
            return

        # 📊 آمار ربات
        if text == ADMIN_BUTTONS["stats"]:
            stats = await asyncio.to_thread(db.get_growth_stats)
            cached = await asyncio.to_thread(db.get_cache_stats)
            msg = (
                "📊 <b>آمار جامع ربات</b>\n\n"
                f"👥 کل کاربران: <b>{stats['total_users']:,}</b>\n"
                f"⚡ کاربران فعال امروز: <b>{stats['active_users_today']:,}</b>\n"
                f"🗓 کاربران فعال این ماه: <b>{stats['active_users_month']:,}</b>\n\n"
                f"📥 کل دانلودها: <b>{stats['total_downloads']:,}</b>\n"
                f"📥 دانلودهای امروز: <b>{stats['downloads_today']:,}</b>\n"
                f"❌ دانلودهای ناموفق: <b>{stats['failed_downloads']:,}</b>\n"
                f"💾 کل ترافیک دانلود: <b>{format_size(stats['total_bytes'])}</b>\n\n"
                f"🗄 فایل‌های کش شده: <b>{cached['count']}</b> ({format_size(cached['total_size'])})"
            )
            await event.respond(msg, parse_mode="html")
            return

        # 🗂 کش و فایل‌ها
        if text == ADMIN_BUTTONS["cache"]:
            cached = await asyncio.to_thread(db.get_cache_stats)
            msg = (
                "🗂 <b>مدیریت کش فایل‌ها</b>\n\n"
                f"تعداد فایل‌های کش شده در دیتابیس: <b>{cached['count']}</b>\n"
                f"حجم کل تخمینی: <b>{format_size(cached['total_size'])}</b>\n\n"
                "برای خالی کردن کش دستور زیر را ارسال کنید:\n"
                "👉 <code>/clear_cache</code>"
            )
            await event.respond(msg, parse_mode="html")
            return

        # 🧾 لیست خطاها
        if text == ADMIN_BUTTONS["errors"]:
            errors = await asyncio.to_thread(db.get_recent_errors, 10)
            if not errors:
                await event.respond("✅ هیچ خطایی در لاگ‌ها ثبت نشده است.")
                return
            lines = ["🧾 <b>آخرین خطاهای ثبت شده:</b>\n"]
            for err in errors:
                uid = err.get("user_id") or "Unknown"
                time_str = err.get("created_at", "")[:19].replace("T", " ")
                msg_snippet = (err.get("error_message") or "")[:120]
                lines.append(f"• <b>User {uid}</b> [{time_str}]:\n  <code>{msg_snippet}</code>\n")
            await event.respond("\n".join(lines), parse_mode="html")
            return

        # Rest of actions require 'full' or 'owner' role
        if role == "viewer":
            await event.respond("⛔ شما تنها به مشاهده آمار و لاگ‌ها دسترسی دارید.")
            return

        # 👥 مدیریت کاربران
        if text == ADMIN_BUTTONS["users"]:
            msg = (
                "👥 <b>راهنمای مدیریت کاربران:</b>\n\n"
                "🔍 جستجوی کاربر:\n<code>/user 123456789</code> یا <code>/user username</code>\n\n"
                "⛔ بن کردن:\n<code>/ban 123456789</code>\n\n"
                "✅ رفع بن:\n<code>/unban 123456789</code>\n\n"
                "🎁 افزودن دانلود هدیه:\n<code>/add_bonus 123456789 10</code>\n\n"
                "♾ تنظیم محدودیت اختصاصی:\n<code>/set_limit 123456789 50</code> (یا 0 برای نامحدود)\n\n"
                "📥 دریافت فایل CSV کل کاربران:\n<code>/export_users</code>"
            )
            await event.respond(msg, parse_mode="html")
            return

        # 📢 پیام همگانی
        if text == ADMIN_BUTTONS["broadcast"]:
            msg = (
                "📢 <b>ارسال پیام همگانی به کاربران فعال</b>\n\n"
                "شما می‌توانید پیام را فقط به کاربرانی که در چند ماه اخیر فعال بوده‌اند بفرستید.\n\n"
                "دستور:\n"
                "<code>/broadcast &lt;تعداد ماه&gt;\nمتن پیام شما</code>\n\n"
                "مثال برای ارسال به کاربران فعال در ۳ ماه اخیر:\n"
                "<code>/broadcast 3\nسلام به تمام کاربران عزیز! نسخه جدید ربات فعال شد.</code>"
            )
            await event.respond(msg, parse_mode="html")
            return

        # ⚙️ تنظیمات ربات
        if text == ADMIN_BUTTONS["settings"]:
            settings = await asyncio.to_thread(db.get_all_settings)
            fj = "روشن ✅" if settings.get("force_join_enabled") == "1" else "خاموش ❌"
            dl_lim = f"{settings.get('daily_limit_count', '10')} در روز" if settings.get("daily_limit_enabled") == "1" else "نامحدود ❌"
            ref_b = settings.get("referral_bonus", "3")
            supp = settings.get("support_id", "@Support")
            chan = settings.get("channel_link", "ندارد")
            dl_log = settings.get("download_log_channel_id") or "تنظیم نشده"
            err_log = settings.get("error_log_channel_id") or "تنظیم نشده"
            max_pl = settings.get("max_playlist_items", "25")

            msg = (
                "⚙️ <b>تنظیمات فعلی ربات:</b>\n\n"
                f"• جوین اجباری: <b>{fj}</b>\n"
                f"• محدودیت روزانه: <b>{dl_lim}</b>\n"
                f"• دانلود هدیه رفرال: <b>{ref_b}</b>\n"
                f"• آیدی پشتیبانی: <code>{supp}</code>\n"
                f"• کانال اطلاع‌رسانی: {chan}\n"
                f"• کانال لاگ دانلود: <code>{dl_log}</code>\n"
                f"• کانال لاگ خطا: <code>{err_log}</code>\n"
                f"• سقف دانلود پلی‌لیست: <b>{max_pl}</b>\n\n"
                "<b>دستورات تغییر:</b>\n"
                "• <code>/set_force_join 1</code> یا <code>0</code>\n"
                "• <code>/add_channel &lt;نام&gt; &lt;لینک&gt;</code>\n"
                "• <code>/del_channel &lt;نام&gt;</code>\n"
                "• <code>/set_daily_limit &lt;1 یا 0&gt; &lt;تعداد&gt;</code>\n"
                "• <code>/set_ref_bonus &lt;تعداد&gt;</code>\n"
                "• <code>/set_support &lt;آیدی&gt;</code>\n"
                "• <code>/set_channel &lt;لینک&gt;</code>\n"
                "• <code>/set_dl_log &lt;channel_id&gt;</code>\n"
                "• <code>/set_err_log &lt;channel_id&gt;</code>\n"
                "• <code>/set_max_playlist &lt;تعداد&gt;</code>"
            )
            await event.respond(msg, parse_mode="html")
            return

        # 💬 ویرایش متن‌ها
        if text == ADMIN_BUTTONS["texts"]:
            msg = (
                "💬 <b>ویرایش متن‌های ربات:</b>\n\n"
                "شما می‌توانید هر متنی را به صورت زنده برای هر زبانی تغییر دهید.\n\n"
                "دستور:\n"
                "<code>/set_text &lt;fa/en/ru&gt; &lt;کلید&gt;\nمتن جدید</code>\n\n"
                "کلیدهای پرکاربرد:\n"
                "• <code>welcome</code> (پیام شروع)\n"
                "• <code>guide_text</code> (راهنما)\n"
                "• <code>search_prompt</code> (متن جستجو)\n"
                "• <code>free_traffic_text</code> (متن رفرال)\n"
                "• <code>support_text</code> (متن پشتیبانی)"
            )
            await event.respond(msg, parse_mode="html")
            return

        # 🔧 مود تعمیر
        if text == ADMIN_BUTTONS["maintenance"]:
            settings = await asyncio.to_thread(db.get_all_settings)
            cur = settings.get("maintenance_mode", "0")
            new_val = "0" if cur == "1" else "1"
            await asyncio.to_thread(db.set_setting, "maintenance_mode", new_val)
            state_str = "فعال 🔴 (کاربران عادی مسدود می‌شوند)" if new_val == "1" else "غیرفعال 🟢 (ربات باز است)"
            await event.respond(f"🔧 مود تعمیر اکنون <b>{state_str}</b> است.", parse_mode="html")
            return

        # 👮 مدیریت ادمین‌ها (Only owner)
        if text == ADMIN_BUTTONS["admins"]:
            if role != "owner":
                await event.respond("⛔ فقط مالک اصلی (Owner) اجازه مدیریت ادمین‌ها را دارد.")
                return
            admins = await asyncio.to_thread(db.get_all_admins)
            lines = ["👮 <b>لیست ادمین‌های ربات:</b>\n"]
            for a in admins:
                lines.append(f"• کاربر <code>{a['user_id']}</code> | نقش: <b>{a['role']}</b>")
            lines.append("\n<b>دستورات:</b>")
            lines.append("• <code>/add_admin &lt;user_id&gt; &lt;full/viewer&gt;</code>")
            lines.append("• <code>/del_admin &lt;user_id&gt;</code>")
            await event.respond("\n".join(lines), parse_mode="html")
            return

    # ------------------------------------------------------------------
    # Admin Commands Implementations
    # ------------------------------------------------------------------

    # /clear_cache
    @client.on(events.NewMessage(pattern=r"^/clear_cache\b"))
    async def cmd_clear_cache(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        await asyncio.to_thread(db.clear_cache)
        await event.respond("✅ کل کش فایل‌ها از دیتابیس پاک شد.")

    # /export_users
    @client.on(events.NewMessage(pattern=r"^/export_users\b"))
    async def cmd_export_users(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        csv_data = await asyncio.to_thread(db.export_users_csv)
        file_obj = io.BytesIO(csv_data.encode("utf-8"))
        file_obj.name = "users_export.csv"
        await client.send_file(
            event.chat_id,
            file_obj,
            caption="📁 خروجی اکسپورت کل کاربران دیتابیس",
        )

    # /user <id or username>
    @client.on(events.NewMessage(pattern=r"^/user\s+(\S+)"))
    async def cmd_find_user(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        query = event.pattern_match.group(1).strip()
        results = await asyncio.to_thread(db.search_users, query)
        if not results:
            await event.respond("❌ کاربری با این مشخصات یافت نشد.")
            return
        u = results[0]
        lim_str = "پیش‌فرض" if u.get("custom_daily_limit") is None else str(u["custom_daily_limit"])
        banned_str = "بله 🔴" if u.get("is_banned") else "خیر 🟢"
        msg = (
            f"👤 <b>اطلاعات کاربر:</b>\n\n"
            f"🆔 آیدی: <code>{u['user_id']}</code>\n"
            f"🏷 یوزرنیم: @{u.get('username') or 'ندارد'}\n"
            f"🌐 زبان: {u.get('language') or 'fa'}\n"
            f"📅 عضویت: {str(u.get('joined_at', ''))[:19]}\n"
            f"⛔ وضعیت بن: {banned_str}\n"
            f"🎁 دانلودهای هدیه: <b>{u.get('bonus_downloads') or 0}</b>\n"
            f"♾ سقف روزانه اختصاصی: <b>{lim_str}</b>\n"
            f"👥 دعوت شده توسط: <code>{u.get('referred_by') or 'هیچ‌کس'}</code>"
        )
        await event.respond(msg, parse_mode="html")

    # /ban <id> & /unban <id>
    @client.on(events.NewMessage(pattern=r"^/(ban|unban)\s+(\d+)"))
    async def cmd_ban_toggle(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        action = event.pattern_match.group(1)
        target_id = int(event.pattern_match.group(2))
        is_banned = 1 if action == "ban" else 0
        await asyncio.to_thread(db.update_user, target_id, is_banned=is_banned)
        label = "بن" if is_banned else "رفع بن"
        await event.respond(f"✅ کاربر <code>{target_id}</code> با موفقیت {label} شد.", parse_mode="html")

    # /add_bonus <id> <count>
    @client.on(events.NewMessage(pattern=r"^/add_bonus\s+(\d+)\s+(\d+)"))
    async def cmd_add_bonus(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        target_id = int(event.pattern_match.group(1))
        bonus = int(event.pattern_match.group(2))
        u = await asyncio.to_thread(db.get_user, target_id)
        if not u:
            await event.respond("❌ کاربر یافت نشد.")
            return
        cur_bonus = u.get("bonus_downloads") or 0
        await asyncio.to_thread(db.update_user, target_id, bonus_downloads=cur_bonus + bonus)
        await event.respond(f"✅ تعداد {bonus} دانلود هدیه به کاربر {target_id} اضافه شد.")

    # /set_limit <id> <count>
    @client.on(events.NewMessage(pattern=r"^/set_limit\s+(\d+)\s+(\d+)"))
    async def cmd_set_limit(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        target_id = int(event.pattern_match.group(1))
        limit_val = int(event.pattern_match.group(2))
        # if limit_val == 0, unlimited or 999999
        val = 999999 if limit_val == 0 else limit_val
        await asyncio.to_thread(db.update_user, target_id, custom_daily_limit=val)
        desc = "نامحدود" if limit_val == 0 else str(limit_val)
        await event.respond(f"✅ سقف روزانه کاربر {target_id} روی {desc} تنظیم شد.")

    # /broadcast <months>\n<message>
    @client.on(events.NewMessage(pattern=r"^/broadcast\s+(\d+)\s*([\s\S]*)"))
    async def cmd_broadcast(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        months = int(event.pattern_match.group(1))
        message_text = event.pattern_match.group(2).strip()
        if not message_text:
            await event.respond("❌ لطفاً متن پیام را در خط بعدی ارسال کنید.")
            return

        status_msg = await event.respond("⏳ در حال جمع‌آوری لیست کاربران فعال و ارسال...")
        user_ids = await asyncio.to_thread(db.get_active_users_since, months)
        success = 0
        failed = 0

        for uid in user_ids:
            try:
                await client.send_message(uid, message_text)
                success += 1
                await asyncio.sleep(0.05)
            except Exception:
                failed += 1

        await status_msg.edit(
            f"📢 <b>گزارش ارسال پیام همگانی:</b>\n\n"
            f"✅ ارسال موفق: <b>{success}</b>\n"
            f"❌ ارسال ناموفق: <b>{failed}</b>\n"
            f"👥 کل هدف (فعال در {months} ماه گذشته): <b>{len(user_ids)}</b>",
            parse_mode="html",
        )

    # Settings commands: /set_force_join, /set_daily_limit, /set_ref_bonus, etc.
    @client.on(events.NewMessage(pattern=r"^/set_force_join\s+([01])"))
    async def cmd_set_force_join(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        val = event.pattern_match.group(1)
        await asyncio.to_thread(db.set_setting, "force_join_enabled", val)
        await event.respond(f"✅ جوین اجباری روی {'روشن' if val == '1' else 'خاموش'} تنظیم شد.")

    @client.on(events.NewMessage(pattern=r"^/add_channel\s+(\S+)\s+(\S+)"))
    async def cmd_add_channel(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        name = event.pattern_match.group(1)
        url = event.pattern_match.group(2)
        raw_list = await asyncio.to_thread(db.get_setting, "force_join_channels", "[]")
        try:
            channels = json.loads(raw_list)
        except Exception:
            channels = []
        channels.append({"name": name, "url": url})
        await asyncio.to_thread(db.set_setting, "force_join_channels", json.dumps(channels, ensure_ascii=False))
        await event.respond(f"✅ کانال {name} به لیست جوین اجباری اضافه شد.")

    @client.on(events.NewMessage(pattern=r"^/del_channel\s+(\S+)"))
    async def cmd_del_channel(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        name = event.pattern_match.group(1)
        raw_list = await asyncio.to_thread(db.get_setting, "force_join_channels", "[]")
        try:
            channels = json.loads(raw_list)
        except Exception:
            channels = []
        channels = [c for c in channels if c.get("name") != name]
        await asyncio.to_thread(db.set_setting, "force_join_channels", json.dumps(channels, ensure_ascii=False))
        await event.respond(f"✅ کانال {name} از لیست حذف شد.")

    @client.on(events.NewMessage(pattern=r"^/set_daily_limit\s+([01])(?:\s+(\d+))?"))
    async def cmd_set_daily_limit(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        enabled = event.pattern_match.group(1)
        count = event.pattern_match.group(2)
        await asyncio.to_thread(db.set_setting, "daily_limit_enabled", enabled)
        if count:
            await asyncio.to_thread(db.set_setting, "daily_limit_count", count)
        await event.respond("✅ تنظیمات محدودیت روزانه ذخیره شد.")

    @client.on(events.NewMessage(pattern=r"^/set_ref_bonus\s+(\d+)"))
    async def cmd_set_ref_bonus(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        val = event.pattern_match.group(1)
        await asyncio.to_thread(db.set_setting, "referral_bonus", val)
        await event.respond(f"✅ پاداش دعوت روی {val} دانلود تنظیم شد.")

    @client.on(events.NewMessage(pattern=r"^/set_support\s+(\S+)"))
    async def cmd_set_support(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        val = event.pattern_match.group(1)
        await asyncio.to_thread(db.set_setting, "support_id", val)
        await event.respond(f"✅ آیدی پشتیبانی روی {val} تنظیم شد.")

    @client.on(events.NewMessage(pattern=r"^/set_channel\s+(\S+)"))
    async def cmd_set_channel(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        val = event.pattern_match.group(1)
        await asyncio.to_thread(db.set_setting, "channel_link", val)
        await event.respond(f"✅ لینک کانال اطلاع‌رسانی روی {val} تنظیم شد.")

    @client.on(events.NewMessage(pattern=r"^/set_dl_log\s+(\S+)"))
    async def cmd_set_dl_log(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        val = event.pattern_match.group(1)
        await asyncio.to_thread(db.set_setting, "download_log_channel_id", val)
        await event.respond(f"✅ کانال لاگ دانلود روی {val} تنظیم شد.")

    @client.on(events.NewMessage(pattern=r"^/set_err_log\s+(\S+)"))
    async def cmd_set_err_log(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        val = event.pattern_match.group(1)
        await asyncio.to_thread(db.set_setting, "error_log_channel_id", val)
        await event.respond(f"✅ کانال لاگ خطاها روی {val} تنظیم شد.")

    @client.on(events.NewMessage(pattern=r"^/set_max_playlist\s+(\d+)"))
    async def cmd_set_max_playlist(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        val = event.pattern_match.group(1)
        await asyncio.to_thread(db.set_setting, "max_playlist_items", val)
        await event.respond(f"✅ سقف دانلود پلی‌لیست روی {val} تنظیم شد.")

    # /set_text <lang> <key>\n<text>
    @client.on(events.NewMessage(pattern=r"^/set_text\s+(fa|en|ru)\s+(\S+)\s*([\s\S]*)"))
    async def cmd_set_text(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") == "viewer":
            return
        lang = event.pattern_match.group(1)
        key = event.pattern_match.group(2)
        new_text = event.pattern_match.group(3).strip()
        if not new_text:
            await event.respond("❌ لطفاً متن جدید را در ادامه یا خط بعدی وارد کنید.")
            return
        await asyncio.to_thread(db.set_custom_text, key, lang, new_text)
        await event.respond(f"✅ متن کلید <code>{key}</code> برای زبان <b>{lang}</b> بروزرسانی شد.", parse_mode="html")

    # /add_admin <user_id> <role> (Owner only)
    @client.on(events.NewMessage(pattern=r"^/add_admin\s+(\d+)\s+(full|viewer)"))
    async def cmd_add_admin(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") != "owner":
            return
        target_id = int(event.pattern_match.group(1))
        role = event.pattern_match.group(2)
        await asyncio.to_thread(db.add_admin, target_id, role)
        await event.respond(f"✅ ادمین <code>{target_id}</code> با نقش <b>{role}</b> اضافه شد.", parse_mode="html")

    # /del_admin <user_id> (Owner only)
    @client.on(events.NewMessage(pattern=r"^/del_admin\s+(\d+)"))
    async def cmd_del_admin(event):
        admin = await _is_admin(event.sender_id)
        if not admin or admin.get("role") != "owner":
            return
        target_id = int(event.pattern_match.group(1))
        ok = await asyncio.to_thread(db.remove_admin, target_id)
        if ok:
            await event.respond(f"✅ ادمین <code>{target_id}</code> حذف شد.", parse_mode="html")
        else:
            await event.respond("❌ امکان حذف این ادمین وجود ندارد (ممکن است مالک باشد).")
