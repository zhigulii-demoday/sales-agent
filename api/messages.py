from fastapi import APIRouter, Depends, status, Query, HTTPException, Header, Security, Body
from api.models import message_post
from messages.emai_scripts import send_email, wait_for_reply
from messages.telegram_scripts import send_message
import asyncio

messages_router = APIRouter(prefix='/messages')

tag = "Messages"

@messages_router.post(
    '/send-message',
    status_code=status.HTTP_200_OK,
    description='Отправка сообщений',
)
async def send(
    message_info: message_post
):
    if message_info.chat_type == 'tg':
        await send_message(message_info.username, message_info.text, message_info.message_id)
    elif message_info.chat_type == 'mail':
        await send_email(to_email=message_info.username, body=message_info.text, message_id=message_info.message_id, subject=message_info.subject)
        asyncio.create_task(wait_for_reply(message_info.username))  
    return {"status": "Message sent successfully"}  