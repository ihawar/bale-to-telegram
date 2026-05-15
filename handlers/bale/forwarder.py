import logging
from typing import List

from aiogram import Router, types, Bot, F, enums
from aiohttp.client_exceptions import ClientResponseError

from db import Channel, BotInfo

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.chat.type != 'private')
async def handle_forwarder(msg: types.Message, 
                          bot_info: BotInfo,
                          tg_bot: Bot, 
                          album: List[types.Message] | None = None):        
    if not msg.bot: return
    channels = await Channel.filter(bale_id=str(msg.chat.id)).prefetch_related("owner")
    if not len(channels):
        return logger.error(
            f"Channel(id={msg.chat.id}, name={msg.chat.full_name}, username={msg.chat.username}) does not exists in DB."
        )

    for ch in channels:
        if ch.is_deleted:
            logger.info("Ignoring forward for deleted channel: " + 
                        f"{ch}")
            continue

        if not ch.is_active:
            logger.info("Ignoring forward for inactive channel: "+
                        f"{ch}")
            continue
            
        try:
            messages_to_send = album if album else [msg]
            await forward_to_telegram(tg_bot, ch.telegram_id, messages_to_send)
            await msg.bot.send_message(chat_id=ch.owner.bale_id,
                                text=f"✌️ پیام کانال *{msg.chat.full_name}* با موفقیت در تلگرام ارسال شد.")
            logger.info(
                f"Message forwarded successfully - " + 
                f"{ch}"
            )
            bot_info.forwards += 1
            await bot_info.save()

        except ClientResponseError as e:
            logger.error(
                f'Bale server error - {type(e)}: {e}'
            )
            txt = """😫 بازم سرورای بله مشکل داره...
کد خطا: {error}
متاسفانه وقتی میخوایم پیام کانال  *{channel_name}* رو دریافت کنیم بله اجازه نمیده. در نتیجه پیام آخر فروارد نشد.""".format(
        channel_name=msg.chat.full_name,
        error=f'{e.code}')
            await msg.bot.send_message(chat_id=ch.owner.bale_id,
                                    text=txt)


async def forward_to_telegram(tg_bot: Bot, 
                              target_id: str,
                              messages: List[types.Message]):
    
    if len(messages) > 1:
        media_group = []
        for msg in messages:
            if not msg.bot: continue
            caption = msg.caption or ""
            # Download file from Bale
            file_id = None
            if msg.photo: file_id = msg.photo[-1]
            elif msg.video: file_id = msg.video
            
            if file_id:
                file_buffer = await msg.bot.download(file_id)
                if not file_buffer: continue
                content = types.BufferedInputFile(file_buffer.read(), filename="file")
                
                # Create the media object
                if msg.photo:
                    media_group.append(types.InputMediaPhoto(media=content, caption=caption))
                elif msg.video:
                    media_group.append(types.InputMediaVideo(media=content, caption=caption))
        
        await tg_bot.send_media_group(chat_id=target_id, media=media_group)
    else:
        msg = messages[0]
        caption = msg.caption or msg.text
        entities = msg.caption_entities or msg.entities
        if not msg.bot: return

        if msg.photo:
            photo = msg.photo[-1]
            file_buffer = await msg.bot.download(photo)
            await tg_bot.send_photo(
                chat_id=target_id,
                photo=types.BufferedInputFile(file_buffer.read(), filename="photo.jpg"),
                caption=caption,
                caption_entities=entities
            )

        elif msg.video:
            file_buffer = await msg.bot.download(msg.video)
            await tg_bot.send_video(
                chat_id=target_id,
                video=types.BufferedInputFile(file_buffer.read(), filename="video.mp4"),
                caption=caption,
                caption_entities=entities
            )

        elif msg.animation:
            file_buffer = await msg.bot.download(msg.animation)
            await tg_bot.send_animation(
                chat_id=target_id,
                animation=types.BufferedInputFile(file_buffer.read(), filename="gif.mp4"),
                caption=caption
            )

        elif msg.audio:
            file_buffer = await msg.bot.download(msg.audio)
            await tg_bot.send_audio(
                chat_id=target_id,
                audio=types.BufferedInputFile(file_buffer.read(), 
                                              filename=msg.audio.title or "audio.mp3"),
                caption=caption,
                caption_entities=entities
            )

        elif msg.voice:
            file_buffer = await msg.bot.download(msg.voice)
            await tg_bot.send_voice(
                chat_id=target_id,
                voice=types.BufferedInputFile(file_buffer.read(), filename="voice.ogg"),
                caption=caption
            )

        elif msg.document:
            file_buffer = await msg.bot.download(msg.document)
            await tg_bot.send_document(
                chat_id=target_id,
                document=types.BufferedInputFile(
                    file_buffer.read(), 
                    filename=msg.document.file_name or "file"
                ),
                caption=caption,
                caption_entities=entities
            )

        elif msg.text:
            await tg_bot.send_message(
                chat_id=target_id,
                text=msg.text,
                entities=msg.entities
            )
