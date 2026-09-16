"""Utility functions for URL validation, formatting, and file cleanup."""

import re
import os
import glob
import math


YOUTUBE_URL_PATTERN = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/|embed/|playlist\?list=)|youtu\.be/)[\w-]+',
    re.IGNORECASE,
)


def is_valid_youtube_url(url):
    """Return True if *url* looks like a public YouTube video or playlist link."""
    clean = url.strip()
    return bool(YOUTUBE_URL_PATTERN.match(clean)) or "youtube.com" in clean or "youtu.be" in clean


def is_playlist_url(url):
    """Return True if *url* points to a YouTube playlist."""
    return "list=" in url.strip()


def sanitize_filename(filename):
    """Strip path components and dangerous characters from a filename."""
    filename = os.path.basename(filename)
    safe = re.sub(r'[^\w\s.-]', '', filename)
    safe = re.sub(r'\s+', '_', safe.strip())
    if not safe:
        safe = "download"
    return safe[:200]


def format_size(num_bytes):
    """Human-readable byte size, e.g. '12.34 MB'."""
    if num_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = min(int(math.floor(math.log(num_bytes, 1024))), len(units) - 1)
    size = num_bytes / (1024 ** i)
    return f"{size:.2f} {units[i]}"


def format_duration(seconds):
    """Seconds → 'M:SS' or 'H:MM:SS'."""
    if seconds is None or seconds <= 0:
        return "0:00"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def cleanup_files(download_dir, session_id):
    """Delete every file whose name starts with *session_id* (including thumbs and temp parts)."""
    pattern = os.path.join(download_dir, f"{session_id}*")
    for filepath in glob.glob(pattern):
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
        except OSError:
            pass


def format_duration_persian(seconds):
    """Convert seconds to friendly Persian text, e.g. '12 دقیقه و 34 ثانیه'."""
    if seconds is None or seconds <= 0:
        return "۰:۰۰"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    parts = []
    if hours > 0:
        parts.append(f"{hours} ساعت")
    if minutes > 0:
        parts.append(f"{minutes} دقیقه")
    if secs > 0 and hours == 0:
        parts.append(f"{secs} ثانیه")
    if not parts:
        return "کمتر از ۱ ثانیه"
    return " و ".join(parts)


def to_persian_digits(text):
    """Convert English digits in text to Persian digits."""
    fa_digits = "۰۱۲۳۴۵۶۷۸۹"
    return re.sub(r'\d', lambda m: fa_digits[int(m.group(0))], str(text))


def format_system_status(active_downloads: int = 0) -> str:
    """Format real-time server health and metrics for the /status Telegram command."""
    try:
        from system_metrics import get_system_metrics
        metrics = get_system_metrics()
    except Exception as exc:
        return f"⚠️ خطا در خواندن اطلاعات سرور: {exc}"

    cpu = metrics.get("cpu_percent", 0.0)
    ram_mb = metrics.get("ram_mb", 0.0)
    ram_pct = metrics.get("ram_percent", 0.0)
    disk_free = metrics.get("disk_free_gb", 0.0)
    temp_mb = metrics.get("disk_temp_mb", 0.0)
    is_safe = metrics.get("is_safe", True)
    warning = metrics.get("warning_msg")

    status_icon = "🟢 وضعیت پایدار و عادی" if is_safe else "🟠 هشدار بار کاری بالا"

    lines = [
        "🖥 <b>گزارش وضعیت و منابع سرور ربات:</b>",
        f"📊 <b>وضعیت کلی:</b> {status_icon}",
        "",
        f"⚙️ <b>مصرف پردازنده (CPU):</b> {cpu:.1f}%",
        f"🧠 <b>مصرف رم پردازه پایتون:</b> {ram_mb:.1f} MB",
        f"📈 <b>درصد کل رم مصرفی سرور:</b> {ram_pct:.1f}%",
        f"💾 <b>فضای آزاد دیسک:</b> {disk_free:.2f} GB",
        f"📁 <b>حجم پوشه موقت دانلود:</b> {temp_mb:.1f} MB",
        f"⚡ <b>دانلودهای فعال همزمان:</b> {active_downloads}",
    ]
    if warning:
        lines.extend(["", f"⚠️ <b>هشدار سیستمی:</b> {warning}"])

    lines.extend([
        "",
        "🚀 <i>سیستم آماده دریافت و پردازش لینک‌های یوتیوب است.</i>"
    ])
    return "\n".join(lines)

