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
            "player_client": ["android", "web"],
        }
    },
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
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
    """Download video with specified max height and return output file path."""
    outtmpl = os.path.join(download_dir, f"{session_id}.%(ext)s")
    fmt = (
        f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]"
        f"/best[height<={quality}][ext=mp4]"
        f"/best[height<={quality}]"
        f"/best"
    )
    opts = dict(
        _BASE_OPTS,
        format=fmt,
        merge_output_format="mp4",
        outtmpl=outtmpl,
        progress_hooks=[progress_hook] if progress_hook else [],
    )
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return _find_output_file(download_dir, session_id)


def download_audio(url, preset, session_id, download_dir, progress_hook=None):
    """Download audio and convert to MP3.

    preset can be 'mp3_medium' (128 kbps) or 'mp3_best' (320 kbps).
    """
    bitrate = "320" if preset == "mp3_best" else "128"
    outtmpl = os.path.join(download_dir, f"{session_id}.%(ext)s")
    opts = dict(
        _BASE_OPTS,
        format="bestaudio/best",
        outtmpl=outtmpl,
        progress_hooks=[progress_hook] if progress_hook else [],
        postprocessors=[{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": bitrate,
        }],
    )
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return _find_output_file(download_dir, session_id)


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
