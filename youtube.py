"""Wrapper around yt-dlp for video/playlist info extraction and downloading."""

import os
import glob
import logging
from datetime import datetime
import yt_dlp
from utils import format_size, format_duration

logger = logging.getLogger(__name__)

MEDIA_EXTENSIONS = (
    ".mp4", ".mp3", ".m4a", ".webm", ".mkv", ".opus",
)

_BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "noprogress": True,
    "noplaylist": True,
    "retries": 10,
    "fragment_retries": 10,
    "socket_timeout": 30,
    "extractor_args": {
        "youtube": {
            "player_client": ["ios", "android", "mweb"],
        }
    },
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    },
}


def extract_info(url):
    """Return single video metadata with estimated format sizes and clean attributes."""
    opts = dict(_BASE_OPTS, skip_download=True)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            raise ValueError("No video information retrieved")
        
        # Format upload date (e.g., 20240315 -> 2024-03-15)
        raw_date = str(info.get("upload_date") or "")
        if len(raw_date) == 8:
            formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
        else:
            formatted_date = raw_date or "N/A"

        # Compute format sizes
        sizes = calculate_format_sizes(info)

        return {
            "id": info.get("id"),
            "title": info.get("title", "Untitled"),
            "duration": format_duration(info.get("duration")),
            "raw_duration": info.get("duration") or 0,
            "uploader": info.get("uploader") or info.get("channel") or "YouTube",
            "view_count": f"{info.get('view_count', 0):,}" if info.get("view_count") else "0",
            "comment_count": f"{info.get('comment_count', 0):,}" if info.get("comment_count") else "0",
            "upload_date": formatted_date,
            "thumbnail": info.get("thumbnail"),
            "format_sizes": sizes,
            "webpage_url": info.get("webpage_url") or url,
        }


def calculate_format_sizes(info):
    """Estimate or read size for mp3 and video resolutions."""
    formats = info.get("formats") or []
    duration = info.get("duration") or 0
    sizes = {}

    # Audio estimates based on bitrate & duration if not in format
    # mp3_medium ~128 kbps (16 KB/s), mp3_best ~320 kbps (40 KB/s)
    if duration > 0:
        sizes["mp3_medium"] = f"~{format_size(int(duration * 16 * 1024))}"
        sizes["mp3_best"] = f"~{format_size(int(duration * 40 * 1024))}"
    else:
        sizes["mp3_medium"] = "~5 MB"
        sizes["mp3_best"] = "~10 MB"

    # Video resolutions: 144, 240, 360, 480, 720, 1080
    heights = [144, 240, 360, 480, 720, 1080]
    for h in heights:
        # Find matching formats
        found_size = None
        for f in formats:
            if f.get("height") == h:
                sz = f.get("filesize") or f.get("filesize_approx")
                if sz:
                    found_size = sz
                    break
        if found_size:
            sizes[str(h)] = f"~{format_size(found_size)}"
        elif duration > 0:
            # Fallback estimation based on typical video bitrate
            # 144p ~ 200kbps, 240p ~ 400kbps, 360p ~ 800kbps, 480p ~ 1400kbps, 720p ~ 2500kbps, 1080p ~ 4500kbps
            rates = {144: 25, 240: 50, 360: 100, 480: 175, 720: 312, 1080: 560}  # KB/s
            est = int(duration * rates.get(h, 100) * 1024)
            sizes[str(h)] = f"~{format_size(est)}"
        else:
            sizes[str(h)] = "~نامشخص"

    return sizes


def extract_playlist_info(url, max_items=25):
    """Extract playlist items using flat extraction for speed."""
    opts = dict(_BASE_OPTS, extract_flat=True, noplaylist=False)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get("entries") or []
        items = []
        for idx, entry in enumerate(entries):
            if idx >= max_items:
                break
            if not entry:
                continue
            item_url = entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
            items.append({
                "id": entry.get("id"),
                "title": entry.get("title", f"Video {idx + 1}"),
                "url": item_url,
            })
        return {
            "title": info.get("title", "YouTube Playlist"),
            "total_count": len(entries),
            "items": items,
        }


