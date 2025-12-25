
import telebot
import threading
import asyncio
from aiohttp import ClientSession
from Python_ARQ import ARQ
import os,random
keys=['YNGZSM-KGFVYX-DKAQID-XHJRYP-ARQ','HVNQZK-DONUYX-TFWNHP-UXPDVU-ARQ','SEKDTT-RJWLAY-ASOYBR-CUTLKY-ARQ','FHUWYE-TOKGGI-DYDSYS-DJOKIW-ARQ','RZOQET-QTRRZI-RQJMMS-JJLYPN-ARQ']
TOKEN = "8102359893:AAEZUgzUtWN4xyjpApOjQ_ZA3Tv9NGssnF0"
ARQ_API_KEY = "YNGZSM-KGFVYX-DKAQID-XHJRYP-ARQ"   # من https://t.me/ARQRoBot
ARQ_API_URL = "https://arq.hamker.dev"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


def run_async(func, *args):
    asyncio.run(func(*args))


@bot.message_handler(
    content_types=["photo", "video", "sticker", "animation"],
    chat_types=["group", "supergroup"]
)
def anti_nsfw(message):

    file_id = None

    if message.photo:
        file_id = message.photo[-1].file_id

    elif message.video and message.video.thumb:
        file_id = message.video.thumb.file_id

    elif message.sticker and message.sticker.thumb:
        file_id = message.sticker.thumb.file_id

    elif message.animation and message.animation.thumb:
        file_id = message.animation.thumb.file_id

    if file_id:
        threading.Thread(
            target=run_async,
            args=(scan_nsfw, message, file_id)
        ).start()


async def scan_nsfw(message, file_id):
    session = ClientSession()
    
    arq = ARQ(ARQ_API_URL, ARQ_API_KEY, session)

    try:
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)

        file_path = f"temp_{message.message_id}.jpg"
        with open(file_path, "wb") as f:
            f.write(downloaded)

        resp = await arq.nsfw_scan(file=file_path)
        print(resp)

        if resp.result.is_nsfw:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(
                message.chat.id,
                f"• <a href='tg://user?id={message.from_user.id}'>User</a>\n"
                f"• تم حذف الرسالة لأنها تحتوي على محتوى NSFW 🚫"
            )

        os.remove(file_path)

    except Exception as e:
        print("Error:", e)

    await session.close()


print("Bot Started ✅")
bot.infinity_polling()
