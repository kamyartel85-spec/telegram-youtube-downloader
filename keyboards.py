"""Keyboard builders for the YouTube downloader bot (User & Admin)."""

from telethon import Button
from i18n import t, LANG_LABELS, SUPPORTED_LANGS, menu_labels


# ----------------------------------------------------------------------
# User Keyboards
# ----------------------------------------------------------------------
def main_menu_keyboard(lang="fa"):
    """Build the reply-keyboard for regular users."""
    labels = menu_labels(lang)
    # 0: search, 1: account, 2: free_traffic, 3: support, 4: change_lang, 5: guide, 6: channel
    return [
        [Button.text(labels[0], resize=True)],
        [Button.text(labels[1]), Button.text(labels[2])],
        [Button.text(labels[3])],
        [Button.text(labels[4]), Button.text(labels[5])],
        [Button.text(labels[6])],
    ]


def lang_inline_keyboard():
    """Inline buttons for selecting a language."""
    return [
        [Button.inline(LANG_LABELS[lang], data=f"lang:{lang}")]
        for lang in SUPPORTED_LANGS
    ]


def force_join_keyboard(channels, lang="fa"):
    """Inline keyboard listing required channels + Joined button."""
    buttons = []
    for ch in channels:
        name = ch.get("name", "Channel")
        url = ch.get("url", "https://t.me")
        buttons.append([Button.url(f"📢 {name}", url)])
    buttons.append([Button.inline(t("btn_joined", lang), data="check_join")])
    return buttons


def quality_and_format_keyboard(download_id, format_sizes=None, lang="fa"):
    """Inline buttons for formats/qualities according to Section 5.1."""
    if format_sizes is None:
        format_sizes = {}

    def _sz(key):
        return format_sizes.get(key, t("unknown_size", lang))

    # Row 1: Audio formats
    audio_row = [
        Button.inline(f"🎧 mp3 متوسط ({_sz('mp3_medium')})", data=f"dl:{download_id}:a_med"),
        Button.inline(f"🎧 mp3 بهترین ({_sz('mp3_best')})", data=f"dl:{download_id}:a_best"),
    ]

    # Video rows (one quality per row)
    video_rows = [
        [Button.inline(f"🎥 144p ({_sz('144')})", data=f"dl:{download_id}:v_144")],
        [Button.inline(f"🎥 240p ({_sz('240')})", data=f"dl:{download_id}:v_240")],
        [Button.inline(f"🎥 360p ({_sz('360')})", data=f"dl:{download_id}:v_360")],
        [Button.inline(f"🎥 480p ({_sz('480')})", data=f"dl:{download_id}:v_480")],
        [Button.inline(f"🎥 720p ({_sz('720')})", data=f"dl:{download_id}:v_720")],
        [Button.inline(f"🎥 1080p ({_sz('1080')})", data=f"dl:{download_id}:v_1080")],
    ]

    return [audio_row] + video_rows


def file_action_keyboard(download_id, lang="fa"):
    """Inline buttons attached under completed downloads."""
    return [
        [Button.inline(t("btn_report_issue", lang), data=f"report:{download_id}")],
    ]


def retry_keyboard(download_id, lang="fa"):
    """Retry prompt buttons if download is interrupted."""
    return [
        [
            Button.inline(t("btn_retry_yes", lang), data=f"retry:{download_id}"),
            Button.inline(t("btn_retry_no", lang), data=f"cancel_retry:{download_id}"),
        ]
    ]


# ----------------------------------------------------------------------
# Admin Keyboards
# ----------------------------------------------------------------------
ADMIN_BUTTONS = {
    "stats": "📊 آمار ربات",
    "users": "👥 مدیریت کاربران",
    "broadcast": "📢 پیام همگانی",
    "settings": "⚙️ تنظیمات ربات",
    "texts": "💬 ویرایش متن‌ها",
    "cache": "🗂 کش و فایل‌ها",
    "errors": "🧾 لیست خطاها",
    "admins": "👮 مدیریت ادمین‌ها",
    "maintenance": "🔧 مود تعمیر",
    "exit": "⬅️ خروج از پنل ادمین",
}


def admin_main_keyboard(role="owner"):
    """Build the reply keyboard for admin panel."""
    if role == "viewer":
        return [
            [Button.text(ADMIN_BUTTONS["stats"], resize=True)],
            [Button.text(ADMIN_BUTTONS["cache"]), Button.text(ADMIN_BUTTONS["errors"])],
            [Button.text(ADMIN_BUTTONS["exit"])],
        ]

    rows = [
        [Button.text(ADMIN_BUTTONS["stats"], resize=True)],
        [Button.text(ADMIN_BUTTONS["users"]), Button.text(ADMIN_BUTTONS["broadcast"])],
        [Button.text(ADMIN_BUTTONS["settings"]), Button.text(ADMIN_BUTTONS["texts"])],
        [Button.text(ADMIN_BUTTONS["cache"]), Button.text(ADMIN_BUTTONS["errors"])],
    ]

    if role == "owner":
        rows.append([Button.text(ADMIN_BUTTONS["admins"]), Button.text(ADMIN_BUTTONS["maintenance"])])
    else:
        rows.append([Button.text(ADMIN_BUTTONS["maintenance"])])

    rows.append([Button.text(ADMIN_BUTTONS["exit"])])
    return rows
