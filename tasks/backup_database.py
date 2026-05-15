import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from aiogram import Bot, types


BACKUP_DIR = Path("backups")
logger = logging.getLogger(__name__)

async def backup_task(
        tg_bot: Bot,
        bale_bot: Bot,
        bale_owner_id: int,
        tg_owner_id: int,
        source_db: str = "db.sqlite3"
):
    await bale_bot.send_message(chat_id=bale_owner_id,
                                text="[+] DB backup task started...")
    logger.info("DB backup task started.")

    backup_file_path = __back_up_db(source_db)

    await bale_bot.send_message(chat_id=bale_owner_id,
                                text=f"[+] New backup saved to {backup_file_path}")
    logger.info(f"New backup saved to {backup_file_path}")

    # send to telegram
    try:
        await tg_bot.send_document(chat_id=tg_owner_id,
                                   document=types.FSInputFile(backup_file_path))
        logger.info("Backup sent to telegram.")
        await bale_bot.send_message(chat_id=bale_owner_id,
                    text="[+] Backup sent to telegram.")
    except Exception as e:
        await bale_bot.send_message(chat_id=bale_owner_id,
                            text=f"Sending backup to telegram failed: {type(e)} - {e}")
        logger.error(f"Sending backup to telegram failed: {type(e)} - {e}")

    # send to bale
    try:
        await bale_bot.send_document(chat_id=bale_owner_id,
                                   document=types.FSInputFile(backup_file_path))
        logger.info("Backup sent to bale.")
        await bale_bot.send_message(chat_id=bale_owner_id,
                    text="[+] Backup sent to bale.")
    except Exception as e:
        await bale_bot.send_message(chat_id=bale_owner_id,
                            text=f"Sending backup to bale failed: {type(e)} - {e}")
        logger.error(f"Sending backup to bale failed: {type(e)} - {e}")
    

def __back_up_db(source_db: str = "db.sqlite3"):
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    backup_path = BACKUP_DIR / f"backup_{timestamp}.sqlite3"

    source = sqlite3.connect(source_db)
    backup = sqlite3.connect(backup_path)

    try:
        source.backup(backup)
    finally:
        backup.close()
        source.close()

    return str(backup_path)
