import os
from telethon import TelegramClient, events
import asyncio
from dotenv import load_dotenv
import requests
from . import models
from .cache_ops import load_cache, update_cache
from front import d_model

load_dotenv()

BASE_API_URL = os.getenv('BASE_API_URL')
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

client = TelegramClient('session_name', TELEGRAM_API_ID, TELEGRAM_API_HASH)

async def send_message(user: str, message: str, message_id: str | None = None):
    if message_id:
        await client.send_message(user, message, reply_to=int(message_id))
    else:
        await client.send_message(user, message)
        
    await update_cache(user)

async def listener():
    try:
        @client.on(events.NewMessage())
        async def handler(event):
            sender = await event.get_sender()
            message = event.message.text
            message_id = event.message.id
            if sender:
                cache = await load_cache()
                if sender.username in cache:
                    request_body = models.AnswerModel(sender.username, message, message_id, 'tg')

                    # TODO: Добавить эндпоинт
                    print(request_body)
                    #requests.post(url=BASE_API_URL+'tg_endpoint', data=request_body.to_json())
                    
        await client.run_until_disconnected()
    except asyncio.CancelledError:
        print("Task was cancelled.")

async def main_listener():
    await client.start(PHONE_NUMBER)
    await listener()

def run_main_listener():
    asyncio.run(main_listener())
