"""Internationalisation for the YouTube downloader bot.

Usage::

    from i18n import t
    text = t("welcome", lang, name="Alice")
"""

from typing import Any

SUPPORTED_LANGS = ("fa", "en", "ru")
DEFAULT_LANG = "fa"

LANG_LABELS = {
    "fa": "🇮🇷 فارسی",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
}

# ── Reply-keyboard button keys ─────────────────────────────────────────
MENU_KEYS = [
    "btn_search",
    "btn_account",
    "btn_free_traffic",
    "btn_support",
    "btn_change_lang",
    "btn_guide",
    "btn_channel",
]

# ── Translations ───────────────────────────────────────────────────────
_STRINGS: dict[str, dict[str, str]] = {
    # ── Force Join ────────────────────────────────────────────────────
    "force_join_prompt": {
        "fa": (
            "📢 برای ادامه استفاده از ربات، لطفاً در کانال‌های زیر عضو شوید.\n\n"
            "📢 To continue using the bot, please join the channels below."
        ),
        "en": "📢 To continue using the bot, please join the channels below.",
        "ru": "📢 Чтобы продолжить использование бота, пожалуйста, подпишитесь на каналы ниже.",
    },
    "btn_joined": {
        "fa": "عضو شدم ✅",
        "en": "Joined ✅",
        "ru": "Подписался ✅",
    },
    "force_join_not_yet": {
        "fa": "❌ شما هنوز در تمام کانال‌ها عضو نشده‌اید! لطفاً ابتدا عضو شده و سپس دکمه زیر را بزنید.",
        "en": "❌ You have not joined all required channels yet! Please join and retry.",
        "ru": "❌ Вы еще не подписались на все необходимые каналы! Пожалуйста, подпишитесь и попробуйте снова.",
    },

    # ── Language selection ────────────────────────────────────────────
    "select_language": {
        "fa": "لطفاً زبان مورد نظر خود را انتخاب کنید:",
        "en": "Please select your language:",
        "ru": "Пожалуйста, выберите язык:",
    },
    "lang_changed": {
        "fa": "✅ زبان شما به فارسی تغییر یافت",
        "en": "✅ Your language has been set to English",
        "ru": "✅ Ваш язык изменен на Русский",
    },

    # ── Welcome ───────────────────────────────────────────────────────
    "welcome": {
        "fa": (
            "🌹 سلام خوش اومدی\n"
            "➕ با من ویدیوهای یوتیوب رو به صورت تصویری و صوتی دانلود کن.\n\n"
            "🔸 برای شروع و دریافت کمک، از دکمه‌های پایین استفاده کن و دانلود از یوتیوب رو آغاز کن:"
        ),
        "en": (
            "🌹 Welcome!\n"
            "➕ Download YouTube videos with me in high-quality video and audio formats.\n\n"
            "🔸 To get started and explore features, use the menu buttons below:"
        ),
        "ru": (
            "🌹 Добро пожаловать!\n"
            "➕ Скачивайте видео с YouTube в видео и аудио форматах с высоким качеством.\n\n"
            "🔸 Чтобы начать, используйте кнопки меню ниже:"
        ),
    },

    # ── Main menu buttons ─────────────────────────────────────────────
    "btn_search": {
        "fa": "🔍 جست‌وجو در یوتیوب",
        "en": "🔍 Search YouTube",
        "ru": "🔍 Поиск на YouTube",
    },
    "btn_account": {
        "fa": "👤 حساب من",
        "en": "👤 My Account",
        "ru": "👤 Мой аккаунт",
    },
    "btn_free_traffic": {
        "fa": "🚀 ترافیک رایگان",
        "en": "🚀 Free Traffic",
        "ru": "🚀 Бесплатный трафик",
    },
    "btn_support": {
        "fa": "☎️ پشتیبانی",
        "en": "☎️ Support",
        "ru": "☎️ Поддержка",
    },
    "btn_change_lang": {
        "fa": "🌐 تغییر زبان",
        "en": "🌐 Change Language",
        "ru": "🌐 Сменить язык",
    },
    "btn_guide": {
        "fa": "🍿 راهنمای دانلود از یوتیوب",
        "en": "🍿 YouTube Download Guide",
        "ru": "🍿 Руководство по скачиванию",
    },
    "btn_channel": {
        "fa": "📢 کانال اطلاع‌رسانی",
        "en": "📢 Information Channel",
        "ru": "📢 Канал новостей",
    },

    # ── Menu responses ────────────────────────────────────────────────
    "search_prompt": {
        "fa": (
            "🔎 جستجوی سریع ویدیو در یوتیوب\n\n"
            "کافیه لینک ویدیو رو کپی کنی و برای ربات بفرستی تا با هر کیفیتی خواستی به صورت فایل تلگرامی تحویل بگیری"
        ),
        "en": (
            "🔎 Quick YouTube Search\n\n"
            "Just copy and paste any YouTube link here to receive it as a Telegram file in your desired quality."
        ),
        "ru": (
            "🔎 Быстрый поиск YouTube\n\n"
            "Просто отправьте ссылку на видео YouTube сюда, чтобы скачать его в нужном качестве."
        ),
    },
    "account_text": {
        "fa": (
            "🆔 آیدی: {user_id}\n"
            "📥 کل دانلودها: {total_downloads}\n"
            "📊 دانلود امروز: {today_downloads}\n"
            "♻️ دانلود باقی‌مانده: {remaining_downloads}"
        ),
        "en": (
            "🆔 ID: {user_id}\n"
            "📥 Total downloads: {total_downloads}\n"
            "📊 Today's downloads: {today_downloads}\n"
            "♻️ Remaining downloads: {remaining_downloads}"
        ),
        "ru": (
            "🆔 ID: {user_id}\n"
            "📥 Всего загрузок: {total_downloads}\n"
            "📊 Загрузок сегодня: {today_downloads}\n"
            "♻️ Осталось загрузок: {remaining_downloads}"
        ),
    },
    "free_traffic_text": {
        "fa": (
            "سلام دوست عزیز! 🎉\n\n"
            "با دعوت از دوستانت به ربات ما، {bonus_count} دانلود رایگان هدیه بگیر! 🚀🎁\n\n"
            "فقط کافیه دوستانت روی لینک زیر کلیک کنن و به ربات بپیوندن تا این هدیه ویژه به حسابت اضافه بشه! 😍\n\n"
            "🔗 لینک دعوت:\n"
            "👉 {referral_link}"
        ),
        "en": (
            "Hello friend! 🎉\n\n"
            "Invite your friends to our bot and earn {bonus_count} free bonus downloads! 🚀🎁\n\n"
            "Just share your referral link with them:\n\n"
            "🔗 Invite link:\n"
            "👉 {referral_link}"
        ),
        "ru": (
            "Привет, друг! 🎉\n\n"
            "Приглашай друзей и получай {bonus_count} бонусных загрузок! 🚀🎁\n\n"
            "🔗 Ваша ссылка для приглашения:\n"
            "👉 {referral_link}"
        ),
    },
    "support_text": {
        "fa": "آیدی پشتیبانی جهت برقراری ارتباط: {support_id}",
        "en": "Support contact ID: {support_id}",
        "ru": "Контакты поддержки: {support_id}",
    },
    "channel_text": {
        "fa": "📢 کانال اطلاع‌رسانی:\n{channel_link}",
        "en": "📢 Information Channel:\n{channel_link}",
        "ru": "📢 Канал новостей:\n{channel_link}",
    },
    "guide_text": {
        "fa": (
            "📥 آموزش دانلود از یوتیوب با من!\n"
            "🚀 فقط کافیه لینک ویدیوی یوتیوب رو برام بفرستی، بعدش خودت انتخاب می‌کنی که با چه کیفیتی دانلود بشه! 🎬⬇️\n\n"
            "🔹 چطور لینک ویدیو رو کپی کنی؟\n"
            "1️⃣ وارد یوتیوب (YouTube) شو.\n"
            "2️⃣ ویدیوی موردنظرت رو باز کن.\n"
            "3️⃣ روی دکمه \"Share\" (اشتراک‌گذاری) بزن و \"Copy Link\" رو انتخاب کن.\n"
            "4️⃣ لینک رو همینجا بفرست، بعدش لیست کیفیت‌های مختلف نمایش داده میشه تا یکی رو انتخاب کنی!\n\n"
            "💡 حالا لینک ویدیوتو بفرست و با کیفیت دلخواه دانلود کن! 🎥⚡️"
        ),
        "en": (
            "📥 How to download from YouTube:\n"
            "🚀 Simply send me any YouTube link, then select your preferred quality! 🎬⬇️\n\n"
            "🔹 Steps:\n"
            "1️⃣ Open YouTube app or website.\n"
            "2️⃣ Find your video.\n"
            "3️⃣ Tap \"Share\" and choose \"Copy Link\".\n"
            "4️⃣ Paste the link here and select your format/quality.\n\n"
            "💡 Send a link now to start downloading! 🎥⚡️"
        ),
        "ru": (
            "📥 Как скачать видео с YouTube:\n"
            "🚀 Просто отправьте ссылку на видео, а затем выберите нужное качество! 🎬⬇️\n\n"
            "🔹 Инструкция:\n"
            "1️⃣ Откройте YouTube.\n"
            "2️⃣ Откройте видео.\n"
            "3️⃣ Нажмите «Поделиться» и «Копировать ссылку».\n"
            "4️⃣ Отправьте ссылку сюда и выберите качество.\n\n"
            "💡 Отправьте ссылку прямо сейчас! 🎥⚡️"
        ),
    },

    # ── Video info & download caption ─────────────────────────────────
    "video_info_caption": {
        "fa": (
            "👀 <b>مشخصات و اطلاعات ویدیو:</b>\n\n"
            "🎬 <b>عنوان:</b> {title}\n"
            "⏱ <b>مدت زمان:</b> {duration}\n"
            "📢 <b>کانال:</b> {uploader}\n"
            "👁 <b>تعداد بازدید:</b> {views}\n"
            "💬 <b>نظرات:</b> {comments}\n"
            "📅 <b>تاریخ انتشار:</b> {upload_date}\n\n"
            "👇 کیفیت یا فرمت دلخواه را انتخاب کنید:"
        ),
        "en": (
            "👀 <b>Video Details:</b>\n\n"
            "🎬 <b>Title:</b> {title}\n"
            "⏱ <b>Duration:</b> {duration}\n"
            "📢 <b>Channel:</b> {uploader}\n"
            "👁 <b>Views:</b> {views}\n"
            "💬 <b>Comments:</b> {comments}\n"
            "📅 <b>Release Date:</b> {upload_date}\n\n"
            "👇 Select your preferred format/quality:"
        ),
        "ru": (
            "👀 Информация о видео:\n"
            "📹 Название: {title}\n"
            "🕰 Длительность: {duration}\n"
            "📺 Канал: {uploader}\n"
            "👁 Просмотры: {views}\n"
            "🖨 Комментарии: {comments}\n"
            "📅 Дата: {upload_date}"
        ),
    },
    "playlist_info_caption": {
        "fa": (
            "📑 <b>اطلاعات پلی‌لیست یوتیوب:</b>\n\n"
            "📌 <b>عنوان:</b> {title}\n"
            "🔢 <b>تعداد کل ویدیوها:</b> {count}\n\n"
            "⚠️ حداکثر {max_items} ویدیو به ترتیب دانلود خواهند شد."
        ),
        "en": (
            "📑 Playlist Information:\n"
            "📌 Title: {title}\n"
            "🔢 Total videos: {count}\n\n"
            "⚠️ Up to {max_items} videos will be downloaded sequentially."
        ),
        "ru": (
            "📑 Информация о плейлисте:\n"
            "📌 Title: {title}\n"
            "🔢 Всего видео: {count}\n\n"
            "⚠️ До {max_items} видео будут загружены последовательно."
        ),
    },

    # ── Progress messages (Section 6.3 - Simple alternating messages) ──
    "status_downloading": {
        "fa": "⏳ در حال دانلود...",
        "en": "⏳ Downloading...",
        "ru": "⏳ Скачивание...",
    },
    "status_processing": {
        "fa": "⚙️ در حال پردازش...",
        "en": "⚙️ Processing...",
        "ru": "⚙️ Обработка...",
    },
    "status_waiting": {
        "fa": "🔄 کمی صبر کنید...",
        "en": "🔄 Please wait...",
        "ru": "🔄 Подождите...",
    },
    "status_uploading": {
        "fa": "📤 در حال آپلود...",
        "en": "📤 Uploading to Telegram...",
        "ru": "📤 Загрузка в Telegram...",
    },
    "status_done": {
        "fa": "✅ دانلود و ارسال با موفقیت انجام شد!",
        "en": "✅ Download and delivery completed successfully!",
        "ru": "✅ Загрузка и доставка успешно завершены!",
    },

    # ── Problem reporting & retries ───────────────────────────────────
    "btn_report_issue": {
        "fa": "⚠️ گزارش مشکل",
        "en": "⚠️ Report Issue",
        "ru": "⚠️ Сообщить об ошибке",
    },
    "issue_reported": {
        "fa": "✅ گزارش شما ثبت و به ادمین ارسال شد.",
        "en": "✅ Your report has been submitted to support.",
        "ru": "✅ Ваше сообщение передано администраторам.",
    },
    "download_incomplete": {
        "fa": "⏳ دانلود کامل نشد، می‌خوای دوباره تلاش کنم؟",
        "en": "⏳ Download was interrupted. Would you like to retry?",
        "ru": "⏳ Загрузка прервана. Хотите попробовать снова?",
    },
    "btn_retry_yes": {
        "fa": "بله، تلاش مجدد 🔄",
        "en": "Yes, retry 🔄",
        "ru": "Да, повторить 🔄",
    },
    "btn_retry_no": {
        "fa": "خیر ❌",
        "en": "No ❌",
        "ru": "Нет ❌",
    },

    # ── Limits & Protections ──────────────────────────────────────────
    "daily_limit_reached": {
        "fa": (
            "❌ سقف دانلود روزانه شما به پایان رسیده است!\n\n"
            "برای دریافت دانلودهای هدیه، از بخش «🚀 ترافیک رایگان» در منو، لینک خود را برای دوستانتان بفرستید."
        ),
        "en": (
            "❌ You have reached your daily download limit!\n\n"
            "To get extra bonus downloads, invite friends using your link in '🚀 Free Traffic'."
        ),
        "ru": (
            "❌ Вы достигли суточного лимита загрузок!\n\n"
            "Чтобы получить бонусные загрузки, приглашайте друзей через раздел «🚀 Бесплатный трафик»."
        ),
    },
    "rate_limit_exceeded": {
        "fa": "⚠️ تعداد درخواست‌های شما بالاست. لطفاً کمی صبر کنید.",
        "en": "⚠️ Too many requests. Please slow down and wait a moment.",
        "ru": "⚠️ Слишком много запросов. Пожалуйста, подождите немного.",
    },
    "maintenance_message": {
        "fa": "🔧 ربات موقتاً در حال به‌روزرسانیه، لطفاً بعداً امتحان کن.",
        "en": "🔧 The bot is currently under maintenance. Please check back later.",
        "ru": "🔧 Бот временно находится на техническом обслуживании. Пожалуйста, попробуйте позже.",
    },
    "banned_message": {
        "fa": "⛔ حساب کاربری شما مسدود شده است.",
        "en": "⛔ Your account has been suspended.",
        "ru": "⛔ Ваш аккаунт заблокирован.",
    },
    "fetch_error": {
        "fa": "نتوانستم اطلاعات ویدیو را دریافت کنم. ممکن است ویدیو خصوصی، دارای محدودیت سنی یا مسدود شده باشد.",
        "en": "Could not fetch video info. It may be private, age-restricted, or removed.",
        "ru": "Не удалось получить информацию о видео. Возможно, оно приватное или удалено.",
    },
    "unknown_size": {
        "fa": "~نامشخص",
        "en": "~Unknown",
        "ru": "~Неизвестно",
    },
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs: Any) -> str:
    """Return the localised string for *key* in *lang*, formatted with **kwargs.

    Checks database for admin-defined text overrides first, then falls back
    to _STRINGS bundle, then to the key itself.
    """
    import db
    try:
        custom = db.get_custom_text(key, lang)
        if custom:
            if kwargs:
                try:
                    return custom.format(**kwargs)
                except (KeyError, IndexError):
                    return custom
            return custom
    except Exception:
        pass

    bundle = _STRINGS.get(key)
    if bundle is None:
        return key
    text = bundle.get(lang) or bundle.get(DEFAULT_LANG) or bundle.get("en") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def menu_labels(lang: str = DEFAULT_LANG) -> list[str]:
    """Return the ordered list of reply-keyboard labels for *lang*."""
    return [t(key, lang) for key in MENU_KEYS]
