"""Internationalisation for the YouTube downloader bot.

Usage::

    from i18n import t
    text = t("welcome", lang, name="Alice")
"""

from typing import Any

SUPPORTED_LANGS = ("fa", "en", "ru")
DEFAULT_LANG = "fa"

# Language display names for the language-picker buttons
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
    # ── Language selection ────────────────────────────────────────────
    "select_language": {
        "fa": "لطفاً زبان خود را انتخاب کنید",
        "en": "Please select your language",
        "ru": "Пожалуйста, выберите язык",
    },
    "welcome": {
        "fa": "خوش آمدید! من یک ربات دانلود از یوتیوب هستم. لینک ویدیو را بفرستید تا آن را برایتان دانلود کنم.",
        "en": "Welcome! I'm a YouTube downloader bot. Send me a video link and I'll download it for you.",
        "ru": "Добро пожаловать! Я бот для скачивания с YouTube. Отправьте ссылку на видео, и я скачаю его для вас.",
    },

    # ── Main menu ─────────────────────────────────────────────────────
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

    # ── Search ────────────────────────────────────────────────────────
    "search_prompt": {
        "fa": "لینک ویدیوی یوتیوب را بفرستید تا آن را برایتان دانلود کنم.",
        "en": "Send me a YouTube video link and I'll download it for you.",
        "ru": "Отправьте ссылку на видео YouTube, и я скачаю его для вас.",
    },

    # ── Account ───────────────────────────────────────────────────────
    "account_title": {
        "fa": "👤 حساب من",
        "en": "👤 My Account",
        "ru": "👤 Мой аккаунт",
    },
    "account_user_id": {
        "fa": "آیدی تلگرام",
        "en": "Telegram ID",
        "ru": "Telegram ID",
    },
    "account_username": {
        "fa": "نام کاربری",
        "en": "Username",
        "ru": "Имя пользователя",
    },
    "account_total_downloads": {
        "fa": "کل دانلودها",
        "en": "Total downloads",
        "ru": "Всего загрузок",
    },
    "account_today_downloads": {
        "fa": "دانلودهای امروز",
        "en": "Today's downloads",
        "ru": "Загрузки сегодня",
    },
    "account_daily_limit": {
        "fa": "سقف روزانه",
        "en": "Daily limit",
        "ru": "Дневной лимит",
    },
    "account_unlimited": {
        "fa": "نامحدود",
        "en": "Unlimited",
        "ru": "Безлимитно",
    },
    "account_not_set": {
        "fa": "تنظیم نشده",
        "en": "Not configured",
        "ru": "Не настроено",
    },
    "account_none": {
        "fa": "ندارد",
        "en": "None",
        "ru": "Нет",
    },

    # ── Free traffic ──────────────────────────────────────────────────
    "free_traffic_placeholder": {
        "fa": "بزودی این بخش فعال خواهد شد. فعلاً در حال توسعه است.",
        "en": "This feature is coming soon. Currently under development.",
        "ru": "Эта функция скоро появится. В данный момент в разработке.",
    },

    # ── Support ───────────────────────────────────────────────────────
    "support_text": {
        "fa": "برای پشتیبانی به آیدی زیر پیام دهید: {support_id}",
        "en": "For support, please message: {support_id}",
        "ru": "Для поддержки напишите: {support_id}",
    },
    "support_not_set": {
        "fa": "اطلاعات پشتیبانی در حال حاضر تنظیم نشده است.",
        "en": "Support is not configured at the moment.",
        "ru": "Поддержка в данный момент не настроена.",
    },

    # ── Change language ───────────────────────────────────────────────
    "lang_changed": {
        "fa": "زبان تغییر کرد. ✅",
        "en": "Language changed. ✅",
        "ru": "Язы изменён. ✅",
    },

    # ── Guide ─────────────────────────────────────────────────────────
    "guide_text": {
        "fa": (
            "🍿 راهنمای دانلود از یوتیوب\n\n"
            "۱. وارد اپلیکیشن یا سایت یوتیوب شوید.\n"
            "۲. ویدیوی مورد نظر را پیدا کنید.\n"
            "۳. روی دکمه «Share» یا «اشتراک‌گذاری» بزنید.\n"
            "۴. گزینه «Copy link» یا «کپی لینک» را انتخاب کنید.\n"
            "۵. لینک کپی شده را در اینجا بفرستید.\n"
            "۶. فرمت (ویدیو یا صدا) و کیفیت را انتخاب کنید.\n"
            "۷. منتظر بمانید تا فایل دانلود و ارسال شود."
        ),
        "en": (
            "🍿 YouTube Download Guide\n\n"
            "1. Open the YouTube app or website.\n"
            "2. Find the video you want.\n"
            "3. Tap the \"Share\" button.\n"
            "4. Select \"Copy link\".\n"
            "5. Paste the link here in this chat.\n"
            "6. Choose format (Video or Audio) and quality.\n"
            "7. Wait for the file to be downloaded and sent."
        ),
        "ru": (
            "🍿 Руководство по скачиванию с YouTube\n\n"
            "1. Откройте приложение или сайт YouTube.\n"
            "2. Найдите нужное видео.\n"
            "3. Нажмите кнопку «Поделиться».\n"
            "4. Выберите «Копировать ссылку».\n"
            "5. Вставьте ссылку сюда в чат.\n"
            "6. Выберите формат (видео или аудио) и качество.\n"
            "7. Дождитесь загрузки и отправки файла."
        ),
    },

    # ── Channel ───────────────────────────────────────────────────────
    "channel_text": {
        "fa": "📢 کانال اطلاع‌رسانی: {channel_link}",
        "en": "📢 Information channel: {channel_link}",
        "ru": "📢 Канал новостей: {channel_link}",
    },
    "channel_not_set": {
        "fa": "کانال اطلاع‌رسانی در حال حاضر تنظیم نشده است.",
        "en": "The information channel is not configured yet.",
        "ru": "Канал новостей пока не настроен.",
    },

    # ── Download flow ─────────────────────────────────────────────────
    "fetching_info": {
        "fa": "در حال دریافت اطلاعات ویدیو…",
        "en": "Fetching video info…",
        "ru": "Получение информации о видео…",
    },
    "fetch_timeout": {
        "fa": "دریافت اطلاعات ویدیو زمان‌بر بود. لطفاً دوباره تلاش کنید.",
        "en": "Fetching video info timed out. Please try again.",
        "ru": "Получение информации о видео заняло слишком много времени. Попробуйте снова.",
    },
    "fetch_error": {
        "fa": "نتوانستم اطلاعات ویدیو را دریافت کنم. ممکن است ویدیو خصوصی، محدود سن یا در دسترس نباشد.",
        "en": "Could not fetch video info. The video might be private, age-restricted, or unavailable.",
        "ru": "Не удалось получить информацию о видео. Возможно, видео приватное, имеет возрастные ограничения или недоступно.",
    },
    "choose_format": {
        "fa": "فرمت را انتخاب کنید:",
        "en": "Choose a format:",
        "ru": "Выберите формат:",
    },
    "video": {
        "fa": "ویدیو",
        "en": "Video",
        "ru": "Видео",
    },
    "audio": {
        "fa": "صدا",
        "en": "Audio",
        "ru": "Аудио",
    },
    "select_quality": {
        "fa": "کیفیت ویدیو را انتخاب کنید:",
        "en": "Select video quality:",
        "ru": "Выберите качество видео:",
    },
    "downloading_video": {
        "fa": "در حال دانلود ویدیو ({quality}p)…",
        "en": "Downloading video ({quality}p)…",
        "ru": "Скачивание видео ({quality}p)…",
    },
    "downloading_audio": {
        "fa": "در حال دانلود صدا…",
        "en": "Downloading audio…",
        "ru": "Скачивание аудио…",
    },
    "uploading": {
        "fa": "در حال ارسال {size}…",
        "en": "Uploading {size}…",
        "ru": "Отправка {size}…",
    },
    "done": {
        "fa": "تمام شد! فایل ارسال شد.",
        "en": "Done! Your file has been sent.",
        "ru": "Готово! Файл отправлен.",
    },
    "file_empty": {
        "fa": "فایل دانلود شده خالی است. ممکن است ویدیو در دسترس نباشد.",
        "en": "The downloaded file is empty. The video may be unavailable.",
        "ru": "Загруженный файл пуст. Возможно, видео недоступно.",
    },
    "file_too_large": {
        "fa": "فایل خیلی بزرگ است ({size}). حداکثر حجم مجاز: {max_size}.",
        "en": "File is too large ({size}). Maximum supported size: {max_size}.",
        "ru": "Файл слишком большой ({size}). Максимальный размер: {max_size}.",
    },
    "already_downloading": {
        "fa": "شما یک دانلود در حال انجام دارید. لطفاً صبر کنید.",
        "en": "You already have a download in progress. Please wait.",
        "ru": "У вас уже есть активная загрузка. Пожалуйста, подождите.",
    },
    "expired": {
        "fa": "این انتخاب منقضی شده است. لینک را دوباره بفرستید.",
        "en": "This selection has expired. Send the URL again.",
        "ru": "Этот выбор истёк. Отправьте ссылку снова.",
    },
    "not_yours": {
        "fa": "این درخواست شما نیست.",
        "en": "This isn't your request.",
        "ru": "Это не ваш запрос.",
    },
    "flood_wait": {
        "fa": "تلگرام درخواست کرد {seconds} ثانیه صبر کنید. لطفاً بعداً تلاش کنید.",
        "en": "Telegram asked us to wait {seconds}s. Please try again later.",
        "ru": "Telegram просит подождать {seconds} сек. Попробуйте позже.",
    },
    "timeout": {
        "fa": "عملیات زمان‌بر بود. لطفاً دوباره تلاش کنید.",
        "en": "The operation timed out. Please try again.",
        "ru": "Время операции истекло. Попробуйте снова.",
    },
    "no_file": {
        "fa": "دانلود ناموفق بود — هیچ فایلی تولید نشد.",
        "en": "Download failed — no output file was produced.",
        "ru": "Загрузка не удалась — файл не создан.",
    },
    "generic_error": {
        "fa": "مشکلی پیش آمد. لطفاً بعداً تلاش کنید.",
        "en": "Something went wrong. Please try again later.",
        "ru": "Что-то пошло не так. Попробуйте позже.",
    },
    "channel": {
        "fa": "کانال",
        "en": "Channel",
        "ru": "Канал",
    },
    "duration": {
        "fa": "مدت",
        "en": "Duration",
        "ru": "Длительность",
    },
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs: Any) -> str:
    """Return the localised string for *key* in *lang*, formatted with **kwargs.

    Falls back to English, then to the key itself if the key is missing.
    """
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
