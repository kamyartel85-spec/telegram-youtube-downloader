"""Thin wrapper around yt-dlp for info extraction and media downloading."""

import os
import glob
import logging

import yt_dlp

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
    # Use the Android player client first — it is far less likely to
    # trigger YouTube's "Sign in to confirm you're not a bot" interstitial
    # on datacenter IPs (e.g. Railway).  Fall back to the web client.
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
    """Return video metadata (title, duration, uploader, …) without downloading."""
    opts = dict(_BASE_OPTS, skip_download=True)
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def download_video(url, quality, session_id, download_dir, progress_hook=None):
    """Download *url* at the requested height and return the file path."""
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


def download_audio(url, session_id, download_dir, progress_hook=None):
    """Download best-audio from *url*, convert to MP3 192 kbps, return path."""
    outtmpl = os.path.join(download_dir, f"{session_id}.%(ext)s")
    opts = dict(
        _BASE_OPTS,
        format="bestaudio/best",
        outtmpl=outtmpl,
        progress_hooks=[progress_hook] if progress_hook else [],
        postprocessors=[{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    )
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return _find_output_file(download_dir, session_id)


def _find_output_file(download_dir, session_id):
    """Locate the media file produced for *session_id*."""
    pattern = os.path.join(download_dir, f"{session_id}.*")
    files = glob.glob(pattern)
    media = [f for f in files if f.lower().endswith(MEDIA_EXTENSIONS)]
    if not media:
        if files:
            return files[0]
        raise FileNotFoundError("Download finished but no output file was found.")
    return max(media, key=os.path.getsize)
