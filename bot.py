import asyncio
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from db import run, BotInfo, User

from middlewares import (BotsMiddleware, 
                         UserMiddleware, 
                         AlbumMiddleware, 
                         AdminMiddleware,
                         JoinRequiredMiddleware)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks.backup_database import backup_task

# bale handler
from handlers.bale.start import router as start_router
from handlers.bale.add_channel import router as add_channel_router
from handlers.bale.cancel import router as cancel_router
from handlers.bale.manage import router as manage_router
from handlers.bale.forwarder import router as forwarder_router
from handlers.bale.admin import router as admin_router
from handlers.bale.help import router as help_router
# tg handlers
from handlers.tg.start import router as tg_start_router


from setup_logger import setup_logger
from config import config


setup_logger(__name__)


async def main():
    # bot
    bale_session = AiohttpSession(api=TelegramAPIServer(
        base="https://tapi.bale.ai/bot{token}/{method}",
        file="https://tapi.bale.ai/file/bot%3Ctoken%3E/%3Cfile_path%3E"),
        proxy=config['PROXY']['BALE'] if config['PROXY']['BALE'] else None)
    tg_session = AiohttpSession(proxy=config['PROXY']['TELEGRAM'] if config['PROXY']['TELEGRAM'] else None)

    bale_bot = Bot(token=config['BALE']['TOKEN'],
            session=bale_session,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    tg_bot = Bot(token=config['TELEGRAM']['TOKEN'],
                session=tg_session,
                default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
                 )
    
    # db
    context = await run(config['DB']['PATH'])
    owner, _ = await User.get_or_create(
        bale_id=config['BALE']['OWNER_ID'],
        defaults={'username': None}
    )
    bot_info, _ = await BotInfo.update_or_create(bale_id=bale_bot.id,
                                    defaults={'owner': owner,
                                            'telegram_id': tg_bot.id})

    # dispatcher
    bale_dp = Dispatcher()
    tg_dp = Dispatcher()


    # middlewares
    bale_dp.update.middleware(BotsMiddleware(bot_info, bale_bot, tg_bot))
    bale_dp.update.middleware(UserMiddleware())
    bale_dp.update.middleware(JoinRequiredMiddleware())

    forwarder_router.message.middleware(AlbumMiddleware())

    admin_router.message.middleware(AdminMiddleware())
    admin_router.callback_query.middleware(AdminMiddleware())

    # handlers bale
    bale_dp.include_router(start_router)
    bale_dp.include_router(help_router)
    bale_dp.include_router(add_channel_router)
    bale_dp.include_router(manage_router)
    bale_dp.include_router(cancel_router)
    bale_dp.include_router(forwarder_router)
    bale_dp.include_router(admin_router)
    # handlers tg
    tg_dp.include_router(tg_start_router)

    # tasks
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(
        hour=5,
        minute=0,
        timezone=ZoneInfo("Asia/Tehran")
    )
    scheduler.add_job(
            backup_task,
            trigger=trigger,
            kwargs={
                "tg_bot": tg_bot,
                "bale_bot": bale_bot,
                "bale_owner_id": config['BALE']['OWNER_ID'],
                "tg_owner_id": config['TELEGRAM']['OWNER_ID'],
                "source_db": config['DB']['PATH']
            },
        )
    
    try:
        scheduler.start()
        await asyncio.gather(
            bale_dp.start_polling(
                bale_bot,
                handle_signals=False
            ),
            tg_dp.start_polling(
                tg_bot,
                handle_signals=False
            )
        )
    except KeyboardInterrupt:
        pass
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        await bale_bot.session.close()
        await tg_bot.session.close()
        await context.close_connections()
    
    
if __name__ == "__main__":
    asyncio.run(main())
