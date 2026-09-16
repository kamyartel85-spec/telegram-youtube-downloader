"""Entry point: logging, health-check server, and Telethon bot startup."""

import asyncio
import logging
import os
import sys

from telethon import TelegramClient

from config import (
    BOT_TOKEN,
    API_ID,
    API_HASH,
    DOWNLOAD_DIR,
    HEALTH_CHECK_PORT,
    SESSION_NAME,
    LOG_LEVEL,
)
from handlers import register_handlers
import db

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger("ytdl-bot")


# ----------------------------------------------------------------------
# Minimal HTTP health-check server (for Railway)
# ----------------------------------------------------------------------
async def _health_handler(reader, writer):
    await reader.read(1024)
    body = b"OK"
    header = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
        b"Content-Length: " + str(len(body)).encode() + b"\r\n"
        b"\r\n"
    )
    writer.write(header + body)
    await writer.drain()
    writer.close()


async def _start_health_server():
    server = await asyncio.start_server(_health_handler, "0.0.0.0", HEALTH_CHECK_PORT)
    logger.info("Health-check server listening on port %d", HEALTH_CHECK_PORT)
    async with server:
        await server.serve_forever()


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Add it to your environment variables.")
        sys.exit(1)
    if not API_ID or not API_HASH:
        logger.error("API_ID and API_HASH are not set. Add them to your environment variables.")
        sys.exit(1)

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    db.initialize_database()

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    register_handlers(client)

    # Run the health-check server in the background
    asyncio.create_task(_start_health_server())

    await client.start(bot_token=BOT_TOKEN)
    me = await client.get_me()
    username = me.username or "unknown"
    logger.info("Bot started as @%s", username)

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
