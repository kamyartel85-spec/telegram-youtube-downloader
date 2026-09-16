"""Wrapper around yt-dlp for video/playlist info extraction and downloading."""

import os
import glob
import logging
import subprocess
from datetime import datetime
import yt_dlp
from utils import format_size, format_duration, format_duration_persian, to_persian_digits

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
            formatted_date = f"{raw_date[:4]}/{raw_date[4:6]}/{raw_date[6:]}"
        else:
            formatted_date = raw_date or "نامشخص"

        # Compute accurate format sizes
        sizes = calculate_format_sizes(info)
        raw_dur = info.get("duration") or 0
        dur_str = format_duration(raw_dur)
        dur_persian = format_duration_persian(raw_dur)

        v_count = info.get("view_count")
        view_str = f"{v_count:,}" if v_count is not None else "0"

        c_count = info.get("comment_count")
        comment_str = f"{c_count:,}" if c_count is not None else "0"

        return {
            "id": info.get("id"),
            "title": info.get("title", "Untitled"),
            "duration": dur_str,
            "duration_persian": dur_persian,
            "raw_duration": raw_dur,
            "uploader": info.get("uploader") or info.get("channel") or "یوتیوب (YouTube)",
            "view_count": view_str,
            "comment_count": comment_str,
            "upload_date": formatted_date,
            "thumbnail": info.get("thumbnail"),
            "format_sizes": sizes,
            "webpage_url": info.get("webpage_url") or url,
        }


def calculate_format_sizes(info):
    """Accurately compute or estimate total size (video + audio) for each quality.
    
    Fixes the issue where 480p or other qualities showed significantly smaller sizes
    (like 101 MB) because they only read a single video-only stream and ignored
    the audio stream and actual format selection!
    """
    formats = info.get("formats") or []
    duration = info.get("duration") or 0
    sizes = {}

    # 1. Find best audio stream size and bitrate (since video downloads merge with best audio)
    audio_formats = [
        f for f in formats
        if f.get("acodec") != "none" and (f.get("vcodec") == "none" or not f.get("height"))
    ]
    best_audio_sz = 0
    if audio_formats:
        best_audio = max(
            audio_formats,
            key=lambda f: f.get("filesize") or f.get("filesize_approx") or (f.get("abr") or 0)
        )
        best_audio_sz = best_audio.get("filesize") or best_audio.get("filesize_approx") or 0
        if not best_audio_sz and duration > 0 and (best_audio.get("abr") or best_audio.get("tbr")):
            abr = best_audio.get("abr") or best_audio.get("tbr")
            best_audio_sz = int((abr * 1000 / 8) * duration)

    if not best_audio_sz and duration > 0:
        # Default ~128 kbps audio stream
        best_audio_sz = int((128 * 1000 / 8) * duration)

    # Audio estimates for mp3 buttons
    if duration > 0:
        sizes["mp3_medium"] = f"~{format_size(int((128 * 1000 / 8) * duration))}"
        sizes["mp3_best"] = f"~{format_size(int((320 * 1000 / 8) * duration))}"
    else:
        sizes["mp3_medium"] = f"~{format_size(best_audio_sz)}" if best_audio_sz else "~5 MB"
        sizes["mp3_best"] = "~10 MB"

    # 2. Compute video sizes for heights: 144, 240, 360, 480, 720, 1080
    heights = [144, 240, 360, 480, 720, 1080]
    for h in heights:
        # Pre-merged format (video + audio in one stream, e.g. fmt 18 for 360p)
        merged_candidates = [
            f for f in formats
            if f.get("height") == h and f.get("vcodec") != "none" and f.get("acodec") != "none"
        ]

        # Video-only candidates for this height
        video_candidates = [
            f for f in formats
            if f.get("height") == h and f.get("vcodec") != "none" and (f.get("acodec") == "none" or not f.get("acodec"))
        ]

        total_sz = 0
        if merged_candidates:
            best_merged = max(
                merged_candidates,
                key=lambda f: f.get("filesize") or f.get("filesize_approx") or (f.get("tbr") or 0)
            )
            sz = best_merged.get("filesize") or best_merged.get("filesize_approx")
            if sz:
                total_sz = sz
            elif duration > 0 and best_merged.get("tbr"):
                total_sz = int((best_merged.get("tbr") * 1000 / 8) * duration)

        if not total_sz and video_candidates:
            # yt-dlp selects the best format, so evaluate candidates matching best quality
            best_v = max(
                video_candidates,
                key=lambda f: f.get("filesize") or f.get("filesize_approx") or (f.get("tbr") or f.get("vbr") or 0)
            )
            v_sz = best_v.get("filesize") or best_v.get("filesize_approx") or 0
            if not v_sz and duration > 0 and (best_v.get("vbr") or best_v.get("tbr")):
                v_bitrate = best_v.get("vbr") or best_v.get("tbr")
                v_sz = int((v_bitrate * 1000 / 8) * duration)

            if v_sz:
                # Crucial fix: Merged file size is Video stream + Audio stream!
                total_sz = v_sz + best_audio_sz

        if total_sz > 0:
            sizes[str(h)] = f"~{format_size(total_sz)}"
        elif duration > 0:
            # Realistic average bitrates for YouTube streams (video + audio combined)
            # 144p: ~300 kbps, 240p: ~550 kbps, 360p: ~950 kbps, 480p: ~1700 kbps, 720p: ~3200 kbps, 1080p: ~5500 kbps
            rates_kbps = {144: 300, 240: 550, 360: 950, 480: 1700, 720: 3200, 1080: 5500}
            est_sz = int((rates_kbps.get(h, 1500) * 1000 / 8) * duration)
            sizes[str(h)] = f"~{format_size(est_sz)}"
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


