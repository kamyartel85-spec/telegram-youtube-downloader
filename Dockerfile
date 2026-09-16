FROM python:3.12-slim

# FFmpeg is required for merging / converting media
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure storage directories exist (for persistent DB, mount a Railway Volume to /app/data in Railway service settings)
RUN mkdir -p /app/data /tmp/ytdl_downloads

CMD ["python", "main.py"]
