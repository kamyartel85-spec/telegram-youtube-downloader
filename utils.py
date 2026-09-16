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
    """Delete every file whose name starts with *session_id*."""
    pattern = os.path.join(download_dir, f"{session_id}.*")
    for filepath in glob.glob(pattern):
        try:
            os.remove(filepath)
        except OSError:
            pass
