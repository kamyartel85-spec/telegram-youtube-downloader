"""System health diagnostics and telemetry metrics for Telegram YouTube Downloader Bot.

Monitors CPU usage, RAM allocation, active downloads, and disk space to prevent
Out-Of-Memory (OOM) kills and high-load container crashes.
"""

import os
import shutil
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def get_system_metrics() -> Dict[str, Any]:
    """Collect real-time CPU, RAM, and disk metrics.
    
    Returns a structured dictionary with usage statistics and a safety flag.
    """
    metrics = {
        "cpu_percent": 0.0,
        "ram_mb": 0.0,
        "ram_percent": 0.0,
        "disk_free_gb": 0.0,
        "disk_temp_mb": 0.0,
        "is_safe": True,
        "warning_msg": None
    }

    # Disk usage in temp directory
    try:
        temp_dir = os.environ.get("DOWNLOAD_DIR", "/tmp/ytdl_downloads")
        if os.path.exists(temp_dir):
            total_temp = sum(
                os.path.getsize(os.path.join(dirpath, f))
                for dirpath, _, filenames in os.walk(temp_dir)
                for f in filenames
            )
            metrics["disk_temp_mb"] = round(total_temp / (1024 * 1024), 1)

        total, used, free = shutil.disk_usage(os.path.dirname(temp_dir) or "/")
        metrics["disk_free_gb"] = round(free / (1024 ** 3), 2)
    except Exception as e:
        logger.debug(f"Error calculating disk usage: {e}")

    if not HAS_PSUTIL:
        # Fallback reading from /proc/meminfo on Linux if psutil is not installed
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem = {}
            for line in lines:
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = int(parts[1].split()[0].strip())
                    mem[key] = val
            total_kb = mem.get("MemTotal", 1024 * 1024)
            avail_kb = mem.get("MemAvailable", total_kb // 2)
            used_kb = total_kb - avail_kb
            metrics["ram_mb"] = round(used_kb / 1024, 1)
            metrics["ram_percent"] = round((used_kb / total_kb) * 100, 1)
        except Exception:
            pass
        return metrics

    try:
        metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        process = psutil.Process(os.getpid())
        proc_mem = process.memory_info()

        metrics["ram_mb"] = round(proc_mem.rss / (1024 * 1024), 1)
        metrics["ram_percent"] = mem.percent

        # Safety evaluation to prevent OOM kill on containers (e.g. Railway 1GB)
        if mem.percent > 88.0:
            metrics["is_safe"] = False
            metrics["warning_msg"] = "خطر کمبود رم سرور! دانلودهای حجیم به صورت موقت در صف قرار می‌گیرند."
        elif metrics["cpu_percent"] > 90.0:
            metrics["is_safe"] = False
            metrics["warning_msg"] = "پردازنده تحت فشار بالا است (FFmpeg Re-encode)."

    except Exception as e:
        logger.error(f"Failed to gather psutil metrics: {e}")

    return metrics