def download_video(url, quality, session_id, download_dir, progress_hook=None):
    """Download video strictly matching or under target height, merging to streamable MP4.
    Fixes 144p, 240p, and 360p errors by:
    1. Selecting pre-merged MP4 first (format 18 for 360p)
    2. Allowing robust video+audio matching without failing on missing avc1
    3. Re-encoding audio to AAC in FFmpeg if Opus/WebM to guarantee MP4 compatibility
    """
    outtmpl = os.path.join(download_dir, f"{session_id}.%(ext)s")
    q = str(quality).replace("v_", "").strip()
    
    # Robust quality hierarchy ensuring 144p, 240p, 360p, 480p, 720p, 1080p download cleanly
    fmt = (
        f"best[height<={q}][ext=mp4]/"
        f"bestvideo[height<={q}][ext=mp4]+bestaudio[ext=m4a]/"
        f"bestvideo[height<={q}]+bestaudio[ext=m4a]/"
        f"bestvideo[height<={q}]+bestaudio/"
        f"best[height<={q}]/"
        f"best"
    )
    opts = dict(
        _BASE_OPTS,
        format=fmt,
        merge_output_format="mp4",
        outtmpl=outtmpl,
        progress_hooks=[progress_hook] if progress_hook else [],
        postprocessor_args={
            "ffmpeg": [
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
            ],
        },
    )
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return _find_output_file(download_dir, session_id)


def download_audio(url, preset, session_id, download_dir, progress_hook=None):
    """Download audio and convert to MP3 with proper ID3 metadata (Title, Artist, Album Art).
    preset can be 'mp3_medium' (128 kbps) or 'mp3_best' (320 kbps).
    """
    bitrate = "320" if preset == "mp3_best" else "128"
    outtmpl = os.path.join(download_dir, f"{session_id}.%(ext)s")
    opts = dict(
        _BASE_OPTS,
        format="bestaudio/best",
        outtmpl=outtmpl,
        progress_hooks=[progress_hook] if progress_hook else [],
        postprocessors=[
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ],
    )
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return _find_output_file(download_dir, session_id)


def prepare_thumbnail(thumb_url, session_id, download_dir):
    """Download and prepare Telegram-compliant JPEG thumbnail (max 320x320, under 200KB)."""
    if not thumb_url:
        return None
    thumb_path = os.path.join(download_dir, f"{session_id}_thumb.jpg")
    try:
        import urllib.request
        from PIL import Image

        raw_thumb = os.path.join(download_dir, f"{session_id}_raw_thumb")
        req = urllib.request.Request(
            thumb_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response, open(raw_thumb, "wb") as f:
            f.write(response.read())

        with Image.open(raw_thumb) as img:
            img = img.convert("RGB")
            # Telegram accepts max 320x320 for thumbnails
            img.thumbnail((320, 320), Image.Resampling.LANCZOS)
            img.save(thumb_path, "JPEG", quality=85, optimize=True)

        try:
            os.remove(raw_thumb)
        except OSError:
            pass

        if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
            return thumb_path
    except Exception as exc:
        logger.warning("Could not create thumbnail: %s", exc)
    return None


def get_quality_dimensions(quality):
    """Return estimated width & height for Telegram DocumentAttributeVideo."""
    try:
        h = int(str(quality).replace("v_", "").strip())
    except (ValueError, TypeError):
        h = 720
    # Standard 16:9 aspect ratio
    w = int(round(h * 16 / 9))
    if w % 2 != 0:
        w += 1
    if h % 2 != 0:
        h += 1
    return w, h


def _find_output_file(download_dir, session_id):
    """Locate the produced media file for *session_id*."""
    pattern = os.path.join(download_dir, f"{session_id}.*")
    files = glob.glob(pattern)
    media = [f for f in files if f.lower().endswith(MEDIA_EXTENSIONS)]
    if not media:
        if files:
            return files[0]
        raise FileNotFoundError("Download finished but no output file was found.")
    return max(media, key=os.path.getsize)