def _ensure_telegram_mp4(raw_file, target_mp4):
    """Guarantee standard, streamable H.264/AAC MP4 for Telegram playback.
    
    Fixes 144p, 240p, 360p and webm/vp9 failures where Telegram can't stream or
    display black screens.
    """
    if not os.path.exists(raw_file):
        raise FileNotFoundError(f"Downloaded media not found: {raw_file}")

    # Attempt 1: Fast stream-copy of video with AAC audio re-encode & faststart
    cmd_copy = [
        "ffmpeg", "-y", "-i", raw_file,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        target_mp4
    ]
    res = subprocess.run(cmd_copy, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode == 0 and os.path.exists(target_mp4) and os.path.getsize(target_mp4) > 1024:
        try:
            if os.path.abspath(raw_file) != os.path.abspath(target_mp4):
                os.remove(raw_file)
        except OSError:
            pass
        return target_mp4

    # Attempt 2: Transcode video to standard H.264 (essential for VP9/AV1 at 144p, 240p, 360p)
    # Uses ultrafast preset so transcoding 144p-360p completes in ~1-2 seconds
    logger.info("Transcoding raw video stream to standard H.264/AAC for Telegram compatibility...")
    cmd_transcode = [
        "ffmpeg", "-y", "-i", raw_file,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        target_mp4
    ]
    res2 = subprocess.run(cmd_transcode, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res2.returncode == 0 and os.path.exists(target_mp4) and os.path.getsize(target_mp4) > 1024:
        try:
            if os.path.abspath(raw_file) != os.path.abspath(target_mp4):
                os.remove(raw_file)
        except OSError:
            pass
        return target_mp4

    logger.warning("FFmpeg conversion returned error: %s", res2.stderr.decode(errors="ignore"))
    if os.path.exists(raw_file):
        return raw_file
    raise RuntimeError("Failed to produce playable MP4 video")


def download_video(url, quality, session_id, download_dir, progress_hook=None):
    """Download video strictly matching or under target height, merging to streamable MP4."""
    raw_tmpl = os.path.join(download_dir, f"{session_id}_raw.%(ext)s")
    final_mp4 = os.path.join(download_dir, f"{session_id}.mp4")
    q = str(quality).replace("v_", "").strip()

    # Robust quality hierarchy ensuring 144p, 240p, 360p, 480p, 720p, 1080p download cleanly
    fmt = (
        f"bestvideo[height={q}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
        f"bestvideo[height={q}]+bestaudio/"
        f"best[height={q}][ext=mp4]/"
        f"bestvideo[height<={q}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
        f"bestvideo[height<={q}]+bestaudio/"
        f"best[height<={q}][ext=mp4]/"
        f"bestvideo[height<={q}]+bestaudio/"
        f"best[height<={q}]/"
        f"best"
    )
    opts = dict(
        _BASE_OPTS,
        format=fmt,
        outtmpl=raw_tmpl,
        progress_hooks=[progress_hook] if progress_hook else [],
    )
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    raw_file = _find_output_file(download_dir, f"{session_id}_raw")
    return _ensure_telegram_mp4(raw_file, final_mp4)



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
